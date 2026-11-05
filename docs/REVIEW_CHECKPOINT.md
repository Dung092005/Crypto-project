# BroadcastGuard review checkpoint

- **Project:** Educational RSA Broadcast Attack, OAEP defense, and later secure
  file sharing. See `PROJECT_CONTEXT.md` for scope and threat model.
- **Repository:** `https://github.com/Dung092005/Crypto-project.git`.
  Verified TASK 02 baseline: `74e2a6c43a3997dd8fdfd90605a3079379227f2e`
  on `main` and `feat/step-02-attack-engine`. TASK 03 review branch:
  `feat/step-03-conditions-analyzer`; verify current SHA with `git log -1`.
- **Completed:** TASK 01 package and arithmetic; TASK 02 public-only attack
  engine and evaluator; TASK 03 seven-subset analyzer, controlled length sweep,
  CLI demo and tests. Read `PROGRESS.md` for executed commands and outcomes.
- **Architecture:** `math_core.py` owns CRT and exact integer roots;
  `attack_lab.py` separates builder, Eve, and ground-truth evaluator;
  `conditions_analyzer.py` enumerates subsets and reuses public moduli across
  message lengths. Examples are CLI only; tests use deterministic small integers
  plus real RSA-2048 integration.
- **Cryptographic assumptions:** Same integer M, e=3, pairwise-coprime moduli,
  `M < n_i`, Textbook RSA deliberately insecure. Eve knows `(n,e,c)` only.
  `exact_root` does not imply recovered M. Evaluator-only bound is `M³ < N`.
  A failed CRT-and-root attempt is no proof of security. Future file-sharing
  design assumes authenticated public keys and uses standard crypto primitives
  provided by the `cryptography` package.
- **Testing:** TASK 03 suite: 145 passed on Python 3.12.10 / cryptography 48.0.1;
  CLI examples 01–05, import and compile checks passed. Local Windows sandbox
  requires the temporary ACL workaround documented in `PROGRESS.md`.
- **Next planned task:** TASK 04 only after reviewer approval. No Streamlit,
  AES-GCM, performance results, or academic report were implemented in TASK 03.
- **Future decisions:** Keep attacker input public-only, report semantic statuses
  separately from UI colors, preserve byte length for leading zeros, and record
  actual seeds/versions/hardware/run artifacts when experiments begin.
  Update this checkpoint after each reviewed milestone. Start the academic
  report only after the software work is complete and explicitly requested.
