# AAAI Paper Package

This folder contains the working AAAI paper package.

Current status:

- `main.tex` uses the official `aaai2027` package and contains the main paper
  plus references only.
- `supplement.tex` compiles `appendix.tex` as separate supplementary material.
- `aaai2027.sty` and `aaai2027.bst` are checked into this folder from the
  official AAAI-27 Author Kit.
- The current reported tables are generated from the FinQA-300 mechanism run,
  FinQA-600 stress run, retrieval-portfolio ablation, confidence intervals,
  and TAT-QA-50/100 portability checks.
- Figure polishing is intentionally tracked separately from this non-figure
  submission checkpoint.

Refresh paper assets after each manifest run:

```powershell
python .\scripts\build_paper_assets.py --eval-dir .\outputs\eval\finqa --output-dir .\paper\generated
```

For the current FinQA-300 local-planner tables:

```powershell
python .\scripts\build_paper_assets.py --eval-dir .\outputs\eval\finqa_300_local_planner_table_ops_v21 --output-dir .\paper\generated\finqa_300_local_planner_table_ops_v21 --preset finqa_300_local
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

Run the official page-budget check with a pdfLaTeX-capable TeX Live or MiKTeX
runtime:

```powershell
powershell -ExecutionPolicy Bypass -File ..\scripts\check_aaai_page_budget.ps1 -AlsoCompileSupplement
```

The official AAAI style rejects XeTeX/Tectonic, so bundled Tectonic is not a
valid final page-count substitute. On the current Windows setup, MiKTeX plus
Strawberry Perl compiles the official template successfully.
