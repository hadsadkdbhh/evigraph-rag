# TAT-QA-20 Cross-Benchmark Pilot

Source run:

- Manifest: `configs/experiments.tatqa_20.local_planner.json`
- Output summary: `outputs/eval/tatqa_20_local_planner/summary.md`
- Retrieval diagnostics: `outputs/eval/tatqa_20_local_planner/tatqa_20_open_bm25_full_retrieval_diagnostics.md`

| setting | method | n | EM | support | source_hit@8 |
| --- | --- | ---: | ---: | ---: | ---: |
| Oracle-doc | Top-K | 20 | 0.500 | 0.800 | n/a |
| Oracle-doc | Utility-only | 20 | 0.500 | 0.800 | n/a |
| Oracle-doc | Retrieve-then-program | 20 | 0.500 | 0.800 | n/a |
| Oracle-doc | Full EviGraph | 20 | 0.500 | 0.800 | n/a |
| Open BM25 | Full EviGraph | 20 | 0.450 | 0.850 | 1.000 |

Interpretation:

- This is a small public cross-benchmark pilot, not a full TAT-QA benchmark claim.
- Open BM25 retrieves the gold source for all 20 examples, but exact match remains 0.450.
- The failure report has 11 failed examples; all are `wrong_with_source_hit`, reinforcing the paper's claim that retrieval exposure alone is insufficient.
