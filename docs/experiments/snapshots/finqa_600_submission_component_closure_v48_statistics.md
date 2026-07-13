# Statistical Confidence Report

- Target method: `full_evigraph`
- Baselines: `direct_rag, retrieve_then_program, utility_only, evigraph_wo_operation_planner`

## outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_oracle_doc_component_closure_v48.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| direct_rag | 600 | 276 | 0.460 | [0.421, 0.500] |
| retrieve_then_program | 600 | 291 | 0.485 | [0.445, 0.525] |
| utility_only | 600 | 287 | 0.478 | [0.439, 0.518] |
| evigraph_wo_operation_planner | 600 | 267 | 0.445 | [0.406, 0.485] |
| full_evigraph | 600 | 302 | 0.503 | [0.463, 0.543] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | direct_rag | 0.043 | 32 | 6 | 562 | 0.000 |
| full_evigraph | retrieve_then_program | 0.018 | 12 | 1 | 587 | 0.003 |
| full_evigraph | utility_only | 0.025 | 17 | 2 | 581 | 0.001 |
| full_evigraph | evigraph_wo_operation_planner | 0.058 | 37 | 2 | 561 | 0.000 |

## outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_open_bm25_component_closure_v48.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| direct_rag | 600 | 192 | 0.320 | [0.284, 0.358] |
| retrieve_then_program | 600 | 209 | 0.348 | [0.311, 0.387] |
| utility_only | 600 | 189 | 0.315 | [0.279, 0.353] |
| evigraph_wo_operation_planner | 600 | 195 | 0.325 | [0.289, 0.363] |
| full_evigraph | 600 | 226 | 0.377 | [0.339, 0.416] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | direct_rag | 0.057 | 47 | 13 | 540 | 0.000 |
| full_evigraph | retrieve_then_program | 0.028 | 29 | 12 | 559 | 0.012 |
| full_evigraph | utility_only | 0.062 | 50 | 13 | 537 | 0.000 |
| full_evigraph | evigraph_wo_operation_planner | 0.052 | 36 | 5 | 559 | 0.000 |

## outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_source_rerank_component_closure_v48.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| direct_rag | 600 | 276 | 0.460 | [0.421, 0.500] |
| retrieve_then_program | 600 | 290 | 0.483 | [0.444, 0.523] |
| utility_only | 600 | 264 | 0.440 | [0.401, 0.480] |
| evigraph_wo_operation_planner | 600 | 266 | 0.443 | [0.404, 0.483] |
| full_evigraph | 600 | 301 | 0.502 | [0.462, 0.542] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | direct_rag | 0.042 | 32 | 7 | 561 | 0.000 |
| full_evigraph | retrieve_then_program | 0.018 | 13 | 2 | 585 | 0.007 |
| full_evigraph | utility_only | 0.062 | 40 | 3 | 557 | 0.000 |
| full_evigraph | evigraph_wo_operation_planner | 0.058 | 37 | 2 | 561 | 0.000 |
