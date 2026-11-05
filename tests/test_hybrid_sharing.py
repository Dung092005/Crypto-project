"""Hybrid sharing invariants, untrusted format handling, and tamper rejection."""

from dataclasses import fields, replace
import hashlib
import json
import secrets

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from broadcastguard.hybrid_sharing import (
    AES_KEY_BYTES,
    CONTENT_ALGORITHM,
    KEY_WRAP_ALGORITHM,
    MAX_FILE_BYTES,
    MAX_PACKAGE_BYTES,
    DecryptionFailed,
    EncryptedPackage,
    PackageValidationError,
    PublicRecipient,
    attempt_decrypt_file_for_recipient,
    decrypt_file_for_recipient,
    deserialize_package,
    encrypt_file_for_recipients,
    generate_demo_recipients,
    public_key_fingerprint,
    serialize_package,
    summarize_package,
)


@pytest.fixture(scope="module")
def recipients():
    return generate_demo_recipients(5)


@pytest.fixture(scope="module")
def package3(recipients):
    data = b"BroadcastGuard demonstration file: " + b"A" * 80
    package = encrypt_file_for_recipients(data, "secret_exam.txt",
                                          tuple(item.public for item in recipients[:3]))
    return data, package


def _json_bytes(value: dict) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def _mutate_json(package: EncryptedPackage, change) -> bytes:
    document = json.loads(serialize_package(package))
    change(document)
    return _json_bytes(document)


@pytest.mark.parametrize("count", [1, 3, 5])
def test_every_selected_recipient_recovers_same_bytes(recipients, count: int) -> None:
    data = b"A\x00B" * 29
    package = encrypt_file_for_recipients(data, "sample.bin",
                                          tuple(item.public for item in recipients[:count]))
    assert len(package.header.recipients) == count
    for recipient in recipients[:count]:
        assert decrypt_file_for_recipient(package, recipient.recipient_id, recipient.private_key) == data


@pytest.mark.parametrize("data", [
    "Xin chào USTH 👋".encode("utf-8"),
    b"\x00" * 128 + b"\xff\x00\x01",
    b"",
    b"X" * 10_000,
    b"Y" * 100_000,
    b"Z" * (1024 * 1024),
], ids=["utf8", "zero_bytes", "empty", "10kb", "100kb", "1mib"])
def test_file_types_and_sizes_round_trip(recipients, data: bytes) -> None:
    package = encrypt_file_for_recipients(data, "tệp thử.bin", (recipients[0].public,))
    encoded = serialize_package(package)
    imported = deserialize_package(encoded)
    assert imported == package
    assert serialize_package(imported) == encoded
    assert decrypt_file_for_recipient(imported, "Alice", recipients[0].private_key) == data
    assert len(package.encrypted_content) == len(data) + 16


def test_random_binary_and_maximum_file(recipients) -> None:
    random_data = secrets.token_bytes(4096)
    package = encrypt_file_for_recipients(random_data, "random.bin", (recipients[0].public,))
    assert decrypt_file_for_recipient(package, "Alice", recipients[0].private_key) == random_data
    maximum = b"Q" * MAX_FILE_BYTES
    package = encrypt_file_for_recipients(maximum, "maximum.bin", (recipients[0].public,))
    assert len(serialize_package(package)) <= MAX_PACKAGE_BYTES
    assert decrypt_file_for_recipient(package, "Alice", recipients[0].private_key) == maximum


def test_bad_encryption_inputs_rejected_before_crypto(recipients) -> None:
    with pytest.raises(ValueError, match="5 MiB"):
        encrypt_file_for_recipients(b"X" * (MAX_FILE_BYTES + 1), "x.bin", (recipients[0].public,))
    for data in (None, "text", bytearray(b"x")):
        with pytest.raises(TypeError):
            encrypt_file_for_recipients(data, "x.bin", (recipients[0].public,))
    for filename in ("../bad", "sub/file", "sub\\file", "C:bad.txt", "bad?.txt",
                     "trailing.", ".", "", "x\x00.txt", "X" * 256, "\ud800"):
        with pytest.raises((ValueError, TypeError)):
            encrypt_file_for_recipients(b"x", filename, (recipients[0].public,))
    with pytest.raises(TypeError):
        encrypt_file_for_recipients(b"x", None, (recipients[0].public,))


