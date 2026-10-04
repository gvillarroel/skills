#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check canonical token copies, output inventory and authored artifact paints."""
from __future__ import annotations
import argparse
import colorsys
import json
import re
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CS1_CATEGORY_ORDER = [
    "#9e1b32",
    "#333e48", "#4f4f4f", "#696969", "#828282", "#9c9c9c",
    "#b5b5b5", "#cfcfcf", "#e7e7e7", "#363636", "#f7f7f7",
    "#1c1c1c", "#000000", "#ffffff",
    "#6d1222", "#e8002a", "#ffccd5",
]
CS1_CATEGORY_PRIORITY = ["primary-red", "grays", "black", "white", "remaining-colors"]
HEX = re.compile(r"(?<![\w-])#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})(?![\w-])")
RGB = re.compile(r"rgba?\(\s*([\d.+-]+%?)\s*[, ]\s*([\d.+-]+%?)\s*[, ]\s*([\d.+-]+%?)(?:\s*[,/]\s*([\d.]+%?))?\s*\)", re.I)
PAINT_ATTRS = {"fill", "stroke", "color", "stop-color", "flood-color", "lighting-color"}
CSS_VALUE = re.compile(r"(?:^|[;{])\s*(?P<property>--[\w-]+|color|background(?:-color)?|border(?:-[\w-]+)?|(?:box|text)-shadow|fill|stroke|stop-color|flood-color|lighting-color|outline(?:-color)?|caret-color|text-decoration-color)\s*:\s*(?P<value>[^;}]+)", re.I)
NAMED = {"black": "#000000", "white": "#ffffff", "gray": "#808080", "grey": "#808080", "red": "#ff0000", "blue": "#0000ff", "green": "#008000", "pink": "#ffc0cb", "orange": "#ffa500", "yellow": "#ffff00", "purple": "#800080", "silver": "#c0c0c0", "navy": "#000080"}


def normalize_hex(value: str) -> str:
    digits = value.lstrip("#").lower()
    if len(digits) in (3, 4):
        return "#" + "".join(v * 2 for v in digits[:3])
    return "#" + digits[:6]


def function_arguments(value: str, name_pattern: str):
    """Yield complete function arguments, including nested paint functions."""
    for match in re.finditer(name_pattern + r"\(", value, re.I):
        start, depth = match.end(), 1
        for index in range(start, len(value)):
            depth += (value[index] == "(") - (value[index] == ")")
            if depth == 0:
                yield value[start:index]
                break


def split_arguments(value: str):
    start, depth = 0, 0
    for index, character in enumerate(value):
        depth += (character == "(") - (character == ")")
        if character == "," and depth == 0:
            yield value[start:index]
            start = index + 1
    yield value[start:]


def value_colors(value: str, strict_literal: bool = False) -> set[str]:
    value = re.sub(r"!\s*important\b", "", value, flags=re.I)
    value = re.sub(r"url\([^)]*\)", "", value, flags=re.I)
    colors = {normalize_hex(match[0]) for match in HEX.finditer(value)}
    recognized = []
    for match in RGB.finditer(value):
        recognized.append(match.span())
        if match[4] is not None and float(match[4].rstrip("%")) == 0:
            continue
        channels = tuple(max(0, min(255, round(float(match[i].rstrip("%")) * (255 / 100 if match[i].endswith("%") else 1)))) for i in (1, 2, 3))
        colors.add("#" + "".join(f"{v:02x}" for v in channels))
    token = value.strip().lower()
    if token in NAMED:
        colors.add(NAMED[token])
    elif strict_literal and re.fullmatch(r"[a-z]+", token) and token not in {"none", "transparent", "currentcolor", "inherit", "initial", "unset", "revert", "context-fill", "context-stroke"}:
        colors.add(f"unresolved-paint:{token}")
    for match in re.finditer(r"hsla?\(\s*([\d.+-]+)(?:deg)?\s*[, ]\s*([\d.]+)%\s*[, ]\s*([\d.]+)%(?:\s*[,/]\s*([\d.]+%?))?\s*\)", value, re.I):
        recognized.append(match.span())
        if match[4] is not None and float(match[4].rstrip("%")) == 0:
            continue
        rgb = colorsys.hls_to_rgb(float(match[1]) % 360 / 360, float(match[3]) / 100, float(match[2]) / 100)
        colors.add("#" + "".join(f"{round(v * 255):02x}" for v in rgb))
    for match in re.finditer(r"(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color|color-mix)\([^)]*\)", value, re.I):
        if match.span() not in recognized:
            colors.add("unresolved-paint:" + match[0].lower())
    if strict_literal:
        # Composite border/shadow/gradient declarations can contain named paint.
        scrubbed = re.sub(r"(?:#[\da-fA-F]+|(?<![\w-])[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:px|em|rem|pt|%|deg)?|var\([^)]*\)|[\w-]+\([^)]*\))", " ", value)
        ignored = {"none", "transparent", "currentcolor", "inherit", "initial", "unset", "revert", "context-fill", "context-stroke", "solid", "dashed", "dotted", "double", "groove", "ridge", "inset", "outset", "to", "left", "right", "top", "bottom", "center", "at", "circle", "ellipse", "repeat", "no-repeat", "cover", "contain", "auto"}
        for word in re.findall(r"(?<![\w-])[a-zA-Z]+(?![\w-])", scrubbed):
            if word.lower() in NAMED:
                colors.add(NAMED[word.lower()])
            elif word.lower() not in ignored:
                colors.add("unresolved-paint:" + word.lower())
        for gradient in function_arguments(value, r"(?:repeating-)?(?:linear|radial|conic)-gradient"):
            for stop in split_arguments(gradient):
                colors.update(value_colors(stop, True))
    return colors


