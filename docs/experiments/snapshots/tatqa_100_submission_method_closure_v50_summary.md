# TAT-QA-100 Submission Method Closure v50

## tatqa_100_oracle_doc_method_closure_v50.csv

- Rows: 500
- Grouping: `dataset, method`

| dataset | method | n | accuracy | answer_supported | supported_accuracy | unsupported_correct | supported_wrong | answer_support_gap | arithmetically_supported | calculation_supported | operation_semantics_checked | operand_semantics_checked | row_operation_grounded | semantically_grounded | citation_correct | source_consistent | misleading_acceptance | input_tokens | tool_calls | latency_ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| tatqa_100 | direct_rag | 100 | 0.49 | 0.69 | 0.41 | 0.08 | 0.28 | -0.2 | 0.99 | 0.58 | 0.71 | 0.98 | 0.69 | 0.69 | 1 | 1 | 0 | 690.5 | 1 | 49.8 |
| tatqa_100 | evigraph_wo_operation_planner | 100 | 0.48 | 0.69 | 0.41 | 0.07 | 0.28 | -0.21 | 0.99 | 0.56 | 0.71 | 0.98 | 0.69 | 0.69 | 1 | 1 | 0 | 572.79 | 1.39 | 56.3 |
| tatqa_100 | full_evigraph | 100 | 0.52 | 0.75 | 0.46 | 0.06 | 0.29 | -0.23 | 0.99 | 0.63 | 0.77 | 0.98 | 0.75 | 0.75 | 1 | 1 | 0 | 572.79 | 1.39 | 56.4 |
| tatqa_100 | retrieve_then_program | 100 | 0.52 | 0.74 | 0.45 | 0.07 | 0.29 | -0.22 | 0.99 | 0.63 | 0.76 | 0.98 | 0.74 | 0.74 | 1 | 1 | 0 | 690.5 | 1 | 49.8 |
| tatqa_100 | utility_only | 100 | 0.52 | 0.74 | 0.45 | 0.07 | 0.29 | -0.22 | 0.99 | 0.63 | 0.76 | 0.98 | 0.74 | 0.74 | 1 | 1 | 0 | 653.57 | 1 | 49.8 |

## tatqa_100_open_bm25_method_closure_v50.csv

- Rows: 500
- Grouping: `dataset, method`

| dataset | method | n | accuracy | answer_supported | supported_accuracy | unsupported_correct | supported_wrong | answer_support_gap | arithmetically_supported | calculation_supported | operation_semantics_checked | operand_semantics_checked | row_operation_grounded | semantically_grounded | citation_correct | source_consistent | misleading_acceptance | input_tokens | tool_calls | latency_ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| tatqa_100 | direct_rag | 100 | 0.4 | 0.74 | 0.34 | 0.06 | 0.4 | -0.34 | 1 | 0.63 | 0.76 | 0.97 | 0.74 | 0.74 | 1 | 0.9 | 0 | 729.6 | 1 | 60 |
| tatqa_100 | evigraph_wo_operation_planner | 100 | 0.35 | 0.75 | 0.31 | 0.04 | 0.44 | -0.4 | 1 | 0.62 | 0.78 | 0.95 | 0.75 | 0.75 | 1 | 0.79 | 0 | 728.99 | 1.29 | 68.7 |
| tatqa_100 | full_evigraph | 100 | 0.41 | 0.85 | 0.39 | 0.02 | 0.46 | -0.44 | 1 | 0.73 | 0.85 | 0.97 | 0.85 | 0.85 | 1 | 0.97 | 0 | 728.99 | 1.29 | 73.7 |
| tatqa_100 | retrieve_then_program | 100 | 0.44 | 0.8 | 0.39 | 0.05 | 0.41 | -0.36 | 1 | 0.7 | 0.82 | 0.97 | 0.8 | 0.8 | 1 | 0.91 | 0 | 729.6 | 1 | 60 |
| tatqa_100 | utility_only | 100 | 0.42 | 0.79 | 0.38 | 0.04 | 0.41 | -0.37 | 1 | 0.67 | 0.81 | 0.97 | 0.79 | 0.79 | 1 | 0.89 | 0 | 720.05 | 1 | 59.95 |
