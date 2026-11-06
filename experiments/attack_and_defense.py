"""E1/E2: paired, public-only broadcast analysis and OAEP comparison."""

from itertools import combinations

from cryptography.hazmat.primitives.asymmetric import rsa

from broadcastguard.attack_lab import AttackScenario, PublicObservation, RECIPIENT_IDS
from broadcastguard.conditions_analyzer import analyze_scenario
from broadcastguard.defense_lab import run_defense_comparison
from experiments.methodology import ATTACK_SAMPLES, DEFENSE_SAMPLE_IDS, RunConfig, keyset_id


E1_FIELDS = (
    "run_id", "experiment_id", "case_id", "repetition", "keyset_id", "sample_id",
    "message_length_bytes", "message_bits", "subset", "recipient_count",
    "modulus_product_bits", "message_lt_each_modulus", "bound_holds",
    "exact_root", "recovered_original", "status", "minimum_successful_count",
    "prediction_matches_recovery", "validation_pass", "error_type",
)
E2_FIELDS = (
    "run_id", "experiment_id", "case_id", "repetition", "keyset_id", "sample_id",
    "message_length_bytes", "same_public_keys", "textbook_status", "textbook_exact_root",
    "textbook_recovered", "oaep_status", "oaep_exact_root", "oaep_recovered",
    "legitimate_all_decrypt", "textbook_deterministic", "oaep_ciphertexts_distinct",
    "oaep_repeated_all_decrypt", "randomization_trials", "validation_pass", "error_type",
)

SUBSETS = tuple(tuple(names) for count in (1, 2, 3)
                for names in combinations(RECIPIENT_IDS, count))


def _scenario(message: bytes, keys: tuple[rsa.RSAPrivateKey, ...]) -> AttackScenario:
    """Controlled educational encryption with existing public moduli.

    build_scenario() would generate a second key set, confounding E1 versus E2.
    Eve still receives only PublicObservation through analyze_scenario().
    """
    value = int.from_bytes(message, "big")
    public = tuple(key.public_key().public_numbers() for key in keys)
    if not message or any(value >= item.n for item in public):
        raise ValueError("Message must be nonempty and smaller than every modulus.")
    observations = tuple(
        PublicObservation(name, item.n, item.e, pow(value, item.e, item.n))
        for name, item in zip(RECIPIENT_IDS, public)
    )
    return AttackScenario(message, observations)


def _e1_failure(run_id: str, repetition: int, sample_id: str, subset: tuple[str, ...],
                key_id: str, error: Exception) -> dict[str, object]:
    return {
        "run_id": run_id, "experiment_id": "E1", "case_id": sample_id + ":" + "+".join(subset),
        "repetition": repetition, "keyset_id": key_id, "sample_id": sample_id,
        "subset": "+".join(subset), "recipient_count": len(subset),
        "status": "error", "validation_pass": False, "error_type": type(error).__name__,
    }


def _e2_failure(run_id: str, repetition: int, sample_id: str, key_id: str,
                error: Exception) -> dict[str, object]:
    return {
        "run_id": run_id, "experiment_id": "E2", "case_id": sample_id,
        "repetition": repetition, "keyset_id": key_id, "sample_id": sample_id,
        "validation_pass": False, "error_type": type(error).__name__,
    }


def run_attack_and_defense(config: RunConfig, run_id: str) -> tuple[list[dict], list[dict]]:
    """Use independent key sets across repetitions, paired within each trial."""
    e1_rows: list[dict] = []
    e2_rows: list[dict] = []
    for repetition in range(config.repetitions):
        try:
            keys = tuple(rsa.generate_private_key(public_exponent=3, key_size=2048)
                         for _ in RECIPIENT_IDS)
            key_id = keyset_id(keys)
        except Exception as error:
            for sample_id, _ in ATTACK_SAMPLES:
                e1_rows.extend(_e1_failure(run_id, repetition, sample_id, subset, "", error)
                               for subset in SUBSETS)
                if sample_id in DEFENSE_SAMPLE_IDS:
                    e2_rows.append(_e2_failure(run_id, repetition, sample_id, "", error))
            continue

        for sample_id, message in ATTACK_SAMPLES:
            try:
                scenario = _scenario(message, keys)
                analysis = analyze_scenario(scenario)
                message_lt_each = all(int.from_bytes(message, "big") < item.n
                                      for item in scenario.observations)
                for row in analysis.subsets:
                    e1_rows.append({
                        "run_id": run_id, "experiment_id": "E1",
                        "case_id": sample_id + ":" + "+".join(row.recipient_ids),
                        "repetition": repetition, "keyset_id": key_id, "sample_id": sample_id,
                        "message_length_bytes": len(message), "message_bits": analysis.message_bits,
                        "subset": "+".join(row.recipient_ids), "recipient_count": row.count,
                        "modulus_product_bits": row.product_bits,
                        "message_lt_each_modulus": message_lt_each,
                        "bound_holds": row.bound_holds, "exact_root": row.exact_root,
                        "recovered_original": row.recovered, "status": row.status,
                        "minimum_successful_count": analysis.minimum_successful_count,
                        "prediction_matches_recovery": row.matches_prediction,
                        "validation_pass": message_lt_each and row.matches_prediction,
                        "error_type": "",
                    })
            except Exception as error:
                e1_rows.extend(_e1_failure(run_id, repetition, sample_id, subset, key_id, error)
                               for subset in SUBSETS)

            if sample_id not in DEFENSE_SAMPLE_IDS:
                continue
            try:
                comparison = run_defense_comparison(message, private_keys=keys)
                same_keys = all(
                    raw.public.n == padded.public.n == key.public_key().public_numbers().n
                    and raw.public.e == padded.public.e == 3
                    for raw, padded, key in zip(comparison.scenario.textbook_observations,
                                                comparison.scenario.oaep_observations, keys)
                )
                randomization = comparison.randomization
                legitimate = all(item.recovered_original_bytes for item in comparison.decryptions)
                valid = (same_keys and comparison.scenario.plaintext == message and legitimate
                         and comparison.textbook.recovered_original
                         and not comparison.oaep.recovered_original
                         and randomization.textbook_ciphertexts_identical
                         and randomization.oaep_ciphertexts_distinct
                         and randomization.oaep_all_decrypt)
                e2_rows.append({
                    "run_id": run_id, "experiment_id": "E2", "case_id": sample_id,
                    "repetition": repetition, "keyset_id": key_id, "sample_id": sample_id,
                    "message_length_bytes": len(message), "same_public_keys": same_keys,
                    "textbook_status": comparison.textbook.status,
                    "textbook_exact_root": comparison.textbook.outcome.exact,
                    "textbook_recovered": comparison.textbook.recovered_original,
                    "oaep_status": comparison.oaep.status,
                    "oaep_exact_root": comparison.oaep.outcome.exact,
                    "oaep_recovered": comparison.oaep.recovered_original,
                    "legitimate_all_decrypt": legitimate,
                    "textbook_deterministic": randomization.textbook_ciphertexts_identical,
                    "oaep_ciphertexts_distinct": randomization.oaep_ciphertexts_distinct,
                    "oaep_repeated_all_decrypt": randomization.oaep_all_decrypt,
                    "randomization_trials": randomization.trial_count,
                    "validation_pass": valid, "error_type": "",
                })
            except Exception as error:
                e2_rows.append(_e2_failure(run_id, repetition, sample_id, key_id, error))
    return e1_rows, e2_rows
