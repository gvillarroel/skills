# Composition and video solid-fill revision — 2026-10-03

The seven bundles below now prioritize opaque category fills without decorative
outlines. Inside labels use pure black or white selected by maximum WCAG contrast
on the actual fill. Canonical palette tokens remain unchanged; the root change
adds the ordered `solidSequence` and `textOnFill` metadata. Usable solid colors
are exhausted before explicit overflow combinations reuse a fill with border
color, dash and width variants. Borders contrast with their fill by at least
3:1, exclude the fill itself, and stay within widths 1–3. Each fill has nine
finite dash/width variants per qualifying border color; `overflowExhausted`
reports when that pool repeats. Direct labels, symbols or split views must
distinguish further identities. Meaningful connectors, axes, physical open line
geometry, explicit authored choices and imported source pixels retain their
contracts.

This is a supplementary contract and visual regression pass for an existing
skill revision. It is not a replacement for the full naturalistic,
generalization and ambiguity release cohorts. Existing recorded Pi model
exceptions are preserved.

| Bundle | Actual output change | Final strict isolated run |
| --- | --- | --- |
| compose-synchronized-svg | Full palette allocation; solid dependency and structural nodes; paired label tokens; borderless world hubs, module indexes, controls and frames; opaque text surfaces survive focus; detail labels and indexes respect camera visibility; all navigation inverse text is exact maximum-contrast black/white. | `solid-composition-compose-synchronized-svg-20261003-5` |
| diagram-composition | Native cards, taxonomy groups, matrix swatches, boundaries and headers use solid fills; interior text and native line icons use the actual fill's black/white contrast. | `solid-composition-diagram-composition-20261003-2` |
| hierarchy-lens | Analytical and exported hierarchy marks have no decorative outlines; on-fill text uses exact black/white; neutral toolbar and panel chrome is borderless. Numeric bands and missing-value semantics remain explicit. | `solid-composition-hierarchy-lens-20261003-1` |
| usefulcharts-style | Graph nodes, timeline categories, cohort/name pills and reading pockets use opaque solid fill without emphasis borders; inside text is black/white. | `solid-composition-usefulcharts-style-20261003-2` |
| hyperframes-explainer | Generated filled mechanism bodies, starter tank and conserved-store fixture use solid neutral silhouettes; filled geometry no longer inherits a default dark stroke. Open physical line geometry is preserved. | `solid-composition-hyperframes-explainer-20261003-1` |
| video | Shared guidance and palette helper; published AI gallery promotes pale outlined category cards to their solid category color, removes mark outlines and white text halos, and selects contrast text under opaque filled surfaces. | `solid-composition-video-20261003-2` |
| manim-svg-video | Opaque wrapper tiles and placeholders have default border width zero; title, tile and placeholder text compute black/white contrast. Explicit border-width and text-color options remain available. | `solid-composition-manim-svg-video-20261003-3` |

All seven final runs passed strict artifact, event JSON, observed model, clean
read-surface and unchanged copied-skill gates. HyperFrames uses the recorded
`openai-codex/gpt-6-luna` exception; the other six use the recorded
`openai-codex/gpt-5.6-luna` exception. Each case copies only the runtime skill
payload, excludes acceptance examples, disables ambient context/skill discovery,
and requires exact output paths. Prompts are retained in [prompts](prompts/).
Machine evidence, exact harness commands, final runtime hashes and artifact
hashes are in [validation-20261003.json](validation-20261003.json). Original
passing snapshots superseded by later refinements are retained and identified
there; they are not the current-source acceptance evidence.

Deterministic verification passed:

- Composition: 80 tool regressions, 16 theme/palette/exhaustion tests, six rendered
  theme tests and three text/fill pairing tests. The palette test checks every
  allowed solid and both canvas exclusions, no outline throughout the initial
  cycle, and explicit overflow thereafter. Targeted tests check inverse
  navigation tokens, long overflow contrast and bounded widths. A separate
  independent WCAG calculation checks 6,240 styles across all five local helper
  copies, both palettes, three canvas colors and long cycles.
- Native diagram composition: 24 composition, 13 native family/browser, eight
  shared color and 21 connector tests.
- UsefulCharts: 27 chart, 51 editorial and 11 panel-poster tests.
- Hierarchy: 21 source/template tests and the full 1,200-record analytical browser
  audit, including export, numeric, focus and mobile states.
- HyperFrames: 11 generated mechanism and 45 explainer contract tests. The
  updated conserved-exchange fixture passes preflight and project generation.
- Video: 13 scene-contract checks, including real browser rendering and the
  mixed-media MP4 render/validation regression.
- Repository pattern IDs, skill structure and skill-independence checks pass.

The exact producer test commands and captured output are recorded by
`uv run --script projects/composition-solid-style/scripts/validate_producers.py`
in `projects/composition-solid-style/artifacts/tests/commands.json`.
Other exact verification commands used were:

