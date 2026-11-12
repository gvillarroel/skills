# Offerings contract: first frozen Luna run

Date: 2026-10-25. Skill: `desktop-plugin-ui`. This is the single first attempt
`20261025-desktop-ui-offerings-contract-v1-luna-1`, evaluated against the
pre-output [frozen criteria](offerings-review-criteria.md). No retry, evaluator
output repair or canonical edit was performed. Preserve the outputs and all
agent-side repair failures.

## Frozen identity and outcome

- Source/runtime/full: **21 files**, SHA-256
  `26b12b4879ba0e4663b7d225bba066424f1baa1dee7d1461ba1c84a4de1060a5`.
- Prompt file SHA-256:
  `373c69bb335973bc3c2972a21234555793b01e17193df28dbbca723ecd5e74ea`.
  The harness's newline-normalized prompt hash is
  `cdba428c882ae6f031fdf454c2efad27be38fa3ee8f491cc29ae0b96d6c9df01`;
  its source file was unchanged at launch.
- Frozen criteria SHA-256:
  `4e6d0d0a0f85c04cc7a73c4a89a8ae8d81f8a4caf8c87b6f9658832173b4d590`.
- Model: **openai-codex/gpt-5.6-luna**, high thinking, Pi 1.4.0, strict JSON,
  runtime profile, 600-second timeout. This uses the recorded deliberate model
  exception after Spark account rejection.

| Gate | Result | Basis |
| --- | --- | --- |
| Strict harness | **Fail, 0/1** | Pi exited 0, but three `edit` tool errors violate strict event policy. Duration 113.777 seconds. |
| Exact outputs/false flags/payload | Pass | Both nonempty artifacts exist; both current-task flags are false; all 21 copied resources are unchanged. |
| Final bundled report checker | Pass after agent repair | Both artifacts checked; 30 URL checks, ten historical rows, zero final findings. Initial check had ten evidence-field findings. |
| Independent sources/paths/numbers | Pass | Fifteen exact URLs in each format, fifteen token/value bindings, seven original/repair contrast pairs independently verified. |
| Manual semantic acceptance | **Fail, 0/1** | One historical canvas observation uses the wrong host/version/layer for the actual CLI measurement. |
| Conservative joint acceptance | **Fail, 0/1** | Strict and semantic failures remain despite correct final numeric/source data. |

This is scoped contract evidence only. It does not clear prior cohorts,
naturalistic/boundary thresholds, installed-host gates or overall skill status.

## What worked

The artifacts provide seven useful positive offerings: npm Codex CLI, Codex
desktop, Codex IDE, Copilot CLI, Copilot Chat MCP Apps, ordinary VS Code
webviews and a named VS Code canvas route. Each gives features, evidence and
version scope, persistence limits, fallback and next checks. They distinguish
backend bytes/callbacks from pixels, inline MCP Apps from extension webviews,
and canvas negotiation from actual canvas use. They preserve the desktop paint
capture's unrecorded-image-build caveat and do not repeat the withdrawn
executing-process/missing-extended-form assertion. No additional PID narrative
or fixed historical-row count was required by the prompt.

Copy is English and concrete, including Save/Cancel, Explain, export scope,
invalid/error and readable text/tool routes. `T-104`, `high` and
`E_INVALID_PRIORITY` remain exact. ColorSet 1 is selected by default, authored
paint stays separate from host chrome/native controls/accessibility overrides,
and all ten H1-H10 IDs and canonical short labels are correct. The heuristic
checks remain untested for this deliverable rather than becoming user research.
Save uses an expected record version; cancellation discards the draft, while
restart/reopen durability remains bounded and untested.

The agent actually ran the value helper twice: the supplied catalog/three-pair
command and four repair-pair calculations. It used the exact catalog to bind
source paths; no separate `--resolve` command occurred. The prompt did not
mandate that flag verbatim, and direct catalog-backed resolution is accepted
because every claimed path/value was independently verified. Do not invent an
extra command-contract failure.

Independent checking used the copied YAML as the source of exact value paths
and a separate **55-digit Decimal sRGB calculation** for the ratios. All
fifteen JSON bindings, including repair paths, resolve correctly. All seven
ratios and applicable threshold decisions pass the frozen 1e-9 tolerance.
The three original ratios are 1.5579550563651179, 2.7454458936977137 and
3.326162240606473. Repair ratios are 7.9046884551695875,
5.489814557409947, 7.720736540005823 and 5.589730997898148. Each repair
passes its intended threshold; valid computation is not mistaken for approval
of the original pair.

## Retained failures

