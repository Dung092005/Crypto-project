# BroadcastGuard final engineering audit — TASK 10

**Conclusion: PASS for the agreed engineering and evidence scope, pending reviewer approval of this branch.** This document is a quality-control record, not the academic report. Baseline reviewed: `b5284233bea900d31a2a2794adef3eee548c3165` (TASK 09). Its parent history was verified against remote `main`; `main` was fast-forwarded to that exact SHA and its remote head verified before creating `feat/step-10-final-audit`. The TASK 10 branch is intentionally not merged into main.

## Cryptographic audit

| Module | Checked assumption and outcome |
| --- | --- |
| `math_core.py` | CRT validates nonempty canonical residues and pairwise-coprime moduli. Integer nth root uses integer binary search, never floating point. `exact` says only that the reconstructed integer is a perfect power. |
| `attack_lab.py` | The builder uses RSA-2048/e=3 and checks `M<n_i`; Textbook RSA is marked intentionally insecure. `attack_observations()` accepts public observations only. `evaluate_experiment()` separately knows plaintext and preserves leading-zero bytes with the original byte length. An exact but wrong root has its own status. |
| `conditions_analyzer.py` | Enumerates all seven nonempty subsets; compares the evaluator's `M³<N_S` prediction with observed recovery and reports the minimum successful count. The two 96-byte samples show why byte length alone is insufficient. |
| `defense_lab.py` | Both schemes share plaintext, recipients, three RSA-2048/e=3 keys and Eve's CRT/root procedure. OAEP uses SHA-256, MGF1-SHA256 and empty label; intended recipients decrypt independently. Repeated OAEP ciphertext diversity is an observation, not a security proof. |
| `hybrid_sharing.py` | Uses RSA-2048/e=65537 OAEP to wrap a freshly generated 32-byte AES key per recipient, and AES-256-GCM with a fresh 12-byte nonce to encrypt file bytes once. The canonical JSON header, including recipient/wrapped-key metadata, is AAD. Version/structure checks and controlled decryption failures return no partial plaintext. Encrypted packages contain no private key or plaintext field; the module does not invoke Textbook RSA. |

Security boundaries remain: recipient public keys are assumed authenticated before use; fingerprints alone do not prove identity. There is no sender authentication, PKI, replay protection, key revocation or general malicious-endpoint defense. Failure of the tested CRT-and-root method on OAEP cannot establish universal security. These limitations are recorded rather than implemented away in TASK 10.

## Evidence and numerical consistency

Official evidence is unchanged at `docs/evidence/official-20261106T083221Z-3bbf57cc/`, with source SHA `46c455819e4588736d4777c252d844fa03e7caf3`. The read-back validator returned **VALID**. Independent tests read the raw CSVs and checked 871 recorded rows: E1 560, E2 60, E3 180, separate E3 keygen 60, E4 11. All `validation_pass` fields are true and error types empty. E1's seven-subset matrix and minimum counts, E2 pairing/counts, E3 means/medians/sample SD/Q1/Q3/IQR/min/max and time decomposition, keygen statistics, actual package sizes/overhead, and E4 expected/observed statuses were recomputed from raw rows against the six committed analysis tables. The six regenerated CSV tables matched the approved TASK 09 tables **byte-for-byte**. No measurements were removed, rerun or altered.

The 1 MiB/one-recipient raw means are 0.479550 ms encrypt+wrap, 7.232030 ms JSON/Base64 serialization and 7.711580 ms total, so serialization is 93.78% of this measured mean. The total excludes RSA key generation and is not an AES-only time. E3 decryption times one valid recipient, not all recipients sequentially. The fixed-format size model has zero residual because it accounts for the current JSON/Base64 serialization skeleton with fixed filename/IDs; this is not independent cryptographic validation or a general-purpose compression claim. E1 verifies established CRT mathematics, E2 comprises 60 paired comparisons within 20 independent key-set blocks, and E4 is 11 deterministic correctness cases rather than a statistical sample of attacks. Claims in `RESEARCH_FINDINGS.md`, `CLAIM_EVIDENCE_MATRIX.md`, `ANALYSIS_METHODS.md`, `EXPERIMENT_EVIDENCE.md` and `REPORT_FIGURE_INDEX.md` were checked against these records and qualifications; no unsupported universal security or cross-machine performance claim was found.

## Figure corrections and visual review

- **Figure 1:** replaced opaque sample IDs with explicit byte patterns, especially the two distinct 96-byte inputs.
- **Figure 2:** expanded vertical spacing and Y limit; all `60/60` labels now clear the title and `0/60` remains visible.
- **Figure 3:** independently labeled, zero-based Y scales per file-size panel; legend moved above all data areas. Title/caption disclose the independent scales. Values still come from the unchanged E3 table.
- **Figure 4:** checked absolute KiB versus relative percent axes, log-scaled file-size ticks and legend; no data/presentation change was necessary beyond regenerated vector text and current Matplotlib rendering.

All four regenerated **300-DPI PNGs were visually inspected** from disk; each also has an SVG with searchable vector text. Figure rendering differences from TASK 09 can result from updated Matplotlib and the approved layout changes; numerical tables did not change. The four PNG/SVG pairs total well under 1 MiB and are suitable for GitHub review. Figure 3 bar heights must be compared only within a panel; numerical Y axes enable cross-panel comparison.

## Verification performed

Fresh Python 3.12.10 virtual environment outside the repo: `..\task10-venv`, installed with `pip install -e ".[dev,analysis]"`. Verified package versions: Streamlit 1.67.0, `cryptography` 49.0.0, Matplotlib 3.11.2, NumPy 2.5.4, pytest 9.2.0. The **original** official run used Python 3.12.10 and `cryptography` 48.0.1; no new official experiment was run. `pip check` returned **No broken requirements found**.

```powershell
..\task10-venv\Scripts\python.exe -m experiments.run_experiments --validate-only docs/evidence/official-20261106T083221Z-3bbf57cc
..\task10-venv\Scripts\python.exe -m analysis.run_analysis --input docs/evidence/official-20261106T083221Z-3bbf57cc --output ..\task10-analysis
..\task10-venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp ..\task10-pytest-final
```

Results: **VALID**, **Analysis PASS**, **235 passed in 47.48s**. The 17 existing Attack/Defense AppTests are included in the full suite. Seven CLI examples `01`–`07` ran with exit code 0. The six tables in temporary analysis output matched committed tables by SHA-256. `compileall`, package imports and `pip check` passed. Local Streamlit startup returned health **HTTP 200 / `ok`** on port 8510; the test server was then stopped. `git diff --check` and the tracked-file secret scan passed before commit. `app.py`, Streamlit pages and all official raw evidence files were left unchanged.

## Remaining limits and next gate

The public deployment is reported working by the user; this audit does not independently verify its live URL or redeploy it. Timing comes from one Windows machine and cannot be generalized to all hardware or cloud. Figure suitability for an instructor's exact page width remains subject to the report template. The instructor's rubric/template, page limit, citation style, author details and submission format are still needed. Academic citations for established broadcast-attack theory, RSAES-OAEP, AES-GCM and hybrid encryption must be verified during report writing. No academic report was drafted here.

After reviewer approval, TASK 10 can be integrated into main by a **fast-forward only** after verifying a clean working tree and that current `origin/main` is an ancestor of the reviewed feature SHA. Do not force-push or deploy automatically.
