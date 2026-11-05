"""Versioned, local multi-recipient hybrid file encryption.

AES-GCM encrypts the file once. RSA-OAEP independently wraps the fresh AES key
for each recipient. Public keys must be authenticated before calling this API;
the package does not authenticate its sender or prevent replay/replacement.
"""

import base64
import binascii
from collections.abc import Sequence
from dataclasses import dataclass, field
import hashlib
import hmac
import json
import re
import secrets
from typing import Literal

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


FORMAT_VERSION = 1
CONTENT_ALGORITHM = "AES-256-GCM"
KEY_WRAP_ALGORITHM = "RSA-OAEP-SHA256-MGF1SHA256"
MAX_FILE_BYTES = 5 * 1024 * 1024
MAX_PACKAGE_BYTES = 8 * 1024 * 1024
MAX_RECIPIENTS = 5
AES_KEY_BYTES = 32
NONCE_BYTES = 12
TAG_BYTES = 16
RSA_KEY_BYTES = 256
DEMO_NAMES = ("Alice", "Bob", "Charlie", "David", "Emma")
_ID_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")
_FINGERPRINT_RE = re.compile(r"[0-9a-f]{64}\Z")


class PackageValidationError(ValueError):
    """The package structure or supported format is invalid."""


class DecryptionFailed(Exception):
    """A recipient cannot authenticate and recover this file."""


@dataclass(frozen=True)
class PublicRecipient:
    recipient_id: str
    public_key: rsa.RSAPublicKey = field(repr=False)

    @property
    def fingerprint(self) -> str:
        return public_key_fingerprint(self.public_key)


@dataclass(frozen=True)
class DemoRecipient:
    """Session-only key pair; never put this object into an encrypted package."""

    recipient_id: str
    private_key: rsa.RSAPrivateKey = field(repr=False)

    @property
    def public(self) -> PublicRecipient:
        return PublicRecipient(self.recipient_id, self.private_key.public_key())


@dataclass(frozen=True)
class WrappedKeyEntry:
    recipient_id: str
    fingerprint: str
    wrapped_key: bytes


@dataclass(frozen=True)
class PackageHeader:
    format_version: int
    content_algorithm: str
    key_wrap_algorithm: str
    filename: str
    original_size: int
    nonce: bytes
    recipients: tuple[WrappedKeyEntry, ...]


@dataclass(frozen=True)
class EncryptedPackage:
    header: PackageHeader
    encrypted_content: bytes  # AESGCM output: ciphertext || 16-byte tag.


@dataclass(frozen=True)
class PackageSummary:
    filename: str
    original_size: int
    package_size: int
    recipient_count: int
    recipient_ids: tuple[str, ...]
    fingerprint_previews: tuple[str, ...]
    content_algorithm: str
    key_wrap_algorithm: str
    encryption_status: Literal["encrypted"] = "encrypted"


@dataclass(frozen=True)
class DecryptionAttempt:
    """UI-facing outcome; no key material and no partial plaintext on failure."""

    status: Literal["decrypted", "invalid_package", "decryption_failed"]
    data: bytes | None


def _oaep() -> padding.OAEP:
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )


def _validate_public_key(key: object) -> rsa.RSAPublicKey:
    if not isinstance(key, rsa.RSAPublicKey):
        raise TypeError("Each recipient must supply an RSA public key.")
    numbers = key.public_numbers()
    if key.key_size != 2048 or numbers.e != 65537:
        raise ValueError("Recipient public keys must be RSA-2048 with e=65537.")
    return key


def public_key_fingerprint(public_key: rsa.RSAPublicKey) -> str:
    """Lowercase SHA-256 hex of DER SubjectPublicKeyInfo."""
    key = _validate_public_key(public_key)
    der = key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(der).hexdigest()


def generate_demo_recipients(count: int) -> tuple[DemoRecipient, ...]:
    """Generate independent RSA key pairs for one local demo session."""
    if not isinstance(count, int) or isinstance(count, bool):
        raise TypeError("count must be an integer.")
    if not 1 <= count <= MAX_RECIPIENTS:
        raise ValueError("count must be between 1 and 5.")
    return tuple(
        DemoRecipient(name, rsa.generate_private_key(public_exponent=65537, key_size=2048))
        for name in DEMO_NAMES[:count]
    )


