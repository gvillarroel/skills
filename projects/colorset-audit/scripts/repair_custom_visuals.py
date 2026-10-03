#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply targeted palette repairs to the five audited canonical bundles."""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "skills/hyperframes-explainer/assets/palettes/colorsets.json"
palette = json.loads(BASE.read_text())
allowed = palette["colorsets"]["colorset2"]["allowed"]
changed = []


def update(path, transform):
    path = ROOT / path
    original = path.read_text(encoding="utf-8")
    result = transform(original)
    if original != result:
        path.write_text(result, encoding="utf-8", newline="\n")
        changed.append(path.relative_to(ROOT).as_posix())


def nearest(value):
    rgb = tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))
    return min(allowed, key=lambda c: sum((rgb[i] - int(c[1+i*2:3+i*2], 16))**2 for i in range(3)))


def canonical_literals(text):
    return re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: m[0].lower() if m[0].lower() in allowed else nearest(m[0]), text)


for skill in ("procedural-svg-animation", "svg-brief-design", "threejs-animated-3d"):
    target = ROOT / "skills" / skill / "assets/palettes/colorsets.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        target.write_bytes(BASE.read_bytes())
        changed.append(target.relative_to(ROOT).as_posix())

# Small named builders must enforce the same contract as the common builder.
for path in (ROOT / "skills/d3/scripts").glob("build*.py"):
    text = path.read_text()
    if "--colorset" in text:
        continue
    primary = "build_html" if "def build_html(" in text else "html_document" if "def html_document(" in text else None
    if primary is None:
        continue
    def repair(text, primary=primary):
        if "from colorset_adapter import colorset_output" not in text:
            text = text.replace("from pathlib import Path", "from pathlib import Path\nfrom colorset_adapter import colorset_output", 1)
            text = text.replace("def " + primary + "(", "@colorset_output\ndef " + primary + "(", 1)
        if '--colorset' not in text:
            text = re.sub(r'(    parser.add_argument\("output"[^\n]+\n)', r'\1    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")\n', text, count=1)
        text = text.replace(primary + "()", primary + "(colorset=args.colorset)")
        text = text.replace("build_html(args.timestamp)", "build_html(args.timestamp, colorset=args.colorset)")
        return canonical_literals(text)
    update(path.relative_to(ROOT), repair)

for path in (ROOT / "skills/d3/references").rglob("*.md"):
    update(path.relative_to(ROOT), canonical_literals)
update("skills/d3/scripts/build_cardinality_variants.ts", canonical_literals)
update("skills/d3/assets/examples/d3/index.html", canonical_literals)

# The original gallery uses many categorical roles; retain it as cs2, enforce
# the palette for the base as well as the two published styled variants.
update("skills/d3/assets/examples/d3-animated-svg/gallery.js", lambda t: t
    .replace('(galleryStyleVersion === "colorset2" ? "colorset2" : "base")', '(galleryStyleVersion === "cs1" ? "colorset1" : "colorset2")')
    .replace('(galleryStyleVersion === "colorset2" ? "full-color-style" : "base")', '(galleryStyleVersion === "cs1" ? "basic-red-neutral-style" : "full-color-style")')
    .replace('remapTokenColor(current, isStyledGallery)', 'remapTokenColor(current, true)')
    .replace('if (isStyledGallery) {\n        const styleText', 'if (true) {\n        const styleText'))

