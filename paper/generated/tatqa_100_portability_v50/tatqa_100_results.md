# TAT-QA-100 Portability Check v50

Source run:

- Manifest: `configs/experiments.tatqa_100.senior_notes_issuance_sum_v50.json`
- Output summary: `outputs/eval/tatqa_100_portability_v50/summary.md`
- Retrieval diagnostics: `outputs/eval/tatqa_100_portability_v50/tatqa_100_open_bm25_full_v50_retrieval_diagnostics.md`
- Failure report: `outputs/eval/tatqa_100_portability_v50/tatqa_100_open_bm25_full_v50_failures.md`
- Row/operation diagnostics: `outputs/eval/tatqa_100_portability_v50/tatqa_100_open_bm25_full_v50_row_operation_diagnostics.md`

| setting | method | n | EM | support | source_hit@8 |
| --- | --- | ---: | ---: | ---: | ---: |
| Oracle-doc | Full EviGraph v50 | 100 | 0.520 | 0.750 | n/a |
| Open BM25 | Full EviGraph v50 | 100 | 0.410 | 0.850 | 0.900 |

Interpretation:

- This is a fixed-seed portability check over 100 arithmetic TAT-QA development examples, not a full TAT-QA benchmark claim.
- The subset is generated with `scripts/build_tatqa_subset.py` using seed 13 and excludes gold derivations from the retrieval corpus.
- The run clears the planned portability gate: Oracle-doc exceeds 0.45 and Open BM25 exceeds 0.35.
- Open BM25 retrieves the gold source for 90/100 examples, while exact match is 41/100; 49/100 examples remain wrong despite source exposure.
- The largest open failure category is `wrong_numeric_operation_or_row` with 35 examples, and row/operation diagnostics identify 26 `ambiguous_supported_wrong_number` cases.
