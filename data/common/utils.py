import phonenumbers
from typing import Tuple

GSM_7_BASIC = (
    "@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;" \
    "<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ§¿abcdefghijklmnopqrstuvwxyzäöñüà"
)


def normalize_e164(raw: str, default_region: str = "UZ") -> str:
    """Normalize phone number to E.164. Raises ValueError if invalid."""


    num = phonenumbers.parse(raw, default_region)
    if not phonenumbers.is_valid_number(num):
        raise ValueError("Invalid phone number")
    return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)


def detect_encoding_and_segments(text: str) -> Tuple[int, int]:


    """Return (data_coding, segments). 0=GSM-7, 8=UCS-2."""
    dcs = 0
    try:
        for ch in text:
            if ch not in GSM_7_BASIC:
                dcs = 8
                break
    except Exception:
        dcs = 8

    if dcs == 0:
        single = 160
        concat = 153
    else:
        single = 70
        concat = 67

    length = len(text)
    if length <= single:
        return dcs, 1
    # compute ceil(length/concat)
    segments = (length + concat - 1) // concat
    return dcs, segments
