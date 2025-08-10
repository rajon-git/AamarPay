from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from paymentGateway.models import FileUpload, PaymentTransaction, ActivityLog
from django.conf import settings

@login_required
def dashboard(request):
    user = request.user

    if user.is_superuser:
        has_paid = PaymentTransaction.objects.filter(
            status__iexact='success',
            amount__gte=100
        ).exists()

        files = FileUpload.objects.all().order_by('-upload_time')
        activities = ActivityLog.objects.all().order_by('-timestamp')[:10]
        payments = PaymentTransaction.objects.all().order_by('-timestamp')
    else:
        has_paid = PaymentTransaction.objects.filter(
            user=user,
            status__iexact='success',
            amount__gte=100
        ).exists()

        files = FileUpload.objects.filter(user=user).order_by('-upload_time')
        activities = ActivityLog.objects.filter(user=user).order_by('-timestamp')[:10]
        payments = PaymentTransaction.objects.filter(user=user).order_by('-timestamp')

    if request.method == "POST":
        if not has_paid:
            messages.error(request, "Payment required to upload files.")
            return redirect('dashboard')

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            messages.error(request, "No file selected for upload.")
            return redirect('dashboard')

        ext = uploaded_file.name.split('.')[-1].lower()
        if ext not in ['txt', 'docx']:
            messages.error(request, "Unsupported file type. Only .txt and .docx allowed.")
            return redirect('dashboard')

        file_upload = FileUpload.objects.create(
            user=user,
            file=uploaded_file,
            filename=uploaded_file.name,
            status='processing'
        )

        ActivityLog.objects.create(
            user=user,
            action="file_uploaded",
            metadata={"filename": file_upload.filename, "file_id": file_upload.id}
        )

        messages.success(request, f"File '{uploaded_file.name}' uploaded successfully.")
        return redirect('dashboard')

    context = {
        'has_paid': has_paid,
        'files': files,
        'activities': activities,
        'payments': payments,
    }
    return render(request, 'dashboard.html', context)
