# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_neural_retrieval_baselines` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | Direct RAG | 0.37 | 0.70 | 0.47 | 0.73 | 0.71 | 858.12 |
| Open BM25 | Retrieve-then-program | 0.40 | 0.77 | 0.54 | 0.79 | 0.77 | 858.12 |
| Open BM25 | Full EviGraph | 0.41 | 0.79 | 0.55 | 0.82 | 0.79 | 859.50 |
| Open neural dense | Direct RAG | 0.28 | 0.62 | 0.34 | 0.63 | 0.63 | 823.74 |
| Open neural dense | Retrieve-then-program | 0.30 | 0.67 | 0.41 | 0.68 | 0.68 | 823.74 |
| Open neural dense | Full EviGraph | 0.30 | 0.69 | 0.43 | 0.72 | 0.70 | 830.65 |
| Open neural hybrid | Direct RAG | 0.38 | 0.71 | 0.47 | 0.73 | 0.72 | 865.37 |
| Open neural hybrid | Retrieve-then-program | 0.41 | 0.78 | 0.56 | 0.79 | 0.78 | 865.37 |
| Open neural hybrid | Full EviGraph | 0.41 | 0.78 | 0.55 | 0.80 | 0.79 | 870.59 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier rejection delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0.79 |
| Open neural dense | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0.69 |
| Open neural hybrid | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | +0.00 | 0.78 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 51 | 34 | 39 | 27 | 18 | 9 |
| Open neural dense | 47 | 43 | 55 | 31 | 26 | 7 |
| Open neural hybrid | 54 | 34 | 38 | 25 | 20 | 5 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 5 | 4 | 5 | 6 | 13 | 25 |
| Open neural dense | 5 | 6 | 4 | 4 | 8 | 27 |
| Open neural hybrid | 5 | 4 | 5 | 4 | 10 | 31 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 1.00 | 0.98 | 0.99 | 0.52 | 0.87 | 1.00 | 0.79 | 0.41 |
| Open neural dense | 1.00 | 0.91 | 0.97 | 0.40 | 0.76 | 1.00 | 0.69 | 0.30 |
| Open neural hybrid | 1.00 | 1.00 | 1.00 | 0.50 | 0.85 | 1.00 | 0.78 | 0.41 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
