# Submission Experiment Closure Check

Overall status: PASS

## Numeric Gates

| Gate | n | EM | Threshold | Status |
| --- | ---: | ---: | ---: | --- |
| FinQA-600 oracle-doc final Full EviGraph | 600 | 0.503 | 0.500 | PASS |
| FinQA-600 source-rerank final Full EviGraph | 600 | 0.502 | 0.500 | PASS |
| FinQA-600 open BM25 final Full EviGraph | 600 | 0.377 | 0.370 | PASS |
| FinQA-600 guarded retrieval portfolio | 600 | 0.407 | 0.400 | PASS |
| TAT-QA-100 oracle-doc portability | 100 | 0.520 | 0.450 | PASS |
| TAT-QA-100 open BM25 portability | 100 | 0.410 | 0.350 | PASS |
| FinQA-600 oracle-doc v48 component closure | 600 | 0.503 | 0.500 | PASS |
| FinQA-600 open BM25 v48 component closure | 600 | 0.377 | 0.370 | PASS |
| FinQA-600 source-rerank v48 component closure | 600 | 0.502 | 0.500 | PASS |
| TAT-QA-100 oracle-doc method closure | 100 | 0.520 | 0.450 | PASS |
| TAT-QA-100 open BM25 method closure | 100 | 0.410 | 0.350 | PASS |

## Artifact Gates

| Gate | Status |
| --- | --- |
| FinQA-600 final oracle failure analysis | PASS: ok |
| FinQA-600 final open row-operation diagnostics | PASS: ok |
| FinQA-600 portfolio significance report | PASS: ok |
| TAT-QA-100 row-operation diagnostics | PASS: ok |
| FinQA-600 v28 component ablation exists | PASS: ok |

## Version-Alignment Notes

- FinQA-600 v48 component closure is complete across oracle-doc, open BM25, and source-rerank.
- TAT-QA-100 v50 method closure is complete across oracle-doc and open BM25.
- v28 component ablation remains useful only as historical development context.
- LLM Direct RAG baselines are complete for FinQA-300 GPT-5.4, but no final FinQA-600 LLM Direct RAG run is present. Keep the 300-sample LLM baseline unless budget allows a 600-sample rerun.
