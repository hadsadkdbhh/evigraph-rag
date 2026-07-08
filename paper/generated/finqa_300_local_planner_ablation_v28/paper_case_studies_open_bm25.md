# Paper Case Studies

- EviGraph CSV: `outputs\eval\finqa_300_local_planner_ablation_v28\finqa_300_subset_open_bm25_ablation_v28.csv`
- GPT CSV: `outputs\eval\finqa_300_gpt54_direct_rag_open_bm25\finqa_300_subset_open_bm25_gpt54_direct_rag.csv`
- Retrieval mode: `open`

## EviGraph Win Over Direct RAG

- id: `IPG/2015/page_48.pdf-2`
- query: what is the percentage change in interest income from 2014 to 2015?
- gold: `-16.8%`
- full EviGraph: `-16.8%`
- baseline `direct_rag`: `5.1%`
- retrieval: source_hit=True, source_rank=1, gold_number_hit=False, query_year_hit=True
- paper use: Shows which component changes the final answer on the same retrieval setting.

## Graph Selection Win Over Utility-Only

- id: `UNP/2009/page_65.pdf-2`
- query: how many options were issued under the 2001 plan as of december 31 , 2009?
- gold: `20633770`
- full EviGraph: `20633770`
- baseline `utility_only`: `Based on the selected evidence: current grants of stock options , rsus and contingent shares are made under the ppg industries , inc . amended and restated omnibus incentive pla...`
- retrieval: source_hit=True, source_rank=1, gold_number_hit=False, query_year_hit=True
- paper use: Shows which component changes the final answer on the same retrieval setting.

## Operation Planner Win

- id: `DRE/2009/page_56.pdf-1`
- query: what was the percent of the decline in net income ( loss ) attributable to common shareholders from 2007 to 2008
- gold: `-76.2%`
- full EviGraph: `-76.2%`
- baseline `evigraph_wo_operation_planner`: `Based on the selected evidence: urities , which we have applied retrospectively to prior period calculations of basic and diluted earnings per common share . pursuant to this ne...`
- retrieval: source_hit=True, source_rank=1, gold_number_hit=False, query_year_hit=True
- paper use: Shows which component changes the final answer on the same retrieval setting.

## Open Retrieval / Operand Failure

- id: `MRO/2007/page_134.pdf-3`
- query: what was the average expected life of the options for the three year period?
- gold: `5.2`
- prediction: `4.6`
- retrieval: source_hit=True, source_rank=3, gold_number_hit=True, query_year_hit=True
- paper use: Shows that retrieval can hit the right source while operand grounding still fails.

## GPT-5.4 Correct But Unsupported

- id: `INTC/2013/page_29.pdf-2`
- query: what percentage of major facilities by square footage are leased as of december 28 , 2013?
- gold: `15%`
- GPT prediction: `15.1%`
- GPT answer_supported: `False`
- retrieval: source_hit=n/a, source_rank=n/a, gold_number_hit=n/a, query_year_hit=n/a
- paper use: Shows why exact match and verifier-supported evidence should be reported separately.
