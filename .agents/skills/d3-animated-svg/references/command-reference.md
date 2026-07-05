# Command Reference

Use these commands only when the task needs the matching capture, contract, gallery, or maintenance validation path.

## Capture

Capture a D3-generated SVG from a local HTML page:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/render_d3_svg.py scene.html -o projects/<project-id>/artifacts/svgs/scene.svg --screenshot projects/<project-id>/artifacts/screenshots/scene.png --wait-ms 1800
```

Use a custom SVG selector:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/render_d3_svg.py scene.html --selector "svg#viz" -o projects/<project-id>/artifacts/svgs/scene.svg --wait-ms 2500
```

## Artifact Checks

Check that a generated HTML artifact is self-contained:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/check_self_contained_html.py artifact.html
```

Check an HTML artifact against explicit SVG IDs, metadata, and mark counts:

```powershell
node .agents/skills/d3-animated-svg/scripts/check_svg_contract.ts artifact.html svg-contract.json
```

Generate small/medium/large force-network or beeswarm variants from a JSON spec:

```powershell
node .agents/skills/d3-animated-svg/scripts/build_cardinality_variants.ts variants.json artifact.html
```

## Composition Audits

Audit SVG points against a dynamic-symmetry armature:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/audit_dynamic_symmetry.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg/index.html --selector "svg#asymmetric-task-overlap-saturated" --output projects/d3-animated-svg-validation/artifacts/data/asymmetric-task-overlap-saturated-dynamic-symmetry.json
```

Verify composition variant sheets expose curated SVG variants with stable composition IDs:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/verify_composition_sheets.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg/composition-sheets.html --min-variants 70 --expected-reviewed-patterns 220 --required-variant d3-composition-radial-rosette-force-network --expect-clean
```

Verify the colorset2 gallery version against `design/colorset2.yaml`:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/verify_colorset2_gallery.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg-colorset2/index.html --expected 224 --screenshot projects/d3-animated-svg-validation/artifacts/screenshots/gallery-colorset2.png --json-report projects/d3-animated-svg-validation/artifacts/data/gallery-colorset2.json --wait-ms 2200
```

Verify the CS1 gallery version against `design/colorset1.yml`:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/verify_style_gallery.py .agents/skills/d3-animated-svg/assets/examples/d3-animated-svg-cs1/index.html --palette-file design/colorset1.yml --style-version cs1 --color-set colorset1 --palette-name basic-red-neutral-style --pattern-id-suffix cs1 --expected 224 --screenshot projects/d3-animated-svg-validation/artifacts/screenshots/gallery-cs1.png --json-report projects/d3-animated-svg-validation/artifacts/data/gallery-cs1.json --wait-ms 2200
```

## Saturated Task Overlap

Generate the collision-audited saturated task-overlap label layout:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/layout_task_overlap_labels.py
```

Audit the saturated task-overlap labels, direct leader colors, and background fit in Chromium:

```powershell
uv run --script .agents/skills/d3-animated-svg/scripts/audit_saturated_task_overlap.py --expect-clean
```
