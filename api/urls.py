from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.contrib.auth import views as auth_views
from paymentGateway import views as paymentviews
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Payment Gateway Integration and Files Uploading System",
        default_version='v1',
        description="API Documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
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