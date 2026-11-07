# R03 manuscript changelog

Compared with reviewed R02 commit `eb1f22584f0d1ec112c6e693225ea2a4aea65726`:

1. **Abstract:** recast E1 as integer-representative recovery and disclose that the 96-byte leading-zero serialization is not inferred from ciphertexts. This repairs the strongest scientific ambiguity without changing 560 measured outcomes.
2. **Introduction:** made the textbook example's teaching role explicit and separated it from correctly configured RSA-OAEP. The question now asks when the attacker recovers an integer, not necessarily the original bytes.
3. **Mathematical section:** added the CRT sum with $N_i$ and modular inverse $u_i$, its pairwise-coprime justification, integer-only floor cube root and perfect-cube test. Kept the independent experiment evaluator distinct from Eve.
4. **Encoding boundary:** added the explicit equivalence between the one-byte `0x02` serialization and the 96-byte leading-zero serialization as integers. The evaluator's known length is not presented as attacker knowledge.
5. **Method:** stated public-input validation and clarified why same-key pairing controls key-set variation between textbook RSA and OAEP.
6. **E1 discussion and Figure 1 caption:** defined the plotted recovery metric as integer equality and qualified the one-ciphertext leading-zero case. Kept the underlying approved figure and CSV unchanged.
7. **E3 interpretation:** identified JSON/Base64 serialization as an application-format cost, not a defect in AES-GCM.
8. **Conclusion:** maintained the integer/bytes distinction and avoided claims of a new primitive or universal OAEP security.
9. **Artifact:** built `BroadcastGuard_Report_Reviewed.pdf` while retaining `BroadcastGuard_Report_Draft.pdf` as the exact R02 reference.
10. **Layout:** kept the converse statement at the start of page 2 rather than leaving “Conversely,” stranded at the foot of page 1. The revised document remains five A4 pages; references occupy page 5 rather than forcing smaller figures or type.

No cryptographic source, dataset, benchmark result, bibliography metadata, Streamlit file or deployed app was changed.
