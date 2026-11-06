# R04 layout and visual QA

## Artifact and build

- Source: `report/main.tex`, `report/cover.tex`, `report/sections/*.tex`, `report/figures/architecture.tex`.
- PDF: `report/BroadcastGuard_Final_Report_Candidate.pdf` (A4, 9 pages).
- Page allocation: **1 standalone cover + 7 substantive content pages + 1 reference page**. Cover is PDF page 1; content is PDF pages 2–8; references are PDF page 9. The content pages are numbered 1–7 in the PDF.
- Compiler used: Tectonic 0.17.0 with XeTeX/Unicode font support. From the repository root on the author's Windows machine:

```powershell
$env:HTTP_PROXY=''; $env:HTTPS_PROXY=''; $env:ALL_PROXY=''
Push-Location report
& '..\..\r02-tools\tectonic.exe' -k --keep-logs -o ..\..\r04-build main.tex
Pop-Location
Copy-Item ..\r04-build\main.pdf report\BroadcastGuard_Final_Report_Candidate.pdf
```

`r02-tools` is a local compiler location, not a repository dependency. Another installation of Tectonic or XeLaTeX can compile the same source; Times New Roman or a metrically suitable Unicode font must be available. The source bibliography remains `research/broadcastguard/REFERENCES.bib`.

## Visual inspection

All nine final PDF pages were rendered and inspected individually. The cover uses the authentic USTH logo extracted from the user-supplied reference thesis and flattened against white using its original transparency mask. The names and student IDs match the request and display with Vietnamese diacritics. The thin border, title, academic heading and date are readable. No lecturer, department or thesis designation was invented.

The CRT equation and package-size identity fit their columns. The architecture diagram, audited E1 recovery matrix and audited E3 timing chart are readable; the E3 chart explicitly indicates independent zero-based Y scales. Tables 1–3 fit within margins. Figure captions state sample counts or measurement units. The reference list is on its own page, with linked DOIs and the RFC link. PDF text extraction retains the seven Vietnamese names; all pages measure approximately 595 × 842 PDF points (A4).

The final LaTeX log contains no overfull/underfull boxes, missing-character warnings, unresolved citations/references or duplicate page destinations. Tectonic reports font-configuration/Windows font-path warnings only; a fresh machine may require a different installed Unicode serif font. Minor intentional whitespace remains at the bottom of the E4 and conclusion pages to keep discussion and references coherent.

## Submission boundary

The seven-page scientific-content allocation follows the user's updated preference. The final written instructor rule on whether cover and references are excluded from the content limit still needs confirmation before submission. This PDF is a **candidate for human review**, not a submitted report.
