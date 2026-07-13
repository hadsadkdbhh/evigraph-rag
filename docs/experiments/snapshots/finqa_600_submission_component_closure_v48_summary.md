# EviGraph FinQA-600 Submission Component Closure v48

## finqa_600_subset_oracle_doc_component_closure_v48.csv

- Rows: 4800
- Grouping: `dataset, method`

| dataset | method | n | accuracy | answer_supported | supported_accuracy | unsupported_correct | supported_wrong | answer_support_gap | arithmetically_supported | calculation_supported | operation_semantics_checked | operand_semantics_checked | row_operation_grounded | semantically_grounded | citation_correct | source_consistent | misleading_acceptance | input_tokens | tool_calls | latency_ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finqa_600_subset | direct_rag | 600 | 0.46 | 0.747 | 0.405 | 0.055 | 0.342 | -0.287 | 0.972 | 0.527 | 0.792 | 0.967 | 0.767 | 0.767 | 1 | 1 | 0 | 1416.208 | 1 | 58.7 |
| finqa_600_subset | evigraph_wo_operation_planner | 600 | 0.445 | 0.748 | 0.405 | 0.04 | 0.343 | -0.303 | 0.972 | 0.502 | 0.793 | 0.967 | 0.768 | 0.768 | 1 | 1 | 0 | 1179.613 | 2.472 | 90.575 |
| finqa_600_subset | evigraph_wo_risk | 600 | 0.485 | 0.798 | 0.448 | 0.037 | 0.35 | -0.313 | 0.97 | 0.598 | 0.845 | 0.963 | 0.82 | 0.82 | 1 | 1 | 0 | 1179.613 | 2.472 | 90.575 |
| finqa_600_subset | evigraph_wo_support | 600 | 0.487 | 0.798 | 0.45 | 0.037 | 0.348 | -0.312 | 0.97 | 0.598 | 0.845 | 0.963 | 0.82 | 0.82 | 1 | 1 | 0 | 1179.613 | 2.472 | 90.575 |
| finqa_600_subset | evigraph_wo_verifier | 600 | 0.5 | 0 | 0 | 0.5 | 0 | 0.5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1179.613 | 1.472 | 70.575 |
| finqa_600_subset | full_evigraph | 600 | 0.503 | 0.82 | 0.467 | 0.037 | 0.353 | -0.317 | 0.97 | 0.617 | 0.848 | 0.97 | 0.842 | 0.842 | 1 | 1 | 0 | 1179.613 | 2.472 | 90.842 |
| finqa_600_subset | retrieve_then_program | 600 | 0.485 | 0.797 | 0.448 | 0.037 | 0.348 | -0.312 | 0.97 | 0.598 | 0.843 | 0.963 | 0.818 | 0.818 | 1 | 1 | 0 | 1416.208 | 1 | 58.7 |
| finqa_600_subset | utility_only | 600 | 0.478 | 0.793 | 0.442 | 0.037 | 0.352 | -0.315 | 0.97 | 0.58 | 0.835 | 0.968 | 0.815 | 0.815 | 1 | 1 | 0 | 1290.823 | 1 | 58.7 |

## finqa_600_subset_open_bm25_component_closure_v48.csv

- Rows: 4800
- Grouping: `dataset, method`

