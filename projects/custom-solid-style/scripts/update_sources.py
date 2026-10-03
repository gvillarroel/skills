#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Integrate solid paint defaults into the owned visual bundle routes."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
contract = json.loads((ROOT / "skills/d3/assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]


def edit(relative, operation):
    path = ROOT / relative
    old = path.read_text(encoding="utf-8")
    new = operation(old)
    if new != old:
        path.write_text(new, encoding="utf-8", newline="\n")


def flat_css(source):
    return re.sub(r"\bborder(?:-(?:top|right|bottom|left))?\s*:[^;}]+", "border: 0", source)


# Keep the published D3 helper in the copied example tree; Pages intentionally
# excludes runtime templates. The equality is checked by the independent audit.
runtime = (ROOT / "skills/d3/assets/templates/solid-style.js").read_text(encoding="utf-8")
(ROOT / "skills/d3/assets/examples/d3-animated-svg/solid-style.js").write_text(runtime, encoding="utf-8", newline="\n")
palette_js = "window.D3_SOLID_PALETTES=" + json.dumps(contract, separators=(",", ":")) + ";\n"
for relative in ["skills/d3/assets/examples/d3-animated-svg/index.html", "skills/d3/assets/examples/d3-animated-svg/composition-sheets.html", "skills/d3/assets/examples/d3-animated-svg-cs1/index.html", "skills/d3/assets/examples/d3-animated-svg-colorset2/index.html"]:
    helper = "./solid-style.js" if "/d3-animated-svg/" in relative else "../d3-animated-svg/solid-style.js"
    edit(relative, lambda source, helper=helper: source if "D3_SOLID_PALETTES=" in source else source.replace("</body>", f"<script>{palette_js}</script>\n<script src=\"{helper}\"></script>\n</body>"))
edit("skills/d3/assets/examples/d3-animated-svg/gallery-page.css", flat_css)
edit("skills/d3/scripts/create_d3_svg_starter.py", flat_css)


def three_template(source):
    source = flat_css(source)
    source = source.replace("background: #ffffff;\n        color: var(--neutral);\n        border-radius: 6px;", "background: #9e1b32;\n        color: #ffffff;\n        border-radius: 6px;")
    source = source.replace("button:hover {\n        background: var(--gray-100);", "button:hover {\n        background: #6d1222;")
    source = source.replace("color: var(--neutral);", "color: #000000;")
    source = source.replace("      const tokenColors = colorset === \"colorset2\"\n        ? [palette.blue, palette.green, palette.orange, palette.yellow, palette.purple]\n        : [palette.neutral, palette.gray700, palette.gray500, palette.dark, palette.gray200];", "      const bundledPalettes = __PALETTES__;\n      const tokenColors = bundledPalettes[colorset].solidSequence\n        .filter(value => value !== '#ffffff' && value !== '#9e1b32')\n        .map(value => Number.parseInt(value.slice(1), 16));")
    source = source.replace("          materialColors:", "          fillStyle: 'solid-first',\n          decorativeOutlineCount: 0,\n          materialColors:")
    return source


edit("skills/threejs-animated-3d/assets/templates/self-contained-token-orbit.html", three_template)
edit("skills/threejs-animated-3d/scripts/build_standalone_threejs.py", lambda source: source.replace('html = html.replace("__TOKEN_COUNT__", str(token_count))', 'html = html.replace("__TOKEN_COUNT__", str(token_count))\n    palette_contract = json.loads((SKILL_ROOT / "assets/palettes/colorsets.json").read_text(encoding="utf-8"))\n    html = html.replace("__PALETTES__", json.dumps(palette_contract["colorsets"], separators=(",", ":")))'))


def three_gallery(source):
    source = re.sub(r"\n  const edges = new THREE.LineSegments\([\s\S]*?\n  cubeGroup.add\(edges\)\n", "\n  // Filled mesh faces carry identity without a decorative edge overlay.\n", source, count=1)
    source = re.sub(r"\n    const edge = new THREE.LineSegments\([\s\S]*?\n    bar.add\(edge\)\n", "\n    // Keep towers as uninterrupted filled materials.\n", source, count=1)
    source = source.replace("material and edge-lighting sanity check", "material and lighting sanity check")
    return source


edit("skills/threejs-animated-3d/assets/examples/threejs-animated-3d/src/main.js", three_gallery)
edit("skills/threejs-animated-3d/assets/examples/threejs-animated-3d/src/styles.css", lambda source: flat_css(source).replace("--ink: #333e48;", "--ink: #000000;").replace("--muted: #696969;", "--muted: #000000;").replace("background: var(--white);\n  color: var(--ink);\n  cursor: pointer;", "background: var(--brand-primary);\n  color: #ffffff;\n  cursor: pointer;").replace("background: var(--blue-highlight);\n  color: var(--blue-hover);", "background: var(--blue);\n  color: #ffffff;").replace("box-shadow: inset 0 0 0 2px rgba(0, 114, 152, .24);", "box-shadow: none;"))
edit("skills/procedural-svg-animation/scripts/build_procedural_gallery.py", flat_css)
edit("skills/vectorize-art-patterns/scripts/build_example_gallery.py", flat_css)


guidance = """

## Solid fill priority

Use opaque, single-token filled marks without decorative borders first. Read
`solidSequence` and `textOnFill` from `assets/palettes/colorsets.json`. Reuse a
fill for the same semantic role; when roles must be distinct, exhaust every
usable distinct token in the preferred sequence, excluding the actual canvas,
before creating outline or tint combinations. Soft tokens occur late. For text
on a fill, use exactly black or white with the larger WCAG contrast computed
from the actual background; composite opacity before evaluating translucent
backgrounds. Do not infer text color from a hue name.

Keep connectors, axes, signal traces, open line art, physical geometry and
explicit source-fidelity modes. A stroke that depicts a relationship or is the
geometry itself is meaningful. Reserve decorative outlines for a documented
palette overflow or an explicit requested style; mark SVG overflow treatments
with `data-outline-tier="overflow"`. A transient keyboard focus ring remains an
interaction affordance. Use position, whitespace and direct labels for ordinary
selection and grouping.
"""
for skill in ("d3", "threejs-animated-3d", "procedural-svg-animation", "svg-brief-design", "vectorize-art-patterns"):
    edit(f"skills/{skill}/SKILL.md", lambda source: source if "## Solid fill priority" in source else source.rstrip() + guidance + "\n")

edit("skills/threejs-animated-3d/references/visual-tokens.md", lambda source: source.replace("position, texture, outline, and direct labels before adding another hue.", "position, texture, and direct labels before adding another hue. Keep filled\nmeshes free of decorative `EdgesGeometry`, wireframes, or silhouette overlays.").replace("Use white or gray surfaces with an opaque red outline for selection.", "Use a solid red material, position, motion or a direct label for selection.\nAn outline is a documented overflow option after the full usable solid palette.").replace("- Use dark text on light surfaces and white text on dark/red surfaces.", "- Use the bundled `textOnFill` mapping: choose exactly black or white by maximum\n  WCAG contrast against the actual material swatch or HTML surface.").replace("- Pair interaction states with labels, outlines, or shape changes.", "- Pair interaction states with labels, solid fills, or shape changes."))
edit("skills/threejs-animated-3d/references/scene-patterns.md", lambda source: source.replace("Cycle existing role colors; do not introduce pink or new hues just because the object count exceeds the palette length.", "Reuse fills for the same semantic role. For unique roles use the complete\n  bundled `solidSequence` before any optional outline variant; exclude the actual\n  canvas and any color already reserved for another distinct role.").replace("- Use `MeshStandardMaterial` with ambient and directional lights for most scenes.", "- Use `MeshStandardMaterial` with ambient and directional lights for most scenes.\n- Keep filled meshes free of decorative edge geometry and default wireframes.\n  Relationship lines, trajectories and scientific line geometry remain visible."))
edit("skills/vectorize-art-patterns/references/colorset-adaptation.md", lambda source: source.replace("- Apply the active contract to background, paths, and outlines.", "- Apply the active contract to background and paths. Keep `--outline 0` for\n  ordinary filled derivatives; outlines require a requested source style or a\n  documented palette overflow after usable unique solid tokens are exhausted."))
edit("skills/d3/references/user-artifact-workflow.md", lambda source: source + "\nThe starter ships `solid-style.js` and its exact bundled palette contract. Keep\nthis runtime file with the editable artifact: it removes decorative outlines,\nuses a solid role fill for light nodes with dark borders, and computes contained\nblack/white label contrast. For new categorical roles call\n`D3SolidStyle.categoryStyle(index, colorset, actualCanvas)`; its initial tier\nexhausts all usable solid tokens before any border variant. Preserve genuine\nline geometry and use explicit `data-paint-mode` for source or line-art modes.\n")

edit("skills/procedural-svg-animation/scripts/build_procedural_svg.py", lambda source: source.replace("DEFAULT_BUILD_OPTIONS: dict[str, object] = {", "_PAINT_CONTRACT = json.loads((SKILL_ROOT / 'assets/palettes/colorsets.json').read_text(encoding='utf-8'))['colorsets']\nfor _colorset, _paint in PALETTES.items():\n    _paint['accents'] = [value for value in _PAINT_CONTRACT[_colorset]['solidSequence'] if value != _paint['surface']]\n\nDEFAULT_BUILD_OPTIONS: dict[str, object] = {"))
print("Updated five independently bundled solid-paint routes and published sources.")
