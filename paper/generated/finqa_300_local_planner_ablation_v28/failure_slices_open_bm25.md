# Failure Slice Analysis

- CSV: `outputs\eval\finqa_300_local_planner_ablation_v28\finqa_300_subset_open_bm25_ablation_v28.csv`
- Questions: `outputs\eval\finqa_300_local_planner_ablation_v28\finqa_questions.jsonl`
- Retrieval mode: `open`
- Method: `full_evigraph`
- Failed rows: 145 / 300

## Source Slices

| slice | count |
| --- | ---: |
| source_hit_gold_number_missing | 93 |
| source_missing | 30 |
| source_hit_gold_number_present | 22 |

## Intent Slices

| intent | count |
| --- | ---: |
| percent_change | 40 |
| lookup_or_other | 31 |
| ratio_percent | 27 |
| sum_or_lookup | 18 |
| average | 11 |
| difference | 10 |
| ratio | 8 |

## Support Slices

| slice | count |
| --- | ---: |
| textual_or_insufficient | 93 |
| supported_wrong_numeric | 46 |
| unsupported_wrong_numeric | 6 |

## Joint Source x Intent

| source/intent | count |
| --- | ---: |
| source_hit_gold_number_missing::percent_change | 25 |
| source_hit_gold_number_missing::lookup_or_other | 21 |
| source_hit_gold_number_missing::ratio_percent | 18 |
| source_missing::percent_change | 10 |
| source_hit_gold_number_missing::average | 9 |
| source_hit_gold_number_missing::sum_or_lookup | 9 |
| source_hit_gold_number_missing::difference | 7 |
| source_missing::lookup_or_other | 7 |
| source_hit_gold_number_present::percent_change | 5 |
| source_hit_gold_number_present::ratio_percent | 5 |
| source_missing::sum_or_lookup | 5 |
| source_hit_gold_number_missing::ratio | 4 |
| source_hit_gold_number_present::sum_or_lookup | 4 |
| source_missing::ratio_percent | 4 |
| source_hit_gold_number_present::lookup_or_other | 3 |
| source_hit_gold_number_present::average | 2 |
| source_hit_gold_number_present::ratio | 2 |
| source_missing::difference | 2 |
| source_missing::ratio | 2 |
| source_hit_gold_number_present::difference | 1 |

## Examples

### source_missing

- `APD/2019/page_48.pdf-2`
  - query: considering the year 2018 , what is the cash flow result?
  - gold: `-454.2`
  - prediction: `Based on the selected evidence: be as the amounts depend on , among other factors , future employee stock option exercises . due to the our tax loss position...`
  - source=source_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=None
- `GPN/2017/page_77.pdf-3`
  - query: what are the total amount of net tangible assets obtained through the acquisition?
  - gold: `$ 62154`
  - prediction: `Based on the selected evidence: # FinQA Evidence EW/2017/page_82.pdf-2 - Source dataset: dreamerdeo/finqa - Split: validation ## Pre Text edwards lifescience...`
  - source=source_missing, intent=sum_or_lookup, support=textual_or_insufficient, source_rank=None
- `RE/2015/page_33.pdf-2`
  - query: what is the percentage change in average of investments from 2014 to 2015?
  - gold: `3.6%`
  - prediction: `5.1%`
  - source=source_missing, intent=percent_change, support=supported_wrong_numeric, source_rank=None

### lookup_or_other

- `APD/2019/page_48.pdf-2`
  - query: considering the year 2018 , what is the cash flow result?
  - gold: `-454.2`
  - prediction: `Based on the selected evidence: be as the amounts depend on , among other factors , future employee stock option exercises . due to the our tax loss position...`
  - source=source_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=None
- `MRO/2017/page_111.pdf-2`
  - query: what was purchases of reserves in place in 2016?
  - gold: `-13`
  - prediction: `Based on the selected evidence: iness and 10 mmboe associated with divestitures of certain conventional assets in oklahoma and colorado . see item 8 . financ...`
  - source=source_hit_gold_number_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=1
