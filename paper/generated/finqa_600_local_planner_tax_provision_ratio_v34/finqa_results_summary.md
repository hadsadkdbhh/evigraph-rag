# FinQA Paper Assets

Generated from `outputs\eval\finqa_600_local_planner_tax_provision_ratio_v34` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Full EviGraph | 0.49 | 0.45 | 0.81 | 0.36 | -0.32 | 0.61 | 0.84 | 0.83 | 1179.61 |
| Open BM25 | Full EviGraph | 0.36 | 0.33 | 0.76 | 0.43 | -0.39 | 0.54 | 0.80 | 0.78 | 870.06 |
| BM25 + source rerank | Full EviGraph | 0.49 | 0.45 | 0.81 | 0.36 | -0.32 | 0.61 | 0.84 | 0.83 | 983.63 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 101 | 54 | 65 | 46 | 27 | 5 |
| Open BM25 | 104 | 62 | 90 | 55 | 36 | 8 |
| BM25 + source rerank | 101 | 55 | 65 | 47 | 27 | 5 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 0 | 0 | 8 | 9 | 21 | 71 |
| Open BM25 | 0 | 0 | 12 | 23 | 19 | 81 |
| BM25 + source rerank | 0 | 0 | 7 | 9 | 20 | 72 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 1.00 | 0.83 | 0.97 | 0.84 | 1.00 | 0.81 | 0.49 |
| Open BM25 | 1.00 | 1.00 | 0.78 | 0.97 | 0.80 | 1.00 | 0.76 | 0.36 |
| BM25 + source rerank | 1.00 | 1.00 | 0.83 | 0.97 | 0.84 | 1.00 | 0.81 | 0.49 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
