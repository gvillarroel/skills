# D3, SVG and procedural connected-diagram compactness

Date: 2026-10-04 in the repository's America/New_York task date; raw run
timestamps continue into 2026-10-05 UTC. Runtime model:
`openai-codex/gpt-5.6-luna`, the explicit backlog exception recorded after Spark
was unsupported before tools. Every final forward run used the runtime payload,
strict JSON mode, exact expected outputs and an unchanged copied skill bundle.

## Inventory and resulting behavior

| Skill | Relevant surface | Result |
| --- | --- | --- |
| `d3` | Processes, node-link networks, architecture, dependency and explanatory mechanisms | Added bounded, route-aware compactness guidance. The contract flow builder measures labels and packs nodes, allocates separate return/skip/parallel lanes and distinct endpoint ports, fits omitted dimensions, and preserves explicit dimensions. Network arrows attach outside measured circles, reciprocal/duplicate routes separate, self loops point outward, and an unrelated-node collision fails clearly. Native-size scrolling protects labels on narrow displays. |
| `svg-brief-design` | Ordered stage flows and connected decorative explanations | Added the connected-diagram procedure and made the flow scaffold the first construction route for supported ordered flows. The scaffold sizes each node to conservative final-font text bounds, defaults to 18 px labels and a 400×100 canvas, uses 35.4-unit node heights and fixed four-unit port gutters, and rejects insufficient room instead of shrinking text. |
| `procedural-svg-animation` | Semantic scenes and operational route explanations | Added compactness guidance that reserves the complete motion envelope. Isolated tests exposed a catalogue-only validator gap for caller-supplied labels, so a narrow connected-scene builder and dedicated validator now support ordered labels and an optional final-to-first return without changing the catalogue validator or published patterns. A three-stage scene defaults to 478×72 with 18 px text and 36-unit nodes. Heads remain visible, tokens start after reveal and stop outside the head envelope, and reduced motion retains all concepts and directions. |
| `hierarchy-lens` | Partition adjacency, pixel, organic and decision packing | Audited without changing behavior. The analytical partition replaces connectors with containment; organic/decision modes already pack tightly and retain exact record ownership. Compressing this data geometry would violate the chart/quantitative exclusion. |

Preserved requested canvas dimensions, labels, relationships, palette contracts,
meaningful motion space, solver coordinates and artistic negative space.
Chart scales, bar geometry and hierarchy partitions were not compressed.
No published example or gallery source changed.

## Deterministic and browser checks

The following commands passed after the relevant final source changes:

```text
uv run --script skills/d3/scripts/test_compact_diagrams.py
uv run --script skills/d3/assets/examples/skill-tests/test_palette_contract.py
uv run --script skills/svg-brief-design/scripts/test_scaffold.py
uv run --script skills/procedural-svg-animation/scripts/test_connected_scene.py
uv run --script skills/procedural-svg-animation/scripts/test_multistrata_contracts.py
uv run --script skills/procedural-svg-animation/scripts/multistrata_core.py --self-test --json
git diff --check -- skills/d3 skills/svg-brief-design skills/procedural-svg-animation
```

- D3: five Chromium geometry tests pass, including content/fixed dimensions,
  narrow-screen native size, measured text fit, skip/return/parallel/self flows,
  reciprocal/self networks, single/two/three-node networks, full endpoint
  separation, route samples against unrelated nodes, and unchanged 900×520 bar
  dimensions. The seven existing palette tests pass.
- SVG: all 17 scaffold tests pass, including exact labels, horizontal/vertical
  four-unit port attachment, independent arrow contrast, content-sized nodes,
  deterministic renders, invalid input and insufficient readable dimensions.
- Procedural: four connected-scene tests pass. Missing heads, changed targets,
  changed token motion and narrowed nodes are rejected. Chromium checks final
  text fit and token/node/head clearance at eight times for a chain and a
  return loop, with readable reduced motion. Existing numerical self-tests and
  five adversarial catalogue mutations pass.

## Strict isolated release evidence

Each required output path was supplied with its own `--expect-output`. The
following final cohorts passed all strict gates and independent visual review:

