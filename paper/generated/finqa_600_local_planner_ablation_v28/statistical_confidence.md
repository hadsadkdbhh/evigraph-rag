# Statistical Confidence Report

- Target method: `full_evigraph`
- Baselines: `direct_rag, retrieve_then_program, utility_only, evigraph_wo_operation_planner`

## outputs\eval\finqa_600_local_planner_ablation_v28\finqa_600_subset_oracle_doc_ablation_v28.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| direct_rag | 600 | 265 | 0.442 | [0.402, 0.482] |
| retrieve_then_program | 600 | 280 | 0.467 | [0.427, 0.507] |
| utility_only | 600 | 277 | 0.462 | [0.422, 0.502] |
| evigraph_wo_operation_planner | 600 | 257 | 0.428 | [0.389, 0.468] |
| full_evigraph | 600 | 292 | 0.487 | [0.447, 0.527] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | direct_rag | 0.045 | 33 | 6 | 561 | 0.000 |
| full_evigraph | retrieve_then_program | 0.020 | 13 | 1 | 586 | 0.002 |
| full_evigraph | utility_only | 0.025 | 18 | 3 | 579 | 0.001 |
| full_evigraph | evigraph_wo_operation_planner | 0.058 | 37 | 2 | 561 | 0.000 |

## outputs\eval\finqa_600_local_planner_ablation_v28\finqa_600_subset_open_bm25_ablation_v28.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| direct_rag | 600 | 186 | 0.310 | [0.274, 0.348] |
| retrieve_then_program | 600 | 203 | 0.338 | [0.302, 0.377] |
| utility_only | 600 | 184 | 0.307 | [0.271, 0.345] |
| evigraph_wo_operation_planner | 600 | 187 | 0.312 | [0.276, 0.350] |
| full_evigraph | 600 | 216 | 0.360 | [0.323, 0.399] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | direct_rag | 0.050 | 40 | 10 | 550 | 0.000 |
| full_evigraph | retrieve_then_program | 0.022 | 22 | 9 | 569 | 0.029 |
| full_evigraph | utility_only | 0.053 | 46 | 14 | 540 | 0.000 |
| full_evigraph | evigraph_wo_operation_planner | 0.048 | 29 | 0 | 571 | 0.000 |

## outputs\eval\finqa_600_local_planner_ablation_v28\finqa_600_subset_source_rerank_ablation_v28.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| direct_rag | 600 | 266 | 0.443 | [0.404, 0.483] |
| retrieve_then_program | 600 | 280 | 0.467 | [0.427, 0.507] |
| utility_only | 600 | 255 | 0.425 | [0.386, 0.465] |
| evigraph_wo_operation_planner | 600 | 256 | 0.427 | [0.388, 0.467] |
| full_evigraph | 600 | 290 | 0.483 | [0.444, 0.523] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | direct_rag | 0.040 | 32 | 8 | 560 | 0.000 |
| full_evigraph | retrieve_then_program | 0.017 | 13 | 3 | 584 | 0.021 |
| full_evigraph | utility_only | 0.058 | 40 | 5 | 555 | 0.000 |
| full_evigraph | evigraph_wo_operation_planner | 0.057 | 37 | 3 | 560 | 0.000 |
