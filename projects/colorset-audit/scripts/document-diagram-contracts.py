#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Install the audited local palette guidance in the six independent bundles."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
names=("mermaid","plantuml-colorset-renderer","echarts-animated-svg","slidev-echarts","slidev-animejs","slidev-quality-audit")
common='''# Colorset Output Contract

Select one palette for each authored visual output and record its name in the output or its report. Default to `colorset1`; use `colorset2` for an explicit full-color request or a documented need to distinguish several independent semantic categories. The full-color acceptance galleries deliberately use `colorset2` to demonstrate multiple category and animation mechanisms. A gallery containing both variants must identify each item's selected palette.

Read [the exact local palette contract](../assets/palettes/colorsets.json). Do not invent close grays, alternate blues, renderer defaults, or theme-derived tints. Use the selected allowlist for backgrounds, text, axes, borders, markers, highlights, controls, hover/focus, errors, legends, and exported assets. Colorset1 is red plus neutrals; reserve pink for an explicit need after readable neutral/red roles.

Inspect actual rendered marks, not just a theme configuration. Native renderer defaults, calculated color lightness/saturation, heatmap interpolation, and arbitrary overrides can introduce undeclared colors. Use discrete exact palette bins for numeric color scales while preserving data values and continuous position/size encodings. Use stepped changes between categorical animation colors; animate geometry and opacity smoothly. Tonal gradients may use exact endpoints in one role; do not interpolate categorical hues. Alpha, raster antialiasing, and compression are compositing effects rather than new authored base colors.

Preserve imported logos, photos, footage, and third-party source image pixels and provenance. Keep this source-media boundary narrow and explicit; all authored wrappers and labels still follow the selected palette. Source media is not permission to keep arbitrary authored chart colors. When editing source presentation is out of scope, report incompatible colors instead of claiming a palette pass.

Validate every output format and state the skill supports: source, static vector, animated vector, canvas, raster/export, gallery/deck chrome, controls, alternate states, and any downstream capture. Keep output paths, chart/diagram facts, relationships, stable IDs, labels, geometry, and accessibility metadata intact when repairing paint.
'''
specific={
"mermaid":"\nThe renderer normalizes actual generated SVG paint declarations to the source's selected colorset and checks the result before animation. Existing static SVG input must already fit one palette; the animator rejects incompatible paint rather than changing a read-only source. Style and check Mermaid source first. Generated static and animated files must match final paint and geometry.\n",
"plantuml-colorset-renderer":"\nThe renderer defaults to colorset1 and normalizes native SVG paint after all theme/source overrides. PNG-only Ditaa and standalone math bypass theme syntax but their raster output is quantized to the selected palette. Source-media PNGs retain their original pixels and report a preservation boundary; inspect their authored chrome through the matching normalized SVG. The report validator rejects undeclared SVG paints. A custom theme must also fit the selected colorset.\n",
"echarts-animated-svg":"\nCopy `assets/templates/echarts-colorsets.mjs` into a chart project when authoring options. Use `colorsetTheme(selected)` at ECharts initialization and `prepareColorsetOption(option, selected)` before `setOption`; use `normalizeSvgPaints(renderToSVGString(), selected)` for residual SVG renderer defaults. The animator rejects off-palette static input. Restyle editable ECharts options first so static and animated paint remain identical. The bundled bar smoke template uses colorset1; the 43-chart acceptance gallery deliberately uses colorset2.\n",
"slidev-echarts":"\nCopy `assets/templates/echarts-colorsets.mjs` into the deck. Initialize with `colorsetTheme(selected)` and call `prepareColorsetOption(option, selected)` before `setOption`. Validate both CanvasRenderer and SVGRenderer paths, chart labels/axes/legends/visualMap states, Slidev controls, and exported HTML. The acceptance deck deliberately uses colorset2 for its chart-category demonstrations. Source numeric data remains unchanged when continuous color maps become exact discrete bins.\n",
"slidev-animejs":"\nThe six runtime SVG templates deliberately use colorset2 to distinguish independent asset mechanisms. For a new red/neutral deck, replace every authored paint with the colorset1 roles before animating. Give categorical fill/background changes per-property `ease: 'steps(1)'`; retain smooth motion/opacity. Check all 21 feature paths, six generated SVG assets, controls, drag/scroll/click states, and exported HTML.\n",
"slidev-quality-audit":"\nRun with `--colorset colorset1` (default) or `--colorset colorset2` matching the deck's declared palette. The browser pass rejects off-palette computed DOM/SVG paints. Use `data-source-media` only on imported artwork itself. Canvas pixels include antialiasing; this DOM paint gate cannot prove hidden CanvasRenderer base paints or arbitrary CSS/pseudoelement states. Inspect ECharts options, settled and interactive renderer states, gradients, and canvas exports independently before claiming complete compliance. Audit reports are Markdown/JSON and need no visual palette; any authored visual report uses the selected colorset.\n",
}
for name in names:
    skill=ROOT / "skills" / name
    (skill / "references/colorset-contract.md").write_text(common+specific[name],encoding="utf-8",newline="\n")
    path=skill / "SKILL.md"
    text=path.read_text(encoding="utf-8")
    text=text.replace('Default to colorset2 unless the user asks for colorset1.', 'Default to colorset1; use colorset2 for an explicit full-color request or a documented semantic category need.')
    anchor='\n## '
    index=text.index(anchor,text.index('\n# '))
    text=text[:index]+ '\nRead [the colorset output contract](references/colorset-contract.md) before authoring or auditing visual output. Apply one exact bundled palette to every authored output path and inspect rendered paint. Default to colorset1; declare colorset2 when its category distinctions are needed.\n'+text[index:]
    path.write_text(text,encoding="utf-8",newline="\n")
    visual=skill / "references/visual-tokens.md"
    if visual.exists():
        text=visual.read_text(encoding="utf-8").replace('Use these tokens for D3 animated examples, replayable galleries, generated SVG assets, and standalone animation-focused artifacts.', 'Use these exact tokens for this skill’s authored visuals. Read [the colorset output contract](colorset-contract.md): colorset1 is the default red/neutral subset; the full-color roles below belong to colorset2 and require its declared selection.')
        visual.write_text(text,encoding="utf-8",newline="\n")
print('Updated six local contracts and runtime routes.')
