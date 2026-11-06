# TASK 08 experiment protocol

This is a predeclared engineering verification protocol, not the academic report. Run the offline CLI from the repository root. The algorithms and package format remain those reviewed in TASK 01–07. Sources for the cryptographic specifications: [RFC 8017](https://www.rfc-editor.org/rfc/rfc8017.html), [NIST SP 800-38D](https://csrc.nist.gov/pubs/sp/800/38/d/final), and the [`cryptography` AESGCM API](https://cryptography.io/en/stable/hazmat/primitives/aead/). Python's [`perf_counter_ns`](https://docs.python.org/3/library/time.html#time.perf_counter_ns) supplies the monotonic high-resolution clock.

## Design and interpretation

| ID | Question and hypothesis | Independent variables | Measured outcomes | Controls and procedure |
| --- | --- | --- | --- | --- |
| E1 | How do the integer plaintext and intercepted subset determine CRT-and-root recovery? Hypothesis: with valid textbook RSA, recovery matches `M**3 < product(moduli)` for every subset. | Four messages: `B` × 1, 96, 180 bytes, and 95 zero bytes followed by `0x02`; seven subsets. | Bound, exact root, recovered original, minimum successful count, modulus-product bits. | 20 independently generated RSA-2048/e=3 key sets; within one repetition the same three public moduli serve all four messages. Analyze all seven subsets. |
| E2 | How does randomized OAEP encoding change the tested attack outcome? Hypothesis: textbook recovers M with three ciphertexts; OAEP does not in these trials, while all intended recipients decrypt. | Encryption scheme; messages of 1, 96, 180 bytes. | Recovery, exact root, legitimate decryption, ciphertext diversity. | Reuse the **same e=3 keys as E1** within each trial, same plaintext and three recipients. Call the reviewed defense API; verify public moduli match. OAEP is SHA-256/MGF1-SHA256. |
| E3 | How do payload size and recipient count affect hybrid workflow time and package overhead? Hypothesis: package overhead grows with recipient count; payload size strongly affects AES work and relative overhead. | 10 KiB, 100 KiB, 1 MiB; 1, 3, 5 recipients. | Raw nanosecond keygen, encryption+wrap, serialization, decryption, total encryption; actual serialized size and overhead. | Prepare one RSA-2048/e=65537 set of five recipients for regular timings. Use the same synthetic bytes per size and first 1/3/5 keys, but generate fresh AES key/nonce for every encryption. Verify decrypted bytes. Measure RSA keygen separately. |
| E4 | Do malformed or mismatched packages fail closed? Hypothesis: the one valid case returns exact bytes; ten invalid or mismatched cases return no plaintext. | Valid recipient, wrong key/ID, changed ciphertext/tag/filename/nonce/wrapped key/recipient list, unsupported version, invalid JSON. | Observed status, rejection, plaintext returned, pass/fail. | One synthetic 1 KiB package and one controlled mutation per case. Correctness checks, not timing samples. |

E1's 96-byte leading-zero sample has integer value 2; the 96-byte `B` sample has a much larger integer. The byte count alone does not determine the RSA bound. An exact cube root is recorded separately from recovered original. The experimenter knows M for evaluation; Eve's backend uses public `(n,e,c)` observations only. OAEP non-recovery in these trials is neither a universal claim about all ciphertexts nor a formal security proof.

## Timing and replication

Official mode requires at least 20 measured repetitions. E1/E2 have 20 independent key-set blocks. E2 samples within a block are paired observations, not 60 independent key sets. E3 runs 20 measured repetitions **per each of nine** recipient-count × file-size configurations and 20 separate key-generation repetitions for each of three recipient counts. Each E3 configuration receives two unmeasured warmups by default. The shuffled schedule seed records workload order only; it never seeds cryptographic randomness. E4 is deterministic correctness testing and runs once per case.

`encryption_ns` spans `encrypt_file_for_recipients`: fresh AES key/nonce, RSA-OAEP wrapping, canonical AAD, and AES-GCM encryption. `serialization_ns` spans `serialize_package`. `total_encryption_ns = encryption_ns + serialization_ns`, excludes RSA keygen and decryption. `decryption_ns` spans `decrypt_file_for_recipient` for the first valid recipient. `key_generation.csv` times `generate_demo_recipients` separately. The schedule and preallocated payloads/public-key selections are outside timed intervals. Every recorded E3 repetition validates decrypted bytes. Package overhead is `len(serialize_package(package)) - len(payload)`; percentages divide by the nonempty file size. No outliers are removed.

The summary uses the **recorded raw nanoseconds** to compute mean, median, sample standard deviation, min/max and linearly interpolated p25/p75, expressed in milliseconds. Wall-clock intervals include OS and interpreter variability. A single Windows laptop is not representative of other machines or Streamlit Cloud. No inference about relative cryptographic strength follows from these timings.

## Data contract and provenance

Every CSV row includes `run_id`, `experiment_id`, `case_id`, `repetition`, `validation_pass`, and `error_type`. E1/E2 include a hash of public moduli to check the within-trial pairing; E3 includes the prepared public-key-set hash. These are experimental identifiers, not identity credentials. The CSVs contain no private keys, AES keys, plaintext bytes, or full 2048-bit integers. E1 stores sample ID, message length/bit length, subset and mathematical outcomes. E2 stores both scheme statuses, key equality, decryption and randomization outcomes. E3 stores raw timing and actual serialized size. E4 stores expected/observed status and whether plaintext was returned. The manifest records run ID, UTC time, source SHA/dirty flag, Python/cryptography/OS/CPU metadata, repetitions, warmups and schedule seed. Hardware fields are `unavailable` if undetected.

The validator reads CSVs back from disk, checks complete case/repetition grids, mathematical and security invariants, same-key pairing, positive timing and package overhead, and recomputes `summary.json` from the raw rows. Failure rows remain in CSV with exception type and `validation_pass=False`; such a run is incomplete. Quick mode is pipeline smoke data and **must not be cited as official evidence**. Raw output lives in ignored `results/`; a validated sanitized copy may be committed under `docs/evidence/`.

## Reproduction

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m experiments.run_experiments --mode quick --output results/quick-check
.\.venv\Scripts\python.exe -m experiments.run_experiments --mode official --repetitions 20 --warmup 2 --output results/official-check
.\.venv\Scripts\python.exe -m experiments.run_experiments --validate-only results/official-check
```

Choose a **new empty output directory** each time. Official mode requires a clean, committed Git tree so its manifest names an exact source commit. Crypto outputs cannot be reproduced bit for bit because keys, OAEP encoding and AES material are randomly generated; configuration, code, case grid and statistical procedure are reproducible.
