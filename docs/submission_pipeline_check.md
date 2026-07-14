# Submission Pipeline Check

Created UTC: 2026-07-14T02:22:12.694058+00:00

Overall status: PASS

## Command Gates

| Gate | Status | Command |
| --- | --- | --- |
| unit tests | PASS | `D:\Anaconda\python.exe -m unittest discover -s tests` |
| submission experiment closure | PASS | `D:\Anaconda\python.exe scripts/check_experiment_closure.py --output docs/experiments/submission_closure_check.md` |
| official AAAI page budget | PASS | `powershell -ExecutionPolicy Bypass -File scripts/check_aaai_page_budget.ps1 -AlsoCompileSupplement` |

## Artifact And Log Gates

| Gate | Status | Detail |
| --- | --- | --- |
| AAAI main paper | PASS | paper/main.tex |
| AAAI supplement wrapper | PASS | paper/supplement.tex |
| AAAI appendix | PASS | paper/appendix.tex |
| Official AAAI style | PASS | paper/aaai2027.sty |
| Official AAAI bibliography style | PASS | paper/aaai2027.bst |
| Main pipeline figure | PASS | paper/figures/evigraph_pipeline.pdf |
| Retrieval portfolio figure | PASS | paper/figures/retrieval_portfolio_mechanism.pdf |
| FinQA-600 main closure table | PASS | paper/generated/finqa_600_submission_component_closure_v48/finqa_main_tables.tex |
| FinQA-600 full diagnostic tables | PASS | paper/generated/finqa_600_submission_component_closure_v48/finqa_results_tables.tex |
| FinQA-600 closure summary | PASS | paper/generated/finqa_600_submission_component_closure_v48/finqa_results_summary.md |
| Retrieval portfolio ablation table | PASS | paper/generated/retrieval_portfolio_ablation/finqa_retrieval_portfolio_ablation.tex |
| Statistical confidence table | PASS | paper/generated/statistical_confidence/main_confidence_table.tex |
| TAT-QA-50 portability table | PASS | paper/generated/tatqa_50_cross_benchmark/tatqa_50_results.tex |
| TAT-QA-100 portability table | PASS | paper/generated/tatqa_100_portability_v50/tatqa_100_results.tex |
| Submission artifact index | PASS | docs/submission_artifact_index.md |
| Experiment closure definition | PASS | docs/experiments/submission_closure.md |
| Experiment closure check report | PASS | docs/experiments/submission_closure_check.md |
| Experiment results index | PASS | docs/experiments/results_index.md |
| Code/data release note | PASS | docs/code_data_release_note.md |
| LaTeX log outputs/latex_sandbox/build/main.log | PASS | no undefined references or citations |
| LaTeX log outputs/latex_sandbox/build/supplement.log | PASS | no undefined references or citations |