- `HUM/2017/page_133.pdf-3`
  - query: what was the number of shares issued in 2015 in millions
  - gold: `149`
  - prediction: `Based on the selected evidence: $ 250 million , three-year senior secured revolving credit facility . as a result of the citadel investment in november 2007...`
  - source=source_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=None

### textual_or_insufficient

- `APD/2019/page_48.pdf-2`
  - query: considering the year 2018 , what is the cash flow result?
  - gold: `-454.2`
  - prediction: `Based on the selected evidence: be as the amounts depend on , among other factors , future employee stock option exercises . due to the our tax loss position...`
  - source=source_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=None
- `GPN/2017/page_77.pdf-3`
  - query: what are the total amount of net tangible assets obtained through the acquisition?
  - gold: `$ 62154`
  - prediction: `Based on the selected evidence: # FinQA Evidence EW/2017/page_82.pdf-2 - Source dataset: dreamerdeo/finqa - Split: validation ## Pre Text edwards lifescience...`
  - source=source_missing, intent=sum_or_lookup, support=textual_or_insufficient, source_rank=None
- `MRO/2017/page_111.pdf-2`
  - query: what was purchases of reserves in place in 2016?
  - gold: `-13`
  - prediction: `Based on the selected evidence: iness and 10 mmboe associated with divestitures of certain conventional assets in oklahoma and colorado . see item 8 . financ...`
  - source=source_hit_gold_number_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=1

### sum_or_lookup

- `GPN/2017/page_77.pdf-3`
  - query: what are the total amount of net tangible assets obtained through the acquisition?
  - gold: `$ 62154`
  - prediction: `Based on the selected evidence: # FinQA Evidence EW/2017/page_82.pdf-2 - Source dataset: dreamerdeo/finqa - Split: validation ## Pre Text edwards lifescience...`
  - source=source_missing, intent=sum_or_lookup, support=textual_or_insufficient, source_rank=None
- `EW/2016/page_94.pdf-1`
  - query: what is the value , in millions of dollars , of the total issuable stock in 2014?
  - gold: `162.2`
  - prediction: `Based on the selected evidence: ease ) in pre-tax income | $ 2 | $ -9 ( 9 ) | $ -5 ( 5 ) | ## Post Text fair value of debt instruments 2013 the fair value of...`
  - source=source_missing, intent=sum_or_lookup, support=textual_or_insufficient, source_rank=None
- `AMT/2005/page_105.pdf-4`
  - query: what portion of total value of net operating loss carryforwards is related to state?
  - gold: `52.8%`
  - prediction: `39.7%`
  - source=source_hit_gold_number_missing, intent=sum_or_lookup, support=supported_wrong_numeric, source_rank=4

### percent_change

- `RE/2015/page_33.pdf-2`
  - query: what is the percentage change in average of investments from 2014 to 2015?
  - gold: `3.6%`
  - prediction: `5.1%`
  - source=source_missing, intent=percent_change, support=supported_wrong_numeric, source_rank=None
- `IPG/2015/page_48.pdf-1`
  - query: what percent decrease for interest income occurred between 2014 and 2015?
  - gold: `16.79%`
  - prediction: `5.2%`
  - source=source_hit_gold_number_missing, intent=percent_change, support=unsupported_wrong_numeric, source_rank=2
- `JPM/2009/page_133.pdf-2`
  - query: if there were a 100bp rise in rates , how much more would the impact be on earnings in 2009 vs . 2008?\\n
  - gold: `1226`
  - prediction: `Based on the selected evidence: s-at-risk tests measure the potential change in the firm 2019s net interest income , and the corresponding impact to the firm...`
  - source=source_hit_gold_number_missing, intent=percent_change, support=textual_or_insufficient, source_rank=1

### supported_wrong_numeric

- `RE/2015/page_33.pdf-2`
  - query: what is the percentage change in average of investments from 2014 to 2015?
  - gold: `3.6%`
  - prediction: `5.1%`
  - source=source_missing, intent=percent_change, support=supported_wrong_numeric, source_rank=None
- `MRO/2007/page_134.pdf-3`
  - query: what was the average expected life of the options for the three year period?
  - gold: `5.2`
  - prediction: `4.6`
  - source=source_hit_gold_number_present, intent=average, support=supported_wrong_numeric, source_rank=3
