"""Frozen experiment settings and sanitized provenance metadata."""

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import os
import platform
import subprocess
import sys
from uuid import uuid4

import cryptography
from cryptography.hazmat.primitives.asymmetric import rsa


ATTACK_SAMPLES: tuple[tuple[str, bytes], ...] = (
    ("short_1", b"B"),
    ("medium_96", b"B" * 96),
    ("long_180", b"B" * 180),
    ("leading_zero_96", b"\x00" * 95 + b"\x02"),
)
DEFENSE_SAMPLE_IDS = ("short_1", "medium_96", "long_180")
FILE_SIZES = (10 * 1024, 100 * 1024, 1024 * 1024)
RECIPIENT_COUNTS = (1, 3, 5)
E4_CASES = (
    "valid_recipient", "wrong_private_key", "wrong_recipient_id",
    "changed_ciphertext", "changed_tag", "changed_filename", "changed_nonce",
    "changed_wrapped_key", "changed_recipient_list", "unsupported_version",
    "invalid_json",
)


@dataclass(frozen=True)
class RunConfig:
    mode: str
    repetitions: int
    warmup: int
    schedule_seed: int

    def __post_init__(self) -> None:
        if self.mode not in ("quick", "official"):
            raise ValueError("mode must be quick or official.")
        if type(self.repetitions) is not int or self.repetitions < 1:
            raise ValueError("repetitions must be a positive integer.")
        if self.mode == "official" and self.repetitions < 20:
            raise ValueError("official mode requires at least 20 repetitions.")
        if type(self.warmup) is not int or self.warmup < 1:
            raise ValueError("warmup must be a positive integer.")
        if type(self.schedule_seed) is not int:
            raise ValueError("schedule_seed must be an integer.")


def keyset_id(keys: tuple[rsa.RSAPrivateKey, ...]) -> str:
    """Hash public moduli only; do not retain or serialize private components."""
    return sha256(b"".join(key.public_key().public_numbers().n.to_bytes(256, "big")
                           for key in keys)).hexdigest()


def git_revision() -> tuple[str, bool]:
    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                         text=True, check=True, timeout=10).stdout.strip()
    dirty = bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True,
                                text=True, check=True, timeout=10).stdout.strip())
    return sha, dirty


def manifest(config: RunConfig) -> dict[str, object]:
    sha, dirty = git_revision()
    now = datetime.now(timezone.utc)
    return {
        "schema_version": 1,
        "run_id": f"{config.mode}-{now.strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}",
        "timestamp_utc": now.isoformat(),
        "git_commit": sha,
        "source_dirty": dirty,
        "mode": config.mode,
        "repetitions": config.repetitions,
        "warmup": config.warmup,
        "schedule_seed": config.schedule_seed,
        "os": platform.system() or "unavailable",
        "os_release": platform.release() or "unavailable",
        "python_version": sys.version.split()[0],
        "cryptography_version": cryptography.__version__,
        "cpu_model": platform.processor() or "unavailable",
        "logical_cpu_count": os.cpu_count() or "unavailable",
        "attack_samples": [name for name, _ in ATTACK_SAMPLES],
        "defense_samples": list(DEFENSE_SAMPLE_IDS),
        "file_sizes_bytes": list(FILE_SIZES),
        "recipient_counts": list(RECIPIENT_COUNTS),
        "timing_clock": "time.perf_counter_ns",
        "timing_unit": "nanoseconds",
        "notes": "Schedule seed controls run order only; cryptographic randomness is never seeded.",
    }
