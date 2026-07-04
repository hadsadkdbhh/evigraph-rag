# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_absolute_change_v10` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Full EviGraph | 0.55 | 0.50 | 0.79 | 0.29 | -0.25 | 0.60 | 0.82 | 0.82 | 1178.88 |
| Open BM25 | Full EviGraph | 0.43 | 0.39 | 0.80 | 0.41 | -0.37 | 0.55 | 0.84 | 0.80 | 859.50 |
| BM25 + source rerank | Full EviGraph | 0.55 | 0.50 | 0.79 | 0.29 | -0.25 | 0.59 | 0.82 | 0.82 | 985.49 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 34 | 28 | 34 | 22 | 16 | 2 |
| Open BM25 | 47 | 33 | 39 | 27 | 17 | 9 |
| BM25 + source rerank | 33 | 28 | 34 | 23 | 16 | 2 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 4 | 1 | 1 | 2 | 5 | 22 |
| Open BM25 | 4 | 4 | 5 | 6 | 10 | 25 |
| BM25 + source rerank | 3 | 1 | 2 | 1 | 4 | 23 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 1.00 | 0.99 | 0.52 | 0.86 | 1.00 | 0.79 | 0.55 |
| Open BM25 | 1.00 | 0.98 | 0.99 | 0.53 | 0.87 | 1.00 | 0.80 | 0.43 |
| BM25 + source rerank | 1.00 | 1.00 | 0.99 | 0.52 | 0.86 | 1.00 | 0.79 | 0.55 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
