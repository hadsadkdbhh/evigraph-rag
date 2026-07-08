# FinQA Paper Assets

Generated from `outputs\eval\finqa_300_local_planner_tax_provision_ratio_v34` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | supported EM | answer supported | supported wrong | support gap | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | Full EviGraph | 0.67 | 0.61 | 0.83 | 0.22 | -0.17 | 0.71 | 0.85 | 0.85 | 1178.88 |
| Open BM25 | Full EviGraph | 0.52 | 0.48 | 0.84 | 0.36 | -0.32 | 0.66 | 0.86 | 0.85 | 859.50 |
| BM25 + source rerank | Full EviGraph | 0.67 | 0.61 | 0.83 | 0.22 | -0.17 | 0.71 | 0.85 | 0.85 | 985.49 |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 30 | 23 | 23 | 11 | 11 | 2 |
| Open BM25 | 41 | 28 | 31 | 18 | 12 | 4 |
| BM25 + source rerank | 29 | 23 | 23 | 12 | 11 | 2 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 0 | 0 | 1 | 2 | 5 | 22 |
| Open BM25 | 0 | 0 | 3 | 7 | 9 | 35 |
| BM25 + source rerank | 0 | 0 | 1 | 2 | 4 | 22 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 1.00 | 0.85 | 0.97 | 0.85 | 1.00 | 0.83 | 0.67 |
| Open BM25 | 1.00 | 1.00 | 0.85 | 0.97 | 0.86 | 1.00 | 0.84 | 0.52 |
| BM25 + source rerank | 1.00 | 1.00 | 0.85 | 0.97 | 0.85 | 1.00 | 0.83 | 0.67 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
