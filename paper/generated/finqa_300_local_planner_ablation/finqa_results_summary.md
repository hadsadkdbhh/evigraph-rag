# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_ablation` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Top-k Program | 0.50 | 0.75 | 0.57 | 0.81 | 0.78 | 1414.75 |
| Oracle-doc | Full context | 0.50 | 0.76 | 0.57 | 0.81 | 0.78 | 1666.70 |
| Oracle-doc | Utility-only | 0.49 | 0.75 | 0.55 | 0.80 | 0.77 | 1265.82 |
| Oracle-doc | No risk | 0.50 | 0.75 | 0.57 | 0.81 | 0.78 | 1176.61 |
| Oracle-doc | No planner | 0.45 | 0.70 | 0.48 | 0.75 | 0.72 | 1176.61 |
| Oracle-doc | No verifier | 0.51 | 0.00 | 0.00 | 0.00 | 0.00 | 1176.61 |
| Oracle-doc | No support graph | 0.50 | 0.75 | 0.57 | 0.81 | 0.78 | 1176.61 |
| Oracle-doc | Full EviGraph | 0.51 | 0.78 | 0.60 | 0.81 | 0.81 | 1176.61 |
| Open BM25 | Top-k Program | 0.39 | 0.77 | 0.54 | 0.79 | 0.78 | 858.12 |
| Open BM25 | Full context | 0.38 | 0.79 | 0.56 | 0.83 | 0.80 | 3417.26 |
| Open BM25 | Utility-only | 0.33 | 0.75 | 0.49 | 0.76 | 0.75 | 857.23 |
| Open BM25 | No risk | 0.40 | 0.79 | 0.55 | 0.82 | 0.79 | 859.50 |
| Open BM25 | No planner | 0.36 | 0.73 | 0.47 | 0.76 | 0.73 | 859.50 |
| Open BM25 | No verifier | 0.41 | 0.00 | 0.00 | 0.00 | 0.00 | 859.50 |
| Open BM25 | No support graph | 0.39 | 0.77 | 0.53 | 0.79 | 0.78 | 859.50 |
| Open BM25 | Full EviGraph | 0.40 | 0.79 | 0.55 | 0.82 | 0.79 | 859.50 |
| BM25 + source rerank | Top-k Program | 0.50 | 0.75 | 0.56 | 0.80 | 0.78 | 1311.80 |
| BM25 + source rerank | Full context | 0.47 | 0.78 | 0.57 | 0.82 | 0.78 | 2577.37 |
| BM25 + source rerank | Utility-only | 0.45 | 0.73 | 0.52 | 0.76 | 0.74 | 1163.78 |
| BM25 + source rerank | No risk | 0.50 | 0.75 | 0.57 | 0.81 | 0.78 | 983.22 |
| BM25 + source rerank | No planner | 0.45 | 0.70 | 0.48 | 0.75 | 0.72 | 983.22 |
| BM25 + source rerank | No verifier | 0.51 | 0.00 | 0.00 | 0.00 | 0.00 | 983.22 |
| BM25 + source rerank | No support graph | 0.50 | 0.72 | 0.57 | 0.80 | 0.78 | 983.22 |
| BM25 + source rerank | Full EviGraph | 0.51 | 0.78 | 0.59 | 0.81 | 0.81 | 983.22 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | +0.06 | +0.00 | +0.01 | +0.01 | +0.01 | +0.02 | 0.78 |
| Open BM25 | +0.04 | -0.01 | +0.02 | +0.00 | +0.01 | +0.07 | 0.79 |
| BM25 + source rerank | +0.06 | +0.00 | +0.01 | +0.01 | +0.01 | +0.06 | 0.78 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 43 | 29 | 34 | 22 | 17 | 2 |
| Open BM25 | 52 | 34 | 39 | 27 | 18 | 9 |
| BM25 + source rerank | 42 | 29 | 34 | 23 | 17 | 2 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 5 | 1 | 3 | 3 | 10 | 24 |
| Open BM25 | 5 | 4 | 5 | 6 | 13 | 26 |
| BM25 + source rerank | 4 | 1 | 4 | 2 | 9 | 25 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
