"""End-to-end checks for recorded experiment evidence and its validator."""

import csv
import json
from pathlib import Path
from uuid import uuid4

import pytest

from experiments.evidence import validate_output
from experiments.methodology import ATTACK_SAMPLES, RunConfig
from experiments.run_experiments import execute
from experiments.statistics import describe_ns


@pytest.fixture(scope="module")
def quick_dataset():
    path = Path("results") / f"pytest-quick-{uuid4().hex}"
    summary, valid, problems = execute(RunConfig("quick", 1, 1, 42), path)
    assert valid, problems
    return path, summary


def test_config_and_statistics():
    with pytest.raises(ValueError, match="at least 20"):
        RunConfig("official", 19, 1, 1)
    with pytest.raises(ValueError):
        RunConfig("quick", 0, 1, 1)
    with pytest.raises(ValueError):
        describe_ns([0])
    stats = describe_ns([1_000_000, 2_000_000, 3_000_000, 4_000_000])
    assert stats == {
        "count": 4, "mean_ms": 2.5, "median_ms": 2.5,
        "std_ms": pytest.approx(1.2909944487358056), "min_ms": 1.0,
        "max_ms": 4.0, "p25_ms": 1.75, "p75_ms": 3.25,
    }


def test_leading_zero_sample_controls_integer_not_length():
    samples = dict(ATTACK_SAMPLES)
    assert len(samples["leading_zero_96"]) == len(samples["medium_96"]) == 96
    assert int.from_bytes(samples["leading_zero_96"], "big") == 2
    assert int.from_bytes(samples["medium_96"], "big").bit_length() > 700


def test_quick_run_is_complete_and_paired(quick_dataset):
    path, summary = quick_dataset
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["mode"] == "quick"
    assert summary["row_counts"] == {
        "attack_conditions.csv": 28, "oaep_comparison.csv": 3,
        "hybrid_performance.csv": 9, "key_generation.csv": 3,
        "security_validation.csv": 11,
    }
    assert summary["complete"]
    assert validate_output(path) == (True, [])
    with (path / "attack_conditions.csv").open(newline="", encoding="utf-8") as stream:
        attack = list(csv.DictReader(stream))
    with (path / "oaep_comparison.csv").open(newline="", encoding="utf-8") as stream:
        defense = list(csv.DictReader(stream))
    assert len({row["keyset_id"] for row in attack + defense}) == 1
    assert {row["subset"] for row in attack if row["sample_id"] == "medium_96"} == {
        "Alice", "Bob", "Charlie", "Alice+Bob", "Alice+Charlie", "Bob+Charlie",
        "Alice+Bob+Charlie",
    }
    assert all(row["legitimate_all_decrypt"] == "True" for row in defense)
    assert all(row["oaep_recovered"] == "False" for row in defense)
    assert all(summary["E4"][case]["passed"] for case in summary["E4"])


def test_validator_catches_missing_case_and_summary_drift(quick_dataset):
    source, _ = quick_dataset
    target = Path("results") / f"pytest-mutated-{uuid4().hex}"
    target.mkdir()
    for path in source.iterdir():
        if path.is_file():
            (target / path.name).write_bytes(path.read_bytes())
    csv_path = target / "security_validation.csv"
    with csv_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    rows.pop()
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    valid, problems = validate_output(target)
    assert not valid
    assert any("missing" in problem for problem in problems)
    assert any("summary.json" in problem for problem in problems)


def test_validator_catches_negative_timing(quick_dataset):
    source, _ = quick_dataset
    target = Path("results") / f"pytest-negative-{uuid4().hex}"
    target.mkdir()
    for path in source.iterdir():
        if path.is_file():
            (target / path.name).write_bytes(path.read_bytes())
    csv_path = target / "hybrid_performance.csv"
    text = csv_path.read_text(encoding="utf-8")
    with csv_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    rows[0]["encryption_ns"] = "-1"
    with csv_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    assert text != csv_path.read_text(encoding="utf-8")
    valid, problems = validate_output(target)
    assert not valid
    assert any("positive" in problem for problem in problems)
