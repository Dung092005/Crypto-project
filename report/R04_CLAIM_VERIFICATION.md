# R04 claim verification

The source of empirical truth is the immutable official run `official-20261106T083221Z-3bbf57cc` in `docs/evidence/official-20261106T083221Z-3bbf57cc/`. Its manifest names source commit `46c455819e4588736d4777c252d844fa03e7caf3`. The read-back validator reports the run as valid. No R04 report number was obtained from a new experiment.

| Manuscript claim | Evidence or derivation | Boundary |
| --- | --- | --- |
| For the controlled fixed-message textbook RSA case, $M^3<N_S$ permits integer recovery. | CRT construction in §2; `broadcastguard/math_core.py`, `attack_lab.py`; `attack_conditions.csv`. | Requires valid inputs, common $M$, $e=3$ and pairwise-coprime moduli. Eve does not know $M$ in advance. |
| E1: 20 independent key-set blocks × four samples × seven subsets = 560 verified observations; minimum successful subset counts 1, 2, 3, 1. | `attack_conditions.csv`; `docs/analysis/tables/e1_*.csv`; audited Figure 1. | The metric is evaluator-confirmed **integer** equality. The 96-byte leading-zero serialization cannot be reconstructed from recovered integer 2 without its length or an encoding convention. |
| E2: 60 paired trials in 20 key-set blocks; textbook recovery 60/60, tested OAEP recovery 0/60 and legitimate OAEP decryption 60/60. | `oaep_comparison.csv`; `docs/analysis/tables/e2_*.csv`; `broadcastguard/defense_lab.py`. | These are clustered same-key comparisons, not 60 independent key sets or a formal proof of OAEP security. |
| E3: nine file-size/recipient configurations with 20 timings each and 60 separately measured RSA key-generation records. | `hybrid_performance.csv`, `key_generation.csv`, `manifest.json`. | One Windows machine. Routine encryption timing excludes recipient-key generation; decryption times one valid recipient. |
| For 1 MiB and one recipient, mean encrypt+wrap = 0.479550 ms, serialization = 7.232030 ms and total = 7.711580 ms; serialization share = 93.78%. | Raw `hybrid_performance.csv`; `docs/analysis/tables/e3_summary.csv`; share $7.232030/7.711580\times100$. | This is the measured Python JSON/Base64 workflow, not a standalone AES-GCM benchmark. |
| E3 table: nine means, medians, IQRs and overhead percentages. | Rounded from `docs/analysis/tables/e3_summary.csv`, which was computed from raw E3 rows. | Rounding is display only; no outliers removed. Small non-monotonic means do not establish a speed advantage. |
| $P(L,r)=4\lceil(L+16)/3\rceil+H(L,r,f,\mathcal I)$ and zero model residual on fixed E3 metadata. | `broadcastguard/hybrid_sharing.py` JSON/Base64 serializer; `docs/analysis/tables/e3_summary.csv` model columns. | Structural accounting for this serialization skeleton; $H$ depends on filename, IDs and decimal length. It is not a fitted law or cryptographic validation. |
| E4: one valid case accepted, ten altered/mismatched cases rejected without plaintext; eight `decryption_failed`, two `invalid_package`. | `security_validation.csv`; `broadcastguard/hybrid_sharing.py`. | Eleven selected correctness cases, not a statistically representative attack sample. Rejection does not identify intent. |

## Literature and implementation claims

- RSA public-key arithmetic: Rivest, Shamir and Adleman (1978), verified DOI `10.1145/359340.359342`.
- Broader low-degree modular context: Håstad (1988), DOI `10.1137/0217019`. The exact fixed-message CRT threshold is derived in this manuscript; Håstad's broader result is not presented as identical. Only accessible publisher abstract/metadata were reviewed.
- OAEP origin: Bellare and Rogaway, EUROCRYPT '94 proceedings published 1995, DOI `10.1007/BFb0053428`; implementation details and the 190-byte RSA-2048/SHA-256 limit: RFC 8017 §7.1. The Bellare–Rogaway full text was not retrieved.
- GCM authenticated encryption/AAD terminology: NIST SP 800-38D, DOI `10.6028/NIST.SP.800-38D`. Neither GCM nor package fingerprints prove sender identity.
- R04 cites the existing verified bibliography `research/broadcastguard/REFERENCES.bib`; BibTeX lint returned five entries and zero errors/warnings.

The report attributes the group's contribution to controlled integration, validation and analysis. It does not claim to invent RSA, CRT, OAEP or AES-GCM, or to prove universal security from E2/E4 observations.
