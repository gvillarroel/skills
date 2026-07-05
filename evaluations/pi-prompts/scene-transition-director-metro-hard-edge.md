Create a strict JSON scene transition plan at exactly:

`projects/metro-transition-director-validation/transition-plan.json`

First action: read `../prompt.md` directly. Do not run directory listings or shell probes at any point. Do not write into the copied skill directory.

Use `scene-transition-director`. The copied skill is at `skills/scene-transition-director`. Read the source-preservation, transition-decision-guide, transition-pattern-catalog, and transition-plan-contract references needed for a JSON plan from that path. Preserve exact scene IDs, persistent element name, and anchors.

Scene chain:

- `s01-intake-grid`: three square intake cells feed the event bus.
- `s02-feedback-control`: queue pressure triggers the feedback throttle gate.
- `s03-output-proof`: output continues after throttle.

Persistent element name: `red work packet`

Style constraints:

- Metro Minimal Tonal Motion.
- Strict 4 px grid, shared baselines, orthogonal or axis-locked paths.
- Square, hard-edge, 0-radius masks, panels, and apertures.
- No curved portals, pills, organic blobs, soft cards, circular wipes, or generic pulses.
- Because validation uses substring checks, do not write soft-corner contradiction terms anywhere in the JSON, even to say they are absent. Use `curved`, `soft-corner`, `square`, or `0-radius` instead.

Create exactly two transitions:

1. `s01-intake-grid` -> `s02-feedback-control`
2. `s02-feedback-control` -> `s03-output-proof`

Each transition must include `semanticPurpose`, `stateChange`, `attentionHandoff`, `styleContinuity`, `alignmentRule`, `edgeRule`, `genericMotionRejected`, `validationFrames`, and structured `validationChecks`.

After writing the JSON, run exactly:

```bash
uv run --script skills/scene-transition-director/scripts/validate_transition_plan.py --plan projects/metro-transition-director-validation/transition-plan.json --expect-transitions 2 --expect-persistent-name "red work packet" --expect-chain "s01-intake-grid,s02-feedback-control,s03-output-proof" --require-anchor "feedback throttle gate" --require-anchor "output continues" --forbid gsap --require-semantic-fields --require-square-edge-style
```

Fix the JSON until validation passes.
