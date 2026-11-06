# BroadcastGuard: research paper blueprint (R01)

**Status:** pre-manuscript plan, not a submitted paper. **Evidence freeze:** audited commit `18327fc7be234ca5328f7a6289a463c8c9e41c6e`; official run `official-20261106T083221Z-3bbf57cc` (runner source `46c455819e4588736d4777c252d844fa03e7caf3`). **Provisional constraint:** five A4 pages *total*, including title, authors and references, based on the instructor information supplied by the student. The exact template and rule remain unverified. Do not shrink type or margins to fit.

## Working title and central argument

**Preferred title:** *BroadcastGuard: A Controlled Study of Low-Exponent RSA Broadcast Recovery and Authenticated Multi-Recipient Sharing*.

**Central argument:** A single educational implementation can connect the exact numerical boundary of textbook RSA broadcast recovery to a same-key OAEP comparison, then show how a standard hybrid design handles multi-recipient files. Its research value lies in controlled conditions, honest failure classification, reproducible evidence, and accounting for application-level overhead. RSA, CRT, OAEP and AES-GCM are established techniques; no new primitive or attack is claimed.

## Questions and claim hierarchy

| Question | Primary answer to establish | Evidence | Strength and boundary |
| --- | --- | --- | --- |
| RQ1: When does the implemented CRT-and-root procedure recover plaintext? | For valid, shared integer `M` and pairwise-coprime moduli, `M^3 < N_S` yields `X=M^3` and exact recovery. | Mathematical derivation; E1 560 rows; Figure 1. | Strongest connection between theorem and measurement; limited to this procedure and assumptions. |
| RQ2: What changes when OAEP replaces textbook RSA under the same keys? | Randomized encoding removes the common unpadded representative used by the simple attack; textbook recovery 60/60, tested OAEP recovery 0/60, legitimate OAEP decryption 60/60. | RFC 8017; E2 paired CSV; Figure 2 or compact table. | Controlled *observation*, not an empirical proof of OAEP security; 60 comparisons occur in 20 independent key-set blocks. |
| RQ3: How do file size and recipient count affect the hybrid workflow and package size? | One AES-GCM content encryption plus one RSA-OAEP key wrap per recipient; JSON/Base64 serialization dominates the measured 1 MiB workflow on the test machine; structural package-size accounting matches fixed-format data. | Design document; E3 180 workflow rows and 60 separate keygen rows; Figures 3–4. | Application engineering and measurement; timings do not generalize to other hardware. |
| RQ4: Do selected invalid packages fail closed? | The one valid E4 case returned plaintext; ten controlled malformed/mismatched/modified cases returned none. | E4 11-case CSV and compact table. | Correctness tests, not a representative sample of attacks or sender authentication. |

### Contribution priority for five pages

1. **Spend most space on RQ1 and RQ2.** The mathematical bound, seven-subset matrix, same-length/different-value comparison, and paired same-key OAEP experiment distinguish this study from an ordinary RSA demo.
2. **Give RQ3 a compact but substantive analysis.** Explain the hybrid data flow, split cryptographic work from JSON/Base64 serialization, and derive package expansion. The 1 MiB/one-recipient means from raw data are 0.479550 ms encrypt+wrap, 7.232030 ms serialization, and 7.711580 ms total (93.78% serialization). Do not call the total AES time.
3. **Summarize RQ4 in a few lines or a compact table.** It confirms selected failure behavior but has less inferential reach. Mention the live Streamlit demo as a reproducibility/teaching artifact, not as a security result.

## Five-page content budget (one column, readable 10.5–11 pt body type)

| Page | Planned content | Display budget |
| --- | --- | --- |
| 1 | Compact title/affiliation/author block, 100–130-word abstract, WHAT/WHY introduction, threat model, contribution list. | No full-page cover. |
| 2 | Prior work in 1 short paragraph; HOW mathematical derivation `c_i=M^3 mod n_i`, `N_S=∏n_i`, `X=M^3 mod N_S`; exact-root versus verified recovery; seven-subset design. | Figure 1 (recovery matrix) at readable width. |
| 3 | Controlled methods: 20 independent key-set blocks, E1 four samples, E2 same keys/three messages, OAEP parameters; implementation boundaries; hybrid format and AAD. | Compact flow schematic only if it replaces prose, not a decorative diagram. |
| 4 | E1 and E2 results and interpretation; 96-byte `B×96` versus `0x00×95 || 0x02`; 60 paired outcomes and 20-block qualification. | Small E2 table; Figure 2 only if it fits without reducing type. |
| 5 | E3 timing/size accounting and E4 integrity outcomes; limitations, conclusion, references and any required contribution statement. | Figure 3 **or** a compact E3 table. Figure 4 is supplemental unless the instructor permits additional material. |

