# FinQA Paper Assets

Generated from `outputs\eval\finqa_300` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | topk | 0.30 | 0.71 | 0.37 | 0.75 | 0.73 | 1414.75 |
| Oracle-doc | utility_only | 0.29 | 0.70 | 0.36 | 0.74 | 0.72 | 1265.82 |
| Oracle-doc | full_evigraph | 0.30 | 0.71 | 0.37 | 0.75 | 0.73 | 1176.61 |
| Open BM25 | topk | 0.23 | 0.70 | 0.35 | 0.72 | 0.71 | 858.12 |
| Open BM25 | utility_only | 0.19 | 0.67 | 0.31 | 0.68 | 0.67 | 857.23 |
| Open BM25 | full_evigraph | 0.20 | 0.72 | 0.37 | 0.75 | 0.73 | 852.98 |
| Open hybrid | topk | 0.23 | 0.70 | 0.35 | 0.72 | 0.71 | 861.57 |
| Open hybrid | utility_only | 0.19 | 0.67 | 0.31 | 0.68 | 0.67 | 859.49 |
| Open hybrid | full_evigraph | 0.21 | 0.72 | 0.37 | 0.75 | 0.72 | 857.03 |
| BM25 + source rerank | topk | 0.29 | 0.69 | 0.37 | 0.74 | 0.73 | 1311.80 |
| BM25 + source rerank | utility_only | 0.27 | 0.68 | 0.33 | 0.70 | 0.69 | 1174.38 |
| BM25 + source rerank | full_evigraph | 0.27 | 0.73 | 0.38 | 0.76 | 0.74 | 1373.26 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 46 | 42 | 52 | 39 | 27 | 5 |
| Open BM25 | 58 | 48 | 57 | 38 | 31 | 7 |
| Open hybrid | 56 | 48 | 58 | 38 | 30 | 7 |
| BM25 + source rerank | 49 | 45 | 52 | 40 | 27 | 5 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 10 | 8 | 5 | 7 | 10 | 18 |
| Open BM25 | 9 | 11 | 9 | 12 | 11 | 26 |
| Open hybrid | 9 | 11 | 9 | 12 | 11 | 24 |
| BM25 + source rerank | 9 | 8 | 8 | 9 | 10 | 20 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open BM25 and open hybrid separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