def artifact_colors(path: Path) -> tuple[set[str], str | None]:
    text = path.read_text(encoding="utf-8")
    colors: set[str] = set()
    declared = None
    css_source = text
    if path.suffix.lower() in {".html", ".htm"}:
        class StyleHTMLParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.in_style, self.parts = False, []
            def handle_starttag(self, tag, attrs):
                self.in_style = tag == "style"
                self.parts.append(dict(attrs).get("style") or "")
            def handle_endtag(self, tag):
                if tag == "style":
                    self.in_style = False
            def handle_data(self, data):
                if self.in_style:
                    self.parts.append(data)
        styles = StyleHTMLParser()
        styles.feed(text)
        css_source = "\n".join(styles.parts)
    css_matches = list(CSS_VALUE.finditer(css_source))
    referenced = set()
    for match in css_matches:
        if not match["property"].startswith("--"):
            referenced.update(re.findall(r"var\(\s*(--[\w-]+)", match["value"]))
    for _ in range(len(css_matches)):
        previous = set(referenced)
        for match in css_matches:
            if match["property"] in referenced:
                referenced.update(re.findall(r"var\(\s*(--[\w-]+)", match["value"]))
        if previous == referenced:
            break
    def css_colors(match):
        return value_colors(match["value"], not match["property"].startswith("--") or match["property"] in referenced)
    if path.suffix.lower() == ".svg":
        root = ET.fromstring(text)
        declared = next((root.get(key) for key in ("data-colorset", "data-color-set", "data-palette", "data-colorset-mode") if root.get(key) in {"colorset1", "colorset2"}), None)
        def visit(node: ET.Element) -> None:
            tag = node.tag.rsplit("}", 1)[-1]
            if tag in {"metadata", "desc", "title"}:
                return
            for key in PAINT_ATTRS:
                if tag in {"animate", "animateTransform", "animateMotion", "set"} and key == "fill":
                    continue
                colors.update(value_colors(node.get(key, ""), True))
            for match in CSS_VALUE.finditer(node.get("style", "")):
                colors.update(css_colors(match))
            if node.tag.rsplit("}", 1)[-1] == "style":
                for match in CSS_VALUE.finditer(node.text or ""):
                    colors.update(css_colors(match))
            if node.tag.rsplit("}", 1)[-1] in {"animate", "set"} and node.get("attributeName") in PAINT_ATTRS:
                for key in ("values", "from", "to", "by"):
                    for value in node.get(key, "").split(";"):
                        colors.update(value_colors(value, True))
            for child in node:
                visit(child)
        visit(root)
    else:
        declared_match = re.search(r'data-(?:colorset|color-set|palette)=["\'](colorset[12])["\']', text) if path.suffix.lower() in {".html", ".htm"} else None
        declared = declared_match[1] if declared_match else None
        # Script/vendor tables are inputs, not proof of rendered paint. Dynamic
        # HTML requires independent browser/SVG/canvas state inspection.
        for match in css_matches:
            colors.update(css_colors(match))
        if path.suffix.lower() in {".html", ".htm"}:
            class PaintHTMLParser(HTMLParser):
                def handle_starttag(self, tag, attrs):
                    attributes = dict(attrs)
                    for key in PAINT_ATTRS:
                        if key == "fill" and tag in {"animate", "animatetransform", "animatemotion", "set"}:
                            continue
                        colors.update(value_colors(attributes.get(key) or "", True))
                    for match in CSS_VALUE.finditer(attributes.get("style") or ""):
                        colors.update(css_colors(match))
                    if tag in {"animate", "set"} and attributes.get("attributename") in PAINT_ATTRS:
                        for key in ("from", "to", "by", "values"):
                            for value in (attributes.get(key) or "").split(";"):
                                colors.update(value_colors(value, True))
                handle_startendtag = handle_starttag
            PaintHTMLParser().feed(text)
        if path.suffix.lower() in {".js", ".ts", ".py", ".json"}:
            colors.update(value_colors(text))
    return colors, declared


