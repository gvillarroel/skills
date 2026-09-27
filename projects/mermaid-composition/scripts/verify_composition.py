#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render and inspect compact Mermaid defaults with a cached pinned CLI."""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--run-name", default="all-families")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    artifact = root / "projects/mermaid-composition/artifacts"
    cli = args.cli.resolve()
    if args.full:
        validator = load_module("composition_family_validation", root / "skills/mermaid/assets/examples/mermaid-max-elements/scripts/validate_max_elements.py")
        validator.render_command = lambda: ["node", str(cli)]
        sys.argv = [str(validator.__file__), "--work-dir", str(artifact / args.run_name), "--report", str(artifact / f"{args.run_name}-report.json"), "--render-attempts", "1"]
        return validator.main()

    baseline = load_module("composition_baseline", artifact / "baseline/scripts/style_mermaid_directory.py")
    current = load_module("composition_current", root / "skills/mermaid/scripts/style_mermaid_directory.py")
    sources = {
        "vertical": '''flowchart TB
 accTitle: Request processing
 accDescr: Requests move through validation, processing, recording, and delivery.
 A[Receive request] --> B[Validate request] --> C[Process request] --> D[Record result] --> E[Deliver response]
''',
        "branching": '''flowchart LR
 accTitle: Validation and recovery
 accDescr: Valid work is processed and delivered; invalid work returns for correction.
 A[Receive request] --> B{Valid?}
 B -->|Yes| C[Process request]:::csPrimary --> D[Deliver response]
 B -->|No| E[Correct input]:::csCritical --> A
''',
        "multiline": '''flowchart TB
 accTitle: Deployment review
 accDescr: Review checks precede release and monitoring.
 subgraph Review[Deployment review]
 A["Validate request<br/>Check owner and quota"] --> B["Review changes<br/>Confirm rollback plan"]
 end
 B -->|Approved| C["Release package<br/>Monitor health checks"]:::csPrimary
''',
        "sequence": '''sequenceDiagram
 accTitle: Request exchange
 accDescr: A client requests processing from a service, which reads storage before replying.
 participant Client
 participant Service
 participant Storage
 Client->>Service: Process request
 Service->>Storage: Read record
 Storage-->>Service: Record
 Service-->>Client: Response
''',
        "state": '''stateDiagram-v2
 accTitle: Ticket lifecycle
 accDescr: Tickets move from Draft to Review and then Approved, or return to Draft.
 [*] --> Draft
 Draft --> Review
 Review --> Approved
 Review --> Draft: Revise
 Approved --> [*]
''',
        "class": '''classDiagram
 accTitle: Order structure
 accDescr: An Order contains LineItems and refers to a Customer.
 class Order {
   +int id
   +total()
 }
 class LineItem {
   +int quantity
   +decimal price
 }
 class Customer {
   +string name
 }
 Customer --> Order
 Order *-- LineItem
''',
        "er": '''erDiagram
 accTitle: Customer orders
 accDescr: A customer places many orders, each with one or more line items.
 CUSTOMER ||--o{ ORDER : places
 ORDER ||--|{ LINE_ITEM : contains
''',
        "roles": '''flowchart LR
 accTitle: Semantic color roles
 accDescr: Nine labels identify the supported semantic roles independently of color.
''' + "\n".join(f' R{i}["{role.removeprefix("cs")}"]:::{role}' for i, role in enumerate(current.COLOR_CLASS_ORDER)),
        "indexed": '''mindmap
 root((Portfolio))
''' + "\n".join(f'  Category {i:02d}' for i in range(1, 12)),
    }
    render_dir = artifact / "comparison"
    render_dir.mkdir(parents=True, exist_ok=True)
    batches = []
    cases = []
    for case_id, source in sources.items():
        for name, styler in (("before", baseline), ("after", current)):
            styled, _ = styler.style_mermaid_block(source, "colorset1")
            (render_dir / f"{case_id}-{name}.mmd").write_text(styled, encoding="utf-8")
            batches.append(f"```mermaid\n{styled}\n```\n")
            cases.append({"id": case_id, "variant": name})
    batch = render_dir / "batch.md"
    batch.write_text("\n".join(batches), encoding="utf-8")
    subprocess.run(["node", str(cli), "-i", str(batch), "-o", str(render_dir / "batch.svg"), "-j", "1", "-b", "white"], check=True)
    for i, case in enumerate(cases, 1):
        path = render_dir / f"{case['id']}-{case['variant']}.svg"
        path.write_bytes((render_dir / f"batch-{i}.svg").read_bytes())
        case["path"] = str(path)
    cards = []
    for case_id in sources:
        cells = []
        dimensions = {
            name: [float(value) for value in ET.parse(render_dir / f"{case_id}-{name}.svg").getroot().get("viewBox").split()][2:]
            for name in ("before", "after")
        }
        scale = min(1.5, 800 / max(size[0] for size in dimensions.values()))
        for name in ("before", "after"):
            width, height = dimensions[name]
            cells.append(f'<div><h3>{name.title()} <small>{width:.0f} × {height:.0f} px</small></h3><img style="width:{width * scale:.2f}px" src="{case_id}-{name}.svg" alt="{case_id} {name}"></div>')
        cards.append(f'<section id="{case_id}"><h2>{html.escape(case_id.title())}</h2><div class="pair">{"".join(cells)}</div></section>')
    gallery = render_dir / "index.html"
    gallery.write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Mermaid composition comparison</title>
