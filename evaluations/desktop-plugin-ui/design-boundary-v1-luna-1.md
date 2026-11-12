# Scoped design boundary validation

Date: October 25, 2026. Skill: `desktop-plugin-ui`.
Case: ColorSet selection, Nielsen usability review, and styling ownership
across authored views, terminal/native controls, and host-owned forms/chrome.

**Result: 1/1 strict, independent artifact checks, and manual content review
passed.** This is one closed-book advisory test of the new design contract,
not a new real UI test, user study, accessibility certification, or broad
release pass. Earlier cross-assistant cohorts and their failures remain
separate and unchanged. No attempt was repeated or discarded.

## Frozen subject and command

Run ID: `20261025-desktop-ui-design-boundary-v1-luna-1`.
The final 19-file source/runtime/full payload SHA-256 is
`bcc6c0051fa2ceaf157a86a58444436d7fad694bec56b586f415aebc53121a86`.
The copied skill retained that exact digest after the run. An earlier
pre-run candidate was replaced before launch; no evaluation used that candidate.

The unchanged [boundary prompt](../pi-prompts/desktop-plugin-ui-design-host-boundary.md)
has SHA-256 `536f3ddb3fdb543e592592d11a41445adeda8054f4645aaaaa53df4367fb4509`.
The documented evaluation-model exception is
`openai-codex/gpt-5.6-luna`, following the retained Spark account rejection.
Static repository gates passed before authorization to launch.

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-design-host-boundary.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261025-desktop-ui-design-boundary-v1-luna-1 --expect-output review/design-host-boundary.md --expect-output review/design-host-boundary.json --expect-output-json-field review/design-host-boundary.json::host_acceptance_verified=false --expect-output-json-field review/design-host-boundary.json::task_empirical_tests_performed=false --expect-output-json-field review/design-host-boundary.json::user_testing_performed=false
```

The run completed in **91.628 seconds**, with Pi exit 0, no timeout, valid
events, zero tool errors, both exact output paths, all three false booleans,
and unchanged skill integrity. Final artifact SHA-256 values:

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `review/design-host-boundary.md` | 18,697 | `78dd5dd14e13bfbc00ae02996efdf2e180b56b67ab911026cf538e0a5c672c59` |
| `review/design-host-boundary.json` | 19,935 | `c6d2b01dcc1c134ef4de67b4f8f2cd3f1c8d2258327529ef23d1ac92e315c180` |

## Independent and manual review

Both complete artifacts were read and reviewed. Eight independent output
checks passed: required JSON fields, false task booleans, unique heuristics
1–10, complete heuristic fields, seven complete surface decisions, both palette
selections and exact role tokens, numeric contrast claims, and safe repair pairs.
The machine result is retained as `design-output-review-independent.json`
inside the raw run directory.

Manual review found no blocking factual or design-boundary defect:

- The ten named Nielsen heuristics are correctly ordered and each includes
  a concrete workflow rule, relevant surface scope, recovery, verification,
  and `untested` evidence. The plan makes no claim of representative-user
  testing, measured efficiency, current rendered usability, or conformance.
- Release A selects `colorset1` because no palette was requested. Release B
  selects `colorset2` because the user explicitly selected it. The first map
  imports no CS2-only hues; the second uses exact extended tokens. Both retain
  labels/icons/shapes rather than color-only status distinctions.
- Both owned views—the MCP App and ordinary VS Code extension webview—receive
  scoped authored styling. Native Claude terminal controls and negotiated
  Copilot forms use supported host controls/theme behavior. Host elicitation,
  MCPB settings, permission dialogs, and toolbars remain host-owned. No CSS,
  DOM, font, icon, truecolor, or host-chrome insertion capability is invented.
- Dark mode, high contrast, forced colors, host styling requirements, visible
  focus, cancellation, and text/structured fallback remain protected. Actual
  terminal colors, installed-host behavior, and computed painted contrast
  are explicitly left for later verification.
- The plan preserves drafts and last useful authoritative data, distinguishes
  cancel/decline from acceptance, validates on both sides, and bounds retry
  by safety/idempotence rather than claiming every operation can be retried.

The agent executed Python relative-luminance calculations before writing the
reports. Its displayed ten-decimal ratios agree with independent calculations.
The independent unrounded values and thresholds are:

| Pair | Ratio | Required | Result |
| --- | ---: | ---: | --- |
| `#cfcfcf` focus / `#ffffff` | 1.5579550563651179 | 3:1 | Expected unsafe proposal |
| `#e8002a` ordinary text / `#ffccd5` | 3.326162240606473 | 4.5:1 | Expected unsafe proposal |
| `#333e48` repaired focus / `#ffffff` | 10.918238644424665 | 3:1 | Safe opaque pair |
| `#9e1b32` alternative focus / `#ffffff` | 7.9046884551695875 | 3:1 | Safe opaque pair |
| `#333e48` repaired text / `#ffccd5` | 7.720736540005823 | 4.5:1 | Safe opaque pair |
| `#9e1b32` alternative text / `#ffccd5` | 5.589730997898148 | 4.5:1 | Safe opaque pair |

These are computed opaque sRGB pairs, not measurements of host pixels,
composited states, user preferences, or terminal color remapping. The reports
correctly require subsequent state/theme/compositing checks.

## Sources, trace surface, and failure classification

The agent checked **both completed reports** with the copied bundle's
`check_reports.py`; its result was `passed:true` before finishing. The reviewer
independently reran:

```powershell
uv run --script skills/desktop-plugin-ui/scripts/check_reports.py review/design-host-boundary.md review/design-host-boundary.json --fail-on-findings
```

The independent result passed **36 official URL checks**, with zero historical
rows, zero findings and zero replacements. This validates exact catalog
citations and required empirical-field placement when applicable; it does not
freshly browse those citations or grade their semantic support. No source
repair was needed. Findings from the two deliberately unsafe proposed color
pairs are design issues detected by the review, not execution failures or
failed product-host tests.

The mandatory trace inspection also passed:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-design-boundary-v1-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

All nine model records identify `openai-codex` / `gpt-5.6-luna`. Reads were
limited to the task prompt, `SKILL.md`, eight relevant bundled references
(surface matrix, usability/color, native patterns, host prompts, Claude limits,
distribution, Copilot limits, chat patterns), and both bundled palette files.
The only shell calls were local contrast arithmetic and the report checker.
The agent wrote the two requested reports without edits, external provider
calls, app opening, account changes, repository-document reads, sibling-skill
reads, or acceptance-gallery reads.

Pi-reported model usage: 35,182 input tokens, 12,197 output tokens, 132,736
cache-read tokens, **180,115 total tokens**. This is evaluation-model usage;
the advisory task consumed no Claude/Copilot model inference.

Raw manifests, events/stderr, strict gates, outputs,
`model-trace-summary.json`, `report-check-independent.json`, and
`design-output-review-independent.json` are preserved under
`evaluations/runs/20261025-desktop-ui-design-boundary-v1-luna-1/`.
No execution, artifact, isolation, or manual semantic failure was observed in
this scoped case. Actual real-host rendering, user testing, accessibility
conformance, broader behavior generalization, and previous failing cohorts
remain outside its acceptance claim.
