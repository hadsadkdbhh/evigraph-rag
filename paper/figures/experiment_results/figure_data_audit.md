# Figure Data Audit

Generated at: 2026-07-16T17:04:01+08:00
Repository root: `.`
Command: `python.exe .\scripts\plot_paper_figures.py --strict --output-dir paper\figures\experiment_results --formats pdf png --dpi 600`
Strict mode: `True`

## Audit Conclusion

- No invented experimental values were used.
- Raw experiment CSV files were not modified.
- CSV is the primary source for EM and answer-support values unless explicitly noted.
- Markdown and LaTeX paper assets were parsed for portfolio intervals, failure categories, and consistency checks.
- No financial OHLC candlestick data was generated; the interval figure is a scientific point-range plot.

## Validation

### Checked files

- `outputs\eval\finqa_600_submission_component_closure_v48\summary.md`
- `outputs\eval\tatqa_100_submission_method_closure_v50\summary.md`
- `paper\generated\finqa_600_submission_component_closure_v48\finqa_main_tables.tex`
- `paper\generated\finqa_600_submission_component_closure_v48\finqa_results_tables.tex`
- `paper\generated\retrieval_portfolio_ablation\finqa_retrieval_portfolio_ablation.md`
- `paper\generated\retrieval_portfolio_ablation\finqa_retrieval_portfolio_ablation.tex`
- `paper\generated\statistical_confidence\main_confidence_table.md`
- `paper\generated\statistical_confidence\main_confidence_table.tex`
- `paper\generated\tatqa_100_portability_v50\tatqa_100_results.md`
- `paper\generated\tatqa_100_portability_v50\tatqa_100_results.tex`

### Notes

- FinQA CSV means match outputs/eval summary.md at displayed three-decimal precision.
- FinQA LaTeX tables match CSV/summary values at their displayed precision.
- Portfolio report and generated paper assets agree on n=600, switches=74, wins=18, losses=0.
- TAT-QA-100 CSV, summary, and paper tables agree at displayed precision.
- No fallback example data used; all plotted values trace to repository CSV, Markdown, or LaTeX artifacts.

### Missing optional files

- none

### Conflicts

- none

## Palette

| item | color |
| --- | --- |
| Direct RAG | `#BFDFD2` |
| Retrieve-then-program | `#51999F` |
| Utility-only | `#4198AC` |
| No operation planner | `#7BC0CD` |
| Full EviGraph | `#ED8D5A` |
| BM25 primary | `#51999F` |
| Neural-hybrid candidate | `#DBCB92` |
| Guarded portfolio | `#EA9E58` |
| EM | `#4198AC` |
| Answer Support | `#ED8D5A` |
| Source Hit@K | `#BFDFD2` |

## fig_finqa_main_results

### Output files

- `paper\figures\experiment_results\fig_finqa_main_results.pdf`
- `paper\figures\experiment_results\fig_finqa_main_results.png`

### Source files

- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_open_bm25_component_closure_v48.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_oracle_doc_component_closure_v48.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_source_rerank_component_closure_v48.csv`

### Fields

- `dataset`
- `method`
- `accuracy`

### Filters

- FinQA-600 only
- methods restricted to five main/baseline variants

### Sample sizes

- Oracle-doc: n=600 per method
- Open BM25: n=600 per method
- BM25 + source rerank: n=600 per method

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'setting': 'Oracle-doc', 'method': 'Direct RAG', 'EM': 0.46}` |
| 2 | `{'setting': 'Oracle-doc', 'method': 'Retrieve-then-program', 'EM': 0.485}` |
| 3 | `{'setting': 'Oracle-doc', 'method': 'Utility-only', 'EM': 0.478333}` |
| 4 | `{'setting': 'Oracle-doc', 'method': 'No operation planner', 'EM': 0.445}` |
| 5 | `{'setting': 'Oracle-doc', 'method': 'Full EviGraph', 'EM': 0.503333}` |
| 6 | `{'setting': 'Open BM25', 'method': 'Direct RAG', 'EM': 0.32}` |
| 7 | `{'setting': 'Open BM25', 'method': 'Retrieve-then-program', 'EM': 0.348333}` |
| 8 | `{'setting': 'Open BM25', 'method': 'Utility-only', 'EM': 0.315}` |
| 9 | `{'setting': 'Open BM25', 'method': 'No operation planner', 'EM': 0.325}` |
| 10 | `{'setting': 'Open BM25', 'method': 'Full EviGraph', 'EM': 0.376667}` |
| 11 | `{'setting': 'BM25 + source rerank', 'method': 'Direct RAG', 'EM': 0.46}` |
| 12 | `{'setting': 'BM25 + source rerank', 'method': 'Retrieve-then-program', 'EM': 0.483333}` |
| 13 | `{'setting': 'BM25 + source rerank', 'method': 'Utility-only', 'EM': 0.44}` |
| 14 | `{'setting': 'BM25 + source rerank', 'method': 'No operation planner', 'EM': 0.443333}` |
| 15 | `{'setting': 'BM25 + source rerank', 'method': 'Full EviGraph', 'EM': 0.501667}` |

