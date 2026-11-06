# TASK 09 analysis methods

The analysis reads only the committed official run official-20261106T083221Z-3bbf57cc. It first executes the existing read-back validator, checks the run ID, source SHA, official mode, 20 repetitions, exact CSV schemas, nanosecond timing unit and expected row counts, then recomputes summary.json directly from raw CSV files. Any failure stops the CLI.

Statistical units:

- E1: one independently generated RSA key-set block per repetition; four messages and seven subsets are repeated within each block.
- E2: paired observations within the same 20 key-set blocks; 60 rows are not 60 independent key sets.
- E3: 20 timed repetitions for each of nine recipient-count/file-size configurations on one machine with prepared keys; key generation is a separate CSV.
- E4: eleven deterministic correctness cases, not a sample of attacks.

Timing summaries use recorded nanoseconds converted to milliseconds and report n, mean, median, sample standard deviation, Q1, Q3, IQR, minimum and maximum. No outliers are removed and no p-values or causal claims are computed.

For plaintext size L, AES-GCM contributes a 16-byte tag, so encrypted content has L+16 bytes. The outer JSON stores this content in Base64, contributing 4*ceil((L+16)/3) ASCII characters. The remaining term is generated from the current compact sorted JSON representation, including algorithm fields, filename, original size, 12-byte nonce in Base64, recipient IDs, 64-character SHA-256 fingerprints and one 256-byte RSA-2048 ciphertext in Base64 per recipient. The model retains the controlled E3 filename synthetic.bin and recipient IDs Alice through Emma; arbitrary filenames and IDs change the metadata term.

Figures use Matplotlib's non-interactive Agg backend and are saved as 300-DPI PNG and SVG. No benchmark runs during import or figure generation.

Source SHA: 46c455819e4588736d4777c252d844fa03e7caf3
Raw evidence: docs/evidence/official-20261106T083221Z-3bbf57cc/
