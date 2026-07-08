# FinQA Paper Assets

Generated from `outputs\eval\finqa_600_local_planner_strong_retrieval_baselines_v21` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | Direct RAG | 0.30 | 0.26 | 0.65 | 0.40 | -0.35 | 0.42 | 0.70 | 0.68 | 865.73 |
| Open BM25 | Top-k Program | 0.33 | 0.29 | 0.71 | 0.42 | -0.38 | 0.48 | 0.76 | 0.74 | 865.73 |
| Open BM25 | Retrieve-then-program | 0.33 | 0.29 | 0.71 | 0.42 | -0.38 | 0.48 | 0.76 | 0.74 | 865.73 |
| Open BM25 | Full context | 0.34 | 0.30 | 0.77 | 0.47 | -0.43 | 0.56 | 0.82 | 0.80 | 3530.20 |
| Open BM25 | Utility-only | 0.30 | 0.26 | 0.69 | 0.43 | -0.39 | 0.43 | 0.72 | 0.70 | 856.75 |
| Open BM25 | Full EviGraph | 0.34 | 0.30 | 0.73 | 0.43 | -0.40 | 0.51 | 0.79 | 0.76 | 870.06 |
| Open TF-IDF | Direct RAG | 0.29 | 0.23 | 0.61 | 0.38 | -0.32 | 0.36 | 0.67 | 0.65 | 801.78 |
| Open TF-IDF | Top-k Program | 0.30 | 0.26 | 0.67 | 0.41 | -0.37 | 0.42 | 0.73 | 0.70 | 801.78 |
| Open TF-IDF | Retrieve-then-program | 0.30 | 0.26 | 0.67 | 0.41 | -0.37 | 0.42 | 0.73 | 0.70 | 801.78 |
| Open TF-IDF | Full context | 0.34 | 0.30 | 0.75 | 0.45 | -0.41 | 0.53 | 0.80 | 0.77 | 3446.09 |
| Open TF-IDF | Utility-only | 0.28 | 0.23 | 0.65 | 0.42 | -0.38 | 0.37 | 0.68 | 0.67 | 810.54 |
| Open TF-IDF | Full EviGraph | 0.32 | 0.28 | 0.71 | 0.43 | -0.39 | 0.47 | 0.77 | 0.74 | 818.58 |
| Open hybrid | Direct RAG | 0.30 | 0.26 | 0.66 | 0.41 | -0.36 | 0.43 | 0.71 | 0.69 | 869.11 |
| Open hybrid | Top-k Program | 0.33 | 0.29 | 0.71 | 0.42 | -0.39 | 0.49 | 0.77 | 0.75 | 869.11 |
| Open hybrid | Retrieve-then-program | 0.33 | 0.29 | 0.71 | 0.42 | -0.39 | 0.49 | 0.77 | 0.75 | 869.11 |
| Open hybrid | Full context | 0.34 | 0.30 | 0.77 | 0.47 | -0.43 | 0.55 | 0.82 | 0.79 | 3529.45 |
| Open hybrid | Utility-only | 0.30 | 0.26 | 0.69 | 0.43 | -0.39 | 0.44 | 0.73 | 0.71 | 860.07 |
| Open hybrid | Full EviGraph | 0.34 | 0.30 | 0.74 | 0.44 | -0.40 | 0.51 | 0.79 | 0.76 | 873.80 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier rejection delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.01 | +0.04 | 0.73 |
| Open TF-IDF | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.02 | +0.05 | 0.71 |
| Open hybrid | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.01 | +0.03 | 0.74 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 133 | 62 | 94 | 55 | 37 | 16 |
| Open TF-IDF | 109 | 69 | 107 | 65 | 43 | 14 |
| Open hybrid | 133 | 63 | 96 | 53 | 36 | 17 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 19 | 15 | 12 | 26 | 22 | 64 |
| Open TF-IDF | 18 | 9 | 19 | 19 | 19 | 44 |
| Open hybrid | 20 | 16 | 9 | 26 | 23 | 65 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 1.00 | 0.97 | 0.99 | 0.50 | 0.83 | 1.00 | 0.73 | 0.34 |
| Open TF-IDF | 1.00 | 0.93 | 0.98 | 0.45 | 0.80 | 1.00 | 0.71 | 0.32 |
| Open hybrid | 1.00 | 0.98 | 1.00 | 0.50 | 0.83 | 1.00 | 0.74 | 0.34 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