def _validate_recipient_id(recipient_id: object) -> str:
    if not isinstance(recipient_id, str) or _ID_RE.fullmatch(recipient_id) is None:
        raise ValueError("recipient_id must be 1-64 ASCII letters, digits, '_' or '-', starting with a letter.")
    return recipient_id


def _validate_filename(filename: object) -> str:
    if not isinstance(filename, str):
        raise TypeError("filename must be a string.")
    try:
        encoded_length = len(filename.encode("utf-8"))
    except UnicodeEncodeError as error:
        raise ValueError("filename must be valid UTF-8 text.") from error
    if (not filename or filename in (".", "..") or "/" in filename or "\\" in filename
            or any(char in '<>:"|?*' for char in filename)
            or filename.endswith((" ", "."))
            or any(ord(char) < 32 or ord(char) == 127 for char in filename)
            or encoded_length > 255):
        raise ValueError("filename must be a safe display-only basename of at most 255 UTF-8 bytes.")
    return filename


def _validate_public_recipients(recipients: object) -> tuple[PublicRecipient, ...]:
    if not isinstance(recipients, Sequence) or isinstance(recipients, (str, bytes, bytearray)):
        raise TypeError("recipients must be a sequence of PublicRecipient.")
    selected = tuple(recipients)
    if not 1 <= len(selected) <= MAX_RECIPIENTS:
        raise ValueError("Choose between 1 and 5 recipients.")
    ids: set[str] = set()
    fingerprints: set[str] = set()
    for recipient in selected:
        if not isinstance(recipient, PublicRecipient):
            raise TypeError("Each recipient must be a PublicRecipient.")
        recipient_id = _validate_recipient_id(recipient.recipient_id)
        fingerprint = recipient.fingerprint
        if recipient_id in ids or fingerprint in fingerprints:
            raise ValueError("Recipient IDs and public keys must be unique.")
        ids.add(recipient_id)
        fingerprints.add(fingerprint)
    return selected


def _b64encode(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _b64decode(value: object, name: str) -> bytes:
    if not isinstance(value, str):
        raise PackageValidationError(f"{name} must be Base64 text.")
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as error:
        raise PackageValidationError(f"{name} is malformed Base64.") from error
    if _b64encode(raw) != value:
        raise PackageValidationError(f"{name} must use canonical Base64.")
    return raw


def _header_object(header: PackageHeader) -> dict:
    return {
        "format_version": header.format_version,
        "content_algorithm": header.content_algorithm,
        "key_wrap_algorithm": header.key_wrap_algorithm,
        "filename": header.filename,
        "original_size": header.original_size,
        "nonce": _b64encode(header.nonce),
        "recipients": [
            {
                "recipient_id": entry.recipient_id,
                "fingerprint": entry.fingerprint,
                "wrapped_key": _b64encode(entry.wrapped_key),
            }
            for entry in header.recipients
        ],
    }


def _canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                      allow_nan=False).encode("utf-8")


def _aad(header: PackageHeader) -> bytes:
    """Canonical UTF-8 JSON header, including every wrapped-key entry."""
    return _canonical_json(_header_object(header))