def validate(root: Path, inputs: list[Path] | None = None, mode: str = "auto") -> dict:
    contract = json.loads((root / "docs/colorsets.json").read_text(encoding="utf-8"))
    allowed = {name: set(row["allowed"]) for name, row in contract["colorsets"].items()}
    findings, checked, copies = [], [], []
    for name, row in contract["colorsets"].items():
        sequence = row.get("solidSequence", [])
        text_map = row.get("textOnFill", {})
        if name == "colorset1":
            for field in ("sequence", "solidSequence"):
                if row.get(field) != CS1_CATEGORY_ORDER:
                    findings.append({"path": "docs/colorsets.json", "colorset": name, "field": field, "error": "CS1 categories must follow primary red, grays, black, white, then remaining colors", "expected": CS1_CATEGORY_ORDER})
            if row.get("categoryPriority") != CS1_CATEGORY_PRIORITY:
                findings.append({"path": "docs/colorsets.json", "colorset": name, "error": "CS1 category priority declaration differs from the user preference"})
        if len(sequence) != len(set(sequence)) or set(sequence) != allowed[name]:
            findings.append({"path": "docs/colorsets.json", "colorset": name, "error": "Solid sequence must contain every allowed token exactly once"})
        if set(text_map) != allowed[name]:
            findings.append({"path": "docs/colorsets.json", "colorset": name, "error": "Every solid token needs a black/white text decision"})
        for fill, text in text_map.items():
            rgb = [int(fill[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            linear = [c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in rgb]
            luminance = sum(c * w for c, w in zip(linear, (.2126, .7152, .0722)))
            black, white = (luminance + .05) / .05, 1.05 / (luminance + .05)
            expected = "#000000" if black >= white else "#ffffff"
            if text != expected:
                findings.append({"path": "docs/colorsets.json", "colorset": name, "fill": fill, "error": "Text must maximize exact black/white contrast", "expected": expected})
    if inputs is None:
        inventory = json.loads((root / "evaluations/colorset-audit/coverage.json").read_text(encoding="utf-8"))
        names = [row["skill"] for row in inventory["skills"]]
        actual = {p.name for p in (root / "skills").iterdir() if (p / "SKILL.md").is_file()}
        if set(names) != actual or len(names) != len(set(names)):
            findings.append({"path": "coverage.json", "error": "Inventory must cover each skill exactly once", "missing": sorted(actual - set(names)), "extra": sorted(set(names) - actual)})
        for row in inventory["skills"]:
            if not row.get("outputs") or not row.get("scope"):
                findings.append({"path": row["skill"], "error": "Output routes and paint scope are required"})
        def includes(expected, actual):
            if isinstance(expected, dict):
                return isinstance(actual, dict) and all(key in actual and includes(value, actual[key]) for key, value in expected.items())
            return expected == actual
        for path in sorted((root / "skills").glob("*/assets/palettes/colorsets.json")):
            if not includes(contract, json.loads(path.read_text(encoding="utf-8"))):
                findings.append({"path": path.relative_to(root).as_posix(), "error": "Palette copy differs from canonical contract"})
            copies.append(path.relative_to(root).as_posix())
        targets = []
        for row in inventory.get("artifactChecks", []):
            matches = sorted(root.glob(row["glob"]))
            if not matches and row.get("required", True):
                findings.append({"path": row["glob"], "error": "Artifact check matched no files"})
            targets.extend((path, row.get("colorset", "auto")) for path in matches if path.is_file())
    else:
        targets = [(path, mode) for path in inputs]
    for path, selected in targets:
        try:
            colors, declared = artifact_colors(path)
            active = selected if selected != "auto" else (declared or ("colorset1" if colors <= allowed["colorset1"] else "colorset2"))
            bad = sorted(colors - allowed[active])
            label = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
            checked.append({"path": label, "colorset": active, "paintCount": len(colors)})
            if bad:
                findings.append({"path": label, "colorset": active, "offPalette": bad})
            if selected != "auto" and declared and declared != selected:
                findings.append({"path": label, "error": "Declared colorset does not match expected mode"})
        except (OSError, ValueError, ET.ParseError, KeyError) as error:
            findings.append({"path": str(path), "error": str(error)})
    return {"ok": not findings, "skillCount": len(names) if inputs is None else None, "paletteCopies": copies, "artifactCount": len(checked), "artifacts": checked, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--input", type=Path, action="append")
    parser.add_argument("--colorset", choices=("auto", "colorset1", "colorset2"), default="auto")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    result = validate(args.root.resolve(), args.input, args.colorset)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Colorset validation {'passed' if result['ok'] else 'failed'}: {result['skillCount']} skills, {len(result['paletteCopies'])} palette copies, {result['artifactCount']} artifacts, {len(result['findings'])} findings.")
    for finding in result["findings"][:40]:
        print(json.dumps(finding))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
