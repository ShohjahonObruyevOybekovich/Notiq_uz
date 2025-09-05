from common.utils import normalize_e164, detect_encoding_and_segments
from rest_framework import serializers

from .models import Message


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ("to", "text", "sender_id")

    def validate(self, attrs):
        request = self.context.get("request")
        customer = request.user  # set by ApiKeyAuthentication (APIUser)

        try:
            attrs["to"] = normalize_e164(attrs["to"], default_region="UZ")
        except Exception as e:
            raise serializers.ValidationError({"to": str(e)})

        dcs, parts = detect_encoding_and_segments(attrs["text"])
        attrs["dcs"] = dcs
        attrs["parts"] = parts

        # Sender rules (very basic)
        sender = attrs.get("sender_id")
        if sender:
            if len(sender) > 11:
                raise serializers.ValidationError({"sender_id": "Max length is 11 for alphanumeric"})
        return attrs

    def create(self, validated):
        request = self.context.get("request")
        customer_id = request.user.id
        msg = Message.objects.create(
            customer_id=customer_id,
            to=validated["to"],
            text=validated["text"],
            sender_id=validated.get("sender_id"),
            dcs=validated.get("dcs", 0),
            parts=validated.get("parts", 1),
        )
        return msg


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            "id", "to", "sender_id", "text", "dcs", "parts", "status", "price",
            "route", "upstream_message_id", "created_at", "updated_at"
        )