Missing values: none detected
Aggregation/filtering: Mean of the row-level `accuracy` column grouped by setting and method.
Markdown fallback: none; CSV is primary, Markdown/LaTeX used only for validation.
Consistency: validated against outputs/eval summary.md and generated LaTeX tables at displayed precision.

### Colors

- Direct RAG: #BFDFD2
- Retrieve-then-program: #51999F
- Utility-only: #4198AC
- No operation planner: #7BC0CD
- Full EviGraph: #ED8D5A

## fig_em_support_comparison

### Output files

- `paper\figures\experiment_results\fig_em_support_comparison.pdf`
- `paper\figures\experiment_results\fig_em_support_comparison.png`

### Source files

- `outputs\eval\finqa_600_retrieval_portfolio_v46_guarded_confidence\finqa_600_subset_open_portfolio_bm25_hybrid_v46_guarded_confidence.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_open_bm25_component_closure_v48.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_oracle_doc_component_closure_v48.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_source_rerank_component_closure_v48.csv`
- `outputs\eval\tatqa_100_submission_method_closure_v50\tatqa_100_open_bm25_method_closure_v50.csv`
- `outputs\eval\tatqa_100_submission_method_closure_v50\tatqa_100_oracle_doc_method_closure_v50.csv`

### Fields

- `dataset`
- `method`
- `accuracy`
- `answer_supported`

### Filters

- Full EviGraph only
- FinQA-600 Guarded portfolio included as completed evidence-state selector output

### Sample sizes

- FinQA-600 Oracle-doc: n=600
- FinQA-600 Open BM25: n=600
- FinQA-600 Source rerank: n=600
- FinQA-600 Guarded portfolio: n=600
- TAT-QA-100 Oracle-doc: n=100
- TAT-QA-100 Open BM25: n=100

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'dataset': 'FinQA-600', 'setting': 'Oracle-doc', 'EM': 0.503333, 'answer_support': 0.82}` |
| 2 | `{'dataset': 'FinQA-600', 'setting': 'Open BM25', 'EM': 0.376667, 'answer_support': 0.786667}` |
| 3 | `{'dataset': 'FinQA-600', 'setting': 'BM25 + source rerank', 'EM': 0.501667, 'answer_support': 0.821667}` |
| 4 | `{'dataset': 'FinQA-600', 'setting': 'Guarded portfolio', 'EM': 0.406667, 'answer_support': 0.806667}` |
| 5 | `{'dataset': 'TAT-QA-100', 'setting': 'Oracle-doc', 'EM': 0.52, 'answer_support': 0.75}` |
| 6 | `{'dataset': 'TAT-QA-100', 'setting': 'Open BM25', 'EM': 0.41, 'answer_support': 0.85}` |

Missing values: none detected
Aggregation/filtering: Mean accuracy and mean answer_supported for each Full EviGraph condition.
Markdown fallback: none for EM/support; portfolio CSV provides Guarded portfolio support.
Consistency: FinQA/TAT-QA values validated against generated summaries; portfolio EM validated against portfolio_report.md.

### Colors

- EM: #4198AC
- Answer Support: #ED8D5A

## fig_retrieval_portfolio_ci

### Output files

- `paper\figures\experiment_results\fig_retrieval_portfolio_ci.pdf`
- `paper\figures\experiment_results\fig_retrieval_portfolio_ci.png`

### Source files

- `outputs\eval\finqa_600_retrieval_portfolio_v46_guarded_confidence\finqa_600_subset_open_portfolio_bm25_hybrid_v46_guarded_confidence.csv`
- `outputs\eval\finqa_600_retrieval_portfolio_v46_guarded_confidence\portfolio_report.md`

### Fields

- `Rows`
- `Portfolio EM`
- `Primary EM (bm25)`
- `Candidate EM (neural_hybrid)`
- `95% Wilson CI`
- `Switches`
- `Wins vs primary`
- `Losses vs primary`
- `Paired McNemar p-value`

### Filters

- FinQA-600 open retrieval portfolio only

### Sample sizes

- n=600

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'selector': 'BM25 primary', 'EM': 0.377, 'CI_low': 0.339, 'CI_high': 0.416}` |
| 2 | `{'selector': 'Neural-hybrid candidate', 'EM': 0.363, 'CI_low': 0.326, 'CI_high': 0.403}` |
| 3 | `{'selector': 'Guarded portfolio', 'EM': 0.407, 'CI_low': 0.368, 'CI_high': 0.446}` |
| 4 | `{'switches': 74, 'wins': 18, 'losses': 0, 'p_value': 0.0}` |

Missing values: none detected
Aggregation/filtering: No averaging in plot; point estimates and Wilson intervals are parsed from portfolio_report.md.
Markdown fallback: Markdown report is the primary source for intervals and paired-test metadata; CSV is used to validate portfolio EM/support.
Consistency: validated against retrieval portfolio ablation and statistical confidence paper assets.

### Colors

- BM25 primary: #51999F
- Neural-hybrid candidate: #DBCB92
- Guarded portfolio: #EA9E58

## fig_component_ablation

### Output files

- `paper\figures\experiment_results\fig_component_ablation.pdf`
- `paper\figures\experiment_results\fig_component_ablation.png`

