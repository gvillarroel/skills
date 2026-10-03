# Information, editorial selection and critique stages

Date: 2026-09-12. Skill: `usefulcharts-style`. Status: **validating**.

## Change and scope

The user asked whether the skill includes three distinct capabilities: establish that the information is sufficient, decide what to display and how, and critique and refine the rendered work. Inspection found extensive composition and visual-review instructions, but no comparably explicit opening decision about the reading question, evidence sufficiency and authorized selection from a research pool.

The entry point now makes all three stages explicit. The new compact `references/information-design.md` distinguishes missing evidence that invalidates a requested claim from an unknown that can be represented honestly. It separates a complete display brief from a selectable research pool, requires reasons for chosen context, retains mandatory intermediates and merger inputs, and connects selection to layout semantics. The existing evaluation reference now separates content, technical execution and visual acceptance; a fixed iteration count, average score or unresolved limitation is not a pass. Planning requests receive a direct route and must describe the future render/inspect/compare/repair/rerender sequence.

This change does not prove that a model will follow every instruction, execute an actual critique loop, or produce a poster indistinguishable from UsefulCharts. The planning study below deliberately tests decisions before drawing. The two renderer command controls use the classic ten-record starter solely to check the command interface; that image is not the aesthetic acceptance target.

## Frozen development protocol

- Naturalistic prompt: [three museum commissions](../pi-prompts/usefulcharts-editorial-decisions.md).
- Evaluator-owned acceptance: [editorial decisions contract](../contracts/usefulcharts-editorial-decisions.md), not visible in the isolated workspace. Revision 2 corrects the original contract's count typo from two to three source successions; [revision 1](../contracts/usefulcharts-editorial-decisions-v1.md) is retained. The original fidelity requirement already preserves all supplied typed relationships. The prompt is unchanged and no acceptance criterion is relaxed.
- Prompt SHA-256: `52de7952bc1a004054f0df034ccaad3197351377719753c5ff11b2aebada0841`.
- Required planning output: exactly `result/editorial-plan.md`.
- Three fresh runs per cohort, strict JSON mode, high thinking, runtime profile and read-only copied skill. Require at least two complete passes; retain failures.
- Default provider/model: `openai-codex/gpt-5.3-codex-spark`. A supplemental `openai-codex/gpt-5.6-luna` cohort on the unchanged revised payload was preregistered in `SKILLS.md` in response to the user's earlier Luna question. This exception does not replace Spark failures.
- No historical web research is needed or performed: all three source packets are explicitly fictional. No baseline or sealed holdout is claimed.

The inputs contrast a complete genealogy with an unknown birth and an undocumented other parent, an unsupported numeric succession request, and a broader civic research pool from which the author may select. The contract checks retained core records and typed links, meaningful exclusions, source-defined merger category, honest uncertainty, appropriate time semantics and a concrete future visual-review loop. Delivered plans are read directly by the evaluator rather than accepted from model self-reports or phrase matching.

| Cohort | Payload files | Payload SHA-256 | Strict execution | Complete planning contract |
| --- | ---: | --- | ---: | ---: |
| Spark A | 112 | `a09214877d3fd6d0ebff671d680f557c9a717f27a2e066dc7e851897b9c56e7d` | 3/3 | 0/3 |
| Spark B | 112 | `1dc2b181a0671e69672885812100c06fff9d5d035593261e8b85c751284ef619` | 2/3 | 0/3 |
| Luna, revised B payload | 112 | `1dc2b181a0671e69672885812100c06fff9d5d035593261e8b85c751284ef619` | 3/3 | 1/3 |

## Observations and retained failures

All six Spark plans correctly distinguish the broadly sufficient genealogy from the unsupported observatory chronology. All six omit the planned visual comparison and rerender/inspection loop, so **none passes the complete contract**. A clean harness execution is not counted as an editorial pass. Several plans also retain peripheral context without explaining its value to the merger question; A3 and B2 omit an explicit c2-to-c3 branch in their diagram descriptions. These are additional weaknesses, not reasons to alter the original acceptance criteria.

Cohort A reads only the entry point from the skill. The revision therefore adds a direct planning-only route to the compact reference and states the future critique sequence explicitly. Cohort B still omits that sequence in its final plans. B1 additionally attempts to read the nonexistent `references/institutional-composition.md`, producing a retained tool error; the real linked file is `institution-composition.md`. Classify this as an agent path error and the incomplete plans as failures to apply the requested skill behavior. The instruction change has not established reliable Spark planning.

