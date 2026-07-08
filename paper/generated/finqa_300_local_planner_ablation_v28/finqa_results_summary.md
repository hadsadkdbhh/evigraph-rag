# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_ablation_v28` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Direct RAG | 0.59 | 0.53 | 0.75 | 0.22 | -0.16 | 0.62 | 0.79 | 0.77 | 1414.75 |
| Oracle-doc | Top-k Program | 0.64 | 0.59 | 0.81 | 0.22 | -0.17 | 0.69 | 0.85 | 0.82 | 1414.75 |
| Oracle-doc | Retrieve-then-program | 0.64 | 0.59 | 0.81 | 0.22 | -0.17 | 0.69 | 0.85 | 0.82 | 1414.75 |
| Oracle-doc | Full context | 0.64 | 0.59 | 0.81 | 0.22 | -0.17 | 0.69 | 0.85 | 0.82 | 1666.70 |
| Oracle-doc | Utility-only | 0.63 | 0.57 | 0.80 | 0.23 | -0.18 | 0.66 | 0.84 | 0.82 | 1265.82 |
| Oracle-doc | No risk | 0.64 | 0.59 | 0.81 | 0.22 | -0.17 | 0.69 | 0.85 | 0.82 | 1178.88 |
| Oracle-doc | No planner | 0.59 | 0.53 | 0.75 | 0.22 | -0.17 | 0.60 | 0.79 | 0.77 | 1178.88 |
| Oracle-doc | No verifier rejection | 0.65 | 0.59 | 0.81 | 0.22 | -0.16 | 0.72 | 0.85 | 0.82 | 1178.88 |
| Oracle-doc | No verifier | 0.65 | 0.00 | 0.00 | 0.00 | +0.65 | 0.00 | 0.00 | 0.00 | 1178.88 |
| Oracle-doc | No support graph | 0.64 | 0.58 | 0.81 | 0.22 | -0.17 | 0.69 | 0.85 | 0.82 | 1178.88 |
| Oracle-doc | Full EviGraph | 0.66 | 0.61 | 0.83 | 0.23 | -0.17 | 0.71 | 0.85 | 0.85 | 1178.88 |
| Open BM25 | Direct RAG | 0.45 | 0.40 | 0.74 | 0.34 | -0.29 | 0.56 | 0.77 | 0.75 | 858.12 |
| Open BM25 | Top-k Program | 0.48 | 0.44 | 0.80 | 0.36 | -0.32 | 0.63 | 0.83 | 0.81 | 858.12 |
| Open BM25 | Retrieve-then-program | 0.48 | 0.44 | 0.80 | 0.36 | -0.32 | 0.63 | 0.83 | 0.81 | 858.12 |
| Open BM25 | Full context | 0.49 | 0.45 | 0.83 | 0.37 | -0.34 | 0.66 | 0.87 | 0.83 | 3417.26 |
| Open BM25 | Utility-only | 0.40 | 0.36 | 0.77 | 0.40 | -0.37 | 0.56 | 0.79 | 0.77 | 857.23 |
| Open BM25 | No risk | 0.50 | 0.47 | 0.82 | 0.35 | -0.31 | 0.65 | 0.86 | 0.82 | 859.50 |
| Open BM25 | No planner | 0.46 | 0.42 | 0.76 | 0.34 | -0.30 | 0.57 | 0.80 | 0.77 | 859.50 |
| Open BM25 | No verifier rejection | 0.51 | 0.47 | 0.82 | 0.35 | -0.31 | 0.68 | 0.86 | 0.82 | 859.50 |
| Open BM25 | No verifier | 0.51 | 0.00 | 0.00 | 0.00 | +0.51 | 0.00 | 0.00 | 0.00 | 859.50 |
| Open BM25 | No support graph | 0.47 | 0.43 | 0.79 | 0.36 | -0.32 | 0.62 | 0.82 | 0.80 | 859.50 |
| Open BM25 | Full EviGraph | 0.52 | 0.48 | 0.84 | 0.36 | -0.32 | 0.66 | 0.86 | 0.85 | 859.50 |
| BM25 + source rerank | Direct RAG | 0.59 | 0.53 | 0.75 | 0.22 | -0.16 | 0.62 | 0.79 | 0.77 | 1311.80 |
| BM25 + source rerank | Top-k Program | 0.64 | 0.59 | 0.80 | 0.22 | -0.16 | 0.68 | 0.84 | 0.82 | 1311.80 |
| BM25 + source rerank | Retrieve-then-program | 0.64 | 0.59 | 0.80 | 0.22 | -0.16 | 0.68 | 0.84 | 0.82 | 1311.80 |
| BM25 + source rerank | Full context | 0.62 | 0.57 | 0.82 | 0.25 | -0.20 | 0.69 | 0.86 | 0.83 | 2577.60 |
| BM25 + source rerank | Utility-only | 0.56 | 0.50 | 0.75 | 0.25 | -0.20 | 0.60 | 0.79 | 0.77 | 1163.78 |
| BM25 + source rerank | No risk | 0.64 | 0.59 | 0.81 | 0.22 | -0.17 | 0.69 | 0.85 | 0.82 | 985.49 |
| BM25 + source rerank | No planner | 0.58 | 0.53 | 0.75 | 0.22 | -0.17 | 0.60 | 0.79 | 0.77 | 985.49 |
| BM25 + source rerank | No verifier rejection | 0.65 | 0.59 | 0.81 | 0.22 | -0.16 | 0.71 | 0.85 | 0.82 | 985.49 |
| BM25 + source rerank | No verifier | 0.65 | 0.00 | 0.00 | 0.00 | +0.65 | 0.00 | 0.00 | 0.00 | 985.49 |
| BM25 + source rerank | No support graph | 0.64 | 0.59 | 0.78 | 0.19 | -0.14 | 0.69 | 0.84 | 0.82 | 985.49 |
| BM25 + source rerank | Full EviGraph | 0.66 | 0.61 | 0.83 | 0.23 | -0.17 | 0.71 | 0.85 | 0.85 | 985.49 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier rejection delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | +0.07 | +0.01 | +0.01 | +0.02 | +0.02 | +0.02 | +0.03 | 0.83 |
| Open BM25 | +0.06 | +0.01 | +0.01 | +0.04 | +0.01 | +0.03 | +0.12 | 0.84 |
| BM25 + source rerank | +0.08 | +0.01 | +0.01 | +0.02 | +0.02 | +0.02 | +0.10 | 0.83 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 32 | 23 | 23 | 11 | 11 | 2 |
| Open BM25 | 42 | 28 | 31 | 18 | 12 | 4 |
| BM25 + source rerank | 31 | 23 | 23 | 12 | 11 | 2 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 0 | 0 | 0 | 0 | 0 | 32 |
| Open BM25 | 0 | 0 | 0 | 0 | 0 | 52 |
| BM25 + source rerank | 0 | 0 | 0 | 0 | 0 | 31 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 1.00 | 0.85 | 0.97 | 0.85 | 1.00 | 0.83 | 0.66 |
| Open BM25 | 1.00 | 1.00 | 0.85 | 0.97 | 0.86 | 1.00 | 0.84 | 0.52 |
| BM25 + source rerank | 1.00 | 1.00 | 0.85 | 0.97 | 0.85 | 1.00 | 0.83 | 0.66 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
