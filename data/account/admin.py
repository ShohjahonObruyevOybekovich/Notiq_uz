from django.contrib import admin
from .models import Customer, ApiKey


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "dlr_webhook", "mo_webhook")
    search_fields = ("name", "email")


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "key", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("key", "customer__name")