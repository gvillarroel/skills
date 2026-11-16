# Clean presentation revision — November 14, 2026

Release: **0.2.0**. Status: **done**. This revision implements explicit user
feedback: remove visible titles, use the presentation space in balance, and
add only a few contextual words when titles are explicitly requested.

## Behavior and reusable guidance

- Remove automatic opening headings, explanatory subtitles, chart headings,
  palette slogans and closing text. Preserve semantic labels, values, units,
  legends and a small provenance tag for illustrative data.
- Expand the particle/relationship field, center the native Mermaid diagram,
  enlarge paired table/chart reading regions and the category partition, and
  arrange the world as four balanced quadrants for the overview.
- Follow actual native node boundaries with the guide dot, avoiding label
  occlusion. Display transport bridges during camera motion and overview;
  reading states retain clear chart and table areas.
- Default `presentation.contextLabels` to an empty mapping. An explicitly
  requested beat may receive one short label, at most six words/48 characters.
  Do not reinterpret legacy copy fields as permission to render titles.
- Keep the 56-second duration, data, units, colorset policy and editable timing.

The transferable rules are in `SKILL.md`, `references/visual-direction.md`,
`references/data-storytelling.md` and `references/pattern-recipes.md` under the
owning skill. The runtime remains standalone; generated movies and screenshots
remain under the project's ignored artifacts.

## Executed validation

| Check | Evidence and outcome |
| --- | --- |
| Deterministic source contract | `uv run --script skills/line-world-video/scripts/test_line_world.py`: 11/11 pass, including default empty context, explicit short context and rejection of unbounded/unknown context labels |
| Actual composition | `uv run --script projects/line-world-video/scripts/verify_clean_layout.py`: 15/15 checks pass. No automatic headings or closing nodes; measured useful bounds and centered geometry in five reading views; four overview quadrants; explicit context appears only in its requested beat |
| Browser/vector audit | `render_line_world.py --project projects/line-world-video/artifacts/film --audit-only --report projects/line-world-video/artifacts/reviews/clean-audit.json`: 26 rendered states, zero findings. Includes beat-end states, visible values, common bar scales, focus paint, native labels, palette, deterministic seeks and explicit-context agreement |
| Native HyperFrames check | Project's `node scripts/hf.ts check --json --timeout 15000`: lint, runtime and layout pass, with zero layout errors and warnings |
| Native final render | HyperFrames 0.8.111, `render --quality delivery --workers 1 --experimental-fast-capture=false --output <line-world-clean.mp4>`: exit 0, actual screenshot capture, 1,680 frames, 56 seconds |
| Encoded artifact | `verify_delivery.py --video projects/line-world-video/artifacts/videos/line-world-clean.mp4 --label clean-decoded`: full decode, H.264/yuv420p, 1920×1080, 30/1 fps, 1,680 frames and 56.000000 seconds pass. Size 5,802,369 bytes. Fourteen decoded samples are nonblank; 49/111 half-second intervals show motion. Contact sheet and hero/overview frames visually inspected |
| Preview | `verify_preview.py`: 9/9 pass for seek, play/pause, beat selection, pan/reset, no filmed controls, mobile layout and browser errors |
| Isolated final cohort | Eight fresh `run-pi-skill-eval.py` runs under `20261114-line-world-clean-*`, JSON/strict/runtime, exact output paths, model `openai-codex/gpt-6.1-sol`, medium thinking: 8/8 strict passes |
| Independent cohort grading | `uv run --script evaluations/contracts/verify-line-world-runs.py --version clean`: 8/8 pass. Contract 1/1, boundary 1/1, naturalistic 3/3, generalization 3/3. Current payload equality, no unrequested context, exact data/units/retiming, actual browser audits and invalid-input preservation all pass. [Compact results](clean-results.json) |
| Metadata routing | `run-line-world-routing.py --run-id 20261114-line-world-clean-routing-sol-1`: 12/12 semantic selections with no forced skill; JSON null is the accepted no-skill representation, following the retained earlier evaluator repair |
| Portable bundle | Five skills, 401 runtime files, 5,354,805 uncompressed bytes. ZIP digest `24336cfdcb0aa3d30858ad4089ba9525a5b2a51f900267a8a3bd4dcb7a4ee2a7`. Fresh extracted starter and full browser audit pass |
| Native installation | `verify_plugin.py`: portable schema has zero errors; five Codex 0.167.0 version/catalog/discovery/install/list commands exit 0 in an isolated home; all five cached skills match |
| Editable project | `package_demo.py`: 32-file archive, fresh extracted rebuild exits 0 and reproduces exact timing |
| Bundle and installation | Source/runtime/full standalone validation passes. Focused repository-helper sync updates ten files and verifies all 30 canonical/installed files |

The Spark account/provider rejection from the initial release remains the
reason for the explicit Sol 6.1 model exception. Strict checks preserve actual
model reporting, JSON validity, zero tool errors, exact outputs, read-surface
limits and an unchanged read-only payload. The eight cases are a fresh clean
presentation cohort; do not pool them with the earlier V2/V3 cohorts.

## Repository scope

Pattern IDs, skill independence and payload checks pass. The global validator
retains the same four pre-existing reference-route findings in unrelated
semantic skills. Focused validation and local synchronization for this skill
pass. No unrelated semantic sources were changed, no public gallery was added,
and no public Pages deployment is claimed.

The artifact is a silent, illustrative demonstration. The starter remains a
16:9 paired-value/history grammar with two to eight nonnegative records. A
context label is added only through an explicit request; accessibility metadata
does not become a visible heading.