### Source files

- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_open_bm25_component_closure_v48.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_oracle_doc_component_closure_v48.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_source_rerank_component_closure_v48.csv`

### Fields

- `method`
- `accuracy`

### Filters

- FinQA-600 only
- deltas computed against Full EviGraph in the same retrieval setting

### Sample sizes

- Oracle-doc: n=600 per method
- Open BM25: n=600 per method
- BM25 + source rerank: n=600 per method

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'setting': 'Oracle-doc', 'vs no planner': 0.058333, 'vs retrieve-then-program': 0.018333, 'vs utility-only': 0.025}` |
| 2 | `{'setting': 'Open BM25', 'vs no planner': 0.051667, 'vs retrieve-then-program': 0.028333, 'vs utility-only': 0.061667}` |
| 3 | `{'setting': 'BM25 + source rerank', 'vs no planner': 0.058333, 'vs retrieve-then-program': 0.018333, 'vs utility-only': 0.061667}` |

Missing values: none detected
Aggregation/filtering: Full EviGraph EM minus baseline EM, where both EM values are CSV means.
Markdown fallback: none; CSV is primary.
Consistency: validated against generated component-contribution LaTeX table at displayed precision.

### Colors

- vs no planner: #51999F
- vs retrieve-then-program: #4198AC
- vs utility-only: #7BC0CD
- max-delta label/edge: #ED8D5A

## fig_failure_analysis

### Output files

- `paper\figures\experiment_results\fig_failure_analysis.pdf`
- `paper\figures\experiment_results\fig_failure_analysis.png`

### Source files

- `paper\generated\finqa_600_submission_component_closure_v48\finqa_results_summary.md`
- `paper\generated\finqa_600_submission_component_closure_v48\finqa_results_tables.tex`

### Fields

- `Full EviGraph Failure Categories table`

### Filters

- Full EviGraph only
- FinQA-600 settings only

### Sample sizes

- Oracle-doc: n=600
- Open BM25: n=600
- BM25 + source rerank: n=600

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'setting': 'Oracle-doc', 'Wrong row / operation': 96, 'No numeric': 54, 'No percent': 64, 'Additive / lookup': 46, 'Ratio': 27, 'Unsupported': 5}` |
| 2 | `{'setting': 'Open BM25', 'Wrong row / operation': 116, 'No numeric': 63, 'No percent': 90, 'Additive / lookup': 55, 'Ratio': 37, 'Unsupported': 4}` |
| 3 | `{'setting': 'BM25 + source rerank', 'Wrong row / operation': 96, 'No numeric': 55, 'No percent': 64, 'Additive / lookup': 47, 'Ratio': 27, 'Unsupported': 4}` |

Missing values: none detected
Aggregation/filtering: Counts parsed from generated failure-category tables; categories are not stacked.
Markdown fallback: Markdown generated paper summary is the primary source for failure counts; LaTeX table is used for consistency validation.
Consistency: validated against generated FinQA failure-category LaTeX table.

### Colors

- Oracle-doc: #51999F
- Open BM25: #ED8D5A
- BM25 + source rerank: #7BC0CD

## fig_cross_dataset_portability

### Output files

- `paper\figures\experiment_results\fig_cross_dataset_portability.pdf`
- `paper\figures\experiment_results\fig_cross_dataset_portability.png`

### Source files

- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_open_bm25_component_closure_v48.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_oracle_doc_component_closure_v48.csv`
- `outputs\eval\tatqa_100_submission_method_closure_v50\tatqa_100_open_bm25_method_closure_v50.csv`
- `outputs\eval\tatqa_100_submission_method_closure_v50\tatqa_100_oracle_doc_method_closure_v50.csv`

### Fields

- `method`
- `accuracy`
- `answer_supported`

### Filters

- Full EviGraph only
- Oracle-doc and Open BM25 only

### Sample sizes

