# PlantUML style delivery repair — 2026-10-04

Status: validating. All five strict isolated runtime outcomes pass. The first
exact-head deployment and public visual gates pass. Canonical source packaging
is repaired; a new exact-head public resource binding remains pending.

## Problem and delivered configuration

Native PlantUML families do not consistently honor generic theme properties.
The previous examples therefore combined pastel bodies, decorative gray
contours, missing internal glyphs, and text selected without checking its actual
backing. A palette-membership pass did not establish the desired style.

The delivery configuration now consists of two editable native themes,
`skills/plantuml-colorset-renderer/assets/themes/cs1.puml` and `cs2.puml`, plus
`native-style-rules.json` in the same directory. Native family selectors are
scoped separately. The fallback configuration covers all seven native ArchiMate
layers, Salt buttons, a separate grammar canvas, and semantic detail thickness.
Each layer has a distinct opaque solid color before outlined overflow.

The native SVG finish restores missing compartments, cylinder/queue curves and
component tabs, removes hardcoded decorative body contours, and chooses exact
black or white from actual label backing. Arrows use at least 3:1 contrast over
their sampled painted surfaces. Shallow body contacts and complete filled tips
receive local gutter clearance while routes and native curve controls remain.
SVG-capable PNG exports derive from the finished SVG. Ditaa uses a bounded
source-backed raster adapter with no shadows and explicit unsupported-geometry
errors. Authored presentation, real source media, and native math retain their
documented narrower contracts.

Comments, quoted labels, title words, and layout-only settings cannot disable
default styling. Actual image/sprite syntax, including scaled references,
retains the media-preservation path. Optioned Ditaa directives remain raster
only. These cases were reproduced with native PlantUML 1.2026.6 before repair
and verified again after repair.

## Deterministic and native checks

- Focused scripts: 72 tests pass (coverage 19, arrows 23, native styles 14,
  Ditaa 12, raster delivery 4).
- Both complete native render batches pass: 29 fixture results, 55 actual SVG
  and PNG outputs per palette, zero failures. Chronology remains explicitly
  unavailable in the frozen version and produces no artifact.
- Published batches pass: 29 results and 28 artifacts per palette, covering all
  28 registered family identities exactly. The canonical gallery retains one
  example-set ID and its Colorset 1 asset source/legacy route.
- Both report validators and exact family/fixture coverage checks pass.
- Repository pattern-ID, skill structure, source authoring, independence and
  payload checks pass. The Pages output boundary's three regression tests pass.
- The actual remote Kroki Ditaa path passes with no-shadow/scale options; local
  Ditaa probes verify scales, uppercase native tags, glyph preservation and
  explicit contract failures.

Reproduce the focused gates with `uv run --script` on these scripts under
`skills/plantuml-colorset-renderer/scripts/`: `test_plantuml_coverage.py`,
`test_arrow_contrast.py`, `test_native_styles.py`, `test_ditaa_styles.py`, and
`test_plantuml_raster.py`.

For native fixture batches, use `render_plantuml_directory.py` with
`assets/examples/base`, both `--colorset` choices, the ordinary local `plantuml`
CLI, `--coverage-manifest references/diagram-types.json`, and both output
formats. Use `--publication-only` for gallery assets. Validate with
`validate_plantuml_render_report.py` and `validate_plantuml_coverage.py`.

## Independent review

The independent Chromium auditor is
`projects/plantuml-style-repair/scripts/audit_native_gallery.ts`. It measures
actual native primitive paint/backing, complete shafts and heads, visible body
silhouettes, canvas separation, label contrast, raw/mounted paint parity and
desktop/mobile gallery geometry. It preserves nine defect controls and three
positive controls, plus four measurement regressions for unrendered line fill,
paint occlusion, zero-area contact and a real narrow inset. All 16 pass.

The audit found and drove repairs for EBNF's full-canvas rectangle, ArchiMate
outer contours, shallow component and rounded mindmap contacts. It also found
the gallery's distorted mobile preview. Mounted SVGs now retain their viewBox
and paints, use uniform scaling, and fit within a definite preview frame.
Floating-point size classification uses a small geometry tolerance; contrast
and real inset thresholds remain unchanged.

The terminal `corrected-r3` audit passes with zero native findings, 54/54
raw/mounted paint signatures, 112/112 desktop/mobile aspect checks, and zero
load or overflow failures. All 16 controls pass. Its report SHA-256 is
`43a672187024528261d054c92f3e6be1aa283324db76070e14225b2f9af9cf2a`;
the asset-binding digest is
`b78c188360e1a08a49f3ba8b81ddf30a7e52b082e6a08bb9ab57b7996dc93c11`.
The local evidence retains 148 screenshots. Direct review includes SVG-capable
PNG exports and actual raster-only Ditaa, both palettes and viewport sizes.

Finite independent source review confirmed the comment/title/layout bypasses,
actual media preservation, optioned Ditaa delivery, and the four additional
ArchiMate layers. Actual rerenders after repair preserve native geometry,
labels and sources; the image control retains all 576 exact source-color pixels.
Both palettes' four additional layers have distinct configured solids, no
outlines, maximum-contrast black/white labels and derived PNG proof.

