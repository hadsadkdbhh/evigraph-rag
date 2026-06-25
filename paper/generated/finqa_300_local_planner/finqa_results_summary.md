# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | full_evigraph | 0.42 | 0.77 | 0.51 | 0.82 | 0.79 | 1176.61 |
| Open BM25 | full_evigraph | 0.33 | 0.81 | 0.51 | 0.84 | 0.81 | 852.98 |
| BM25 + source rerank | full_evigraph | 0.39 | 0.79 | 0.52 | 0.84 | 0.80 | 1185.57 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 45 | 35 | 37 | 30 | 18 | 9 |
| Open BM25 | 60 | 39 | 39 | 35 | 19 | 8 |
| BM25 + source rerank | 52 | 37 | 35 | 32 | 17 | 11 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 6 | 2 | 2 | 6 | 10 | 24 |
| Open BM25 | 7 | 7 | 7 | 12 | 13 | 28 |
| BM25 + source rerank | 5 | 3 | 6 | 8 | 9 | 29 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
