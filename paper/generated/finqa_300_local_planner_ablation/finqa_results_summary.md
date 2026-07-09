# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_ablation` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Direct RAG | 0.49 | 0.43 | 0.71 | 0.28 | -0.22 | 0.51 | 0.76 | 0.73 | 1414.75 |
| Oracle-doc | Top-k Program | 0.53 | 0.48 | 0.77 | 0.28 | -0.24 | 0.57 | 0.82 | 0.79 | 1414.75 |
| Oracle-doc | Retrieve-then-program | 0.53 | 0.48 | 0.77 | 0.28 | -0.24 | 0.57 | 0.82 | 0.79 | 1414.75 |
| Oracle-doc | Full context | 0.53 | 0.48 | 0.77 | 0.29 | -0.24 | 0.57 | 0.82 | 0.79 | 1666.70 |
| Oracle-doc | Utility-only | 0.52 | 0.47 | 0.76 | 0.29 | -0.24 | 0.55 | 0.81 | 0.78 | 1265.82 |
| Oracle-doc | No risk | 0.53 | 0.48 | 0.77 | 0.28 | -0.24 | 0.57 | 0.82 | 0.79 | 1178.88 |
| Oracle-doc | No planner | 0.48 | 0.43 | 0.71 | 0.28 | -0.23 | 0.48 | 0.76 | 0.73 | 1178.88 |
| Oracle-doc | No verifier rejection | 0.54 | 0.48 | 0.77 | 0.28 | -0.23 | 0.60 | 0.82 | 0.79 | 1178.88 |
| Oracle-doc | No verifier | 0.54 | 0.00 | 0.00 | 0.00 | +0.54 | 0.00 | 0.00 | 0.00 | 1178.88 |
| Oracle-doc | No support graph | 0.52 | 0.48 | 0.77 | 0.29 | -0.24 | 0.57 | 0.82 | 0.79 | 1178.88 |
| Oracle-doc | Full EviGraph | 0.55 | 0.50 | 0.79 | 0.29 | -0.25 | 0.60 | 0.82 | 0.82 | 1178.88 |
| Open BM25 | Direct RAG | 0.39 | 0.33 | 0.72 | 0.39 | -0.33 | 0.47 | 0.74 | 0.72 | 858.12 |
| Open BM25 | Top-k Program | 0.42 | 0.37 | 0.79 | 0.41 | -0.37 | 0.54 | 0.81 | 0.79 | 858.12 |
| Open BM25 | Retrieve-then-program | 0.42 | 0.37 | 0.79 | 0.41 | -0.37 | 0.54 | 0.81 | 0.79 | 858.12 |
| Open BM25 | Full context | 0.41 | 0.38 | 0.81 | 0.43 | -0.40 | 0.56 | 0.85 | 0.81 | 3417.26 |
| Open BM25 | Utility-only | 0.35 | 0.31 | 0.76 | 0.45 | -0.41 | 0.49 | 0.78 | 0.76 | 857.23 |
| Open BM25 | No risk | 0.43 | 0.39 | 0.80 | 0.41 | -0.37 | 0.55 | 0.84 | 0.80 | 859.50 |
| Open BM25 | No planner | 0.38 | 0.35 | 0.74 | 0.39 | -0.36 | 0.47 | 0.78 | 0.74 | 859.50 |
| Open BM25 | No verifier rejection | 0.43 | 0.39 | 0.80 | 0.41 | -0.37 | 0.58 | 0.84 | 0.80 | 859.50 |
| Open BM25 | No verifier | 0.43 | 0.00 | 0.00 | 0.00 | +0.43 | 0.00 | 0.00 | 0.00 | 859.50 |
| Open BM25 | No support graph | 0.41 | 0.37 | 0.78 | 0.41 | -0.37 | 0.53 | 0.80 | 0.79 | 859.50 |
| Open BM25 | Full EviGraph | 0.43 | 0.39 | 0.80 | 0.41 | -0.37 | 0.55 | 0.84 | 0.80 | 859.50 |
| BM25 + source rerank | Direct RAG | 0.49 | 0.43 | 0.71 | 0.28 | -0.22 | 0.50 | 0.76 | 0.74 | 1311.80 |
| BM25 + source rerank | Top-k Program | 0.53 | 0.48 | 0.76 | 0.28 | -0.24 | 0.56 | 0.82 | 0.79 | 1311.80 |
| BM25 + source rerank | Retrieve-then-program | 0.53 | 0.48 | 0.76 | 0.28 | -0.24 | 0.56 | 0.82 | 0.79 | 1311.80 |
| BM25 + source rerank | Full context | 0.50 | 0.46 | 0.79 | 0.33 | -0.29 | 0.57 | 0.83 | 0.80 | 2577.60 |
| BM25 + source rerank | Utility-only | 0.48 | 0.43 | 0.74 | 0.31 | -0.27 | 0.52 | 0.77 | 0.75 | 1163.78 |
| BM25 + source rerank | No risk | 0.53 | 0.48 | 0.77 | 0.28 | -0.24 | 0.57 | 0.82 | 0.79 | 985.49 |
| BM25 + source rerank | No planner | 0.47 | 0.43 | 0.71 | 0.28 | -0.24 | 0.48 | 0.76 | 0.73 | 985.49 |
| BM25 + source rerank | No verifier rejection | 0.54 | 0.48 | 0.77 | 0.28 | -0.23 | 0.60 | 0.82 | 0.79 | 985.49 |
| BM25 + source rerank | No verifier | 0.54 | 0.00 | 0.00 | 0.00 | +0.54 | 0.00 | 0.00 | 0.00 | 985.49 |
| BM25 + source rerank | No support graph | 0.53 | 0.48 | 0.73 | 0.25 | -0.20 | 0.57 | 0.82 | 0.79 | 985.49 |
| BM25 + source rerank | Full EviGraph | 0.55 | 0.50 | 0.79 | 0.29 | -0.25 | 0.59 | 0.82 | 0.82 | 985.49 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier rejection delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | +0.07 | +0.01 | +0.01 | +0.02 | +0.02 | +0.02 | +0.03 | 0.79 |
| Open BM25 | +0.04 | -0.01 | -0.01 | +0.02 | +0.00 | +0.01 | +0.07 | 0.80 |
| BM25 + source rerank | +0.07 | +0.01 | +0.01 | +0.02 | +0.02 | +0.02 | +0.07 | 0.79 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 34 | 28 | 34 | 22 | 16 | 2 |
| Open BM25 | 47 | 33 | 39 | 27 | 17 | 9 |
| BM25 + source rerank | 33 | 28 | 34 | 23 | 16 | 2 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 4 | 1 | 1 | 2 | 6 | 21 |
| Open BM25 | 4 | 4 | 5 | 6 | 6 | 28 |
| BM25 + source rerank | 3 | 1 | 2 | 1 | 5 | 22 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 1.00 | 0.99 | 0.52 | 0.86 | 1.00 | 0.79 | 0.55 |
| Open BM25 | 1.00 | 0.98 | 0.99 | 0.53 | 0.87 | 1.00 | 0.80 | 0.43 |
| BM25 + source rerank | 1.00 | 1.00 | 0.99 | 0.52 | 0.86 | 1.00 | 0.79 | 0.55 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
