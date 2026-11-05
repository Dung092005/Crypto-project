# BroadcastGuard review checkpoint

- **Project:** Educational RSA Broadcast Attack, OAEP defense, and secure
  hybrid file sharing. See `PROJECT_CONTEXT.md` for scope and threat model.
- **Repository:** `https://github.com/Dung092005/Crypto-project.git`.
  TASK 01–04 approved by reviewer. Verified TASK 04 baseline:
  `2ab75d50a2fe036aa3811809b7b9a608c46bbdc4` on
  `feat/step-04-oaep-defense`. TASK 05 review branch:
  `feat/step-05-hybrid-sharing`; verify final SHA with `git log -1`.
- **Completed:** TASK 01 package and arithmetic; TASK 02 public-only attack
  engine and evaluator; TASK 03 seven-subset analyzer and length sweep; TASK 04
  controlled RSA-OAEP Defense Lab. TASK 05 hybrid sharing is implemented on
  the review branch, pending review.
  Read `PROGRESS.md` for executed commands and outcomes.
- **Architecture:** `math_core.py` owns CRT and exact integer roots;
  `attack_lab.py` separates builder, Eve, and ground-truth evaluator;
  `conditions_analyzer.py` enumerates subsets and reuses public moduli across
  message lengths. `defense_lab.py` uses the same three RSA keys for both modes,
  calls the same Eve method, then evaluates OAEP separately and checks legitimate
  decryption. `hybrid_sharing.py` is separate from Textbook RSA modules and owns
  demo key generation, AES-GCM file encryption, RSA-OAEP key wrapping, package
  validation/serialization and recipient decryption. Main APIs:
  `generate_demo_recipients`, `encrypt_file_for_recipients`,
  `serialize_package`, `deserialize_package`, `decrypt_file_for_recipient`,
  `attempt_decrypt_file_for_recipient`, `summarize_package`. See
  `SECURE_SHARING_DESIGN.md` for data flows.
- **Cryptographic assumptions:** Same integer M, e=3, pairwise-coprime moduli,
  `M < n_i`, Textbook RSA deliberately insecure. Eve knows `(n,e,c)` only.
  `exact_root` does not imply recovered M. Evaluator-only bound is `M³ < N`.
  TASK 04 holds plaintext, recipients, keys, e=3, modulus size and Eve method
  fixed; changes only Textbook versus randomized OAEP-SHA256/MGF1-SHA256 with
  empty label. The 190-byte limit follows RFC 8017 §7.1. A failed CRT-and-root
  attempt is no proof of security. TASK 05 uses AES-256-GCM with a fresh 32-byte
  key and 12-byte nonce, RSA-2048/e=65537 OAEP-SHA256/MGF1-SHA256, and package
  format v1 canonical JSON header as AAD. Public keys must be authenticated
  beforehand. Fingerprints do not prove identity; no sender authentication or
  replay protection is provided.
- **Testing:** TASK 04 baseline: 162 passed. TASK 05 full suite: 203 passed;
  CLI examples 01–07, compileall, imports and diff check status are recorded
  in `PROGRESS.md`. Python 3.12.10 / cryptography 48.0.1; local Windows
  sandbox requires the temporary ACL workaround documented there. No benchmark
  claims are based on these engineering checks.
- **Technical debt:** In-memory demo private keys only, 5 MiB whole-file limit;
  no streaming, certificate/key distribution, sender signature, replay defense,
  network or persistence. Filename is display-only, never a trusted output path.
- **Next planned task:** TASK 06 Attack Lab Streamlit UI, only after TASK 05
  review and a separate request. The academic report has not begun.
- **Future decisions:** Keep attacker input public-only, report semantic statuses
  separately from UI colors, preserve byte length for leading zeros, and record
  actual seeds/versions/hardware/run artifacts when experiments begin.
  Historic Codex proxy `127.0.0.1:9` issue did not mean the GitHub branch was
  absent; TASK 03 was verified on GitHub. Update this checkpoint after each
  reviewed milestone. Start the academic
  report only after the software work is complete and explicitly requested.
