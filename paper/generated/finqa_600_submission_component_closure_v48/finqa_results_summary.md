# FinQA Paper Assets

Generated from `outputs\eval\finqa_600_submission_component_closure_v48` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Direct RAG | 0.46 | 0.41 | 0.75 | 0.34 | -0.29 | 0.53 | 0.79 | 0.77 | 1416.21 |
| Oracle-doc | Retrieve-then-program | 0.48 | 0.45 | 0.80 | 0.35 | -0.31 | 0.60 | 0.84 | 0.82 | 1416.21 |
| Oracle-doc | Utility-only | 0.48 | 0.44 | 0.79 | 0.35 | -0.32 | 0.58 | 0.83 | 0.81 | 1290.82 |
| Oracle-doc | No planner | 0.45 | 0.41 | 0.75 | 0.34 | -0.30 | 0.50 | 0.79 | 0.77 | 1179.61 |
| Oracle-doc | No risk | 0.48 | 0.45 | 0.80 | 0.35 | -0.31 | 0.60 | 0.84 | 0.82 | 1179.61 |
| Oracle-doc | No support graph | 0.49 | 0.45 | 0.80 | 0.35 | -0.31 | 0.60 | 0.84 | 0.82 | 1179.61 |
| Oracle-doc | No verifier | 0.50 | 0.00 | 0.00 | 0.00 | +0.50 | 0.00 | 0.00 | 0.00 | 1179.61 |
| Oracle-doc | Full EviGraph | 0.50 | 0.47 | 0.82 | 0.35 | -0.32 | 0.62 | 0.85 | 0.84 | 1179.61 |
| Open BM25 | Direct RAG | 0.32 | 0.28 | 0.67 | 0.39 | -0.35 | 0.43 | 0.72 | 0.70 | 865.73 |
| Open BM25 | Retrieve-then-program | 0.35 | 0.32 | 0.73 | 0.41 | -0.38 | 0.50 | 0.78 | 0.76 | 865.73 |
| Open BM25 | Utility-only | 0.32 | 0.28 | 0.71 | 0.42 | -0.39 | 0.45 | 0.74 | 0.72 | 856.75 |
| Open BM25 | No planner | 0.33 | 0.29 | 0.71 | 0.41 | -0.38 | 0.45 | 0.76 | 0.73 | 870.06 |
| Open BM25 | No risk | 0.36 | 0.33 | 0.75 | 0.42 | -0.39 | 0.53 | 0.80 | 0.77 | 870.06 |
| Open BM25 | No support graph | 0.35 | 0.32 | 0.73 | 0.41 | -0.38 | 0.51 | 0.78 | 0.76 | 870.06 |
| Open BM25 | No verifier | 0.37 | 0.00 | 0.00 | 0.00 | +0.37 | 0.00 | 0.00 | 0.00 | 870.06 |
| Open BM25 | Full EviGraph | 0.38 | 0.35 | 0.79 | 0.44 | -0.41 | 0.55 | 0.81 | 0.81 | 870.06 |
| BM25 + source rerank | Direct RAG | 0.46 | 0.40 | 0.73 | 0.33 | -0.27 | 0.52 | 0.79 | 0.77 | 1305.35 |
| BM25 + source rerank | Retrieve-then-program | 0.48 | 0.45 | 0.78 | 0.34 | -0.30 | 0.59 | 0.83 | 0.81 | 1305.35 |
| BM25 + source rerank | Utility-only | 0.44 | 0.40 | 0.76 | 0.36 | -0.32 | 0.53 | 0.79 | 0.78 | 1181.44 |
| BM25 + source rerank | No planner | 0.44 | 0.41 | 0.75 | 0.34 | -0.30 | 0.50 | 0.79 | 0.77 | 983.63 |
| BM25 + source rerank | No risk | 0.48 | 0.45 | 0.80 | 0.35 | -0.32 | 0.60 | 0.84 | 0.82 | 983.63 |
| BM25 + source rerank | No support graph | 0.51 | 0.46 | 0.77 | 0.31 | -0.26 | 0.61 | 0.85 | 0.82 | 983.63 |
| BM25 + source rerank | No verifier | 0.50 | 0.00 | 0.00 | 0.00 | +0.50 | 0.00 | 0.00 | 0.00 | 983.63 |
| BM25 + source rerank | Full EviGraph | 0.50 | 0.47 | 0.82 | 0.35 | -0.32 | 0.62 | 0.85 | 0.84 | 983.63 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier rejection delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | +0.06 | +0.00 | +0.00 | +0.02 | +0.02 | +0.00 | +0.02 | 0.82 |
| Open BM25 | +0.05 | +0.00 | +0.01 | +0.03 | +0.01 | +0.00 | +0.06 | 0.79 |
| BM25 + source rerank | +0.06 | +0.00 | +0.00 | -0.00 | +0.02 | +0.00 | +0.06 | 0.82 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 96 | 54 | 64 | 46 | 27 | 5 |
| Open BM25 | 116 | 63 | 90 | 55 | 37 | 4 |
| BM25 + source rerank | 96 | 55 | 64 | 47 | 27 | 4 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 0 | 0 | 7 | 9 | 19 | 69 |
| Open BM25 | 0 | 0 | 9 | 17 | 15 | 87 |
| BM25 + source rerank | 0 | 0 | 6 | 9 | 18 | 70 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 1.00 | 0.84 | 0.97 | 0.85 | 1.00 | 0.82 | 0.50 |
| Open BM25 | 1.00 | 1.00 | 0.81 | 0.98 | 0.81 | 1.00 | 0.79 | 0.38 |
| BM25 + source rerank | 1.00 | 1.00 | 0.84 | 0.97 | 0.85 | 1.00 | 0.82 | 0.50 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
