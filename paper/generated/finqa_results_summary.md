# FinQA Paper Assets

Generated from `outputs/eval/finqa` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | topk | 0.57 | 0.81 | 0.65 | 0.88 | 0.85 | 1433.58 |
| Oracle-doc | utility_only | 0.57 | 0.81 | 0.65 | 0.88 | 0.85 | 1318.61 |
| Oracle-doc | full_evigraph | 0.57 | 0.81 | 0.65 | 0.88 | 0.85 | 1189.47 |
| Open BM25 | topk | 0.49 | 0.80 | 0.61 | 0.83 | 0.82 | 840.41 |
| Open BM25 | utility_only | 0.39 | 0.69 | 0.49 | 0.73 | 0.71 | 839.26 |
| Open BM25 | full_evigraph | 0.50 | 0.81 | 0.62 | 0.84 | 0.83 | 842.87 |
| Open hybrid | topk | 0.49 | 0.81 | 0.62 | 0.84 | 0.83 | 845.99 |
| Open hybrid | utility_only | 0.40 | 0.69 | 0.49 | 0.73 | 0.71 | 849.18 |
| Open hybrid | full_evigraph | 0.49 | 0.82 | 0.63 | 0.85 | 0.84 | 849.60 |
| BM25 + source rerank | topk | 0.55 | 0.79 | 0.63 | 0.86 | 0.83 | 1252.04 |
| BM25 + source rerank | utility_only | 0.49 | 0.74 | 0.57 | 0.80 | 0.77 | 1157.64 |
| BM25 + source rerank | full_evigraph | 0.58 | 0.82 | 0.65 | 0.88 | 0.85 | 1367.17 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 12 | 13 | 9 | 4 | 2 | 3 |
| Open BM25 | 15 | 14 | 12 | 5 | 3 | 1 |
| Open hybrid | 17 | 14 | 11 | 5 | 3 | 1 |
| BM25 + source rerank | 12 | 12 | 9 | 4 | 2 | 3 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 4 | 1 | 1 | 2 | 0 | 5 |
| Open BM25 | 5 | 2 | 1 | 2 | 1 | 7 |
| Open hybrid | 5 | 3 | 2 | 3 | 1 | 7 |
| BM25 + source rerank | 5 | 1 | 1 | 2 | 0 | 5 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open BM25 and open hybrid separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
