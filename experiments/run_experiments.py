"""Run E1–E4 offline; never execute benchmarks on import or app startup."""

import argparse
import json
from pathlib import Path

from experiments.attack_and_defense import run_attack_and_defense
from experiments.evidence import SCHEMAS, calculate_summary, read_csv, validate_output, write_csv
from experiments.hybrid import run_hybrid_performance, run_security_validation
from experiments.methodology import RunConfig, manifest


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def execute(config: RunConfig, output: Path, info: dict | None = None) -> tuple[dict, bool, list[str]]:
    """Produce every raw record, then validate the read-back dataset."""
    info = info or manifest(config)
    if config.mode == "official" and info["source_dirty"]:
        raise ValueError("Official runs require a clean, committed Git working tree.")
    directory = output.resolve()
    if directory.exists() and any(directory.iterdir()):
        raise ValueError("Output directory already contains data; choose a new path.")
    directory.mkdir(parents=True, exist_ok=True)
    run_id = str(info["run_id"])
    _write_json(directory / "manifest.json", info)

    print("E1/E2: controlled RSA key sets and message samples...", flush=True)
    e1, e2 = run_attack_and_defense(config, run_id)
    print("E3: separate key generation and hybrid workflow timings...", flush=True)
    e3, keygen = run_hybrid_performance(config, run_id)
    print("E4: controlled acceptance and rejection cases...", flush=True)
    e4 = run_security_validation(run_id)
    generated = {
        "attack_conditions.csv": e1,
        "oaep_comparison.csv": e2,
        "hybrid_performance.csv": e3,
        "key_generation.csv": keygen,
        "security_validation.csv": e4,
    }
    for name, rows in generated.items():
        write_csv(directory / name, SCHEMAS[name], rows)
    recorded = {name: read_csv(directory / name, fields) for name, fields in SCHEMAS.items()}
    summary = calculate_summary(info, recorded)
    _write_json(directory / "summary.json", summary)
    valid, problems = validate_output(directory)
    notes = [
        f"# Run notes · {run_id}", "",
        f"- Mode: **{config.mode}**. Quick mode is pipeline smoke data, not official evidence.",
        f"- Git commit: `{info['git_commit']}`; source dirty: `{info['source_dirty']}`.",
        f"- Repetitions: {config.repetitions}; warmup: {config.warmup}; "
        f"schedule seed: {config.schedule_seed} (run order only).",
        f"- Validation: **{'PASS' if valid else 'FAIL'}**.",
        "- E1/E2 share each e=3 key set within a repetition; the four E1 samples "
        "and three E2 samples are paired, not independent observations.",
        "- E3 reuses prepared e=65537 keys for regular encryption; key generation "
        "has its own timing CSV. Total encryption = encrypt+wrap+serialize, "
        "excluding key generation and recipient decryption.",
        "- E3 times are wall-clock intervals from perf_counter_ns and can vary "
        "with OS scheduling, load and this machine. No outliers were removed.",
        "- E4 is correctness validation; rejection does not identify the cause "
        "as tampering and does not authenticate a sender.",
        "- OAEP non-recovery in these trials is not a formal security proof. "
        "RSA mathematical conditions are established, not a new discovery.",
        "- Cryptographic key generation is not seeded; exact ciphertext and key "
        "values cannot be reproduced from the schedule seed.",
    ]
    if problems:
        notes.extend(("", "## Validation problems", ""))
        notes.extend(f"- {problem}" for problem in problems)
    (directory / "RUN_NOTES.md").write_text("\n".join(notes) + "\n", encoding="utf-8")
    return summary, valid, problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect BroadcastGuard E1–E4 evidence offline.")
    parser.add_argument("--mode", choices=("quick", "official"), default="quick")
    parser.add_argument("--repetitions", type=int, default=None,
                        help="Measured repetitions per configuration (official >=20).")
    parser.add_argument("--warmup", type=int, default=None,
                        help="Unmeasured warmup repetitions per E3 configuration.")
    parser.add_argument("--schedule-seed", type=int, default=20261106,
                        help="Reproducible timing order only; never seeds crypto randomness.")
    parser.add_argument("--output", type=Path, default=None,
                        help="New output directory (default: results/<unique run ID> ).")
    parser.add_argument("--validate-only", type=Path, default=None,
                        help="Recheck an existing output directory without running crypto.")
    args = parser.parse_args(argv)
    if args.validate_only is not None:
        valid, problems = validate_output(args.validate_only)
        print("VALID" if valid else "INVALID", *(problems or []), sep="\n")
        return 0 if valid else 2
    try:
        config = RunConfig(args.mode,
                           args.repetitions if args.repetitions is not None else
                           (20 if args.mode == "official" else 2),
                           args.warmup if args.warmup is not None else
                           (2 if args.mode == "official" else 1),
                           args.schedule_seed)
        info = manifest(config)
        output = args.output or Path("results") / str(info["run_id"])
        summary, valid, problems = execute(config, output, info)
    except (ValueError, OSError) as error:
        parser.error(str(error))
    print("Run ID:", summary["run_id"])
    print("Output:", output)
    print("Rows:", summary["row_counts"])
    print("Validation:", "PASS" if valid else "FAIL")
    if problems:
        print("Problems:", *problems, sep="\n- ")
    return 0 if valid else 2


if __name__ == "__main__":
    raise SystemExit(main())
