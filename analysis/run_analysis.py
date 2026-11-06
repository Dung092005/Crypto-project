"""CLI for TASK 09 scientific analysis; never runs cryptographic benchmarks."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .figures import generate_all
from .tables import build_tables, load_official_evidence, write_tables


def _write_methods(output: Path, manifest: dict[str, object]) -> None:
    text = f"""# TASK 09 analysis methods

The analysis reads only the committed official run {manifest['run_id']}. It first executes the existing read-back validator, checks the run ID, source SHA, official mode, 20 repetitions, exact CSV schemas, nanosecond timing unit and expected row counts, then recomputes summary.json directly from raw CSV files. Any failure stops the CLI.

Statistical units:

- E1: one independently generated RSA key-set block per repetition; four messages and seven subsets are repeated within each block.
- E2: paired observations within the same 20 key-set blocks; 60 rows are not 60 independent key sets.
- E3: 20 timed repetitions for each of nine recipient-count/file-size configurations on one machine with prepared keys; key generation is a separate CSV.
- E4: eleven deterministic correctness cases, not a sample of attacks.

Timing summaries use recorded nanoseconds converted to milliseconds and report n, mean, median, sample standard deviation, Q1, Q3, IQR, minimum and maximum. No outliers are removed and no p-values or causal claims are computed.

For plaintext size L, AES-GCM contributes a 16-byte tag, so encrypted content has L+16 bytes. The outer JSON stores this content in Base64, contributing 4*ceil((L+16)/3) ASCII characters. The remaining term is generated from the current compact sorted JSON representation, including algorithm fields, filename, original size, 12-byte nonce in Base64, recipient IDs, 64-character SHA-256 fingerprints and one 256-byte RSA-2048 ciphertext in Base64 per recipient. The model retains the controlled E3 filename synthetic.bin and recipient IDs Alice through Emma; arbitrary filenames and IDs change the metadata term.

Figures use Matplotlib's non-interactive Agg backend and are saved as 300-DPI PNG and SVG. No benchmark runs during import or figure generation.

Source SHA: {manifest['git_commit']}
Raw evidence: docs/evidence/{manifest['run_id']}/
"""
    (output / "ANALYSIS_METHODS.md").write_text(text, encoding="utf-8")


def _write_findings(output: Path, manifest: dict[str, object], tables: dict[str, list[dict[str, object]]]) -> None:
    e1 = tables["e1_minimum_success"]
    e2 = tables["e2_comparison"][-1]
    e3 = tables["e3_summary"]
    one_mib = [row for row in e3 if row["file_size_bytes"] == 1048576]
    timing = "; ".join(f"{row['recipient_count']} recipient(s): total {float(row['total_encryption_ms_mean']):.6f} ms, encrypt+wrap {float(row['encryption_ms_mean']):.6f} ms, serialization {float(row['serialization_ms_mean']):.6f} ms" for row in one_mib)
    one_mib_one = next(row for row in one_mib if row["recipient_count"] == 1)
    serialization_share = 100 * float(one_mib_one["serialization_ms_mean"]) / float(one_mib_one["total_encryption_ms_mean"])
    text = f"""# TASK 09 research findings

Analysis input: {manifest['run_id']}; source SHA {manifest['git_commit']}; mode {manifest['mode']}.

This is a technical analysis package, not the final academic report.

## E1 — mathematical broadcast recovery

For fixed integer plaintext M and exponent e=3, a subset S of pairwise-coprime moduli has N_S = product(n_i). CRT reconstructs X = M^3 mod N_S. When M^3 < N_S, X is the exact integer M^3 and an exact cube root returns M. Under the experiment's valid-input assumptions, this numerical inequality is the prediction tested by the CRT-and-root procedure.

The official 20-block matrix shows minimum successful recipient counts of {', '.join(f"{row['sample_id']}={row['minimum_successful_count']}" for row in e1)}. All 560 E1 rows matched the bound prediction. The 96-byte medium_96 message is 96 bytes of B, whereas leading_zero_96 is 95 zero bytes followed by 0x02, so its integer value is 2 despite the same byte length. Byte length is an intuition aid; the exact integer inequality determines the result.

