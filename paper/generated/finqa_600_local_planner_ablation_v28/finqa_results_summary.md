# FinQA Paper Assets

Generated from `outputs\eval\finqa_600_local_planner_ablation_v28` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Direct RAG | 0.44 | 0.38 | 0.73 | 0.35 | -0.29 | 0.52 | 0.78 | 0.76 | 1416.21 |
| Oracle-doc | Top-k Program | 0.47 | 0.42 | 0.78 | 0.36 | -0.32 | 0.59 | 0.83 | 0.81 | 1416.21 |
| Oracle-doc | Retrieve-then-program | 0.47 | 0.42 | 0.78 | 0.36 | -0.32 | 0.59 | 0.83 | 0.81 | 1416.21 |
| Oracle-doc | Full context | 0.47 | 0.42 | 0.79 | 0.36 | -0.32 | 0.59 | 0.83 | 0.81 | 1672.74 |
| Oracle-doc | Utility-only | 0.46 | 0.42 | 0.78 | 0.36 | -0.32 | 0.57 | 0.82 | 0.80 | 1290.82 |
| Oracle-doc | No risk | 0.47 | 0.43 | 0.79 | 0.36 | -0.32 | 0.59 | 0.83 | 0.81 | 1179.61 |
| Oracle-doc | No planner | 0.43 | 0.38 | 0.73 | 0.35 | -0.31 | 0.49 | 0.78 | 0.76 | 1179.61 |
| Oracle-doc | No verifier rejection | 0.48 | 0.43 | 0.79 | 0.36 | -0.30 | 0.62 | 0.83 | 0.81 | 1179.61 |
| Oracle-doc | No verifier | 0.48 | 0.00 | 0.00 | 0.00 | +0.48 | 0.00 | 0.00 | 0.00 | 1179.61 |
| Oracle-doc | No support graph | 0.47 | 0.43 | 0.79 | 0.36 | -0.32 | 0.59 | 0.83 | 0.81 | 1179.61 |
| Oracle-doc | Full EviGraph | 0.49 | 0.45 | 0.81 | 0.36 | -0.32 | 0.61 | 0.84 | 0.83 | 1179.61 |
| Open BM25 | Direct RAG | 0.31 | 0.27 | 0.66 | 0.39 | -0.35 | 0.42 | 0.71 | 0.69 | 865.73 |
| Open BM25 | Top-k Program | 0.34 | 0.30 | 0.71 | 0.41 | -0.38 | 0.49 | 0.77 | 0.75 | 865.73 |
| Open BM25 | Retrieve-then-program | 0.34 | 0.30 | 0.71 | 0.41 | -0.38 | 0.49 | 0.77 | 0.75 | 865.73 |
| Open BM25 | Full context | 0.35 | 0.32 | 0.78 | 0.46 | -0.43 | 0.56 | 0.83 | 0.80 | 3530.20 |
| Open BM25 | Utility-only | 0.31 | 0.27 | 0.70 | 0.43 | -0.39 | 0.44 | 0.73 | 0.71 | 856.75 |
| Open BM25 | No risk | 0.35 | 0.31 | 0.74 | 0.43 | -0.39 | 0.52 | 0.79 | 0.77 | 870.06 |
| Open BM25 | No planner | 0.31 | 0.28 | 0.69 | 0.42 | -0.38 | 0.44 | 0.74 | 0.72 | 870.06 |
| Open BM25 | No verifier rejection | 0.35 | 0.31 | 0.74 | 0.43 | -0.39 | 0.55 | 0.79 | 0.77 | 870.06 |
| Open BM25 | No verifier | 0.35 | 0.00 | 0.00 | 0.00 | +0.35 | 0.00 | 0.00 | 0.00 | 870.06 |
| Open BM25 | No support graph | 0.34 | 0.30 | 0.72 | 0.42 | -0.38 | 0.50 | 0.77 | 0.75 | 870.06 |
| Open BM25 | Full EviGraph | 0.36 | 0.32 | 0.76 | 0.43 | -0.40 | 0.53 | 0.80 | 0.78 | 870.06 |
| BM25 + source rerank | Direct RAG | 0.44 | 0.38 | 0.72 | 0.34 | -0.28 | 0.51 | 0.77 | 0.75 | 1305.35 |
| BM25 + source rerank | Top-k Program | 0.47 | 0.42 | 0.77 | 0.34 | -0.30 | 0.58 | 0.82 | 0.80 | 1305.35 |
| BM25 + source rerank | Retrieve-then-program | 0.47 | 0.42 | 0.77 | 0.34 | -0.30 | 0.58 | 0.82 | 0.80 | 1305.35 |
| BM25 + source rerank | Full context | 0.46 | 0.42 | 0.80 | 0.38 | -0.34 | 0.60 | 0.84 | 0.81 | 2601.38 |
| BM25 + source rerank | Utility-only | 0.42 | 0.38 | 0.74 | 0.36 | -0.32 | 0.52 | 0.78 | 0.76 | 1181.44 |
| BM25 + source rerank | No risk | 0.47 | 0.43 | 0.79 | 0.36 | -0.32 | 0.59 | 0.83 | 0.81 | 983.63 |
| BM25 + source rerank | No planner | 0.43 | 0.38 | 0.73 | 0.35 | -0.31 | 0.49 | 0.78 | 0.76 | 983.63 |
| BM25 + source rerank | No verifier rejection | 0.48 | 0.43 | 0.79 | 0.36 | -0.30 | 0.62 | 0.83 | 0.81 | 983.63 |
| BM25 + source rerank | No verifier | 0.48 | 0.00 | 0.00 | 0.00 | +0.48 | 0.00 | 0.00 | 0.00 | 983.63 |
| BM25 + source rerank | No support graph | 0.49 | 0.44 | 0.76 | 0.31 | -0.26 | 0.60 | 0.84 | 0.81 | 983.63 |
| BM25 + source rerank | Full EviGraph | 0.48 | 0.44 | 0.81 | 0.36 | -0.32 | 0.61 | 0.84 | 0.83 | 983.63 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier rejection delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | +0.06 | +0.00 | +0.00 | +0.02 | +0.02 | +0.02 | +0.03 | 0.81 |
| Open BM25 | +0.05 | +0.01 | +0.01 | +0.02 | +0.01 | +0.02 | +0.05 | 0.76 |
| BM25 + source rerank | +0.06 | +0.00 | +0.00 | -0.01 | +0.02 | +0.02 | +0.06 | 0.81 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 104 | 54 | 66 | 46 | 27 | 5 |
| Open BM25 | 105 | 62 | 92 | 55 | 36 | 8 |
| BM25 + source rerank | 104 | 55 | 66 | 47 | 27 | 5 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 0 | 0 | 0 | 0 | 0 | 110 |
| Open BM25 | 0 | 0 | 0 | 0 | 0 | 131 |
| BM25 + source rerank | 0 | 0 | 0 | 0 | 0 | 110 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 1.00 | 0.83 | 0.97 | 0.84 | 1.00 | 0.81 | 0.49 |
| Open BM25 | 1.00 | 1.00 | 0.78 | 0.97 | 0.80 | 1.00 | 0.76 | 0.36 |
| BM25 + source rerank | 1.00 | 1.00 | 0.83 | 0.97 | 0.84 | 1.00 | 0.81 | 0.48 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
