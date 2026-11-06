# TASK 09 research findings

Analysis input: official-20261106T083221Z-3bbf57cc; source SHA 46c455819e4588736d4777c252d844fa03e7caf3; mode official.

This is a technical analysis package, not the final academic report.

## E1 — mathematical broadcast recovery

For fixed integer plaintext M and exponent e=3, a subset S of pairwise-coprime moduli has N_S = product(n_i). CRT reconstructs X = M^3 mod N_S. When M^3 < N_S, X is the exact integer M^3 and an exact cube root returns M. Under the experiment's valid-input assumptions, this numerical inequality is the prediction tested by the CRT-and-root procedure.

The official 20-block matrix shows minimum successful recipient counts of short_1=1, medium_96=2, long_180=3, leading_zero_96=1. All 560 E1 rows matched the bound prediction. The 96-byte medium_96 message is 96 bytes of B, whereas leading_zero_96 is 95 zero bytes followed by 0x02, so its integer value is 2 despite the same byte length. Byte length is an intuition aid; the exact integer inequality determines the result.

This verifies established RSA/CRT mathematics in a controlled implementation. It is not a new cryptanalytic algorithm.

## E2 — textbook RSA versus OAEP

Across 60 paired comparisons drawn from 20 key-set blocks and three messages, Textbook RSA recovery was 60/60; the tested CRT-and-root method recovered the OAEP plaintext in 0/60; legitimate OAEP decryption was 60/60; repeated Textbook ciphertexts were deterministic in 60/60 checks and OAEP ciphertexts were distinct in 60/60 checks.

OAEP changes the RSA representative with randomized encoding, so the attack's shared-M assumption does not apply to observed encoded values. The 0/60 result is empirical for this tested method and sample, not a formal security guarantee. The 60 comparisons are clustered within 20 key-set blocks.

## E3 — hybrid workflow timing and package overhead

The timing unit is a wall-clock interval from perf_counter_ns; keys were prepared for routine workflow timing and key generation was measured separately. total_encryption_ns is encrypt+wrap plus JSON/Base64 serialization, not AES-only time. The 1 MiB results recomputed from raw CSV are: 1 recipient(s): total 7.711580 ms, encrypt+wrap 0.479550 ms, serialization 7.232030 ms; 3 recipient(s): total 7.795145 ms, encrypt+wrap 0.592930 ms, serialization 7.202215 ms; 5 recipient(s): total 7.594015 ms, encrypt+wrap 0.583145 ms, serialization 7.010870 ms. For one recipient, serialization accounts for 93.78% of the observed total mean.

At 1 MiB, serialization is the dominant observed component for all recipient counts in this run. Small non-monotone differences in total means across recipient counts should be read with medians, IQRs and standard deviations; they do not establish a performance advantage. Decryption measures the first valid recipient only, not sequential decryption of every recipient.

The structural package model uses 4*ceil((L+16)/3) Base64 characters for ciphertext-plus-tag and a JSON/header term that depends on filename, recipient IDs, fingerprints and one Base64 RSA-2048 wrapped key per recipient. For the fixed E3 format, the model matched every observed package size with zero residual. This is exact structural accounting for the controlled serializer format, not a fitted performance model. Relative overhead approaches roughly one-third for large files because Base64 expands encrypted content by about 4/3; JSON metadata and wrapped keys become smaller relative contributions as L grows.

## E4 — security correctness

The 11 deterministic cases all matched their expected outcome: one valid recipient returned plaintext and ten malformed, mismatched or modified inputs returned no plaintext. Structural errors were classified as invalid_package; wrong keys/IDs and failed RSA-OAEP or AES-GCM authentication were classified as decryption_failed. These cases demonstrate fail-closed behavior for the tested mutations. They do not establish sender authentication, replay protection, public-key identity verification, or protection against every possible attack.

## Critical review

Strong result: every E1 mathematical prediction matched the recorded recovery outcome, and every E3 decryption correctness check passed. Instructive result: equal byte lengths can produce radically different RSA integer values, as shown by the two 96-byte samples. Measurement limitation: E3 uses one Windows machine, 20 repetitions per configuration and wall-clock timings. Threat to validity: timing results may reflect OS scheduling and interpreter behavior, while E2 observations are clustered by key-set block. Future work: repeat descriptive timing and overhead analysis across independent hardware and a larger workload range, preserving the separation of cryptographic, serialization and key-generation costs.

## Reproducibility

Regenerate with python -m analysis.run_analysis --input docs/evidence/official-20261106T083221Z-3bbf57cc --output docs/analysis. The command validates the committed official dataset before reading rows and does not run cryptographic benchmarks.
