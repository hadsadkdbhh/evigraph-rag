# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_strong_retrieval_baselines_v21` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | Direct RAG | 0.45 | 0.39 | 0.74 | 0.35 | -0.29 | 0.55 | 0.76 | 0.74 | 858.12 |
| Open BM25 | Top-k Program | 0.47 | 0.43 | 0.80 | 0.37 | -0.33 | 0.62 | 0.83 | 0.81 | 858.12 |
| Open BM25 | Retrieve-then-program | 0.47 | 0.43 | 0.80 | 0.37 | -0.33 | 0.62 | 0.83 | 0.81 | 858.12 |
| Open BM25 | Full context | 0.48 | 0.44 | 0.82 | 0.38 | -0.34 | 0.65 | 0.86 | 0.83 | 3417.26 |
| Open BM25 | Utility-only | 0.39 | 0.35 | 0.76 | 0.41 | -0.37 | 0.55 | 0.78 | 0.77 | 857.23 |
| Open BM25 | Full EviGraph | 0.49 | 0.46 | 0.81 | 0.36 | -0.32 | 0.64 | 0.85 | 0.82 | 859.50 |
| Open TF-IDF | Direct RAG | 0.42 | 0.37 | 0.69 | 0.32 | -0.27 | 0.49 | 0.71 | 0.70 | 806.08 |
| Open TF-IDF | Top-k Program | 0.45 | 0.41 | 0.74 | 0.33 | -0.29 | 0.53 | 0.76 | 0.74 | 806.08 |
| Open TF-IDF | Retrieve-then-program | 0.45 | 0.41 | 0.74 | 0.33 | -0.29 | 0.53 | 0.76 | 0.74 | 806.08 |
| Open TF-IDF | Full context | 0.48 | 0.44 | 0.78 | 0.34 | -0.29 | 0.61 | 0.83 | 0.78 | 3298.74 |
| Open TF-IDF | Utility-only | 0.37 | 0.33 | 0.69 | 0.36 | -0.32 | 0.47 | 0.71 | 0.69 | 806.57 |
| Open TF-IDF | Full EviGraph | 0.47 | 0.42 | 0.74 | 0.32 | -0.27 | 0.55 | 0.78 | 0.75 | 810.77 |
| Open hybrid | Direct RAG | 0.44 | 0.39 | 0.74 | 0.35 | -0.30 | 0.55 | 0.76 | 0.75 | 861.57 |
| Open hybrid | Top-k Program | 0.47 | 0.43 | 0.80 | 0.37 | -0.33 | 0.63 | 0.83 | 0.81 | 861.57 |
| Open hybrid | Retrieve-then-program | 0.47 | 0.43 | 0.80 | 0.37 | -0.33 | 0.63 | 0.83 | 0.81 | 861.57 |
| Open hybrid | Full context | 0.48 | 0.45 | 0.82 | 0.37 | -0.34 | 0.65 | 0.87 | 0.83 | 3425.11 |
| Open hybrid | Utility-only | 0.39 | 0.36 | 0.76 | 0.41 | -0.37 | 0.55 | 0.79 | 0.77 | 859.49 |
| Open hybrid | Full EviGraph | 0.49 | 0.46 | 0.81 | 0.36 | -0.32 | 0.63 | 0.85 | 0.82 | 863.71 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier rejection delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.02 | +0.10 | 0.81 |
| Open TF-IDF | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.02 | +0.10 | 0.74 |
| Open hybrid | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.02 | +0.10 | 0.81 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 53 | 28 | 31 | 18 | 13 | 9 |
| Open TF-IDF | 36 | 32 | 49 | 22 | 12 | 9 |
| Open hybrid | 52 | 28 | 32 | 18 | 13 | 9 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 5 | 4 | 5 | 8 | 12 | 27 |
| Open TF-IDF | 4 | 3 | 5 | 6 | 6 | 18 |
| Open hybrid | 6 | 3 | 4 | 8 | 11 | 27 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 1.00 | 0.98 | 0.99 | 0.59 | 0.90 | 1.00 | 0.81 | 0.49 |
| Open TF-IDF | 1.00 | 0.95 | 0.98 | 0.52 | 0.82 | 1.00 | 0.74 | 0.47 |
| Open hybrid | 1.00 | 0.99 | 0.99 | 0.59 | 0.90 | 1.00 | 0.81 | 0.49 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
