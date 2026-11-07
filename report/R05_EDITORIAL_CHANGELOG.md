# R05 editorial changelog from approved R04

## Layout and navigation

- Removed the forced \clearpage before Discussion and References. The nine-page R04 PDF left substantial unused space late in the report and placed five short references alone on its last page.
- Added a real section-level \tableofcontents immediately after the abstract. LaTeX generates and hyperlinks seven major sections and References; no separate contents page was added.
- Added an explicit References TOC entry with \phantomsection and \addcontentsline. The bibliography remains generated from the verified shared BibTeX file.
- Preserved the R04 cover, logo, 11-point body, A4 paper and 2.35 cm margins.
- Added a float barrier after the E3 timing figure so its caption precedes the E3 statistical table. A trial barrier after the architecture diagram produced nine pages and was removed.

## Scientific editing

- Removed R04's E1–E4 methodology table because its factor, control and outcome cells repeated the adjacent method paragraphs. Those paragraphs still state the independent variables, controlled key sets, measurements, repetitions and correctness checks.
- Removed one closing contribution/novelty sentence from the Introduction that repeated the abstract and Conclusion.
- Rewrote the Discussion at lower length: retained the integer-versus-byte boundary, paired E2 design and limits, single-machine E3 interpretation, first-recipient decryption limit, public-key-authentication assumption, visible metadata and unsupported security properties. Removed repeated restatements of the full E1–E4 results.
- Shortened the Conclusion while retaining all four experiment connections and the bounded engineering contribution.
- Clarified that one fresh AES file key is wrapped separately for every recipient, named the three E3 payload sizes explicitly after removing the methods table, and corrected the ambiguous phrase identifying the two 96-byte samples.
- Left the CRT derivation, system design, E1 recovery matrix, E2 comparison table, E3 timing figure and nine-configuration table, E4 case list, package-size identity and five citations intact. No measurement or official evidence file was changed.

The candidate changed from **9 to 8 total A4 pages** by using existing space and removing genuine repetition, without reducing the body font or margins.

The organization was checked against [IEEE's paper-structure guidance](https://conferences.ieeeauthorcenter.ieee.org/write-your-paper/structure-your-paper/), [UNSW's engineering/science report guidance](https://www.unsw.edu.au/student/managing-your-studies/academic-skills-support/toolkit/writing/engineering-science/report), and [UW–Madison's science-report guidance](https://writing.wisc.edu/handbook/academicwriting/sciencereport/). The real LaTeX contents mechanism follows [Overleaf's TOC documentation](https://www.overleaf.com/learn/latex/Table_of_contents). These are editorial/technical guides, not new cryptographic references in the paper.
