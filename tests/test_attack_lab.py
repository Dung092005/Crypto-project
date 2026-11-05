"""Attack Lab invariants: public-only attacker and separate ground truth."""

from dataclasses import fields
import inspect
from math import prod

import pytest

from broadcastguard.attack_lab import (
    AttackScenario,
    PublicObservation,
    attack_observations,
    build_scenario,
    evaluate_experiment,
)
from broadcastguard.math_core import integer_to_message, message_to_integer

SMALL_MODULI = (55, 391, 1189)
NAMES = ("Alice", "Bob", "Charlie")


def sample_scenario(plaintext: bytes, moduli: tuple[int, ...] = SMALL_MODULI) -> AttackScenario:
    message = message_to_integer(plaintext)
    observations = tuple(
        PublicObservation(name, n, 3, pow(message, 3, n))
        for name, n in zip(NAMES, moduli)
    )
    return AttackScenario(plaintext, observations)


def test_m12_crt_and_public_display() -> None:
    scenario = sample_scenario(b"\x0c")
    assert [item.c for item in scenario.observations] == [23, 164, 539]
    outcome = attack_observations(scenario.observations)
    evaluation = evaluate_experiment(scenario, scenario.observations, outcome)
    assert outcome.used_count == 3
    assert outcome.recipient_ids == NAMES
    assert outcome.product == prod(SMALL_MODULI)
    assert outcome.combined == 1728
    assert (outcome.candidate, outcome.exact, outcome.reason) == (12, True, None)
    assert evaluation.status == "recovered"
    assert evaluation.matches_original and evaluation.bound_holds
    assert evaluation.candidate_bytes == b"\x0c"
    assert scenario.observations[0].modulus_bits == 6
    assert scenario.observations[0].ciphertext_preview == "0x17"
    assert len(outcome.steps) == 3


@pytest.mark.parametrize("message,minimum", [(2, 1), (12, 2), (30, 3)])
def test_recovery_threshold_depends_on_message_and_product(message: int, minimum: int) -> None:
    scenario = sample_scenario(bytes([message]))
    for count in (1, 2, 3):
        observed = scenario.observations[:count]
        outcome = attack_observations(observed)
        evaluation = evaluate_experiment(scenario, observed, outcome)
        assert evaluation.used_count == count
        assert evaluation.bound_holds == (message**3 < prod(SMALL_MODULI[:count]))
        assert evaluation.matches_original == (count >= minimum)
        assert evaluation.status == ("recovered" if count >= minimum else "no_exact_root")


def test_exact_root_can_be_wrong_plaintext() -> None:
    scenario = sample_scenario(b"\x02", (7,))
    observed = scenario.observations
    outcome = attack_observations(observed)
    evaluation = evaluate_experiment(scenario, observed, outcome)
    assert outcome.exact and outcome.candidate == 1
    assert evaluation.status == "wrong_exact_root"
    assert evaluation.candidate_bytes == b"\x01"
    assert not evaluation.matches_original
    assert evaluation.bound_holds is False


def test_nonprefix_intercepts_are_supported() -> None:
    scenario = sample_scenario(b"\x1e")  # M=30
    observed = (scenario.observations[1], scenario.observations[2])
    outcome = attack_observations(observed)
    evaluation = evaluate_experiment(scenario, observed, outcome)
    assert outcome.recipient_ids == ("Bob", "Charlie")
    assert outcome.product == 391 * 1189
    assert evaluation.status == "recovered"
    assert not evaluate_experiment(
        scenario, scenario.observations[:2], attack_observations(scenario.observations[:2])
    ).matches_original


def test_leading_zero_bytes_preserved() -> None:
    scenario = sample_scenario(b"\x00\x00\x0c")
    outcome = attack_observations(scenario.observations[:2])
    evaluation = evaluate_experiment(scenario, scenario.observations[:2], outcome)
    assert evaluation.status == "recovered"
    assert evaluation.candidate_bytes == scenario.plaintext
    assert integer_to_message(outcome.candidate, len(scenario.plaintext)) == scenario.plaintext