def _validate_header(header: object) -> PackageHeader:
    if not isinstance(header, PackageHeader):
        raise PackageValidationError("header must be a PackageHeader.")
    if type(header.format_version) is not int or header.format_version != FORMAT_VERSION:
        raise PackageValidationError("Unsupported package format version.")
    if header.content_algorithm != CONTENT_ALGORITHM or header.key_wrap_algorithm != KEY_WRAP_ALGORITHM:
        raise PackageValidationError("Unsupported encryption algorithm.")
    try:
        _validate_filename(header.filename)
    except (TypeError, ValueError) as error:
        raise PackageValidationError("Invalid display filename.") from error
    if type(header.original_size) is not int or not 0 <= header.original_size <= MAX_FILE_BYTES:
        raise PackageValidationError("Invalid original file size.")
    if not isinstance(header.nonce, bytes) or len(header.nonce) != NONCE_BYTES:
        raise PackageValidationError("AES-GCM nonce must be 12 bytes.")
    if not isinstance(header.recipients, tuple) or not 1 <= len(header.recipients) <= MAX_RECIPIENTS:
        raise PackageValidationError("Package must contain 1-5 recipient entries.")
    ids: set[str] = set()
    fingerprints: set[str] = set()
    for entry in header.recipients:
        if not isinstance(entry, WrappedKeyEntry):
            raise PackageValidationError("Malformed recipient entry.")
        try:
            _validate_recipient_id(entry.recipient_id)
        except ValueError as error:
            raise PackageValidationError("Invalid recipient ID.") from error
        if not isinstance(entry.fingerprint, str) or not _FINGERPRINT_RE.fullmatch(entry.fingerprint):
            raise PackageValidationError("Invalid public-key fingerprint.")
        if not isinstance(entry.wrapped_key, bytes) or len(entry.wrapped_key) != RSA_KEY_BYTES:
            raise PackageValidationError("Wrapped AES key must be one RSA-2048 ciphertext.")
        if entry.recipient_id in ids or entry.fingerprint in fingerprints:
            raise PackageValidationError("Duplicate recipient ID or public key.")
        ids.add(entry.recipient_id)
        fingerprints.add(entry.fingerprint)
    return header


def _validate_package(package: object) -> EncryptedPackage:
    if not isinstance(package, EncryptedPackage):
        raise PackageValidationError("Expected an EncryptedPackage.")
    _validate_header(package.header)
    content = package.encrypted_content
    if not isinstance(content, bytes) or len(content) != package.header.original_size + TAG_BYTES:
        raise PackageValidationError("Encrypted content length does not match the header and 16-byte tag.")
    return package


def encrypt_file_for_recipients(
    data: bytes, filename: str, recipients: Sequence[PublicRecipient]
) -> EncryptedPackage:
    """Encrypt file bytes once; wrap one fresh AES key for each public key."""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes.")
    if len(data) > MAX_FILE_BYTES:
        raise ValueError("File exceeds the 5 MiB educational limit.")
    _validate_filename(filename)
    selected = _validate_public_recipients(recipients)
    key = AESGCM.generate_key(bit_length=256)
    nonce = secrets.token_bytes(NONCE_BYTES)
    entries = tuple(
        WrappedKeyEntry(recipient.recipient_id, recipient.fingerprint,
                        recipient.public_key.encrypt(key, _oaep()))
        for recipient in selected
    )
    header = PackageHeader(FORMAT_VERSION, CONTENT_ALGORITHM, KEY_WRAP_ALGORITHM,
                           filename, len(data), nonce, entries)
    encrypted_content = AESGCM(key).encrypt(nonce, data, _aad(header))
    return _validate_package(EncryptedPackage(header, encrypted_content))


def serialize_package(package: EncryptedPackage) -> bytes:
    """Canonical UTF-8 JSON; Base64 represents all binary fields."""
    valid = _validate_package(package)
    encoded = _canonical_json({
        "header": _header_object(valid.header),
        "ciphertext": _b64encode(valid.encrypted_content),
    })
    if len(encoded) > MAX_PACKAGE_BYTES:
        raise PackageValidationError("Serialized package exceeds the 8 MiB limit.")
    return encoded


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise PackageValidationError(f"Duplicate JSON key: {key}.")
        result[key] = value
    return result


def _parse_constant(value: str) -> None:
    raise PackageValidationError(f"Non-JSON numeric constant: {value}.")


def _require_keys(value: object, expected: set[str], name: str) -> dict:
    if not isinstance(value, dict) or set(value) != expected:
        raise PackageValidationError(f"{name} has missing or unknown fields.")
    return value


