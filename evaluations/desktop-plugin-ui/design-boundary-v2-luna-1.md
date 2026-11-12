# Scoped design boundary v2 validation

Date: October 25, 2026. Skill: `desktop-plugin-ui`.
Case: Nielsen usability review, default/explicit ColorSet selection, contrast,
and styling ownership across authored, native/terminal, and host-owned UI.

**Result: 1/1 strict, eight independent output checks, and manual content
acceptance passed.** The output has a nonblocking record-structure caution,
described below. This is a closed-book advisory case, not a real-host UI test,
user study, accessibility certification, or aggregate release claim. The v1
cohort and its independently classified outcomes remain unchanged and separate.
No run was retried or discarded, and no generated output was repaired by the
reviewer.

## Frozen subject and command

Run ID: `20261025-desktop-ui-design-boundary-v2-luna-1`.
The 19-file source/runtime/full payload SHA-256 is
`d02ed682c82aaa66db71ca29019b3d866145c2a314bb0db3714dcde4d7c8f038`.
The skill copy retained that digest after execution. All repository static
gates, including the full skill validator, passed before launch authorization.

The [unchanged boundary prompt](../pi-prompts/desktop-plugin-ui-design-host-boundary.md)
has SHA-256 `536f3ddb3fdb543e592592d11a41445adeda8054f4645aaaaa53df4367fb4509`.
The continuing documented model exception is `openai-codex/gpt-5.6-luna`,
following the retained Spark account rejection.

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-design-host-boundary.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261025-desktop-ui-design-boundary-v2-luna-1 --expect-output review/design-host-boundary.md --expect-output review/design-host-boundary.json --expect-output-json-field review/design-host-boundary.json::host_acceptance_verified=false --expect-output-json-field review/design-host-boundary.json::task_empirical_tests_performed=false --expect-output-json-field review/design-host-boundary.json::user_testing_performed=false
```

The run finished in **103.594 seconds**, with Pi exit 0, no timeout, valid
event JSON, zero tool errors, both exact output paths, all three false task
booleans, and unchanged payload integrity.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `review/design-host-boundary.md` | 16,910 | `f505b5eff6530998a5fc634ad0e2abfdcf45014f0ee0473a6a95558b61659fe2` |
| `review/design-host-boundary.json` | 19,786 | `9a42f95ee1eb783a2f83ca8df4bde82a3fe6c136e247cf121c10ece9cd928107` |

## Independent and manual acceptance

The reviewer read both complete reports. Eight independent output checks
passed: requested fields, false task booleans, unique heuristic numbers 1–10,
complete heuristic records, complete surface records, both palette selections
and exact role tokens, contrast claims, and safe repair pairs. The result is
retained as `design-output-review-independent.json` in the raw run directory.
The prompt does not mandate palette enum capitalization, numeric rather than
descriptive threshold fields, or a fixed surface-row count; those were not
invented as acceptance requirements.

Manual review confirms:

- All ten heuristic entries correctly map to Nielsen's principles, using the
  bundled short labels. Each has a concrete rule, affected surfaces, recovery,
  and verification; evidence remains `untested`. No representative-user result,
  measured efficiency, current paint acceptance, or conformance is claimed.
- Release A uses ColorSet1 by default. Release B uses ColorSet2 because of the
  explicit selection. All authored role tokens belong to the appropriate
  bundled set. Status words and icons/shapes/patterns supplement color.
- The authored MCP App iframe and VS Code webview retain exact-token styling
  within their permitted content. Host frame/chrome, native/terminal controls,
  elicitation, settings, permission dialogs, and toolbars retain host control.
  No CSS, DOM, arbitrary font, terminal truecolor, or top-application styling
  API is invented.
- Dark mode, high contrast, forced colors, visible focus, cancellation, useful
  text/structured fallback, safe retry, drafts, and authoritative state survive
  the proposed adaptations. Terminal effective colors and host rendering are
  explicitly pending checks.
- Both unsafe proposed contrast pairs are correctly calculated and rejected.
  The repairs use exact, safe palette tokens rather than a new hex color.

**Nonblocking record-structure caution:** the MCP App JSON row records exact
authored iframe paint and host-owned surrounding frame/chrome within one
record. A separate permission-dialogs/toolbars record also marks host chrome
as host-owned. This is explicit, correct ownership, with no claim that the
whole authored iframe is host-mapped. It departs from the reference's
separate-record instruction by omitting a dedicated authored-iframe versus
surrounding-MCP-frame/chrome row split. Acceptance uses the original semantic
criterion—correct explicit ownership and no whole-iframe misclassification.
The prompt does not require a dedicated row by that name. The parent reviewer
independently confirmed this distinction; no new post-run row-name gate was
added, and the output was preserved as generated.

## Contrast evidence

The agent ran local Python sRGB relative-luminance arithmetic before writing
the reports. Its ten-decimal values agree with independent calculations; the
following unrounded values were used for threshold comparisons:

| Foreground / background | Ratio | Required | Classification |
| --- | ---: | ---: | --- |
| `#cfcfcf` / `#ffffff` | 1.5579550563651179 | 3:1 focus indicator | Unsafe proposal |
| `#e8002a` / `#ffccd5` | 3.326162240606473 | 4.5:1 ordinary text | Unsafe proposal |
| `#333e48` / `#ffffff` | 10.918238644424665 | 3:1 focus indicator | Safe repair |
| `#9e1b32` / `#ffffff` | 7.9046884551695875 | 3:1 focus indicator | Safe alternative |
| `#333e48` / `#ffccd5` | 7.720736540005823 | 4.5:1 ordinary text | Safe repair |
| `#9e1b32` / `#ffccd5` | 5.589730997898148 | 4.5:1 ordinary text | Safe alternative |