- FinQA-600 Oracle-doc: n=600
- FinQA-600 Open BM25: n=600
- TAT-QA-100 Oracle-doc: n=100
- TAT-QA-100 Open BM25: n=100

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'dataset': 'FinQA-600', 'setting': 'Oracle-doc', 'EM': 0.503333, 'answer_support': 0.82}` |
| 2 | `{'dataset': 'FinQA-600', 'setting': 'Open BM25', 'EM': 0.376667, 'answer_support': 0.786667}` |
| 3 | `{'dataset': 'TAT-QA-100', 'setting': 'Oracle-doc', 'EM': 0.52, 'answer_support': 0.75}` |
| 4 | `{'dataset': 'TAT-QA-100', 'setting': 'Open BM25', 'EM': 0.41, 'answer_support': 0.85}` |

Missing values: none detected
Aggregation/filtering: Mean accuracy and answer_supported grouped by dataset and retrieval setting.
Markdown fallback: none for plotted values; generated TAT-QA paper tables are validation sources.
Consistency: validated against TAT-QA-100 generated Markdown/LaTeX tables at displayed precision.

### Colors

- EM: #4198AC
- Answer Support: #ED8D5A

## fig_tatqa_subset_size_sweep

### Output files

- `paper\figures\experiment_results\fig_tatqa_subset_size_sweep.pdf`
- `paper\figures\experiment_results\fig_tatqa_subset_size_sweep.png`

### Source files

- `paper\generated\tatqa_100_portability_v50\tatqa_100_results.md`
- `paper\generated\tatqa_20_cross_benchmark\tatqa_20_results.md`
- `paper\generated\tatqa_50_cross_benchmark\tatqa_50_results.md`

### Fields

- `setting`
- `method`
- `n`
- `EM`
- `support`
- `source_hit@8`

### Filters

- TAT-QA only
- Full EviGraph rows only
- Oracle-doc and Open BM25 settings

### Sample sizes

- TAT-QA-20: Oracle-doc and Open BM25
- TAT-QA-50: Oracle-doc and Open BM25
- TAT-QA-100: Oracle-doc and Open BM25

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'sample_size': 20, 'setting': 'Open BM25', 'method': 'Full EviGraph', 'EM': 0.45, 'answer_support': 0.85, 'source_hit@8': 1.0}` |
| 2 | `{'sample_size': 50, 'setting': 'Open BM25', 'method': 'Full EviGraph v47', 'EM': 0.4, 'answer_support': 0.92, 'source_hit@8': 0.96}` |
| 3 | `{'sample_size': 50, 'setting': 'Open BM25', 'method': 'Full EviGraph v48', 'EM': 0.42, 'answer_support': 0.9, 'source_hit@8': 0.96}` |
| 4 | `{'sample_size': 50, 'setting': 'Open BM25', 'method': 'Full EviGraph v49', 'EM': 0.44, 'answer_support': 0.9, 'source_hit@8': 0.96}` |
| 5 | `{'sample_size': 50, 'setting': 'Open BM25', 'method': 'Full EviGraph v50', 'EM': 0.46, 'answer_support': 0.9, 'source_hit@8': 0.96}` |
| 6 | `{'sample_size': 100, 'setting': 'Open BM25', 'method': 'Full EviGraph v50', 'EM': 0.41, 'answer_support': 0.85, 'source_hit@8': 0.9}` |
| 7 | `{'sample_size': 20, 'setting': 'Oracle-doc', 'method': 'Full EviGraph', 'EM': 0.5, 'answer_support': 0.8, 'source_hit@8': None}` |
| 8 | `{'sample_size': 50, 'setting': 'Oracle-doc', 'method': 'Full EviGraph v47', 'EM': 0.48, 'answer_support': 0.78, 'source_hit@8': None}` |
| 9 | `{'sample_size': 50, 'setting': 'Oracle-doc', 'method': 'Full EviGraph v48', 'EM': 0.52, 'answer_support': 0.74, 'source_hit@8': None}` |
| 10 | `{'sample_size': 50, 'setting': 'Oracle-doc', 'method': 'Full EviGraph v49', 'EM': 0.52, 'answer_support': 0.74, 'source_hit@8': None}` |
| 11 | `{'sample_size': 50, 'setting': 'Oracle-doc', 'method': 'Full EviGraph v50', 'EM': 0.54, 'answer_support': 0.74, 'source_hit@8': None}` |
| 12 | `{'sample_size': 100, 'setting': 'Oracle-doc', 'method': 'Full EviGraph v50', 'EM': 0.52, 'answer_support': 0.75, 'source_hit@8': None}` |

Missing values: source_hit@8 is n/a for Oracle-doc by design; EM/support complete.
Aggregation/filtering: No aggregation across files; plotted values are read directly from generated TAT-QA result tables.
Markdown fallback: generated Markdown tables are the primary source because the sweep spans separate pilot/portability reports.
Consistency: subset sizes and values are constrained by n fields in each generated report; no invented sweep points.

### Colors

- Oracle-doc EM: #51999F
- Open BM25 EM: #ED8D5A
- Oracle-doc Support: #4198AC
- Open BM25 Support: #DBCB92
- best marker: #222222

## fig_marag_style_main_results_table

### Output files

- `paper\figures\experiment_results\fig_marag_style_main_results_table.pdf`
- `paper\figures\experiment_results\fig_marag_style_main_results_table.png`

### Source files

- `outputs\eval\finqa_600_retrieval_portfolio_v46_guarded_confidence\finqa_600_subset_open_portfolio_bm25_hybrid_v46_guarded_confidence.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_open_bm25_component_closure_v48.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_oracle_doc_component_closure_v48.csv`
- `outputs\eval\finqa_600_submission_component_closure_v48\finqa_600_subset_source_rerank_component_closure_v48.csv`
- `outputs\eval\tatqa_100_submission_method_closure_v50\tatqa_100_open_bm25_method_closure_v50.csv`
- `outputs\eval\tatqa_100_submission_method_closure_v50\tatqa_100_oracle_doc_method_closure_v50.csv`

### Fields

- `setting`
- `method`
- `n`
- `accuracy`
- `answer_supported`

### Filters

- Main FinQA-600 methods, guarded portfolio, and TAT-QA-100 Full EviGraph rows

### Sample sizes