- `NKE/2016/page_37.pdf-2`
  - query: what percentage of long-term debt is due after 2021?
  - gold: `89%`
  - prediction: `42.4%`
  - source=source_missing, intent=ratio_percent, support=supported_wrong_numeric, source_rank=None

### source_hit_gold_number_present

- `MRO/2007/page_134.pdf-3`
  - query: what was the average expected life of the options for the three year period?
  - gold: `5.2`
  - prediction: `4.6`
  - source=source_hit_gold_number_present, intent=average, support=supported_wrong_numeric, source_rank=3
- `DISH/2013/page_138.pdf-1`
  - query: what is the tax expense related to discontinued operations in 2013?
  - gold: `7`
  - prediction: `Based on the selected evidence: cate users from the spectrum then licensed to dbsd north america and terrestar . the total consideration to acquire the dbsd...`
  - source=source_hit_gold_number_present, intent=ratio, support=textual_or_insufficient, source_rank=1
- `PNC/2011/page_78.pdf-1`
  - query: for december 31 , 2011 and december 31 , 2010 , what was the average unpaid principal balance outstanding of loans sold as a participant in these programs , in billions?
  - gold: `13.1`
  - prediction: `1849.5`
  - source=source_hit_gold_number_present, intent=average, support=supported_wrong_numeric, source_rank=1

### average

- `MRO/2007/page_134.pdf-3`
  - query: what was the average expected life of the options for the three year period?
  - gold: `5.2`
  - prediction: `4.6`
  - source=source_hit_gold_number_present, intent=average, support=supported_wrong_numeric, source_rank=3
- `AON/2010/page_115.pdf-1`
  - query: what was the average total stock-based compensation expense from 2008 to 2010 in millions
  - gold: `218`
  - prediction: `219`
  - source=source_hit_gold_number_missing, intent=average, support=supported_wrong_numeric, source_rank=1
- `PNC/2011/page_78.pdf-1`
  - query: for december 31 , 2011 and december 31 , 2010 , what was the average unpaid principal balance outstanding of loans sold as a participant in these programs , in billions?
  - gold: `13.1`
  - prediction: `1849.5`
  - source=source_hit_gold_number_present, intent=average, support=supported_wrong_numeric, source_rank=1

### source_hit_gold_number_missing

- `MRO/2017/page_111.pdf-2`
  - query: what was purchases of reserves in place in 2016?
  - gold: `-13`
  - prediction: `Based on the selected evidence: iness and 10 mmboe associated with divestitures of certain conventional assets in oklahoma and colorado . see item 8 . financ...`
  - source=source_hit_gold_number_missing, intent=lookup_or_other, support=textual_or_insufficient, source_rank=1
- `IPG/2015/page_48.pdf-1`
  - query: what percent decrease for interest income occurred between 2014 and 2015?
  - gold: `16.79%`
  - prediction: `5.2%`
  - source=source_hit_gold_number_missing, intent=percent_change, support=unsupported_wrong_numeric, source_rank=2
- `AON/2010/page_115.pdf-1`
  - query: what was the average total stock-based compensation expense from 2008 to 2010 in millions
  - gold: `218`
  - prediction: `219`
  - source=source_hit_gold_number_missing, intent=average, support=supported_wrong_numeric, source_rank=1

### ratio_percent

- `NKE/2016/page_37.pdf-2`
  - query: what percentage of long-term debt is due after 2021?
  - gold: `89%`
  - prediction: `42.4%`
  - source=source_missing, intent=ratio_percent, support=supported_wrong_numeric, source_rank=None
- `GS/2012/page_165.pdf-3`
  - query: for miscellaneous receivables and other assets , what was the percentage that represented assets related to the firm 2019s reinsurance business which were classified as held for sale as of december 2012?
  - gold: `3.464`
  - prediction: `Based on the selected evidence: on about income taxes . 4 . excludes investments accounted for at fair value under the fair value option where the firm would...`
  - source=source_hit_gold_number_missing, intent=ratio_percent, support=textual_or_insufficient, source_rank=1