All three Luna plans explicitly cover sufficiency, justified selection, source-defined color, and a future full-page/detail comparison with repair, rerender and inspection. They exclude the furniture inventory for its lack of explanatory value, retain the original pool, and preserve the core branching story. All three read the new information reference and the existing evaluation reference. Strict execution, exact outputs, independent trace checks and unchanged payload checks pass 3/3.

Direct review still finds two unresolved production ambiguities, so complete acceptance is **1/3**, below the preregistered 2/3 threshold:

- Luna 1 describes all core institutions and links, but its styling instruction refers to “two successor claims” although the source has three. Reconcile the relation inventory and its encoding before drawing. This also exposed the count typo in the original evaluator contract; both the agent output and original contract are preserved.
- Luna 2 meets the planning contract: source-backed sufficiency decisions, all three successions, the c2-to-c3 branch, both merger inputs, justified context/exclusions, and a concrete visual review loop.
- Luna 3 preserves the factual Cora-to-Evan parentage in its text, but suggests a “single-parent/uncertain-parent connector” for that known connection. The unknown concerns the other parent's identity; the known parentage must remain definite. Resolve that ambiguous rendering instruction before production.

These retained weaknesses do not erase the observed three-stage coverage, and that coverage does not convert the two unresolved plans into complete passes. No additional cohort was run to select a more favorable result. The study supports explicit inclusion of the three stages and shows why a final semantic review remains necessary; it does not establish broad execution reliability, rendered-poster quality, or model superiority.

## Reproduction and evidence paths

Run IDs are `usefulcharts-v34-editorial-spark-{1,2,3}-20260912`, `usefulcharts-v34b-editorial-spark-{1,2,3}-20260912`, and `usefulcharts-v34b-editorial-luna-{1,2,3}-20260912`. Each ignored run folder retains its original prompt, copied skill, model trace, delivered plan, strict gates and payload-integrity results.

For each planning run, substitute the registered run ID and its declared model:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-editorial-decisions.md --expect-output result/editorial-plan.md --model openai-codex/gpt-5.3-codex-spark --thinking high --mode json --strict --run-id <run-id> --timeout-seconds 900
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/independent-trace.json --require-model gpt-5.3-codex-spark --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md
```

For Luna, replace the two model values with `openai-codex/gpt-5.6-luna` and `gpt-5.6-luna` respectively. Read the exact final `workspace/result/editorial-plan.md` against the independent contract after each run. A completed trace check for B1 must remain failed because of the recorded tool error.

The command controls are `usefulcharts-v34-editorial-contract-spark-20260912` and `usefulcharts-v34b-editorial-contract-spark-20260912`:

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-contract.md --require-exact-command-from-prompt --expect-output deliverables/chart.svg --expect-output deliverables/chart.html --expect-output deliverables/layout.json --model openai-codex/gpt-5.3-codex-spark --thinking high --mode json --strict --run-id <control-run-id> --timeout-seconds 900
```

Both controls pass strict execution and independent browser replay against the corresponding copied `assets/templates/starter.json`: 10 nodes, 10 edges, 37 text elements, minimum contrast 6.0273 and zero geometry findings or composition warnings. The evaluator opened the shared preview after verifying identical PNG SHA-256 `10f16a482d0bbb6111e742993a5b3e93de765b900ce9fbd61a3c2a80c2c46ef2`. Its sparse persistent columns are plainly not proof of UsefulCharts composition quality.

The independent replay command for each control is:

```powershell
uv run --script evaluations/runs/<control-run-id>/workspace/skills/usefulcharts-style/scripts/audit_chart.py evaluations/runs/<control-run-id>/workspace/deliverables/chart.svg --source evaluations/runs/<control-run-id>/workspace/skills/usefulcharts-style/assets/templates/starter.json --report evaluations/runs/<control-run-id>/independent-browser.json --png evaluations/runs/<control-run-id>/independent-preview.png
```

## Local verification and remaining work

Passed the relevant existing suites: `test_timeline_geometry.py` (11), `test_timeline_events.py` (25), `test_editorial.py` (51), and `test_chart.py` (27): 114 tests total. The Pi harness passes 14 tests. Pattern IDs (1,222), repository structure, skill independence, payload and quick skill validation pass. Local synchronization refreshes eight changed files and `--check` confirms all 129 canonical source files. No new published example or pattern is introduced by this editorial revision.

The runtime snapshots also contain four earlier uncommitted chronology script changes for horizontal interval labels and illustrated-note priority. They remain work in progress: the separate complete chronology prototype still fails note placement, and the planning runs cannot validate those new visual features. All failed prototypes remain under `projects/usefulcharts-style/artifacts/reviews/varied-chronology-v34/`; no prototype is promoted as an improved final poster. Preserve this distinction when continuing the original visual-quality objective.
