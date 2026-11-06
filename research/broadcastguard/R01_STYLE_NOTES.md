# Style observations from the USTH thesis reference

**Source:** local 35-page PDF, *Password Security Analysis: Experimental Evaluation of Cryptographic Hash Functions* (cover dated July 2026). Read-only inspection of pages 1, 18, 22 and 33, plus a text-level page map. It is a **bachelor thesis example, not a verified midterm template**. No results, citations, names, figures or prose from it are used as BroadcastGuard evidence.

| Observed convention | Appropriate adaptation for a five-page report |
| --- | --- |
| USTH and department identity centered on a dedicated thesis cover (p. 1). | Use a compact title/affiliation block on page 1. Do not spend a whole page on a cover unless required. Do not reuse the thesis author's or supervisor's details. |
| Strong numbered section hierarchy and readable serif mathematics (p. 18). | Use concise numbered sections, consistent symbols (`M`, `n_i`, `N_S`, `X`) and numbered equations only when cross-referenced. |
| Tables have descriptive captions above them; results follow methods (p. 22). | Keep captions self-contained with units, denominators and sample counts. Put measured results next to their interpretation. |
| Numerical bracket references and hanging entries (p. 33). | Numeric citations are a reasonable provisional choice; defer to the instructor's required style. Use DOI/RFC/NIST identifiers and verified metadata. |

The thesis has extensive front matter and many chapters because it is 35 pages. Those conventions do not imply the midterm report requires a title page, abstract length, chapter structure, font, logo, or citation style. A provisional LaTeX implementation could use standard A4 `article`, 11 pt serif text, ordinary margins, `amsmath`, `graphicx`, `booktabs`, and numeric references. Do not alter margins or typography to overfill five pages. No official USTH LaTeX class was verified in R01.