These are opaque authored-token calculations, not sampled host pixels or
measurements after theme remapping, alpha compositing, or user accessibility
settings. Actual states, adjacent surfaces, focus, and rendering remain
unverified. The two intentional unsafe proposals are detected design issues,
not failed product-host executions.

## Source checks, traces, and limits

The agent checked both reports, made two successful edits to its own outputs,
then checked both final reports again. The reviewer independently ran the
copied bundled checker with the clean-CI flag:

```powershell
uv run --script skills/desktop-plugin-ui/scripts/check_reports.py review/design-host-boundary.md review/design-host-boundary.json --fail-on-findings
```

The independent result is `passed:true`: **32 official URL checks**, zero
historical rows, zero findings and zero replacements. Exact citations are
checked against the copied catalog; this closed-book run did not freshly fetch
the linked pages. The source checker cannot establish semantic support or
usability by itself, so both complete reports were also reviewed manually.

The required event inspection passed:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-design-boundary-v2-luna-1/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

All **13 model records** identify `openai-codex` / `gpt-5.6-luna`. Reads stayed
within the prompt, `SKILL.md`, nine relevant references (surface matrix, host
prompts, usability/color, evidence/probing, chat patterns, distribution, Claude
limits, Copilot limits, native patterns), and both bundled palettes. Shell calls
were the bundled source catalog, local contrast arithmetic, and two bundled
report checks. No external app, account, provider tool, repository documents,
sibling skill, project evidence, or acceptance gallery was accessed. Successful
output edits are not run retries, and no skill file was changed.

Pi-reported model usage was 43,716 input tokens, 14,787 output tokens, 284,544
cache-read tokens, **343,047 total tokens**. This is evaluation-model usage;
the task consumed no Claude/Copilot inference.

Raw manifests, events/stderr, outputs, strict checks,
`model-trace-summary.json`, `report-check-independent.json`, and
`design-output-review-independent.json` remain under
`evaluations/runs/20261025-desktop-ui-design-boundary-v2-luna-1/`.
No execution, artifact, isolation, or blocking manual failure was observed.
Real-host rendering, representative-user testing, full accessibility
conformance, broader behavior generalization, and earlier cohort failures
remain outside this scoped pass.
