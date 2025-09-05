import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone

from data.account.models import Customer


class Upstream(models.Model):
    KIND_CHOICES = (
        ("http", "HTTP"),
    )
    name = models.CharField(max_length=64, unique=True)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default="http")
    base_url = models.URLField()
    token = models.CharField(max_length=255, blank=True, null=True)
    tps = models.PositiveIntegerField(default=20, help_text="Throttle messages per second")

    def __str__(self):
        return self.name


class Route(models.Model):
    country = models.CharField(max_length=2, default="UZ")
    upstream = models.ForeignKey(Upstream, on_delete=models.PROTECT, related_name="routes")
    allow_alphanumeric = models.BooleanField(default=True)
    max_sender_len = models.PositiveSmallIntegerField(default=11)

    def __str__(self):
        return f"{self.country} -> {self.upstream.name}"


class Message(models.Model):
    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SUBMITTED = "submitted", "Submitted"
        SENT = "sent", "Sent"
        DELIVERED = "delivered", "Delivered"
        UNDELIVERED = "undelivered", "Undelivered"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="messages")

    to = models.CharField(max_length=32)
    sender_id = models.CharField(max_length=16, blank=True, null=True)
    text = models.TextField()
    dcs = models.PositiveSmallIntegerField(default=0)  # 0=GSM7, 8=UCS2
    parts = models.PositiveSmallIntegerField(default=1)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal("0.0000"))

    route = models.ForeignKey(Route, on_delete=models.PROTECT, related_name="messages", null=True)
    upstream_message_id = models.CharField(max_length=64, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} -> {self.to} [{self.status}]"


class DLRLog(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="dlrs")
    raw_status = models.CharField(max_length=64)
    mapped_status = models.CharField(max_length=16)
    error_code = models.CharField(max_length=64, blank=True, null=True)
    received_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"DLR {self.message_id} {self.mapped_status}"


class InboundMessage(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="inbounds")
    to = models.CharField(max_length=32)
    sender = models.CharField(max_length=32)
    text = models.TextField()
    received_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"MO {self.sender} -> {self.to}"
