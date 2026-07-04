# FinQA Paper Assets

Generated from `outputs\eval\finqa_600_local_planner` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Full EviGraph | 0.40 | 0.36 | 0.78 | 0.42 | -0.38 | 0.54 | 0.81 | 0.81 | 1178.44 |
| Open BM25 | Full EviGraph | 0.29 | 0.26 | 0.73 | 0.47 | -0.44 | 0.47 | 0.78 | 0.75 | 870.06 |
| BM25 + source rerank | Full EviGraph | 0.40 | 0.36 | 0.78 | 0.42 | -0.38 | 0.54 | 0.81 | 0.81 | 982.46 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 116 | 60 | 86 | 57 | 35 | 4 |
| Open BM25 | 126 | 68 | 104 | 64 | 43 | 18 |
| BM25 + source rerank | 115 | 62 | 86 | 58 | 35 | 4 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 19 | 11 | 10 | 8 | 27 | 53 |
| Open BM25 | 18 | 15 | 12 | 20 | 21 | 63 |
| BM25 + source rerank | 18 | 11 | 10 | 7 | 26 | 54 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 0.99 | 0.99 | 0.50 | 0.85 | 1.00 | 0.78 | 0.40 |
| Open BM25 | 1.00 | 0.97 | 0.99 | 0.46 | 0.82 | 1.00 | 0.73 | 0.29 |
| BM25 + source rerank | 1.00 | 0.99 | 0.99 | 0.50 | 0.85 | 1.00 | 0.78 | 0.40 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
