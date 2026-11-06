"""Regression tests for TASK 09 analysis artifacts and integrity checks."""

from __future__ import annotations

from pathlib import Path
import shutil
import uuid

import pytest
import matplotlib.image as mpimg
import numpy as np

from analysis.models import predicted_package_size, theoretical_broadcast_condition
from analysis.run_analysis import run
from analysis.tables import EXPECTED_RUN_ID, build_tables, load_official_evidence
from broadcastguard.hybrid_sharing import encrypt_file_for_recipients, generate_demo_recipients, serialize_package


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence" / EXPECTED_RUN_ID


def _workspace_tmp(name: str) -> Path:
    path = ROOT / ".task09-test-tmp" / f"{name}-{uuid.uuid4().hex}"
    path.mkdir(parents=True)
    return path


def test_reads_official_raw_csv_and_matches_summary() -> None:
    manifest, data = load_official_evidence(EVIDENCE)
    assert manifest["run_id"] == EXPECTED_RUN_ID
    assert {name: len(rows) for name, rows in data.items()} == {
        "attack_conditions.csv": 560, "oaep_comparison.csv": 60,
        "hybrid_performance.csv": 180, "key_generation.csv": 60,
        "security_validation.csv": 11,
    }


def test_missing_or_malformed_evidence_is_rejected() -> None:
    target = _workspace_tmp("malformed") / "evidence"
    target.mkdir()
    try:
        for path in EVIDENCE.iterdir():
            target.joinpath(path.name).write_bytes(path.read_bytes())
        target.joinpath("attack_conditions.csv").write_text("broken\n", encoding="utf-8")
        with pytest.raises(ValueError, match="validation failed"):
            load_official_evidence(target)
    finally:
        shutil.rmtree(target.parent, ignore_errors=True)


def test_e1_matrix_and_e2_counts_are_derived_from_rows() -> None:
    _, data = load_official_evidence(EVIDENCE)
    tables = build_tables(data)
    minimums = {row["sample_id"]: row["minimum_successful_count"] for row in tables["e1_minimum_success"]}
    assert minimums == {"short_1": 1, "medium_96": 2, "long_180": 3, "leading_zero_96": 1}
    assert tables["e2_comparison"][-1] == {
        "sample_id": "all", "comparisons": 60, "textbook_recovery": 60,
        "oaep_recovery": 0, "legitimate_oaep_decryption": 60,
        "textbook_deterministic": 60, "oaep_ciphertexts_distinct": 60,
        "oaep_repeated_decryption": 60,
    }


def test_e3_decomposition_and_package_model() -> None:
    _, data = load_official_evidence(EVIDENCE)
    tables = build_tables(data)
    assert all(row["model_residual_bytes"] == 0 for row in tables["e3_summary"])
    assert len(tables["e3_keygen_summary"]) == 3
    assert all(row["ciphertext_base64_chars"] > row["file_size_bytes"] for row in tables["e3_summary"])
    assert all(row["model_metadata_increment_vs_1r"] == 0 for row in tables["e3_summary"] if row["recipient_count"] == 1)
    assert all(row["total_encryption_ms_mean"] == pytest.approx(
        row["encryption_ms_mean"] + row["serialization_ms_mean"]) for row in tables["e3_summary"])
    recipients = generate_demo_recipients(5)
    for count in (1, 3, 5):
        package = encrypt_file_for_recipients(b"x" * 1024, "synthetic.bin",
                                              tuple(item.public for item in recipients[:count]))
        assert len(serialize_package(package)) == predicted_package_size(1024, count)


def test_units_and_math_model() -> None:
    manifest, _ = load_official_evidence(EVIDENCE)
    assert manifest["timing_unit"] == "nanoseconds"
    assert theoretical_broadcast_condition(2, 2**2048)
    assert not theoretical_broadcast_condition(2**700, 2**2048)


def test_analysis_is_repeatable_and_figures_are_noninteractive() -> None:
    root = _workspace_tmp("repeatable")
    first, second = root / "first", root / "second"
    try:
        run(EVIDENCE, first)
        run(EVIDENCE, second)
        for name in ("e1_recovery_matrix.csv", "e1_minimum_success.csv", "e2_comparison.csv", "e3_summary.csv", "e4_validation.csv"):
            assert first.joinpath("tables", name).read_bytes() == second.joinpath("tables", name).read_bytes()
        for name in ("figure_1_e1_recovery_matrix", "figure_2_e2_scheme_comparison", "figure_3_e3_timing_decomposition", "figure_4_e3_package_overhead"):
            first_png = first.joinpath("figures", name + ".png")
            second_png = second.joinpath("figures", name + ".png")
            assert np.array_equal(mpimg.imread(first_png), mpimg.imread(second_png))
            for suffix in (".svg",):
                assert first.joinpath("figures", name + suffix).stat().st_size > 1000
                assert second.joinpath("figures", name + suffix).stat().st_size > 1000
    finally:
        shutil.rmtree(root, ignore_errors=True)
