"""Stable CSV schemas, summaries and validation against recorded raw rows."""

from collections import Counter, defaultdict
import csv
import json
from pathlib import Path

from experiments.attack_and_defense import E1_FIELDS, E2_FIELDS, SUBSETS
from experiments.hybrid import E3_FIELDS, E4_FIELDS, KEYGEN_FIELDS
from experiments.methodology import (
    ATTACK_SAMPLES, DEFENSE_SAMPLE_IDS, E4_CASES, FILE_SIZES, RECIPIENT_COUNTS,
)
from experiments.statistics import describe_ns


SCHEMAS = {
    "attack_conditions.csv": E1_FIELDS,
    "oaep_comparison.csv": E2_FIELDS,
    "hybrid_performance.csv": E3_FIELDS,
    "key_generation.csv": KEYGEN_FIELDS,
    "security_validation.csv": E4_FIELDS,
}
TIMING_FIELDS = ("encryption_ns", "serialization_ns", "total_encryption_ns", "decryption_ns")


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path, fields: tuple[str, ...]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if tuple(reader.fieldnames or ()) != fields:
            raise ValueError(f"Schema mismatch: {path.name}.")
        rows = list(reader)
    if any(None in row for row in rows):
        raise ValueError(f"Malformed CSV row: {path.name}.")
    return rows


def _true(value: str) -> bool:
    if value not in ("True", "False"):
        raise ValueError("Expected a recorded boolean.")
    return value == "True"


def calculate_summary(manifest: dict, data: dict[str, list[dict[str, str]]]) -> dict:
    """Always compute from parsed CSV, never from unrecorded in-memory values."""
    e1, e2 = data["attack_conditions.csv"], data["oaep_comparison.csv"]
    e3, kg, e4 = (data[name] for name in ("hybrid_performance.csv",
                                           "key_generation.csv", "security_validation.csv"))
    result = {
        "run_id": manifest["run_id"], "mode": manifest["mode"],
        "row_counts": {name: len(rows) for name, rows in data.items()},
        "validation_failures": {name: sum(row["validation_pass"] != "True" for row in rows)
                                for name, rows in data.items()},
        "E1": {}, "E2": {}, "E3": {}, "E3_keygen": {}, "E4": {},
    }
    for sample_id, _ in ATTACK_SAMPLES:
        sample = [row for row in e1 if row["sample_id"] == sample_id]
        minimums = {
            (row["repetition"], row["minimum_successful_count"])
            for row in sample if row["minimum_successful_count"]
        }
        result["E1"][sample_id] = {
            "row_count": len(sample),
            "recovered_rows": sum(row["recovered_original"] == "True" for row in sample),
            "prediction_matches": sum(row["prediction_matches_recovery"] == "True"
                                      for row in sample),
            "minimum_count_distribution": dict(sorted(Counter(value for _, value in minimums).items())),
            "subset_recovery": {
                "+".join(subset): sum(row["subset"] == "+".join(subset)
                                     and row["recovered_original"] == "True" for row in sample)
                for subset in SUBSETS
            },
        }
    for sample_id in DEFENSE_SAMPLE_IDS:
        sample = [row for row in e2 if row["sample_id"] == sample_id]
        result["E2"][sample_id] = {
            "trials": len(sample),
            "textbook_recovered": sum(row["textbook_recovered"] == "True" for row in sample),
            "oaep_recovered": sum(row["oaep_recovered"] == "True" for row in sample),
            "legitimate_all_decrypt": sum(row["legitimate_all_decrypt"] == "True" for row in sample),
            "oaep_distinct": sum(row["oaep_ciphertexts_distinct"] == "True" for row in sample),
            "textbook_deterministic": sum(row["textbook_deterministic"] == "True" for row in sample),
        }
    for count in RECIPIENT_COUNTS:
        key_rows = [row for row in kg if row["recipient_count"] == str(count)]
        durations = [int(row["duration_ns"]) for row in key_rows if row["duration_ns"]]
        result["E3_keygen"][str(count)] = {
            "recorded": len(key_rows),
            "timing": describe_ns(durations) if durations else None,
        }
        for size in FILE_SIZES:
            case = f"{count}r_{size}b"
            sample = [row for row in e3 if row["case_id"] == case]
            result["E3"][case] = {
                "recorded": len(sample), "recipient_count": count, "file_size_bytes": size,
                "package_size_bytes": sorted({int(row["package_size_bytes"]) for row in sample
                                              if row["package_size_bytes"]}),
                "overhead_bytes": sorted({int(row["overhead_bytes"]) for row in sample
                                          if row["overhead_bytes"]}),
                "timing": {
                    field: describe_ns([int(row[field]) for row in sample if row[field]])
                    if any(row[field] for row in sample) else None
                    for field in TIMING_FIELDS
                },
            }
    for case in E4_CASES:
        sample = [row for row in e4 if row["case_id"] == case]
        result["E4"][case] = {
            "expected": sample[0]["expected_status"] if sample else None,
            "observed": sample[0]["observed_status"] if sample else None,
            "passed": sample[0]["validation_pass"] == "True" if sample else False,
        }
    result["complete"] = all(count == 0 for count in result["validation_failures"].values())
    return result


