# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_retrieval_baselines` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | Direct RAG | 0.37 | 0.31 | 0.71 | 0.40 | -0.34 | 0.47 | 0.73 | 0.71 | 858.12 |
| Open BM25 | Top-k Program | 0.39 | 0.34 | 0.77 | 0.43 | -0.38 | 0.54 | 0.79 | 0.78 | 858.12 |
| Open BM25 | Retrieve-then-program | 0.39 | 0.34 | 0.77 | 0.43 | -0.38 | 0.54 | 0.79 | 0.78 | 858.12 |
| Open BM25 | Full context | 0.38 | 0.34 | 0.79 | 0.45 | -0.41 | 0.56 | 0.83 | 0.80 | 3417.26 |
| Open BM25 | Utility-only | 0.33 | 0.29 | 0.75 | 0.46 | -0.41 | 0.49 | 0.76 | 0.75 | 857.23 |
| Open BM25 | Full EviGraph | 0.40 | 0.36 | 0.79 | 0.43 | -0.39 | 0.55 | 0.82 | 0.79 | 859.50 |
| Open dense | Direct RAG | 0.10 | 0.07 | 0.44 | 0.37 | -0.34 | 0.13 | 0.48 | 0.47 | 854.53 |
| Open dense | Top-k Program | 0.12 | 0.09 | 0.47 | 0.38 | -0.34 | 0.17 | 0.50 | 0.50 | 854.53 |
| Open dense | Retrieve-then-program | 0.12 | 0.09 | 0.47 | 0.38 | -0.34 | 0.17 | 0.50 | 0.50 | 854.53 |
| Open dense | Full context | 0.16 | 0.13 | 0.57 | 0.44 | -0.41 | 0.26 | 0.60 | 0.58 | 4332.01 |
| Open dense | Utility-only | 0.11 | 0.08 | 0.48 | 0.40 | -0.37 | 0.16 | 0.50 | 0.49 | 844.32 |
| Open dense | Full EviGraph | 0.13 | 0.10 | 0.52 | 0.42 | -0.39 | 0.20 | 0.56 | 0.53 | 849.89 |
| Open hybrid | Direct RAG | 0.37 | 0.31 | 0.71 | 0.40 | -0.34 | 0.47 | 0.73 | 0.71 | 861.57 |
| Open hybrid | Top-k Program | 0.39 | 0.35 | 0.78 | 0.43 | -0.38 | 0.55 | 0.79 | 0.78 | 861.57 |
| Open hybrid | Retrieve-then-program | 0.39 | 0.35 | 0.78 | 0.43 | -0.38 | 0.55 | 0.79 | 0.78 | 861.57 |
| Open hybrid | Full context | 0.39 | 0.35 | 0.79 | 0.44 | -0.40 | 0.56 | 0.84 | 0.80 | 3425.11 |
| Open hybrid | Utility-only | 0.33 | 0.29 | 0.75 | 0.46 | -0.41 | 0.49 | 0.77 | 0.75 | 859.49 |
| Open hybrid | Full EviGraph | 0.40 | 0.36 | 0.79 | 0.43 | -0.39 | 0.55 | 0.82 | 0.79 | 863.71 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier rejection delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.01 | +0.07 | 0.79 |
| Open dense | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.01 | +0.02 | 0.52 |
| Open hybrid | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.01 | +0.07 | 0.79 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 52 | 34 | 39 | 27 | 18 | 9 |
| Open dense | 31 | 49 | 89 | 44 | 38 | 9 |
| Open hybrid | 52 | 34 | 40 | 27 | 18 | 9 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 5 | 4 | 5 | 6 | 11 | 28 |
| Open dense | 3 | 3 | 8 | 5 | 8 | 10 |
| Open hybrid | 6 | 3 | 4 | 6 | 10 | 29 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 1.00 | 0.98 | 0.99 | 0.52 | 0.87 | 1.00 | 0.79 | 0.40 |
| Open dense | 1.00 | 0.74 | 0.89 | 0.21 | 0.58 | 1.00 | 0.52 | 0.13 |
| Open hybrid | 1.00 | 0.99 | 0.99 | 0.52 | 0.87 | 1.00 | 0.79 | 0.40 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
