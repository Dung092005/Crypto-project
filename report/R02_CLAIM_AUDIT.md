# R02 claim and evidence audit

Official run directory: `docs/evidence/official-20261106T083221Z-3bbf57cc/`. All numerical evidence below comes from its raw CSV files and `manifest.json`; `summary.json` was used only as a cross-check. The original evidence was not edited.

| ID | Manuscript claim | Direct evidence or derivation | Scope and qualification |
| --- | --- | --- | --- |
| M1 | `c_i=M^3 mod n_i`; CRT yields `X=M^3 mod N_S`; recovery of original integer by this procedure requires `M^3<N_S` | Elementary modular arithmetic and CRT; implementation in `broadcastguard/math_core.py`, `attack_lab.py` and `conditions_analyzer.py` | Pairwise-coprime moduli, same valid integer, e=3, nonnegative exact root. The inequality is evaluator-side ground truth; Eve does not receive M. The user prompt's unexponentiated formulas were corrected. |
| E1-1 | 20 key-set blocks, four samples, seven subsets, 560 rows and all predictions matched | `attack_conditions.csv`: unique `keyset_id`, `sample_id`, `subset`; count rows with `prediction_matches_recovery=True` and `validation_pass=True` | Verification of known fixed-message mathematics, not a new attack. |
| E1-2 | Minimum successful counts 1, 2, 3, 1 | `attack_conditions.csv`: `minimum_successful_count`, checked against `recovered_original` by sample and subset | Order: `short_1`, `medium_96`, `long_180`, `leading_zero_96`. Message bytes are not a general threshold. |
| E1-3 | Two 96-byte inputs differ; `B` repeated 96 has 767-bit integer value, leading-zero sample represents 2 | Construct declared bytes exactly and call `int.from_bytes(..., 'big')`; E1 `message_bits` and recovery rows corroborate | The 95 leading zero bytes are retained for message identity even though integer conversion drops them. |
| E2-1 | 60 paired comparisons nested in 20 key-set blocks; same public keys within each pair | `oaep_comparison.csv`: row count, unique `keyset_id`, `same_public_keys=True` | 60 comparisons are not 60 independent RSA key sets. |
| E2-2 | 60/60 textbook recovery; 0/60 OAEP recovery by tested CRT-and-root; 60/60 legitimate decryptions; 60/60 repeated OAEP ciphertexts distinct | `oaep_comparison.csv`: `textbook_recovered`, `oaep_recovered`, `legitimate_all_decrypt`, `oaep_ciphertexts_distinct` | No claim of universal or formal OAEP security. Legitimate decryption and attack recovery are distinct outcomes. |
| E3-1 | Nine configurations, 20 timed repetitions each, two warmups, separate key generation | `manifest.json`: file sizes, recipient counts, `repetitions`, `warmup`; `hybrid_performance.csv` 180 rows; `key_generation.csv` 60 rows | One Windows 11 system, Python 3.12.10, cryptography 48.0.1; routine workflow excludes RSA keygen. |
| E3-2 | 1 MiB/one-recipient means: 0.479550 ms encrypt+wrap; 7.232030 ms serialization; 7.711580 ms total; 93.78% serialization share | Filter `hybrid_performance.csv` where `file_size_bytes=1048576` and `recipient_count=1`; average `encryption_ns`, `serialization_ns`, `total_encryption_ns`, divide by 1e6; `sum(serialization_ns)/sum(total_encryption_ns)*100` | This is application workflow time, not an isolated AES timing. No causal inference from small differences among recipient groups. |
| E3-3 | At 1 MiB relative serialized overhead is 33.40% for one recipient and 33.58% for five | Same CSV, `overhead_percent` grouped by recipient count, rounded to 2 decimals; `(package_size_bytes-file_size_bytes)/file_size_bytes*100` | Includes JSON/Base64, wrapped keys and metadata; not an intrinsic AES-GCM expansion ratio. |
| E3-4 | Exact structural package accounting for fixed E3 metadata | Eq. (2), based on 16-byte GCM tag and Base64 length `4 ceil((L+16)/3)` plus serialized header/envelope `H`; see `docs/analysis/RESEARCH_FINDINGS.md` and `analysis/models.py` | `H` depends on filename, recipient IDs and decimal length; zero residual under fixed current serializer is not independent cryptographic validation. |
| E4-1 | One valid case accepted; ten invalid/mismatched/modified cases rejected without plaintext | `security_validation.csv`: `expected_status`, `observed_status`, `plaintext_returned`, `validation_pass` across 11 rows | Selected deterministic correctness checks, not a statistical attack sample; rejection does not identify malicious intent. |

## Literature scope

The source-of-truth bibliography is `research/broadcastguard/REFERENCES.bib`, with exactly five cited entries. R01 verification lives in `R01_LITERATURE_VERIFICATION.md`, `R01_CITATION_QC.md` and `02-evidence-matrix.csv`. RSA public-key construction is attributed to Rivest–Shamir–Adleman (1978); Håstad (1988) is historical context for broader low-degree systems, not claimed as the proof of the elementary fixed-message bound. Bellare–Rogaway (EUROCRYPT '94, published 1995) is cited for OAEP's probabilistic-encoding origin; RFC 8017 governs the implemented RSAES-OAEP limit; NIST SP 800-38D supports GCM/AAD semantics. The first two research-paper full texts were not retrieved in R01, so the manuscript does not attribute detailed theorem statements to them.

## Unsupported claims deliberately excluded

- Formal proof that OAEP is universally secure because 0/60 trials recovered original plaintext.
- Sender authentication, replay protection or recipient identity verification from GCM, fingerprints or the package alone.
- General speed ordering for 1, 3 and 5 recipients based on one machine's small measured differences.
- Novel invention of RSA, CRT, OAEP, AES-GCM or a new compression theorem.