def _expected_keys(manifest: dict, name: str) -> Counter:
    repetitions = manifest["repetitions"]
    if name == "attack_conditions.csv":
        return Counter((sample + ":" + "+".join(subset), str(rep))
                       for sample, _ in ATTACK_SAMPLES for subset in SUBSETS
                       for rep in range(repetitions))
    if name == "oaep_comparison.csv":
        return Counter((sample, str(rep)) for sample in DEFENSE_SAMPLE_IDS
                       for rep in range(repetitions))
    if name == "hybrid_performance.csv":
        return Counter((f"{count}r_{size}b", str(rep)) for count in RECIPIENT_COUNTS
                       for size in FILE_SIZES for rep in range(repetitions))
    if name == "key_generation.csv":
        return Counter((str(count), str(rep)) for count in RECIPIENT_COUNTS
                       for rep in range(repetitions))
    return Counter((case, "0") for case in E4_CASES)


def _validate_output(directory: Path) -> tuple[bool, list[str]]:
    """Independent, read-back validation of schemas, counts, invariants and summary."""
    problems: list[str] = []
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((directory / "summary.json").read_text(encoding="utf-8"))
    data = {name: read_csv(directory / name, fields) for name, fields in SCHEMAS.items()}
    for name, rows in data.items():
        observed = Counter((row["case_id"], row["repetition"]) for row in rows)
        if observed != _expected_keys(manifest, name):
            problems.append(name + ": missing, duplicate or unexpected case/repetition")
        if any(row["run_id"] != manifest["run_id"] for row in rows):
            problems.append(name + ": run_id mismatch")
        if any(row["validation_pass"] != "True" or row["error_type"] for row in rows):
            problems.append(name + ": failed measured repetition")
    for row in data["attack_conditions.csv"]:
        if row["validation_pass"] == "True":
            if (_true(row["bound_holds"]) != _true(row["recovered_original"])
                    or not _true(row["prediction_matches_recovery"])
                    or not _true(row["message_lt_each_modulus"])):
                problems.append("E1: mathematical prediction mismatch")
            if int(row["modulus_product_bits"]) < 2048:
                problems.append("E1: invalid modulus product size")
    sample_lookup = dict(ATTACK_SAMPLES)
    e1_groups = defaultdict(list)
    for row in data["attack_conditions.csv"]:
        e1_groups[row["repetition"], row["sample_id"]].append(row)
        if row["sample_id"] in sample_lookup and row["validation_pass"] == "True":
            message = sample_lookup[row["sample_id"]]
            if (int(row["message_length_bytes"]) != len(message)
                    or int(row["message_bits"]) != int.from_bytes(message, "big").bit_length()
                    or int(row["recipient_count"]) != len(row["subset"].split("+"))):
                problems.append("E1: sample metadata mismatch")
    for rows in e1_groups.values():
        keysets = {row["keyset_id"] for row in rows}
        minimum = min((int(row["recipient_count"]) for row in rows
                       if row["recovered_original"] == "True"), default=None)
        if (len(keysets) != 1 or not next(iter(keysets))
                or any(row["minimum_successful_count"] !=
                       (str(minimum) if minimum is not None else "") for row in rows)):
            problems.append("E1: key reuse or minimum successful count mismatch")
    for row in data["oaep_comparison.csv"]:
        if row["validation_pass"] == "True" and not all(_true(row[field]) for field in (
            "same_public_keys", "textbook_recovered", "legitimate_all_decrypt",
            "textbook_deterministic", "oaep_ciphertexts_distinct", "oaep_repeated_all_decrypt"
        )):
            problems.append("E2: paired comparison or decryption mismatch")
    e1_keys = defaultdict(set)
    for row in data["attack_conditions.csv"]:
        e1_keys[row["repetition"]].add(row["keyset_id"])
    for row in data["oaep_comparison.csv"]:
        if row["keyset_id"] not in e1_keys[row["repetition"]] or len(e1_keys[row["repetition"]]) != 1:
            problems.append("E1/E2: key set mismatch")
        if (row["validation_pass"] == "True"
                and (row["sample_id"] not in sample_lookup
                     or int(row["message_length_bytes"]) != len(sample_lookup[row["sample_id"]])
                     or int(row["randomization_trials"]) < 2
                     or _true(row["oaep_recovered"]))):
            problems.append("E2: comparison metadata or recovery mismatch")
    prepared_ids = {row["prepared_keyset_id"] for row in data["hybrid_performance.csv"]}
    if len(prepared_ids) != 1 or not next(iter(prepared_ids)):
        problems.append("E3: prepared key set changed across configurations")
    for row in data["hybrid_performance.csv"]:
        if row["validation_pass"] != "True":
            continue
        try:
            size = int(row["file_size_bytes"])
            package_size = int(row["package_size_bytes"])
            overhead = int(row["overhead_bytes"])
            durations = [int(row[field]) for field in TIMING_FIELDS]
            if (any(value <= 0 for value in durations) or overhead != package_size - size
                    or durations[2] != durations[0] + durations[1]
                    or abs(float(row["overhead_percent"]) - 100 * overhead / size) > 1e-8
                    or not _true(row["decrypted_correctly"]) or row["package_version"] != "1"):
                problems.append("E3: invalid timing, overhead or decryption")
        except (TypeError, ValueError):
            problems.append("E3: malformed numeric value")
    for row in data["key_generation.csv"]:
        if row["validation_pass"] == "True" and (
            int(row["duration_ns"]) <= 0 or not _true(row["valid_keys"])):
            problems.append("E3 keygen: invalid duration or keys")
    for row in data["security_validation.csv"]:
        if row["validation_pass"] == "True":
            expected = row["expected_status"]
            prescribed = "decrypted" if row["case_id"] == "valid_recipient" else (
                "invalid_package" if row["case_id"] in ("unsupported_version", "invalid_json")
                else "decryption_failed")
            if (expected != prescribed or row["observed_status"] != expected
                    or _true(row["plaintext_returned"]) != (expected == "decrypted")
                    or _true(row["rejected"]) == (expected == "decrypted")):
                problems.append("E4: rejection or plaintext-return mismatch")
    if summary != calculate_summary(manifest, data):
        problems.append("summary.json differs from the raw CSV measurements")
    forbidden = ("-----BEGIN PRIVATE KEY-----", "-----BEGIN RSA PRIVATE KEY-----",
                 '"private_key":', '"aes_key":', '"hostname":', '"username":',
                 "C:\\Users\\")
    for path in directory.iterdir():
        if path.suffix not in (".csv", ".json", ".md"):
            continue
        contents = path.read_text(encoding="utf-8")
        if any(marker in contents for marker in forbidden):
            problems.append(path.name + ": forbidden sensitive output marker")
    return not problems, problems


def validate_output(directory: Path) -> tuple[bool, list[str]]:
    """Return a controlled validation failure for corrupted or incomplete output."""
    try:
        return _validate_output(directory)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        return False, [f"Malformed or incomplete dataset: {type(error).__name__}: {error}"]