- FinQA-600 BM25 + source rerank: n=600
- FinQA-600 Open BM25: n=600
- FinQA-600 Oracle-doc: n=600
- TAT-QA-100 Open BM25: n=100
- TAT-QA-100 Oracle-doc: n=100

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'dataset': 'FinQA-600', 'setting': 'Oracle-doc', 'method': 'Direct RAG', 'n': 600, 'EM': 0.46, 'answer_support': 0.746667, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_oracle_doc_component_closure_v48.csv'}` |
| 2 | `{'dataset': 'FinQA-600', 'setting': 'Oracle-doc', 'method': 'Retrieve-then-program', 'n': 600, 'EM': 0.485, 'answer_support': 0.796667, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_oracle_doc_component_closure_v48.csv'}` |
| 3 | `{'dataset': 'FinQA-600', 'setting': 'Oracle-doc', 'method': 'Utility-only', 'n': 600, 'EM': 0.478333, 'answer_support': 0.793333, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_oracle_doc_component_closure_v48.csv'}` |
| 4 | `{'dataset': 'FinQA-600', 'setting': 'Oracle-doc', 'method': 'No operation planner', 'n': 600, 'EM': 0.445, 'answer_support': 0.748333, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_oracle_doc_component_closure_v48.csv'}` |
| 5 | `{'dataset': 'FinQA-600', 'setting': 'Oracle-doc', 'method': 'Full EviGraph', 'n': 600, 'EM': 0.503333, 'answer_support': 0.82, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_oracle_doc_component_closure_v48.csv'}` |
| 6 | `{'dataset': 'FinQA-600', 'setting': 'Open BM25', 'method': 'Direct RAG', 'n': 600, 'EM': 0.32, 'answer_support': 0.67, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_open_bm25_component_closure_v48.csv'}` |
| 7 | `{'dataset': 'FinQA-600', 'setting': 'Open BM25', 'method': 'Retrieve-then-program', 'n': 600, 'EM': 0.348333, 'answer_support': 0.726667, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_open_bm25_component_closure_v48.csv'}` |
| 8 | `{'dataset': 'FinQA-600', 'setting': 'Open BM25', 'method': 'Utility-only', 'n': 600, 'EM': 0.315, 'answer_support': 0.706667, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_open_bm25_component_closure_v48.csv'}` |
| 9 | `{'dataset': 'FinQA-600', 'setting': 'Open BM25', 'method': 'No operation planner', 'n': 600, 'EM': 0.325, 'answer_support': 0.706667, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_open_bm25_component_closure_v48.csv'}` |
| 10 | `{'dataset': 'FinQA-600', 'setting': 'Open BM25', 'method': 'Full EviGraph', 'n': 600, 'EM': 0.376667, 'answer_support': 0.786667, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_open_bm25_component_closure_v48.csv'}` |
| 11 | `{'dataset': 'FinQA-600', 'setting': 'BM25 + source rerank', 'method': 'Direct RAG', 'n': 600, 'EM': 0.46, 'answer_support': 0.733333, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_source_rerank_component_closure_v48.csv'}` |
| 12 | `{'dataset': 'FinQA-600', 'setting': 'BM25 + source rerank', 'method': 'Retrieve-then-program', 'n': 600, 'EM': 0.483333, 'answer_support': 0.781667, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_source_rerank_component_closure_v48.csv'}` |
| 13 | `{'dataset': 'FinQA-600', 'setting': 'BM25 + source rerank', 'method': 'Utility-only', 'n': 600, 'EM': 0.44, 'answer_support': 0.758333, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_source_rerank_component_closure_v48.csv'}` |
| 14 | `{'dataset': 'FinQA-600', 'setting': 'BM25 + source rerank', 'method': 'No operation planner', 'n': 600, 'EM': 0.443333, 'answer_support': 0.748333, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_source_rerank_component_closure_v48.csv'}` |
| 15 | `{'dataset': 'FinQA-600', 'setting': 'BM25 + source rerank', 'method': 'Full EviGraph', 'n': 600, 'EM': 0.501667, 'answer_support': 0.821667, 'source': 'outputs\\eval\\finqa_600_submission_component_closure_v48\\finqa_600_subset_source_rerank_component_closure_v48.csv'}` |
| 16 | `{'dataset': 'FinQA-600', 'setting': 'Open BM25', 'method': 'Guarded portfolio', 'n': 600, 'EM': 0.406667, 'answer_support': 0.806667, 'source': 'outputs\\eval\\finqa_600_retrieval_portfolio_v46_guarded_confidence\\finqa_600_subset_open_portfolio_bm25_hybrid_v46_guarded_confidence.csv'}` |
| 17 | `{'dataset': 'TAT-QA-100', 'setting': 'Oracle-doc', 'method': 'Full EviGraph', 'n': 100, 'EM': 0.52, 'answer_support': 0.75, 'source': 'outputs\\eval\\tatqa_100_submission_method_closure_v50\\tatqa_100_oracle_doc_method_closure_v50.csv'}` |
| 18 | `{'dataset': 'TAT-QA-100', 'setting': 'Open BM25', 'method': 'Full EviGraph', 'n': 100, 'EM': 0.41, 'answer_support': 0.85, 'source': 'outputs\\eval\\tatqa_100_submission_method_closure_v50\\tatqa_100_open_bm25_method_closure_v50.csv'}` |

