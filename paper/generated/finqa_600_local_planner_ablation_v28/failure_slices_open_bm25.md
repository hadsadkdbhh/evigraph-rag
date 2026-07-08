# Failure Slice Analysis

- CSV: `outputs\eval\finqa_600_local_planner_ablation_v28\finqa_600_subset_open_bm25_ablation_v28.csv`
- Questions: `outputs\eval\finqa_600_local_planner_ablation_v28\finqa_questions.jsonl`
- Retrieval mode: `open`
- Method: `full_evigraph`
- Failed rows: 384 / 600

## Source Slices

| slice | count |
| --- | ---: |
| source_hit_gold_number_missing | 254 |
| source_missing | 82 |
| source_hit_gold_number_present | 48 |

## Intent Slices

| intent | count |
| --- | ---: |
| percent_change | 105 |
| ratio_percent | 83 |
| lookup_or_other | 74 |
| sum_or_lookup | 63 |
| average | 30 |
| difference | 15 |
| ratio | 14 |

## Support Slices

| slice | count |
| --- | ---: |
| textual_or_insufficient | 252 |
| supported_wrong_numeric | 118 |
| unsupported_wrong_numeric | 14 |

## Joint Source x Intent

| source/intent | count |
| --- | ---: |
| source_hit_gold_number_missing::percent_change | 66 |
| source_hit_gold_number_missing::ratio_percent | 58 |
| source_hit_gold_number_missing::lookup_or_other | 46 |
| source_hit_gold_number_missing::sum_or_lookup | 42 |
| source_hit_gold_number_missing::average | 26 |
| source_missing::percent_change | 25 |
| source_missing::lookup_or_other | 18 |
| source_missing::ratio_percent | 16 |
| source_hit_gold_number_present::percent_change | 14 |
| source_missing::sum_or_lookup | 14 |
| source_hit_gold_number_present::lookup_or_other | 10 |
| source_hit_gold_number_missing::ratio | 9 |
| source_hit_gold_number_present::ratio_percent | 9 |
| source_hit_gold_number_missing::difference | 7 |
| source_hit_gold_number_present::sum_or_lookup | 7 |
| source_missing::difference | 5 |
| source_hit_gold_number_present::average | 3 |
| source_hit_gold_number_present::difference | 3 |
| source_missing::ratio | 3 |
| source_hit_gold_number_present::ratio | 2 |

## Examples

### source_missing

- `EW/2016/page_79.pdf-3`
  - query: what is the current ratio?
  - gold: `-0.85`
  - prediction: `Based on the selected evidence: for intersegment revenue as if the revenue were from third parties and at what management believes are current market prices...`
  - source=source_missing, intent=ratio, support=textual_or_insufficient, source_rank=None
- `LKQ/2010/page_84.pdf-2`
  - query: what was the percentage change in rental expense for operating leases from 2009 to 2010?
  - gold: `17%`
  - prediction: `-31.4%`
  - source=source_missing, intent=percent_change, support=unsupported_wrong_numeric, source_rank=None
- `SLB/2012/page_44.pdf-1`
  - query: as of december 312012 what was the outstanding amount of share repurchase authorized in billions?
  - gold: `0.88`
  - prediction: `Based on the selected evidence: | --- | --- | | number of shares repurchased | 9.6 | 8.4 | | amount paid | $ 610.7 | $ 403.8 | | weighted average cost per sh...`
  - source=source_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=None

### ratio

- `EW/2016/page_79.pdf-3`
  - query: what is the current ratio?
  - gold: `-0.85`
  - prediction: `Based on the selected evidence: for intersegment revenue as if the revenue were from third parties and at what management believes are current market prices...`
  - source=source_missing, intent=ratio, support=textual_or_insufficient, source_rank=None
- `DISH/2013/page_138.pdf-1`
  - query: what is the tax expense related to discontinued operations in 2013?
  - gold: `7`
  - prediction: `Based on the selected evidence: # FinQA Evidence AMT/2005/page_54.pdf-2 - Source dataset: dreamerdeo/finqa - Split: validation ## Pre Text with apb no . 25 ....`
  - source=source_hit_gold_number_present, intent=ratio, support=textual_or_insufficient, source_rank=3
