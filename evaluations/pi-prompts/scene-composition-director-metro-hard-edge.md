Create a strict JSON scene composition plan at exactly:

`projects/metro-composition-director-validation/composition-plan.json`

First action: read `../prompt.md` directly. Do not run directory listings or shell probes at any point. Do not write into the copied skill directory.

Use `scene-composition-director`. The copied skill is at `skills/scene-composition-director`. Read the source-preservation, selection-guide, and composition-brief-contract references needed for a JSON plan from that path. Preserve exact scene IDs and anchors.

Video constraints:

- Format: 1280x720.
- Style: Metro Minimal Tonal Motion, colorset1 red/gray/white/black palette.
- Alignment: strict 4 px modular grid with shared baselines.
- Edges: square, hard-edge, 0-radius panels and masks.
- Prohibited motifs: rounded cards, pills, organic blobs, soft panels, gradient orbs, and decorative UI chrome.
- Captions: none.
- Runtime handoff: deterministic HTML/D3/Anime.js is allowed later; GSAP is forbidden.
- Because validation uses substring checks, do not write the literal forbidden term `gsap` anywhere in the JSON, even to say it is forbidden. Use `renderer-neutral handoff` instead.

Scenes:

1. `s01-intake-grid`, duration `3s`: show three square intake cells feeding an event bus and bounded queue. Source anchors: `square intake cells`, `event bus`, `bounded queue`.
2. `s02-feedback-control`, duration `3s`: show queue pressure causing a feedback throttle gate while output continues. Source anchors: `queue pressure metric`, `feedback throttle gate`, `output stream`.

The JSON must include per-scene `alignmentGrid`, `edgePolicy`, `cornerPolicy`, `armatureAnchors`, `objectBounds`, `validationContract`, and structured `validationChecks` objects with `method`, `target`, and `passCriterion`.

After writing the JSON, run exactly:

```bash
uv run --script skills/scene-composition-director/scripts/validate_scene_composition_plan.py --plan projects/metro-composition-director-validation/composition-plan.json --expect-scenes 2 --require-anchor "bounded queue" --require-anchor "feedback throttle gate" --forbid gsap --require-strict-alignment --require-square-edges --require-validation-contract
```

Fix the JSON until validation passes.
