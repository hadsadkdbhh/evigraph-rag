# Submission Artifact Index

Last updated: 2026-07-13

This file maps the current EviGraph-RAG submission story to reproducible
artifacts, commands, and reporting boundaries. Use it as the first stop before
editing the paper, preparing supplementary material, or handing the project to
another runner.

## Submission Claim Boundary

Main claim:

- The paper formulates numerically grounded RAG as Evidence State Optimization
  (ESO): search over candidate evidence states rather than directly consuming a
  retrieved top-\(K\) prefix.
- EviGraph-RAG is the current ESO implementation. It converts retrieved
  candidates into an evidence graph, searches the Evidence State Space, selects
  a Minimal Reliable Support Subgraph, executes local table/text operations, and
  verifies answer support.

Safe empirical claim:

- On deterministic FinQA diagnostic subsets, evidence-state selection and
  verifier-guided retrieval portfolio selection improve auditable numerical RAG
  behavior while exposing a gap between retrieval exposure and answer accuracy.
- The present system uses deterministic verifier-guided state search; do not
  claim reinforcement learning, learned policy optimization, or SOTA benchmark
  performance.
- TAT-QA-50 and TAT-QA-100 are cross-format portability checks, not full TAT-QA
  benchmark claims.

Unsafe claims:

- Do not claim state-of-the-art FinQA or TAT-QA performance.
- Do not merge oracle-doc, open BM25, source-rerank, neural-hybrid, and
  portfolio numbers into one headline.
- Do not present source-rerank as a deployable open-retrieval setting.
- Do not describe synthetic stress results as benchmark evidence.

## Current Reportable Results

### FinQA-600 Submission Component Closure

Artifact:

- `paper/generated/finqa_600_submission_component_closure_v48/finqa_results_tables.tex`
- `paper/generated/finqa_600_submission_component_closure_v48/finqa_results_summary.md`
- `docs/experiments/snapshots/finqa_600_submission_component_closure_v48_statistics.md`

Main Full EviGraph numbers:

| setting | EM | answer support |
| --- | ---: | ---: |
| Oracle-doc | 0.503 | 0.820 |
| Open BM25 | 0.377 | 0.787 |
| BM25 + source rerank | 0.502 | 0.822 |

Component contribution highlights:

| setting | planner delta EM | support-graph delta EM | graph vs utility-only EM |
| --- | ---: | ---: | ---: |
| Oracle-doc | +0.058 | +0.017 | +0.025 |
| Open BM25 | +0.052 | +0.028 | +0.062 |
| BM25 + source rerank | +0.058 | -0.003 | +0.062 |

Reporting role:

- Primary mechanism/ablation table for the deterministic submission closure.
- Use to argue that operation planning, support selection, and verification
  matter separately.

### FinQA-600 Stress Setting

Artifacts:

- `paper/generated/retrieval_portfolio_ablation/finqa_retrieval_portfolio_ablation.tex`
- `paper/generated/statistical_confidence/main_confidence_table.tex`
- `outputs/eval/finqa_600_local_planner_guarded_top8_repair_v43/summary.md`
- `outputs/eval/finqa_600_retrieval_portfolio_v46_guarded_confidence/portfolio_report.md`

Main open-retrieval stress numbers:

| setting | method | EM | 95% Wilson CI |
| --- | --- | ---: | --- |
| FinQA-600 Open | BM25 primary | 0.377 | [0.339, 0.416] |
| FinQA-600 Open | Guarded portfolio v46 | 0.407 | [0.368, 0.446] |

Paired test:

- Guarded portfolio vs BM25 primary: 18 wins, 0 losses, exact McNemar p < 0.001.

Reporting role:

- Larger stress subset for generalization pressure.
- Use to support the retrieval-exposure argument: neural/hybrid candidates help
  only when a verifier-guided evidence-state selector chooses the better state.

### TAT-QA Cross-Format Portability

Artifacts:

- `paper/generated/tatqa_50_cross_benchmark/tatqa_50_results.tex`
- `paper/generated/tatqa_100_portability_v50/tatqa_100_results.tex`
- `outputs/eval/tatqa_50_senior_notes_issuance_sum_v50/summary.md`
- `outputs/eval/tatqa_100_portability_v50/summary.md`

TAT-QA-50 pilot:

| setting | EM | support | source_hit@8 |
| --- | ---: | ---: | ---: |
| Oracle-doc | 0.540 | 0.740 | n/a |
| Open BM25 | 0.460 | 0.900 | 0.960 |

TAT-QA-100 portability check:

| setting | EM | support | source_hit@8 |
| --- | ---: | ---: | ---: |
| Oracle-doc | 0.520 | 0.750 | n/a |
| Open BM25 | 0.410 | 0.850 | 0.900 |

Reporting role:

- Cross-format evidence that the manifest pipeline and adapter are not
  FinQA-only.
- Keep language conservative: portability check, not leaderboard result.

## Command Map

### Global Smoke and Unit Tests

```powershell
python -m unittest discover -s tests
```

Expected latest verified result:

- 397 tests OK after the v50 senior-notes repair.

### Paper Figures

```powershell
python .\scripts\render_paper_figures.py
```

Generated artifacts:

- `paper/figures/evigraph_pipeline.pdf`
- `paper/figures/evigraph_pipeline.png`
- `paper/figures/retrieval_portfolio_mechanism.pdf`
- `paper/figures/retrieval_portfolio_mechanism.png`
- `paper/figures/experimental_story_panel.pdf`
- `paper/figures/experimental_story_panel.png`

Use these for:

- Figure 1: the EviGraph-RAG teaser example and evidence-state control pipeline.
- Figure 2: the retrieval-portfolio mechanism and FinQA-600 open-retrieval
  ablation result.
- Figure 3: the multi-panel experimental story covering component gains,
  retrieval portfolio selection, TAT-QA portability, and EM/support gap.

### Supplementary Material

Artifact:

- `paper/appendix.tex`
- `paper/supplement.tex`
- `docs/submission_gap_checklist.md`
- `docs/code_data_release_note.md`

Use this for:

- Prompt and output contracts.
- Evidence-distraction diagnostics inspired by RAG-hurts failure analysis.
- Row/operation error taxonomy.
- Dataset and manifest construction details.
- Baseline/ablation controls.
- Retrieval portfolio selector details.
- Computational cost and traceability summary.
- Boundary conditions and reproducibility commands.
- Code/data packaging scope, privacy exclusions, and release commands.
- EvoGraph-R1-inspired gap tracking: algorithm block, action/interface table,
  exact schemas, trace-style case studies, metrics definitions, implementation
  details, and official-template compile notes.

### FinQA-600 Submission Component Closure Table

```powershell
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_600.submission_component_closure_v48.json
python .\scripts\build_paper_assets.py --eval-dir .\outputs\eval\finqa_600_submission_component_closure_v48 --output-dir .\paper\generated\finqa_600_submission_component_closure_v48 --preset finqa_600_submission_component_closure_v48
```

Use this for:

- Main FinQA-600 baseline ladder.
- Operation-planner, verifier, risk, and support-graph ablations.
- Failure categories and row/operation diagnostic tables.

### FinQA-600 Guarded BM25 Stress Run

```powershell
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_600.local_planner_guarded_top8_repair_v43.json
```

Use this for:

- Oracle-doc, Open BM25, and source-rerank FinQA-600 stress numbers.
- BM25 primary input to the retrieval-portfolio selector.

### FinQA-600 Neural-Hybrid Retrieval Candidate

```powershell
python .\scripts\check_neural_retrieval_ready.py
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_600.neural_retrieval_full_evigraph_v43.json
```

Use this for:

- Neural dense and neural hybrid candidate states.
- Source-exposure comparison against BM25.

### Retrieval Portfolio v46

```powershell
python .\scripts\build_retrieval_portfolio.py `
  --primary-csv .\outputs\eval\finqa_600_local_planner_guarded_top8_repair_v43\finqa_600_subset_open_bm25_full_local_planner_v43_guarded_top8_repair.csv `
  --candidate-csv .\outputs\eval\finqa_600_neural_retrieval_full_evigraph_v43\finqa_600_subset_open_neural_hybrid_full_evigraph_top16_v43.csv `
  --output-dir .\outputs\eval\finqa_600_retrieval_portfolio_v46_guarded_confidence `
  --primary-name "BM25 top-8" `
  --candidate-name "Neural-hybrid top-16" `
  --method full_evigraph `
  --policy confidence `
  --title "FinQA-600 Guarded Confidence Portfolio v46"
```

Use this for:

- The open-retrieval portfolio ablation table.
- The paired wins/losses story.

### Confidence Intervals

