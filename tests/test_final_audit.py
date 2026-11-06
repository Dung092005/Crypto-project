"""Independent read-back checks for the frozen TASK 08 evidence and TASK 09 tables."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean, median, stdev
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/evidence/official-20261106T083221Z-3bbf57cc"
TABLES = ROOT / "docs/analysis/tables"
FIGURES = ROOT / "docs/analysis/figures"


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    low = int(position)
    return ordered[low] + (ordered[min(low + 1, len(ordered) - 1)] - ordered[low]) * (position - low)


def _check_stats(rows: list[dict[str, str]], field: str, table: dict[str, str], prefix: str) -> None:
    values = [int(row[field]) / 1_000_000 for row in rows]
    q1, q3 = _percentile(values, 0.25), _percentile(values, 0.75)
    computed = {"n": len(values), "mean": fmean(values), "median": median(values),
                "sd": stdev(values), "q1": q1, "q3": q3, "iqr": q3 - q1,
                "min": min(values), "max": max(values)}
    for metric, value in computed.items():
        assert math.isclose(float(table[f"{prefix}_{metric}"]), value, rel_tol=1e-12, abs_tol=1e-12)


def test_official_manifest_and_all_records() -> None:
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_id"] == "official-20261106T083221Z-3bbf57cc"
    assert manifest["git_commit"] == "46c455819e4588736d4777c252d844fa03e7caf3"
    assert manifest["mode"] == "official" and manifest["repetitions"] == 20
    assert manifest["timing_unit"] == "nanoseconds"
    expected = {"attack_conditions.csv": 560, "oaep_comparison.csv": 60,
                "hybrid_performance.csv": 180, "key_generation.csv": 60,
                "security_validation.csv": 11}
    for name, count in expected.items():
        rows = _csv(DATA / name)
        assert len(rows) == count
        assert all(row["validation_pass"] == "True" and row["error_type"] == "" for row in rows)


def test_e1_matrix_minimums_and_e2_pairing() -> None:
    e1, e2 = _csv(DATA / "attack_conditions.csv"), _csv(DATA / "oaep_comparison.csv")
    matrix = {row["sample_id"]: row for row in _csv(TABLES / "e1_recovery_matrix.csv")}
    minimums = {row["sample_id"]: row for row in _csv(TABLES / "e1_minimum_success.csv")}
    for sample, table in matrix.items():
        selected = [row for row in e1 if row["sample_id"] == sample]
        for subset in ("Alice", "Bob", "Charlie", "Alice+Bob", "Alice+Charlie",
                       "Bob+Charlie", "Alice+Bob+Charlie"):
            assert int(table[subset]) == sum(row["subset"] == subset and row["recovered_original"] == "True"
                                             for row in selected)
        minimum = min(int(row["recipient_count"]) for row in selected
                      if row["recovered_original"] == "True")
        assert int(minimums[sample]["minimum_successful_count"]) == minimum
        assert all(row["bound_holds"] == row["recovered_original"] for row in selected)
    e1_keys = defaultdict(set)
    for row in e1:
        e1_keys[row["repetition"]].add(row["keyset_id"])
    assert len(e1_keys) == 20 and all(len(keys) == 1 for keys in e1_keys.values())
    assert all(row["keyset_id"] in e1_keys[row["repetition"]] for row in e2)
    comparison = {row["sample_id"]: row for row in _csv(TABLES / "e2_comparison.csv")}
    for sample, table in comparison.items():
        selected = e2 if sample == "all" else [row for row in e2 if row["sample_id"] == sample]
        assert int(table["comparisons"]) == len(selected)
        for output, raw in (("textbook_recovery", "textbook_recovered"),
                            ("oaep_recovery", "oaep_recovered"),
                            ("legitimate_oaep_decryption", "legitimate_all_decrypt"),
                            ("textbook_deterministic", "textbook_deterministic"),
                            ("oaep_ciphertexts_distinct", "oaep_ciphertexts_distinct")):
            assert int(table[output]) == sum(row[raw] == "True" for row in selected)


def test_e3_statistics_decomposition_keygen_and_size() -> None:
    raw = _csv(DATA / "hybrid_performance.csv")
    for table in _csv(TABLES / "e3_summary.csv"):
        rows = [row for row in raw if row["case_id"] == table["case_id"]]
        assert len(rows) == 20
        for field, prefix in (("encryption_ns", "encryption_ms"),
                              ("serialization_ns", "serialization_ms"),
                              ("total_encryption_ns", "total_encryption_ms"),
                              ("decryption_ns", "decryption_ms")):
            _check_stats(rows, field, table, prefix)
        assert all(int(row["total_encryption_ns"]) ==
                   int(row["encryption_ns"]) + int(row["serialization_ns"]) for row in rows)
        assert {int(row["package_size_bytes"]) for row in rows} == {int(table["package_size_bytes"])}
        assert int(table["overhead_bytes"]) == int(table["package_size_bytes"]) - int(table["file_size_bytes"])
        assert int(table["model_residual_bytes"]) == 0
    keygen = _csv(DATA / "key_generation.csv")
    for table in _csv(TABLES / "e3_keygen_summary.csv"):
        rows = [row for row in keygen if row["recipient_count"] == table["recipient_count"]]
        assert len(rows) == 20
        _check_stats(rows, "duration_ns", table, "keygen_ms")


def test_e4_table_and_figure_labels() -> None:
    e4 = {row["case_id"]: row for row in _csv(DATA / "security_validation.csv")}
    for table in _csv(TABLES / "e4_validation.csv"):
        raw = e4[table["case_id"]]
        assert table["expected_outcome"] == raw["expected_status"]
        assert table["observed_outcome"] == raw["observed_status"]
        assert table["plaintext_returned"] == raw["plaintext_returned"]
        assert table["pass"] == "True"
    svg_ns = "{http://www.w3.org/2000/svg}"
    for name, labels in {
        "figure_1_e1_recovery_matrix.svg": ("96 bytes: B", "95 zeros + 0x02"),
        "figure_2_e2_scheme_comparison.svg": ("0/60", "60/60"),
        "figure_3_e3_timing_decomposition.svg": ("independent Y scales", "JSON/Base64 serialize"),
        "figure_4_e3_package_overhead.svg": ("Absolute overhead", "Overhead (%)"),
    }.items():
        root = ElementTree.parse(FIGURES / name).getroot()
        text = " ".join("".join(node.itertext()) for node in root.iter(svg_ns + "text"))
        assert all(label in text for label in labels)
