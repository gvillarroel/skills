#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check visible poster content against evaluator-owned task data, not agent claims."""

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

NS={"s":"http://www.w3.org/2000/svg"}
CHAINS=[
    ["Glass Hall","Prism School","Color Studio","Light College","Spectrum Lab"],
    ["Glass Hall","Lens School","Focus Studio","Image College","Vision Lab"],
    ["Timber Hall","Oak School","Beam Studio","Frame College","Timber Lab"],
    ["Timber Hall","Cedar School","Joinery Studio","Craft College","Wood Lab"],
    ["Iron Hall","Forge School","Heat Studio","Alloy College","Metal Lab"],
    ["Iron Hall","Tool School","Gear Studio","Motion College","Kinetic Lab"],
]
INFLUENCES=[("Color Studio","Frame College"),("Gear Studio","Vision Lab")]
PHASES=[
    ("Steam Era",1900,1925),("Electric Era",1925,1950),("Metro Era",1950,1975),("Regional Era",1975,2000),("Integrated Rail",2000,2020),
    ("Ferry Guild",1900,1920),("Motor Ferries",1920,1945),("River Authority",1945,1970),("Fast Ferries",1970,1995),("Water Transit",1995,2020),
    ("Coach Routes",1900,1930),("Motor Buses",1930,1955),("City Transit",1955,1980),("Busways",1980,2000),("Electric Buses",2000,2020),
]


def check(workspace,case):
    findings=[]
    if case=="boundary":
        data=json.loads((workspace/"review/diagnostic.json").read_text(encoding="utf-8-sig"))
        if data.get("status")!="needs-data" or data.get("missing_ids")!=["unknown-42"]:findings.append("The unresolved parent was not explicitly identified.")
        if list((workspace/"review").glob("*.svg")):findings.append("A final diagram was created despite unresolved input.")
        source=(workspace/"review/source.json").read_text(encoding="utf-8-sig")
        if not all(v in source for v in ("Ada","Bram","Cora","unknown-42")):findings.append("Source data was not preserved.")
        return {"case":case,"status":"fail" if findings else "pass","findings":findings}
    paths={"naturalistic":"result/poster.svg","generalization":"museum/timeline.svg","contract":"deliverables/chart.svg"}
    root=ET.parse(workspace/paths[case]).getroot()
    nodes=root.findall(".//s:g[@data-node-id]",NS)
    visible={n.attrib["data-node-id"]:" ".join(t.text or "" for t in n.findall("s:text",NS)) for n in nodes}
    texts=" ".join(t.text or "" for t in root.findall(".//s:text",NS))
    if "synthetic" not in texts.lower():findings.append("Synthetic-data notice is not visible.")
    if not root.find("s:title",NS).text or not root.find("s:desc",NS).text:findings.append("Missing accessible title or description.")
    metrics={"node_count":len(nodes)}
    if case=="naturalistic":
        labels={"Quay Guild"}|{x for chain in CHAINS for x in chain}
        expected={("Quay Guild",x,"branch") for x in ("Glass Hall","Timber Hall","Iron Hall")}
        for chain in CHAINS:expected.update((a,b,"branch") for a,b in zip(chain,chain[1:]))
        expected.update((a,b,"influence") for a,b in INFLUENCES)
        lookup={}
        for label in labels:
            hits=[nid for nid,value in visible.items() if re.search(r"(?<!\w)"+re.escape(label)+r"(?!\w)",value,re.IGNORECASE)]
            if len(hits)!=1:findings.append(f"Expected exactly one visible {label}; found {len(hits)}.")
            else:lookup[hits[0]]=label
        continuation_pairs={(a,b) for chain in CHAINS for a,b in zip(chain[1:],chain[2:])}
        actual=set()
        for edge in root.findall(".//s:path[@data-edge-id]",NS):
            a,b,kind=lookup.get(edge.attrib["data-source"]),lookup.get(edge.attrib["data-target"]),edge.attrib["data-kind"]
            # The prompt's "led to" permits institutional continuation or succession.
            # Explicit splits and influence retain their distinct required semantics.
            if (a,b) in continuation_pairs and kind=="succession":kind="branch"
            actual.add((a,b,kind))
        if actual!=expected:findings.append(f"Relationship differences: missing={sorted(expected-actual,key=str)}, extra={sorted(actual-expected,key=str)}")
        if len(nodes)!=28:findings.append("Expected 28 institutions.")
        metrics.update(expected_edges=len(expected),actual_edges=len(actual))
    elif case=="generalization":
        boxes={}
        for label,start,end in PHASES:
            hits=[nid for nid,value in visible.items() if label.lower() in value.lower()]
            if len(hits)!=1:
                findings.append(f"Expected one visible phase: {label}")
                continue
            nid=hits[0]
            if not all(str(y) in visible[nid] for y in (start,end)):findings.append(f"Incorrect visible dates for {label}")
            node=next(n for n in nodes if n.attrib["data-node-id"]==nid)
            # Measure the painted interval ribbon, not metadata or its transparent layout box.
            box=next((r for r in node.findall("s:rect",NS) if r.attrib.get("fill") not in ("none","transparent") and r.attrib.get("data-node-box")!="true"),None)
            if box is None:
                findings.append(f"No painted interval ribbon: {label}")
                continue
            boxes[label]=(float(box.attrib["y"]),float(box.attrib["height"]))
        if len(boxes)==15:
            y0=min(b[0] for b in boxes.values());y1=max(b[0]+b[1] for b in boxes.values())
            for label,start,end in PHASES:
                y,h=boxes[label]
                if abs(y-(y0+(start-1900)/120*(y1-y0)))>.05 or abs(h-(end-start)/120*(y1-y0))>.05:
                    findings.append(f"Incorrect numeric time geometry: {label}")
        if len(nodes)!=15:findings.append("Expected 15 intervals.")
        if root.findall(".//s:path[@data-edge-id]",NS):findings.append("Chronological phases gained unrequested descent links.")
        metrics["intervals_checked"]=len(boxes)
    elif len(nodes)!=10:findings.append("The contract starter must retain ten nodes.")
    return {"case":case,"status":"fail" if findings else "pass","metrics":metrics,"findings":findings}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace",type=Path)
    parser.add_argument("--case",choices=["contract","naturalistic","generalization","boundary"],required=True)
    parser.add_argument("--report",type=Path,required=True)
    args=parser.parse_args()
    report=check(args.workspace,args.case)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report))
    return 0 if report["status"]=="pass" else 1


if __name__=="__main__":
    raise SystemExit(main())