| Case | Run IDs under `evaluations/runs/` | Exact outputs | Result |
| --- | --- | --- | --- |
| D3 process contract | `20261004-diagram-compact-d3-contract-luna-2` | `artifacts/workflow.html`, `artifacts/decision.json`, `artifacts/workflow.svg`, `artifacts/preview.png` | 1/1 pass; 345×135 content canvas, 16 px labels and 32-unit nodes |
| D3 network boundary contract | `20261004-diagram-compact-d3-network-contract-luna-1` | `artifacts/network.html`, `artifacts/decision.json`, `artifacts/network.svg`, `artifacts/preview.png` | 1/1 pass; requested 720×400 retained, all five reciprocal/duplicate/self directions visible |
| D3 natural consent workflow | `20261004-diagram-compact-d3-natural-luna-1`, `-2`, `-3` | `artifacts/consent.html`, `artifacts/decision.json`, `artifacts/consent.svg`, `artifacts/preview.png` | 3/3 pass; four full labels and return edge, 510×168/169 occupied canvas |
| SVG default-flow contract | `20261004-diagram-compact-svg-contract-luna-3` | `artifacts/design.json`, `artifacts/process.svg`, `artifacts/preview.png` | 1/1 pass; compact 400×100 default and readable 18 px labels |
| SVG natural five-stage review | `20261004-diagram-compact-svg-natural-luna-4`, `-5`, `-6` | `artifacts/review.svg`, `artifacts/preview.png` | 3/3 pass; requested 680×160 retained, every stage in a 35.4-unit content-sized node at 18 px |
| Procedural connected-scene contract | `20261004-diagram-compact-procedural-connected-contract-luna-1` | `artifacts/route.svg`, `artifacts/preview.png`, `artifacts/browser.json` | 1/1 pass; 478×72, named endpoints, readable full and reduced-motion states |
| Procedural natural message scene | `20261004-diagram-compact-procedural-natural-luna-4`, `-5`, `-6` | `artifacts/message.svg`, `artifacts/preview.png`, `artifacts/browser.json` | 3/3 pass; 478×72, full exact labels and directional paths |

Representative command, with the same strict flags used for each skill and
case above:

```text
uv run --script scripts/run-pi-skill-eval.py d3 --prompt-file evaluations/pi-prompts/diagram-compact-d3-natural-20261004.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id 20261004-diagram-compact-d3-natural-luna-1 --expect-output artifacts/consent.html --expect-output artifacts/decision.json --expect-output artifacts/consent.svg --expect-output artifacts/preview.png
```

Contract cases additionally used `--require-exact-command-from-prompt`.
Reusable prompt files are in `evaluations/pi-prompts/diagram-compact-*-20261004.md`.
The separate historical catalogue regression
`20261004-diagram-compact-procedural-contract-luna-2` passed before the new
connected helper was added. Its 18-file runtime SHA-256 was
`2b928763dd06bd8540949fc17abb11b78503d55805da75bfad305d668e66cb0f`.
It is retained as pre-helper evidence, rather than current-bundle acceptance.

Every final trace was summarized with:

```text
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/trace-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex "(?i)(^|[\\/])assets[\\/]examples([\\/]|$)"
```

All 13 final summaries pass. Read surfaces contain the prompt, target
`SKILL.md`, focused matching references/palette data and generated task artifacts.
They do not read acceptance examples, sibling skills or repository docs. The
new scene route reads `references/connected-scenes.md` instead of the complete
pattern catalogue. Raw manifests retain exact output hashes and payload hashes.

Independent evaluator Chromium inspection checked exact output labels, final
font sizes, actual painted text bounds, node fit and requested dimensions for
all 13 final outputs. Its raw result is
`evaluations/runs/diagram-compact-svg/final-artifact-check.json`. All 13 pass.
All final previews were opened for direct visual inspection. Bulky screenshots,
browser reports and event logs remain in the ignored run directory.

## Current-bundle catalogue regression