| dataset | method | n | accuracy | answer_supported | supported_accuracy | unsupported_correct | supported_wrong | answer_support_gap | arithmetically_supported | calculation_supported | operation_semantics_checked | operand_semantics_checked | row_operation_grounded | semantically_grounded | citation_correct | source_consistent | misleading_acceptance | input_tokens | tool_calls | latency_ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finqa_600_subset | direct_rag | 600 | 0.32 | 0.67 | 0.282 | 0.038 | 0.388 | -0.35 | 0.943 | 0.428 | 0.72 | 0.972 | 0.698 | 0.698 | 1 | 0.97 | 0 | 865.73 | 1 | 60 |
| finqa_600_subset | evigraph_wo_operation_planner | 600 | 0.325 | 0.707 | 0.295 | 0.03 | 0.412 | -0.382 | 0.963 | 0.445 | 0.757 | 0.965 | 0.727 | 0.727 | 1 | 0.933 | 0 | 870.063 | 1.933 | 87.917 |
| finqa_600_subset | evigraph_wo_risk | 600 | 0.362 | 0.752 | 0.33 | 0.032 | 0.422 | -0.39 | 0.962 | 0.527 | 0.803 | 0.963 | 0.773 | 0.773 | 1 | 0.933 | 0 | 870.063 | 1.933 | 87.917 |
| finqa_600_subset | evigraph_wo_support | 600 | 0.348 | 0.73 | 0.317 | 0.032 | 0.413 | -0.382 | 0.948 | 0.507 | 0.782 | 0.967 | 0.76 | 0.76 | 1 | 0.973 | 0 | 870.063 | 1.933 | 87.917 |
| finqa_600_subset | evigraph_wo_verifier | 600 | 0.368 | 0 | 0 | 0.368 | 0 | 0.368 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 870.063 | 0.933 | 67.917 |
| finqa_600_subset | full_evigraph | 600 | 0.377 | 0.787 | 0.348 | 0.028 | 0.438 | -0.41 | 0.963 | 0.545 | 0.812 | 0.977 | 0.807 | 0.807 | 1 | 0.977 | 0 | 870.063 | 1.933 | 90.017 |
| finqa_600_subset | retrieve_then_program | 600 | 0.348 | 0.727 | 0.318 | 0.03 | 0.408 | -0.378 | 0.945 | 0.5 | 0.777 | 0.97 | 0.755 | 0.755 | 1 | 0.972 | 0 | 865.73 | 1 | 60 |
| finqa_600_subset | utility_only | 600 | 0.315 | 0.707 | 0.282 | 0.033 | 0.425 | -0.392 | 0.967 | 0.447 | 0.737 | 0.968 | 0.722 | 0.722 | 1 | 0.98 | 0 | 856.755 | 1 | 58.867 |

## finqa_600_subset_source_rerank_component_closure_v48.csv

- Rows: 4800
- Grouping: `dataset, method`

| dataset | method | n | accuracy | answer_supported | supported_accuracy | unsupported_correct | supported_wrong | answer_support_gap | arithmetically_supported | calculation_supported | operation_semantics_checked | operand_semantics_checked | row_operation_grounded | semantically_grounded | citation_correct | source_consistent | misleading_acceptance | input_tokens | tool_calls | latency_ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| finqa_600_subset | direct_rag | 600 | 0.46 | 0.733 | 0.403 | 0.057 | 0.33 | -0.273 | 0.953 | 0.52 | 0.785 | 0.973 | 0.765 | 0.765 | 1 | 1 | 0 | 1305.35 | 1 | 60 |
| finqa_600_subset | evigraph_wo_operation_planner | 600 | 0.443 | 0.748 | 0.405 | 0.038 | 0.343 | -0.305 | 0.972 | 0.502 | 0.793 | 0.967 | 0.768 | 0.768 | 1 | 1 | 0 | 983.627 | 2.043 | 67.992 |
| finqa_600_subset | evigraph_wo_risk | 600 | 0.483 | 0.798 | 0.448 | 0.035 | 0.35 | -0.315 | 0.97 | 0.598 | 0.845 | 0.963 | 0.82 | 0.82 | 1 | 1 | 0 | 983.627 | 2.043 | 67.992 |
| finqa_600_subset | evigraph_wo_support | 600 | 0.505 | 0.768 | 0.46 | 0.045 | 0.308 | -0.263 | 0.918 | 0.607 | 0.847 | 0.967 | 0.825 | 0.825 | 1 | 1 | 0 | 983.627 | 2.043 | 67.992 |
| finqa_600_subset | evigraph_wo_verifier | 600 | 0.498 | 0 | 0 | 0.498 | 0 | 0.498 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 983.627 | 1.043 | 47.992 |
| finqa_600_subset | full_evigraph | 600 | 0.502 | 0.822 | 0.467 | 0.035 | 0.355 | -0.32 | 0.97 | 0.618 | 0.848 | 0.97 | 0.843 | 0.843 | 1 | 1 | 0 | 983.627 | 2.043 | 68.325 |
| finqa_600_subset | retrieve_then_program | 600 | 0.483 | 0.782 | 0.445 | 0.038 | 0.337 | -0.298 | 0.953 | 0.593 | 0.835 | 0.97 | 0.815 | 0.815 | 1 | 1 | 0 | 1305.35 | 1 | 60 |
| finqa_600_subset | utility_only | 600 | 0.44 | 0.758 | 0.4 | 0.04 | 0.358 | -0.318 | 0.978 | 0.528 | 0.792 | 0.965 | 0.777 | 0.777 | 1 | 0.993 | 0 | 1181.443 | 1 | 59.458 |
