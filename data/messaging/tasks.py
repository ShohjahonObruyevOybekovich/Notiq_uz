from celery import shared_task
from django.db import transaction
from integrations.http_client import HttpUpstreamClient

from .models import Message
from .routing import select_route, bootstrap_env_upstreams


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_message_task(self, message_id: str):
    # Ensure env upstreams exist (idempotent)
    bootstrap_env_upstreams()

    with transaction.atomic():
        msg = Message.objects.select_for_update().get(id=message_id)
        if msg.status not in [Message.Status.QUEUED, Message.Status.FAILED]:
            return
        route = select_route(country="UZ")
        msg.route = route
        msg.status = Message.Status.SUBMITTED
        msg.save()

    client = HttpUpstreamClient(route.upstream)
    upstream_id = client.send_sms(
        to=msg.to,
        text=msg.text,
        sender=msg.sender_id,
        dcs=msg.dcs,
    )

    Message.objects.filter(id=message_id).update(
        upstream_message_id=upstream_id,
        status=Message.Status.SENT,
    )
