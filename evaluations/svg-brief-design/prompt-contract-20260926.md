# Naturalistic prompt-contract cohort — 2026-09-26

**All three new cases passed their predeclared routing, exact-path, technical
SVG, and literal-text assertions.** A separate post hoc visual review observed
the requested labels and relationships in these three outputs. This is
baseline-only evidence of brief compliance on these fixtures; it is not a
comparison, a general accuracy estimate, or evidence that the skill improved.

## Predeclared requests and assertions

The exact Spanish prompts, output paths, text strings, and occurrence counts
were frozen at 09:50:00 UTC before inference. Three sequential calls and zero
retries were allowed. No purchased artwork, reference vector, style target,
reserved task, similarity computation, or fitness feedback was used.

| Request | Exact output | Required editable XML text, once each | Result |
| --- | --- | --- | --- |
| Three-stage flow with ordered arrows | `workflow.svg` | `Captura`, `Limpieza`, `Entrega` | Pass |
| Plain laboratory specimen label | `specimen.svg` | `MUESTRA 07`, `LAB-A` | Pass |
| Central energy vessel with input and output arrows | `energy.svg` | `Sol`, `Consumo` | Pass |

Each prompt explicitly required editable SVG text and no other text. The
evaluator collects the full text of each XML `text` node and requires its
multiset to equal the predeclared strings/counts. This does not independently
prove visibility, spelling rendered as paths, correct hierarchy, arrow
direction, or semantic relationships; those observations belong to the manual
review below.

The prompts remain short requests for a human-readable artifact, but their
exact text, occurrence counts, and delivery constraints are more explicit than
the earlier style-similarity benchmark. Do not compare their pass fraction with
that benchmark's numeric similarity score. These fixtures do not test arbitrary
short briefs or adversarially hidden text.

## Runtime and technical evidence

The unchanged baseline three-file bundle was discovered natively in each fresh
container's `~/.agents/skills/svg-brief-design` directory. The requests contained
no skill name or forced invocation. There was no `--skill` argument, `/skill`
command, injected body, ambient skill, or context file. Pi exposed only native
`read` and `write` tools. Every trace records an actual successful `SKILL.md`
read and the exact output write; model self-report is not accepted as evidence.

All three cases used `openai-codex/gpt-6-luna`, medium reasoning, Pi `0.84.2`, and
SSE transport. All completed normally with valid JSON events, no tool error,
unchanged source payload, and only the requested output in the agent workspace.
The model calls finished by 09:50:44 UTC. Total observed usage was 13,905 tokens;
USD cost is unavailable.

The existing verifier 1.1.0 `render()` function ran in its pinned offline image
without a reference mount. All outputs passed its static, self-contained vector,
viewBox, visible non-solid drawing, transparency, and monochrome checks. The
added evaluator-side XML assertion passed all seven required string/count
entries, with no additional `text` nodes. No similarity score was computed.

The model-side setup was reused from the unchanged earlier creation runner.
Only the new process's prospective cases, protocol fields, and evaluator-side
text checks differ. Earlier planning and creation observations remain intact.
No skill, installed bundle, description, or other metadata was changed.

## Post hoc manual review

The root reviewer and routing evaluator inspected independent rendered previews
after all model calls finished. The review is descriptive, applies only to these
three outputs, and does not alter the predeclared automated results.

- [Workflow preview](../runs/svg-brief-design-prompt-contract-20260926/three-stage-cleaning-flow/workflow.preview.jpg):
  the three boxes read left to right as Captura, Limpieza, and Entrega, with
  clear connecting arrows and legible, unclipped labels.
- [Specimen preview](../runs/svg-brief-design-prompt-contract-20260926/specimen-identification-label/specimen.preview.jpg):
  MUESTRA 07 is the larger title and LAB-A is smaller beneath it. There are no
  additional visible marks or machine-readable-code claims.
- [Energy preview](../runs/svg-brief-design-prompt-contract-20260926/energy-input-output-diagram/energy.preview.jpg):
  an outlined central vessel receives the Sol arrow at its left boundary and
  sends the Consumo arrow out at its right boundary. The labels are readable.
  The arrows express incoming and outgoing roles as requested; both point
  rightward in screen coordinates.

These observations support request compliance for the three reviewed fixtures.
The cohort has one attempt per case, no comparison arm, no calibrated semantic
judge, and no estimate of repeatability or general skill effect. It does not
replace the earlier planning routing miss or justify a promotion by itself.

## Reproduction and retained evidence

Runner:
[`validate_prompt_contract.py`](../../projects/svg-brief-design/scripts/validate_prompt_contract.py).
It is a separate entry point and does not edit either historical routing helper.

```text
wsl -d Ubuntu --exec env FOX_PI_AUTH=<existing-read-only-auth-path> \
  <pinned-runtime>/bin/python \
  <repository>/projects/svg-brief-design/scripts/validate_prompt_contract.py
```

Credentials travel only through stdin into the ephemeral container and are not
included in repository evidence. The original output directory is create-once.

- [Frozen protocol, including complete prompts](../runs/svg-brief-design-prompt-contract-20260926/protocol.json).
- [Machine-readable summary](../runs/svg-brief-design-prompt-contract-20260926/summary.json).
- Each case directory retains its original events, exact SVG, technical receipt,
  and independent preview.

Baseline `SKILL.md` SHA-256:
`740953f66380e648093af346231429ddf755d0fd564f910241157ea3beb57d04`.
The protocol records every source-file hash, both pinned image identities,
shared runner/setup hashes, the new entry-point hash, and the exact technical
check hash. `uv run python -m py_compile projects/svg-brief-design/scripts/validate_prompt_contract.py`
passed. Raw outputs and previews remain outside the shipped skill and under the
ignored evaluation run directory.
