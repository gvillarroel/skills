# Colorset 1 default revision — 2026-10-24

## Change and frozen subject

Every new XY chart defaults to `colorset1`, including after a prior explicitly
selected `colorset2` chart. Colorset 2 remains available only for an explicit
user request or selection. Multiple categories no longer justify selecting it
automatically. The canonical entry point, colorset reference and UI prompt now
agree with this policy. Template/helper rendering logic is unchanged.

The updated canonical skill has 18 runtime files, SHA-256
`f361de1b148be659671ad1eb3100a34fcdfa9b7b5061109981bfd8ff587b5ae6`.
Source/full has 31 files, SHA-256
`06edeffd8d99e8c514361e4ecaa563ff25c9a075ca1490a31569c10cbc68d561`.
Static source/runtime/full audits pass with exact copied inventories; evidence
is `projects/reflex-xy-plugins/artifacts/default-colorset1-audit/report.json`.

Claude Code fresh commands, inline JSON, project JSON files and model tool
calls now inject Colorset 1 independently of the pane's previous selection.
Edits to the current chart still honor the explicitly selected palette.
The MCP input parser normalizes an omitted palette independently for each call.
Server instructions, tool descriptions and the capability catalog expose the
same rule. Authored widget fallback colors are all canonical Colorset 1:
red active/focus/error states and neutral backgrounds, text and borders.
Host-provided theme variables remain supported.

## Updated distributions

Release **0.1.1** is under
`projects/reflex-xy-plugins/artifacts/releases/0.1.1/`; 0.1.0 is preserved.

| Archive | SHA-256 |
| --- | --- |
| `reflex-xy-claude-code.zip` | `52a4a488c8ea06c08cac1d7489f47b34fa3a8c6579e5f70f515ceed3cb66c34b` |
| `reflex-xy-chatgpt.zip` | `1f8dc3ce649053a38be41ad7aca5f7b4573eec543bda4c10c9a5889a336689cc` |
| `reflex-xy-claude-desktop.mcpb` | `03f1e7d76f5b1ca260cd72fed063d1489211f5487f5ebfd8ca7784d87974a074` |

The builder copies the updated canonical skill, adapter versions, standalone
MCP server/widget, notices and installation instructions. No signed-in account
connection or native application configuration outside the repository changed.

## Functional validation

- Claude Code 2.1.302 strict source validation and **7/7 native tests** pass.
  The added test covers omitted palettes after explicit Colorset 2 in commands,
  JSON, files and model tool calls, plus explicit pane selection. **157**
  portable assertions pass. Mod entry SHA-256 is
  `0d5358aa1b9186a176d5378f88b16c351665b0d1c13b35cc603c0ee4e3bd5dd9`.
- Official MCPB 2.1.2 schema validation passes for the 0.1.1 Desktop manifest.
- Node type checking, **4/4 boundary suites**, build and actual bundled stdio
  regression pass. The same process renders explicit Colorset 2 then a new
  omitted-palette request as Colorset 1, including downloaded normalized JSON.
- Real HTTP/Python/MCP Apps browser acceptance passes both palettes at desktop
  and mobile, defaults after an explicit Colorset 2 chart, downloads and error
  recovery. Authored CSS hex values match the canonical Colorset 1 contract;
  computed initial active background is `rgb(158,27,50)`, active text is white,
  canvas is `rgb(247,247,247)` and borders are canonical gray. Evidence is
  `artifacts/chatgpt-browser-v0.1.1-cs1-chrome/report.json` inside the project.
  This is the real component in a protocol host fixture, not a signed-in Claude
  or ChatGPT account screenshot.

Independent extracted-archive default checks are recorded under
`projects/reflex-xy-plugins/artifacts/independent/0.1.1/`: **4/4 CLI** and
**4/4 same-process SDK stdio** requests pass the sequence
`[colorset2, colorset1, colorset2, colorset1]` with explicit then omitted palettes
for presets and generic supplied-data charts. Native mark paint, saved
measurements, PNG/offline HTML and editable source pass. The Desktop capability
catalog advertises the default and its bundled skill carries the updated rule.
All three archive audits, official MCPB schema validation, extracted Code strict
validation and **7/7 native tests** pass. `source-identity.json` confirms all
18 runtime files match canonical source byte-for-byte and each adapter,
renderer and Node/widget bundle is current.
The prior [90-case release matrix](plugins-20261024.md) remains historical
evidence; it is not relabeled or pooled as a new 0.1.1 result.

## Isolated skill forward test

Ran one fresh scoped contract on the frozen runtime with the existing recorded
model exception, **`openai-codex/gpt-5.6-sol`**, following the earlier Spark
provider rejection. Prompt: [default palette with six categories](../pi-prompts/reflex-xy-default-colorset1.md).

```powershell
uv run --script scripts/run-pi-skill-eval.py reflex-xy --prompt-file evaluations/pi-prompts/reflex-xy-default-colorset1.md --model openai-codex/gpt-5.6-sol --mode json --strict --run-id 20261024-reflex-xy-default-colorset1-contract --expect-output chart.py --expect-output chart.html --expect-output chart.svg --expect-output chart.png --expect-output result.json --expect-output-json-field result.json::colorset=colorset1
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-reflex-xy-default-colorset1-contract/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error
```

Result: **0/1 strict/joint; 1/1 palette/artifact/manual**. Pi exits zero and
creates all five exact outputs with Colorset 1 and the original six values.
Independent SVG inspection finds no noncanonical paints; PNG, offline HTML,
source and JSON pass, and the chart was visually inspected. The skill payload
is unchanged before/after, with the runtime hash above. Read surface is focused
on the entry point and relevant in-bundle references/template/helper.

Strict mode correctly fails for five agent tool errors during native argument
and verification corrections, plus one forbidden absolute temporary-image read.
The attempt, JSON events and failures are retained without reroll at
`evaluations/runs/20261024-reflex-xy-default-colorset1-contract/`. The independent
artifact review is
`projects/reflex-xy-plugins/artifacts/default-colorset1-pi-artifact-review.json`.
The default selection succeeds; this is not a clean authoring certification.
Keep the broader skill status **validating** and preserve earlier cohorts.

## Repository checks and boundaries

Pattern-ID, skill, independence and payload validators pass. The normal local
sync command updates the three changed canonical files and preserves other
local files. An initial unsupported `--skill` sync flag and an audit argument
treated as a name instead of a directory were rejected before mutation; the
correct sync and scoped source/runtime/full audit then pass.

Actual installation/painting inside signed-in Claude Desktop or ChatGPT remains
unverified as documented in the original release. This revision changes default
selection and authored component chrome, not those host acceptance boundaries.
