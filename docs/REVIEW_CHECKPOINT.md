# BroadcastGuard review checkpoint

- **Project:** Educational RSA Broadcast Attack, OAEP defense, and later secure
  file sharing. See `PROJECT_CONTEXT.md` for scope and threat model.
- **Repository:** `https://github.com/Dung092005/Crypto-project.git`.
  TASK 01–03 reviewed. Verified TASK 03 baseline:
  `3ef78b63877017f0e92a1f71f1eab1ef2dab0569` on
  `feat/step-03-conditions-analyzer`. TASK 04 branch:
  `feat/step-04-oaep-defense`; verify final SHA with `git log -1`.
- **Completed:** TASK 01 package and arithmetic; TASK 02 public-only attack
  engine and evaluator; TASK 03 seven-subset analyzer and length sweep. TASK 04
  RSA-OAEP Defense Lab is implemented on the review branch, pending review.
  Read `PROGRESS.md` for executed commands and outcomes.
- **Architecture:** `math_core.py` owns CRT and exact integer roots;
  `attack_lab.py` separates builder, Eve, and ground-truth evaluator;
  `conditions_analyzer.py` enumerates subsets and reuses public moduli across
  message lengths. `defense_lab.py` uses the same three RSA keys for both modes,
  calls the same Eve method, then evaluates OAEP separately and checks legitimate
  decryption. Main API: `run_defense_comparison`, `DefenseComparison.summary_rows`,
  `recipient_rows`, `detail_rows`. Examples remain CLI only.
- **Cryptographic assumptions:** Same integer M, e=3, pairwise-coprime moduli,
  `M < n_i`, Textbook RSA deliberately insecure. Eve knows `(n,e,c)` only.
  `exact_root` does not imply recovered M. Evaluator-only bound is `M³ < N`.
  TASK 04 holds plaintext, recipients, keys, e=3, modulus size and Eve method
  fixed; changes only Textbook versus randomized OAEP-SHA256/MGF1-SHA256 with
  empty label. The 190-byte limit follows RFC 8017 §7.1. A failed CRT-and-root
  attempt is no proof of security. Future file-sharing
  design assumes authenticated public keys and uses standard crypto primitives
  provided by the `cryptography` package.
- **Testing:** TASK 03 baseline: 145 passed. TASK 04 full suite: 162 passed;
  CLI examples 01–06, compileall, imports and diff check passed on Python
  3.12.10 / cryptography 48.0.1. Executed commands are in `PROGRESS.md`; local Windows
  sandbox requires the temporary ACL workaround documented there. No benchmark
  claims are based on these engineering checks.
- **Next planned task:** TASK 05 Secure Hybrid Encryption only after TASK 04
  review and a separate request. No Streamlit, AES-GCM, or academic report in TASK 04.
- **Future decisions:** Keep attacker input public-only, report semantic statuses
  separately from UI colors, preserve byte length for leading zeros, and record
  actual seeds/versions/hardware/run artifacts when experiments begin.
  Historic Codex proxy `127.0.0.1:9` issue did not mean the GitHub branch was
  absent; TASK 03 was verified on GitHub. Update this checkpoint after each
  reviewed milestone. Start the academic
  report only after the software work is complete and explicitly requested.