This is a layout target, not a claim that an unbuilt LaTeX document already fits. If the instructor requires a separate title page, shorten the main text or obtain clarification; do not assume references are excluded from the five pages. Prefer two figures (1 and 3), one compact E2 table, and a one-line E4 result in the strictest version. Preserve legibility over figure count.

## Evidence-to-prose rules

- **Established mathematics:** cite the original RSA paper and Håstad for low-exponent context, but derive this project's simple CRT inequality explicitly. Håstad's broader low-degree result is not identical to the seven-subset experiment.
- **Scheme definition:** cite RFC 8017 §7.1 for RSAES-OAEP, including randomized seed and `mLen ≤ k−2hLen−2`; 2048-bit RSA with SHA-256 allows at most 190 plaintext bytes. Attack/Defense use `e=3` for a controlled comparison; Secure Sharing uses `e=65537`. Cite Bellare–Rogaway for the original OAEP construction; do not transfer claims from the abstract into an unconditional security statement.
- **Authenticated encryption:** cite NIST SP 800-38D for GCM and AAD; state that public-key identity and sender authentication are outside the implemented system.
- **Measured values:** cite the immutable official run, not unit-test runtime, quick-mode data or approximate values copied from another document. E1: 20 key sets × 4 samples × 7 subsets = 560 rows; minimum successful counts 1/2/3/1. E2: 60 paired rows in 20 key-set blocks. E3: nine configurations × 20 repetitions, with separate key-generation timing. E4: 11 selected correctness cases.
- **Interpretation:** do not equate an exact cube root with the original plaintext without evaluator comparison; do not call 0/60 OAEP recoveries a proof of security; do not call package rejection proof of malicious intent.

## Analytical details that earn space

For a nonempty subset `S`, the attacker knows only public `(n_i,e,c_i)`. The experimenter checks `M^3<N_S` and candidate equality. In E1, the `B×96` integer is much larger than the integer 2 encoded as 95 leading zero bytes plus `0x02`; both occupy 96 bytes. Figure 1 shows every recipient subset, including non-prefix pairs. This is the report's clearest original *experimental design* choice.

For E3, write `P(L,r)=4⌈(L+16)/3⌉+H(L,r,f,IDs)` bytes for the current compact JSON package. `H` covers the JSON envelope, nonce, filename, decimal file size, fingerprints, and `r` RSA-2048 wrapped-key Base64 strings. It is **not constant** for arbitrary filenames or IDs. Exact zero residual in the controlled dataset means structural accounting matches the serializer; it is not an independently fitted law. Distinguish encrypt+wrap, serialization, total, first-recipient decryption and separate key generation.

## Threat model and limitations to retain

Eve observes public keys and ciphertexts, not private keys. Textbook RSA is intentionally insecure and limited to the attack study. Hybrid sharing assumes recipient public keys were authenticated before use; fingerprints alone do not establish identity. No sender authentication, replay protection, certificate management or revocation is implemented. E3 timing is a Python workflow on one Windows machine, and E4 is a finite set of selected mutations. The live application is a demonstration, not an independent security validation.

## Inputs still needed before manuscript drafting

Instructor-approved template/citation style and confirmation of the five-page counting rule; author names/order, student IDs and contribution statement; any mandatory acknowledgments or disclosure rule; final submission format; permission to include the live URL and figure thumbnails. Do not infer these from the 35-page thesis example.

## Source map

Literature and status: `R01_LITERATURE_VERIFICATION.md` and `REFERENCES.bib`. Empirical claims: `docs/analysis/CLAIM_EVIDENCE_MATRIX.md`, `docs/analysis/tables/`, and `docs/evidence/official-20261106T083221Z-3bbf57cc/`. Figure choices: `docs/analysis/REPORT_FIGURE_INDEX.md`. Reproduction: `docs/REPRODUCIBILITY.md`.
