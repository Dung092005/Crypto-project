# R05 content-preservation check

| Indispensable R04 content | R05 location and status |
| --- | --- |
| Textbook RSA $e=3$, same integer under distinct RSA-2048 moduli, Eve's public observations and pairwise coprimality | §2, retained |
| CRT construction with $N_i=N_S/n_i$ and modular inverses | Eq. (1), retained |
| Integer cube-root check, $M^3<N_S$, exact-root versus correct original integer, attacker versus evaluator | §2 and §3, retained |
| Leading-zero 96-byte input: Eve learns integer 2 but not original byte length | §2, Fig. 2 caption and §5.1, retained |
| Same-key textbook/OAEP experiment; SHA-256, MGF1(SHA-256), empty label and qualified non-recovery | §2, §3, §4, §5.2 and Table 1, retained |
| AES-256-GCM encrypts file once with fresh key/nonce; RSA-2048/$e=65537$ OAEP wraps key per recipient; canonical JSON header is AAD | §3 and Fig. 1, retained |
| Valid recipient decryption, fail-closed selected cases, authenticated public-key assumption and visible metadata | §3, §5.4, §6, retained |
| E1: 20 independent key sets, four samples, seven subsets, 560 predictions, minimum counts 1/2/3/1 | §4, §5.1 and Fig. 2, retained |
| E2: 60 pairs clustered within 20 blocks; 60/60 textbook, 0/60 tested OAEP, 60/60 legitimate decryption | §4, §5.2 and Table 1, retained |
| E3: nine configurations × 20 repetitions; separate RSA key-generation time; 93.78% serialization share in measured 1 MiB/one-recipient workflow | §4, §5.3, Fig. 3 and Table 2, retained |
| E3: medians/IQRs, non-monotonic 1 MiB means, one-recipient decryption limitation and JSON/Base64 size model | §5.3, Eq. (2), Table 2 and §6, retained |
| E4: 11 selected cases, one accepted, ten rejected without plaintext; error-category and interpretation limits | §5.4 and §6, retained |
| No universal OAEP/security proof, one-machine performance limit, no sender identity/replay protection/PKI, no invented primitive | §5.2, §6 and §7, retained |
| Five verified literature references, GitHub, live demonstration and official evidence links | §1, §4 and References, retained |

Only the duplicative methodology table, repeated introduction sentence and restatements in Discussion/Conclusion were removed or shortened. The archived R04 manuscript and PDF remain the comparison baseline; no crypto source, official dataset or audited figure value changed.
