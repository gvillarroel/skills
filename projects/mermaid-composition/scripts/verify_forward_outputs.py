#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6,<7"]
# ///
"""Independently render isolated outputs and inspect palette, labels and metadata."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cli", type=Path, required=True)
    parser.add_argument("--run-id", action="append", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    output = root / "projects/mermaid-composition/artifacts/forward"
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for run_id in args.run_id:
        workspace = root / "evaluations/runs" / run_id / "workspace"
        case = next((kind for kind in ("boundary", "contract", "generalization") if kind in run_id), "naturalistic")
        name = {"boundary": "manual-review.mmd", "contract": "diagrams/intake.mmd", "naturalistic": "shipment.mmd", "generalization": "lending.mmd"}[case]
        source_path = workspace / "deliverables" / name
        source = source_path.read_text(encoding="utf-8")
        frontmatter = yaml.safe_load(source.split("---", 2)[1])
        config = frontmatter["config"]
        findings = []
        spacing = config.get("er" if case == "generalization" else "flowchart", {})
        expected = {"padding": 18, "rankSpacing": 90, "nodeSpacing": 70, "curve": "linear"} if case == "boundary" else {"padding": 6, "rankSpacing": 32, "nodeSpacing": 24}
        if case == "generalization":
            expected = {"entityPadding": 6, "diagramPadding": 6, "nodeSpacing": 60, "rankSpacing": 80}
        for key, value in expected.items():
            if spacing.get(key) != value:
                findings.append(f"Unexpected {key}: {spacing.get(key)}")
        if "#ffccd5" in source.lower():
            findings.append("Unexpected pink source styling")
        svg = output / f"{run_id}.svg"
        subprocess.run(["node", str(args.cli), "-i", str(source_path), "-o", str(svg), "-b", "white"], check=True, capture_output=True)
        tree = ET.parse(svg).getroot()
        nodes = list(tree.iter())
        local = lambda element: element.tag.rsplit("}", 1)[-1]
        visible = " ".join(" ".join(e.itertext()) for e in nodes if local(e) in {"p", "text"})
        labels = {
            "contract": ["Receive work", "Check work", "Archive result"],
            "boundary": ["Analyst", "Review evidence", "Make decision"],
            "naturalistic": ["Receive shipment", "Inspect shipment", "Accepted", "Store goods", "Update inventory", "Record damage", "Request replacement", "Yes", "No"],
            "generalization": ["READER", "BOOK", "LOAN", "reader_id", "book_id", "loan_id", "name", "title", "due_date", "borrows", "records"],
        }[case]
        for label in labels:
            if label not in visible:
                findings.append(f"Missing visible label: {label}")
        ids = [e.get("id") for e in nodes if e.get("id")]
        if len(ids) != len(set(ids)):
            findings.append("Duplicate SVG IDs")
        for attribute, kind in (("aria-labelledby", "title"), ("aria-describedby", "desc")):
            refs = tree.get(attribute, "").split()
            targets = [e for e in tree if e.get("id") in refs and local(e) == kind and "".join(e.itertext()).strip()]
            if not targets:
                findings.append(f"Missing resolved accessible {kind}")
        if tree.get("aria-roledescription") == "error":
            findings.append("Mermaid error SVG")
        relations = len(re.findall(r"-->", source.split("---", 2)[2]))
        if case == "generalization":
            relations = 0
            for entity, label in (("READER", "borrows"), ("BOOK", "records")):
                if re.search(rf'\b{entity}\s+\|\|--o\{{\s+LOAN\s*:\s*"?{label}"?', source) or re.search(rf'\bLOAN\s+\}}o--\|\|\s+{entity}\s*:\s*"?{label}"?', source):
                    relations += 1
                else:
                    findings.append(f"Missing exact cardinality and label for {entity}")
            attributes = {
                "READER": [("int", "reader_id", "PK"), ("string", "name", "")],
                "BOOK": [("int", "book_id", "PK"), ("string", "title", "")],
                "LOAN": [("int", "loan_id", "PK"), ("int", "reader_id", "FK"), ("int", "book_id", "FK"), ("date", "due_date", "")],
            }
            for entity, rows in attributes.items():
                block = re.search(rf'\b{entity}\s*\{{([^}}]*)\}}', source, re.S)
                for kind, name, key in rows:
                    if not block or not re.search(rf'^\s*{kind}\s+{name}\b\s*{key}\s*$', block.group(1), re.M):
                        findings.append(f"Missing exact attribute: {entity}.{name}")
        if relations != (6 if case == "naturalistic" else 2):
            findings.append(f"Unexpected relation count: {relations}")
        results.append({"runId": run_id, "case": case, "passed": not findings, "findings": findings, "svg": str(svg.relative_to(root)), "labelsVerified": len(labels), "relationCount": relations, "viewBox": tree.get("viewBox")})
    report = {"passed": all(r["passed"] for r in results), "results": results}
    (output / "review.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    capture = r'''
const {createRequire} = require('module');
const {pathToFileURL} = require('url');
const path = require('path');
const fs = require('fs');
(async () => {
 const puppeteer = createRequire(process.argv[1])('puppeteer');
 const dir = process.argv[2];
 const browser = await puppeteer.launch({headless:true});
 try {
  const page = await browser.newPage();
  await page.setViewport({width:1200,height:900,deviceScaleFactor:1});
  for (const result of JSON.parse(fs.readFileSync(path.join(dir,'review.json'),'utf8')).results) {
   await page.goto(pathToFileURL(path.join(dir,result.runId+'.svg')).href);
   await (await page.$('svg')).screenshot({path:path.join(dir,result.runId+'.png')});
  }
 } finally { await browser.close(); }
})().catch(error=>{console.error(error);process.exit(1)});
'''
    subprocess.run(["node", "-e", capture, str(args.cli.resolve().parent.parent / "package.json"), str(output)], check=True)
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
