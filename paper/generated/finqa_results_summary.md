# FinQA Paper Assets

Generated from `outputs\eval\finqa` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | topk | 0.65 | 0.82 | 0.66 | 0.89 | 0.86 | 1433.58 |
| Oracle-doc | utility_only | 0.65 | 0.82 | 0.66 | 0.89 | 0.86 | 1318.61 |
| Oracle-doc | full_evigraph | 0.65 | 0.82 | 0.66 | 0.89 | 0.86 | 1189.47 |
| Open BM25 | topk | 0.54 | 0.80 | 0.61 | 0.84 | 0.82 | 840.41 |
| Open BM25 | utility_only | 0.45 | 0.70 | 0.50 | 0.75 | 0.72 | 839.26 |
| Open BM25 | full_evigraph | 0.55 | 0.80 | 0.61 | 0.86 | 0.82 | 842.87 |
| Open hybrid | topk | 0.54 | 0.81 | 0.62 | 0.85 | 0.83 | 845.99 |
| Open hybrid | utility_only | 0.46 | 0.71 | 0.51 | 0.76 | 0.73 | 849.18 |
| Open hybrid | full_evigraph | 0.54 | 0.81 | 0.62 | 0.86 | 0.83 | 849.60 |
| BM25 + source rerank | topk | 0.63 | 0.81 | 0.65 | 0.88 | 0.85 | 1252.04 |
| BM25 + source rerank | utility_only | 0.58 | 0.77 | 0.60 | 0.83 | 0.80 | 1157.64 |
| BM25 + source rerank | full_evigraph | 0.65 | 0.82 | 0.65 | 0.89 | 0.85 | 1367.17 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 5 | 13 | 8 | 4 | 2 | 3 |
| Open BM25 | 9 | 14 | 10 | 5 | 3 | 4 |
| Open hybrid | 11 | 14 | 10 | 5 | 3 | 3 |
| BM25 + source rerank | 5 | 12 | 8 | 4 | 2 | 4 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1 | 1 | 0 | 0 | 0 | 3 |
| Open BM25 | 2 | 1 | 0 | 0 | 0 | 6 |
| Open hybrid | 2 | 2 | 1 | 1 | 0 | 6 |
| BM25 + source rerank | 1 | 1 | 0 | 0 | 0 | 3 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open BM25 and open hybrid separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