The initial report checker found all ten historical `evidence` fields
unsuitable for its string-field contract. The agent inspected the JSON and
repaired it, but three edit requests failed with exact-match errors:

- event line 10489: `Could not find edits[2] ... oldText must match exactly`;
- event lines 10647 and 10779: `Could not find edits[1] ... oldText must match exactly`.

There were 21 tool calls in total: nine reads, five shell calls, two writes
and five edits. Three edits errored; two succeeded. The successful final
checker result cannot erase those strict failures. Classify these as **agent
workflow failures**, not a provider, harness or palette-calculation failure.

Final historical row index 9 is a separate **agent evidence-scope failure**:

```json
{
  "host": "VS Code Copilot canvas",
  "surface": "native canvas visual rendering",
  "version": "1.143.1; Agent Host build not recorded",
  "layer": "canvas frontend",
  "result": "canvases:true was observed in CLI negotiation, but no canvas was opened; paint is unverified.",
  "evidence": "observed-working; untested; conditional"
}
```

The frozen evidence attributes the executed `canvases:true` measurement to
**Copilot CLI 1.0.103 protocol negotiation**, not a VS Code 1.143.1 canvas
frontend. The result appropriately says paint is unverified, so this is not
a claim that a canvas actually painted. Nevertheless, its host/surface/version/
layer metadata misattributes the successful measurement. A downstream reader
grouping structured observations by those fields would receive the wrong
evidence layer. Split the CLI measurement from the untested canvas offering;
do not add an observed label to an untested UI row merely to satisfy a checker.
This violates the frozen mechanism/evidence identity criteria even though the
checker finds the expected labels.

All ten final historical rows contain the six requested fields and a literal
canonical observed label. That mechanical field pass is reported separately
from factual attribution. The adjacent Copilot Chat row mixes observed access
gates with untested paint but explicitly states no chat exercise; the clear
canvas metadata mismatch is the semantic failure counted here.

## Trace, commands and retained identities

Observed model and provider match. Event JSON is valid; the read surface is
limited to prompt, SKILL, relevant Codex/Copilot/matrix/offerings/evidence/design
references and the generated JSON. Prompt-first and bundle integrity pass.
Helper-internal palette reads stay inside the copied bundle. No network,
additional provider call, installation, host/account/global action, renderer
build or empirical UI test occurs. The trace summary correctly fails on the
three tool errors; it is not presented as a clean trace.

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-offerings-contract.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261025-desktop-ui-offerings-contract-v1-luna-1 --expect-output offerings/contract.md --expect-output offerings/contract.json --expect-output-json-field offerings/contract.json::host_acceptance_verified=false --expect-output-json-field offerings/contract.json::task_empirical_tests_performed=false
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-offerings-contract-v1-luna-1/events.jsonl --output evaluations/runs/20261025-desktop-ui-offerings-contract-v1-luna-1/trace-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!desktop-plugin-ui([\\/]|$))'
```

The raw run retains manifests, events, checker diagnostics/repairs, final
artifacts and `independent-values-sources.json`. The latter has SHA-256
`ecc4657143594af6be6e107f36b6a346c6e0e0bf2cc7abaf8a6957bc17cdd4b1`.
No grader information was fed back into the run.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `offerings/contract.md` | 13,783 | `887584854b7746d7be696c11f0907180aeed265454d79033cb1537e68ab98a3e` |
| `offerings/contract.json` | 19,467 | `f39ddd46fd316b51f1548f71d387b99b7387af4ef43a7e44e1cf1b8edcc5ea1a` |

## Small follow-up candidates and final helper regression

Two compact guidance changes are suggested, without modifying this frozen
subject: build structured evidence rows before prose, using one actual probe's
host/surface/version/layer/result tuple; keep untested offerings outside that
empirical row. For JSON repair, load/modify/serialize the complete structure
or use a uniquely anchored record rather than ambiguous repeated text edits.
Provide a short string-valued `evidence` example with its scope. Do not invent
observation labels or automatically repair facts.

The separate final deterministic value-helper regression passes **16/16**:

```powershell
uv run --script projects/desktop-plugin-ui/scripts/test-design-values.py --output projects/desktop-plugin-ui/artifacts/design-values-tests-20261025/offerings-final.json
```

The helper remains SHA-256
`edc8b152cb8a274722532e03caef1f09e19df7e2af1741a00df92866ca29fb1f`.
Its success confirms palette/path/numeric machinery; it does not turn this
failed skill-use case into a pass. Repository-wide final checks belong to the
parent workflow. No new host acceptance or representative-user result is claimed.
