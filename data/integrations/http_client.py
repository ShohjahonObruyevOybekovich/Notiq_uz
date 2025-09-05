import time

import httpx

from .base import UpstreamClient


class HttpUpstreamClient(UpstreamClient):
    def __init__(self, upstream):
        self.upstream = upstream
        self.client = httpx.Client(timeout=10.0)

        def _headers(self):
            headers = {"Content-Type": "application/json"}
            if self.upstream.token:
                headers["Authorization"] = f"Bearer {self.upstream.token}"
            return headers

    def send_sms(self, to: str, text: str, sender: str | None, dcs: int) -> str:
        payload = {
            "to": to,
            "text": text,
            "sender_id": sender,
            "dcs": dcs,
            "dlr_callback": "${PUBLIC_BASE_URL}/api/v1/webhooks/dlr",  # replace with your public URL
        }
        # Simple TPS limiter (sleep). For prod use distributed rate limiting.
        time.sleep(1.0 / max(self.upstream.tps, 1))
        r = self.client.post(self.upstream.base_url, json=payload, headers=self._headers())
        r.raise_for_status()
        data = r.json()

        # Expect upstream to return {"id": "<their-id>"}
        return str(data.get("id") or data.get("message_id") or "")
