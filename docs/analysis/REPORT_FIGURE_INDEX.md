# Report figure index

| Figure | Files | Role | Caption guidance |
| --- | --- | --- | --- |
| Figure 1 | figures/figure_1_e1_recovery_matrix.png/.svg | Essential | E1 recovery counts out of 20 key-set blocks for all seven subsets. The two 96-byte samples are B repeated 96 times and 95 leading zero bytes followed by 0x02. |
| Figure 2 | figures/figure_2_e2_scheme_comparison.png/.svg | Essential | E2 paired outcomes across 60 comparisons in 20 key-set blocks; distinguish attack recovery from legitimate decryption and ciphertext diversity. |
| Figure 3 | figures/figure_3_e3_timing_decomposition.png/.svg | Essential | E3 mean encrypt+wrap versus JSON/Base64 serialization, n=20 per bar; total excludes key generation. Each file-size panel has an independent Y scale starting at zero; compare numerical axes, not bar heights across panels. |
| Figure 4 | figures/figure_4_e3_package_overhead.png/.svg | Essential for storage argument | Absolute and relative serialized package overhead for nine E3 configurations, n=20 per point. |

Figures 1–4 are suitable for a short report. E4 is better as a compact correctness table than as a chart. Figure 3 should be paired with the median/IQR table; Figure 4 should be paired with the exact structural model and residual column.
