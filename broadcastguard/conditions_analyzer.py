"""Evaluate all recipient subsets in a controlled Textbook RSA experiment.

Only the evaluator sees M. Eve still receives public observations through
attack_observations(); this module must never be used to protect real data.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations

from broadcastguard.attack_lab import (
    AttackScenario,
    EvaluationStatus,
    PUBLIC_EXPONENT,
    PublicObservation,
    RECIPIENT_IDS,
    attack_observations,
    evaluate_experiment,
)
from broadcastguard.math_core import message_to_integer

REFERENCE_LENGTHS = (1, 96, 180)


@dataclass(frozen=True)
class SubsetAnalysis:
    recipient_ids: tuple[str, ...]
    count: int
    modulus_product: int
    product_bits: int
    crt_value: int
    candidate: int
    exact_root: bool
    recovered: bool
    bound_holds: bool
    status: EvaluationStatus
    explanation: str

    @property
    def matches_prediction(self) -> bool:
        """Compare M³ < N with actual recovery, only in the evaluator."""
        return self.bound_holds == self.recovered

    def to_row(self) -> dict[str, object]:
        """Plain values for a future table; full integers remain available."""
        return {
            "recipient_ids": self.recipient_ids,
            "subset": " + ".join(self.recipient_ids),
            "count": self.count,
            "modulus_product": self.modulus_product,
            "product_bits": self.product_bits,
            "crt_value": self.crt_value,
            "candidate": self.candidate,
            "exact_root": self.exact_root,
            "recovered": self.recovered,
            "bound_holds": self.bound_holds,
            "matches_prediction": self.matches_prediction,
            "status": self.status,
            "explanation": self.explanation,
        }


@dataclass(frozen=True)
class ScenarioAnalysis:
    message_length: int
    message_bits: int
    subsets: tuple[SubsetAnalysis, ...]

    @property
    def successful_subsets(self) -> tuple[tuple[str, ...], ...]:
        return tuple(row.recipient_ids for row in self.subsets if row.recovered)

    @property
    def minimum_successful_count(self) -> int | None:
        return min((row.count for row in self.subsets if row.recovered), default=None)

    def table_rows(self) -> list[dict[str, object]]:
        return [row.to_row() for row in self.subsets]


@dataclass(frozen=True)
class LengthSweep:
    """One key set reused for all messages; no private keys retained."""

    analyses: tuple[ScenarioAnalysis, ...]

    def matrix_rows(self) -> list[dict[str, object]]:
        """One row per message length; each recipient subset maps to a status."""
        return [
            {
                "message_length": analysis.message_length,
                "message_bits": analysis.message_bits,
                **{" + ".join(row.recipient_ids): row.status for row in analysis.subsets},
            }
            for analysis in self.analyses
        ]

    def minimum_rows(self) -> list[dict[str, int | None]]:
        return [
            {
                "message_length": analysis.message_length,
                "minimum_successful_count": analysis.minimum_successful_count,
            }
            for analysis in self.analyses
        ]

    def comparison_rows(self) -> list[dict[str, object]]:
        """Long-form mathematical prediction versus observed recovery."""
        return [
            {"message_length": analysis.message_length, **row.to_row()}
            for analysis in self.analyses
            for row in analysis.subsets
        ]


def _validated_observations(scenario: AttackScenario) -> tuple[PublicObservation, ...]:
    if not isinstance(scenario, AttackScenario):
        raise TypeError("scenario must be an AttackScenario.")
    message = message_to_integer(scenario.plaintext)
    observations = scenario.observations
    if not isinstance(observations, Sequence) or isinstance(
        observations, (str, bytes, bytearray)
    ) or len(observations) != len(RECIPIENT_IDS):
        raise ValueError("A scenario needs exactly three public observations.")
    public = tuple(observations)
    checked = attack_observations(public)
    if checked.product is None:
        raise ValueError(f"Invalid public observations: {checked.reason}")
    if {item.recipient_id for item in public} != set(RECIPIENT_IDS):
        raise ValueError("A scenario needs Alice, Bob, and Charlie once each.")
    for item in public:
        if message >= item.n:
            raise ValueError("The message integer must be smaller than every modulus.")
        if item.c != pow(message, PUBLIC_EXPONENT, item.n):
            raise ValueError("Ciphertext is inconsistent with the scenario plaintext.")
    by_id = {item.recipient_id: item for item in public}
    return tuple(by_id[name] for name in RECIPIENT_IDS)


def analyze_scenario(scenario: AttackScenario) -> ScenarioAnalysis:
    """Run Eve and the separate evaluator for all seven nonempty subsets."""
    public = _validated_observations(scenario)
    rows = []
    for count in range(1, len(public) + 1):
        for selected in combinations(public, count):
            attack = attack_observations(selected)
            evaluation = evaluate_experiment(scenario, selected, attack)
            if attack.product is None or attack.combined is None or attack.candidate is None:
                raise ValueError(f"Public observations could not be analyzed: {attack.reason}")
            if evaluation.bound_holds is None:
                raise ValueError("The experiment cannot evaluate the mathematical bound.")
            if evaluation.matches_original:
                explanation = (
                    "Experimenter: M³ < N, so CRT reconstructs M³ and Eve recovers M."
                )
            elif attack.exact:
                explanation = (
                    "Experimenter: an exact cube root exists, but it is not the original M."
                )
            else:
                explanation = (
                    "Experimenter: M³ >= N; CRT returns a residue without an exact "
                    "cube root in this trial. This does not prove security."
                )
            rows.append(
                SubsetAnalysis(
                    recipient_ids=attack.recipient_ids,
                    count=count,
                    modulus_product=attack.product,
                    product_bits=attack.product.bit_length(),
                    crt_value=attack.combined,
                    candidate=attack.candidate,
                    exact_root=attack.exact,
                    recovered=evaluation.matches_original,
                    bound_holds=evaluation.bound_holds,
                    status=evaluation.status,
                    explanation=explanation,
                )
            )
    message = message_to_integer(scenario.plaintext)
    return ScenarioAnalysis(len(scenario.plaintext), message.bit_length(), tuple(rows))


def sweep_message_lengths(
    base_scenario: AttackScenario,
    lengths: Sequence[int] = REFERENCE_LENGTHS,
) -> LengthSweep:
    """Encrypt b'B' * length with the same three public moduli for each row."""
    public = _validated_observations(base_scenario)
    if not isinstance(lengths, Sequence) or isinstance(lengths, (str, bytes, bytearray)):
        raise TypeError("lengths must be a sequence of positive integers.")
    if not lengths or any(not isinstance(n, int) or isinstance(n, bool) or n < 1 for n in lengths):
        raise ValueError("lengths must contain positive integers.")
    if len(set(lengths)) != len(lengths):
        raise ValueError("lengths must be unique for a clear comparison matrix.")
    analyses = []
    for length in lengths:
        # b'B' has seven significant bits; reject impossible sizes before
        # allocating an arbitrarily large test message.
        if 8 * length - 1 > min(item.n.bit_length() for item in public):
            raise ValueError(f"Message of {length} bytes is not below every modulus.")
        plaintext = b"B" * length
        message = message_to_integer(plaintext)
        if any(message >= item.n for item in public):
            raise ValueError(f"Message of {length} bytes is not below every modulus.")
        observations = tuple(
            PublicObservation(item.recipient_id, item.n, item.e, pow(message, item.e, item.n))
            for item in public
        )
        analyses.append(analyze_scenario(AttackScenario(plaintext, observations)))
    return LengthSweep(tuple(analyses))
