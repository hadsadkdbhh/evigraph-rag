# FinQA Paper Assets

Generated from `outputs\eval\finqa_600_neural_retrieval_baselines_v21` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | Direct RAG | 0.30 | 0.26 | 0.65 | 0.40 | -0.35 | 0.42 | 0.70 | 0.68 | 865.73 |
| Open BM25 | Retrieve-then-program | 0.33 | 0.29 | 0.71 | 0.42 | -0.38 | 0.48 | 0.76 | 0.74 | 865.73 |
| Open BM25 | Full EviGraph | 0.34 | 0.30 | 0.73 | 0.43 | -0.40 | 0.51 | 0.79 | 0.76 | 870.06 |
| Open neural dense | Direct RAG | 0.23 | 0.17 | 0.56 | 0.38 | -0.33 | 0.28 | 0.60 | 0.60 | 822.37 |
| Open neural dense | Retrieve-then-program | 0.24 | 0.19 | 0.60 | 0.42 | -0.37 | 0.34 | 0.65 | 0.64 | 822.37 |
| Open neural dense | Full EviGraph | 0.25 | 0.21 | 0.67 | 0.46 | -0.41 | 0.40 | 0.70 | 0.68 | 830.49 |
| Open neural hybrid | Direct RAG | 0.32 | 0.27 | 0.67 | 0.40 | -0.35 | 0.43 | 0.72 | 0.71 | 873.10 |
| Open neural hybrid | Retrieve-then-program | 0.34 | 0.29 | 0.72 | 0.43 | -0.38 | 0.50 | 0.78 | 0.76 | 873.10 |
| Open neural hybrid | Full EviGraph | 0.33 | 0.29 | 0.75 | 0.46 | -0.42 | 0.52 | 0.79 | 0.77 | 879.12 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 133 | 62 | 94 | 55 | 37 | 16 |
| Open neural dense | 115 | 80 | 127 | 72 | 43 | 12 |
| Open neural hybrid | 143 | 61 | 92 | 56 | 37 | 14 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 19 | 15 | 12 | 26 | 22 | 64 |
| Open neural dense | 17 | 15 | 13 | 20 | 24 | 49 |
| Open neural hybrid | 19 | 16 | 8 | 24 | 22 | 77 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Open BM25 | 1.00 | 0.97 | 0.99 | 0.50 | 0.83 | 1.00 | 0.73 | 0.34 |
| Open neural dense | 1.00 | 0.88 | 0.97 | 0.38 | 0.74 | 1.00 | 0.67 | 0.25 |
| Open neural hybrid | 1.00 | 0.99 | 1.00 | 0.49 | 0.82 | 1.00 | 0.75 | 0.33 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