Missing values: none detected
Aggregation/filtering: Table values are the same CSV/report means used by the plotted figures.
Markdown fallback: none for FinQA/TAT-QA EM/support; portfolio row uses portfolio CSV.
Consistency: values already passed strict validation against generated summary and LaTeX assets.

### Colors

- mostly black-and-white MA-RAG-style table
- highlight fill: #FFF4ED
- section fill: #F2F2F2

## fig_tatqa_repair_trajectory

### Output files

- `paper\figures\experiment_results\fig_tatqa_repair_trajectory.pdf`
- `paper\figures\experiment_results\fig_tatqa_repair_trajectory.png`

### Source files

- `outputs\eval\tatqa_50_activity_share_average_v49\summary.md`
- `outputs\eval\tatqa_50_direction_repair_v47\summary.md`
- `outputs\eval\tatqa_50_local_planner\summary.md`
- `outputs\eval\tatqa_50_non_vested_ratio_v48\summary.md`
- `outputs\eval\tatqa_50_senior_notes_issuance_sum_v50\summary.md`

### Fields

- `setting`
- `method/version`
- `n`
- `EM`
- `support`
- `source_hit@8`

### Filters

- TAT-QA-50 repair sequence
- Oracle-doc and Open BM25

### Sample sizes

- TAT-QA-50 for all repair rounds

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'version': 'base', 'setting': 'Open BM25', 'EM': 0.36, 'answer_support': 0.92, 'source_hit@8': None}` |
| 2 | `{'version': 'v47', 'setting': 'Open BM25', 'EM': 0.4, 'answer_support': 0.92, 'source_hit@8': None}` |
| 3 | `{'version': 'v48', 'setting': 'Open BM25', 'EM': 0.42, 'answer_support': 0.9, 'source_hit@8': None}` |
| 4 | `{'version': 'v49', 'setting': 'Open BM25', 'EM': 0.44, 'answer_support': 0.9, 'source_hit@8': None}` |
| 5 | `{'version': 'v50', 'setting': 'Open BM25', 'EM': 0.46, 'answer_support': 0.9, 'source_hit@8': None}` |
| 6 | `{'version': 'base', 'setting': 'Oracle-doc', 'EM': 0.42, 'answer_support': 0.78, 'source_hit@8': None}` |
| 7 | `{'version': 'v47', 'setting': 'Oracle-doc', 'EM': 0.48, 'answer_support': 0.78, 'source_hit@8': None}` |
| 8 | `{'version': 'v48', 'setting': 'Oracle-doc', 'EM': 0.52, 'answer_support': 0.74, 'source_hit@8': None}` |
| 9 | `{'version': 'v49', 'setting': 'Oracle-doc', 'EM': 0.52, 'answer_support': 0.74, 'source_hit@8': None}` |
| 10 | `{'version': 'v50', 'setting': 'Oracle-doc', 'EM': 0.54, 'answer_support': 0.74, 'source_hit@8': None}` |

Missing values: none detected
Aggregation/filtering: No aggregation; values are parsed from per-round TAT-QA-50 summary tables.
Markdown fallback: generated Markdown summaries are the primary source for this trajectory.
Consistency: all repair-round values come from outputs/eval summary tables.

### Colors

- Oracle-doc: #51999F
- Open BM25: #ED8D5A

## fig_tatqa_repair_diagnostic_grid

### Output files

- `paper\figures\experiment_results\fig_tatqa_repair_diagnostic_grid.pdf`
- `paper\figures\experiment_results\fig_tatqa_repair_diagnostic_grid.png`

### Source files

- `outputs\eval\tatqa_50_activity_share_average_v49\summary.md`
- `outputs\eval\tatqa_50_direction_repair_v47\summary.md`
- `outputs\eval\tatqa_50_local_planner\summary.md`
- `outputs\eval\tatqa_50_non_vested_ratio_v48\summary.md`
- `outputs\eval\tatqa_50_senior_notes_issuance_sum_v50\summary.md`

### Fields

- `accuracy`
- `answer_supported`
- `supported_wrong`
- `calculation_supported`
- `operation_semantics_checked`
- `row_operation_grounded`

### Filters

- TAT-QA-50 full_evigraph rows
- Oracle-doc and Open BM25
- repair rounds base/v47/v48/v49/v50

### Sample sizes

- n=50 per setting per repair round

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'version': 'base', 'setting': 'Open BM25', 'EM': 0.36, 'answer_support': 0.92, 'supported_wrong': 0.56, 'calculation_supported': 0.78, 'operation_semantics_checked': 0.92, 'row_operation_grounded': 0.92}` |
| 2 | `{'version': 'v47', 'setting': 'Open BM25', 'EM': 0.4, 'answer_support': 0.92, 'supported_wrong': 0.52, 'calculation_supported': 0.78, 'operation_semantics_checked': 0.92, 'row_operation_grounded': 0.92}` |
| 3 | `{'version': 'v48', 'setting': 'Open BM25', 'EM': 0.42, 'answer_support': 0.9, 'supported_wrong': 0.5, 'calculation_supported': 0.78, 'operation_semantics_checked': 0.9, 'row_operation_grounded': 0.9}` |
| 4 | `{'version': 'v49', 'setting': 'Open BM25', 'EM': 0.44, 'answer_support': 0.9, 'supported_wrong': 0.48, 'calculation_supported': 0.78, 'operation_semantics_checked': 0.9, 'row_operation_grounded': 0.9}` |
| 5 | `{'version': 'v50', 'setting': 'Open BM25', 'EM': 0.46, 'answer_support': 0.9, 'supported_wrong': 0.46, 'calculation_supported': 0.8, 'operation_semantics_checked': 0.9, 'row_operation_grounded': 0.9}` |
| 6 | `{'version': 'base', 'setting': 'Oracle-doc', 'EM': 0.42, 'answer_support': 0.78, 'supported_wrong': 0.4, 'calculation_supported': 0.64, 'operation_semantics_checked': 0.82, 'row_operation_grounded': 0.78}` |
| 7 | `{'version': 'v47', 'setting': 'Oracle-doc', 'EM': 0.48, 'answer_support': 0.78, 'supported_wrong': 0.34, 'calculation_supported': 0.64, 'operation_semantics_checked': 0.82, 'row_operation_grounded': 0.78}` |
| 8 | `{'version': 'v48', 'setting': 'Oracle-doc', 'EM': 0.52, 'answer_support': 0.74, 'supported_wrong': 0.3, 'calculation_supported': 0.64, 'operation_semantics_checked': 0.78, 'row_operation_grounded': 0.74}` |
| 9 | `{'version': 'v49', 'setting': 'Oracle-doc', 'EM': 0.52, 'answer_support': 0.74, 'supported_wrong': 0.3, 'calculation_supported': 0.64, 'operation_semantics_checked': 0.78, 'row_operation_grounded': 0.74}` |
| 10 | `{'version': 'v50', 'setting': 'Oracle-doc', 'EM': 0.54, 'answer_support': 0.74, 'supported_wrong': 0.28, 'calculation_supported': 0.66, 'operation_semantics_checked': 0.78, 'row_operation_grounded': 0.74}` |

