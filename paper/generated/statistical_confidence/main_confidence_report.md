# Statistical Confidence Report

- Target method: `full_evigraph`
- Baselines: `direct_rag, retrieve_then_program, utility_only, topk`

## outputs\eval\finqa_600_local_planner_guarded_top8_repair_v43\finqa_600_subset_open_bm25_full_local_planner_v43_guarded_top8_repair.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| full_evigraph | 600 | 226 | 0.377 | [0.339, 0.416] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |

## outputs\eval\finqa_300_neural_retrieval_baselines_v21\finqa_300_subset_open_bm25_baseline_v21.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| direct_rag | 300 | 134 | 0.447 | [0.391, 0.503] |
| retrieve_then_program | 300 | 142 | 0.473 | [0.418, 0.530] |
| full_evigraph | 300 | 148 | 0.493 | [0.437, 0.550] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | direct_rag | 0.047 | 25 | 11 | 264 | 0.029 |
| full_evigraph | retrieve_then_program | 0.020 | 14 | 8 | 278 | 0.286 |

## outputs\eval\stress\stress_numeric_ablation.csv

### Accuracy Intervals

| method | n | correct | accuracy | 95% Wilson CI |
| --- | ---: | ---: | ---: | --- |
| utility_only | 3 | 1 | 0.333 | [0.061, 0.792] |
| topk | 3 | 1 | 0.333 | [0.061, 0.792] |
| full_evigraph | 3 | 3 | 1.000 | [0.438, 1.000] |

### Paired Comparisons

| target | baseline | delta EM | target-only | baseline-only | ties | McNemar p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| full_evigraph | utility_only | 0.667 | 2 | 0 | 1 | 0.500 |
| full_evigraph | topk | 0.667 | 2 | 0 | 1 | 0.500 |
