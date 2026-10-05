# Compact connected video scenes — 2026-10-04

Final immutable-payload forward validation passes: command contract and all
three natural repetitions pass strict execution plus independent native review.
The final run prefix is `compact-video-20261004-sol-semantic-final-`.

## Scope and reusable changes

The `video` bundle owns placement and cross-asset routing, while producer
geometry, chart scales, exact frame dimensions and safe areas remain intact.
Connected explanatory scenes default to measured native-size concepts, short
clear routes, separate feedback/branch lanes and complete motion envelopes.
Supplied diagrams and richer specialist outputs keep their source semantics.

The self-contained fallback route consists of:

- `scripts/scaffold_connected_asset.py`: Chromium measures complete 18 px
  labels, then independently checks the actual native SVG text and clearance.
  Its passing report is explicitly scoped to single-asset painting.
- `scripts/scaffold_compact_scene.py`: composes 2–6 ordered concepts, optional
  last-to-first feedback and one upward branch; writes the requested contract,
  HTML and geometry paths. It retains all declared directed relationships.
  Repeatable `--meaning source:target=Description` parameters serialize
  source-backed relationship descriptions without manual JSON replacement.
- `references/compact-fallback-assets.md`: input contract, commands, protected
  bounds, supported topology and source-preservation boundary.
- `references/browser-rendering.md`: native planning-only capture and actual
  screenshot paths, held-state arrow audit, and correct single-scene assertions.

The existing compositor now paints a complete static head after each route
arrives, persists it with the shaft, and keeps the moving token outside the
node/head envelope. Validated normalized polyline waypoints support distinct
feedback corridors. Direction-aware curve tangents fix backwards source/target
approaches. Insufficient terminal runs or signal travel fail explicitly rather
than producing an unreadable path. The contract validator rejects malformed,
nonfinite and out-of-canvas waypoints.

The video paint auditor now infers the actual stage's CSS backing through its
ancestors, rather than assuming the differently colored outer document body.
Its CLI supports an explicit deterministic timestamp and optional actual canvas
paint. The whole `#stage` includes sibling asset and connector SVGs. Tests retain
the contrast/occlusion gates; no issue class is disabled.

## Measured compaction and independent native review

A prior readable sensor-loop baseline occupies **404×157 px**. A concrete
additional reduction uses separate clearance budgets: 22 px outer terminal
lanes for the full head approach, and a 10 px lower corridor for the 7 px token
radius plus 3 px body clearance. The final complete motion envelope occupies
**396×141 px**, **11.97% less area** than that baseline, at the same 18 px text,
12 px heads, 4 px strokes and four retained relationships. Both versions keep
the requested 960×540 frame and 24 px safe area.

The 52 px forward/branch gaps include source and target clearances, full heads
and at least 12 px of actual token travel. A 48 px candidate is explicitly
rejected by the compositor. These are measured supported-topology budgets,
not a claim of global mathematical packing optimality.

Native screenshots were captured at forward midpoints, feedback midpoint,
branch midpoint and the held state. The final held image and feedback midpoint
were manually opened: full labels remain distinct, all four heads are visible
after arrival, feedback stays below the concepts, and its signal stays clear
of the bodies. Independent Chromium tests additionally check token/body
clearance, complete head/body bounds, route samples against every unrelated
node, actual 18 px text and full expected labels at all sampled states.

Evidence remains locally under ignored
`projects/diagram-compactness/artifacts/{data,images,reviews}/video-tight*`.

## Deterministic gates

```text
uv run --script skills/video/scripts/test_connected_asset.py
uv run --script skills/video/scripts/test_compact_scene.py
uv run --script skills/video/scripts/test_compositor_arrows.py
uv run --script skills/video/scripts/test_scene_contracts.py
uv run --script scripts/validate-skills.py --skill skills/video
```