def test_bad_recipient_lists_and_keys(recipients) -> None:
    for selected in ((), tuple(item.public for item in recipients) + (recipients[0].public,)):
        with pytest.raises(ValueError):
            encrypt_file_for_recipients(b"x", "x.bin", selected)
    with pytest.raises(ValueError, match="unique"):
        encrypt_file_for_recipients(b"x", "x.bin", (recipients[0].public, recipients[0].public))
    with pytest.raises(ValueError, match="unique"):
        encrypt_file_for_recipients(b"x", "x.bin", (
            recipients[0].public, PublicRecipient("Other", recipients[0].public.public_key)
        ))
    with pytest.raises(ValueError, match="unique"):
        encrypt_file_for_recipients(b"x", "x.bin", (
            recipients[0].public, PublicRecipient("Alice", recipients[1].public.public_key)
        ))
    with pytest.raises(TypeError):
        encrypt_file_for_recipients(b"x", "x.bin", "Alice")
    with pytest.raises(TypeError):
        encrypt_file_for_recipients(b"x", "x.bin", ("Alice",))
    old_key = rsa.generate_private_key(public_exponent=3, key_size=2048).public_key()
    with pytest.raises(ValueError, match="e=65537"):
        encrypt_file_for_recipients(b"x", "x.bin", (PublicRecipient("Wrong", old_key),))
    with pytest.raises(ValueError, match="recipient_id"):
        encrypt_file_for_recipients(b"x", "x.bin", (PublicRecipient("../bad", recipients[0].public.public_key),))


def test_demo_recipients_and_fingerprints(recipients) -> None:
    assert [item.recipient_id for item in recipients] == ["Alice", "Bob", "Charlie", "David", "Emma"]
    for item in recipients:
        assert item.private_key.key_size == 2048
        assert item.public.public_key.public_numbers().e == 65537
        der = item.public.public_key.public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        assert item.public.fingerprint == hashlib.sha256(der).hexdigest()
        assert public_key_fingerprint(item.private_key.public_key()) == item.public.fingerprint
        assert "private_key" not in repr(item)
    for count in (0, 6):
        with pytest.raises(ValueError):
            generate_demo_recipients(count)
    with pytest.raises(TypeError):
        generate_demo_recipients(True)


def test_summary_and_no_secret_fields(package3) -> None:
    data, package = package3
    summary = summarize_package(package)
    assert summary.filename == "secret_exam.txt" and summary.original_size == len(data)
    assert summary.package_size == len(serialize_package(package))
    assert summary.recipient_count == 3
    assert summary.recipient_ids == ("Alice", "Bob", "Charlie")
    assert all(len(value) < 20 for value in summary.fingerprint_previews)
    assert summary.content_algorithm == CONTENT_ALGORITHM
    assert summary.key_wrap_algorithm == KEY_WRAP_ALGORITHM
    assert summary.encryption_status == "encrypted"
    document = json.loads(serialize_package(package))
    assert set(document) == {"header", "ciphertext"}
    assert set(document["header"]) == {
        "format_version", "content_algorithm", "key_wrap_algorithm", "filename",
        "original_size", "nonce", "recipients",
    }
    assert all(set(entry) == {"recipient_id", "fingerprint", "wrapped_key"}
               for entry in document["header"]["recipients"])
    assert "private_key" not in serialize_package(package).decode("utf-8")
    assert "aes_key" not in serialize_package(package).decode("utf-8")
    assert "plaintext" not in serialize_package(package).decode("utf-8")
    assert not any("private" in field.name for field in fields(EncryptedPackage))


