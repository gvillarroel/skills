#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare source-derived SVG recreation templates for isolated pi runs."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from colorset_adapter import adapt_artifact
from check_palette_contract import FUNCTIONAL_COLOR_RE, PAINT_VALUE_RE, ALLOWED_NON_COLOR_VALUES, static_surface


WORD_BANK = [
    "Atlas",
    "Beacon",
    "Cinder",
    "Delta",
    "Echo",
    "Flux",
    "Harbor",
    "Ion",
    "Juno",
    "Kite",
    "Lumen",
    "Mica",
    "Nova",
    "Orbit",
    "Pulse",
    "Quill",
    "Relay",
    "Sol",
    "Tess",
    "Vale",
    "Wave",
    "Xenon",
    "Yara",
    "Zen",
]

MONTHS = {
    "jan": "Apr",
    "feb": "May",
    "mar": "Jun",
    "apr": "Jul",
    "may": "Aug",
    "jun": "Sep",
    "jul": "Oct",
    "aug": "Nov",
    "sep": "Dec",
    "oct": "Jan",
    "nov": "Feb",
    "dec": "Mar",
    "january": "April",
    "february": "May",
    "march": "June",
    "april": "July",
    "june": "September",
    "july": "October",
    "august": "November",
    "september": "December",
    "october": "January",
    "november": "February",
    "december": "March",
}

DIGIT_RE = re.compile(r"\d")
TEXT_TAGS = {"text", "tspan", "title", "desc"}


