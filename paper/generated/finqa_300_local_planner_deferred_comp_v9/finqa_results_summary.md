# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_deferred_comp_v9` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Full EviGraph | 0.54 | 0.49 | 0.78 | 0.29 | -0.24 | 0.60 | 0.81 | 0.81 | 1178.88 |
| Open BM25 | Full EviGraph | 0.42 | 0.38 | 0.79 | 0.40 | -0.36 | 0.55 | 0.82 | 0.79 | 859.50 |
| BM25 + source rerank | Full EviGraph | 0.54 | 0.49 | 0.78 | 0.29 | -0.24 | 0.59 | 0.81 | 0.81 | 985.49 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 36 | 28 | 34 | 22 | 16 | 2 |
| Open BM25 | 48 | 33 | 39 | 27 | 17 | 9 |
| BM25 + source rerank | 35 | 28 | 34 | 23 | 16 | 2 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 4 | 1 | 1 | 2 | 8 | 21 |
| Open BM25 | 4 | 4 | 5 | 6 | 12 | 24 |
| BM25 + source rerank | 3 | 1 | 2 | 1 | 7 | 22 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 1.00 | 0.99 | 0.53 | 0.86 | 1.00 | 0.78 | 0.54 |
| Open BM25 | 1.00 | 0.98 | 0.99 | 0.53 | 0.87 | 1.00 | 0.79 | 0.42 |
| BM25 + source rerank | 1.00 | 1.00 | 0.99 | 0.53 | 0.86 | 1.00 | 0.78 | 0.54 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