- `AAL/2015/page_118.pdf-2`
  - query: what were total operating expenses as a percentage of revenue in 2013?
  - gold: `93.8%`
  - prediction: `Based on the selected evidence: , and received wholesale brokerage services from , an entity that is controlled by one of the company 2019s stockholders . th...`
  - source=source_missing, intent=ratio_percent, support=textual_or_insufficient, source_rank=None

### unsupported_wrong_numeric

- `IPG/2015/page_48.pdf-1`
  - query: what percent decrease for interest income occurred between 2014 and 2015?
  - gold: `16.79%`
  - prediction: `5.2%`
  - source=source_hit_gold_number_missing, intent=percent_change, support=unsupported_wrong_numeric, source_rank=2
- `AES/2015/page_117.pdf-4`
  - query: net cash provided by operating activities increased by what percentage in 2014?
  - gold: `19%`
  - prediction: `8.2%`
  - source=source_hit_gold_number_present, intent=percent_change, support=unsupported_wrong_numeric, source_rank=8
- `ETFC/2014/page_26.pdf-4`
  - query: what was the difference in total return percentage beteween e*trade financial corporation and the s&p 500 index for the five years ended 12/14?
  - gold: `-67.33`
  - prediction: `66.9%`
  - source=source_hit_gold_number_missing, intent=ratio_percent, support=unsupported_wrong_numeric, source_rank=5

### ratio

- `DISH/2013/page_138.pdf-1`
  - query: what is the tax expense related to discontinued operations in 2013?
  - gold: `7`
  - prediction: `Based on the selected evidence: cate users from the spectrum then licensed to dbsd north america and terrestar . the total consideration to acquire the dbsd...`
  - source=source_hit_gold_number_present, intent=ratio, support=textual_or_insufficient, source_rank=1
- `DRE/2007/page_59.pdf-1`
  - query: what was the ratio of the debts to the assets in the purchase transaction
  - gold: `17.8%`
  - prediction: `Based on the selected evidence: ject . capital funds agreement pursuant to an agreement with certain creditors , entergy corporation has agreed to supply sys...`
  - source=source_missing, intent=ratio, support=textual_or_insufficient, source_rank=None
- `HII/2017/page_104.pdf-4`
  - query: what is the ratio of the deffered tax assets for the state income tax credit carry-forwards to the net operating loss carry-forward
  - gold: `5.3`
  - prediction: `Based on the selected evidence: mpany has provided a valuation allowance of approximately $ 422.4 million , including approximately $ 249.5 million attributa...`
  - source=source_hit_gold_number_missing, intent=ratio, support=textual_or_insufficient, source_rank=1

### difference

- `ZBH/2017/page_71.pdf-1`
  - query: what was the change in defined contribution plans expenses for the u.s . between 2015 and 2016 in millions?
  - gold: `2.3`
  - prediction: `Based on the selected evidence: # FinQA Evidence ZBH/2017/page_71.pdf-1 - Source dataset: dreamerdeo/finqa - Split: validation ## Pre Text zimmer biomet hold...`
  - source=source_hit_gold_number_missing, intent=difference, support=textual_or_insufficient, source_rank=1
- `MRO/2009/page_139.pdf-4`
  - query: what was the change in receivables for recoverable costs from certain states , under programs to assist companies in clean-up efforts related to underground storage tanks between december 31 , 2009 and 2008 , in millions?
  - gold: `-1`
  - prediction: `Based on the selected evidence: elating to the environment . certain of these matters are discussed below . the ultimate resolution of these contingencies co...`
  - source=source_hit_gold_number_missing, intent=difference, support=textual_or_insufficient, source_rank=1
- `IPG/2015/page_37.pdf-2`
  - query: what is the net change in cash in 2015?
  - gold: `-1.6`
  - prediction: `Based on the selected evidence: ash flow | $ 1241 | $ 891 | $ 1271 | $ 350 | $ -380 ( 380 ) | ## Post Text ( 1 ) service concession asset expenditures exclud...`
  - source=source_missing, intent=difference, support=textual_or_insufficient, source_rank=None