# Keep dark catalog structure but replace the unrelated neon identity with
# exact red/neutral paint. All SVG patterns inherit the requested contract.
night = {
    '#f7f8fc':'#f7f7f7', '#aeb8c8':'#b5b5b5', '#f6f2e9':'#f7f7f7',
    '#18202a':'#1c1c1c', '#596473':'#696969', '#08101a':'#1c1c1c',
    '#111c29':'#363636', '#7ee7dc':'#e8002a', '#ffbf69':'#9e1b32',
    '#fff27a':'#e8002a', '#071019':'#000000', '#0b1521':'#1c1c1c',
    '#101b28':'#363636', '#14202d':'#363636', '#173b35':'#4f4f4f',
    '#283845':'#333e48', '#31586c':'#4f4f4f', '#475362':'#4f4f4f',
    '#75d59a':'#cfcfcf', '#77d5ff':'#cfcfcf', '#8cb8ff':'#828282',
    '#a8fff5':'#e7e7e7', '#a9ef8e':'#cfcfcf', '#c8a7ff':'#b5b5b5',
    '#d3a6ff':'#b5b5b5', '#e8f2ff':'#f7f7f7', '#f7dd72':'#9c9c9c',
    '#ff8fb8':'#e8002a', '#ff9776':'#9e1b32',
}
def gallery_css(text):
    for before, after in night.items(): text = text.replace(before, after)
    # Opacity is retained while the RGB base comes from a canonical token.
    def rgba(m):
        rgb = tuple(int(m[i]) for i in (1,2,3)); alpha=m[4]
        raw = '#' + ''.join(f'{v:02x}' for v in rgb)
        target = night.get(raw, raw if raw in allowed else nearest(raw))
        rgb = [int(target[i:i+2],16) for i in (1,3,5)]
        return f'rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})'
    text = re.sub(r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([.\d]+)\s*\)',rgba,text)
    return text.replace('default="colorset2"','default="colorset1"').replace('<body data-example-id=', '<body data-colorset="{palette}" data-example-id=')
update("skills/procedural-svg-animation/scripts/build_procedural_gallery.py", gallery_css)
update("skills/procedural-svg-animation/scripts/build_procedural_svg.py", lambda t: t.replace('#9f9f9f','#9c9c9c').replace('"highlight": "#ffccd5"','"highlight": "#e7e7e7"').replace('"palette": "colorset2"','"palette": "colorset1"'))
update("skills/procedural-svg-animation/assets/templates/pattern-config.json", lambda t: t.replace('"colorset2"','"colorset1"'))

# Avoid authored interpolated vertex hues and global colored lighting.
update("skills/threejs-animated-3d/assets/examples/threejs-animated-3d/src/main.js", lambda t: t
    .replace('new THREE.DirectionalLight(TOKEN_HEX.blue,', 'new THREE.DirectionalLight(TOKEN_HEX.white,')
    .replace('new THREE.PointLight(TOKEN_HEX.yellow,', 'new THREE.PointLight(TOKEN_HEX.white,')
    .replace('mixed.lerpColors(colorA, colorB, normalized < 0.5 ? normalized * 2 : (normalized - 0.5) * 2)', 'mixed.copy(COLOR_OBJECTS[["blue", "green", "yellow", "red"][Math.min(3, Math.floor(normalized * 4))]])'))
update("skills/threejs-animated-3d/assets/examples/threejs-animated-3d/index.html", lambda t: t.replace('<body data-example-id=', '<body data-colorset="colorset2" data-example-id='))

# Tracing quantizes source colors internally; all derivative SVG output is
# adapted by default. Source images and source-color provenance stay intact.
update("skills/vectorize-art-patterns/scripts/vectorize_art.py", lambda t: t.replace('choices=COLORSET_NAMES,\n', 'choices=COLORSET_NAMES,\n        default="colorset1",\n'))
update("skills/vectorize-art-patterns/scripts/vectorize_with_vtracer.py", lambda t: t.replace('choices=("colorset1", "colorset2"), required=True', 'choices=("colorset1", "colorset2"), default="colorset1"'))
update("skills/vectorize-art-patterns/scripts/validate_art_svg.py", lambda t: t.replace('colorset not in {"source", "colorset1", "colorset2"}', 'colorset not in {"colorset1", "colorset2"}').replace('choices=("source", "colorset1", "colorset2")', 'choices=("colorset1", "colorset2")'))
update("skills/vectorize-art-patterns/scripts/test_vectorize_art.py", lambda t: t.replace('colorset or "source",', 'colorset or "colorset1",'))

output = ROOT / 'projects/colorset-audit/artifacts/data/custom-repair-paths.json'
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(changed,indent=2)+'\n')
print(json.dumps({'changedPaths':len(changed),'inventory':str(output)}))
