#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.52"]
# ///
"""Independently inspect PlantUML delivery files through Chromium and decoded PNG."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image
from playwright.sync_api import sync_playwright


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgb(value: str) -> tuple[int, int, int] | None:
    if re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))
    match = re.fullmatch(r"rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*[\d.]+)?\)", value)
    return tuple(int(item) for item in match.groups()) if match else None


def luminance(color: tuple[int, int, int]) -> float:
    channels = [channel / 255 for channel in color]
    linear = [channel / 12.92 if channel <= .04045 else ((channel + .055) / 1.055) ** 2.4 for channel in channels]
    return sum(channel * weight for channel, weight in zip(linear, (.2126, .7152, .0722)))


def contrast(first: tuple[int, int, int], second: tuple[int, int, int]) -> float:
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + .05) / (dark + .05)


def backing(image: Image.Image, point: list[float]) -> tuple[int, int, int]:
    x, y = int(round(point[0])), int(round(point[1]))
    samples = [image.getpixel((min(max(x + dx, 0), image.width - 1), min(max(y + dy, 0), image.height - 1)))[:3]
               for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    return Counter(samples).most_common(1)[0][0]


DOM_AUDIT = r"""() => {
  const svg = document.querySelector('svg');
  const point = (element, x, y) => { const p = new DOMPoint(x,y).matrixTransform(element.getScreenCTM()); return [p.x,p.y]; };
  const nativeShapes = Array.from(svg.querySelectorAll('rect,ellipse,circle,polygon,path')).filter(element => !element.closest('defs,marker,clipPath'));
  const text = Array.from(svg.querySelectorAll('text')).filter(element => element.textContent.trim()).map(element => {
    const box = element.getBBox(), style = getComputedStyle(element);
    const center=point(element,box.x+box.width*.5,box.y+box.height*.5);
    let bodyIndex=null;
    nativeShapes.forEach((shape,index) => {
      if (getComputedStyle(shape).fill==='none' || shape.closest('g.link,g.message') || shape.hasAttribute('data-arrow-id')) return;
      if (!(shape.compareDocumentPosition(element)&Node.DOCUMENT_POSITION_FOLLOWING)) return;
      const p=new DOMPoint(...center).matrixTransform(shape.getScreenCTM().inverse());
      if(typeof shape.isPointInFill==='function'&&shape.isPointInFill(p)) bodyIndex=index;
    });
    return {text:element.textContent, paint:style.fill, bodyIndex, points:[.15,.5,.85].map(f => point(element,box.x+box.width*f,box.y+box.height*.5))};
  });
  const shapes = nativeShapes.map(element => {
    const box=element.getBBox(), style=getComputedStyle(element), group=element.closest('g.entity,g.participant');
    return {tag:element.localName, entity:group?.getAttribute('data-qualified-name'), groupText:group?.textContent.trim(), role:element.getAttribute('data-style-role'), fill:style.fill, stroke:style.stroke, width:Number.parseFloat(style.strokeWidth), opacity:Number(style.opacity)*Number(style.fillOpacity), area:box.width*box.height};
  });
  const arrows = Array.from(svg.querySelectorAll('g.link path,g.link line,g.link polygon,g.message path,g.message line,g.message polygon,[data-arrow-id]')).filter(element => !element.closest('defs,marker,clipPath')).map(element => {
    const style=getComputedStyle(element), tag=element.localName, points=[];
    if (typeof element.getTotalLength==='function') {
      const length=element.getTotalLength();
      const count=Math.max(3, Math.ceil(length/3));
      for(let i=0;i<=count;i++) { const p=element.getPointAtLength(length*i/count); points.push(point(element,p.x,p.y)); }
    } else if (element.points) {
      for(let i=0;i<element.points.numberOfItems;i++) { const p=element.points.getItem(i); points.push(point(element,p.x,p.y)); }
    }
    return {tag,id:element.getAttribute('data-arrow-id'),paint:style.stroke!=='none'&&Number.parseFloat(style.strokeWidth)>0?style.stroke:style.fill,points};
  }).filter(element => element.points.length && element.paint!=='none');
  const rect=svg.getBoundingClientRect();
  return {type:svg.getAttribute('data-diagram-type'),width:rect.width,height:rect.height,text,shapes,arrows};
}"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=["baseline", "boundary", "generalization"], required=True)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", args.run_id):
        parser.error("Run ID must be a safe directory name.")
    run_dir = ROOT / "evaluations/runs" / args.run_id
    workspace = run_dir / "workspace"
    case = json.loads((HERE / "cases.json").read_text(encoding="utf-8"))["cases"][args.case]
    findings: list[str] = []
    rows = []
    run_dir.mkdir(parents=True, exist_ok=True)
    required = [workspace / "render-report.json"]
    for name in case["fixtures"]:
        required.extend([workspace / "input" / f"{name}.puml", workspace / "rendered/svg" / f"{name}.svg", workspace / "rendered/png" / f"{name}.png"])
    missing = [path.relative_to(run_dir).as_posix() for path in required if not path.is_file() or not path.stat().st_size]
    if missing:
        result = {"passed": False, "case": args.case, "runId": args.run_id, "findings": [f"Missing or empty required artifact: {path}" for path in missing], "visualReviewRequired": True, "diagrams": []}
        (run_dir / "independent-validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result))
        return 1
    report = json.loads((workspace / "render-report.json").read_text(encoding="utf-8"))
    palette = json.loads((workspace / "skills/plantuml-colorset-renderer/assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"][case["colorset"]]["allowed"]
    allowed = {rgb(token) for token in palette}
    expected_names = set(case["fixtures"])
    results = {row["diagramId"]: row for row in report["results"]}
    if set(results) != expected_names:
        findings.append("Report diagram IDs do not match the exact task sources.")
    if report.get("colorset") != case["colorset"] or report.get("engine") != "cli":
        findings.append("Report palette or engine differs from the task contract.")
    prompt = (HERE / f"{args.case}.md").read_text(encoding="utf-8")
    for source_path, exact_source in re.findall(r"Save exactly `([^`]+)`:\s*```plantuml\s*\n(.*?)\n```", prompt, re.DOTALL):
        actual = (workspace / source_path).read_text(encoding="utf-8").replace("\r\n", "\n").strip()
        if actual != exact_source.strip():
            findings.append(f"Exact source changed: {source_path}")
    screenshots = run_dir / "independent-screenshots"
    screenshots.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for name, contract in case["fixtures"].items():
            svg = workspace / "rendered/svg" / f"{name}.svg"
            png = workspace / "rendered/png" / f"{name}.png"
            xml = ET.parse(svg).getroot()
            page = browser.new_page(viewport={"width": 2500, "height": 1800}, device_scale_factor=1)
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(svg.resolve().as_uri(), wait_until="load")
            dom = page.evaluate(DOM_AUDIT)
            if dom["type"] != contract["type"]:
                findings.append(f"{name}: unexpected native diagram family {dom['type']}.")
            delivered_text = " ".join(item["text"] for item in dom["text"])
            for label in contract["labels"]:
                if label not in delivered_text:
                    findings.append(f"{name}: missing semantic label {label!r}.")
            page.locator("svg").screenshot(path=str(screenshots / f"{name}-svg.png"))
            page.evaluate("""() => { document.querySelectorAll('text,g.link,g.message,[data-arrow-id]').forEach(element=>element.style.visibility='hidden'); }""")
            backings = Image.open(io.BytesIO(page.screenshot())).convert("RGB")
            text_checks = []
            body_labels = {
                "activity": ["Receive specimen", "Validate specimen", "Request missing data", "Archive specimen"],
                "chen": ["Collection"],
                "deployment": ["Gateway", "Collector", "Archive"],
                "expedition-map": contract["labels"] if name == "expedition-map" else [],
                "work-breakdown": contract["labels"] if name == "work-breakdown" else [],
                "lab-network": ["Workstation", "Sample server"],
            }.get(name, [])
            for item in dom["text"]:
                paint = rgb(item["paint"])
                fills = [backing(backings, point) for point in item["points"]]
                choices = [max(((0, 0, 0), (255, 255, 255)), key=lambda color: contrast(color, fill)) for fill in fills]
                ratios = [contrast(paint, fill) if paint is not None else 0 for fill in fills]
                if paint not in {(0, 0, 0), (255, 255, 255)}:
                    findings.append(f"{name}: text {item['text']!r} is not exact black or white.")
                elif any(paint != choice for choice in choices) or min(ratios) < 4.5:
                    findings.append(f"{name}: text {item['text']!r} has wrong actual-backing contrast.")
                if item["text"] in body_labels:
                    body = dom["shapes"][item["bodyIndex"]] if item["bodyIndex"] is not None else None
                    if body is None or rgb(body["fill"]) == (255, 255, 255) or body["opacity"] < .999 or body["stroke"] != "none" and body["width"] > 0:
                        findings.append(f"{name}: native category {item['text']!r} lacks a distinct opaque borderless body.")
                text_checks.append({"text": item["text"], "paint": item["paint"], "backings": fills, "minimumContrast": min(ratios)})
            arrow_checks = []
            for item in dom["arrows"]:
                paint = rgb(item["paint"])
                sampled_backings = [backing(backings, point) for point in item["points"]]
                ratios = [contrast(paint, fill) if paint is not None else 0 for fill in sampled_backings]
                if min(ratios) < 3:
                    findings.append(f"{name}: arrow {item['tag']} has actual-backing contrast below 3:1.")
                low_samples = [{"point": point, "backing": fill, "contrast": ratio}
                               for point, fill, ratio in zip(item["points"], sampled_backings, ratios) if ratio < 3]
                arrow_checks.append({"tag": item["tag"], "id": item["id"], "paint": item["paint"],
                                     "sampleCount": len(ratios), "minimumContrast": min(ratios), "lowContrastSamples": low_samples})
            with Image.open(png) as image:
                image.load()
                decoded = image.convert("RGB")
                pixels = decoded.tobytes()
                colors = {tuple(pixels[offset:offset + 3]) for offset in range(0, len(pixels), 3)}
                if not colors <= allowed:
                    findings.append(f"{name}: PNG contains colors outside the exact selected palette.")
                if abs(image.width - dom["width"]) > 1.5 or abs(image.height - dom["height"]) > 1.5:
                    findings.append(f"{name}: SVG and PNG delivery dimensions disagree.")
                if len(colors) < 3:
                    findings.append(f"{name}: PNG appears blank.")
                dimensions = [image.width, image.height]
            png_output = [output for output in results.get(name, {}).get("outputs", []) if output["format"] == "png"]
            if len(png_output) != 1 or png_output[0].get("svg_derived") is not True:
                findings.append(f"{name}: PNG was not recorded as derived from the finished SVG.")
            for shape in dom["shapes"]:
                if shape["role"] == "solid-body" and (shape["opacity"] < .999 or shape["stroke"] != "none" and shape["width"] > 0):
                    findings.append(f"{name}: declared solid body has transparency or a visible decorative outline.")
            if name == "authored-style":
                authored = [shape for shape in dom["shapes"] if shape["tag"] == "rect" and shape["area"] > 100]
                if len(authored) < 2 or any(rgb(shape["fill"]) != rgb("#cdf3ff") or rgb(shape["stroke"]) != rgb("#007298") or shape["width"] != 3 for shape in authored):
                    findings.append("authored-style: requested exact fill, border paint, or 3px width was lost.")
            rows.append({"diagram": name, "type": dom["type"], "dimensions": dimensions, "svgSha256": digest(svg), "pngSha256": digest(png), "textChecks": text_checks, "arrowChecks": arrow_checks, "shapeInventory": dom["shapes"], "browserErrors": errors, "nativeStyle": xml.get("data-native-style")})
            findings.extend(f"{name}: browser error {error}" for error in errors)
            page.close()
        browser.close()
    result = {"passed": not findings, "case": args.case, "runId": args.run_id, "findings": findings, "visualReviewRequired": True, "method": "Independent Chromium backing samples, native geometry inventory, exact source/label/type checks and decoded PNG", "diagrams": rows}
    (run_dir / "independent-validation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "diagrams"}))
    return int(bool(findings))


if __name__ == "__main__":
    raise SystemExit(main())