This verifies established RSA/CRT mathematics in a controlled implementation. It is not a new cryptanalytic algorithm.

## E2 — textbook RSA versus OAEP

Across {e2['comparisons']} paired comparisons drawn from 20 key-set blocks and three messages, Textbook RSA recovery was {e2['textbook_recovery']}/{e2['comparisons']}; the tested CRT-and-root method recovered the OAEP plaintext in {e2['oaep_recovery']}/{e2['comparisons']}; legitimate OAEP decryption was {e2['legitimate_oaep_decryption']}/{e2['comparisons']}; repeated Textbook ciphertexts were deterministic in {e2['textbook_deterministic']}/{e2['comparisons']} checks and OAEP ciphertexts were distinct in {e2['oaep_ciphertexts_distinct']}/{e2['comparisons']} checks.

OAEP changes the RSA representative with randomized encoding, so the attack's shared-M assumption does not apply to observed encoded values. The 0/60 result is empirical for this tested method and sample, not a formal security guarantee. The 60 comparisons are clustered within 20 key-set blocks.

## E3 — hybrid workflow timing and package overhead

The timing unit is a wall-clock interval from perf_counter_ns; keys were prepared for routine workflow timing and key generation was measured separately. total_encryption_ns is encrypt+wrap plus JSON/Base64 serialization, not AES-only time. The 1 MiB results recomputed from raw CSV are: {timing}. For one recipient, serialization accounts for {serialization_share:.2f}% of the observed total mean.

At 1 MiB, serialization is the dominant observed component for all recipient counts in this run. Small non-monotone differences in total means across recipient counts should be read with medians, IQRs and standard deviations; they do not establish a performance advantage. Decryption measures the first valid recipient only, not sequential decryption of every recipient.

The structural package model uses 4*ceil((L+16)/3) Base64 characters for ciphertext-plus-tag and a JSON/header term that depends on filename, recipient IDs, fingerprints and one Base64 RSA-2048 wrapped key per recipient. For the fixed E3 format, the model matched every observed package size with zero residual. This is exact structural accounting for the controlled serializer format, not a fitted performance model. Relative overhead approaches roughly one-third for large files because Base64 expands encrypted content by about 4/3; JSON metadata and wrapped keys become smaller relative contributions as L grows.

## E4 — security correctness

The 11 deterministic cases all matched their expected outcome: one valid recipient returned plaintext and ten malformed, mismatched or modified inputs returned no plaintext. Structural errors were classified as invalid_package; wrong keys/IDs and failed RSA-OAEP or AES-GCM authentication were classified as decryption_failed. These cases demonstrate fail-closed behavior for the tested mutations. They do not establish sender authentication, replay protection, public-key identity verification, or protection against every possible attack.

## Critical review

Strong result: every E1 mathematical prediction matched the recorded recovery outcome, and every E3 decryption correctness check passed. Instructive result: equal byte lengths can produce radically different RSA integer values, as shown by the two 96-byte samples. Measurement limitation: E3 uses one Windows machine, 20 repetitions per configuration and wall-clock timings. Threat to validity: timing results may reflect OS scheduling and interpreter behavior, while E2 observations are clustered by key-set block. Future work: repeat descriptive timing and overhead analysis across independent hardware and a larger workload range, preserving the separation of cryptographic, serialization and key-generation costs.

## Reproducibility

Regenerate with python -m analysis.run_analysis --input docs/evidence/official-20261106T083221Z-3bbf57cc --output docs/analysis. The command validates the committed official dataset before reading rows and does not run cryptographic benchmarks.
"""
    (output / "RESEARCH_FINDINGS.md").write_text(text, encoding="utf-8")


def _write_claim_matrix(output: Path) -> None:
    text = """# Claim–evidence matrix

