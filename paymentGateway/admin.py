from django.contrib import admin
from .models import FileUpload, PaymentTransaction, ActivityLog

class FileUploadAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "filename", "status", "word_count", "upload_time")
    readonly_fields = ("user", "filename", "upload_time", "status", "word_count", "file")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "user", "amount", "status", "timestamp")
    readonly_fields = ("user", "transaction_id", "amount", "status", "gateway_response", "timestamp")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "timestamp")
    readonly_fields = ("user", "action", "metadata", "timestamp")

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(PaymentTransaction, PaymentTransactionAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)
