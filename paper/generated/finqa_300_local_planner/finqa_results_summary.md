# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Full EviGraph | 0.51 | 0.78 | 0.60 | 0.81 | 0.81 | 1176.61 |
| Open BM25 | Full EviGraph | 0.40 | 0.79 | 0.55 | 0.82 | 0.79 | 859.50 |
| BM25 + source rerank | Full EviGraph | 0.51 | 0.78 | 0.59 | 0.81 | 0.81 | 983.22 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0.78 |
| Open BM25 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0.79 |
| BM25 + source rerank | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0.78 |

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
