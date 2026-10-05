#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51,<2"]
# ///
"""Review every retained narrow palette-key run with an independent native oracle."""
from pathlib import Path
import argparse
import hashlib
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = ["#9e1b32", "#000000", "#828282", "#1c1c1c", "#9c9c9c", "#363636", "#b5b5b5",
            "#333e48", "#cfcfcf", "#4f4f4f", "#e7e7e7", "#696969", "#f7f7f7",
            "#6d1222", "#e8002a", "#ffccd5"]
FULL_SEQUENCE = EXPECTED[:13] + ["#ffffff"] + EXPECTED[13:]
LABELS = ["Intake", "Triage", "Research", "Proposal", "Review", "Planning", "Design", "Build",
          "Test", "Repair", "Approval", "Release", "Observe", "Support", "Archive", "Learn", "Iterate"]
RAMP = ["#1c1c1c", "#4f4f4f", "#828282", "#b5b5b5", "#e7e7e7"]


def contrast(a, b):
    def lum(token):
        values = [int(token[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        return sum((c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4) * w
                   for c, w in zip(values, (.2126, .7152, .0722)))
    x, y = sorted((lum(a), lum(b)))
    return (y + .05) / (x + .05)


def declared_canvas_is_white(value):
    if isinstance(value, str):
        return value == "#ffffff"
    if isinstance(value, dict):
        paints = [value[name] for name in ("fill", "background", "color") if name in value]
        return bool(paints) and all(paint == "#ffffff" for paint in paints)
    return False


SCRIPT = """() => {
 const svg=document.querySelector('svg');
 const hex=value=>{const m=value.match(/^rgb\\((\\d+),\\s*(\\d+),\\s*(\\d+)\\)$/);return m?'#'+m.slice(1).map(v=>(+v).toString(16).padStart(2,'0')).join(''):value;};
 const rect=e=>{const r=e.getBoundingClientRect();return{x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
 const item=(e,index)=>{const s=getComputedStyle(e);let opacity=1,visible=true;for(let p=e;p&&p instanceof Element;p=p.parentElement){const style=getComputedStyle(p);opacity*=+style.opacity;visible&&=style.visibility==='visible'&&style.display!=='none'&&style.clipPath==='none';}return{index,tag:e.tagName,fill:hex(s.fill),stroke:hex(s.stroke),strokeWidth:parseFloat(s.strokeWidth),fillOpacity:+s.fillOpacity,opacity,visible,rect:rect(e)};};
 const bodies=attribute=>{const seen=new Set(),out=[];for(const owner of document.querySelectorAll('['+attribute+']')){const candidates=owner.matches('rect,circle,ellipse,path,polygon')?[owner]:[...owner.querySelectorAll('rect,circle,ellipse,path,polygon')];for(const e of candidates){if(seen.has(e)||getComputedStyle(e).fill==='none')continue;seen.add(e);out.push(item(e,+owner.getAttribute(attribute)));}}return out;};
 return {title:svg?.querySelector('title')?.textContent,description:svg?.querySelector('desc')?.textContent,stage:svg?rect(svg):null,
 bodies:bodies('data-category-index'),
 labels:[...document.querySelectorAll('[data-category-label]')].map(e=>({...item(e,+e.dataset.categoryLabel),text:e.textContent.trim(),fontSize:parseFloat(getComputedStyle(e).fontSize)})),
 quantitative:bodies('data-quantitative-index'),allText:[...svg.querySelectorAll('text')].map(e=>({...item(e,null),text:e.textContent.trim(),fontSize:parseFloat(getComputedStyle(e).fontSize)})),
 svgBackground:hex(getComputedStyle(svg).backgroundColor),
 backings:[...svg.querySelectorAll('rect')].filter(e=>{const a=rect(e),b=rect(svg);return a.x<=b.x+.5&&a.y<=b.y+.5&&a.right>=b.right-.5&&a.bottom>=b.bottom-.5;}).map(e=>item(e,null))};
}"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", choices=("r1", "r2", "r3", "r4"), default="r1")
    parser.add_argument("--report-name", help="New report filename; existing reports are never overwritten.")
    args = parser.parse_args()
    category_count = 13 if args.revision == "r4" else 17
    labels_expected = LABELS[:category_count]
    case_family = "gray-prefix" if args.revision == "r4" else "full-cycle"
    rows = []
    canonical = json.loads((ROOT / "docs/colorsets.json").read_bytes())["colorsets"]
    out = ROOT / "projects/grayscale-interleave/artifacts/reviews/forward-native"
    out.mkdir(parents=True, exist_ok=True)
    report_name = args.report_name or f"{args.revision}-results.json"
    if Path(report_name).name != report_name or not report_name.endswith(".json"):
        raise SystemExit("Use a plain JSON report filename.")
    report_path = out / report_name
    if report_path.exists():
        raise SystemExit(f"Preserve the existing report and choose a new report name: {report_path}")
    captures = out / report_path.stem
    captures.mkdir(exist_ok=False)
    oracle_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1200})
        for run in sorted((ROOT / "evaluations/runs").glob(f"gray-20261005-{args.revision}-*")):
            result_file = run / "evaluation-result.json"
            if not result_file.exists():
                continue
            manifest = json.loads((run / "run-manifest.json").read_bytes())
            result = json.loads(result_file.read_bytes())
            skill = manifest["skill"]["name"]
            workspace = run / "workspace"
            family = "naturalistic" if "naturalistic" in run.name else "contract"
            findings = []
            detail = None
            if family == "contract":
                path = workspace / "contract.json"
                if not path.exists():
                    findings.append("missing contract.json")
                else:
                    observed = json.loads(path.read_bytes())
                    owner = json.loads((workspace / "skills" / skill / "assets/palettes/colorsets.json").read_bytes())["colorsets"]
                    for palette in ("colorset1", "colorset2"):
                        if observed.get(palette) != owner[palette]:
                            findings.append(f"{palette} contract differs from copied owner definition")
                        for field, value in canonical[palette].items():
                            if field not in owner[palette] or owner[palette][field] != value:
                                findings.append(f"{palette} canonical field differs or is missing: {field}")
                    for canvas in ("#ffffff", "#000000", "#828282"):
                        expected = [c for c in FULL_SEQUENCE if c != canvas]
                        if observed.get("canvases", {}).get(canvas) != expected:
                            findings.append(f"incorrect canvas filter {canvas}")
            else:
                svg, allocation = workspace / "key.svg", workspace / "allocation.json"
                if not svg.exists() or not allocation.exists():
                    findings.append("missing naturalistic artifacts")
                else:
                    try:
                        data = json.loads(allocation.read_bytes())
                        if not declared_canvas_is_white(data.get("canvas")) or data.get("quantitativeRamp") != RAMP:
                            findings.append("incorrect canvas or quantitative JSON ramp")
                        print(f"Reviewing {run.name}", flush=True)
                        page.set_content('<!doctype html><style>body{margin:0;background:white}</style>' + svg.read_text(encoding='utf-8'), wait_until='domcontentloaded')
                        detail = page.evaluate(SCRIPT)
                        if not detail["title"] or not detail["description"]:
                            findings.append("missing accessible title/description")
                        if (not detail['backings'] and detail['svgBackground'] != '#ffffff') or any(r['fill'] != '#ffffff' or r['opacity'] != 1 or r['fillOpacity'] != 1 or not r['visible'] for r in detail['backings']):
                            findings.append('actual white canvas backing missing or incorrect')
                        if len(detail["bodies"]) != category_count or len(detail["labels"]) != category_count:
                            findings.append("incorrect actual body/label count")
                        body_map = {r["index"]: r for r in detail["bodies"]}
                        label_map = {r["index"]: r for r in detail["labels"]}
                        entries = {r["index"]: r for r in data.get("categories", [])}
                        if len(entries) != category_count or (category_count == 13 and len(data.get("categories", [])) != 13):
                            findings.append("incorrect allocation count")
                        def contains(outer, inner, tolerance=.5):
                            return inner["x"] >= outer["x"]-tolerance and inner["y"] >= outer["y"]-tolerance and inner["right"] <= outer["right"]+tolerance and inner["bottom"] <= outer["bottom"]+tolerance
                        for i, text in enumerate(labels_expected):
                            body, label, entry = body_map.get(i), label_map.get(i), entries.get(i)
                            if not body or not label or not entry:
                                findings.append(f"missing category {i}")
                                continue
                            fill = EXPECTED[i % 16]
                            ink = canonical["colorset1"]["textOnFill"][fill]
                            if body["fill"] != fill or entry.get("fill") != fill:
                                findings.append(f"incorrect actual/declared fill {i}")
                            if label["fill"] != ink or entry.get("text") != ink or label["text"] != text or entry.get("label") != text:
                                findings.append(f"incorrect text/identity {i}")
                            if i < 16 and (body["stroke"] != "none" or entry.get("stroke") != "none"):
                                findings.append(f"premature border {i}")
                            if i == 16:
                                border = body["stroke"]
                                if entry.get('stroke') != border:
                                    findings.append('declared overflow border differs from actual paint')
                                if border not in canonical["colorset1"]["allowed"] or border == fill or body["strokeWidth"] <= 0 or contrast(border, fill) < 3:
                                    findings.append("invalid first overflow border")
                            if body["opacity"] != 1 or body["fillOpacity"] != 1 or not body['visible']:
                                findings.append(f"nonopaque body {i}")
                            if label['opacity'] != 1 or label['fillOpacity'] != 1 or not label['visible']:
                                findings.append(f"hidden or translucent category label {i}")
                            if label["fontSize"] < 18 or not contains(body["rect"], label["rect"]):
                                findings.append(f"unreadable/overflowing label {i}")
                            if not contains(detail["stage"], body["rect"]):
                                findings.append(f"clipped body {i}")
                        for i, a in enumerate(detail["bodies"]):
                            for b in detail["bodies"][i+1:]:
                                ar, br = a["rect"], b["rect"]
                                if min(ar["right"],br["right"])-max(ar["x"],br["x"]) > .5 and min(ar["bottom"],br["bottom"])-max(ar["y"],br["y"]) > .5:
                                    findings.append(f"overlapping categories {a['index']}/{b['index']}")
                        quant = sorted(detail["quantitative"], key=lambda r:r["index"])
                        if [r["fill"] for r in quant] != RAMP:
                            findings.append("actual quantitative ramp changed")
                        for i, text in enumerate(['Low', 'Medium-low', 'Medium', 'Medium-high', 'High']):
                            labels = [r for r in detail['allText'] if r['text'] == text]
                            if len(labels) != 1 or labels[0]['fontSize'] < 18 or i >= len(quant):
                                findings.append(f"unreadable quantitative label {text}")
                            elif not labels[0]['visible'] or labels[0]['opacity'] != 1 or labels[0]['fillOpacity'] != 1 or not quant[i]['visible'] or quant[i]['opacity'] != 1 or quant[i]['fillOpacity'] != 1:
                                findings.append(f"hidden/translucent quantitative mark {text}")
                            else:
                                ink = labels[0]['fill']
                                backing = RAMP[i] if contains(quant[i]['rect'], labels[0]['rect']) else '#ffffff'
                                if backing == '#ffffff':
                                    lr = labels[0]['rect']
                                    for mark in detail['bodies'] + quant:
                                        mr = mark['rect']
                                        if min(lr['right'],mr['right'])-max(lr['x'],mr['x']) > .5 and min(lr['bottom'],mr['bottom'])-max(lr['y'],mr['y']) > .5:
                                            findings.append(f"quantitative caption crosses a painted mark {text}")
                                if ink not in canonical['colorset1']['allowed'] or contrast(ink, backing) < 4.5:
                                    findings.append(f"weak quantitative text contrast {text}")
                        for label in detail['allText']:
                            if not contains(detail['stage'], label['rect']):
                                findings.append(f"clipped visible text {label['text']}")
                        page.locator('svg').screenshot(path=str(captures / f"{run.name}.png"), timeout=10000)
                    except Exception as error:
                        findings.append(f"artifact review error: {error}")
            row = {"runId": run.name, "skill": skill, "family": family,
                   "strictPassed": result.get("passed") is True, "artifactPassed": not findings,
                   "passed": result.get("passed") is True and not findings, "findings": findings,
                   "payloadSha256": manifest["skill"]["payloadSha256"], "native": detail,
                   "caseFamily": "complete-contract" if family == "contract" else case_family,
                   "categoryCount": None if family == "contract" else category_count, "oracleSha256": oracle_sha256,
                   "capturePath": (captures/f"{run.name}.png").relative_to(ROOT).as_posix() if detail else None,
                   "outputSha256": {name:hashlib.sha256((workspace/name).read_bytes()).hexdigest()
                                    for name in manifest['expectedOutputs'] if (workspace/name).is_file()}}
            rows.append(row)
        browser.close()
    report_path.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    summary = {"runCount": len(rows), "strictPassed": sum(r['strictPassed'] for r in rows),
               "accepted": sum(r['passed'] for r in rows), "failures": [{"run":r['runId'],"findings":r['findings']} for r in rows if not r['passed']]}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
