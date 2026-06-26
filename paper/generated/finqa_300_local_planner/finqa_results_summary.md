# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | full_evigraph | 0.44 | 0.77 | 0.52 | 0.82 | 0.80 | 1176.61 |
| Open BM25 | full_evigraph | 0.35 | 0.81 | 0.51 | 0.84 | 0.82 | 852.98 |
| BM25 + source rerank | full_evigraph | 0.40 | 0.79 | 0.52 | 0.84 | 0.81 | 1185.57 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 43 | 35 | 35 | 29 | 18 | 9 |
| Open BM25 | 57 | 39 | 38 | 34 | 19 | 8 |
| BM25 + source rerank | 49 | 37 | 34 | 31 | 17 | 11 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 6 | 2 | 2 | 5 | 10 | 23 |
| Open BM25 | 7 | 5 | 6 | 9 | 13 | 28 |
| BM25 + source rerank | 5 | 2 | 5 | 6 | 9 | 28 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
