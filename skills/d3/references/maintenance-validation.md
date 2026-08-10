# Maintenance Validation

Read this file before changing this skill, its pattern references, scripts, examples, palettes, logo engine, gallery, or composition sheets.

The unified `d3` bundle owns the former animation, composition-evaluation,
composition-recomposition, and logo-design surfaces. Do not create a sibling
D3 skill to change one of those routes; keep progressive detail in this
bundle's references and scripts.

## Pattern Promotion

When a gallery card or standalone SVG pattern proves reusable during skill maintenance, update the owning reference before finishing.

Capture:

- stable `d3-*` ID
- trigger context
- data contract
- geometry contract
- animation contract
- semantic color roles
- validation hooks
- isolated-workspace caveats

For patterns expected to work in isolated skill-only workspaces, include a minimal standalone implementation recipe that does not depend on reading the gallery source.

## Baseline Validation

After changing this skill, references, scripts, or examples, run:

```powershell
uv run --script skills/d3/scripts/test_palette_contract.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
```

When changing the capture script or example fixture, also run the relevant smoke command from `references/command-reference.md` and inspect the generated screenshot.

## Gallery Changes

When changing the examples gallery, read `references/gallery-patterns.md` and run the gallery verifier documented there.

Verify that:

- all cards render
- each card has exactly one replay control
- release replay checks restart every target card in isolation; sampled replay remains acceptable for a fast smoke check
- repeated replay does not duplicate marks or listeners
- desktop and mobile screenshots keep text and controls readable

For large galleries, create contact sheets and run an explicit visual critique pass by example or batch before final validation. Integrate the critique centrally when possible: shared token ramps, label halos, axis/grid contrast, and replay-safe post-render polish should handle recurring issues before adding one-off chart fixes.

Generate the full settled-frame review with `scripts/review_gallery_visuals.py` for desktop and mobile viewports. Keep its cards, contact sheets, JSON, and Markdown reports under `projects/<project-id>/artifacts/`; do not commit generated review media.

Before release, validate reference and index coverage with `uv run --script skills/d3/scripts/extract_gallery_pattern_references.py --check-only --expected 225`.

## Composition Sheet Changes

When changing the composition sheets, run `scripts/verify_composition_sheets.py`.

Confirm that:

- every current gallery pattern is reviewed
- every curated variant has an inline SVG preview plus stable `data-composition-id`, `data-example-id`, `data-pattern-id`, `data-composition-pattern-id`, `data-armature-lines`, `data-quadrants`, and `data-reviewed` attributes
- each SVG includes a semantic `.source-pattern-recomposition` group plus a metadata-only source-pattern signature
- each card exposes one replay control and animates visible source-derived marks inside the SVG on load and replay without duplicating nodes or rebuilding unrelated cards
- visible composition guide lines, quadrant overlays, source-field borders, signature boxes, or direction cues are absent unless they are source-derived marks, route paths, process links, label leaders, or another narrative element

Keep only variants that work well for the selected composition. Do not restore fit classes such as `support` tiers or duplicate every pattern into every sheet.

## Palette Changes

Keep `assets/palettes/colorsets.json`, `assets/palettes/colorset1.yml`, and
`assets/palettes/colorset2.yaml` in exact token parity. Colorset1 remains the
runtime default; colorset2 remains opt-in extended color. Run the palette unit
tests, a positive colorset1 artifact, a negative colorset1 artifact containing
a colorset2-only token, and a colorset2 artifact with `--require-extended`.

For JavaScript-rendered work, do not accept static token presence alone. Render
the artifact and inspect computed visible SVG paint. Embedded palette JSON or
unused CSS is not evidence.

## Logo and Texture Changes

Keep the pattern, texture, and composition inventories synchronized across the
manifest, engine, templates, and validators. Run `validate_logo_artifact.py`,
`validate_texture_gallery.py`, and both browser verifiers at desktop and mobile
sizes. Inspect the 96 px logo state and text-clearance findings.

## Release

When source paths or published examples change, rebuild Pages. Before marking
the skill done, run the repository payload check, Pi harness tests, an isolated
runtime forward test, and the declared Harbor development/validation/final-
holdout protocol. Freeze the selected bundle before releasing holdout; never
use holdout output to revise the score or continue evolution.
