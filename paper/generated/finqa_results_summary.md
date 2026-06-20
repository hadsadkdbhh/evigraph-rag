# FinQA Paper Assets

Generated from `outputs/eval/finqa` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | topk | 0.56 | 0.81 | 0.65 | 0.87 | 0.85 | 1433.58 |
| Oracle-doc | utility_only | 0.56 | 0.81 | 0.65 | 0.87 | 0.85 | 1318.61 |
| Oracle-doc | full_evigraph | 0.56 | 0.81 | 0.65 | 0.87 | 0.85 | 1189.47 |
| Open BM25 | topk | 0.47 | 0.80 | 0.61 | 0.83 | 0.82 | 840.41 |
| Open BM25 | utility_only | 0.37 | 0.69 | 0.49 | 0.72 | 0.71 | 839.26 |
| Open BM25 | full_evigraph | 0.47 | 0.81 | 0.62 | 0.84 | 0.83 | 842.87 |
| Open hybrid | topk | 0.47 | 0.81 | 0.62 | 0.84 | 0.83 | 845.99 |
| Open hybrid | utility_only | 0.38 | 0.69 | 0.49 | 0.72 | 0.71 | 849.18 |
| Open hybrid | full_evigraph | 0.47 | 0.82 | 0.63 | 0.85 | 0.84 | 849.60 |
| BM25 + source rerank | topk | 0.53 | 0.79 | 0.63 | 0.85 | 0.83 | 1252.04 |
| BM25 + source rerank | utility_only | 0.47 | 0.74 | 0.57 | 0.79 | 0.77 | 1157.64 |
| BM25 + source rerank | full_evigraph | 0.56 | 0.82 | 0.65 | 0.87 | 0.85 | 1367.17 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 13 | 13 | 10 | 4 | 2 | 2 |
| Open BM25 | 18 | 14 | 12 | 5 | 3 | 1 |
| Open hybrid | 19 | 14 | 11 | 5 | 3 | 1 |
| BM25 + source rerank | 14 | 12 | 10 | 4 | 2 | 2 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open BM25 and open hybrid separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
