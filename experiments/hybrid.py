"""E3 measured hybrid operations and E4 controlled rejection cases."""

from dataclasses import replace
from random import Random
from time import perf_counter_ns

from broadcastguard.hybrid_sharing import (
    FORMAT_VERSION,
    attempt_decrypt_file_for_recipient,
    decrypt_file_for_recipient,
    encrypt_file_for_recipients,
    generate_demo_recipients,
    serialize_package,
)
from experiments.methodology import E4_CASES, FILE_SIZES, RECIPIENT_COUNTS, RunConfig, keyset_id


E3_FIELDS = (
    "run_id", "experiment_id", "case_id", "repetition", "prepared_keyset_id",
    "recipient_count", "file_size_bytes", "package_size_bytes", "overhead_bytes",
    "overhead_percent", "encryption_ns", "serialization_ns", "total_encryption_ns",
    "decryption_ns", "decrypted_correctly", "package_version", "validation_pass",
    "error_type",
)
KEYGEN_FIELDS = (
    "run_id", "experiment_id", "case_id", "repetition", "recipient_count",
    "duration_ns", "valid_keys", "validation_pass", "error_type",
)
E4_FIELDS = (
    "run_id", "experiment_id", "case_id", "repetition", "expected_status",
    "observed_status", "rejected", "plaintext_returned", "validation_pass", "error_type",
)