- `NWS/2016/page_61.pdf-1`
  - query: what on the net interest reduction of 13 million or 23% ( 23 % ) compared to 2015 what was the interest amount in 2016 in millions
  - gold: `69.5`
  - prediction: `Based on the selected evidence: # FinQA Evidence NWS/2016/page_61.pdf-1 - Source dataset: dreamerdeo/finqa - Split: validation ## Pre Text increased investme...`
  - source=source_hit_gold_number_missing, intent=ratio, support=textual_or_insufficient, source_rank=1

### textual_or_insufficient

- `EW/2016/page_79.pdf-3`
  - query: what is the current ratio?
  - gold: `-0.85`
  - prediction: `Based on the selected evidence: for intersegment revenue as if the revenue were from third parties and at what management believes are current market prices...`
  - source=source_missing, intent=ratio, support=textual_or_insufficient, source_rank=None
- `AMAT/2013/page_18.pdf-2`
  - query: what is the applied 2019s net sales in 2018 , ( in billions ) ?
  - gold: `7.22`
  - prediction: `Based on the selected evidence: tegy requires continued development of new products . the company 2019s significant investment in research , development and...`
  - source=source_hit_gold_number_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=1
- `FRT/2005/page_117.pdf-1`
  - query: what is the growth of the additions in comparison with the growth of the deductions during 2003 and 2004?
  - gold: `92%`
  - prediction: `Based on the selected evidence: columns: ['year', 'value'] rows: [['2003', '514177000.0'], ['2004', '595338000.0']] raw_text: # FinQA Evidence FRT/2005/page_...`
  - source=source_hit_gold_number_missing, intent=percent_change, support=textual_or_insufficient, source_rank=1

### source_hit_gold_number_missing

- `IP/2005/page_35.pdf-3`
  - query: what was the percent f the purchase obligations in 2006 set aside for the contract for the purchase of pulpwood , logs and wood chips
  - gold: `73.5%`
  - prediction: `8.6%`
  - source=source_hit_gold_number_missing, intent=percent_change, support=supported_wrong_numeric, source_rank=1
- `HWM/2017/page_41.pdf-2`
  - query: considering the second quarter of 2017 , what is the average sale price per share of the company 2019s common stock?
  - gold: `25.20`
  - prediction: `26.2`
  - source=source_hit_gold_number_missing, intent=average, support=supported_wrong_numeric, source_rank=6
- `AMAT/2013/page_18.pdf-2`
  - query: what is the applied 2019s net sales in 2018 , ( in billions ) ?
  - gold: `7.22`
  - prediction: `Based on the selected evidence: tegy requires continued development of new products . the company 2019s significant investment in research , development and...`
  - source=source_hit_gold_number_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=1

### percent_change

- `IP/2005/page_35.pdf-3`
  - query: what was the percent f the purchase obligations in 2006 set aside for the contract for the purchase of pulpwood , logs and wood chips
  - gold: `73.5%`
  - prediction: `8.6%`
  - source=source_hit_gold_number_missing, intent=percent_change, support=supported_wrong_numeric, source_rank=1
- `FRT/2005/page_117.pdf-1`
  - query: what is the growth of the additions in comparison with the growth of the deductions during 2003 and 2004?
  - gold: `92%`
  - prediction: `Based on the selected evidence: columns: ['year', 'value'] rows: [['2003', '514177000.0'], ['2004', '595338000.0']] raw_text: # FinQA Evidence FRT/2005/page_...`
  - source=source_hit_gold_number_missing, intent=percent_change, support=textual_or_insufficient, source_rank=1
- `LKQ/2010/page_84.pdf-2`
  - query: what was the percentage change in rental expense for operating leases from 2009 to 2010?
  - gold: `17%`
  - prediction: `-31.4%`
  - source=source_missing, intent=percent_change, support=unsupported_wrong_numeric, source_rank=None

### supported_wrong_numeric

- `IP/2005/page_35.pdf-3`
  - query: what was the percent f the purchase obligations in 2006 set aside for the contract for the purchase of pulpwood , logs and wood chips
  - gold: `73.5%`
  - prediction: `8.6%`
  - source=source_hit_gold_number_missing, intent=percent_change, support=supported_wrong_numeric, source_rank=1
- `HWM/2017/page_41.pdf-2`
  - query: considering the second quarter of 2017 , what is the average sale price per share of the company 2019s common stock?
  - gold: `25.20`
  - prediction: `26.2`
  - source=source_hit_gold_number_missing, intent=average, support=supported_wrong_numeric, source_rank=6