The additional fresh catalogue command contract
`20261004-diagram-compact-procedural-contract-luna-3` passed on the unchanged
current 21-file procedural runtime bundle, SHA-256
`cf8211540382faed79d9104fd19bb3975c3e6d8ab18b5f20165512fc2741a7b5`.
It used Luna with high thinking and completed in 47.405 seconds. This catalogue
regression is separate from the 13 final connected/network cases above; it
does not replace or expand their compact-layout coverage.

```text
uv run --script scripts/run-pi-skill-eval.py procedural-svg-animation --prompt-file evaluations/pi-prompts/diagram-compact-procedural-contract-20261004.md --model openai-codex/gpt-5.6-luna --thinking high --mode json --strict --require-exact-command-from-prompt --run-id 20261004-diagram-compact-procedural-contract-luna-3 --expect-output artifacts/route.svg --expect-output artifacts/preview.png --expect-output artifacts/browser.json
```

All strict gates passed, including the literal fenced build command, three
exact outputs and identical before/after payload digests. The observed-model
summary at that run's `trace-summary.json` passed with only `gpt-5.6-luna`, zero
invalid event JSON and zero tool errors. The trace reads the prompt, skill entry
point, runtime/validation reference, and generated browser report and PNG. It
queries the one requested pattern through `--describe`; it does not read the
catalogue, examples, sibling skills or repository documents.

Independent native inspection passed at the unchanged 960×640 delivery size.
Seven real-time states cover initial growth, later growth, two operating phases,
the loop, document reload and reduced motion. Visible labels and tokens stay in
bounds without text collisions; operating tokens traverse the root-to-leaf
network, and reduced motion retains all 63 static branch paths. Manual review
confirmed the complete native preview, network silhouette and route motion.
Raw-pixel checks confirm identical complete header and footer paint in all seven
frames. Local evidence is under
`projects/diagram-compactness/artifacts/reviews/20261004-diagram-compact-procedural-contract-luna-3-native/`
in `browser.json`, `static-paint.json` and native PNGs. The SVG SHA-256 is
`4265ca90f2fcaaf4c3690c5d195071e6bf03249f5928c570c88f6a19922832a8`;
its bytes match the pre-helper catalogue output exactly. No skill source changed
for this regression closure, and the owned browser was closed.

## Retained failures and repairs

- D3/SVG first contract attempts created every output with zero tool errors,
  but the extra command-contract gate rejected their `text` code fences with
  `no-fenced-command-in-prompt`. Classification: harness/evaluator prompt.
  Changed contract fences to `bash` and ran fresh workspaces. Did not weaken
  the gate or reclassify those first attempts as passes.
- Procedural first contract named the nonexistent `procedural-svg-draw-follow`
  ID. Classification: evaluator prompt. The corrected catalogue contract uses
  the actual `procedural-svg-growth-to-flow` ID; the failed attempt and all its
  recovery tool errors remain preserved.
- SVG natural attempts 1–3 passed strict execution but produced hand-authored
  nodes 64–80 units high around 15–18 px labels. Independent inspection rejected
  their compactness. Classification: skill guidance was insufficiently concrete
  for this supported route. Required the already bundled content-sized flow
  scaffold for ordered flows, then ran fresh final attempts 4–6. All three now
  pass; the previous outputs were retained.
- Procedural custom natural attempts 1–3 could not satisfy the catalogue-only
  validator without impersonating unrelated catalogue metadata; auxiliary tool
  errors and an unnecessary complete-catalogue read also occurred.
  Classification: missing custom-scene skill route, with additional agent
  recovery mistakes. Added the self-contained narrow helper and dedicated
  validator, preserved catalogue validation, and ran final fresh attempts 4–6.
  All three pass without tool errors or catalogue reads.
- The first independent evaluator text-fit check associated sibling scaffold
  labels with the first rectangle in their shared parent. Classification:
  evaluator validator. Corrected association to the exact `label-N`/`node-N`
  identity and reran; no skill source changed for this false alarm.

Coverage is representative connected diagram behavior, not a claim of a global
layout optimum or arbitrary-graph support. Unsupported graphs retain the
documented custom layout and explicit browser-audit path; the narrow builders
fail clearly rather than hiding a node, shrinking text or dropping a relation.