def synthetic_payload(size: int) -> bytes:
    """Identical, non-sensitive binary workload for every run of a file size."""
    if type(size) is not int or size < 0:
        raise ValueError("size must be nonnegative.")
    pattern = bytes(range(256))
    return pattern * (size // 256) + pattern[:size % 256]


def _keygen_rows(config: RunConfig, run_id: str) -> list[dict]:
    for count in RECIPIENT_COUNTS:
        for _ in range(config.warmup):
            generate_demo_recipients(count)
    schedule = [(count, repetition) for count in RECIPIENT_COUNTS
                for repetition in range(config.repetitions)]
    Random(config.schedule_seed + 1).shuffle(schedule)  # Timing order only, never CSPRNG.
    rows = []
    for count, repetition in schedule:
        row = {"run_id": run_id, "experiment_id": "E3-keygen", "case_id": str(count),
               "repetition": repetition, "recipient_count": count}
        try:
            start = perf_counter_ns()
            recipients = generate_demo_recipients(count)
            duration = perf_counter_ns() - start
            valid = (len(recipients) == count and
                     len({item.public.fingerprint for item in recipients}) == count and
                     all(item.private_key.key_size == 2048 and
                         item.public.public_key.public_numbers().e == 65537
                         for item in recipients))
            row.update(duration_ns=duration, valid_keys=valid,
                       validation_pass=valid and duration > 0, error_type="")
        except Exception as error:
            row.update(validation_pass=False, error_type=type(error).__name__)
        rows.append(row)
    return rows


def run_hybrid_performance(config: RunConfig, run_id: str) -> tuple[list[dict], list[dict]]:
    """Key generation is separate; regular encryption reuses prepared keys."""
    keygen_rows = _keygen_rows(config, run_id)
    prepared = generate_demo_recipients(5)
    prepared_id = keyset_id(tuple(item.private_key for item in prepared))
    payloads = {size: synthetic_payload(size) for size in FILE_SIZES}
    for count in RECIPIENT_COUNTS:
        public = tuple(item.public for item in prepared[:count])
        for size in FILE_SIZES:
            for _ in range(config.warmup):
                package = encrypt_file_for_recipients(payloads[size], "synthetic.bin", public)
                encoded = serialize_package(package)
                assert decrypt_file_for_recipient(package, prepared[0].recipient_id,
                                                  prepared[0].private_key) == payloads[size]
                assert encoded

    schedule = [(count, size, repetition) for count in RECIPIENT_COUNTS
                for size in FILE_SIZES for repetition in range(config.repetitions)]
    Random(config.schedule_seed).shuffle(schedule)  # Reproducible order, not crypto randomness.
    rows: list[dict] = []
    for count, size, repetition in schedule:
        row = {
            "run_id": run_id, "experiment_id": "E3", "case_id": f"{count}r_{size}b",
            "repetition": repetition, "prepared_keyset_id": prepared_id,
            "recipient_count": count, "file_size_bytes": size,
        }
        try:
            public = tuple(item.public for item in prepared[:count])
            start = perf_counter_ns()
            package = encrypt_file_for_recipients(payloads[size], "synthetic.bin", public)
            encrypted_at = perf_counter_ns()
            encoded = serialize_package(package)
            serialized_at = perf_counter_ns()
            decrypted = decrypt_file_for_recipient(package, prepared[0].recipient_id,
                                                   prepared[0].private_key)
            decrypted_at = perf_counter_ns()
            overhead = len(encoded) - size
            durations = (encrypted_at - start, serialized_at - encrypted_at,
                         serialized_at - start, decrypted_at - serialized_at)
            valid = (decrypted == payloads[size] and all(value > 0 for value in durations)
                     and overhead >= 0 and package.header.format_version == FORMAT_VERSION)
            row.update(
                package_size_bytes=len(encoded), overhead_bytes=overhead,
                overhead_percent=100 * overhead / size,
                encryption_ns=durations[0], serialization_ns=durations[1],
                total_encryption_ns=durations[2], decryption_ns=durations[3],
                decrypted_correctly=decrypted == payloads[size],
                package_version=package.header.format_version,
                validation_pass=valid, error_type="",
            )
        except Exception as error:
            row.update(validation_pass=False, error_type=type(error).__name__)
        rows.append(row)
    return rows, keygen_rows


def _flip(raw: bytes, index: int) -> bytes:
    changed = bytearray(raw)
    changed[index] ^= 1
    return bytes(changed)


def run_security_validation(run_id: str) -> list[dict]:
    """Correctness cases; no timing claims and no plaintext bytes in rows."""
    recipients = generate_demo_recipients(3)
    payload = synthetic_payload(1024)
    package = encrypt_file_for_recipients(payload, "synthetic.bin",
                                          tuple(item.public for item in recipients))
    first = package.header.recipients[0]
    changed_first = replace(first, wrapped_key=_flip(first.wrapped_key, 0))
    cases = {
        "valid_recipient": (package, "Alice", recipients[0].private_key, "decrypted"),
        "wrong_private_key": (package, "Alice", recipients[1].private_key, "decryption_failed"),
        "wrong_recipient_id": (package, "Nobody", recipients[0].private_key, "decryption_failed"),
        "changed_ciphertext": (replace(package, encrypted_content=_flip(package.encrypted_content, 0)),
                               "Alice", recipients[0].private_key, "decryption_failed"),
        "changed_tag": (replace(package, encrypted_content=_flip(package.encrypted_content, -1)),
                        "Alice", recipients[0].private_key, "decryption_failed"),
        "changed_filename": (replace(package, header=replace(package.header, filename="renamed.bin")),
                             "Alice", recipients[0].private_key, "decryption_failed"),
        "changed_nonce": (replace(package, header=replace(package.header,
                                                           nonce=_flip(package.header.nonce, 0))),
                          "Alice", recipients[0].private_key, "decryption_failed"),
        "changed_wrapped_key": (replace(package, header=replace(package.header,
                                                                recipients=(changed_first, *package.header.recipients[1:]))),
                                "Alice", recipients[0].private_key, "decryption_failed"),
        "changed_recipient_list": (replace(package, header=replace(package.header,
                                                                  recipients=package.header.recipients[:2])),
                                   "Alice", recipients[0].private_key, "decryption_failed"),
        "unsupported_version": (replace(package, header=replace(package.header,
                                                                format_version=FORMAT_VERSION + 1)),
                                "Alice", recipients[0].private_key, "invalid_package"),
        "invalid_json": (b'{"header":', "Alice", recipients[0].private_key, "invalid_package"),
    }
    assert set(cases) == set(E4_CASES)
    rows = []
    for case_id in E4_CASES:
        candidate, recipient_id, private_key, expected = cases[case_id]
        row = {"run_id": run_id, "experiment_id": "E4", "case_id": case_id,
               "repetition": 0, "expected_status": expected}
        try:
            attempt = attempt_decrypt_file_for_recipient(candidate, recipient_id, private_key)
            returned = attempt.data is not None
            valid = (attempt.status == expected and
                     (attempt.data == payload if expected == "decrypted" else not returned))
            row.update(observed_status=attempt.status, rejected=attempt.status != "decrypted",
                       plaintext_returned=returned, validation_pass=valid, error_type="")
        except Exception as error:
            row.update(observed_status="error", rejected=False, plaintext_returned=False,
                       validation_pass=False, error_type=type(error).__name__)
        rows.append(row)
    return rows
