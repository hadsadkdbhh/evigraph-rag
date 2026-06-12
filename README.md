# EviGraph-RAG

Utility-Risk Evidence State Control for Multimodal RAG.

Core claim: retrieved information is not evidence. This project treats retrieval
outputs as candidate evidence states, scores their utility and risks, selects a
minimal reliable support subgraph, and generates grounded answers from that
subgraph only.

## MVP-0

Run a toy end-to-end pipeline with mock retrieved candidates:

```powershell
python scripts/run_query.py --query "According to the chart, how much higher was 2023 than 2022?"
```

The run writes:

- `outputs/runs/<run_id>/trace.jsonl`
- `outputs/runs/<run_id>/graph.json`
- `outputs/runs/<run_id>/answer.md`
- `outputs/runs/<run_id>/cost.json`
