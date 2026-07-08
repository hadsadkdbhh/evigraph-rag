# TAT-QA-50 Cross-Benchmark Pilot

Source run:

- Manifest: `configs/experiments.tatqa_50.local_planner.json`
- Output summary: `outputs/eval/tatqa_50_local_planner/summary.md`
- Retrieval diagnostics: `outputs/eval/tatqa_50_local_planner/tatqa_50_open_bm25_full_retrieval_diagnostics.md`

| setting | method | n | EM | support | source_hit@8 |
| --- | --- | ---: | ---: | ---: | ---: |
| Oracle-doc | Top-K | 50 | 0.420 | 0.780 | n/a |
| Oracle-doc | Utility-only | 50 | 0.420 | 0.780 | n/a |
| Oracle-doc | Retrieve-then-program | 50 | 0.420 | 0.780 | n/a |
| Oracle-doc | Full EviGraph | 50 | 0.420 | 0.780 | n/a |
| Open BM25 | Full EviGraph | 50 | 0.360 | 0.920 | 0.960 |

Interpretation:

- This is a public cross-benchmark pilot, not a full TAT-QA benchmark claim.
- Open BM25 retrieves the gold source for 48/50 examples, but exact match remains 0.360.
- The failure report has 32 failed examples; 30 of them have the gold source in the retrieved context.
- The largest open failure category is `wrong_numeric_operation_or_row` with 21 examples.
- Row/operation diagnostics split 24 wrong numeric rows into 16 `ambiguous_supported_wrong_number`, 4 `wrong_year_or_period`, 2 `wrong_row_label`, and 2 `wrong_operation_type`.
