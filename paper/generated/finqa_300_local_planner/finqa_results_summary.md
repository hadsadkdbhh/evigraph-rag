# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | full_evigraph | 0.50 | 0.75 | 0.57 | 0.81 | 0.78 | 1176.61 |
| Open BM25 | full_evigraph | 0.40 | 0.79 | 0.56 | 0.83 | 0.80 | 852.98 |
| BM25 + source rerank | full_evigraph | 0.48 | 0.77 | 0.57 | 0.82 | 0.78 | 1182.17 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 38 | 29 | 34 | 22 | 17 | 10 |
| Open BM25 | 54 | 34 | 38 | 26 | 18 | 9 |
| BM25 + source rerank | 42 | 30 | 33 | 23 | 17 | 12 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 5 | 1 | 2 | 3 | 7 | 22 |
| Open BM25 | 6 | 4 | 6 | 7 | 12 | 27 |
| BM25 + source rerank | 4 | 1 | 5 | 4 | 5 | 26 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
