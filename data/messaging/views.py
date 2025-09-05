from typing import Any, Dict

from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Message, DLRLog, InboundMessage
from .serializers import MessageCreateSerializer, MessageSerializer
from .tasks import send_message_task


class MessageViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    queryset = Message.objects.all().order_by('-created_at')
    serializer_class = MessageSerializer
    filterset_fields = ("status",)
    search_fields = ("to", "sender_id", "upstream_message_id")
    ordering_fields = ("created_at", "status")

    def get_queryset(self):
        # Scope to current customer
        return super().get_queryset().filter(customer_id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        msg = ser.save()
        # Enqueue async send
        send_message_task.delay(str(msg.id))
        return Response({"id": str(msg.id), "status": msg.status}, status=status.HTTP_202_ACCEPTED)


@api_view(["POST"])
@permission_classes([AllowAny])
def dlr_webhook(request):
    """Generic DLR webhook; map vendor fields to our model.
    Expect JSON like: {"message_id": "uuid", "status": "DELIVRD", "error_code": ""}
    """
    try:
        data: Dict[str, Any] = request.data
        message_id = data.get("message_id") or data.get("id")
        raw_status = (data.get("status") or "").upper()
        error_code = data.get("error_code")
        msg = Message.objects.get(id=message_id)
    except Exception:
        return Response({"ok": False, "error": "invalid payload"}, status=400)

    map_table = {
        "DELIVRD": Message.Status.DELIVERED,
        "DELIVERED": Message.Status.DELIVERED,
        "UNDELIV": Message.Status.UNDELIVERED,
        "UNDELIVERED": Message.Status.UNDELIVERED,
        "EXPIRED": Message.Status.EXPIRED,
        "REJECTED": Message.Status.REJECTED,
        "FAILED": Message.Status.FAILED,
        "SENT": Message.Status.SENT,
    }
    mapped = map_table.get(raw_status, Message.Status.SENT)

    DLRLog.objects.create(
        message=msg,
        raw_status=raw_status,
        mapped_status=mapped,
        error_code=error_code,
        received_at=timezone.now(),
    )
    msg.status = mapped
    msg.save(update_fields=["status", "updated_at"])

    return Response({"ok": True})


@api_view(["POST"])
@permission_classes([AllowAny])
def mo_webhook(request):
    """Inbound MO webhook; expect {to, from, text, customer_id?}
    In production you'd validate signatures/whitelist IPs."""
    data = request.data
    try:
        to = data["to"]
        sender = data["from"]
        text = data.get("text", "")
        customer_id = data.get("customer_id")  # Optional: map by number instead
    except KeyError:
        return Response({"ok": False, "error": "missing fields"}, status=400)

    if not customer_id:
        # If you run dedicated numbers per customer, look up by 'to' mapping
        return Response({"ok": False, "error": "customer_id required for demo"}, status=400)

    InboundMessage.objects.create(
        customer_id=customer_id,
        to=to,
        sender=sender,
        text=text,
    )
    return Response({"ok": True})