@pytest.mark.parametrize("bad", [b"", "abc", None, bytearray(b"a")])
def test_builder_rejects_empty_or_wrong_plaintext(bad: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        build_scenario(bad)


@pytest.mark.parametrize("observed,reason_fragment", [
    ((), "one, two, or three"),
    ((PublicObservation("Alice", 7, 3, 1),) * 2, "unique"),
    ((PublicObservation("Alice", 55, 3, 1), PublicObservation("Bob", 11, 3, 1)), "coprime"),
    ((PublicObservation("Mallory", 7, 3, 1),), "Unknown"),
    ((PublicObservation("Alice", 7, 5, 1),), "e=3"),
    ((PublicObservation("Alice", 7, 3, 7),), "[0, modulus)"),
    ((PublicObservation("Alice", 1, 3, 0),), "modulus"),
    ((PublicObservation("Alice", 7, 3, -1),), "[0, modulus)"),
    ((PublicObservation("Alice", 7, 3, True),), "ciphertext"),
    ((PublicObservation("Alice", 7, True, 1),), "e=3"),
    ((PublicObservation("Alice", 7.0, 3, 1),), "modulus"),
    (("not-an-observation",), "PublicObservation"),
])
def test_attacker_reports_invalid_input(observed: tuple, reason_fragment: str) -> None:
    outcome = attack_observations(observed)
    assert outcome.reason and reason_fragment in outcome.reason
    assert outcome.product is None and outcome.combined is None
    assert outcome.candidate is None and not outcome.exact


def test_attacker_rejects_nonsequence() -> None:
    outcome = attack_observations(None)
    assert outcome.used_count == 0 and outcome.reason


def test_evaluator_rejects_mismatched_experiment() -> None:
    scenario = sample_scenario(b"\x0c")
    observed = scenario.observations[:2]
    outcome = attack_observations(observed)
    with pytest.raises(ValueError, match="Outcome does not match"):
        evaluate_experiment(scenario, scenario.observations[1:], outcome)
    unrelated = PublicObservation("Alice", 7, 3, 1)
    with pytest.raises(ValueError, match="not from this scenario"):
        evaluate_experiment(scenario, (unrelated,), attack_observations((unrelated,)))


def test_attacker_api_has_only_public_input_and_output() -> None:
    assert tuple(inspect.signature(attack_observations).parameters) == ("observations",)
    assert {field.name for field in fields(PublicObservation)} == {"recipient_id", "n", "e", "c"}
    scenario = sample_scenario(b"\x0c")
    outcome = attack_observations(scenario.observations)
    assert not hasattr(outcome, "plaintext")
    assert not hasattr(outcome, "private_key")


def test_real_rsa_2048_integration_and_utf8() -> None:
    plaintext = b"\x00" + "Xin chào BroadcastGuard".encode("utf-8")
    scenario = build_scenario(plaintext)
    assert len(scenario.observations) == 3
    assert {item.recipient_id for item in scenario.observations} == set(NAMES)
    assert all(item.e == 3 and item.modulus_bits == 2048 for item in scenario.observations)
    assert all(0 <= item.c < item.n for item in scenario.observations)
    message = message_to_integer(plaintext)
    assert all(item.c == pow(message, 3, item.n) for item in scenario.observations)
    assert all(len(item.ciphertext_preview) <= 27 for item in scenario.observations)
    outcome = attack_observations((scenario.observations[2],))
    evaluation = evaluate_experiment(scenario, (scenario.observations[2],), outcome)
    assert evaluation.status == "recovered"
    assert evaluation.candidate_bytes == plaintext
    assert not any(hasattr(item, "private_key") for item in scenario.observations)


def test_builder_rejects_message_not_below_modulus() -> None:
    with pytest.raises(ValueError, match="smaller than every RSA modulus"):
        build_scenario(b"\xff" * 257)
