"""Controlled RSA-OAEP comparison and public/private boundary tests."""

from dataclasses import asdict, fields
import inspect

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from broadcastguard.attack_lab import PublicObservation, attack_observations
from broadcastguard.defense_lab import (
    OAEP_MAX_MESSAGE_BYTES,
    DefenseComparison,
    SchemeObservation,
    _evaluate_attack,
    _oaep_padding,
    run_defense_comparison,
)
from broadcastguard.math_core import integer_to_message, message_to_integer


@pytest.fixture(scope="module")
def keys() -> tuple[rsa.RSAPrivateKey, ...]:
    return tuple(rsa.generate_private_key(public_exponent=3, key_size=2048) for _ in range(3))


@pytest.fixture(scope="module")
def comparison_180(keys: tuple[rsa.RSAPrivateKey, ...]) -> DefenseComparison:
    return run_defense_comparison(b"B" * 180, private_keys=keys)


def test_same_plaintext_keys_exponent_and_recipients(comparison_180: DefenseComparison) -> None:
    scenario = comparison_180.scenario
    assert scenario.plaintext == b"B" * 180
    assert tuple(item.recipient_id for item in scenario.textbook_observations) == (
        "Alice", "Bob", "Charlie"
    )
    assert tuple(item.recipient_id for item in scenario.oaep_observations) == (
        "Alice", "Bob", "Charlie"
    )
    for textbook, oaep in zip(scenario.textbook_observations, scenario.oaep_observations):
        assert textbook.scheme == "textbook" and oaep.scheme == "oaep"
        assert (textbook.public.n, textbook.public.e) == (oaep.public.n, oaep.public.e)
        assert textbook.public.e == 3 and textbook.public.modulus_bits == 2048
        assert textbook.public.c == pow(message_to_integer(scenario.plaintext), 3, textbook.public.n)
        assert 0 <= oaep.public.c < oaep.public.n


def test_textbook_recovers_with_three_not_two(comparison_180: DefenseComparison) -> None:
    result = comparison_180.textbook
    assert result.outcome.used_count == 3
    assert result.outcome.exact
    assert result.outcome.candidate == message_to_integer(comparison_180.scenario.plaintext)
    assert result.recovered_original and result.status == "recovered"
    assert result.textbook_bound_holds is True
    for count in (1, 2):
        public = tuple(item.public for item in comparison_180.scenario.textbook_observations[:count])
        outcome = attack_observations(public)
        assert not (outcome.exact and outcome.candidate == message_to_integer(comparison_180.scenario.plaintext))


def test_same_attack_fails_to_recover_oaep_and_legitimate_decryption_succeeds(
    comparison_180: DefenseComparison,
) -> None:
    result = comparison_180.oaep
    assert result.outcome.used_count == 3
    assert not result.recovered_original
    assert result.status in ("no_exact_root", "wrong_exact_root")
    assert result.textbook_bound_holds is None
    assert tuple((item.recipient_id, item.recovered_original_bytes) for item in comparison_180.decryptions) == (
        ("Alice", True), ("Bob", True), ("Charlie", True)
    )


def test_exact_root_does_not_confirm_plaintext_in_defense_evaluator() -> None:
    observation = SchemeObservation("oaep", PublicObservation("Alice", 7, 3, 1))
    outcome = attack_observations((observation.public,))
    result = _evaluate_attack(b"\x02", (observation,), outcome)
    assert outcome.exact and outcome.candidate == 1
    assert result.status == "wrong_exact_root"
    assert not result.recovered_original
    assert result.candidate_bytes == b"\x01"
    assert result.textbook_bound_holds is None


def test_randomization_and_determinism(comparison_180: DefenseComparison) -> None:
    result = comparison_180.randomization
    assert result.recipient_id == "Alice" and result.trial_count == 3
    assert result.textbook_ciphertexts_identical
    assert result.oaep_ciphertexts_distinct
    assert result.oaep_all_decrypt


@pytest.mark.parametrize("length", [1, 96, 180, 190])
def test_supported_message_lengths(length: int, keys: tuple[rsa.RSAPrivateKey, ...]) -> None:
    comparison = run_defense_comparison(b"B" * length, private_keys=keys, randomization_trials=2)
    assert comparison.textbook.recovered_original
    assert not comparison.oaep.recovered_original
    assert all(item.recovered_original_bytes for item in comparison.decryptions)
    assert comparison.randomization.oaep_ciphertexts_distinct


