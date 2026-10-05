#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Bind the narrow palette change to its Git baseline and build a visual key."""
from pathlib import Path
import json
import subprocess
import xml.etree.ElementTree as ET
from apply_contract import metrics, NEUTRALS

ROOT = Path(__file__).resolve().parents[3]
BASE = "daaee75353c63ed6dde204d57cfdbae6b9936586"
EXPECTED = ["#9e1b32", "#000000", "#828282", "#1c1c1c", "#9c9c9c", "#363636", "#b5b5b5",
            "#333e48", "#cfcfcf", "#4f4f4f", "#e7e7e7", "#696969", "#f7f7f7",
            "#ffffff", "#6d1222", "#e8002a", "#ffccd5"]


def main():
    findings, records = [], []
    old_sequence = None
    for path in [ROOT / "docs/colorsets.json", *sorted((ROOT / "skills").glob("*/assets/palettes/colorsets.json"))]:
        rel = path.relative_to(ROOT).as_posix()
        old = json.loads(subprocess.run(["git", "show", f"{BASE}:{rel}"], cwd=ROOT, capture_output=True, check=True).stdout)
        current = json.loads(path.read_bytes())
        if old_sequence is None:
            old_sequence = old["colorsets"]["colorset1"]["solidSequence"]
        old["colorsets"]["colorset1"].update(sequence=EXPECTED, solidSequence=EXPECTED,
                                               categoryPriority=["primary-red", "grays", "white", "remaining-colors"])
        if old != current:
            findings.append(rel)
        records.append(rel)
    output = ROOT / "projects/grayscale-interleave/artifacts"
    (output / "manifests").mkdir(parents=True, exist_ok=True)
    report = {"ok": not findings, "baseline": BASE, "contractCount": len(records),
              "findings": findings, "before": metrics(old_sequence), "after": metrics(EXPECTED),
              "preserved": ["allowed tokens", "named roles", "textOnFill", "colorset2"], "paths": records}
    (output / "manifests/contract-scope.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    palette = json.loads((ROOT / "docs/colorsets.json").read_bytes())["colorsets"]["colorset1"]
    ns = "http://www.w3.org/2000/svg"
    ET.register_namespace("", ns)
    svg = ET.Element(f"{{{ns}}}svg", {"viewBox": "0 0 1160 420", "width": "1160", "height": "420", "data-colorset": "colorset1"})
    ET.SubElement(svg, f"{{{ns}}}title").text = "Colorset1 categorical grayscale: previous and interleaved order"
    ET.SubElement(svg, f"{{{ns}}}desc").text = "Twelve unchanged neutral tokens. The revised order alternates darker and lighter halves to increase adjacent separation."
    ET.SubElement(svg, f"{{{ns}}}rect", {"width": "1160", "height": "420", "fill": "#ffffff"})
    def label(x, y, value, size="18", fill="#333e48"):
        ET.SubElement(svg, f"{{{ns}}}text", {"x": str(x), "y": str(y), "font-family": "Arial, sans-serif", "font-size": size, "fill": fill}).text = value
    label(28, 42, "Colorset1 · categorical grayscale", "26")
    for y, caption, colors in [(94, "Previous order", [c for c in old_sequence if c in NEUTRALS]),
                               (250, "Interleaved order", [c for c in EXPECTED if c in NEUTRALS])]:
        label(28, y, caption, "20")
        for i, color in enumerate(colors):
            x = 28 + i * 94
            ET.SubElement(svg, f"{{{ns}}}rect", {"x": str(x), "y": str(y + 16), "width": "86", "height": "72", "fill": color})
            label(x + 12, y + 59, str(i + 1), "22", palette["textOnFill"][color])
            label(x, y + 112, color, "16")
    label(28, 400, "Category order: red → interleaved black/grays → white → remaining colors. Quantitative ramps stay ordered.", "17")
    (output / "svgs").mkdir(exist_ok=True)
    ET.ElementTree(svg).write(output / "svgs/grayscale-order.svg", encoding="utf-8", xml_declaration=True)
    print(json.dumps({k: report[k] for k in ("ok", "contractCount", "findings")}, indent=2))
    print(f"Minimum adjacent neutral lightness gap: {report['before']['minimumLightnessGap']:.3f} -> {report['after']['minimumLightnessGap']:.3f}")
    return bool(findings)


if __name__ == "__main__":
    raise SystemExit(main())