def deserialize_package(data: bytes) -> EncryptedPackage:
    """Bound, parse, and validate untrusted bytes before any decryption."""
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes.")
    if not data or len(data) > MAX_PACKAGE_BYTES:
        raise PackageValidationError("Package is empty or exceeds the 8 MiB limit.")
    try:
        document = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_pairs,
                              parse_constant=_parse_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError, ValueError) as error:
        raise PackageValidationError("Malformed package JSON.") from error
    top = _require_keys(document, {"header", "ciphertext"}, "package")
    raw_header = _require_keys(top["header"], {
        "format_version", "content_algorithm", "key_wrap_algorithm", "filename",
        "original_size", "nonce", "recipients",
    }, "header")
    raw_entries = raw_header["recipients"]
    if not isinstance(raw_entries, list) or not 1 <= len(raw_entries) <= MAX_RECIPIENTS:
        raise PackageValidationError("Package must contain 1-5 recipient entries.")
    entries = []
    for raw in raw_entries:
        entry = _require_keys(raw, {"recipient_id", "fingerprint", "wrapped_key"}, "recipient")
        entries.append(WrappedKeyEntry(entry["recipient_id"], entry["fingerprint"],
                                       _b64decode(entry["wrapped_key"], "wrapped_key")))
    header = PackageHeader(
        raw_header["format_version"], raw_header["content_algorithm"],
        raw_header["key_wrap_algorithm"], raw_header["filename"],
        raw_header["original_size"], _b64decode(raw_header["nonce"], "nonce"),
        tuple(entries),
    )
    _validate_header(header)
    content = _b64decode(top["ciphertext"], "ciphertext")
    return _validate_package(EncryptedPackage(header, content))


def decrypt_file_for_recipient(
    package: EncryptedPackage | bytes, recipient_id: str, private_key: rsa.RSAPrivateKey
) -> bytes:
    """Return bytes only after OAEP key unwrap and AES-GCM authentication pass."""
    valid = deserialize_package(package) if isinstance(package, bytes) else _validate_package(package)
    try:
        _validate_recipient_id(recipient_id)
    except ValueError:
        raise DecryptionFailed("Recipient cannot decrypt this package.") from None
    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise DecryptionFailed("Recipient cannot decrypt this package.")
    entry = next((item for item in valid.header.recipients if item.recipient_id == recipient_id), None)
    if entry is None:
        raise DecryptionFailed("Recipient cannot decrypt this package.")
    try:
        fingerprint = public_key_fingerprint(private_key.public_key())
    except (TypeError, ValueError):
        raise DecryptionFailed("Recipient cannot decrypt this package.") from None
    if not hmac.compare_digest(fingerprint, entry.fingerprint):
        raise DecryptionFailed("Recipient cannot decrypt this package.")
    try:
        key = private_key.decrypt(entry.wrapped_key, _oaep())
        if len(key) != AES_KEY_BYTES:
            raise DecryptionFailed("Recipient cannot decrypt this package.")
        plaintext = AESGCM(key).decrypt(valid.header.nonce, valid.encrypted_content,
                                        _aad(valid.header))
    except (ValueError, InvalidTag):
        raise DecryptionFailed("Recipient cannot decrypt this package.") from None
    if len(plaintext) != valid.header.original_size:
        raise DecryptionFailed("Recipient cannot decrypt this package.")
    return plaintext


def summarize_package(package: EncryptedPackage) -> PackageSummary:
    """Short, public-only details for a later UI."""
    valid = _validate_package(package)
    return PackageSummary(
        valid.header.filename, valid.header.original_size, len(serialize_package(valid)),
        len(valid.header.recipients),
        tuple(item.recipient_id for item in valid.header.recipients),
        tuple(item.fingerprint[:12] + "…" for item in valid.header.recipients),
        valid.header.content_algorithm, valid.header.key_wrap_algorithm,
    )


def attempt_decrypt_file_for_recipient(
    package: EncryptedPackage | bytes, recipient_id: str, private_key: rsa.RSAPrivateKey
) -> DecryptionAttempt:
    """Convert controlled exceptions to semantic UI states without guessing cause."""
    try:
        data = decrypt_file_for_recipient(package, recipient_id, private_key)
    except PackageValidationError:
        return DecryptionAttempt("invalid_package", None)
    except DecryptionFailed:
        return DecryptionAttempt("decryption_failed", None)
    return DecryptionAttempt("decrypted", data)
