# FinQA Paper Assets

Generated from `outputs\eval\paper_anchor` after the latest manifest run.

## Main Diagnostic Table

| setting | method | EM | answer supported | calculation supported | operation semantics | row grounded | tokens |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | LLM Direct RAG | 0.69 | 0.34 | 0.92 | 0.38 | 0.38 | 1414.75 |
| Open BM25 | LLM Direct RAG | 0.52 | 0.27 | 0.79 | 0.38 | 0.38 | 858.12 |
| BM25 + source rerank | LLM Direct RAG | 0.69 | 0.34 | 0.92 | 0.38 | 0.38 | 1311.80 |

## Component Contribution Diagnostics

| setting | planner delta EM | verifier rejection delta EM | verifier delta EM | support delta EM | risk delta EM | graph vs top-k EM | graph vs utility-only EM | full answer support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |

## Full EviGraph Failure Categories

| setting | wrong row/op | no numeric | no percent | additive/lookup | ratio | unsupported |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 82 | 0 | 0 | 0 | 0 | 10 |
| Open BM25 | 95 | 0 | 0 | 0 | 0 | 48 |
| BM25 + source rerank | 78 | 0 | 0 | 0 | 0 | 15 |

## Row/Operation Diagnostics

| setting | wrong numerator | wrong denominator | wrong year/period | wrong row label | wrong operation type | ambiguous |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 0 | 0 | 1 | 0 | 9 | 72 |
| Open BM25 | 0 | 0 | 1 | 0 | 4 | 90 |
| BM25 + source rerank | 0 | 0 | 1 | 0 | 7 | 70 |

## Process Trace Diagnostics

| setting | evidence | period | row | operand | operation | citation | support | EM |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Oracle-doc | 1.00 | 1.00 | 0.99 | 0.89 | 0.94 | 1.00 | 0.34 | 0.69 |
| Open BM25 | 1.00 | 0.98 | 0.99 | 0.78 | 0.89 | 1.00 | 0.27 | 0.52 |
| BM25 + source rerank | 1.00 | 0.99 | 0.99 | 0.87 | 0.94 | 1.00 | 0.34 | 0.69 |

## Paper-Safe Claims

- Treat these as diagnostic smoke-subset results, not final benchmark claims.
- Report open retrieval settings separately from oracle-doc and source-rerank settings.
- Use the failure-category table to justify the next row/operation-selection iteration.