def load_compare_module():
    script = Path(__file__).resolve().with_name("compare_svg_style_signatures.py")
    spec = importlib.util.spec_from_file_location("compare_svg_style_signatures", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {script}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def register_default_namespace(root: ET.Element) -> None:
    if root.tag.startswith("{"):
        namespace = root.tag.split("}", 1)[0][1:]
        ET.register_namespace("", namespace)


def preserve_case(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement.lower()


def shift_digits(text: str) -> str:
    return DIGIT_RE.sub(lambda match: str((int(match.group(0)) + 3) % 10), text)


def closest_word(index: int, target_len: int) -> str:
    rotated = WORD_BANK[index % len(WORD_BANK) :] + WORD_BANK[: index % len(WORD_BANK)]
    return min(rotated, key=lambda word: (abs(len(word) - target_len), len(word)))


def synthetic_token(token: str, index: int) -> str:
    lower = token.lower()
    if lower in MONTHS:
        return preserve_case(token, MONTHS[lower])
    if DIGIT_RE.search(token):
        return shift_digits(token)
    letters = re.findall(r"[A-Za-z]+", token)
    if not letters:
        return token
    replacement = closest_word(index, len(letters[0]))
    return preserve_case(letters[0], token.replace(letters[0], replacement, 1))


def synthetic_text(text: str, index: int) -> str:
    stripped = text.strip()
    if not stripped:
        return text
    if DIGIT_RE.search(stripped) and not re.search(r"[A-Za-z]", stripped):
        changed = shift_digits(stripped)
    else:
        parts = re.split(r"(\s+)", stripped)
        word_index = 0
        changed_parts = []
        for part in parts:
            if part.isspace() or not part:
                changed_parts.append(part)
                continue
            changed_parts.append(synthetic_token(part, index + word_index))
            word_index += 1
        changed = "".join(changed_parts)
    prefix = text[: len(text) - len(text.lstrip())]
    suffix = text[len(text.rstrip()) :]
    return prefix + changed + suffix


def mutate_text_nodes(root: ET.Element) -> list[dict]:
    replacements: list[dict] = []
    text_index = 1
    for node in root.iter():
        tag = local_name(node.tag)
        if tag not in TEXT_TAGS:
            continue
        original = node.text or ""
        if not original.strip():
            continue
        replacement = synthetic_text(original, text_index)
        if replacement == original:
            replacement = f"{original.strip()} {text_index}"
        node.set("data-template-text-id", f"text-{text_index:03d}")
        node.set("data-source-text", original.strip())
        node.text = replacement
        replacements.append(
            {
                "id": f"text-{text_index:03d}",
                "tag": tag,
                "sourceText": original.strip(),
                "seedText": replacement.strip(),
            }
        )
        text_index += 1
    return replacements


def write_inventory(path: Path, source: Path, signature: dict, replacements: list[dict]) -> None:
    render_counts = signature.get("renderTagCounts", {})
    animation_counts = signature.get("animationCounts", {})
    colors = signature.get("colors", {})
    font_sizes = signature.get("fontSizes", {})
    stroke_widths = signature.get("strokeWidths", {})
    opacities = signature.get("opacities", {})
    lines = [
        f"# SVG Recreation Template: {source.name}",
        "",
        "Use the seeded SVG as the base. Change labels and values only where data must differ.",
        "Do not remove dense marks, sketchy overlays, calendar cells, stippling points, paths, or animation nodes.",
        "",
        "## Required Signature",
        "",
        f"- viewBox: `{signature.get('viewbox')}`",
        f"- root font family: `{signature.get('rootFontFamily')}`",
        f"- render tag counts: `{json.dumps(render_counts, sort_keys=True)}`",
        f"- animation counts: `{json.dumps(animation_counts, sort_keys=True)}`",
        f"- font sizes: `{json.dumps(font_sizes, sort_keys=True)}`",
        f"- stroke widths: `{json.dumps(stroke_widths, sort_keys=True)}`",
        f"- opacity bins: `{json.dumps(opacities, sort_keys=True)}`",
        f"- color set: `{', '.join(sorted(colors))}`",
        "",
        "## Seed Text Replacements",
        "",
    ]
    if replacements:
        for item in replacements:
            lines.append(f"- `{item['id']}` `{item['tag']}`: `{item['sourceText']}` -> `{item['seedText']}`")
    else:
        lines.append("- No text nodes found; preserve geometry and style signature.")
    lines.extend(
        [
            "",
            "## Editing Rules",
            "",
            "- Keep the seeded SVG's element counts and animation nodes unless the source itself is sparse.",
            "- Keep all colors, stroke widths, opacity values, dash arrays, and font-size bins from the seed.",
            "- If you need a different topic, change text values to similarly sized labels instead of changing geometry.",
            "- Write the final candidate to the matching file under `expected/`.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_html_template(path: Path, svg_text: str, signature_file: str, colorset: str) -> None:
    runtime_path = Path(__file__).resolve().parents[1] / "assets/vendor/d3.v7.9.0.min.js"
    runtime = runtime_path.read_text(encoding="utf-8").replace("</script", "<\\/script")
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SVG recreation template</title>
  <script>{runtime}</script>
  <style>body {{ margin: 0; font-family: Open Sans, Arial, sans-serif; }}</style>
</head>
<body data-colorset="{colorset}" style="background:#f7f7f7;color:#333e48">
  <div id="stage"></div>
  <script type="module">
    // Edit the seeded SVG/data comments, not the rendering structure. Signature: {signature_file}
    const seededSvgMarkup = {json.dumps(svg_text)};
    const documentSvg = new DOMParser().parseFromString(seededSvgMarkup, "image/svg+xml").documentElement;
    d3.select("#stage").node().appendChild(document.importNode(documentSvg, true));
  </script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def prepare_one(source: Path, template_dir: Path, expected_dir: Path, compare_module, overwrite_expected: bool, colorset: str = "colorset1") -> dict:
    source_signature = compare_module.build_signature(source).to_jsonable()
    root = ET.parse(source).getroot()
    register_default_namespace(root)
    root.set("font-family", root.get("font-family") or source_signature.get("rootFontFamily") or "Open Sans, Arial, sans-serif")
    replacements = mutate_text_nodes(root)
    seed_text = ET.tostring(root, encoding="unicode")
    if not seed_text.lstrip().startswith("<svg"):
        seed_text = seed_text[seed_text.find("<svg") :]
    seed_text = adapt_artifact(seed_text, colorset)
    # Unsupported paint must be normalized explicitly instead of leaking into
    # an authored reconstruction. The source file itself remains immutable.
    visible_seed, _ = static_surface(Path("seed.svg"), seed_text)
    named = {match[1] for match in PAINT_VALUE_RE.finditer(visible_seed)
             if match[1].lower() not in ALLOWED_NON_COLOR_VALUES}
    if FUNCTIONAL_COLOR_RE.search(visible_seed) or named:
        raise ValueError("Normalize source named/functional paint to hex before preparing a colorset reconstruction")

    stem = source.stem
    template_dir.mkdir(parents=True, exist_ok=True)
    expected_dir.mkdir(parents=True, exist_ok=True)
    seed_path = template_dir / f"{stem}.seed.svg"
    signature_path = template_dir / f"{stem}.signature.json"
    source_signature_path = template_dir / f"{stem}.source-signature.json"
    inventory_path = template_dir / f"{stem}.inventory.md"
    html_path = template_dir / f"{stem}.template.html"
    expected_path = expected_dir / source.name

    seed_path.write_text(seed_text, encoding="utf-8")
    signature = compare_module.build_signature(seed_path).to_jsonable()
    signature_path.write_text(json.dumps(signature, indent=2, sort_keys=True), encoding="utf-8")
    source_signature_path.write_text(json.dumps(source_signature, indent=2, sort_keys=True), encoding="utf-8")
    write_inventory(inventory_path, source, signature, replacements)
    write_html_template(html_path, seed_text, signature_path.name, colorset)
    if overwrite_expected or not expected_path.exists():
        shutil.copy2(seed_path, expected_path)

    return {
        "source": str(source),
        "expected": str(expected_path),
        "seed": str(seed_path),
        "signature": str(signature_path),
        "sourceSignature": str(source_signature_path),
        "colorset": colorset,
        "inventory": str(inventory_path),
        "templateHtml": str(html_path),
        "textReplacementCount": len(replacements),
        "renderTagCounts": signature.get("renderTagCounts", {}),
        "animationCounts": signature.get("animationCounts", {}),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", type=Path)
    parser.add_argument("--template-dir", type=Path, required=True)
    parser.add_argument("--expected-dir", type=Path, required=True)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--no-overwrite-expected", action="store_true")
    parser.add_argument("--colorset", choices=("colorset1", "colorset2"), default="colorset1")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    compare_module = load_compare_module()
    records = [
        prepare_one(
            source.resolve(),
            args.template_dir.resolve(),
            args.expected_dir.resolve(),
            compare_module,
            overwrite_expected=not args.no_overwrite_expected,
            colorset=args.colorset,
        )
        for source in args.sources
    ]
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps({"templates": records}, indent=2), encoding="utf-8")
    print(f"Prepared templates: {len(records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