- `IP/2007/page_75.pdf-2`
  - query: what percentage of december 31 , 2007 , total future minimum commitments under existing non-cancelable operating leases and purchase obligations were due to lease obligations for the year of 2008?
  - gold: `7%`
  - prediction: `46.9%`
  - source=source_hit_gold_number_present, intent=ratio_percent, support=supported_wrong_numeric, source_rank=1

### average

- `HWM/2017/page_41.pdf-2`
  - query: considering the second quarter of 2017 , what is the average sale price per share of the company 2019s common stock?
  - gold: `25.20`
  - prediction: `26.2`
  - source=source_hit_gold_number_missing, intent=average, support=supported_wrong_numeric, source_rank=6
- `AES/2017/page_157.pdf-2`
  - query: as of december 31 , 2017 , assuming an average price per share of $ 12.12 , what would be the cost in millions to repurchase all the remaining shares remaining in the program?
  - gold: `2981.5`
  - prediction: `Based on the selected evidence: columns: ['year', 'value'] rows: [['2010', '2017.0'], ['2017', '2015.0']] raw_text: # FinQA Evidence AES/2017/page_157.pdf-2...`
  - source=source_hit_gold_number_missing, intent=average, support=textual_or_insufficient, source_rank=1
- `AES/2015/page_117.pdf-3`
  - query: what were average proportional recoverable environmental capital expenditures for the years december 31 , 2015 , 2014 and 2013 , in millions?
  - gold: `159.3`
  - prediction: `-61`
  - source=source_hit_gold_number_missing, intent=average, support=unsupported_wrong_numeric, source_rank=1

### lookup_or_other

- `AMAT/2013/page_18.pdf-2`
  - query: what is the applied 2019s net sales in 2018 , ( in billions ) ?
  - gold: `7.22`
  - prediction: `Based on the selected evidence: tegy requires continued development of new products . the company 2019s significant investment in research , development and...`
  - source=source_hit_gold_number_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=1
- `PM/2017/page_38.pdf-2`
  - query: what are the net earnings attributable to pmi in the previous year , ( in billions ) ?
  - gold: `7.0`
  - prediction: `Based on the selected evidence: ( 201ceps 201d ) were calculated using the following: . ## Table | ( in millions ) | for the years ended december 31 , 2017 |...`
  - source=source_hit_gold_number_present, intent=lookup_or_other, support=textual_or_insufficient, source_rank=4
- `SLB/2012/page_44.pdf-1`
  - query: as of december 312012 what was the outstanding amount of share repurchase authorized in billions?
  - gold: `0.88`
  - prediction: `Based on the selected evidence: | --- | --- | | number of shares repurchased | 9.6 | 8.4 | | amount paid | $ 610.7 | $ 403.8 | | weighted average cost per sh...`
  - source=source_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=None

### ratio_percent

- `TROW/2010/page_22.pdf-4`
  - query: what percentage of tangible book value at december 31 , 2010 is due to cash and cash equivalents and mutual fund investment holdings?
  - gold: `58%`
  - prediction: `Based on the selected evidence: t a l r e s o u r c e s a n d l i q u i d i t y . during 2010 , stockholders 2019 equity increased from $ 2.9 billion to $ 3....`
  - source=source_hit_gold_number_missing, intent=ratio_percent, support=textual_or_insufficient, source_rank=1
- `RE/2017/page_159.pdf-1`
  - query: at december 31 , 2017 under the 2010 employee plan what was the percent of shares that had been granted
  - gold: `36.2%`
  - prediction: `Based on the selected evidence: . aside from litigation and arbitrations related to these insurance and reinsurance agreements , the company is not a party t...`
  - source=source_hit_gold_number_missing, intent=ratio_percent, support=textual_or_insufficient, source_rank=1
- `IP/2007/page_75.pdf-2`
  - query: what percentage of december 31 , 2007 , total future minimum commitments under existing non-cancelable operating leases and purchase obligations were due to lease obligations for the year of 2008?
  - gold: `7%`
  - prediction: `46.9%`
  - source=source_hit_gold_number_present, intent=ratio_percent, support=supported_wrong_numeric, source_rank=1

### unsupported_wrong_numeric

- `LKQ/2010/page_84.pdf-2`
  - query: what was the percentage change in rental expense for operating leases from 2009 to 2010?
  - gold: `17%`
  - prediction: `-31.4%`
  - source=source_missing, intent=percent_change, support=unsupported_wrong_numeric, source_rank=None
