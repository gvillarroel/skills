#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply the bundled palette to authored HTML/SVG paint without changing geometry."""
from functools import wraps
import json
from pathlib import Path
import re

CONTRACT = Path(__file__).resolve().parents[1] / "assets" / "palettes" / "colorsets.json"
SOLID_RUNTIME = Path(__file__).resolve().parents[1] / "assets" / "templates" / "solid-style.js"
HEX = re.compile(r"(?<![\w-])#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-fA-F])\b")


def category_style(index, palette, canvas="#ffffff"):
    """Allocate every solid first, then a finite set of modest contrasting rims."""
    if not isinstance(index, int) or index < 0:
        raise ValueError("Category index must be a nonnegative integer")
    solids = [value for value in dict.fromkeys(palette["solidSequence"]) if value.lower() != canvas.lower()]
    if not solids:
        raise ValueError("The canvas leaves no category colors")
    fill = solids[index % len(solids)]
    style = dict(fill=fill, text=palette["textOnFill"][fill], stroke="none", strokeWidth=0, strokeDasharray=None, tier="solid", cue=None)
    variant = index // len(solids) - 1
    if variant < 0:
        return style
    def luminance(paint):
        channels = [int(paint[start:start + 2], 16) / 255 for start in (1, 3, 5)]
        return sum((value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4) * weight
                   for value, weight in zip(channels, (.2126, .7152, .0722)))
    level = luminance(fill)
    borders = [paint for paint in dict.fromkeys(palette["allowed"]) if paint != fill and
               (max(level, luminance(paint)) + .05) / (min(level, luminance(paint)) + .05) >= 3]
    if variant >= len(borders) * 9:
        return dict(style, tier="structural", cue="label-symbol-or-split")
    return dict(style, stroke=borders[variant % len(borders)], strokeWidth=1 + variant // (len(borders) * 3),
                strokeDasharray=(None, "6 4", "1 3")[(variant // len(borders)) % 3], tier="overflow")


def adapt_artifact(source, colorset="colorset1"):
    """Map authored paint only; source raster and vendor runtime bytes are immutable."""
    palettes = json.loads(CONTRACT.read_text(encoding="utf-8"))["colorsets"]
    if colorset not in palettes:
        raise ValueError("Select colorset1 or colorset2")
    allowed = palettes[colorset]["allowed"]
    immutable_vendor = []

    def protect_vendor(match):
        script = match.group(0)
        opening, _, body = script.partition(">")
        if (re.search(r'\bid\s*=\s*["\']d3-runtime["\']', opening, re.I)
                or re.search(r"https://d3js\.org\s+v\d", body[:512])):
            immutable_vendor.append(script)
            return f"__IMMUTABLE_D3_VENDOR_{len(immutable_vendor) - 1}__"
        return script

    source = re.sub(r"<script\b[^>]*>[\s\S]*?</script\s*>", protect_vendor, source, flags=re.I)
    # Distinct extended semantic roles become stable red/neutral roles in cs1.
    fallback = {"#007298": "#333e48", "#004d66": "#1c1c1c", "#00ace6": "#828282",
                "#e77204": "#9e1b32", "#994a00": "#6d1222", "#ff9633": "#e8002a",
                "#45842a": "#4f4f4f", "#294d19": "#363636", "#36b300": "#696969",
                "#652f6c": "#6d1222", "#431f47": "#1c1c1c", "#9e00b3": "#9e1b32",
                "#f1c319": "#9c9c9c", "#98700c": "#696969", "#ffd332": "#b5b5b5"}
    for value in ("#cdf3ff", "#ffe5cc", "#dbffcc", "#f9ccff", "#fff4cc", "#ffccd5"):
        fallback[value] = "#e7e7e7"

    def token(match):
        # Hex-looking IDs are geometry references, not authored color values.
        prefix = source[max(0, match.start() - 80):match.start()]
        suffix = source[match.end():match.end() + 30]
        if (re.search(r"url\(\s*$", prefix, re.I)
                or re.search(r"\b(?:xlink:)?href\s*=\s*[\"']$", prefix, re.I)
                or re.match(r"\s*\{", suffix)):
            return match.group(0)
        value = match.group(1).lower()
        value = "#" + ("".join(ch * 2 for ch in value) if len(value) == 3 else value)
        if colorset == "colorset1" and value in fallback:
            return fallback[value]
        if value in allowed:
            return value
        rgb = tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))
        return min(allowed, key=lambda candidate: sum((rgb[i] - int(candidate[1 + i * 2:3 + i * 2], 16)) ** 2 for i in range(3)))

    # These builders used decorative CSS drop shadows with arbitrary rgba
    # syntax. Removing the shadows leaves deterministic, readable flat paint.
    source = re.sub(r"filter:\s*drop-shadow\([^;]+;", "filter: none;", source)
    def alpha_paint(match):
        prop, red, green, blue, alpha = match.groups()
        base = "#" + ''.join(f'{int(channel):02x}' for channel in (red, green, blue))
        return f'{prop}: {base}; {prop}-opacity: {alpha};'
    source = re.sub(r"\b(fill|stroke):\s*rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([.\d]+)\s*\)\s*;", alpha_paint, source)
    source = HEX.sub(token, source)
    # Ordinary surfaces and controls use filled, borderless paint. Focus rings
    # remain transient keyboard affordances; open SVG curves remain geometry.
    source = re.sub(r"\bborder(?:-(?:top|right|bottom|left))?\s*:[^;}]+", "border: 0", source)
    # A generated standalone builder has one active contract across UI and SVG.
    source = re.sub(r'\bdata-(?:colorset|color-set)=["\'](?:base|colorset[12])["\']', '', source)
    source = re.sub(r"<body\b", f'<body data-colorset="{colorset}"', source, count=1)
    source = re.sub(r"<svg\b", f'<svg data-colorset="{colorset}"', source)
    if "</body>" in source:
        runtime = SOLID_RUNTIME.read_text(encoding="utf-8")
        contract = json.dumps({colorset: palettes[colorset]}, separators=(",", ":"))
        finalizer = f'<script>window.D3_SOLID_PALETTES={contract};\n{runtime}</script>'
        source = source.replace("</body>", finalizer + "\n</body>", 1)
    for index, script in enumerate(immutable_vendor):
        source = source.replace(f"__IMMUTABLE_D3_VENDOR_{index}__", script)
    return source


def colorset_output(function):
    """Keep builders callable while making colorset1 their actual output default."""
    @wraps(function)
    def generate(*args, colorset="colorset1", **kwargs):
        return adapt_artifact(function(*args, **kwargs), colorset)
    return generate


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Apply solid-first palette styling to a custom D3 HTML artifact before capturing its SVG.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.output.exists() and not args.force:
        parser.error("Output exists; pass --force to replace it")
    source = args.input.read_text(encoding="utf-8")
    if "</body>" not in source or "window.D3SolidStyle =" in source:
        parser.error("Supply an authored HTML body that has not already been finalized")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(adapt_artifact(source, args.colorset), encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(args.output), "colorset": args.colorset, "fillStyle": "solid-first"}))


if __name__ == "__main__":
    main()
