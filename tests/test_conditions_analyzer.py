"""Deterministic subset analysis plus one real RSA-2048 integration test."""

from dataclasses import replace
from itertools import combinations
from math import prod

import pytest

from broadcastguard.attack_lab import (
    AttackScenario,
    PublicObservation,
    attack_observations,
    build_scenario,
    evaluate_experiment,
)
from broadcastguard.conditions_analyzer import (
    ScenarioAnalysis,
    analyze_scenario,
    sweep_message_lengths,
)
from broadcastguard.math_core import message_to_integer

NAMES = ("Alice", "Bob", "Charlie")
SMALL_MODULI = (55, 391, 1189)
EXPECTED_SUBSETS = tuple(
    names for count in (1, 2, 3) for names in combinations(NAMES, count)
)


def scenario_for(plaintext: bytes, moduli: tuple[int, int, int] = SMALL_MODULI) -> AttackScenario:
    message = message_to_integer(plaintext)
    return AttackScenario(
        plaintext,
        tuple(
            PublicObservation(name, n, 3, pow(message, 3, n))
            for name, n in zip(NAMES, moduli)
        ),
    )


def test_all_seven_subsets_are_ordered_labeled_and_computed() -> None:
    scenario = scenario_for(b"\x0c")
    result = analyze_scenario(scenario)
    assert len(result.subsets) == 7
    assert tuple(row.recipient_ids for row in result.subsets) == EXPECTED_SUBSETS
    assert [row.count for row in result.subsets] == [1, 1, 1, 2, 2, 2, 3]
    modulus_by_name = dict(zip(NAMES, SMALL_MODULI))
    for row in result.subsets:
        expected_product = prod(modulus_by_name[name] for name in row.recipient_ids)
        assert row.modulus_product == expected_product
        assert row.product_bits == expected_product.bit_length()
        assert row.crt_value == 12**3 % expected_product
        assert row.bound_holds == (12**3 < expected_product)
        assert row.recovered == (row.exact_root and row.candidate == 12)
        assert row.matches_prediction
        assert row.to_row()["status"] == row.status
        assert row.explanation.startswith("Experimenter:")
    assert result.minimum_successful_count == 2
    assert len(result.successful_subsets) == 4
    assert result.table_rows()[0]["subset"] == "Alice"


def test_different_recipient_pairs_can_change_the_result() -> None:
    result = analyze_scenario(scenario_for(b"\x1e"))  # M=30
    by_ids = {row.recipient_ids: row for row in result.subsets}
    assert not by_ids[("Alice", "Bob")].recovered
    assert by_ids[("Alice", "Charlie")].recovered
    assert by_ids[("Bob", "Charlie")].recovered
    assert result.minimum_successful_count == 2


@pytest.mark.parametrize("plaintext,moduli,minimum", [
    (b"\x02", SMALL_MODULI, 1),
    (b"\x0c", SMALL_MODULI, 2),
    (b"\x0a", (11, 13, 17), 3),
])
def test_minimum_counts_from_actual_products(
    plaintext: bytes, moduli: tuple[int, int, int], minimum: int
) -> None:
    result = analyze_scenario(scenario_for(plaintext, moduli))
    assert result.minimum_successful_count == minimum
    assert all(row.count >= minimum for row in result.subsets if row.recovered)
    assert any(row.count == minimum for row in result.subsets if row.recovered)
    assert all(row.matches_prediction for row in result.subsets)


def test_exact_root_is_not_automatically_original_plaintext() -> None:
    result = analyze_scenario(scenario_for(b"\x02", (7, 11, 13)))
    alice = result.subsets[0]
    assert alice.recipient_ids == ("Alice",)
    assert alice.crt_value == 1 and alice.candidate == 1
    assert alice.exact_root and not alice.recovered
    assert not alice.bound_holds
    assert alice.status == "wrong_exact_root"
    assert "not the original" in alice.explanation


