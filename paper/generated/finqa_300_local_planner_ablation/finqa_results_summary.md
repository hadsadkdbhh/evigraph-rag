# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_ablation` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Top-k | 0.50 | 0.75 | 0.57 | 0.81 | 0.78 | 1414.75 |
| Oracle-doc | Utility-only | 0.49 | 0.75 | 0.55 | 0.80 | 0.77 | 1265.82 |
| Oracle-doc | No risk | 0.50 | 0.75 | 0.57 | 0.81 | 0.78 | 1176.61 |
| Oracle-doc | No planner | 0.45 | 0.70 | 0.48 | 0.75 | 0.72 | 1176.61 |
| Oracle-doc | No verifier | 0.51 | 0.00 | 0.00 | 0.00 | 0.00 | 1176.61 |
| Oracle-doc | No support graph | 0.50 | 0.75 | 0.57 | 0.81 | 0.78 | 1176.61 |
| Oracle-doc | Full EviGraph | 0.50 | 0.75 | 0.57 | 0.81 | 0.78 | 1176.61 |
| Open BM25 | Top-k | 0.39 | 0.77 | 0.54 | 0.79 | 0.78 | 858.12 |
| Open BM25 | Utility-only | 0.33 | 0.75 | 0.49 | 0.76 | 0.75 | 857.23 |
| Open BM25 | No planner | 0.37 | 0.74 | 0.48 | 0.77 | 0.74 | 852.98 |
| Open BM25 | Full EviGraph | 0.40 | 0.79 | 0.56 | 0.83 | 0.80 | 852.98 |
| BM25 + source rerank | Top-k | 0.50 | 0.75 | 0.56 | 0.80 | 0.78 | 1311.80 |
| BM25 + source rerank | Utility-only | 0.45 | 0.73 | 0.52 | 0.76 | 0.74 | 1163.78 |
| BM25 + source rerank | No planner | 0.45 | 0.70 | 0.48 | 0.75 | 0.72 | 983.22 |
| BM25 + source rerank | Full EviGraph | 0.50 | 0.75 | 0.57 | 0.81 | 0.78 | 983.22 |

## Component Contribution Diagnostics

| setting | planner delta EM | graph vs top-k EM | graph vs utility-only EM | full verifier answer support |
| --- | ---: | ---: | ---: | ---: |
| Oracle-doc | +0.05 | +0.00 | +0.01 | 0.75 |
| Open BM25 | +0.04 | +0.01 | +0.07 | 0.79 |
| BM25 + source rerank | +0.05 | +0.00 | +0.05 | 0.75 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 38 | 29 | 34 | 22 | 17 | 10 |
| Open BM25 | 54 | 34 | 38 | 26 | 18 | 9 |
| BM25 + source rerank | 37 | 29 | 34 | 23 | 17 | 10 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 5 | 1 | 2 | 3 | 7 | 22 |
| Open BM25 | 6 | 4 | 6 | 7 | 12 | 27 |
| BM25 + source rerank | 4 | 1 | 3 | 2 | 6 | 23 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
