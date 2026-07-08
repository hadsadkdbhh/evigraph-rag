# Main-Conference Attack Plan

Last updated: 2026-07-05

## Current Position

The project should no longer be framed as a small rule-improvement exercise.
The strongest current story is evidence-state control for numerical RAG:
EviGraph turns retrieved candidates into a selected, executable, and verified evidence graph.

Latest FinQA-300 v21 full-system results:

| setting | EM | supported EM | answer support | main bottleneck |
| --- | ---: | ---: | ---: | --- |
| Oracle-doc Full EviGraph | 0.650 | 0.597 | 0.830 | operand selection |
| Open BM25 Full EviGraph | 0.493 | 0.463 | 0.813 | retrieval plus operand selection |
| Source-rerank Full EviGraph | 0.650 | 0.597 | 0.830 | operand selection |

Strong external baseline:

| setting | GPT-5.4 Direct RAG EM | GPT-5.4 answer support |
| --- | ---: | ---: |
| Oracle-doc | 0.693 | 0.343 |
| Open BM25 | 0.523 | 0.273 |
| Source-rerank | 0.690 | 0.340 |

Interpretation: GPT-5.4 Direct RAG is currently stronger on raw exact match, but much weaker on cited answer support.
The paper should not claim benchmark superiority over frontier readers.
It should claim that evidence-state control gives a better auditable reasoning object: explicit support graph, operation trace, citation check, and failure diagnosis.

## Main Claim

EviGraph-RAG improves numerical RAG by separating three things that ordinary RAG collapses:

1. Evidence selection: which retrieved nodes are safe and useful.
2. Operation execution: which rows, periods, operands, and arithmetic operation produce the answer.
3. Verification: whether the final answer is supported by the cited evidence and calculation trace.

The main-conference angle is not "we added more rules."
The angle is "we expose and control the evidence state, then evaluate both answer correctness and support correctness."

## Non-Negotiable Boundaries

- Do not claim state of the art on full FinQA.
- Do not describe local hashed dense retrieval as a neural dense retriever.
- Do not mix old ablation numbers with v21 main results without labeling them as earlier component-ablation runs.
- Do not add broad generic rules unless a failure cluster and a test justify them.
- Do not hide GPT-5.4 Direct RAG being stronger on raw EM; use it to motivate support diagnostics.

## Attack Tracks

### Track A: Empirical Closure

Goal: make the tables reviewer-proof.

- Rerun v21-compatible ablations: full EviGraph, no planner, no verifier rejection, no verifier, utility-only, retrieve-then-program.
- Add a true retrieval baseline: neural embeddings or a documented external reranker, not hashed dense.
- Add retrieval diagnostics: source hit rate, chunk hit rate, operand hit rate, and source-document recall.
- Keep GPT-5.4, Kimi, and GLM as external reader baselines only if their API outputs are complete and stable.

### Track B: Method Upgrade

Goal: turn remaining repairs into a named mechanism.

- Implement verifier-guided operand repair for numerator, denominator, year/period, and row-label disagreements.
- Add an EvidenceCritic stage that proposes a minimal repair action when verifier support fails.
- Keep the executor deterministic: LLMs may propose plans, but the local executor verifies arithmetic and citations.
- Make process traces first-class outputs, not debugging leftovers.

### Track C: Paper Story

Goal: make the paper read like a method paper, not an engineering diary.

- Main pipeline figure: retrieval candidates to evidence graph to support subgraph to executor to verifier.
- Mechanism figure: verifier-guided operand repair loop.
- Main table: v21 Full EviGraph plus GPT-5.4 Direct RAG and local baselines.
- Ablation table: v21-compatible component removals.
- Failure table: wrong row/op, no numeric, no percent, unsupported, and operand diagnostic split.
- Case studies: one win over Direct RAG, one GPT-5.4 unsupported answer, one open-retrieval failure.

## Immediate Execution Queue

1. Refresh paper claims and generated-table references to v21 numbers.
2. Run v21-compatible ablation manifest.
3. Add retrieval recall diagnostics for open BM25.
4. Implement verifier-guided operand repair for the largest shared failure cluster.
5. Rerun FinQA-300 v22 across oracle-doc, open BM25, and source-rerank.
6. Update paper skeleton with method, experiment, failure-analysis, and limitation sections.

## Success Criteria

Submission-grade internal target:

- Oracle-doc Full EviGraph at or above 0.650, preferably 0.680.
- Source-rerank Full EviGraph at or above 0.650, preferably 0.680.
- Open BM25 Full EviGraph at or above 0.520 without weakening support metrics.
- Answer support remains above 0.800 for Full EviGraph.
- GPT-5.4 Direct RAG remains reported as a strong raw-accuracy baseline.
- The paper includes at least one table proving that EviGraph improves support diagnostics, not just final EM.

## Next Decision

The next engineering action should be v21-compatible ablations or verifier-guided operand repair.
If API budget is limited, prioritize local v21 ablations and open-retrieval diagnostics before more LLM baseline runs.

Run the v21 ablation manifest from the project root:

```powershell
cd "C:\Users\24431\Documents\每日清单"
python .\scripts\run_manifest.py --manifest .\configs\experiments.finqa_300.local_planner_ablation_v21.json
```
