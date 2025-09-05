from abc import ABC, abstractmethod


class UpstreamClient(ABC):
    @abstractmethod
    def send_sms(self, to: str, text: str, sender: str | None, dcs: int) -> str:
        """Send SMS, return upstream message id."""
        raise NotImplementedError