- `JPM/2008/page_85.pdf-4`
  - query: assuming a 5% ( 5 % ) rate of return , what would the earnings be ( in millions ) on 2008 total adjusted average assets?
  - gold: `98345`
  - prediction: `696.5`
  - source=source_hit_gold_number_missing, intent=percent_change, support=unsupported_wrong_numeric, source_rank=7
- `AES/2015/page_117.pdf-3`
  - query: what were average proportional recoverable environmental capital expenditures for the years december 31 , 2015 , 2014 and 2013 , in millions?
  - gold: `159.3`
  - prediction: `-61`
  - source=source_hit_gold_number_missing, intent=average, support=unsupported_wrong_numeric, source_rank=1

### source_hit_gold_number_present

- `PM/2017/page_38.pdf-2`
  - query: what are the net earnings attributable to pmi in the previous year , ( in billions ) ?
  - gold: `7.0`
  - prediction: `Based on the selected evidence: ( 201ceps 201d ) were calculated using the following: . ## Table | ( in millions ) | for the years ended december 31 , 2017 |...`
  - source=source_hit_gold_number_present, intent=lookup_or_other, support=textual_or_insufficient, source_rank=4
- `IP/2007/page_75.pdf-2`
  - query: what percentage of december 31 , 2007 , total future minimum commitments under existing non-cancelable operating leases and purchase obligations were due to lease obligations for the year of 2008?
  - gold: `7%`
  - prediction: `46.9%`
  - source=source_hit_gold_number_present, intent=ratio_percent, support=supported_wrong_numeric, source_rank=1
- `PM/2018/page_31.pdf-1`
  - query: by what percentage will the 2019 pre-tax pension and postretirement expense be higher than that of 2018?
  - gold: `28.1%`
  - prediction: `Based on the selected evidence: would decrease our 2019 pension and postretirement .`
  - source=source_hit_gold_number_present, intent=percent_change, support=textual_or_insufficient, source_rank=1

### sum_or_lookup

- `APD/2019/page_31.pdf-1`
  - query: considering the year 2019 , what is the contribution of the first quarter in the total dividend?
  - gold: `24.01%`
  - prediction: `Based on the selected evidence: ## Post Text purchases of equity securities by the issuer on 15 september 2011 , the board of directors authorized the repurc...`
  - source=source_hit_gold_number_present, intent=sum_or_lookup, support=textual_or_insufficient, source_rank=1
- `BKR/2017/page_103.pdf-4`
  - query: what is the total value of rsus converted to bhge rsus , in millions?
  - gold: `68.3`
  - prediction: `Based on the selected evidence: ns . additionally , as a result of the acquisition of baker hughes , there were 1.7 million baker hughes restricted stock uni...`
  - source=source_hit_gold_number_missing, intent=sum_or_lookup, support=textual_or_insufficient, source_rank=1
- `CME/2017/page_97.pdf-4`
  - query: how many total votes can the class b-3 provide in 2017?
  - gold: `1300`
  - prediction: `Based on the selected evidence: ave the right to approve changes in specified rights relating to the trading privileges at cme associated with those shares ....`
  - source=source_hit_gold_number_missing, intent=sum_or_lookup, support=textual_or_insufficient, source_rank=1

### difference

- `IPG/2015/page_37.pdf-3`
  - query: what is the cash flow statement effect of the change in cash used for working capital from 2013 to 2014?
  - gold: `-121.5`
  - prediction: `-924`
  - source=source_hit_gold_number_missing, intent=difference, support=supported_wrong_numeric, source_rank=4
- `IP/2012/page_93.pdf-1`
  - query: what was the change in rent expenses between 2011 and 2012?
  - gold: `26`
  - prediction: `-6738`
  - source=source_missing, intent=difference, support=supported_wrong_numeric, source_rank=None
- `FIS/2007/page_91.pdf-1`
  - query: what is the net change in unrecognized tax benefits during 2007?
  - gold: `11918`
  - prediction: `Based on the selected evidence: december 31 2007 | $ 23743 | | amount of decreases due to lapse of the applicable statute of limitations | $ -3429 ( 3429 ) |...`
  - source=source_hit_gold_number_missing, intent=difference, support=textual_or_insufficient, source_rank=1
