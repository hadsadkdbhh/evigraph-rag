# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_table_ops_v21` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Full EviGraph | 0.65 | 0.60 | 0.83 | 0.23 | -0.18 | 0.70 | 0.85 | 0.84 | 1178.88 |
| Open BM25 | Full EviGraph | 0.49 | 0.46 | 0.81 | 0.36 | -0.32 | 0.64 | 0.85 | 0.82 | 859.50 |
| BM25 + source rerank | Full EviGraph | 0.65 | 0.60 | 0.83 | 0.23 | -0.18 | 0.70 | 0.85 | 0.84 | 985.49 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 34 | 23 | 24 | 11 | 11 | 2 |
| Open BM25 | 53 | 28 | 31 | 18 | 13 | 9 |
| BM25 + source rerank | 33 | 23 | 24 | 12 | 11 | 2 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 5 | 1 | 1 | 3 | 4 | 21 |
| Open BM25 | 5 | 4 | 5 | 8 | 12 | 27 |
| BM25 + source rerank | 4 | 1 | 2 | 2 | 3 | 22 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 1.00 | 0.99 | 0.61 | 0.89 | 1.00 | 0.83 | 0.65 |
| Open BM25 | 1.00 | 0.98 | 0.99 | 0.59 | 0.90 | 1.00 | 0.81 | 0.49 |
| BM25 + source rerank | 1.00 | 1.00 | 0.99 | 0.61 | 0.89 | 1.00 | 0.83 | 0.65 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
