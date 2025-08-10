from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import json, os
import requests
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import PaymentTransaction, FileUpload, ActivityLog
from .serializers import PaymentTransactionSerializer, FileUploadSerializer, ActivityLogSerializer
from .tasks import process_file_wordcount
from decouple import config

User = get_user_model()

AAMARPAY_STORE_ID = config("AAMARPAY_STORE_ID")
AAMARPAY_SIGNATURE_KEY = config("AAMARPAY_SIGNATURE_KEY")
AAMARPAY_ENDPOINT = config("AAMARPAY_ENDPOINT")

class InitiatePaymentView(generics.CreateAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        amount = "100.00"
        tran_id = f"tnx_{int(timezone.now().timestamp())}"

        payload = {
            "store_id": AAMARPAY_STORE_ID,
            "signature_key": AAMARPAY_SIGNATURE_KEY,
            "amount": amount,
            "currency": "BDT",
            "tran_id": tran_id,
            "success_url": request.build_absolute_uri(reverse("payment-success")),
            "fail_url": request.build_absolute_uri(reverse("payment-fail")),
            "cancel_url": request.build_absolute_uri(reverse("payment-cancel")),
            "cus_name": user.get_full_name() or user.username,
            "cus_email": user.email or "",
            "cus_add1": request.data.get("cus_add1", ""),
            "cus_city": request.data.get("cus_city", ""),
            "cus_country": request.data.get("cus_country", "Bangladesh"),
            "cus_phone": request.data.get("cus_phone", "01700000000"),
            "desc": "File upload payment",
            "type": "json",
        }

        try:
            resp = requests.post(AAMARPAY_ENDPOINT, json=payload, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            redirect_url = data.get("payment_url") or data.get("redirect_url") or data.get("url")

            PaymentTransaction.objects.create(
                user=user,
                transaction_id=tran_id,
                amount=amount,
                status="initiated",
                gateway_response=data
            )

            ActivityLog.objects.create(
                user=user,
                action="payment_initiated",
                metadata={"transaction_id": tran_id, "gateway_response": data}
            )

            return Response({
                "redirect_url": redirect_url,
                "transaction_id": tran_id,
                "status": "initiated",
                "data": data
            })
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class PaymentSuccessView(generics.RetrieveAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        tran_id = request.GET.get("tran_id")
        status_param = request.GET.get("status") or request.GET.get("pay_status") or "success"
        gateway_data = dict(request.GET)

        tx = PaymentTransaction.objects.filter(transaction_id=tran_id).first()

        if tx.status == "success":
            return Response({
                "message": "Payment already recorded",
                "transaction_id": tx.transaction_id,
                "status": tx.status,
                "transaction": PaymentTransactionSerializer(tx).data
            })

        tx.status = "success" if status_param.lower() in ("success", "completed", "paid") else "failed"
        tx.gateway_response = gateway_data
        tx.save()

        ActivityLog.objects.create(
            user=tx.user,
            action="payment_success" if tx.status == "success" else "payment_failed",
            metadata={"transaction_id": tx.transaction_id, "gateway_response": gateway_data}
        )

        return Response({
            "message": "Payment recorded",
            "transaction_id": tx.transaction_id,
            "status": tx.status,
            "transaction": PaymentTransactionSerializer(tx).data
        })


class PaymentFailView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        tran_id = request.GET.get("tran_id") or request.GET.get("transaction_id")
        if not tran_id:
            return Response({"error": "Missing transaction id"}, status=400)

        tx = PaymentTransaction.objects.filter(transaction_id=tran_id).first()
        if tx:
            tx.status = "failed"
            tx.gateway_response = dict(request.GET)
            tx.save()

            ActivityLog.objects.create(
                user=tx.user,
                action="payment_failed",
                metadata={"transaction_id": tx.transaction_id, "gateway_response": tx.gateway_response}
            )

        return Response({"detail": "Payment failed", "transaction_id": tran_id})


class PaymentCancelView(generics.RetrieveAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        tran_id = request.GET.get("tran_id") or request.GET.get("transaction_id")
        if not tran_id:
            return Response({"error": "Missing transaction id"}, status=400)

        tx = PaymentTransaction.objects.filter(transaction_id=tran_id).first()
        if tx:
            tx.status = "cancelled"
            tx.gateway_response = dict(request.GET)
            tx.save()

            ActivityLog.objects.create(
                user=tx.user,
                action="payment_cancelled",
                metadata={"transaction_id": tx.transaction_id, "gateway_response": tx.gateway_response}
            )

        return Response({"detail": "Payment cancelled", "transaction_id": tran_id})

  

class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        user = request.user
        paid = PaymentTransaction.objects.filter(user=user, status="success").exists()
        if not paid:
            return Response({"error": "Payment required"}, status=403)

        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file provided"}, status=400)

        ext = os.path.splitext(file.name)[1].lower()
        if ext not in [".txt", ".docx"]:
            return Response({"error": "Unsupported file type"}, status=400)

        file_upload = FileUpload.objects.create(
            user=user,
            file=file,
            filename=file.name,
            status="processing"
        )

        process_file_wordcount.delay(file_upload.id)

        ActivityLog.objects.create(
            user=user,
            action="file_uploaded",
            metadata={"filename": file_upload.filename, "file_id": file_upload.id}
        )

        return Response(FileUploadSerializer(file_upload).data, status=status.HTTP_201_CREATED)


class ListFilesView(generics.ListAPIView):
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FileUpload.objects.filter(user=self.request.user).order_by("-upload_time")

class ListActivityView(generics.ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user).order_by("-timestamp")


class ListTransactionsView(generics.ListAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user).order_by("-timestamp")