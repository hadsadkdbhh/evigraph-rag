# FinQA Paper Assets

Generated from `outputs\eval\finqa_600_local_planner_table_ops_v21` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Full EviGraph | 0.47 | 0.43 | 0.80 | 0.37 | -0.33 | 0.60 | 0.83 | 0.83 | 1179.61 |
| Open BM25 | Full EviGraph | 0.34 | 0.30 | 0.73 | 0.43 | -0.40 | 0.51 | 0.79 | 0.76 | 870.06 |
| BM25 + source rerank | Full EviGraph | 0.47 | 0.43 | 0.80 | 0.37 | -0.33 | 0.60 | 0.83 | 0.83 | 983.63 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 114 | 54 | 68 | 46 | 28 | 5 |
| Open BM25 | 133 | 62 | 94 | 55 | 37 | 16 |
| BM25 + source rerank | 113 | 55 | 68 | 47 | 28 | 5 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 21 | 13 | 9 | 12 | 23 | 49 |
| Open BM25 | 19 | 15 | 12 | 26 | 22 | 64 |
| BM25 + source rerank | 20 | 13 | 9 | 11 | 22 | 50 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 0.99 | 0.99 | 0.56 | 0.87 | 1.00 | 0.80 | 0.47 |
| Open BM25 | 1.00 | 0.97 | 0.99 | 0.50 | 0.83 | 1.00 | 0.73 | 0.34 |
| BM25 + source rerank | 1.00 | 0.99 | 0.99 | 0.56 | 0.87 | 1.00 | 0.80 | 0.47 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