| ID | Exact claim | Evidence file(s) | Derivation/measurement | Conditions/assumptions | Limitation/qualification | Future report section |
| --- | --- | --- | --- | --- | --- | --- |
| C1 | For the tested valid textbook RSA inputs, CRT-and-root recovery agrees with M^3 < N_S. | official attack_conditions.csv, summary.json | 560 raw rows; prediction_matches_recovery=True for all rows. | e=3, pairwise-coprime RSA-2048 moduli, same integer M, valid RSA message range. | Establishes the tested mathematical condition, not a new attack or a claim about invalid inputs. | Attack mathematics and results |
| C2 | The minimum successful recipient count differed across the four message samples: 1, 2, or 3. | attack_conditions.csv, tables/e1_minimum_success.csv | Minimum computed from all seven subset rows in each of 20 blocks. | Exact integer values from four declared samples. | Do not generalize that all 96-byte messages need two ciphertexts. | Attack analysis |
| C3 | In the controlled comparison, Textbook RSA recovered 60/60 while the tested OAEP CRT-and-root method recovered 0/60 and legitimate OAEP decryption succeeded 60/60. | oaep_comparison.csv, tables/e2_comparison.csv | Direct counts from 60 paired rows. | Same three keypairs within each block; three messages; OAEP randomized. | 0/60 is empirical, not a formal OAEP security proof; rows cluster within 20 key blocks. | Defense comparison |
| C4 | For fixed E3 package format, the structural size model matches every observed serialized package size. | hybrid_performance.csv, tables/e3_summary.csv, analysis/models.py | Canonical JSON skeleton with length-preserving fields; residual checked per configuration. | Fixed filename and recipient IDs; RSA-2048 wrapped key and SHA-256 fingerprint lengths. | Arbitrary filenames/IDs change metadata; structural accounting, not a fitted model. | Storage overhead |
| C5 | At 1 MiB, JSON/Base64 serialization dominates the observed total encryption workflow. | hybrid_performance.csv, tables/e3_summary.csv, Figure 3 | Compare raw timing components and distributions for n=20 per configuration. | Prepared RSA keys; total excludes key generation. | One Windows machine and wall-clock timing; do not call total time AES-only. | Performance |
| C6 | The 11 E4 correctness cases matched expected statuses and returned no plaintext for rejected cases. | security_validation.csv, tables/e4_validation.csv | Deterministic expected/observed status comparison. | One controlled package and one mutation per case. | Not a population percentage; no sender authentication, replay protection or universal attack guarantee. | Security validation |
"""
    (output / "CLAIM_EVIDENCE_MATRIX.md").write_text(text, encoding="utf-8")


def _write_figure_index(output: Path) -> None:
    text = """# Report figure index

| Figure | Files | Role | Caption guidance |
| --- | --- | --- | --- |
| Figure 1 | figures/figure_1_e1_recovery_matrix.png/.svg | Essential | E1 recovery counts out of 20 key-set blocks for all four messages and seven subsets. |
| Figure 2 | figures/figure_2_e2_scheme_comparison.png/.svg | Essential | E2 paired outcomes across 60 comparisons; distinguish attack recovery from legitimate decryption and ciphertext diversity. |
| Figure 3 | figures/figure_3_e3_timing_decomposition.png/.svg | Essential | E3 mean encrypt+wrap versus JSON/Base64 serialization, n=20 per bar; total excludes key generation. |
| Figure 4 | figures/figure_4_e3_package_overhead.png/.svg | Essential for storage argument | Absolute and relative serialized package overhead for nine E3 configurations, n=20 per point. |

Figures 1–4 are suitable for a short report. E4 is better as a compact correctness table than as a chart. Figure 3 should be paired with the median/IQR table; Figure 4 should be paired with the exact structural model and residual column.
"""
    (output / "REPORT_FIGURE_INDEX.md").write_text(text, encoding="utf-8")


def run(input_dir: Path, output_dir: Path) -> None:
    manifest, data = load_official_evidence(input_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "analysis_manifest.json").write_text(json.dumps({"input": str(input_dir), "run_id": manifest["run_id"], "source_sha": manifest["git_commit"]}, indent=2) + "\n", encoding="utf-8")
    tables = build_tables(data)
    write_tables(output_dir, tables)
    _write_methods(output_dir, manifest)
    _write_findings(output_dir, manifest, tables)
    _write_claim_matrix(output_dir)
    _write_figure_index(output_dir)
    generate_all(output_dir / "tables", output_dir / "figures")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate BroadcastGuard TASK 09 analysis from validated evidence.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    run(args.input, args.output)
    print(f"Analysis PASS: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