def test_oaep_limit_and_bad_inputs(keys: tuple[rsa.RSAPrivateKey, ...]) -> None:
    assert OAEP_MAX_MESSAGE_BYTES == 190
    with pytest.raises(ValueError, match="at most 190 bytes"):
        run_defense_comparison(b"B" * 191, private_keys=keys)
    with pytest.raises(ValueError, match="empty"):
        run_defense_comparison(b"", private_keys=keys)
    for invalid in (None, "hello", bytearray(b"B"), 3):
        with pytest.raises(TypeError):
            run_defense_comparison(invalid, private_keys=keys)
    with pytest.raises(ValueError, match="at least 2"):
        run_defense_comparison(b"B", private_keys=keys, randomization_trials=1)
    with pytest.raises(TypeError, match="integer"):
        run_defense_comparison(b"B", private_keys=keys, randomization_trials=True)


@pytest.mark.parametrize("message", [b"\x00\x00Hi", "Xin chào 👋".encode("utf-8")])
def test_bytes_preserved(message: bytes, keys: tuple[rsa.RSAPrivateKey, ...]) -> None:
    comparison = run_defense_comparison(message, private_keys=keys, randomization_trials=2)
    assert comparison.scenario.plaintext == message
    assert comparison.textbook.candidate_bytes == message
    assert integer_to_message(comparison.textbook.outcome.candidate, len(message)) == message
    assert all(item.recovered_original_bytes for item in comparison.decryptions)


def test_tampering_and_wrong_recipient_key_rejected(
    comparison_180: DefenseComparison, keys: tuple[rsa.RSAPrivateKey, ...]
) -> None:
    observations = comparison_180.scenario.oaep_observations
    alice_ciphertext = observations[0].public.c.to_bytes(256, "big")
    tampered = alice_ciphertext[:-1] + bytes([alice_ciphertext[-1] ^ 1])
    with pytest.raises(ValueError):
        keys[0].decrypt(tampered, _oaep_padding())
    with pytest.raises(ValueError):
        keys[1].decrypt(alice_ciphertext, _oaep_padding())
    assert keys[0].decrypt(alice_ciphertext, _oaep_padding()) == comparison_180.scenario.plaintext


def test_attacker_only_receives_public_data_and_results_contain_no_keys(
    comparison_180: DefenseComparison,
) -> None:
    assert tuple(inspect.signature(attack_observations).parameters) == ("observations",)
    for observations in (
        comparison_180.scenario.textbook_observations,
        comparison_180.scenario.oaep_observations,
    ):
        assert all(isinstance(item.public, PublicObservation) for item in observations)
        outcome = attack_observations(tuple(item.public for item in observations))
        assert outcome.recipient_ids == ("Alice", "Bob", "Charlie")
    assert "private" not in repr(comparison_180).lower()
    assert not any("key" in field.name for field in fields(DefenseComparison))
    assert not any(isinstance(value, rsa.RSAPrivateKey) for value in asdict(comparison_180).values())


def test_summary_and_recipient_rows_are_short_and_semantic(comparison_180: DefenseComparison) -> None:
    summary = comparison_180.summary_rows()
    assert [row["scheme"] for row in summary] == ["textbook", "oaep"]
    assert [row["recovered_original"] for row in summary] == [True, False]
    assert [row["legitimate_decryption"] for row in summary] == [None, True]
    assert all(len(row["attack_candidate_preview"]) < 40 for row in summary)
    rows = comparison_180.recipient_rows()
    assert len(rows) == 6
    assert all(len(row["ciphertext_preview"]) < 40 for row in rows)
    assert all(row["legitimate_decryption"] is True for row in rows[3:])
    assert comparison_180.detail_rows()[1]["textbook_bound_holds"] is None


def test_invalid_key_configuration_rejected(keys: tuple[rsa.RSAPrivateKey, ...]) -> None:
    with pytest.raises(ValueError, match="Exactly three"):
        run_defense_comparison(b"B", private_keys=keys[:2])
    wrong_exponent = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with pytest.raises(ValueError, match="e=3"):
        run_defense_comparison(b"B", private_keys=(keys[0], keys[1], wrong_exponent))
    with pytest.raises(ValueError, match="pairwise coprime"):
        run_defense_comparison(b"B", private_keys=(keys[0], keys[0], keys[2]))
