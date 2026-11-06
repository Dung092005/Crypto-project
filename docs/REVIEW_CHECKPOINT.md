# BroadcastGuard review checkpoint

- **Project:** Educational RSA Broadcast Attack, OAEP defense, and secure
  hybrid file sharing. See `PROJECT_CONTEXT.md` for scope and threat model.
- **Repository:** `https://github.com/Dung092005/Crypto-project.git`.
  TASK 01–06 approved by reviewer. Verified TASK 06 baseline:
  `0dc6ad3a8f6bf9cd5abb79ab7ee681d3a2af268d` on
  `feat/step-06-attack-ui`. `main` was subsequently fast-forwarded through
  docs commit `806ba9e972b10dd482c879766e963a80991c7440`.
  TASK 07 branch: `feat/step-07-defense-ui` (base is exact TASK 06 SHA).
  PR #1 was merged into `main` at
  `48ab2e9d540bd2beb9759f13fd8149598bf1dc5b` after resolving the
  three documentation conflicts with commit `806ba9e`.
- **Completed:** TASK 01 package and arithmetic; TASK 02 public-only attack
  engine and evaluator; TASK 03 seven-subset analyzer and length sweep; TASK 04
  controlled RSA-OAEP Defense Lab; TASK 05 hybrid sharing; TASK 06 interactive
  Attack Lab UI. TASK 07 adds Defense Lab UI and multipage routing; integrated
  through PR #1 after the reviewer-approved TASK 07 branch.
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
  `app.py` routes with `st.Page`/`st.navigation` to Attack and Defense pages;
  `ui/attack_page.py` retains TASK 06 behavior. `ui/defense_page.py` calls
  reviewed `run_defense_comparison()`; `ui/defense_presenter.py` formats
  summaries. Lab results use distinct session keys and no global crypto cache.
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
- **Testing:** TASK 06 baseline: 212 tests including 9 Attack AppTests. TASK 07:
  220 passed including 8 new Defense AppTests; CLI examples 01–07, compileall,
  imports and local Streamlit health 200 passed. See `PROGRESS.md` for commands.
  Python 3.12 / Streamlit 1.60.0 / cryptography 48.0.1. The Windows sandbox
  needs an in-workspace pytest temporary directory. No benchmark claim.
  Existing unrelated research packages make `pip check` fail in this shared
  venv; the project tests and local runtime passed. Browser visual QA is pending.
- **Technical debt:** In-memory demo private keys only, 5 MiB whole-file limit;
  no streaming, certificate/key distribution, sender signature, replay defense,
  network or persistence. Filename is display-only, never a trusted output path.
- **TASK 08 research milestone:** TASK 01–07 are reviewer-approved; TASK 07 is
  merged into `main`. Verified TASK 08 base is
  `626c68e881a459d63a82f7f844ab558abed81752`. The user confirms the
  public Streamlit deployment works; this agent has not independently verified
  its URL. Branch `feat/step-08-research-experiments` adds offline E1 attack
  conditions, E2 paired OAEP defense, E3 hybrid timing/overhead and E4 package
  failure validation. The CLI, data schema and interpretation rules are in
  `EXPERIMENT_PROTOCOL.md`; the run and measured results are indexed in
  `EXPERIMENT_EVIDENCE.md`. Official run
  `official-20261106T083221Z-3bbf57cc` used clean source commit `46c4558`,
  20 repetitions, 2 E3 warmups, 871 total CSV rows and passed read-back
  validation with zero failed cases. Curated data are in `docs/evidence/`;
  raw local `results/` is ignored. Full pytest: 225 passed. No Streamlit
  changes are part of TASK 08.
- **Next planned tasks:** TASK 09 data analysis and visualization; TASK 10
  final validation. Each needs separate request/review. The academic report is
  a separate high-priority deliverable after software completion and requires
  the user's rubric. It has not begun.
- **Cloud readiness:** root `app.py`, pinned `requirements.txt`, dark theme,
  session isolation, `DEPLOYMENT.md`. `main` contains TASK 07 via PR #1 merge
  commit `48ab2e9d540bd2beb9759f13fd8149598bf1dc5b`; verify the SHA
  before selecting `main`. Historical TASK 07 note: that agent did not deploy;
  the user later confirmed a working public Streamlit deployment. Browser visual QA/screenshot was unavailable; AppTest and health
  check are separate evidence.
- **Repository presentation:** root README now gives quick start, two UI demos,
  Secure Sharing CLI status and security limits. Root `LICENSE` uses MIT with
  `BroadcastGuard contributors` as copyright holder; `pyproject.toml` declares
  SPDX `MIT` and packages the license file. No application behavior changed.
- **Future decisions:** Keep attacker input public-only, report semantic statuses
  separately from UI colors, preserve byte length for leading zeros, and record
  actual seeds/versions/hardware/run artifacts when experiments begin.
  Historic Codex proxy `127.0.0.1:9` issue did not mean the GitHub branch was
  absent; TASK 03 was verified on GitHub. Update this checkpoint after each
  reviewed milestone. Start the academic
  report only after the software work is complete and explicitly requested.
## TASK 09 scientific analysis checkpoint

- TASK 08 approved va integrated: main fast-forward tu 626c68e881a459d63a82f7f844ab558abed81752 den 46eff82c6f8bc91c577dac05c027fe2f115bb9da. TASK 09 branch: feat/step-09-scientific-analysis. Khong force-push, reset hay resolve conflict.
- Official evidence: run official-20261106T083221Z-3bbf57cc; source SHA 46c455819e4588736d4777c252d844fa03e7caf3; dataset tai docs/evidence/official-20261106T083221Z-3bbf57cc/; validator tra ve VALID truoc khi phan tich.
- Analysis command: python -m analysis.run_analysis --input docs/evidence/official-20261106T083221Z-3bbf57cc --output docs/analysis.
- Artifacts: analysis/models.py, analysis/tables.py, analysis/figures.py, analysis/run_analysis.py, tests/test_analysis.py va docs/analysis/ gom methods, findings, claim-evidence matrix, figure index, nam CSV tables va bon cap PNG/SVG.
- Evidence interpretation: E1 la verification cua exact bound; E2 paired trong 20 key blocks va 0/60 OAEP non-recovery la empirical; E3 tach encrypt+wrap, serialization, total va key generation; E3 package model khop ca 9 controlled sizes; E4 la 11 deterministic correctness cases.
- Next: TASK 10 se final validation va research-quality audit. Academic report la buoc sau va chua duoc tao.
