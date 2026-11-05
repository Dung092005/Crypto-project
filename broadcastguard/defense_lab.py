"""Controlled Textbook RSA versus RSA-OAEP educational experiment.

Textbook RSA is deliberately insecure and belongs only to this comparison.
Private keys stay in the orchestration call; returned data contains public
parameters, ciphertexts, and experiment results only.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from math import gcd, prod
from typing import Literal

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from broadcastguard.attack_lab import (
    KEY_SIZE,
    PUBLIC_EXPONENT,
    RECIPIENT_IDS,
    AttackOutcome,
    PublicObservation,
    attack_observations,
)
from broadcastguard.math_core import integer_to_message, message_to_integer

Scheme = Literal["textbook", "oaep"]
DefenseStatus = Literal["recovered", "wrong_exact_root", "no_exact_root", "invalid_input"]
OAEP_HASH_BYTES = hashes.SHA256().digest_size
OAEP_MAX_MESSAGE_BYTES = KEY_SIZE // 8 - 2 * OAEP_HASH_BYTES - 2


def _oaep_padding() -> padding.OAEP:
    """RSAES-OAEP with SHA-256, MGF1(SHA-256), and the empty label."""
    return padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None,
    )


@dataclass(frozen=True)
class SchemeObservation:
    """Attacker-visible observation with an explicit encryption scheme tag."""

    scheme: Scheme
    public: PublicObservation

    @property
    def recipient_id(self) -> str:
        return self.public.recipient_id

    def row(self) -> dict[str, str | int]:
        return {
            "scheme": self.scheme,
            "recipient_id": self.recipient_id,
            "public_exponent": self.public.e,
            "modulus_bits": self.public.modulus_bits,
            "modulus_preview": _preview_integer(self.public.n),
            "ciphertext_preview": self.public.ciphertext_preview,
        }


@dataclass(frozen=True)
class DefenseScenario:
    """Controlled experiment setup; do not pass this to the attacker."""

    plaintext: bytes
    textbook_observations: tuple[SchemeObservation, ...]
    oaep_observations: tuple[SchemeObservation, ...]


@dataclass(frozen=True)
class DefenseAttackResult:
    """Eve's public outcome plus a separate ground-truth evaluation."""

    scheme: Scheme
    outcome: AttackOutcome
    candidate_bytes: bytes | None
    recovered_original: bool
    status: DefenseStatus
    textbook_bound_holds: bool | None
    explanation: str

    def summary_row(self, plaintext_length: int, legitimate_decryption: bool | None) -> dict:
        return {
            "scheme": self.scheme,
            "recipient_count": self.outcome.used_count,
            "public_exponent": PUBLIC_EXPONENT,
            "plaintext_length": plaintext_length,
            "attack_candidate": self.outcome.candidate,
            "attack_candidate_preview": _preview_integer(self.outcome.candidate)
            if self.outcome.candidate is not None else None,
            "exact_root": self.outcome.exact,
            "recovered_original": self.recovered_original,
            "legitimate_decryption": legitimate_decryption,
            "status": self.status,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class RecipientDecryption:
    recipient_id: str
    recovered_original_bytes: bool


@dataclass(frozen=True)
class RandomizationResult:
    """Observed property of repeated encryption, not a security proof."""

    recipient_id: str
    trial_count: int
    textbook_ciphertexts_identical: bool
    oaep_ciphertexts_distinct: bool
    oaep_all_decrypt: bool


@dataclass(frozen=True)
class DefenseComparison:
    scenario: DefenseScenario
    textbook: DefenseAttackResult
    oaep: DefenseAttackResult
    decryptions: tuple[RecipientDecryption, ...]
    randomization: RandomizationResult

    def summary_rows(self) -> list[dict]:
        length = len(self.scenario.plaintext)
        return [
            self.textbook.summary_row(length, None),
            self.oaep.summary_row(length, all(item.recovered_original_bytes for item in self.decryptions)),
        ]

    def recipient_rows(self) -> list[dict]:
        status_by_id = {item.recipient_id: item.recovered_original_bytes for item in self.decryptions}
        rows = []
        for observation in (*self.scenario.textbook_observations, *self.scenario.oaep_observations):
            row = observation.row()
            row["legitimate_decryption"] = (
                status_by_id[observation.recipient_id] if observation.scheme == "oaep" else None
            )
            rows.append(row)
        return rows

    def detail_rows(self) -> list[dict]:
        return [
            {
                "scheme": result.scheme,
                "crt_combined": result.outcome.combined,
                "modulus_product_bits": result.outcome.product.bit_length()
                if result.outcome.product is not None else None,
                "textbook_bound_holds": result.textbook_bound_holds,
                "encoding": "raw integer" if result.scheme == "textbook" else "randomized OAEP-SHA256",
            }
            for result in (self.textbook, self.oaep)
        ]


def _preview_integer(value: int) -> str:
    digits = f"{value:x}"
    return f"0x{digits[:12]}…{digits[-12:]}" if len(digits) > 28 else f"0x{digits}"


def _validate_keys(keys: Sequence[rsa.RSAPrivateKey]) -> tuple[rsa.RSAPrivateKey, ...]:
    if not isinstance(keys, Sequence) or isinstance(keys, (bytes, bytearray, str)):
        raise TypeError("private_keys must be a sequence of three RSA private keys.")
    selected = tuple(keys)
    if len(selected) != len(RECIPIENT_IDS) or any(
        not isinstance(key, rsa.RSAPrivateKey) for key in selected
    ):
        raise ValueError("Exactly three RSA private keys are required.")
    numbers = [key.public_key().public_numbers() for key in selected]
    if any(public.e != PUBLIC_EXPONENT or public.n.bit_length() != KEY_SIZE for public in numbers):
        raise ValueError("Each RSA key must be 2048-bit with public exponent e=3.")
    moduli = [public.n for public in numbers]
    if any(gcd(n, other) != 1 for index, n in enumerate(moduli) for other in moduli[index + 1:]):
        raise ValueError("RSA moduli must be pairwise coprime.")
    return selected


def _evaluate_attack(
    plaintext: bytes,
    observations: tuple[SchemeObservation, ...],
    outcome: AttackOutcome,
) -> DefenseAttackResult:
    """Experimenter-only check. The Textbook M³ bound is not applied to OAEP."""
    scheme = observations[0].scheme
    if any(item.scheme != scheme for item in observations):
        raise ValueError("All observations in one attack must use the same scheme.")
    if outcome.recipient_ids != tuple(item.recipient_id for item in observations):
        raise ValueError("Attack outcome does not match selected recipients.")
    if outcome.used_count != len(observations):
        raise ValueError("Attack outcome count does not match observations.")
    if outcome.product is not None and outcome.product != prod(item.public.n for item in observations):
        raise ValueError("Attack outcome does not match selected moduli.")
    original = message_to_integer(plaintext)
    recovered = outcome.exact and outcome.candidate == original
    candidate_bytes = None
    if outcome.exact and outcome.candidate is not None:
        try:
            candidate_bytes = integer_to_message(outcome.candidate, len(plaintext))
        except ValueError:
            pass
    bound = original**PUBLIC_EXPONENT < outcome.product if scheme == "textbook" and outcome.product else None
    if outcome.product is None:
        status: DefenseStatus = "invalid_input"
    elif recovered:
        status = "recovered"
    elif outcome.exact:
        status = "wrong_exact_root"
    else:
        status = "no_exact_root"
    if scheme == "textbook":
        explanation = (
            "Experimenter: M³ < N, so CRT reconstructs M³ and its cube root is M."
            if recovered else
            "Experimenter: this CRT-and-root result did not recover M; an exact root alone is insufficient."
        )
    else:
        explanation = (
            "Experimenter: OAEP encodes the same bytes with independent randomness before RSA; "
            "this CRT-and-root attempt did not recover the original bytes."
            if not recovered else
            "Experimenter: this run recovered the original integer; investigate this exceptional outcome."
        )
    return DefenseAttackResult(scheme, outcome, candidate_bytes, recovered, status, bound, explanation)


def run_defense_comparison(
    plaintext: bytes,
    *,
    private_keys: Sequence[rsa.RSAPrivateKey] | None = None,
    randomization_trials: int = 3,
) -> DefenseComparison:
    """Compare two schemes on the same plaintext, RSA keys, recipients, and Eve method.

    ``private_keys`` permits controlled tests with a shared in-memory key set.
    It is never copied into a returned dataclass or passed to Eve.
    """
    message = message_to_integer(plaintext)
    if len(plaintext) > OAEP_MAX_MESSAGE_BYTES:
        raise ValueError(f"RSA-2048 OAEP-SHA256 accepts at most {OAEP_MAX_MESSAGE_BYTES} bytes.")
    if not isinstance(randomization_trials, int) or isinstance(randomization_trials, bool):
        raise TypeError("randomization_trials must be an integer.")
    if randomization_trials < 2:
        raise ValueError("randomization_trials must be at least 2.")
    keys = _validate_keys(private_keys if private_keys is not None else tuple(
        rsa.generate_private_key(public_exponent=PUBLIC_EXPONENT, key_size=KEY_SIZE)
        for _ in RECIPIENT_IDS
    ))
    public_numbers = tuple(key.public_key().public_numbers() for key in keys)
    if any(message >= public.n for public in public_numbers):
        raise ValueError("The message integer must be smaller than every RSA modulus.")

    # Deliberately insecure Textbook RSA, only for this educational baseline.
    textbook_observations = tuple(
        SchemeObservation("textbook", PublicObservation(name, public.n, public.e,
                          pow(message, public.e, public.n)))
        for name, public in zip(RECIPIENT_IDS, public_numbers)
    )
    oaep_ciphertexts = tuple(key.public_key().encrypt(plaintext, _oaep_padding()) for key in keys)
    oaep_observations = tuple(
        SchemeObservation("oaep", PublicObservation(name, public.n, public.e,
                          int.from_bytes(ciphertext, "big")))
        for name, public, ciphertext in zip(RECIPIENT_IDS, public_numbers, oaep_ciphertexts)
    )
    scenario = DefenseScenario(plaintext, textbook_observations, oaep_observations)

    # Eve receives only public observations. The two calls use identical CRT/root code.
    textbook_outcome = attack_observations(tuple(item.public for item in textbook_observations))
    oaep_outcome = attack_observations(tuple(item.public for item in oaep_observations))
    textbook_result = _evaluate_attack(plaintext, textbook_observations, textbook_outcome)
    oaep_result = _evaluate_attack(plaintext, oaep_observations, oaep_outcome)

    decryptions = tuple(
        RecipientDecryption(name, key.decrypt(ciphertext, _oaep_padding()) == plaintext)
        for name, key, ciphertext in zip(RECIPIENT_IDS, keys, oaep_ciphertexts)
    )
    first_key = keys[0]
    repeated_oaep = tuple(
        first_key.public_key().encrypt(plaintext, _oaep_padding())
        for _ in range(randomization_trials)
    )
    textbook_a = pow(message, PUBLIC_EXPONENT, public_numbers[0].n)
    textbook_b = pow(message, PUBLIC_EXPONENT, public_numbers[0].n)
    randomization = RandomizationResult(
        RECIPIENT_IDS[0], randomization_trials, textbook_a == textbook_b,
        len(set(repeated_oaep)) == randomization_trials,
        all(first_key.decrypt(ciphertext, _oaep_padding()) == plaintext for ciphertext in repeated_oaep),
    )
    return DefenseComparison(scenario, textbook_result, oaep_result, decryptions, randomization)
