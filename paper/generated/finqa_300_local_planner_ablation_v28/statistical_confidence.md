# Statistical Confidence Report

- Target method: `full_evigraph`
- Baselines: `direct_rag, retrieve_then_program, utility_only, evigraph_wo_operation_planner`

## outputs\eval\finqa_300_local_planner_ablation_v28\finqa_300_subset_oracle_doc_ablation_v28.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| direct_rag | 300 | 178 | 0.593 | [0.537, 0.647] |
| retrieve_then_program | 300 | 192 | 0.640 | [0.584, 0.692] |
| utility_only | 300 | 188 | 0.627 | [0.571, 0.679] |
| evigraph_wo_operation_planner | 300 | 176 | 0.587 | [0.530, 0.641] |
| full_evigraph | 300 | 198 | 0.660 | [0.605, 0.711] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | direct_rag | 0.067 | 21 | 1 | 278 | 0.000 |
| full_evigraph | retrieve_then_program | 0.020 | 7 | 1 | 292 | 0.070 |
| full_evigraph | utility_only | 0.033 | 11 | 1 | 288 | 0.006 |
| full_evigraph | evigraph_wo_operation_planner | 0.073 | 23 | 1 | 276 | 0.000 |

## outputs\eval\finqa_300_local_planner_ablation_v28\finqa_300_subset_open_bm25_ablation_v28.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| direct_rag | 300 | 136 | 0.453 | [0.398, 0.510] |
| retrieve_then_program | 300 | 145 | 0.483 | [0.427, 0.540] |
| utility_only | 300 | 120 | 0.400 | [0.346, 0.456] |
| evigraph_wo_operation_planner | 300 | 137 | 0.457 | [0.401, 0.513] |
| full_evigraph | 300 | 155 | 0.517 | [0.460, 0.573] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | direct_rag | 0.063 | 27 | 8 | 265 | 0.002 |
| full_evigraph | retrieve_then_program | 0.033 | 16 | 6 | 278 | 0.052 |
| full_evigraph | utility_only | 0.117 | 42 | 7 | 251 | 0.000 |
| full_evigraph | evigraph_wo_operation_planner | 0.060 | 18 | 0 | 282 | 0.000 |

## outputs\eval\finqa_300_local_planner_ablation_v28\finqa_300_subset_source_rerank_ablation_v28.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| direct_rag | 300 | 178 | 0.593 | [0.537, 0.647] |
| retrieve_then_program | 300 | 192 | 0.640 | [0.584, 0.692] |
| utility_only | 300 | 167 | 0.557 | [0.500, 0.612] |
| evigraph_wo_operation_planner | 300 | 175 | 0.583 | [0.527, 0.638] |
| full_evigraph | 300 | 198 | 0.660 | [0.605, 0.711] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | direct_rag | 0.067 | 23 | 3 | 274 | 0.000 |
| full_evigraph | retrieve_then_program | 0.020 | 8 | 2 | 290 | 0.109 |
| full_evigraph | utility_only | 0.103 | 32 | 1 | 267 | 0.000 |
| full_evigraph | evigraph_wo_operation_planner | 0.077 | 24 | 1 | 275 | 0.000 |
