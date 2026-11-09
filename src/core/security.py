"""Security, credential masking, and encryption helpers."""

import base64
import hashlib
from typing import Optional
from src.core.config import settings


def mask_credential(secret: Optional[str]) -> str:
    """Mask a sensitive credential for safe display in logs or UI."""
    if not secret:
        return "<EMPTY>"
    if len(secret) <= 8:
        return "********"
    return f"{secret[:4]}...{secret[-4:]}"


def derive_key_from_secret(secret: str) -> bytes:
    """Derive a 32-byte url-safe base64 key suitable for Fernet from the SECRET_KEY."""
    digest = hashlib.sha256(secret.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)
