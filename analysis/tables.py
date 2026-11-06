"""Read, validate, summarize and export official TASK 08 evidence."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import fmean, median, stdev
from typing import Any

from experiments.attack_and_defense import SUBSETS
from experiments.evidence import SCHEMAS, calculate_summary, read_csv, validate_output
from experiments.methodology import ATTACK_SAMPLES, DEFENSE_SAMPLE_IDS, E4_CASES, FILE_SIZES, RECIPIENT_COUNTS
from .models import ciphertext_base64_chars, metadata_bytes, predicted_overhead_bytes, predicted_package_size

EXPECTED_RUN_ID = "official-20261106T083221Z-3bbf57cc"
EXPECTED_SOURCE_SHA = "46c455819e4588736d4777c252d844fa03e7caf3"
EXPECTED_EVIDENCE_ROWS = {
    "attack_conditions.csv": 560,
    "oaep_comparison.csv": 60,
    "hybrid_performance.csv": 180,
    "key_generation.csv": 60,
    "security_validation.csv": 11,
}


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def describe(values: list[float]) -> dict[str, float | int]:
    if not values:
        raise ValueError("cannot describe an empty sample")
    q1 = _percentile(values, 0.25)
    q3 = _percentile(values, 0.75)
    return {"n": len(values), "mean": fmean(values), "median": median(values),
            "sd": stdev(values) if len(values) > 1 else 0.0, "q1": q1, "q3": q3,
            "iqr": q3 - q1, "min": min(values), "max": max(values)}


def load_official_evidence(input_dir: Path) -> tuple[dict[str, Any], dict[str, list[dict[str, str]]]]:
    """Fail closed before any table or plot computation."""
    valid, problems = validate_output(input_dir)
    if not valid:
        raise ValueError("official evidence validation failed: " + "; ".join(problems))
    try:
        manifest = json.loads((input_dir / "manifest.json").read_text(encoding="utf-8"))
        summary = json.loads((input_dir / "summary.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read evidence metadata: {error}") from error
    if manifest.get("run_id") != EXPECTED_RUN_ID:
        raise ValueError("unexpected official run_id")
    if manifest.get("git_commit") != EXPECTED_SOURCE_SHA:
        raise ValueError("unexpected source SHA in official manifest")
    if manifest.get("mode") != "official" or manifest.get("repetitions") != 20:
        raise ValueError("input is not the reviewed official 20-repetition dataset")
    if manifest.get("timing_unit") != "nanoseconds" or manifest.get("timing_clock") != "time.perf_counter_ns":
        raise ValueError("unexpected timing units or clock")
    data = {name: read_csv(input_dir / name, fields) for name, fields in SCHEMAS.items()}
    counts = {name: len(rows) for name, rows in data.items()}
    if counts != EXPECTED_EVIDENCE_ROWS:
        raise ValueError(f"unexpected evidence row counts: {counts}")
    if any(row["run_id"] != EXPECTED_RUN_ID for rows in data.values() for row in rows):
        raise ValueError("run_id mismatch in raw CSV")
    if any(row["validation_pass"] != "True" or row["error_type"] for rows in data.values() for row in rows):
        raise ValueError("raw CSV contains failed validation rows")
    if calculate_summary(manifest, data) != summary:
        raise ValueError("summary.json does not match raw CSV")
    return manifest, data


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty table: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _e1_tables(data: dict[str, list[dict[str, str]]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    rows = data["attack_conditions.csv"]
    matrix = []
    minimums = []
    for sample_id, message in ATTACK_SAMPLES:
        selected = [row for row in rows if row["sample_id"] == sample_id]
        item: dict[str, object] = {"sample_id": sample_id, "message_length_bytes": len(message),
                                   "message_bits": int.from_bytes(message, "big").bit_length()}
        for subset in SUBSETS:
            label = "+".join(subset)
            item[label] = sum(row["recovered_original"] == "True" for row in selected if row["subset"] == label)
        min_values = sorted({row["minimum_successful_count"] for row in selected})
        minimums.append({"sample_id": sample_id, "message_length_bytes": len(message),
                         "message_integer": int.from_bytes(message, "big"),
                         "minimum_successful_count": int(min_values[0]), "blocks": len({row["repetition"] for row in selected}),
                         "prediction_matches": all(row["prediction_matches_recovery"] == "True" for row in selected)})
        matrix.append(item)
    return matrix, minimums


def _e2_table(data: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    rows = data["oaep_comparison.csv"]
    result = []
    for sample_id in (*DEFENSE_SAMPLE_IDS, "all"):
        selected = rows if sample_id == "all" else [row for row in rows if row["sample_id"] == sample_id]
        result.append({"sample_id": sample_id, "comparisons": len(selected),
                       "textbook_recovery": sum(row["textbook_recovered"] == "True" for row in selected),
                       "oaep_recovery": sum(row["oaep_recovered"] == "True" for row in selected),
                       "legitimate_oaep_decryption": sum(row["legitimate_all_decrypt"] == "True" for row in selected),
                       "textbook_deterministic": sum(row["textbook_deterministic"] == "True" for row in selected),
                       "oaep_ciphertexts_distinct": sum(row["oaep_ciphertexts_distinct"] == "True" for row in selected),
                       "oaep_repeated_decryption": sum(row["oaep_repeated_all_decrypt"] == "True" for row in selected)})
    return result


def _e3_table(data: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in data["hybrid_performance.csv"]:
        grouped[row["case_id"]].append(row)
    output = []
    for count in RECIPIENT_COUNTS:
        for size in FILE_SIZES:
            selected = grouped[f"{count}r_{size}b"]
            result: dict[str, object] = {"case_id": f"{count}r_{size}b", "recipient_count": count,
                "file_size_bytes": size, "package_size_bytes": int(selected[0]["package_size_bytes"]),
                "overhead_bytes": int(selected[0]["overhead_bytes"]), "overhead_percent": float(selected[0]["overhead_percent"]),
                "ciphertext_base64_chars": ciphertext_base64_chars(size),
                "model_package_size_bytes": predicted_package_size(size, count),
                "model_overhead_bytes": predicted_overhead_bytes(size, count), "model_metadata_bytes": metadata_bytes(size, count)}
            result["model_metadata_increment_vs_1r"] = metadata_bytes(size, count) - metadata_bytes(size, 1)
            result["model_residual_bytes"] = result["package_size_bytes"] - result["model_package_size_bytes"]
            for field in ("encryption_ns", "serialization_ns", "total_encryption_ns", "decryption_ns"):
                prefix = field.removesuffix("_ns") + "_ms"
                for metric, value in describe([int(row[field]) / 1_000_000 for row in selected]).items():
                    result[f"{prefix}_{metric}"] = value
            output.append(result)
    return output


def _e3_keygen_table(data: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    output = []
    rows = data["key_generation.csv"]
    for count in RECIPIENT_COUNTS:
        selected = [row for row in rows if int(row["recipient_count"]) == count]
        result = {"recipient_count": count}
        for metric, value in describe([int(row["duration_ns"]) / 1_000_000 for row in selected]).items():
            result[f"keygen_ms_{metric}"] = value
        output.append(result)
    return output


def _e4_table(data: dict[str, list[dict[str, str]]]) -> list[dict[str, object]]:
    rows = {row["case_id"]: row for row in data["security_validation.csv"]}
    descriptions = {"valid_recipient": "valid package and matching private key", "wrong_private_key": "private key for another recipient",
        "wrong_recipient_id": "recipient ID absent from package", "changed_ciphertext": "one ciphertext byte changed",
        "changed_tag": "one GCM tag byte changed", "changed_filename": "authenticated filename changed",
        "changed_nonce": "one nonce byte changed", "changed_wrapped_key": "one RSA-wrapped-key byte changed",
        "changed_recipient_list": "recipient list shortened", "unsupported_version": "unsupported package version",
        "invalid_json": "malformed JSON bytes"}
    return [{"case_id": case, "tested_modification": descriptions[case], "expected_outcome": rows[case]["expected_status"],
             "observed_outcome": rows[case]["observed_status"], "plaintext_returned": rows[case]["plaintext_returned"],
             "pass": rows[case]["validation_pass"]} for case in E4_CASES]


def build_tables(data: dict[str, list[dict[str, str]]]) -> dict[str, list[dict[str, object]]]:
    e1_matrix, e1_minimums = _e1_tables(data)
    return {"e1_recovery_matrix": e1_matrix, "e1_minimum_success": e1_minimums,
            "e2_comparison": _e2_table(data), "e3_summary": _e3_table(data),
            "e3_keygen_summary": _e3_keygen_table(data), "e4_validation": _e4_table(data)}


def write_tables(output_dir: Path, tables: dict[str, list[dict[str, object]]]) -> None:
    for name, rows in tables.items():
        write_csv(output_dir / "tables" / f"{name}.csv", rows)
