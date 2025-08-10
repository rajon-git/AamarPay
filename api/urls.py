from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth import views as auth_views
from paymentGateway import views as paymentviews

urlpatterns = [
    path('register/', views.RegisterAPI.as_view(), name='register'),
    path("login/", TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   
    path('initiate-payment/', paymentviews.InitiatePaymentView.as_view(), name='initiate-payment'),
    path('payment/success/', paymentviews.PaymentSuccessView.as_view(), name='payment-success'),
    path('payment/fail/', paymentviews.PaymentFailView.as_view(), name='payment-fail'),
    path('payment/cancel/', paymentviews.PaymentCancelView.as_view(), name='payment-cancel'),

    path("upload/", paymentviews.UploadFileView.as_view(), name="file-upload"),
    path("files/", paymentviews.ListFilesView.as_view(), name="list-files"),
    path("activity/", paymentviews.ListActivityView.as_view(), name="list-activity"),
    path("transactions/", paymentviews.ListTransactionsView.as_view(), name="list-transactions"),
]