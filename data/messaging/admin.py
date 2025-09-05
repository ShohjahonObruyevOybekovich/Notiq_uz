from django.contrib import admin
from .models import Message, DLRLog, InboundMessage, Route, Upstream


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "customer", "to", "sender_id", "status", "route", "upstream_message_id", "created_at")
    list_filter = ("status", "route__country", "customer")
    search_fields = ("to", "sender_id", "id", "upstream_message_id")


@admin.register(DLRLog)
class DLRLogAdmin(admin.ModelAdmin):
    list_display = ("message", "mapped_status", "raw_status", "error_code", "received_at")
    search_fields = ("message__id", "raw_status")


@admin.register(InboundMessage)
class InboundAdmin(admin.ModelAdmin):
    list_display = ("customer", "sender", "to", "received_at")
    search_fields = ("sender", "to")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("country", "upstream", "allow_alphanumeric", "max_sender_len")
    list_filter = ("country", "upstream")


@admin.register(Upstream)
class UpstreamAdmin(admin.ModelAdmin):
    list_display = ("name", "kind", "base_url", "tps")
    search_fields = ("name", "base_url")