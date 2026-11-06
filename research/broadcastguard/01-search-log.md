# R01 source search log

Date: 2026-11-06 UTC. Tool: `C:/Users/admin/.cs-research-lab/lab/scripts/paper_api.py` (OpenAlex first, Crossref DOI verification). No OpenAlex MCP tool was connected. Raw normalized JSONL and BibTeX exports are retained under `01-raw/`. Searches were **targeted core-source checks**, not an exhaustive systematic search.

| Step | Exact query/identifier | Source | Returned | Outcome |
| --- | --- | --- | ---: | --- |
| 1 | `Solving simultaneous modular equations of low degree Håstad` | OpenAlex search, limit 5 | 5 | Target absent from top five; no inference of absence in literature. |
| 2 | `Optimal Asymmetric Encryption Bellare Rogaway` | OpenAlex search, limit 5 | 5 | Target absent from top five; DOI lookup used. |
| 3 | `A Method for Obtaining Digital Signatures and Public-Key Cryptosystems` | OpenAlex search, limit 5 | 5 | Original 1978 article identified among other editions. |
| 4 | `10.1137/0217019`, `10.1007/BFb0053428`, `10.1145/359340.359342`, `10.6028/NIST.SP.800-38D` | Crossref exact DOI get and BibTeX export | 4 + 4 | Title/author/year identifiers checked; publisher/standard pages cross-checked. |
| 5 | `https://www.rfc-editor.org/rfc/rfc8017.html`; NIST, SIAM and Springer DOI pages | Official web pages | 4 core pages | Checked relevant abstract/sections and publication metadata. |

Re-run a DOI check with `python C:/Users/admin/.cs-research-lab/lab/scripts/paper_api.py get --source crossref --id doi:10.1137/0217019`. API response timestamps and request URLs are stored in each JSONL `provenance` field. No search snippets were promoted to full-text evidence.
