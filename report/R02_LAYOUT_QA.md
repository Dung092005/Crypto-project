# R02 compiled-layout QA

- Final artifact: `BroadcastGuard_Report_Draft.pdf`.
- Compiler: Tectonic 0.17.0 (XeTeX). Final PDF: **4 A4 pages**, confirmed by PDF inspection after compilation.
- All four pages were rendered to PNG previews outside the repository and visually inspected. The previews are not manuscript assets and were not committed.
- Page 1: title, seven Vietnamese names and student IDs, affiliation, abstract, introduction and attack equations render. Unicode name extraction confirms the glyphs are encoded. Page 2: method and first two result discussions. Page 3: E1 heatmap, E2 table, E3 data and structural-size equation. Page 4: E3 timing figure, limitations, conclusion and all five references.
- Both figures have readable labels and captions. The E3 figure explicitly identifies independent zero-based Y-axis scales for file-size panels. Table 1's 0/60 and 60/60 entries are visible.
- No clipped objects, missing-character warnings, overfull boxes, undefined references or unresolved citations were found in the final build log. The cited bibliography entries all resolve.
- PDF link inspection found active links to GitHub, the live Streamlit demo, the official evidence directory, four DOI resolvers and RFC 8017. The PDF's existence/HTTP link checks do not constitute a browser test of every destination's full content.
- `Times New Roman` rendered the Vietnamese names correctly on this Windows machine. A new environment without that font must install it or substitute another Unicode-capable font and rebuild/check the PDF.
- The draft is below the provisional five-page ceiling without reduced fonts or margins. The instructor's final template/page-limit rules remain unconfirmed.
