# Run notes · official-20261106T083221Z-3bbf57cc

- Mode: **official**. Quick mode is pipeline smoke data, not official evidence.
- Git commit: `46c455819e4588736d4777c252d844fa03e7caf3`; source dirty: `False`.
- Repetitions: 20; warmup: 2; schedule seed: 20261106 (run order only).
- Validation: **PASS**.
- E1/E2 share each e=3 key set within a repetition; the four E1 samples and three E2 samples are paired, not independent observations.
- E3 reuses prepared e=65537 keys for regular encryption; key generation has its own timing CSV. Total encryption = encrypt+wrap+serialize, excluding key generation and recipient decryption.
- E3 times are wall-clock intervals from perf_counter_ns and can vary with OS scheduling, load and this machine. No outliers were removed.
- E4 is correctness validation; rejection does not identify the cause as tampering and does not authenticate a sender.
- OAEP non-recovery in these trials is not a formal security proof. RSA mathematical conditions are established, not a new discovery.
- Cryptographic key generation is not seeded; exact ciphertext and key values cannot be reproduced from the schedule seed.