Missing values: none detected
Aggregation/filtering: No aggregation; each point is read from the per-round generated summary table.
Markdown fallback: outputs/eval summary.md files are the primary source.
Consistency: Uses the same source summaries as the TAT-QA repair trajectory; no invented diagnostics.

### Colors

- Oracle-doc: #51999F
- Open BM25: #ED8D5A

## fig_selector_lambda_sweep

### Output files

- `paper\figures\experiment_results\fig_selector_lambda_sweep.pdf`
- `paper\figures\experiment_results\fig_selector_lambda_sweep.png`

### Source files

- `outputs\eval\finqa_600_retrieval_portfolio_v46_guarded_confidence\finqa_600_subset_open_portfolio_bm25_hybrid_v46_guarded_confidence.csv`

### Fields

- `primary_prediction`
- `candidate_prediction`
- `primary_calculation`
- `candidate_calculation`
- `primary_accuracy`
- `candidate_accuracy`

### Filters

- FinQA-600 v46 guarded-confidence portfolio rows
- no-gold selector scores; gold accuracy used only for post-hoc plotting

### Sample sizes

- n=600; lambda grid=0.00..1.00 step=0.05

### Final plotted values

| item | value |
| --- | --- |
| 1 | `{'selector': 'BM25 primary', 'lambda': 0.0, 'EM': 0.376667, 'switch_rate': 0.0, 'accepted_gain': 0.0, 'accepted_loss': 0.0}` |
| 2 | `{'selector': 'BM25 primary', 'lambda': 0.25, 'EM': 0.376667, 'switch_rate': 0.0, 'accepted_gain': 0.0, 'accepted_loss': 0.0}` |
| 3 | `{'selector': 'BM25 primary', 'lambda': 0.5, 'EM': 0.376667, 'switch_rate': 0.0, 'accepted_gain': 0.0, 'accepted_loss': 0.0}` |
| 4 | `{'selector': 'BM25 primary', 'lambda': 0.75, 'EM': 0.376667, 'switch_rate': 0.0, 'accepted_gain': 0.0, 'accepted_loss': 0.0}` |
| 5 | `{'selector': 'BM25 primary', 'lambda': 1.0, 'EM': 0.376667, 'switch_rate': 0.0, 'accepted_gain': 0.0, 'accepted_loss': 0.0}` |
| 6 | `{'selector': '$\\hat{s}_{\\mathrm{num}}$', 'lambda': 0.0, 'EM': 0.393333, 'switch_rate': 0.44, 'accepted_gain': 0.026667, 'accepted_loss': 0.01}` |
| 7 | `{'selector': '$\\hat{s}_{\\mathrm{num}}$', 'lambda': 0.25, 'EM': 0.393333, 'switch_rate': 0.44, 'accepted_gain': 0.026667, 'accepted_loss': 0.01}` |
| 8 | `{'selector': '$\\hat{s}_{\\mathrm{num}}$', 'lambda': 0.5, 'EM': 0.393333, 'switch_rate': 0.43, 'accepted_gain': 0.026667, 'accepted_loss': 0.01}` |
| 9 | `{'selector': '$\\hat{s}_{\\mathrm{num}}$', 'lambda': 0.75, 'EM': 0.393333, 'switch_rate': 0.191667, 'accepted_gain': 0.02, 'accepted_loss': 0.003333}` |
| 10 | `{'selector': '$\\hat{s}_{\\mathrm{num}}$', 'lambda': 1.0, 'EM': 0.376667, 'switch_rate': 0.0, 'accepted_gain': 0.0, 'accepted_loss': 0.0}` |
| 11 | `{'selector': '$\\hat{s}_{\\mathrm{evi}}$', 'lambda': 0.0, 'EM': 0.363333, 'switch_rate': 1.0, 'accepted_gain': 0.036667, 'accepted_loss': 0.05}` |
| 12 | `{'selector': '$\\hat{s}_{\\mathrm{evi}}$', 'lambda': 0.25, 'EM': 0.361667, 'switch_rate': 0.443333, 'accepted_gain': 0.015, 'accepted_loss': 0.03}` |
| 13 | `{'selector': '$\\hat{s}_{\\mathrm{evi}}$', 'lambda': 0.5, 'EM': 0.373333, 'switch_rate': 0.238333, 'accepted_gain': 0.008333, 'accepted_loss': 0.011667}` |
| 14 | `{'selector': '$\\hat{s}_{\\mathrm{evi}}$', 'lambda': 0.75, 'EM': 0.375, 'switch_rate': 0.123333, 'accepted_gain': 0.005, 'accepted_loss': 0.006667}` |
| 15 | `{'selector': '$\\hat{s}_{\\mathrm{evi}}$', 'lambda': 1.0, 'EM': 0.376667, 'switch_rate': 0.0, 'accepted_gain': 0.0, 'accepted_loss': 0.0}` |
| 16 | `{'selector': '$\\hat{s}_{\\mathrm{ans}}$', 'lambda': 0.0, 'EM': 0.388333, 'switch_rate': 0.031667, 'accepted_gain': 0.011667, 'accepted_loss': 0.0}` |
| 17 | `{'selector': '$\\hat{s}_{\\mathrm{ans}}$', 'lambda': 0.25, 'EM': 0.386667, 'switch_rate': 0.03, 'accepted_gain': 0.01, 'accepted_loss': 0.0}` |
| 18 | `{'selector': '$\\hat{s}_{\\mathrm{ans}}$', 'lambda': 0.5, 'EM': 0.386667, 'switch_rate': 0.03, 'accepted_gain': 0.01, 'accepted_loss': 0.0}` |
| 19 | `{'selector': '$\\hat{s}_{\\mathrm{ans}}$', 'lambda': 0.75, 'EM': 0.386667, 'switch_rate': 0.03, 'accepted_gain': 0.01, 'accepted_loss': 0.0}` |
| 20 | `{'selector': '$\\hat{s}_{\\mathrm{ans}}$', 'lambda': 1.0, 'EM': 0.376667, 'switch_rate': 0.0, 'accepted_gain': 0.0, 'accepted_loss': 0.0}` |
| 21 | `{'selector': '$s_{\\mathrm{EviGraph}}$', 'lambda': 0.0, 'EM': 0.363333, 'switch_rate': 1.0, 'accepted_gain': 0.036667, 'accepted_loss': 0.05}` |
| 22 | `{'selector': '$s_{\\mathrm{EviGraph}}$', 'lambda': 0.25, 'EM': 0.373333, 'switch_rate': 0.481667, 'accepted_gain': 0.026667, 'accepted_loss': 0.03}` |
| 23 | `{'selector': '$s_{\\mathrm{EviGraph}}$', 'lambda': 0.5, 'EM': 0.386667, 'switch_rate': 0.453333, 'accepted_gain': 0.026667, 'accepted_loss': 0.016667}` |
| 24 | `{'selector': '$s_{\\mathrm{EviGraph}}$', 'lambda': 0.75, 'EM': 0.39, 'switch_rate': 0.433333, 'accepted_gain': 0.026667, 'accepted_loss': 0.013333}` |
| 25 | `{'selector': '$s_{\\mathrm{EviGraph}}$', 'lambda': 1.0, 'EM': 0.376667, 'switch_rate': 0.0, 'accepted_gain': 0.0, 'accepted_loss': 0.0}` |

Missing values: none detected
Aggregation/filtering: For each selector and lambda, choose candidate when no-gold score > lambda; EM/gain/loss are sample means.
Markdown fallback: none; row-level CSV is the source for the sweep.
Consistency: The combined selector recovers the same primary/candidate evidence-state family as the guarded portfolio analysis without using labels for selection.

### Colors

- BM25 primary: #4C78A8
- $\hat{s}_{\mathrm{num}}$: #F58518
- $\hat{s}_{\mathrm{evi}}$: #54A24B
- $\hat{s}_{\mathrm{ans}}$: #E45756
- $s_{\mathrm{EviGraph}}$: #8E6BBE
