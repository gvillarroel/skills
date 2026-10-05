#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.51"]
# ///
"""Verify content-sized native conceptual graph output in Chromium."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

from playwright.sync_api import sync_playwright


SNAPSHOT = r"""() => {
  const svg=document.querySelector('svg'), view=svg.viewBox.baseVal;
  const bounds=el=>{const b=el.getBBox(),m=el.getCTM(),p=[[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].map(([x,y])=>({x:m.a*x+m.c*y+m.e,y:m.b*x+m.d*y+m.f}));const x=Math.min(...p.map(v=>v.x)),y=Math.min(...p.map(v=>v.y));return {x,y,width:Math.max(...p.map(v=>v.x))-x,height:Math.max(...p.map(v=>v.y))-y};};
  const nodeEls=[...svg.querySelectorAll('path[ecmeta_series_index="0"][ecmeta_data_index]')].filter(el=>getComputedStyle(el).fill!=='none'&&!el.getAttribute('d').startsWith('M0 0L'));
  const nodes=nodeEls.map(el=>({index:Number(el.getAttribute('ecmeta_data_index')),bounds:bounds(el)}));
  const gap=(a,b)=>Math.hypot(Math.max(b.x-a.x-a.width,a.x-b.x-b.width,0),Math.max(b.y-a.y-a.height,a.y-b.y-b.height,0));
  const heads=[...svg.querySelectorAll('path[d^="M0 0L"]')].map(el=>({index:Number(el.getAttribute('ecmeta_data_index')),bounds:bounds(el),gap:Math.min(...nodes.map(n=>gap(bounds(el),n.bounds)))}));
  const labels=[...svg.querySelectorAll('text')].map(el=>({text:el.textContent,bounds:bounds(el),fontSize:parseFloat(getComputedStyle(el).fontSize)}));
  const routes=[...svg.querySelectorAll('path[ecmeta_series_index="0"][ecmeta_data_index]')].filter(el=>getComputedStyle(el).fill==='none').map(el=>{
    const m=el.getCTM(),length=el.getTotalLength(),points=[];
    for(let i=0;i<=160;i++){const p=el.getPointAtLength(length*i/160);points.push([m.a*p.x+m.c*p.y+m.e,m.b*p.x+m.d*p.y+m.f]);}
    return {index:Number(el.getAttribute('ecmeta_data_index')),length,points};});
  return {width:view.width,height:view.height,nodes,heads,labels,routes};
}"""


def normalized_svg(source: str) -> str:
    names: dict[str, str] = {}
    return re.sub(r"\bzr\d+-cls-\d+\b", lambda match: names.setdefault(match[0], f"native-{len(names)}"), source)


def intersects(a: dict, b: dict) -> bool:
    return a["x"] < b["x"] + b["width"] and a["x"] + a["width"] > b["x"] and a["y"] < b["y"] + b["height"] and a["y"] + a["height"] > b["y"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Task-owned test workspace and evidence directory.")
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    renderer = Path(__file__).with_name("render_concept_graph.py").resolve()
    workflow = {"title": "Laboratory sample workflow", "nodes": [{"id": name.lower(), "label": name} for name in ["Receive", "Barcode", "Analyze", "Review", "Archive", "Quarantine"]], "edges": [{"source": a, "target": b} for a, b in [("receive", "barcode"), ("barcode", "analyze"), ("analyze", "review"), ("review", "archive")]] + [{"source": "review", "target": "analyze", "kind": "return", "label": "Retest"}, {"source": "analyze", "target": "quarantine", "label": "Failed sample"}]}
    explicit = {**copy.deepcopy(workflow), "width": 1200, "height": 700}
    long_labels = {"title": 'Names & "quoted" provenance', "nodes": [{"id": "a", "label": "Incoming material verification and source provenance"}, {"id": "b", "label": "Independent review of complete relationship labels"}], "edges": [{"source": "a", "target": "b", "label": "Accept & verify"}]}
    row = {"nodes": [{"id": "a", "label": "Input"}, {"id": "b", "label": "Result"}], "edges": [{"source": "a", "target": "b", "label": "Pass"}]}
    column = {"nodes": [{"id": "a", "label": "Input", "x": 0, "y": 0}, {"id": "b", "label": "Result", "x": 0, "y": 180}], "edges": [{"source": "a", "target": "b"}]}
    single = {"nodes": [{"id": "only", "label": "One complete concept"}], "edges": []}
    literal = {"title": 'Literal braces & "XML"', "nodes": [{"id": "a", "label": "Source {a} & provenance"}, {"id": "b", "label": "Target {b} <verified>"}], "edges": [{"source": "a", "target": "b", "label": 'Choose {a}, {b}, {c} & "verify" <next>'}]}
    cases = {"workflow": workflow, "workflow-repeat": workflow, "explicit": explicit, "long-labels": long_labels, "row": row, "column": column, "single": single, "literal-braces": literal}
    reports = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 2000, "height": 1200})
        for name, data in cases.items():
            input_path = output / f"{name}.json"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            result = subprocess.run([sys.executable, str(renderer), input_path.name, "--svg", f"{name}.svg", "--option", f"{name}.option.json", "--review", f"{name}.review.json"], cwd=output, capture_output=True, text=True, encoding="utf-8")
            assert result.returncode == 0, (name, result.stdout, result.stderr)
            svg = (output / f"{name}.svg").read_text(encoding="utf-8")
            ET.fromstring(svg)
            review = json.loads((output / f"{name}.review.json").read_text(encoding="utf-8"))
            assert review["repeat"]["adjustedEdges"] == 0
            page.set_content("<!doctype html><style>body{margin:0}</style>" + svg)
            page.evaluate("document.fonts.ready")
            proof = page.evaluate(SNAPSHOT)
            assert len(proof["nodes"]) == len(data["nodes"]), (name, proof)
            assert len(proof["heads"]) == len(data["edges"]), (name, proof)
            for record in [*proof["nodes"], *proof["heads"], *proof["labels"]]:
                b = record["bounds"]
                assert b["x"] >= -.2 and b["y"] >= -.2 and b["x"] + b["width"] <= proof["width"] + .2 and b["y"] + b["height"] <= proof["height"] + .2, (name, record)
            for head in proof["heads"]:
                assert head["gap"] >= 2.4, (name, head)
            text = " ".join(label["text"] for label in proof["labels"])
            for node in data["nodes"]:
                assert " ".join(node["label"].split()) in " ".join(text.split()), (name, node["label"], text)
            option = json.loads((output / f"{name}.option.json").read_text(encoding="utf-8"))
            for index, node in enumerate(option["series"][0]["data"]):
                body = next(record["bounds"] for record in proof["nodes"] if record["index"] == index)
                for line in node["name"].splitlines():
                    candidates = [label for label in proof["labels"] if label["text"] == line]
                    assert any(label["fontSize"] >= 16 and label["bounds"]["x"] >= body["x"] and label["bounds"]["y"] >= body["y"] and label["bounds"]["x"] + label["bounds"]["width"] <= body["x"] + body["width"] and label["bounds"]["y"] + label["bounds"]["height"] <= body["y"] + body["height"] for label in candidates), (name, line, body, candidates)
            for edge in data["edges"]:
                if edge.get("label"):
                    assert edge["label"] in text
                    caption = next(label for label in proof["labels"] if label["text"] == edge["label"])
                    assert caption["fontSize"] >= 14
                    assert not any(intersects(caption["bounds"], node["bounds"]) for node in proof["nodes"]), (name, caption)
            for route in proof["routes"]:
                edge = data["edges"][route["index"]]
                unrelated = [node for node in proof["nodes"] if data["nodes"][node["index"]]["id"] not in (edge["source"], edge["target"])]
                for x, y in route["points"]:
                    assert not any(intersects({"x": x, "y": y, "width": .01, "height": .01}, node["bounds"]) for node in unrelated), (name, edge)
            if name in ("workflow", "explicit", "long-labels", "literal-braces"):
                page.locator("svg").screenshot(path=str(output / f"{name}.png"), animations="disabled")
            (output / f"{name}.browser.json").write_text(json.dumps(proof, indent=2), encoding="utf-8")
            reports.append({"case": name, "width": proof["width"], "height": proof["height"], "minimumHeadGap": min((head["gap"] for head in proof["heads"]), default=None)})
        browser.close()
    assert normalized_svg((output / "workflow.svg").read_text(encoding="utf-8")) == normalized_svg((output / "workflow-repeat.svg").read_text(encoding="utf-8"))
    natural = json.loads((output / "workflow.review.json").read_text(encoding="utf-8"))
    fixed = json.loads((output / "explicit.review.json").read_text(encoding="utf-8"))
    assert fixed["width"] == 1200 and fixed["height"] == 700
    assert [(n["width"], n["height"]) for n in natural["nodes"]] == [(n["width"], n["height"]) for n in fixed["nodes"]]
    rejected = {"crossing": {"nodes": [{"id": "a", "label": "A", "x": 0, "y": 0}, {"id": "b", "label": "Unrelated", "x": 160, "y": 0}, {"id": "c", "label": "C", "x": 320, "y": 0}], "edges": [{"source": "a", "target": "c"}]}, "too-small": {**workflow, "width": 300, "height": 80}}
    for name, data in rejected.items():
        (output / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")
        result = subprocess.run([sys.executable, str(renderer), f"{name}.json", "--svg", f"{name}.svg", "--option", f"{name}.option.json", "--review", f"{name}.review.json", "--no-install"], cwd=output, capture_output=True, text=True, encoding="utf-8")
        assert result.returncode != 0 and not (output / f"{name}.svg").exists()
        assert ("crosses unrelated node" if name == "crossing" else "Canvas must accommodate") in result.stderr
    compact_probe = {**copy.deepcopy(workflow), "nodes": [{"id": node["id"], "label": node["fullLabel"], "x": node["x"], "y": node["y"]} for node in natural["nodes"]]}
    compact_probe["edges"][-1]["label"] = "Failed sample requires additional independent testing"
    probes = {**rejected, "tight-caption": compact_probe, "accepted": row}
    probe_results = []
    for name, data in probes.items():
        stem = f"probe-{name}"
        (output / f"{stem}.json").write_text(json.dumps(data), encoding="utf-8")
        result = subprocess.run([sys.executable, str(renderer), f"{stem}.json", "--probe", "--svg", f"{stem}.svg", "--option", f"{stem}.option.json", "--review", f"{stem}.review.json", "--no-install"], cwd=output, capture_output=True, text=True, encoding="utf-8")
        assert result.returncode == 0, (name, result.stdout, result.stderr)
        comparison = json.loads((output / f"{stem}.review.json").read_text(encoding="utf-8"))
        assert comparison["accepted"] == (name == "accepted"), (name, comparison)
        if not comparison["accepted"]:
            assert comparison["reason"] and not (output / f"{stem}.svg").exists() and not (output / f"{stem}.option.json").exists()
        if name == "tight-caption":
            assert comparison["gate"] == "caption-node-overlap", comparison
        probe_results.append({"case": name, "accepted": comparison["accepted"], "gate": comparison.get("gate")})
    for name, content in {"invalid-input": json.dumps({"nodes": [{"id": "a", "label": "A"}], "edges": [{"source": "a", "target": "missing"}]}), "broken-json": "{"}.items():
        (output / f"{name}.json").write_text(content, encoding="utf-8")
        result = subprocess.run([sys.executable, str(renderer), f"{name}.json", "--probe", "--svg", f"{name}.svg", "--option", f"{name}.option.json", "--review", f"{name}.review.json", "--no-install"], cwd=output, capture_output=True, text=True, encoding="utf-8")
        assert result.returncode != 0 and not (output / f"{name}.review.json").exists(), (name, result.stdout)
    report = {"ok": True, "cases": reports, "rejected": list(rejected), "probes": probe_results, "invalidInputAndUnexpectedParserErrorsStillFail": True, "repeatedGeometryStable": True, "explicitCanvasPreservesSymbolSizes": True, "fullLabelBoundsAndHeadsCheckedInChromium": True, "literalBraceCaptionsAndXmlCharactersPreserved": True}
    (output / "test-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
