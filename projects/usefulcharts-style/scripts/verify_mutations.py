#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Prove the browser audit detects independently corrupted visible SVG geometry."""

import argparse
import copy
import importlib.util
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill",type=Path,required=True)
    parser.add_argument("--svg",type=Path,required=True)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--artifacts",type=Path,required=True)
    args=parser.parse_args();args.artifacts.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location("poster_audit",args.skill/"scripts/audit_chart.py")
    audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    ns={"s":"http://www.w3.org/2000/svg"};ET.register_namespace("",ns["s"])
    original=ET.parse(args.svg).getroot();source=json.loads(args.source.read_text(encoding="utf-8"))
    mutations=[]
    node=copy.deepcopy(original);target=node.find(".//s:g[@data-node-id]",ns);node.remove(target)
    mutations.append(("deleted-node",node,"node-inventory"))
    node=copy.deepcopy(original);node.find(".//s:g[@data-node-id]/s:text",ns).set("font-size","300")
    mutations.append(("oversized-label",node,"label-outside-node"))
    node=copy.deepcopy(original);text=node.find(".//s:g[@data-node-id]/s:text",ns);text.set("fill",text.attrib["data-background"])
    mutations.append(("invisible-label",node,"text-contrast"))
    node=copy.deepcopy(original);edge=node.find(".//s:path[@data-edge-id]",ns);edge.set("data-kind","adopted")
    mutations.append(("wrong-relation-kind",node,"source-relation-inventory"))
    node=copy.deepcopy(original);edge=node.find(".//s:path[@data-edge-id]",ns);tokens=edge.attrib["d"].split();tokens[1]=str(float(tokens[1])+100);edge.set("d"," ".join(tokens))
    mutations.append(("detached-source",node,"detached-source"))
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page()
        for name,root,expected in mutations:
            path=args.artifacts/f"{name}.svg";ET.ElementTree(root).write(path,encoding="utf-8",xml_declaration=True)
            page.goto(path.resolve().as_uri());page.evaluate("document.fonts.ready")
            report=page.evaluate(audit.AUDIT);audit.check_source(report,source)
            types={f["type"] for f in report["findings"]}
            assert expected in types,(name,types)
            results.append({"mutation":name,"expected_finding":expected,"detected":True,"finding_count":len(report["findings"])})
        browser.close()
    report={"status":"pass","mutations":results}
    (args.artifacts/"mutation-audit.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report))


if __name__=="__main__":
    main()
