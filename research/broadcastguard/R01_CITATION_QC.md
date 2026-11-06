# Citation and claim QC (R01)

`REFERENCES.bib` contains five core references. Crossref BibTeX was exported to `01-raw/` and normalized for key names, DOI casing, page dashes and BibTeX entry types. `bib_lint.py` found no errors or warnings.

The automated `verify_citations.py` reports **3 verified, 1 uncertain and 1 mismatch**. The `uncertain` RFC entry arises from an editor-order discrepancy between index metadata and the RFC Editor page; the NIST `mismatch` arises because Crossref truncates the standard's title to “Recommendation for block cipher modes of operation :”. Manual checks against the [SIAM publisher](https://epubs.siam.org/doi/abs/10.1137/0217019), [NIST publication record](https://csrc.nist.gov/pubs/sp/800/38/d/final), and [RFC Editor full text](https://www.rfc-editor.org/rfc/rfc8017.html) resolve the *bibliographic* identities. The BibTeX uses the Crossref/publisher spelling `Hastad`; the author's name is often rendered Håstad. The accessible abstracts and standard text were used only for the claims in `02-evidence-matrix.csv`. Full Håstad and Bellare–Rogaway texts were not accessed; their status remains `INACCESSIBLE` for full-text claims.

Before manuscript submission, recheck each in-text citation against the exact final sentence. The R01 blueprint has no final prose or page-number citations. No citation is offered as evidence that BroadcastGuard invented any underlying primitive.

## R01 acceptance checks

- Audited source SHA and live main head were checked independently; main remains at the approved TASK 09 SHA at R01 intake.
- Official evidence read-back validator returned `VALID`; no raw experiment data or cryptographic source was edited.
- All four final figures were opened from disk and judged for potential five-page use; Figure 1 and Figure 3 take priority. The reference thesis was read locally, with pages 1, 18, 22 and 33 visually inspected.
- Five core citations have identifiable primary records and bounded claim uses; full-text access limits are explicit.
- BibTeX lint: **5 entries, 0 errors, 0 warnings**. Automated citation verification and manual resolutions are reported above, without hiding the two machine flags.
- `git diff --check` completed with no whitespace errors. No full report or LaTeX manuscript was drafted.
