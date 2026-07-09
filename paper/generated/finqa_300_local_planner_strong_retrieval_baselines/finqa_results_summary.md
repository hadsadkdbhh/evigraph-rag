# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_strong_retrieval_baselines` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | Direct RAG | 0.37 | 0.31 | 0.71 | 0.40 | -0.34 | 0.47 | 0.73 | 0.71 | 858.12 |
| Open BM25 | Top-k Program | 0.39 | 0.34 | 0.77 | 0.43 | -0.38 | 0.54 | 0.79 | 0.78 | 858.12 |
| Open BM25 | Retrieve-then-program | 0.39 | 0.34 | 0.77 | 0.43 | -0.38 | 0.54 | 0.79 | 0.78 | 858.12 |
| Open BM25 | Full context | 0.38 | 0.34 | 0.79 | 0.45 | -0.41 | 0.56 | 0.83 | 0.80 | 3417.26 |
| Open BM25 | Utility-only | 0.33 | 0.29 | 0.75 | 0.46 | -0.41 | 0.49 | 0.76 | 0.75 | 857.23 |
| Open BM25 | Full EviGraph | 0.40 | 0.36 | 0.79 | 0.43 | -0.39 | 0.55 | 0.82 | 0.79 | 859.50 |
| Open TF-IDF | Direct RAG | 0.35 | 0.30 | 0.67 | 0.37 | -0.31 | 0.42 | 0.68 | 0.67 | 806.08 |
| Open TF-IDF | Top-k Program | 0.38 | 0.33 | 0.72 | 0.38 | -0.34 | 0.47 | 0.73 | 0.72 | 806.08 |
| Open TF-IDF | Retrieve-then-program | 0.38 | 0.33 | 0.72 | 0.38 | -0.34 | 0.47 | 0.73 | 0.72 | 806.08 |
| Open TF-IDF | Full context | 0.38 | 0.34 | 0.75 | 0.41 | -0.37 | 0.53 | 0.79 | 0.76 | 3298.74 |
| Open TF-IDF | Utility-only | 0.31 | 0.27 | 0.67 | 0.40 | -0.36 | 0.42 | 0.69 | 0.68 | 806.57 |
| Open TF-IDF | Full EviGraph | 0.38 | 0.34 | 0.72 | 0.38 | -0.34 | 0.48 | 0.76 | 0.73 | 810.77 |
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
| Open TF-IDF | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.07 | 0.72 |
| Open hybrid | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.01 | +0.07 | 0.79 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 52 | 34 | 39 | 27 | 18 | 9 |
| Open TF-IDF | 38 | 37 | 54 | 30 | 17 | 10 |
| Open hybrid | 52 | 34 | 40 | 27 | 18 | 9 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 5 | 4 | 5 | 6 | 7 | 31 |
| Open TF-IDF | 4 | 3 | 4 | 5 | 6 | 22 |
| Open hybrid | 6 | 3 | 4 | 6 | 5 | 33 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 1.00 | 0.98 | 0.99 | 0.52 | 0.87 | 1.00 | 0.79 | 0.40 |
| Open TF-IDF | 1.00 | 0.95 | 0.98 | 0.46 | 0.80 | 1.00 | 0.72 | 0.38 |
| Open hybrid | 1.00 | 0.99 | 0.99 | 0.52 | 0.87 | 1.00 | 0.79 | 0.40 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
