# Cross-v2 generalization validation

Date: October 24, 2026, America/New_York (UTC logs are October 25).
Skill: `desktop-plugin-ui`. Model: `openai-codex/gpt-5.6-luna`, continuing the
parent task's recorded model exception. Prompt:
[desktop-plugin-ui-cross-generalization.md](../pi-prompts/desktop-plugin-ui-cross-generalization.md).

**Result: 3/3 strict harness passes, 3/3 original structured-evidence grader
passes, and 3/3 manual factual reviews passed.** The prompt and original grader
were unchanged. The copied skill clarifies literal evidence labels in JSON;
the previous v1 format failure remains preserved in
[cross-v1-generalization.md](cross-v1-generalization.md). No generated output
was repaired, and no criterion was relaxed.

## Frozen run contract

The three 15-file runtime bundles share payload SHA-256
`455db7f6daee26026e3c3be314406baf2f19a9e3c31c2250f09fc4d978389c05`.
Before/after skill integrity passed in every run. The prompt SHA-256 remains
`45d19d83b245ed31d9e0307b2da37910addb2cef0179670f91d44c5e52458a89`.
No skill file changed during the three concurrent runs.

For each `N` in 1, 2, 3, the exact command was:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-cross-generalization.md --model openai-codex/gpt-5.6-luna --mode json --strict --timeout-seconds 600 --run-id 20261024-desktop-ui-cross-v2-generalization-luna-N --expect-output handoff/restricted-surfaces.md --expect-output handoff/recovery-plan.json --expect-output-json-field handoff/recovery-plan.json::host_acceptance_verified=false --expect-output-json-field handoff/recovery-plan.json::task_empirical_tests_performed=false
```

Every run created both exact nonempty artifacts, passed the false-boolean
assertions, and exited zero without timeout, invalid event JSON, tool errors,
read-policy findings, or payload mutation. The mandatory per-run trace command
was also executed and saved as `model-trace-summary.json`:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-cross-v2-generalization-luna-N/events.jsonl --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

| Suffix | Duration | Model records | Read/write/bash calls | Original grader | Independent source checker |
| --- | ---: | ---: | --- | --- | --- |
| `luna-1` | 87.720 s | 9 | 14 / 2 / 3 | Passed | 52 official URLs; no findings |
| `luna-2` | 75.264 s | 8 | 13 / 2 / 2 | Passed | 43 official URLs; no findings |
| `luna-3` | 89.564 s | 9 | 14 / 2 / 3 | Passed | 29 official URLs; no findings |

All model records identify exactly `openai-codex` / `gpt-5.6-luna`. Reads were
limited to the copied prompt, SKILL.md, and relevant compact references; no
examples, sibling skills, project artifacts, repository documents, or external
sources were read. The broad cross-host task justifies the 11–12 reference
reads. Bash only used the bundled source catalog/checker; no account, app,
installation or network command occurred.

The unmodified original grader was run with:

```powershell
uv run --script evaluations/desktop-plugin-ui/inspect_cross_runs.py --prefix 20261024-desktop-ui-cross-v2-generalization-luna- --output evaluations/desktop-plugin-ui/cross-v2-generalization-structure.json
```

It passed all three runs with one frozen payload, 42 canonical patterns in
each bundle, 19/20/19 selected patterns, no structural findings, and no broad
exclusion or external-command review cues.

## Manual findings

All six artifacts were inspected. Every JSON has the required fields and all
five host IDs, both task-level booleans false, and six historical observations
with literal empirical labels at their recorded evidence layer. Unlike v1
run 3, no historical array relies on narrative alone for the empirical label.

All three plans reject the universal HTML assumption, retain useful text and
structured results, and correctly choose current terminal/VS Code routes.
They distinguish Claude native Mod controls from HTML, surface-specific
Svg/Image/Raster validation from real image pixels, terminal Copilot forms
from MCP Apps/canvas painting, and an extension-owned VS Code webview from
Copilot chat. They handle decline/cancel/null without granting approval.

Codex `never` uses the automatic-decline path and continues with text/data;
the future `on-request` custom client owns callback presentation and request
IDs. HTML bytes, image input, MCP metadata, and advertised canvas capability
are not promoted to a widget. Prior Claude Desktop Chat paint/direct action/
error/fullscreen evidence is preserved without claiming host elicitation,
remote or mobile acceptance. ChatGPT setup-to-consent remains separate from
connection completion and component paint.

Deployment and budget rules preserve local stdio versus remote HTTPS/tunnel,
host-specific origin rules, private tunnel gates, direct local controls before
model work, and soft-cap limitations. Future investigations require named-host
paint, interaction, cancellation, state recovery, lifecycle and text fallback.
No current task host session is invented. Minor wording compresses bare-SDK
callback support into the form discussion, but context does not imply that an
elicitation callback supplies a universal HTML renderer.

The forward agents checked both final artifacts and inspected `passed:true`.
The independent review reran the copied checker with `--fail-on-findings` and
manually reviewed citation scope; catalog membership was not treated as proof
of factual correctness. No blocking factual overclaim was found.

Pi-reported evaluation-model usage is separate from Claude/Copilot application
usage and from an inference HTTP-request count:

| Run | Input | Output | Cache read | Total tokens |
| --- | ---: | ---: | ---: | ---: |
| 1 | 38,096 | 11,532 | 145,024 | 194,652 |
| 2 | 36,403 | 10,348 | 109,568 | 156,319 |
| 3 | 38,812 | 12,247 | 159,872 | 210,931 |

## Evidence retention

Raw traces, manifests, generated artifacts, all strict checks, trace summaries,
and independent source checks remain under
`evaluations/runs/20261024-desktop-ui-cross-v2-generalization-luna-{1,2,3}/`.
The compact original-grader result is `cross-v2-generalization-structure.json`.

| Run | Markdown SHA-256 | JSON SHA-256 |
| --- | --- | --- |
| 1 | `865e6f8a2b2c26dd918a31e5f1a88b54afb7f44beceba361d397a8f643bf9561` | `a990346ae73658f14340072e2a449b7b5a121cf0438098d30321ec07d20b3b62` |
| 2 | `b3d1eae2583978b136c0e1c6a2cdd32932730a8168a6cb558d2780c77851bab0` | `794b8a4c75a31b74780f2b32f366fe5eb16f0939aec21931e186ecb032d91d2e` |
| 3 | `30787c598e270984de32d1785eb1e6a724ec5cce152e120989155a166989dd27` | `6990008b12d90ec51181c83bba25599c45e6916f50a053b164865dca821e06b1` |

This validates isolated skill use and generalization for the bounded planning
case. It does not add new empirical product-host acceptance.
