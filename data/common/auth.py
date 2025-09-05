from typing import Optional, Tuple

from accounts.models import ApiKey
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class APIUser:
    """Lightweight auth user holding customer context."""

    def __init__(self, customer_id: int, key_id: int):
        self.id = customer_id
        self.is_authenticated = True
        self.apikey_id = key_id


class ApiKeyAuthentication(BaseAuthentication):
    keyword = "X-API-Key"

    def authenticate(self, request) -> Optional[Tuple[APIUser, None]]:
        key = request.headers.get(self.keyword)
        if not key:
            return None
        try:
            api_key = ApiKey.objects.select_related("customer").get(key=key, is_active=True)
        except ApiKey.DoesNotExist:
            raise AuthenticationFailed("Invalid API key")
        return APIUser(api_key.customer_id, api_key.id), None

    def authenticate_header(self, request):
        return self.keyword
