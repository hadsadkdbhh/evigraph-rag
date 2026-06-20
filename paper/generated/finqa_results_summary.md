# FinQA Paper Assets

Generated from `outputs/eval/finqa` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | topk | 0.63 | 0.83 | 0.67 | 0.90 | 0.87 | 1433.58 |
| Oracle-doc | utility_only | 0.63 | 0.83 | 0.67 | 0.90 | 0.87 | 1318.61 |
| Oracle-doc | full_evigraph | 0.63 | 0.83 | 0.67 | 0.90 | 0.87 | 1189.47 |
| Open BM25 | topk | 0.53 | 0.82 | 0.63 | 0.85 | 0.84 | 840.41 |
| Open BM25 | utility_only | 0.45 | 0.72 | 0.52 | 0.76 | 0.74 | 839.26 |
| Open BM25 | full_evigraph | 0.54 | 0.82 | 0.63 | 0.87 | 0.84 | 842.87 |
| Open hybrid | topk | 0.53 | 0.83 | 0.64 | 0.86 | 0.85 | 845.99 |
| Open hybrid | utility_only | 0.46 | 0.73 | 0.53 | 0.77 | 0.75 | 849.18 |
| Open hybrid | full_evigraph | 0.53 | 0.83 | 0.64 | 0.87 | 0.85 | 849.60 |
| BM25 + source rerank | topk | 0.61 | 0.82 | 0.66 | 0.89 | 0.86 | 1252.04 |
| BM25 + source rerank | utility_only | 0.56 | 0.78 | 0.61 | 0.84 | 0.81 | 1157.64 |
| BM25 + source rerank | full_evigraph | 0.63 | 0.84 | 0.67 | 0.90 | 0.87 | 1367.17 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 8 | 13 | 7 | 4 | 2 | 3 |
| Open BM25 | 12 | 14 | 9 | 5 | 3 | 3 |
| Open hybrid | 14 | 14 | 9 | 5 | 3 | 2 |
| BM25 + source rerank | 9 | 12 | 7 | 4 | 2 | 3 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 2 | 0 | 1 | 2 | 0 | 4 |
| Open BM25 | 3 | 1 | 1 | 1 | 0 | 7 |
| Open hybrid | 3 | 3 | 2 | 2 | 0 | 6 |
| BM25 + source rerank | 2 | 0 | 1 | 2 | 0 | 5 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open BM25 and open hybrid separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
