"""Educational Textbook RSA broadcast scenario, attacker, and evaluator.

Textbook RSA here is deliberately insecure. Never use this module to protect
real messages or files. Private keys are generated only inside the builder and
are never passed to the attacker or stored in its output.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from math import gcd
from typing import Literal

from cryptography.hazmat.primitives.asymmetric import rsa

from broadcastguard.math_core import (
    broadcast_attack,
    integer_to_message,
    message_to_integer,
)

RECIPIENT_IDS = ("Alice", "Bob", "Charlie")
PUBLIC_EXPONENT = 3
KEY_SIZE = 2048
EvaluationStatus = Literal[
    "recovered", "wrong_exact_root", "no_exact_root", "invalid_input"
]


@dataclass(frozen=True)
class PublicObservation:
    """Everything Eve can observe for one recipient; no secret key material."""

    recipient_id: str
    n: int
    e: int
    c: int

    @property
    def modulus_bits(self) -> int:
        return self.n.bit_length()

    @property
    def ciphertext_preview(self) -> str:
        """Short display value; the full ciphertext remains available as c."""
        digits = f"{self.c:x}"
        return f"0x{digits}" if len(digits) <= 28 else f"0x{digits[:12]}…{digits[-12:]}"


@dataclass(frozen=True)
class AttackScenario:
    """Experiment setup; keep plaintext out of attacker-facing calls."""

    plaintext: bytes
    observations: tuple[PublicObservation, ...]


@dataclass(frozen=True)
class AttackOutcome:
    """Public-only result; exact never means the plaintext is confirmed."""

    recipient_ids: tuple[str, ...]
    used_count: int
    product: int | None
    combined: int | None
    candidate: int | None
    exact: bool
    reason: str | None
    steps: tuple[str, ...]


@dataclass(frozen=True)
class ExperimentEvaluation:
    """Ground-truth comparison, strictly outside the attacker engine."""

    original_message: bytes
    candidate: int | None
    candidate_bytes: bytes | None
    matches_original: bool
    bound_holds: bool | None
    used_count: int
    status: EvaluationStatus


def _validate_public(observations: Sequence[PublicObservation]) -> None:
    if not isinstance(observations, Sequence) or isinstance(
        observations, (str, bytes, bytearray)
    ):
        raise TypeError("observations must be a sequence of PublicObservation.")
    if not 1 <= len(observations) <= len(RECIPIENT_IDS):
        raise ValueError("Eve must have one, two, or three observations.")
    ids: set[str] = set()
    moduli: list[int] = []
    for observation in observations:
        if not isinstance(observation, PublicObservation):
            raise TypeError("Each item must be a PublicObservation.")
        if observation.recipient_id not in RECIPIENT_IDS:
            raise ValueError("Unknown recipient ID.")
        if observation.recipient_id in ids:
            raise ValueError("Recipient IDs must be unique.")
        ids.add(observation.recipient_id)
        if (
            not isinstance(observation.e, int)
            or isinstance(observation.e, bool)
            or observation.e != PUBLIC_EXPONENT
        ):
            raise ValueError("All observations must use public exponent e=3.")
        if (
            not isinstance(observation.n, int)
            or isinstance(observation.n, bool)
            or observation.n <= 1
        ):
            raise ValueError("Each public modulus must be an integer > 1.")
        if not isinstance(observation.c, int) or isinstance(observation.c, bool):
            raise ValueError("Each ciphertext must be an integer.")
        if not 0 <= observation.c < observation.n:
            raise ValueError("Each ciphertext must be in [0, modulus).")
        if any(gcd(observation.n, previous) != 1 for previous in moduli):
            raise ValueError("Public moduli must be pairwise coprime.")
        moduli.append(observation.n)


def _recipient_ids(observations: Sequence[object]) -> tuple[str, ...]:
    return tuple(
        item.recipient_id
        if isinstance(item, PublicObservation) and isinstance(item.recipient_id, str)
        else "?"
        for item in observations
    )


def build_scenario(plaintext: bytes) -> AttackScenario:
    """Generate three real RSA-2048 key pairs and encrypt the same bytes.

    Only public numbers survive this function. Validate the integer message
    against every modulus before doing any modular exponentiation; never
    silently truncate, pad, or reduce an oversized message.
    """
    message = message_to_integer(plaintext)
    keys = [
        rsa.generate_private_key(public_exponent=PUBLIC_EXPONENT, key_size=KEY_SIZE)
        for _ in RECIPIENT_IDS
    ]
    public_numbers = [key.public_key().public_numbers() for key in keys]
    moduli = [public.n for public in public_numbers]
    if any(
        public.e != PUBLIC_EXPONENT or public.n.bit_length() != KEY_SIZE
        for public in public_numbers
    ):
        raise ValueError("Generated RSA keys do not match e=3 and 2048 bits.")
    if any(message >= n for n in moduli):
        raise ValueError("The message integer must be smaller than every RSA modulus.")
    if any(
        gcd(n, other) != 1
        for index, n in enumerate(moduli)
        for other in moduli[index + 1 :]
    ):
        raise ValueError("Generated RSA moduli must be pairwise coprime.")
    # This pow is intentionally insecure Textbook RSA, for the attack lab only.
    observations = tuple(
        PublicObservation(recipient_id, n, PUBLIC_EXPONENT, pow(message, PUBLIC_EXPONENT, n))
        for recipient_id, n in zip(RECIPIENT_IDS, moduli)
    )
    return AttackScenario(plaintext, observations)


def attack_observations(observations: Sequence[PublicObservation]) -> AttackOutcome:
    """Eve uses public observations only; no plaintext or private key input."""
    if not isinstance(observations, Sequence) or isinstance(
        observations, (str, bytes, bytearray)
    ):
        return AttackOutcome((), 0, None, None, None, False,
                             "observations must be a sequence of PublicObservation.", ())
    selected = tuple(observations)
    recipient_ids = _recipient_ids(selected)
    try:
        _validate_public(selected)
    except (TypeError, ValueError) as error:
        return AttackOutcome(recipient_ids, len(selected), None, None, None, False,
                             str(error), ("Public observations failed validation.",))

    result = broadcast_attack(
        [item.c for item in selected], [item.n for item in selected], PUBLIC_EXPONENT
    )
    steps = (
        f"Collected {len(selected)} public ciphertext(s), all with e=3.",
        f"CRT combines pairwise-coprime moduli into N ({result.product.bit_length()} bits).",
        f"Integer cube root of X is {result.root.bit_length()} bits; exact={result.exact}.",
    )
    reason = None if result.exact else "CRT result X is not a perfect cube."
    return AttackOutcome(recipient_ids, len(selected), result.product,
                         result.combined, result.root, result.exact, reason, steps)


def evaluate_experiment(
    scenario: AttackScenario,
    observed: Sequence[PublicObservation],
    outcome: AttackOutcome,
) -> ExperimentEvaluation:
    """Compare Eve's candidate with ground truth in a separate component.

    The selected public observations must belong to the supplied scenario and
    match the outcome, so a result cannot be scored against an unrelated run.
    """
    if not isinstance(scenario, AttackScenario) or not isinstance(outcome, AttackOutcome):
        raise TypeError("scenario and outcome must use Attack Lab data types.")
    message = message_to_integer(scenario.plaintext)
    if not isinstance(observed, Sequence) or isinstance(observed, (str, bytes, bytearray)):
        raise TypeError("observed must be a sequence of PublicObservation.")
    selected = tuple(observed)
    if outcome.used_count != len(selected) or outcome.recipient_ids != _recipient_ids(selected):
        raise ValueError("Outcome does not match the selected observations.")
    if any(item not in scenario.observations for item in selected):
        raise ValueError("Selected observations are not from this scenario.")

    bound_holds = (
        message**PUBLIC_EXPONENT < outcome.product
        if outcome.product is not None
        else None
    )
    matches_original = outcome.exact and outcome.candidate == message
    candidate_bytes = None
    if outcome.exact and outcome.candidate is not None:
        try:
            candidate_bytes = integer_to_message(outcome.candidate, len(scenario.plaintext))
        except ValueError:
            pass  # The candidate integer does not fit the original byte length.
    if outcome.product is None:
        status: EvaluationStatus = "invalid_input"
    elif matches_original:
        status = "recovered"
    elif outcome.exact:
        status = "wrong_exact_root"
    else:
        status = "no_exact_root"
    return ExperimentEvaluation(
        scenario.plaintext, outcome.candidate, candidate_bytes,
        matches_original, bound_holds, outcome.used_count, status,
    )
