# Actual-creation routing control — 2026-09-26

**Both new actual-creation cases passed unforced routing and technical SVG
validation.** This narrower result supplements the separate
[planning-only control](routing-20260926.md), whose 3/4 result and diagram routing
miss remain unchanged. No retry, metadata revision, or replacement observation
was used.

## Prospective contract

Two new Spanish requests asked for actual files: a circular rainwater-collection
diagram and an original fern ornament for an invitation corner. Each named its
own exact SVG output path and requested editable black geometry on a transparent
background. Neither named the skill or asked the agent to read instructions.

The unchanged three-file bundle was installed in native automatic discovery at
`~/.agents/skills/svg-brief-design` in a fresh ephemeral container. There was no
`--skill`, `/skill` command, injected skill body, ambient skill, or context file.
Only native `read` and `write` tools were enabled. The declared budget was two
calls, concurrency one, zero retries, each at one CPU and 1 GiB. Both used
`openai-codex/gpt-6-luna`, medium reasoning, Pi `0.84.2`, and SSE transport.

| Case | Observed native SKILL.md read | Exact output | Existing technical verifier |
| --- | --- | --- | --- |
| Rainwater cycle diagram | Successful | `rainwater.svg` | Pass |
| Fern corner ornament | Successful | `fern-corner.svg` | Pass |

Both traces contain an actual `read` tool call for the skill's `SKILL.md`, paired
with a successful completion event, followed by the exact output write. Both
match the required provider and model, contain valid JSONL, have no tool errors,
and preserve the complete source bundle. Only the requested output was created
in each agent workspace. Combined observed usage was 11,527 tokens; USD cost is
unavailable.

Technical checks call the existing verifier 1.1.0 `render()` function in its
pinned offline image. This validates self-contained static vector markup,
positive viewBox dimensions, a visible non-solid drawing, transparency, and
monochrome output. No reference artwork was mounted or accessed, and no
similarity or fitness score was computed. The model and verifier were executed
sequentially per case.

## Post hoc manual quality review

Independent previews were rendered after both calls completed and reviewed by
the root reviewer and the routing evaluator. The
[rainwater preview](../runs/svg-brief-design-creation-routing-20260926/rainwater-cycle-diagram/rainwater.preview.jpg)
contains a recognizable cloud, roof, tank, and circular flow. Several arrows
point around the composition without visibly terminating at the three named
components, and some rain marks overlap the roof. Do not infer semantic or
relationship correctness from the routing result. The
[ornament preview](../runs/svg-brief-design-creation-routing-20260926/fern-corner-ornament/fern-corner.preview.jpg)
contains two curved leafy stems, but its leaflets read as generic broad leaves
rather than clearly fern fronds; the upper stem reaches the canvas edge. No
calibrated subject-fidelity test was conducted. These observations are outside
the routing and technical acceptance assertions and do not change any recorded
pass or reward. They are not a semantic-quality pass or proof of improvement
over another skill version.

Two positive creation cases do not establish general routing accuracy. The
earlier planning miss remains an open limitation. No canonical skill,
installation, metadata, or private evaluation data was changed.

## Reproduction and retained evidence

Runner:
[`validate_creation_routing.py`](../../projects/svg-brief-design/scripts/validate_creation_routing.py).
It reuses the unchanged native-discovery setup from the planning runner, enables
the additional `write` tool, and independently records all creation evidence.

```text
wsl -d Ubuntu --exec env FOX_PI_AUTH=<existing-read-only-auth-path> \
  <pinned-runtime>/bin/python \
  <repository>/projects/svg-brief-design/scripts/validate_creation_routing.py
```

Credentials travel only through stdin to the ephemeral container and are not
stored in repository evidence. The original output directory is create-once.

- [Predeclared protocol](../runs/svg-brief-design-creation-routing-20260926/protocol.json).
- [Machine-readable results](../runs/svg-brief-design-creation-routing-20260926/summary.json).
- [Rainwater preview](../runs/svg-brief-design-creation-routing-20260926/rainwater-cycle-diagram/rainwater.preview.jpg).
- [Fern preview](../runs/svg-brief-design-creation-routing-20260926/fern-corner-ornament/fern-corner.preview.jpg).

Source `SKILL.md` SHA-256:
`740953f66380e648093af346231429ddf755d0fd564f910241157ea3beb57d04`.
The protocol records all source-file digests, runner and shared setup digests,
and both pinned Docker image identities. Native traces, exact SVG files,
receipts, and independent previews remain in the ignored evidence directory.

`uv run python -m py_compile projects/svg-brief-design/scripts/validate_creation_routing.py`
passed. This evidence applies to the unchanged bundle and these two actual
creation requests only.
