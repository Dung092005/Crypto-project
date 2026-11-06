"""Mathematical models used by the TASK 09 analysis."""

from __future__ import annotations

import base64
import json
import math
from collections.abc import Sequence

TAG_BYTES = 16
RSA_CIPHERTEXT_BYTES = 256
NONCE_BYTES = 12
FINGERPRINT_HEX_CHARS = 64
E3_FILENAME = "synthetic.bin"
E3_RECIPIENT_IDS = ("Alice", "Bob", "Charlie", "David", "Emma")
E3_CONTENT_ALGORITHM = "AES-256-GCM"
E3_KEY_WRAP_ALGORITHM = "RSA-OAEP-SHA256-MGF1SHA256"


def base64_chars(byte_count: int) -> int:
    """Number of ASCII characters emitted by standard Base64."""
    if byte_count < 0:
        raise ValueError("byte_count must be nonnegative")
    return 4 * math.ceil(byte_count / 3)


def ciphertext_base64_chars(plaintext_bytes: int) -> int:
    return base64_chars(plaintext_bytes + TAG_BYTES)


def canonical_package_skeleton(
    plaintext_bytes: int,
    recipient_ids: Sequence[str] = E3_RECIPIENT_IDS,
    filename: str = E3_FILENAME,
) -> bytes:
    """Build a serializer-shaped package with length-preserving placeholders."""
    if type(plaintext_bytes) is not int or plaintext_bytes < 0:
        raise ValueError("plaintext_bytes must be a nonnegative integer")
    recipients = [
        {
            "fingerprint": "0" * FINGERPRINT_HEX_CHARS,
            "recipient_id": recipient_id,
            "wrapped_key": base64.b64encode(b"0" * RSA_CIPHERTEXT_BYTES).decode("ascii"),
        }
        for recipient_id in recipient_ids
    ]
    document = {
        "header": {
            "content_algorithm": E3_CONTENT_ALGORITHM,
            "filename": filename,
            "format_version": 1,
            "key_wrap_algorithm": E3_KEY_WRAP_ALGORITHM,
            "nonce": base64.b64encode(b"0" * NONCE_BYTES).decode("ascii"),
            "original_size": plaintext_bytes,
            "recipients": recipients,
        },
        "ciphertext": base64.b64encode(b"0" * (plaintext_bytes + TAG_BYTES)).decode("ascii"),
    }
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def predicted_package_size(
    plaintext_bytes: int,
    recipient_count: int,
    *,
    recipient_ids: Sequence[str] = E3_RECIPIENT_IDS,
    filename: str = E3_FILENAME,
) -> int:
    """Exact serialized length for the controlled E3 format."""
    ids = tuple(recipient_ids[:recipient_count])
    if len(ids) != recipient_count or recipient_count < 1:
        raise ValueError("recipient_count must select available recipient IDs")
    return len(canonical_package_skeleton(plaintext_bytes, ids, filename))


def predicted_overhead_bytes(plaintext_bytes: int, recipient_count: int, **kwargs: object) -> int:
    return predicted_package_size(plaintext_bytes, recipient_count, **kwargs) - plaintext_bytes


def metadata_bytes(plaintext_bytes: int, recipient_count: int, **kwargs: object) -> int:
    """Serialized bytes excluding the Base64 encoded ciphertext field value."""
    package_size = predicted_package_size(plaintext_bytes, recipient_count, **kwargs)
    return package_size - ciphertext_base64_chars(plaintext_bytes)


def theoretical_broadcast_condition(message_integer: int, modulus_product: int, exponent: int = 3) -> bool:
    """Return whether M**e < product(N) for the exact CRT-and-root condition."""
    if message_integer < 0 or modulus_product <= 0 or exponent < 1:
        raise ValueError("invalid RSA condition inputs")
    return message_integer**exponent < modulus_product
