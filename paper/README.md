# AAAI Paper Skeleton

This folder contains the working AAAI-style paper skeleton.

Current status:

- Title, abstract, introduction, related work, method, experiments, failure analysis, and conclusion draft sections are present.
- The current main results and failure-analysis tables are generated from
  the FinQA-300 local planner source-match v11 outputs and the split GPT-5.4 Direct RAG
  baseline outputs.
- The method figure is a lightweight LaTeX diagram; replace it with a polished graph diagram before final submission if space allows.

Refresh paper assets after each manifest run:

```powershell
python .\scripts\build_paper_assets.py --eval-dir .\outputs\eval\finqa --output-dir .\paper\generated
```

For the current FinQA-300 local-planner tables:

```powershell
python .\scripts\build_paper_assets.py --eval-dir .\outputs\eval\finqa_300_local_planner_source_match_v11 --output-dir .\paper\generated\finqa_300_local_planner_source_match_v11 --preset finqa_300_local
```

For the GPT-5.4 Direct RAG baseline tables, the results are split across
`finqa_300_gpt54_direct_rag_open_bm25` and `finqa_300_gpt54_direct_rag_oracle_source`.
Use the paper-anchor eval directory so the preset can resolve both sibling
folders:

```powershell
python .\scripts\build_paper_assets.py --eval-dir .\outputs\eval\paper_anchor --output-dir .\paper\generated\finqa_300_gpt54_direct_rag --preset finqa_300_gpt54_direct_rag
```

For the neural retrieval baseline tables after running the optional neural
manifest:

```powershell
python .\scripts\build_paper_assets.py --eval-dir .\outputs\eval\finqa_300_neural_retrieval_baselines --output-dir .\paper\generated\finqa_300_neural_retrieval_baselines --preset finqa_300_neural_retrieval_baselines
```

The draft is intentionally conservative: current FinQA results are oracle-document reasoning baselines, not final open-retrieval benchmark claims.
