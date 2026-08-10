# Command Reference

Use these commands only when the task needs the matching capture, contract, gallery, or maintenance validation path.

## Capture

Capture a D3-generated SVG from a local HTML page:

```powershell
uv run --script skills/d3/scripts/render_d3_svg.py scene.html -o projects/<project-id>/artifacts/svgs/scene.svg --screenshot projects/<project-id>/artifacts/screenshots/scene.png --wait-ms 1800
```

Use a custom SVG selector:

```powershell
uv run --script skills/d3/scripts/render_d3_svg.py scene.html --selector "svg#viz" -o projects/<project-id>/artifacts/svgs/scene.svg --wait-ms 2500
```

## Dithering

Convert any settled SVG, HTML element, canvas, or image into a portable ordered-dither SVG:

```powershell
uv run --script skills/d3/scripts/dither_d3_output.py scene.html -o projects/<project-id>/artifacts/svgs/scene-dithered.svg --selector "svg#viz" --algorithm ordered --matrix-size 4 --cell-size 4 --palette "#000000,#ffffff" --preview-png projects/<project-id>/artifacts/screenshots/scene-dithered.png --json-report projects/<project-id>/artifacts/data/scene-dithered.json
```

Use `--algorithm floyd-steinberg` or `--algorithm atkinson` only for settled frames. For zoom/scale animation that must keep points attached to surface coordinates, use `assets/templates/surface-stable-fractal-dither.js` and validate its nested boundary:

```powershell
node -e "const d=require('./skills/d3/assets/templates/surface-stable-fractal-dither.js'); const r=d.validateZoomSequence(); console.log(JSON.stringify(r)); if(!r.ok) process.exit(1)"
```

## Artifact Checks

Check that a generated HTML artifact is self-contained:

```powershell
uv run --script skills/d3/scripts/check_self_contained_html.py artifact.html
```

Check an HTML artifact against explicit SVG IDs, metadata, and mark counts:

```powershell
node skills/d3/scripts/check_svg_contract.ts artifact.html svg-contract.json
```

Generate small/medium/large force-network or beeswarm variants from a JSON spec:

```powershell
node skills/d3/scripts/build_cardinality_variants.ts variants.json artifact.html
```

Build a deterministic offline Solar Terminator with a UTC-consistent NOAA astronomy tuple:

```powershell
uv run --script skills/d3/scripts/build_solar_terminator.py solar-terminator.html
uv run --script skills/d3/scripts/check_self_contained_html.py solar-terminator.html
```

## Composition Audits

Audit SVG points against a dynamic-symmetry armature:

```powershell
uv run --script skills/d3/scripts/audit_dynamic_symmetry.py skills/d3/assets/examples/d3-animated-svg/index.html --selector "svg#task-overlap-dense" --output projects/d3-animated-svg-validation/artifacts/data/task-overlap-dense-dynamic-symmetry.json
```

Verify composition variant sheets expose curated SVG variants with stable composition IDs:

```powershell
uv run --script skills/d3/scripts/verify_composition_sheets.py skills/d3/assets/examples/d3-animated-svg/composition-sheets.html --min-variants 70 --expected-reviewed-patterns 225 --required-variant d3-composition-radial-force-network --expect-clean
```

Verify the colorset2 gallery version against the bundled `assets/palettes/colorset2.yaml`:

```powershell
uv run --script skills/d3/scripts/verify_colorset2_gallery.py skills/d3/assets/examples/d3-animated-svg-colorset2/index.html --expected 225 --screenshot projects/d3-animated-svg-validation/artifacts/screenshots/gallery-colorset2.png --json-report projects/d3-animated-svg-validation/artifacts/data/gallery-colorset2.json --wait-ms 2200
```

Verify the CS1 gallery version against the bundled `assets/palettes/colorset1.yml`:

```powershell
uv run --script skills/d3/scripts/verify_style_gallery.py skills/d3/assets/examples/d3-animated-svg-cs1/index.html --palette-file skills/d3/assets/palettes/colorset1.yml --style-version cs1 --color-set colorset1 --palette-name basic-red-neutral-style --pattern-id-suffix cs1 --expected 225 --screenshot projects/d3-animated-svg-validation/artifacts/screenshots/gallery-cs1.png --json-report projects/d3-animated-svg-validation/artifacts/data/gallery-cs1.json --wait-ms 2200
```

## Full Gallery Visual Review

Capture every settled SVG as a labeled card, build contact sheets, and write per-pattern text-fit signals:

```powershell
uv run --script skills/d3/scripts/review_gallery_visuals.py skills/d3/assets/examples/d3-animated-svg/index.html --expected 225 --output-dir projects/d3-animated-svg-validation/artifacts/screenshots/gallery-review --json-report projects/d3-animated-svg-validation/artifacts/data/gallery-review.json --markdown-report projects/d3-animated-svg-validation/artifacts/reviews/gallery-review.md --expect-clean
```

Run the same command with `--viewport 390x900` and a separate output directory for mobile review. Treat overlap, overflow, and tiny-text counts as critique signals; inspect the labeled contact sheets before editing protected data geometry.

Validate release replay behavior across every card and confirm reference/index coverage:

```powershell
uv run --script skills/d3/scripts/verify_d3_gallery.py skills/d3/assets/examples/d3-animated-svg/index.html --expected 225 --replay-all --wait-ms 2200
uv run --script skills/d3/scripts/extract_gallery_pattern_references.py --check-only --expected 225
```

## Saturated Task Overlap

Generate the collision-audited saturated task-overlap label layout:

```powershell
uv run --script skills/d3/scripts/layout_task_overlap_labels.py
```

Audit the saturated task-overlap labels, direct leader colors, and background fit in Chromium:

```powershell
uv run --script skills/d3/scripts/audit_saturated_task_overlap.py --expect-clean
```