```powershell
python .\scripts\analyze_statistics.py `
  --inputs .\outputs\eval\finqa_600_retrieval_portfolio_v46_guarded_confidence\finqa_600_subset_open_portfolio_bm25_hybrid_v46_guarded_confidence.csv `
  --output .\paper\generated\statistical_confidence\main_confidence_report.md
```

Current paper tables are already generated at:

- `paper/generated/statistical_confidence/main_confidence_table.md`
- `paper/generated/statistical_confidence/main_confidence_table.tex`

If regenerating from scratch, verify that the output includes both Wilson
intervals and paired McNemar results before updating the paper.

### TAT-QA-50 v50 Pilot

```powershell
python .\scripts\run_manifest.py --manifest .\configs\experiments.tatqa_50.senior_notes_issuance_sum_v50.json
```

Use this for:

- The TAT-QA-50 pilot table.
- Failure-driven v47-v50 repair trajectory.

### TAT-QA-100 Portability Check

```powershell
python .\scripts\run_manifest.py --manifest .\configs\experiments.tatqa_100.senior_notes_issuance_sum_v50.json
```

Use this for:

- The scaled second-dataset portability check.

To rebuild the TAT-QA-100 subset from the original TAT-QA development JSON when
available locally:

```powershell
python .\scripts\build_tatqa_subset.py `
  --input <path-to-tatqa_dataset_dev.json> `
  --raw-output .\data\raw\tatqa_100_subset.jsonl `
  --corpus-output .\data\tatqa_100_corpus `
  --sample-size 100 `
  --seed 13 `
  --answer-types arithmetic
```

The checked-in `data/raw/tatqa_100_subset.jsonl` and `data/tatqa_100_corpus/`
allow a clean checkout to rerun the manifest without needing the raw TAT-QA JSON.

## Submission Checklist

Before declaring the paper submission-ready:

- [x] FinQA-300 mechanism table exists and is generated from a manifest.
- [x] FinQA-600 stress results exist and are separated from FinQA-300.
- [x] Open retrieval, source-rerank, and oracle-doc settings are not merged.
- [x] Retrieval portfolio has paired wins/losses and confidence intervals.
- [x] TAT-QA-50 and TAT-QA-100 portability checks are recorded.
- [x] Unit tests pass after the latest v50 repair.
- [x] Download the official AAAI-27 Author Kit and place the required style and
  bibliography files in `paper/`. The official kit uses `aaai2027.sty` and
  `aaai2027.bst`; `paper/main.tex` now imports the official package name
  directly.
- [x] Split supplementary material out of the main submission PDF:
  `paper/main.tex` now contains only main paper plus references, while
  `paper/supplement.tex` compiles `paper/appendix.tex` separately.
- [x] Add final code/data release note for supplementary material:
  `docs/code_data_release_note.md`.
- [x] Re-run the local no-API submission-suite gate from the current checkout:
  `python scripts/run_pipeline.py --suite submission --skip-llm-direct-rag`
  passed on 2026-07-10. For a fresh external clone, run the same command after
  restoring or regenerating ignored `outputs/` artifacts.
- [x] Freeze the current checkpoint's reported numbers in the paper/docs. After
  paper draft lock, do not change tables without a new named manifest and
  paired failure report.

Final PDF upload check:

- Windows MiKTeX 25.12 plus Strawberry Perl was installed on 2026-07-10 after
  the Codex-managed TeX Live installer reported Windows is unsupported.
- `scripts/check_aaai_page_budget.ps1 -AlsoCompileSupplement` passed with the
  official `aaai2027.sty`: main PDF is 8 pages total, References starts on
  page 8, estimated main content is 7/7 pages, and supplement is 6 pages.

## Current Compile Status

Latest local compile check:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\check_aaai_page_budget.ps1 -AlsoCompileSupplement
```

Result:

- The official AAAI-27 style and bibliography files are present in `paper/`.
- The official `aaai2027.sty` requires pdfTeX; bundled Tectonic invokes XeTeX
  and is rejected by the style file.
- Windows MiKTeX 25.12 provides `pdflatex`, `bibtex`, `latexmk`, `pdfinfo`, and
  `pdftotext`; Strawberry Perl provides the script engine required by
  MiKTeX's `latexmk`.
- Main PDF: 8 total pages, References start page 8, estimated main-content
  pages 7/7.
- Supplement PDF: 6 pages.