All pass: measured-asset tests **2/2**, compact-scene tests **3/3** (including
two-node, six-node/long-branch bounds and unreadable/nonfinite refusal), arrow
tests **5/5**, existing scene contracts and actual MP4 smoke **13/13**.
The final compact-scene test includes at least 2.8 px measured token/body
clearance, allowing subpixel rounding around the declared 3 px clearance.

## Retained development evidence

Earlier `final`, `v2`, `v3`, `release*` and `sol-*` attempts remain in the raw
registry. Windows process exhaustion interrupted early batches; these are
infrastructure failures, not passes. Other sampled agent errors remain agent
failures: wrong exact paths, plain Python dependency calls, a multi-scene beat
threshold for one scene, or visual-ID assertions without their required manifest
and composition plan. Recovered final images do not erase strict tool errors.

`sol-release-contract` was strict green but visual red: its held route had no
arrowhead. `sol-head-release-natural-1` recovered readable heads but still used
needlessly long 98–106 px forward gaps and a 97 px branch gap. These findings
led to actual native-head and measured-layout helpers instead of accepting the
agent's unsupported minimal-layout claim.

`sol-compact-release-contract` exposed a genuine audit backing defect: a red
arrow on the light stage was measured against the black outer body. The backing
and held-timestamp fixes are covered by the native CLI regression.
`sol-paint-final-contract` and natural repetition 1 passed strict plus visual
checks on the previous 404×157 baseline, but their cohort was superseded after
the independent tighter-lane comparison. Those successes are development
evidence and are not substituted for the final frozen cohort.

The first `sol-motion-final` natural cohort independently passed all native
geometry checks, but only one of three runs passed strict execution. Both failed
repetitions manually rewrote multiline metadata and introduced the same missing
JSON comma before recovery. This concrete burden led to the typed `--meaning`
interface, a quote-preservation regression and parser/serializer-only guidance.
Its contract also guessed nonexistent asset paths; the final guidance routes
reads to actual contract-declared paths. No strict failure was relabeled a pass.

## Final forward cohort

Model exception: `openai-codex/gpt-5.6-sol`, recorded in `SKILLS.md`, with medium
thinking. Use JSON strict mode, every exact required output, runtime-only bundle,
no ambient discovery, clean read surface, zero tool errors and unchanged copied
payload. The harness and its forbidden-read rules are unchanged.

```text
uv run --script projects/diagram-compactness/scripts/run_root_cases.py sol-semantic-final all video openai-codex/gpt-5.6-sol
uv run --script projects/diagram-compactness/scripts/inspect_video_scene.py <run-id>
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error
```

| Final suffix | Strict execution | Independent native artifact |
| --- | --- | --- |
| `contract` | Pass | Pass: 5 states, 2 full 18 px labels, one complete held head. |
| `natural-1` | Pass | Pass: 17 states, all 4 full labels/relations, no token/node/route collision. |
| `natural-2` | Pass | Pass: same native quality and full motion clearance. |
| `natural-3` | Pass | Pass: same native quality and full motion clearance. |

All four runs use the same final runtime SHA-256
`74a94bfb9cfd346fe4b1fe977e91e560b21846e4b54ac59c1585afa69e7f1be1`.
Observed Sol, zero tool errors, valid JSON events, every exact output, clean read
surface and immutable payload pass. The independent collector reruns the event
summarizer rather than trusting the tested agent's prose:

```text
uv run --script projects/diagram-compactness/scripts/collect_video_evidence.py
```

The bounded evidence is [video-sol-semantic-final-20261004.json](video-sol-semantic-final-20261004.json).
All 56 independently sampled states pass complete-label, viewport, node/route,
head/body and token/body geometry checks; minimum observed token clearance is
at least 3 px. Whole-stage held audits show one head/shaft for the command case
and four for every natural case, with no contrast/occlusion issues. Held and
critical motion PNGs were manually opened at native size. No global packing
optimum is asserted. Bulky traces, copied bundles, PNGs and build output remain
ignored under `evaluations/runs/` and project artifact directories.