<style>body{font:16px Arial,sans-serif;color:#333e48;background:#f7f7f7;margin:32px}h1{color:#9e1b32}section{padding:22px;margin:24px 0;background:white;border:1px solid #cfcfcf}h2{text-transform:capitalize}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px}.pair>div{min-width:0;overflow:auto}img{display:block;max-width:100%;height:auto;margin:auto}h3{border-bottom:2px solid #9e1b32;padding-bottom:8px}@media(max-width:800px){.pair{grid-template-columns:1fr}}</style>
<h1>Mermaid composition review</h1><p>Identical source facts. Each pair uses a shared display scale; headings report native SVG bounds. Native compact geometry and neutral surfaces with red emphasis.</p>''' + "".join(cards) + "</html>", encoding="utf-8")
    manifest = render_dir / "cases.json"
    manifest.write_text(json.dumps(cases), encoding="utf-8")
    inspect_js = r'''
const fs = require('fs');
const {createRequire} = require('module');
const {pathToFileURL} = require('url');
const path = require('path');
(async () => {
 const req = createRequire(process.argv[1]);
 const puppeteer = req('puppeteer');
 const dir = process.argv[2];
 const browser = await puppeteer.launch({headless:true});
 try {
  const page = await browser.newPage();
  await page.setViewport({width:1800,height:1100,deviceScaleFactor:1});
  const cases = JSON.parse(fs.readFileSync(path.join(dir,'cases.json'),'utf8'));
  for (const item of cases) {
   await page.goto(pathToFileURL(item.path).href);
   item.metrics = await page.evaluate(() => {
    const svg = document.querySelector('svg');
    const box = el => {const r=el.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}};
    const nodes = [...document.querySelectorAll('.node')].map(n=>{
     const shape = n.querySelector(':scope > rect, :scope > polygon, :scope > path, :scope > circle');
     const label = n.querySelector('.label');
     return {text:n.textContent.trim(),shape:shape?box(shape):null,label:label?box(label):null,fill:shape?getComputedStyle(shape).fill:null,fontSize:label?getComputedStyle(label).fontSize:null};
    });
    const fills = [...document.querySelectorAll('rect,polygon,path,circle')].map(n=>getComputedStyle(n).fill);
    const headings = [...document.querySelectorAll('.cluster-label')].map(box);
    const headingOverlap = headings.some(h=>nodes.some(n=>n.shape && Math.min(h.x+h.width,n.shape.x+n.shape.width)-Math.max(h.x,n.shape.x)>1 && Math.min(h.y+h.height,n.shape.y+n.shape.height)-Math.max(h.y,n.shape.y)>1));
    return {viewBox:svg.getAttribute('viewBox'),width:svg.viewBox.baseVal.width,height:svg.viewBox.baseVal.height,nodes,headingOverlap,hasPink:fills.includes('rgb(255, 204, 213)'),hasError:!!document.querySelector('.error-icon,.error-text,svg[aria-roledescription="error"]')};
   });
  }
  fs.writeFileSync(path.join(dir,'metrics.json'),JSON.stringify(cases,null,2));
  await page.goto(pathToFileURL(path.join(dir,'index.html')).href);
  for (const id of ['vertical','branching','multiline','roles','sequence','class','er','state','indexed']) {
   await page.$eval('#'+id,el=>el.scrollIntoView());
   await (await page.$('#'+id)).screenshot({path:path.join(dir,id+'.png')});
  }
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
'''
    subprocess.run(["node", "-e", inspect_js, str(cli.parent.parent / "package.json"), str(render_dir)], check=True)
    metrics = json.loads((render_dir / "metrics.json").read_text())
    findings = []
    summary = {}
    for case_id in sources:
        before, after = [x["metrics"] for x in metrics if x["id"] == case_id]
        summary[case_id] = {"beforeHeight": before["height"], "afterHeight": after["height"], "heightReductionPercent": round(100 * (1 - after["height"] / before["height"]), 2)}
        if after["hasPink"] or after["hasError"]:
            findings.append(f"{case_id}: pink fill or error SVG")
        if after["headingOverlap"]:
            findings.append(f"{case_id}: cluster title overlaps a node")
        if case_id in {"vertical", "branching", "multiline"}:
            for node in after["nodes"]:
                box, label = node["shape"], node["label"]
                if box and label and (label["height"] > box["height"] - 4 or label["width"] > box["width"] - 4):
                    findings.append(f"{case_id}: label lacks clearance: {node['text']}")
            if after["height"] >= before["height"]:
                findings.append(f"{case_id}: diagram height did not shrink")
            if [n["fontSize"] for n in before["nodes"]] != [n["fontSize"] for n in after["nodes"]]:
                findings.append(f"{case_id}: font size changed")
    report = {"passed": not findings, "findings": findings, "cases": summary}
    (render_dir / "review.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
