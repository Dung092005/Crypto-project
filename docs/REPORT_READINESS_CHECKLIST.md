# Report readiness checklist

This is a planning and verification checklist, **not** the academic report. Obtain the instructor's template, page limit, required citation format and marking details before drafting.

## WHAT: problem and scope

- [ ] Define Textbook RSA broadcast with the same integer plaintext `M`, `e=3`, distinct pairwise-coprime moduli, and public observations `(n,e,c)`.
- [ ] State the threat model: Eve sees ciphertexts and public keys, not private keys. Textbook RSA is intentionally insecure and is confined to the research labs.
- [ ] Identify Secure Sharing as AES-256-GCM plus RSA-OAEP, with recipient public keys assumed authenticated beforehand. Do not claim sender authentication, replay protection, certificate management or identity verification.

## WHY: evidence-backed claims

| Claim | Traceable evidence and suitable report material | Qualification |
| --- | --- | --- |
| The exact CRT-and-root recovery condition matched the controlled E1 trials. | `docs/evidence/.../attack_conditions.csv`; `docs/analysis/tables/e1_recovery_matrix.csv`; Figure 1; Claim C1. | Known RSA mathematics, not a new attack algorithm. |
| Two messages of 96 bytes can require different interception counts. | E1 `medium_96` versus `leading_zero_96`; `e1_minimum_success.csv`; Figure 1; Claim C2. | Numeric `M`, not byte count alone, determines the bound. |
| The tested CRT-and-root method recovered 60/60 Textbook samples and 0/60 OAEP samples; legitimate OAEP decryptions succeeded 60/60. | `oaep_comparison.csv`; `e2_comparison.csv`; Figure 2; Claim C3. | Three messages are paired within each of 20 independent key-set blocks. No formal OAEP security proof follows. |
| JSON/Base64 serialization dominated observed 1 MiB workflow time. | `hybrid_performance.csv`; `e3_summary.csv`; Figure 3; Claim C5. | Prepared keys, one Windows machine, 20 timed repetitions per configuration; total includes serialization and excludes keygen. |
| The fixed-format package-size skeleton matched every controlled E3 package size. | `analysis/models.py`; `e3_summary.csv` model residual; Figure 4; Claim C4. | Exact structural accounting for fixed filename/IDs, not independent cryptographic validation or a general compression law. |
| One valid E4 case succeeded and ten controlled invalid/mismatched cases returned no plaintext. | `security_validation.csv`; `e4_validation.csv`; Claim C6. | Deterministic correctness cases, not a representative attack sample; rejection does not establish malicious intent. |

The full [claim–evidence matrix](analysis/CLAIM_EVIDENCE_MATRIX.md) gives the assumptions and intended report sections. Recheck every numerical sentence against raw rows before submission.

## HOW: mathematics, implementation and evaluation

- [ ] Explain `c_i = M³ mod n_i`, `N_S = ∏ n_i`, `X = M³ mod N_S`; with valid inputs, `M³ < N_S` gives `X=M³` and exact integer cube root `M`. Distinguish an exact root from experimentally confirmed original plaintext.
- [ ] Show the seven nonempty recipient subsets and the two 96-byte integer values (`B` repeated versus 95 leading zero bytes and `0x02`).
- [ ] Explain that OAEP's randomized encoding gives different RSA representatives before exponentiation; keep same three keys and plaintext in paired comparison.
- [ ] Explain AES-GCM file encryption once, RSA-OAEP wrapping per recipient, canonical JSON header as AAD, and package validation. `PackageSize(L,r) = 4⌈(L+16)/3⌉ + HeaderAndEnvelopeBytes(L,r,filename,IDs)` for the current JSON format. The metadata term can depend on decimal size length and identifier lengths.
- [ ] Describe E1/E2 key-set blocking, E3 warmups and `perf_counter_ns` intervals, separate keygen, CSV provenance, no outlier removal, and E4 correctness cases. Distinguish cryptographic cost, serialization cost and end-to-end workflow time.

## Figures, tables and limits

- **Short report priority:** Figure 1 (attack matrix), Figure 2 (paired defense) and Figure 3 (timing decomposition). Use Figure 4 when the storage-overhead argument has room. Figures 2–3 were corrected in TASK 10; Figure 3 uses independent labeled Y scales.
- **Tables:** compact E1 minimum-count table, E2 comparison, E3 mean/median/IQR and overhead, E4 case outcomes. Keep the full nine-row E3 table as a supplement if page space is tight.
- **Threats to validity:** E2 observations cluster in 20 key blocks; E3 measures a Python workflow on one Windows machine, with first-recipient decryption only; random RSA/OAEP/AES outputs are not bit-for-bit reproducible; E4 tests selected mutations only. The 0/60 OAEP observation is limited to the tested attack procedure.
- **Facts needing academic sources:** the established broadcast attack and CRT condition; RSAES-OAEP definition/security context; AES-GCM authenticated encryption and nonce requirements; hybrid encryption design. Verify primary standards and any papers when writing the report. Do not invent a prior-work gap or citations.
- **Open inputs from the user/instructor:** rubric text, report template, page/word limits, citation style, author list and contribution approval, figure limits, and required submission format.
