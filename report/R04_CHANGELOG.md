# R04 changelog from approved R03

- Rebuilt the report as a maintainable LaTeX source: `main.tex`, a separate `cover.tex`, six section files and a source-based TikZ architecture diagram. The verified R01 BibTeX file remains the only bibliography source.
- Added a standalone USTH-style cover using the authentic logo extracted from the user-provided reference thesis. Preserved all seven names and IDs; omitted unsupported supervisor and department fields.
- Expanded the introduction into four connected research questions and clarified that the contribution is controlled integration and evidence-based interpretation of established methods.
- Expanded the mathematical and system-design explanations: explicit CRT construction, exact integer-root check, attacker/evaluator boundary, OAEP same-key controls, AES-GCM/RSA-OAEP data flow and AAD binding. Preserved R03's correction that recovered integer 2 does not reveal 95 leading zero bytes.
- Added a compact architecture diagram and controlled-factor table; connected E1–E4 methods to their correctness checks and official run provenance.
- Extended analysis of the audited E1 matrix, paired E2 results, E3 timing decomposition and nine-configuration statistics, exact package-size accounting, and selected E4 rejections. Preserved all raw values, key-set clustering and limitations.
- Expanded the discussion of byte encoding, empirical versus formal security, JSON/Base64 overhead, one-machine timing and absent sender authentication, replay protection and PKI.
- Produced and visually inspected the nine-page candidate PDF: one cover, seven research-content pages and one reference page. The R02 draft and R03 reviewed PDFs remain untouched.
- No cryptographic source, official dataset, audited figure data or deployed application code was changed.