def test_leading_zero_and_utf8_bytes_remain_intact() -> None:
    zero_scenario = scenario_for(b"\x00\x00\x0c")
    zero_analysis = analyze_scenario(zero_scenario)
    assert zero_analysis.message_length == 3
    selected = zero_scenario.observations[1:]
    evaluation = evaluate_experiment(zero_scenario, selected, attack_observations(selected))
    assert evaluation.candidate_bytes == b"\x00\x00\x0c"

    utf8_bytes = "é".encode("utf-8")
    utf8_scenario = scenario_for(utf8_bytes, (65537, 65539, 65543))
    utf8_analysis = analyze_scenario(utf8_scenario)
    assert utf8_analysis.message_length == len(utf8_bytes)
    assert utf8_analysis.message_bits == message_to_integer(utf8_bytes).bit_length()
    assert utf8_analysis.subsets[-1].recovered
    selected = utf8_scenario.observations
    assert evaluate_experiment(
        utf8_scenario, selected, attack_observations(selected)
    ).candidate_bytes == utf8_bytes


def test_no_success_aggregation_is_explicit_none() -> None:
    # With three valid RSA moduli all > M, the full set always succeeds.
    # Empty or filtered result sets still need honest summary behavior.
    result = ScenarioAnalysis(message_length=1, message_bits=7, subsets=())
    assert result.minimum_successful_count is None
    assert result.successful_subsets == ()


@pytest.mark.parametrize("mutation,reason", [
    (lambda s: replace(s, observations=s.observations[:2]), "exactly three"),
    (lambda s: replace(s, observations=(s.observations[0],) * 3), "Invalid public"),
    (
        lambda s: replace(
            s, observations=(replace(s.observations[0], c=0), *s.observations[1:])
        ),
        "inconsistent",
    ),
    (lambda s: replace(s, plaintext=b"\xff"), "smaller than every modulus"),
    (lambda s: replace(s, plaintext=b""), "empty"),
])
def test_inconsistent_scenarios_fail_clearly(mutation, reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        analyze_scenario(mutation(scenario_for(b"\x0c")))


def test_bad_scenario_type_and_bad_moduli_are_rejected() -> None:
    with pytest.raises(TypeError, match="AttackScenario"):
        analyze_scenario(None)
    scenario = scenario_for(b"\x0c")
    duplicate = replace(scenario.observations[1], n=55)
    with pytest.raises(ValueError, match="Invalid public"):
        analyze_scenario(
            replace(
                scenario,
                observations=(scenario.observations[0], duplicate, scenario.observations[2]),
            )
        )


@pytest.mark.parametrize("lengths,exception", [
    ((), ValueError), ([0], ValueError), ([True], ValueError),
    ([1, 1], ValueError), ("1", TypeError), ([257], ValueError),
])
def test_sweep_rejects_invalid_lengths(lengths, exception: type[Exception]) -> None:
    with pytest.raises(exception):
        sweep_message_lengths(scenario_for(b"\x0c"), lengths)


def test_real_rsa_2048_sweep_reuses_public_moduli() -> None:
    base = build_scenario(b"B")
    assert all(item.modulus_bits == 2048 for item in base.observations)
    sweep = sweep_message_lengths(base)
    assert [analysis.message_length for analysis in sweep.analyses] == [1, 96, 180]
    assert [analysis.minimum_successful_count for analysis in sweep.analyses] == [1, 2, 3]
    assert all(len(analysis.subsets) == 7 for analysis in sweep.analyses)
    assert len(sweep.comparison_rows()) == 21
    assert all(row["matches_prediction"] for row in sweep.comparison_rows())
    matrix = sweep.matrix_rows()
    assert len(matrix) == 3
    assert set(matrix[0]) == {"message_length", "message_bits"} | {
        " + ".join(names) for names in EXPECTED_SUBSETS
    }
    assert matrix[0]["Alice"] == "recovered"
    assert matrix[1]["Alice"] != "recovered" and matrix[1]["Alice + Bob"] == "recovered"
    assert matrix[2]["Alice + Bob"] != "recovered"
    assert matrix[2]["Alice + Bob + Charlie"] == "recovered"
    assert sweep.minimum_rows() == [
        {"message_length": 1, "minimum_successful_count": 1},
        {"message_length": 96, "minimum_successful_count": 2},
        {"message_length": 180, "minimum_successful_count": 3},
    ]
    by_subset = {
        row["subset"]: row["modulus_product"]
        for row in sweep.comparison_rows()
        if row["message_length"] == 1
    }
    for length in (96, 180):
        assert {
            row["subset"]: row["modulus_product"]
            for row in sweep.comparison_rows()
            if row["message_length"] == length
        } == by_subset
