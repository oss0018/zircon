"""AES-256 encryption service for API keys."""

import base64
import os
import logging
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.config import settings

logger = logging.getLogger(__name__)


def _get_key() -> bytes:
    """Get the 32-byte encryption key."""
    key_bytes = base64.b64decode(settings.ENCRYPTION_KEY)
    if len(key_bytes) < 32:
        key_bytes = key_bytes.ljust(32, b'\x00')
    return key_bytes[:32]


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string value using AES-256-GCM."""
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    combined = nonce + ciphertext
    return base64.b64encode(combined).decode("utf-8")


def decrypt_value(encrypted: str) -> str:
    """Decrypt a string value using AES-256-GCM."""
    key = _get_key()
    aesgcm = AESGCM(key)
    combined = base64.b64decode(encrypted.encode("utf-8"))
    nonce = combined[:12]
    ciphertext = combined[12:]
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
