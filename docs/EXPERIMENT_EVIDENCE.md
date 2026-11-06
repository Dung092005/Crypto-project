# TASK 08 evidence register

This is a verified technical evidence index, **not** the academic report. Interpret it with the predeclared [protocol](EXPERIMENT_PROTOCOL.md). The [raw official dataset](evidence/official-20261106T083221Z-3bbf57cc/) contains the manifest, five CSV files (including key-generation), summary and run notes.

| Provenance field | Recorded value |
| --- | --- |
| Official run ID | `official-20261106T083221Z-3bbf57cc` |
| Source Git commit | `46c455819e4588736d4777c252d844fa03e7caf3` (clean tree at launch) |
| Time / system | 2026-11-06 UTC; Windows 11; Python 3.12.10; `cryptography` 48.0.1 |
| Processor / logical CPUs | Intel64 Family 6 Model 191 Stepping 2, GenuineIntel / 20 |
| Official settings | 20 measured repetitions, 2 E3 warmups per configuration, run-order seed 20261106 |
| Validation | Read-back validator **PASS**; 0 failed rows across all five CSVs; no forbidden secret/path markers found |

The source SHA is the experiment-runner commit. Subsequent documentation and data commits do not change the executed algorithms. The run order seed does not seed cryptographic keys or OAEP/AES randomness.

## Result checks

| Group | Rows and observed result |
| --- | --- |
| E1 | 560 rows = 20 key sets × 4 messages × 7 subsets. Minimum successful count was **1** for 1-byte `B` and 96-byte leading-zero/`0x02`, **2** for 96-byte `B`, and **3** for 180-byte `B`, in all 20 key-set blocks. All 560 mathematical bound predictions matched actual recovery. Recovered subset rows were 140, 140, 80, and 20 respectively. |
| E2 | 60 paired comparisons = 20 key sets × 3 messages. Textbook RSA recovered original in **60/60**; the tested CRT-and-root method recovered OAEP original in **0/60**; all three intended recipients decrypted correctly in **60/60** comparisons. Textbook repeated ciphertext was identical, OAEP repeated ciphertexts differed and decrypted in each comparison. |
| E3 | 180 workflow rows = 20 repetitions × 3 sizes × 3 recipient counts; **180/180** decrypted bytes matched. Separate key-generation CSV has 60 rows = 20 × 3 recipient counts. |
| E4 | 11/11 controlled cases matched expected status: one accepted, ten rejected, and no plaintext returned for the rejected cases. Wrong key/ID and modified GCM/OAEP material yielded controlled decryption failure; unsupported version/invalid JSON yielded invalid-package status. |

### E3 selected descriptive results

Values below are means from actual raw `perf_counter_ns` intervals. `total` means encrypt+wrap+serialize, with pre-generated RSA keys. Full mean, median, sample standard deviation, min/max and quartiles for every operation appear in [summary.json](evidence/official-20261106T083221Z-3bbf57cc/summary.json); every raw interval remains in [hybrid_performance.csv](evidence/official-20261106T083221Z-3bbf57cc/hybrid_performance.csv).

| Recipients | File | Mean total encryption (ms) | Mean recipient decryption (ms) | Serialized package overhead |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 10 KiB | 0.205 | 0.530 | 4,125 B / 40.28% |
| 3 | 10 KiB | 0.283 | 0.508 | 5,059 B / 49.40% |
| 5 | 10 KiB | 0.375 | 0.606 | 5,992 B / 58.52% |
| 1 | 100 KiB | 0.870 | 0.563 | 34,846 B / 34.03% |
| 3 | 100 KiB | 0.934 | 0.576 | 35,780 B / 34.94% |
| 5 | 100 KiB | 0.985 | 0.528 | 36,713 B / 35.85% |
| 1 | 1 MiB | 7.712 | 1.046 | 350,239 B / 33.40% |
| 3 | 1 MiB | 7.795 | 0.992 | 351,173 B / 33.49% |
| 5 | 1 MiB | 7.594 | 0.871 | 352,106 B / 33.58% |

Mean key-generation times for independently generated 1/3/5-recipient sets were 31.130 / 117.645 / 163.276 ms respectively. These are separate from total encryption. Do not infer that the small non-monotone 1 MiB means show a speed advantage at five recipients: run-to-run scheduling noise and this single machine limit interpretation. The overhead uses the **serialized JSON+Base64 package**, including metadata and wrapped-key entries.

## Suitable use in the later report

- E1: subset recovery matrix, minimum successful count by integer message value, bound-prediction agreement.
- E2: paired Textbook/OAEP outcomes and legitimate decrypt/randomization checks.
- E3: descriptive timing and package-overhead tables/plots with sample counts, spread and hardware context. Do not use unit-test runtimes as benchmarks.
- E4: acceptance/rejection correctness table. Do not treat rejection as proof that a cause was tampering.

These data verify known RSA arithmetic and observed behavior of **one tested attack method**. They do not establish a new attack, formal OAEP security, sender authentication, replay protection, or universal performance across computers/cloud deployments. The report needs the user's rubric and any separately verified prior-work citations. Quick-mode smoke data in ignored `results/` must not be cited as official evidence.

Revalidate the committed copy from the repository root:

```powershell
.\.venv\Scripts\python.exe -m experiments.run_experiments --validate-only docs/evidence/official-20261106T083221Z-3bbf57cc
```