def test_wrong_private_key_and_recipient_id(recipients, package3) -> None:
    _, package = package3
    with pytest.raises(DecryptionFailed, match="Recipient cannot decrypt"):
        decrypt_file_for_recipient(package, "Alice", recipients[1].private_key)
    with pytest.raises(DecryptionFailed):
        decrypt_file_for_recipient(package, "Emma", recipients[4].private_key)
    with pytest.raises(DecryptionFailed):
        decrypt_file_for_recipient(package, "../Alice", recipients[0].private_key)
    outsider = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with pytest.raises(DecryptionFailed):
        decrypt_file_for_recipient(package, "Alice", outsider)


def test_wrapped_key_is_32_bytes_after_oaep_unwrap(recipients, package3) -> None:
    _, package = package3
    for person, entry in zip(recipients, package.header.recipients):
        key = person.private_key.decrypt(entry.wrapped_key, padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
        ))
        assert len(key) == AES_KEY_BYTES


def test_new_aes_key_nonce_and_package_each_time(recipients) -> None:
    public = (recipients[0].public,)
    first = encrypt_file_for_recipients(b"same file", "same.bin", public)
    second = encrypt_file_for_recipients(b"same file", "same.bin", public)
    unwrap = lambda package: recipients[0].private_key.decrypt(
        package.header.recipients[0].wrapped_key,
        padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                     algorithm=hashes.SHA256(), label=None),
    )
    assert unwrap(first) != unwrap(second)
    assert first.header.nonce != second.header.nonce
    assert first.encrypted_content != second.encrypted_content
    assert serialize_package(first) != serialize_package(second)


def test_file_is_encrypted_once_for_five_recipients(monkeypatch, recipients) -> None:
    actual_encrypt = AESGCM.encrypt
    calls = []

    def counted_encrypt(self, nonce, data, associated_data):
        calls.append((nonce, data, associated_data))
        return actual_encrypt(self, nonce, data, associated_data)

    monkeypatch.setattr(AESGCM, "encrypt", counted_encrypt)
    data = b"one encryption" * 10
    package = encrypt_file_for_recipients(data, "once.bin", tuple(item.public for item in recipients))
    assert len(calls) == 1
    assert calls[0][1] == data
    assert calls[0][2].startswith(b"{")
    assert len(package.header.recipients) == 5


def test_textbook_rsa_module_is_not_used(monkeypatch, recipients) -> None:
    import broadcastguard.attack_lab as attack_lab
    import broadcastguard.math_core as math_core

    def forbidden(*args, **kwargs):
        raise AssertionError("Textbook RSA was invoked by Secure Sharing")

    monkeypatch.setattr(attack_lab, "build_scenario", forbidden)
    monkeypatch.setattr(attack_lab, "attack_observations", forbidden)
    monkeypatch.setattr(math_core, "broadcast_attack", forbidden)
    package = encrypt_file_for_recipients(b"safe test", "safe.txt", (recipients[0].public,))
    assert decrypt_file_for_recipient(package, "Alice", recipients[0].private_key) == b"safe test"


@pytest.mark.parametrize("change", [
    lambda p: replace(p, encrypted_content=bytes([p.encrypted_content[0] ^ 1]) + p.encrypted_content[1:]),
    lambda p: replace(p, encrypted_content=p.encrypted_content[:-1] + bytes([p.encrypted_content[-1] ^ 1])),
    lambda p: replace(p, header=replace(p.header, nonce=bytes([p.header.nonce[0] ^ 1]) + p.header.nonce[1:])),
    lambda p: replace(p, header=replace(p.header, filename="changed.txt")),
    lambda p: replace(p, header=replace(p.header, recipients=p.header.recipients[:1])),
    lambda p: replace(p, header=replace(p.header, recipients=(
        replace(p.header.recipients[0], wrapped_key=bytes([p.header.recipients[0].wrapped_key[0] ^ 1])
                + p.header.recipients[0].wrapped_key[1:]), *p.header.recipients[1:]
    ))),
    lambda p: replace(p, header=replace(p.header, recipients=(
        p.header.recipients[0], replace(p.header.recipients[1], recipient_id="Other"),
        p.header.recipients[2]
    ))),
])
def test_tampering_rejected_without_partial_plaintext(recipients, package3, change) -> None:
    _, original = package3
    tampered = change(original)
    encoded = serialize_package(tampered)  # Still structurally valid.
    with pytest.raises(DecryptionFailed):
        decrypt_file_for_recipient(deserialize_package(encoded), "Alice", recipients[0].private_key)