Bulky local reports, hashes, native comparisons and screenshots remain under
ignored `projects/plantuml-style-repair/artifacts/`. The strict isolated
runtime protocol and retained attempts are in
[style-repair-20261003](style-repair-20261003/summary.md). Its five initial
dispatches failed before model execution at the source authoring gate; they
remain recorded, and no runtime pass is claimed for them.

## Release outcome

The first sampled `final-r2` runtime cohort is rejected. Baseline passed strict
execution but failed Activity source/stop-ring contrast at its native contacts.
Boundary passed jointly. All three generalization runs had retained source/API
tool errors; fresh WBS stems also had low-contrast contacts, and one network's
requested name was substituted by a title. Final artifact recovery does not
erase those failures. All 34 deliveries were directly reviewed and all five
26-file runtime payloads remained immutable. The independent record retains
the five earlier pre-Pi dispatch failures and these five sampled attempts.

The next candidate clips ungrouped Activity contacts, hollow final-state rings
and short WBS stems with clearance for the target's stroke as well as the
connector. Headless tree stems receive the same visible contrast requirement.
The skill adds a compact native NWDIAG/Gantt reference for bare identifiers,
exact display descriptions and predecessor-end dependencies. The evaluator's
ordinary Bash/Python installed-tool preflight now verifies both CLI entry
points against the same native jar before dispatch.

Fresh `final-r3` runtime trials pass all five joint gates after the clean
`corrected-r4` gallery audit: one baseline, one boundary and exactly three
generalization attempts. Strict execution, independent artifacts, trace and
command audits, unchanged payloads, and direct visual/semantic review all pass.
All 34 SVG/PNG deliveries were reviewed. The minimum sampled text contrast is
5.4400:1 and connector contrast is 3.2835:1; Activity and WBS are 5.4898:1.
The 27-file payload SHA-256 is unchanged in every manifest/before/after proof:
`5f0988c9c6b6a035c5a75c82791b1cf1ed5cad703a808c4a0bc0dc94a27d3e5f`.
Generalization succeeds on its first renderer call in all three runs and
preserves the requested network names, hierarchy facts, dates, durations and
dependencies. All earlier failures remain retained. Publication still requires
exact-head Pages deployment and public resource verification.

The repaired `corrected-r4` gallery is now independently clean: all 548 visible
SVG labels use maximum-contrast black/white, with minimum ratio 4.58698.
Grouped shafts/heads have minimum 4.43944 and ungrouped connector primitives
minimum 3.10431. Raw/mounted parity is 54/54, desktop/mobile aspect checks are
112/112, all 16 controls pass, and no load/overflow failure remains. Complete
head-stroke contacts are clear except intentional semantic IE cardinality
attachments. Direct review covers all 56 native artifacts and their changed
mobile cards. Report SHA-256:
`5e2e169fd51e8c017bf5879f0dd35069e464488be1919a90e1d2316df4ea8717`.
Asset-binding digest:
`6f249f25c3ec9b272c8af8beb3212e6029f144d391bf8ed2ffc43e101a6939dc`.
The 148-screenshot manifest digest is
`33399980eb2c4a8a056f5a200de94b561f4c4a1f7183a55dba5d89dfa58228b3`.

Finite native rerendering of the retained failed Activity and WBS sources into
new artifacts also passes independently: complete painted shafts and heads
have zero contacts with bodies/hollow stop rings, and every measured backing
passes 3:1. Native body geometry and retained input hashes are unchanged.
The exact new NWDIAG/Gantt reference examples render successfully in SVG and
PNG with exact display names/addresses, 2/3/4-day spans and forward dependencies.
All eight fresh previews received direct review. No rejected evaluation
workspace was edited. The final 27-file candidate is frozen for `final-r3`.

## Publication verification

Source [`014fece01384f5e72bf00ce40f7c0d1d3ed80565`](https://github.com/gvillarroel/skills/commit/014fece01384f5e72bf00ce40f7c0d1d3ed80565)
is pushed to `main` and deployed by successful exact-head
[Pages run 37213408650](https://github.com/gvillarroel/skills/actions/runs/37213408650).
All Linux workflow steps pass. The first public audit finds no native visual
findings, passes 108/108 committed/native-to-live SVG paint comparisons,
224/224 combined local/public desktop/mobile aspect checks, and all 16 controls.
The owner directly reviews published Activity, WBS, Ditaa and ArchiMate cards
in both selected viewport/palette combinations.

Its exact public-byte gate is correctly rejected: 54 SVGs and two render
reports lack a final LF in the committed source; the established Pages builder
adds that LF. All 60 actual public resources match the local build exactly,
and every one of the 56 differences is precisely one added terminal LF.
The four already-canonical resources match Git bytes directly. This is a source
packaging mismatch, with no stale response or paint/geometry difference.
The bounded correction aligns only those gallery source assets with the
existing builder policy. The frozen 27-file runtime payload, themes, source
semantics, visual criteria and exact public equality remain unchanged.
Retain the rejected public audit and its byte diagnosis; rerun the unchanged
public gate against the corrected deployed commit before release completion.

The repaired 56 sources pass exact pre-repair-blob-plus-terminal-LF verification,
both native report validators and frozen fixture/family coverage. The local
packaged audit exits 0, with zero findings, 54/54 paint parity, 112/112 aspect
checks and all 16 controls. Repository gates and the 10,241-file canonical
local installation check also pass.
