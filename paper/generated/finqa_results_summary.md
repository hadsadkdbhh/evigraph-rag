# FinQA Paper Assets

Generated from `outputs/eval/finqa` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | topk | 0.60 | 0.82 | 0.65 | 0.89 | 0.86 | 1433.58 |
| Oracle-doc | utility_only | 0.60 | 0.82 | 0.65 | 0.89 | 0.86 | 1318.61 |
| Oracle-doc | full_evigraph | 0.60 | 0.82 | 0.65 | 0.89 | 0.86 | 1189.47 |
| Open BM25 | topk | 0.52 | 0.82 | 0.62 | 0.85 | 0.84 | 840.41 |
| Open BM25 | utility_only | 0.42 | 0.71 | 0.50 | 0.75 | 0.73 | 839.26 |
| Open BM25 | full_evigraph | 0.52 | 0.82 | 0.62 | 0.87 | 0.84 | 842.87 |
| Open hybrid | topk | 0.52 | 0.83 | 0.63 | 0.86 | 0.85 | 845.99 |
| Open hybrid | utility_only | 0.43 | 0.71 | 0.50 | 0.75 | 0.73 | 849.18 |
| Open hybrid | full_evigraph | 0.51 | 0.83 | 0.63 | 0.87 | 0.85 | 849.60 |
| BM25 + source rerank | topk | 0.58 | 0.81 | 0.64 | 0.88 | 0.85 | 1252.04 |
| BM25 + source rerank | utility_only | 0.53 | 0.76 | 0.58 | 0.82 | 0.79 | 1157.64 |
| BM25 + source rerank | full_evigraph | 0.61 | 0.83 | 0.65 | 0.89 | 0.86 | 1367.17 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 9 | 13 | 9 | 4 | 2 | 3 |
| Open BM25 | 13 | 14 | 10 | 5 | 3 | 3 |
| Open hybrid | 15 | 14 | 10 | 5 | 3 | 2 |
| BM25 + source rerank | 9 | 12 | 9 | 4 | 2 | 3 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 2 | 1 | 1 | 2 | 0 | 4 |
| Open BM25 | 4 | 2 | 1 | 2 | 1 | 6 |
| Open hybrid | 4 | 3 | 2 | 3 | 1 | 6 |
| BM25 + source rerank | 3 | 1 | 1 | 2 | 0 | 4 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open BM25 and open hybrid separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
