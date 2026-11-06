# R03 independent critical review (working review for the student authors)

**Manuscript reviewed:** R02 commit `eb1f22584f0d1ec112c6e693225ea2a4aea65726`, `report/main.tex` and its four-page PDF. **Scope:** mathematical argument, source/evidence correspondence, citations, five-page layout. This is an author-requested local review, not an editorial decision. **Verdict:** major scientific correction was necessary and has been incorporated; the revised five-page draft is suitable for independent student/instructor review, with open items below.

## Major issues and action

1. **Conflation of integer and byte-string recovery (correctness).** R02 repeatedly called E1's 560 outcomes “original-plaintext recovery.” `evaluate_experiment()` actually scores `outcome.exact and outcome.candidate == message`, where `message` is an integer. It can reconstruct bytes only by receiving `len(scenario.plaintext)` from the evaluator. In particular, ciphertexts yielding integer 2 cannot reveal whether the serialized original was `0x02` or 95 zero bytes followed by `0x02`. **Revision:** abstract, attack-model paragraph, E1 interpretation, Figure 1 caption and conclusion now use *integer-representative recovery* and state the required length/encoding assumption. The raw E1 results were left intact.
2. **CRT algorithm hidden behind notation (HOW).** R02 stated the CRT result but not the construction. **Revision:** define $N_i=N_S/n_i$, inverse $u_i=N_i^{-1}\bmod n_i$, and $X=(\sum c_iN_iu_i)\bmod N_S$; explain the coprimality premise, floor cube root, exact-cube check and evaluator boundary. This matches `math_core.crt()` and `integer_nth_root()`.
3. **Motivation and controls could be sharper (WHY).** R02 did not explain why a same-key OAEP comparison controls a confounder. **Revision:** introduce textbook RSA as an intentionally unsafe teaching case, distinguish it from correctly configured OAEP, and state that using identical keys inside each pair prevents key variation from explaining its difference. The E3 bottleneck is explicitly attributed to the chosen JSON/Base64 workflow, not AES-GCM.

## Minor issues and evidence quality

- The E1 source graphic retains its historical shorthand “recovery”; the revised manuscript caption defines the plotted metric precisely. Rebuilding audited figures would be unnecessary for this manuscript-only review.
- R02's original four-page balance benefited from a compact result presentation. The more explicit CRT and leading-zero analysis expand R03 to five pages; the fifth holds references. The type remains 11 pt with 2.35 cm margins. This is within the provisional maximum but leaves little room for a stricter template.
- E2 reports 60 paired comparisons in **20** independent key-set blocks; its 0/60 OAEP result concerns this attacker procedure, not universal security. E3's timings come from one Windows machine and are application workflow timings; E4 is a selected correctness checklist. These qualifications remain in the paper.
- The package-size equation is an accounting identity for the fixed JSON/Base64 serializer and controlled metadata, not a fitted or universal law.
- Official CSV and source code were examined read-only. The official validator returned `VALID`; independent recounts confirmed E1 560, E2 60, E3 180 and E4 11 records and all stated outcomes.

## WHAT / WHY / HOW assessment

| Rubric | Strength after revision | Remaining risk |
| --- | --- | --- |
| WHAT | The threat model states Eve sees public $(n,e,c)$ observations, no private keys, and explains the exact integer condition and byte-encoding boundary. | Students must explain orally why integer equality alone does not reveal leading-zero serialization. |
| WHY | Connects the classroom vulnerability to historical low-exponent context, a controlled OAEP contrast and measurable packaging costs. | The short report cannot survey the full RSA security literature; no novelty gap is claimed. |
| HOW | Shows explicit CRT arithmetic, exact-root test, public-only attacker versus evaluator, same-key experimental control, hybrid AAD construction and measurement separation. | A five-page limit permits only a compact account of package validation and E4 failure classes. |

## Citation and integrity check

The five R01 bibliography records were retained. The in-text claims were checked against [RSA's bibliographic record](https://doi.org/10.1145/359340.359342), [Håstad's publisher abstract](https://epubs.siam.org/doi/10.1137/0217019), [Bellare–Rogaway's publisher abstract](https://link.springer.com/chapter/10.1007/BFb0053428), [RFC 8017 §7.1](https://www.rfc-editor.org/rfc/rfc8017.html) and [NIST SP 800-38D](https://csrc.nist.gov/pubs/sp/800/38/d/final). Håstad's and Bellare–Rogaway's full texts remain **INACCESSIBLE** under the R01 record; the manuscript uses only the accessible abstract-level claims. RFC 8017 supplies the RSAES-OAEP length formula and empty-label definition; NIST identifies GCM as authenticated encryption with associated data. No source is made to support an E1–E4 experimental number.

## Remaining weaknesses before R04

- The instructor's exact template and whether references count toward the page limit remain unconfirmed; the draft assumes five A4 pages total.
- Authors should confirm spelling, order, student IDs and any required contribution/declaration fields. No roles, supervisor or emails were invented.
- The source uses the locally installed `Times New Roman` font; a different build machine requires that font or an approved Unicode-capable substitution with another visual check.
- The authors should defend the limits of 20 key sets, the 20 timing repetitions on one computer, and the distinction between structural size accounting and cryptographic security.
