# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | full_evigraph | 0.37 | 0.75 | 0.50 | 0.80 | 0.77 | 1176.61 |
| Open BM25 | full_evigraph | 0.28 | 0.79 | 0.49 | 0.82 | 0.80 | 852.98 |
| BM25 + source rerank | full_evigraph | 0.34 | 0.77 | 0.50 | 0.82 | 0.79 | 1185.57 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 57 | 36 | 40 | 30 | 18 | 9 |
| Open BM25 | 71 | 40 | 43 | 35 | 19 | 8 |
| BM25 + source rerank | 62 | 38 | 38 | 32 | 17 | 11 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 6 | 6 | 5 | 8 | 15 | 26 |
| Open BM25 | 7 | 10 | 9 | 15 | 19 | 30 |
| BM25 + source rerank | 5 | 6 | 8 | 10 | 14 | 31 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
