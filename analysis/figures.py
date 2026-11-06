"""Report-sized Matplotlib figures generated from analysis tables."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

COLORS = {"textbook": "#0072B2", "oaep": "#D55E00", "decrypt": "#009E73",
          "crypto": "#0072B2", "serialization": "#E69F00"}


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(path.with_suffix(".svg"), bbox_inches="tight")
    svg_path = path.with_suffix(".svg")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)


def figure_1(matrix_csv: Path, output: Path) -> None:
    rows = _read(matrix_csv)
    columns = ["Alice", "Bob", "Charlie", "Alice+Bob", "Alice+Charlie", "Bob+Charlie", "Alice+Bob+Charlie"]
    values = np.array([[int(row[col]) for col in columns] for row in rows])
    fig, ax = plt.subplots(figsize=(7.1, 2.65))
    image = ax.imshow(values, cmap="Blues", vmin=0, vmax=20, aspect="auto")
    ax.set_xticks(range(len(columns)), columns, rotation=35, ha="right")
    ax.set_yticks(range(len(rows)), [row["sample_id"] for row in rows])
    ax.set_xlabel("Intercepted recipient subset")
    ax.set_ylabel("Message sample")
    ax.set_title("E1. Textbook RSA recovery across recipient subsets (n=20 blocks)")
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ax.text(j, i, f"{values[i, j]}/20", ha="center", va="center",
                    color="white" if values[i, j] >= 12 else "black", fontsize=8)
    fig.colorbar(image, ax=ax, label="Recovered blocks (out of 20)")
    _save(fig, output)


def figure_2(e2_csv: Path, output: Path) -> None:
    row = next(row for row in _read(e2_csv) if row["sample_id"] == "all")
    labels = ["Textbook\nrecovery", "OAEP\nrecovery", "OAEP legitimate\ndecryption", "OAEP ciphertext\ndiversity"]
    values = [int(row["textbook_recovery"]), int(row["oaep_recovery"]), int(row["legitimate_oaep_decryption"]), int(row["oaep_ciphertexts_distinct"])]
    colors = [COLORS["textbook"], COLORS["oaep"], COLORS["decrypt"], COLORS["oaep"]]
    fig, ax = plt.subplots(figsize=(6.6, 3.3))
    bars = ax.bar(labels, values, color=colors, edgecolor="black", linewidth=0.5)
    ax.set_ylim(0, 64)
    ax.set_ylabel("Paired comparisons (out of 60)")
    ax.set_title("E2. Controlled Textbook RSA and RSA-OAEP outcomes")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 1.5, f"{value}/60", ha="center", va="bottom", fontsize=9)
    _save(fig, output)


def figure_3(e3_csv: Path, output: Path) -> None:
    rows = _read(e3_csv)
    sizes = sorted({int(row["file_size_bytes"]) for row in rows})
    recipients = [1, 3, 5]
    fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.9), sharey=True)
    for ax, size in zip(axes, sizes):
        selected = [row for row in rows if int(row["file_size_bytes"]) == size]
        crypto = [float(next(row for row in selected if int(row["recipient_count"]) == r)["total_encryption_ms_mean"]) - float(next(row for row in selected if int(row["recipient_count"]) == r)["serialization_ms_mean"]) for r in recipients]
        serialization = [float(next(row for row in selected if int(row["recipient_count"]) == r)["serialization_ms_mean"]) for r in recipients]
        x = np.arange(len(recipients))
        ax.bar(x, crypto, color=COLORS["crypto"], edgecolor="black", linewidth=0.35, hatch="//", label="Encrypt + wrap")
        ax.bar(x, serialization, bottom=crypto, color=COLORS["serialization"], edgecolor="black", linewidth=0.35, hatch="..", label="JSON/Base64 serialize")
        ax.set_xticks(x, [str(r) for r in recipients])
        ax.set_xlabel("Recipients")
        ax.set_title("1 MiB" if size == 1048576 else f"{size / 1024:g} KiB")
        ax.grid(axis="y", alpha=0.25)
    axes[0].set_ylabel("Mean time (ms)")
    axes[-1].legend(frameon=True, framealpha=0.9, fontsize=7, loc="upper left")
    fig.suptitle("E3. Mean encryption workflow decomposition (n=20 per bar)", y=1.02)
    _save(fig, output)


def figure_4(e3_csv: Path, output: Path) -> None:
    rows = _read(e3_csv)
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for recipient_count in (1, 3, 5):
        selected = sorted((row for row in rows if int(row["recipient_count"]) == recipient_count), key=lambda row: int(row["file_size_bytes"]))
        x = np.array([int(row["file_size_bytes"]) / 1024 for row in selected])
        overhead = np.array([int(row["overhead_bytes"]) for row in selected])
        percent = np.array([float(row["overhead_percent"]) for row in selected])
        axes[0].plot(x, overhead / 1024, marker="o", label=f"{recipient_count} recipient(s)")
        axes[1].plot(x, percent, marker="o", label=f"{recipient_count} recipient(s)")
    for ax in axes:
        ax.set_xscale("log", base=2)
        ax.set_xticks([10, 100, 1024], ["10", "100", "1024"])
        ax.set_xlabel("Original file size (KiB)")
        ax.grid(alpha=0.25)
    axes[0].set_ylabel("Absolute overhead (KiB)")
    axes[1].set_ylabel("Overhead (%)")
    axes[1].legend(frameon=False, fontsize=7)
    fig.suptitle("E3. Serialized JSON/Base64 package overhead (n=20 per point)", y=1.02)
    _save(fig, output)


def generate_all(table_dir: Path, figure_dir: Path) -> None:
    figure_1(table_dir / "e1_recovery_matrix.csv", figure_dir / "figure_1_e1_recovery_matrix")
    figure_2(table_dir / "e2_comparison.csv", figure_dir / "figure_2_e2_scheme_comparison")
    figure_3(table_dir / "e3_summary.csv", figure_dir / "figure_3_e3_timing_decomposition")
    figure_4(table_dir / "e3_summary.csv", figure_dir / "figure_4_e3_package_overhead")