```powershell
uv run --script skills/compose-synchronized-svg/scripts/test_synchronized_svg_tools.py
uv run --script skills/compose-synchronized-svg/scripts/test_theme_contract.py
uv run --script skills/compose-synchronized-svg/scripts/test_svg_themes.py
uv run --script skills/compose-synchronized-svg/scripts/test_svg_text_pairs.py
uv run --script skills/hyperframes-explainer/scripts/test_composition.py --work-dir projects/composition-solid-style/artifacts/hyperframes-composition-final
uv run --script skills/hyperframes-explainer/scripts/test_explainer.py --work-dir projects/composition-solid-style/artifacts/hyperframes-explainer-final
uv run --script skills/video/scripts/test_scene_contracts.py --json
uv run --script skills/hyperframes-explainer/scripts/explainer.py preflight --brief skills/hyperframes-explainer/assets/examples/conserved-exchange.json --report projects/composition-solid-style/artifacts/conserved-exchange-preflight.json
uv run --script skills/hyperframes-explainer/scripts/explainer.py build --brief skills/hyperframes-explainer/assets/examples/conserved-exchange.json --project projects/composition-solid-style/artifacts/conserved-exchange --report projects/composition-solid-style/artifacts/conserved-exchange-build.json
uv run --script skills/compose-synchronized-svg/scripts/audit_synchronized_svg.py skills/compose-synchronized-svg/assets/examples/compose-synchronized-svg/heatwave-tree.svg --report projects/composition-solid-style/artifacts/heatwave-browser-release.json --screenshot projects/composition-solid-style/artifacts/heatwave-browser-release.png --json
uv run --script projects/composition-solid-style/scripts/audit_solid_outputs.py
uv run --script projects/composition-solid-style/scripts/audit_navigation_pairs.py --output projects/composition-solid-style/artifacts/navigation-final.json
uv run --script projects/composition-solid-style/scripts/audit_overflow_helpers.py
uv run --script projects/composition-solid-style/scripts/run_final_overflow_contracts.py
uv run --script projects/composition-solid-style/scripts/regenerate_examples.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
```

`regenerate_examples.py` records 11 successful exact regeneration commands. It
rebuilds the two synchronized SVGs, four hierarchy views and three UsefulCharts
SVG/HTML pairs from their existing source models, preserving stable example and
pattern IDs. Pages publication, installation and repository-wide final evidence
are integrated by the parent task.

The independent browser style inspection passes 83 states: six composed/poster/
hierarchy fixtures plus seven animation times for all 11 published AI concepts.
It records outline absence and binary text pairs, with explicit overflow shapes
counted separately. Desktop and mobile screenshots are retained. The stronger
existing heatwave auditor separately passes all scenario, zoom, focus,
reduced-motion and script-free checks with zero contrast findings. These sampled
states do not prove every possible animation frame, custom source asset or
palette choice.

The final Manim smoke command was:

```powershell
uv run --script skills/manim-svg-video/scripts/compose_svg_video.py --discover-root evaluations/runs/solid-composition-manim-svg-video-20261003-1/workspace/output --include source.svg --out projects/composition-solid-style/artifacts/manim-smoke-visible --duration 3 --intro-seconds 0.2 --outro-seconds 0.2 --enter-seconds 0.2 --exit-seconds 0.2 --max-assets 1 --layout replace --active-slots 1 --show-labels --render --quality l --fps 5 --resolution 640,360
```

It produced a visible source/tile/label sequence; `ffprobe` confirms H.264,
640 × 360, 5 fps, 15 frames and exactly 3 seconds. The inspected middle frame and
probe are retained under `projects/composition-solid-style/artifacts/manim-smoke-visible/`.
The existing `SVGMobject` limitation remains: SVG text/CSS may be omitted or
simplified. This pass checks the authored wrapper and vector geometry, does not
claim browser-faithful source text import, and does not introduce a new raster
converter. No fresh HyperFrames MP4 encode was requested by its supplementary
project-generation contract.

Retained repaired failures establish the limits of the first style check:

- Initial composition text-token matching needed to recognize `--on-value-*`.
- Whitespace normalization was initially attached to the wrong scaffold return;
  fragment tests caught the missing return and the final 80 regressions pass.
- Actual browser contrast exposed module-tier hub indexes without their backing,
  faded unbound structural-node label surfaces, branches crossing singleton
  labels, and script-free overview link labels. The final painter fixes those
  states; overview link explanations retain their accessible titles and appear
  when the camera route calls for them.
- Video's geometric point test initially treated an unpainted activation outline
  as a background. It now skips unpainted candidates; the inspected Gemma label
  is white on the solid red model.
- The first 3-second Manim smoke spent its short duration in the default intro;
  the final smoke uses explicit short intro/outro and visibly tests the tile.
- The later on-fill review caught muted navigation text using `#cfcfcf` on
  `#333e48`. Both inverse tokens now select exact `#ffffff` on that backing,
  including help, tier and handoff text; light inverse backings select black.
  Actual computed navigation paint passes. A legacy test expectation was
  updated to the requested binary paint and all three browser pairing tests pass.
- Initial overflow border pools admitted colors below 3:1 contrast and allowed
  unbounded widths. Five helpers now use contrast-filtered finite pools with
  widths 1–3; final matching strict runs supersede the previous frozen payloads.

Bulky logs, screenshots, MP4s and retired failure reports stay in ignored project
artifacts or ignored `evaluations/runs/`. Source examples, compact references,
reusable scripts and this durable evidence remain versioned. No commit or push
was performed by the composition/video subagent.
