# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_ablation` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | topk | 0.46 | 0.75 | 0.53 | 0.81 | 0.78 | 1414.75 |
| Oracle-doc | utility_only | 0.46 | 0.75 | 0.52 | 0.80 | 0.77 | 1265.82 |
| Oracle-doc | evigraph_wo_risk | 0.46 | 0.75 | 0.53 | 0.81 | 0.78 | 1176.61 |
| Oracle-doc | evigraph_wo_verifier | 0.47 | 0.00 | 0.00 | 0.00 | 0.00 | 1176.61 |
| Oracle-doc | evigraph_wo_support | 0.46 | 0.75 | 0.53 | 0.81 | 0.78 | 1176.61 |
| Oracle-doc | full_evigraph | 0.46 | 0.75 | 0.53 | 0.81 | 0.78 | 1176.61 |
| Open BM25 | topk | 0.36 | 0.77 | 0.51 | 0.79 | 0.78 | 858.12 |
| Open BM25 | utility_only | 0.31 | 0.75 | 0.46 | 0.76 | 0.75 | 857.23 |
| Open BM25 | full_evigraph | 0.37 | 0.79 | 0.52 | 0.83 | 0.80 | 852.98 |
| BM25 + source rerank | topk | 0.46 | 0.75 | 0.53 | 0.80 | 0.78 | 1311.80 |
| BM25 + source rerank | utility_only | 0.41 | 0.73 | 0.48 | 0.76 | 0.74 | 1163.78 |
| BM25 + source rerank | full_evigraph | 0.43 | 0.77 | 0.54 | 0.82 | 0.79 | 1185.57 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 38 | 31 | 35 | 29 | 18 | 10 |
| Open BM25 | 54 | 36 | 38 | 33 | 19 | 9 |
| BM25 + source rerank | 44 | 33 | 34 | 31 | 17 | 12 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 5 | 1 | 2 | 3 | 7 | 22 |
| Open BM25 | 6 | 4 | 6 | 7 | 12 | 27 |
| BM25 + source rerank | 4 | 1 | 5 | 4 | 6 | 27 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