@pytest.mark.parametrize("change", [
    lambda d: d["header"].__setitem__("format_version", 2),
    lambda d: d["header"].__setitem__("format_version", True),
    lambda d: d["header"].__setitem__("content_algorithm", "AES-128-GCM"),
    lambda d: d["header"].__setitem__("key_wrap_algorithm", "RSA-TEXTBOOK"),
    lambda d: d["header"].__setitem__("nonce", "AAAA"),
    lambda d: d["header"]["recipients"].append(d["header"]["recipients"][0]),
    lambda d: d["header"]["recipients"][0].__setitem__("wrapped_key", "not-base64!"),
    lambda d: d["header"].__setitem__("original_size", MAX_FILE_BYTES + 1),
    lambda d: d["header"].__setitem__("filename", "../escape.txt"),
    lambda d: d.__setitem__("unexpected", "field"),
])
def test_malformed_or_unsupported_header_rejected(package3, change) -> None:
    _, package = package3
    with pytest.raises(PackageValidationError):
        deserialize_package(_mutate_json(package, change))


def test_malformed_json_base64_duplicate_keys_and_size_rejected(package3) -> None:
    _, package = package3
    for data in (b"", b"not JSON", b"\xff", b"[1,2]", b"{" + b"X" * MAX_PACKAGE_BYTES):
        with pytest.raises(PackageValidationError):
            deserialize_package(data)
    with pytest.raises(PackageValidationError):
        deserialize_package(_mutate_json(package, lambda d: d.__setitem__("ciphertext", "not-base64!")))
    document = serialize_package(package).decode("utf-8")
    duplicate = document.replace('"ciphertext":', '"ciphertext":"AA==","ciphertext":', 1)
    with pytest.raises(PackageValidationError):
        deserialize_package(duplicate.encode("utf-8"))
    duplicate_nested = document.replace('"filename":', '"filename":"x","filename":', 1)
    with pytest.raises(PackageValidationError):
        deserialize_package(duplicate_nested.encode("utf-8"))


def test_structural_validation_is_distinct_from_authentication(recipients, package3) -> None:
    _, package = package3
    invalid = replace(package, header=replace(package.header, nonce=b"short"))
    with pytest.raises(PackageValidationError):
        decrypt_file_for_recipient(invalid, "Alice", recipients[0].private_key)
    tampered = replace(package, header=replace(package.header, filename="other.txt"))
    with pytest.raises(DecryptionFailed):
        decrypt_file_for_recipient(tampered, "Alice", recipients[0].private_key)


def test_ui_attempt_states_do_not_expose_partial_plaintext(recipients, package3) -> None:
    data, package = package3
    success = attempt_decrypt_file_for_recipient(package, "Alice", recipients[0].private_key)
    assert (success.status, success.data) == ("decrypted", data)
    invalid = replace(package, header=replace(package.header, nonce=b"bad"))
    assert attempt_decrypt_file_for_recipient(invalid, "Alice", recipients[0].private_key) == (
        type(success)("invalid_package", None)
    )
    tampered = replace(package, header=replace(package.header, filename="changed.txt"))
    assert attempt_decrypt_file_for_recipient(tampered, "Alice", recipients[0].private_key) == (
        type(success)("decryption_failed", None)
    )


def test_noncanonical_json_whitespace_does_not_change_canonical_aad(recipients, package3) -> None:
    data, package = package3
    pretty = json.dumps(json.loads(serialize_package(package)), ensure_ascii=False, indent=2).encode("utf-8")
    imported = deserialize_package(pretty)
    assert decrypt_file_for_recipient(imported, "Alice", recipients[0].private_key) == data
