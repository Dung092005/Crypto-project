# R02 manuscript notes

## Draft and layout

- `main.tex` builds `BroadcastGuard_Report_Draft.pdf`: **4 A4 pages**, including all seven authors, two figures, one table and five references. The page count was read from the compiled PDF, not estimated from source.
- Sections: Abstract; Introduction and motivation; Background and attack model; System design and experimental method; Results and analysis; Limitations and discussion; Conclusion; References.
- Figure 1 embeds audited E1 recovery matrix `docs/analysis/figures/figure_1_e1_recovery_matrix.png`. Figure 2 embeds audited E3 timing decomposition `docs/analysis/figures/figure_3_e3_timing_decomposition.png`. Table 1 reports E2's paired outcomes. E4 is summarized in text. The source figure number 3 becomes Figure 2 in the shorter manuscript.
- E2's standalone figure and E3's standalone package-overhead figure were omitted to preserve space for the exact attack condition, paired-design explanation and package-size equation. Their audited originals remain available in `docs/analysis/figures/`.
- The paper uses the verified shared bibliography at `research/broadcastguard/REFERENCES.bib`. R02 adds linked DOI notes because the selected IEEEtran bibliography style does not print the `doi` field itself.

## Provenance and construction

- Official run: `official-20261106T083221Z-3bbf57cc`, with source commit `46c455819e4588736d4777c252d844fa03e7caf3`. The audited evidence revision is `18327fc7be234ca5328f7a6289a463c8c9e41c6e`. Raw data live at `docs/evidence/official-20261106T083221Z-3bbf57cc/`.
- E1: 560 rows, 20 independent key-set blocks, four messages, seven subsets; four minimum counts 1, 2, 3, 1. E2: 60 paired rows nested within 20 key-set blocks, with 60 textbook recoveries, zero OAEP recoveries by the tested method and 60 successful legitimate decryptions. E3: 180 timed workflow rows plus 60 separately timed key-generation rows. E4: 11 correctness cases. Every official record has `validation_pass=True`.
- For 1 MiB and one recipient, means recomputed from `hybrid_performance.csv` are 0.479550 ms encrypt+wrap, 7.232030 ms serialization and 7.711580 ms total. Serialization's share is 93.78143% of that mean. The 1 MiB relative-overhead endpoints are 33.40% and 33.58% after rounding. See `R02_CLAIM_AUDIT.md` for field-level traceability.
- The English manuscript follows `research/broadcastguard/R01_RESEARCH_BLUEPRINT.md` and citation scope in `R01_LITERATURE_VERIFICATION.md`. The fixed-message CRT inequality is derived in the paper; Håstad's broader result is cited only for historical context.

## Build

Compiler used: Tectonic **0.17.0**, XeTeX engine, on Windows. The source currently requests installed `Times New Roman` for Vietnamese-name coverage. It therefore needs that font, or a deliberate Unicode-capable font substitution, on another machine. The compiler was downloaded outside the repository and is not a tracked dependency.

From the repository root, with Tectonic available:

```powershell
tectonic -k --keep-logs -o report report/main.tex
Copy-Item report/main.pdf report/BroadcastGuard_Report_Draft.pdf
```

The R02 build used the same command with an external temporary output directory (`..\r02-build`) and copied only the final PDF into `report/`.

Evidence read-back command:

```powershell
python -m experiments.run_experiments --validate-only docs/evidence/official-20261106T083221Z-3bbf57cc
```

The compiled PDF was rendered and all four pages visually inspected. See `R02_LAYOUT_QA.md`.

## Open items for R03

- Confirm whether the instructor has a mandatory template or a stricter interpretation of the provisional five-page limit. R02 intentionally uses standard 11 pt A4 typography and does not reserve a full cover page.
- Confirm the exact spelling/IDs of the seven authors and whether a contribution statement is required. No contribution roles, supervisor, department or emails were invented.
- Check prose and claim scope independently in R03, especially the distinction between observed OAEP non-recovery and a formal security guarantee.
- The five references were verified in R01. Håstad and Bellare–Rogaway full texts remained inaccessible; only accessible abstracts/metadata support the narrowly scoped claims.
