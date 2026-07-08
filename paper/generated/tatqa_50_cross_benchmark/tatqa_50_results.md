# TAT-QA-50 Cross-Benchmark Pilot

Source run:

- Manifest: `configs/experiments.tatqa_50.local_planner.json`
- Baseline output summary: `outputs/eval/tatqa_50_local_planner/summary.md`
- v47 output summary: `outputs/eval/tatqa_50_direction_repair_v47/summary.md`
- v47 retrieval diagnostics: `outputs/eval/tatqa_50_direction_repair_v47/tatqa_50_open_bm25_full_v47_retrieval_diagnostics.md`

| setting | method | n | EM | support | source_hit@8 |
| --- | --- | ---: | ---: | ---: | ---: |
| Oracle-doc | Top-K | 50 | 0.420 | 0.780 | n/a |
| Oracle-doc | Utility-only | 50 | 0.420 | 0.780 | n/a |
| Oracle-doc | Retrieve-then-program | 50 | 0.420 | 0.780 | n/a |
| Oracle-doc | Full EviGraph v47 | 50 | 0.480 | 0.780 | n/a |
| Open BM25 | Full EviGraph v47 | 50 | 0.400 | 0.920 | 0.960 |

Interpretation:

- This is a public cross-benchmark pilot, not a full TAT-QA benchmark claim.
- v47 adds a narrow direction-semantics repair for `in target_year from base_year` and malformed `from, later_year to earlier_year` TAT-QA questions.
- Oracle-doc improves from 0.420 to 0.480 with 3 paired wins and 0 losses.
- Open BM25 improves from 0.360 to 0.400 with 2 paired wins and 0 losses.
- Open BM25 retrieves the gold source for 48/50 examples, but exact match remains 0.400.
- The v47 failure report has 30 failed examples; 28 of them have the gold source in the retrieved context.
- The largest open failure category remains `wrong_numeric_operation_or_row` with 19 examples.
- Row/operation diagnostics split 22 wrong numeric rows into 14 `ambiguous_supported_wrong_number`, 4 `wrong_year_or_period`, 2 `wrong_row_label`, and 2 `wrong_operation_type`.
