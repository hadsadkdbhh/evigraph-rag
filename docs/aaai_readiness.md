# AAAI Readiness Notes

Last updated: 2026-07-10

This file tracks what the current repository can and cannot support as paper
evidence. It is intentionally conservative: the project should be pitched as
Evidence State Optimization (ESO) for auditable numerical RAG, not as a
leaderboard or SOTA benchmark paper.

## Supported Claims Now

- The codebase runs a manifest-driven EviGraph-RAG pipeline with candidate
  evidence construction, utility/risk scoring, support-subgraph selection,
  local table/text operation execution, verifier diagnostics, and artifact
  logging.
- The main paper defines Evidence Unit, Candidate Evidence Graph, Evidence
  State, Evidence State Space, ESO, and Minimal Reliable Support Subgraph
  (MRSG), and includes a monotone submodular relaxation for greedy selection.
- FinQA-300 is the main diagnostic mechanism setting. The current paper table
  reports Full EviGraph v38 at 0.670 oracle-doc EM, 0.523 open BM25 EM, and
  0.670 source-rerank EM, with verifier-checked support rates of 0.850, 0.853,
  and 0.850.
- Stronger baselines are present: Direct RAG, GPT-5.4 Direct RAG,
  retrieve-then-program, full-context, utility-only selection, no-planner,
  no-verifier-grounded rejection, no-risk, no-support-graph, dense retrieval,
  neural hybrid retrieval, and retrieval-portfolio controls.
- The GPT-5.4 Direct RAG baseline is useful as a storytelling contrast: it can
  reach high exact match on FinQA-300 but has much lower verifier-checked answer
  support, motivating the EM/support gap.
- FinQA-600 is wired as a larger stress subset. Guarded retrieval-portfolio
  selection improves open retrieval from BM25 0.377 EM to 0.407 EM with 18
  paired wins, 0 losses, and exact McNemar p < 0.001.
- TAT-QA-50 and TAT-QA-100 portability checks are present. The TAT-QA-100 run
  reaches 0.520 oracle-doc EM and 0.410 open BM25 EM, clearing the planned
  small second-dataset portability gate.
- The row/operation diagnostic splits wrong numeric answers into numerator,
  denominator, year/period, row-label, operation-type, and ambiguous
  supported-wrong-number categories.
- The supplement contains prompt/output contracts, evidence-distraction
  diagnostics, trace-style case studies, failure-to-fix provenance,
  dataset/manifest construction, metrics definitions, implementation details,
  retrieval-portfolio details, computational cost, and boundary conditions.
- Official AAAI-27 style files are checked into `paper/`, and
  `paper/main.tex` no longer includes the supplement.

## Claims Not Supported

- Do not claim state-of-the-art FinQA or TAT-QA performance.
- Do not claim reinforcement learning, learned policy optimization, persistent
  graph memory, self-evolving hypergraphs, or multimodal document reasoning.
- Do not merge oracle-doc, open BM25, source-rerank, dense/hybrid retrieval, and
  portfolio results into a single headline number.
- Do not present source-rerank as a deployable open-retrieval result.
- Do not describe synthetic stress examples as public benchmark evidence.
- Do not claim that the current system solves open retrieval; frame Open BM25
  and FinQA-600 as stress settings that reveal retrieval-exposure failures.

## Submission-Ready Non-Figure Package

The non-figure submission package now contains:

- Official-template main paper: `paper/main.tex`.
- Separate supplement: `paper/supplement.tex` and `paper/appendix.tex`.
- Generated paper tables: `paper/generated/`.
- Artifact/claim map: `docs/submission_artifact_index.md`.
- Gap checklist: `docs/submission_gap_checklist.md`.
- Code/data release note: `docs/code_data_release_note.md`.
- Current-state handoff: `docs/context/current_state.md`.

The remaining non-content blocker is environment-level: final official page
count requires a pdfLaTeX-capable TeX Live or MiKTeX installation. The bundled
Tectonic path uses XeTeX and is rejected by `aaai2027.sty`.

## Validation Commands

Run tests:

```powershell
python -m unittest discover -s tests
```

Run the local no-API submission-suite gate:

```powershell
python scripts/run_pipeline.py --suite submission --skip-llm-direct-rag
```

Run the official page-budget check after installing TeX Live or MiKTeX:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_aaai_page_budget.ps1 -AlsoCompileSupplement
```
