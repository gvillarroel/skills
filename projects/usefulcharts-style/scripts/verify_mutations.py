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
import re
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
    node=copy.deepcopy(original);metadata=node.find('.//s:metadata[@id="chart-data"]',ns)
    values=json.loads(metadata.text);values['data_sha256']='0'*64;metadata.text=json.dumps(values)
    mutations.append(('stale-source-revision',node,'source-revision-mismatch'))
    for role,field in [('date','date-label'),('caption','detail')]:
        if original.find(f'.//s:text[@data-content-role="{role}"]',ns) is not None:
            node=copy.deepcopy(original);text=node.find(f'.//s:text[@data-content-role="{role}"]',ns)
            text.text='Incorrect content'
            mutations.append((f'changed-{role}',node,f'source-{field}-missing'))
    if original.find('.//s:g[@data-event-id]/s:text',ns) is not None:
        node=copy.deepcopy(original);event_text=node.find('.//s:g[@data-event-id]/s:text',ns)
        edge=node.find('.//s:path[@data-edge-id]',ns)
        points=[float(value) for value in re.findall(r'-?\d+(?:\.\d+)?',edge.get('d'))]
        x=float(event_text.get('x'))+8;y=float(event_text.get('y'))-3
        edge.set('d',f'M {points[0]} {points[1]} L {x} {points[1]} L {x} {y} L {points[-2]} {y} L {points[-2]} {points[-1]}')
        mutations.append(('path-through-event-text',node,'edge-event-text-collision'))
        node=copy.deepcopy(original);event_art=node.find('.//s:g[@data-event-id]/s:svg[@data-artwork]',ns)
        if event_art is not None:
            edge=node.find('.//s:path[@data-edge-id]',ns)
            points=[float(value) for value in re.findall(r'-?\d+(?:\.\d+)?',edge.get('d'))]
            x=float(event_art.get('x'))+float(event_art.get('width'))/2
            y=float(event_art.get('y'))+float(event_art.get('height'))/2
            edge.set('d',f'M {points[0]} {points[1]} L {x} {points[1]} L {x} {y} L {points[-2]} {y} L {points[-2]} {points[-1]}')
            mutations.append(('path-through-event-art',node,'edge-event-illustration-collision'))
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
    node=copy.deepcopy(original);edge=node.find(".//s:path[@data-edge-id]",ns);tokens=edge.attrib["d"].split();x,y=float(tokens[1]),float(tokens[2])
    edge.set("d",f'M {x} {y} L {x} {y-12} L {x} {y} '+" ".join(tokens[3:]));edge.set("data-route-style","rounded")
    mutations.append(("source-reentry",node,"edge-node-collision"))
    if original.find('.//s:path[@data-transition-fill]',ns) is not None:
        node=copy.deepcopy(original);box=node.find('.//s:rect[@data-node-box]',ns)
        x,y,w,h=[float(box.attrib[k]) for k in ('x','y','width','height')]
        node.find('.//s:path[@data-transition-fill]',ns).set('d',f'M {x+1} {y+1} L {x+w-1} {y+1} L {x+w-1} {y+h-1} L {x+1} {y+h-1} Z')
        mutations.append(('filled-bridge-over-period',node,'transition-fill-node-collision'))
    if original.find('.//s:g[@data-event-id]',ns) is not None:
        node=copy.deepcopy(original);event=node.find('.//s:g[@data-event-id]',ns);event.set('data-origin-y',str(float(event.attrib['data-origin-y'])+50))
        mutations.append(('shifted-event-date-anchor',node,'event-time-mismatch'))
    if original.find('.//s:path[@data-era-rule]',ns) is not None:
        node=copy.deepcopy(original);rule=node.find('.//s:path[@data-era-rule]',ns)
        tokens=rule.attrib['d'].split();tokens[1]='45';rule.set('d',' '.join(tokens))
        mutations.append(('era-rule-over-year',node,'era-rule-text-collision'))
    if original.find('.//s:g[@data-event-id]/s:svg[@data-artwork]',ns) is not None:
        node=copy.deepcopy(original);art=node.find('.//s:g[@data-event-id]/s:svg[@data-artwork]',ns)
        box=node.find('.//s:rect[@data-node-box]',ns)
        art.set('x',box.attrib['x']);art.set('y',str(float(box.attrib['y'])+30))
        mutations.append(('illustration-over-period',node,'illustration-node-collision'))
        if original.find('.//s:path[@data-transition-fill]',ns) is not None:
            node=copy.deepcopy(original);art=node.find('.//s:g[@data-event-id]/s:svg[@data-artwork]',ns)
            x,y,w,h=[float(art.attrib[k]) for k in ('x','y','width','height')]
            node.find('.//s:path[@data-transition-fill]',ns).set('d',f'M {x+1} {y+1} L {x+w-1} {y+1} L {x+w-1} {y+h-1} L {x+1} {y+h-1} Z')
            mutations.append(('bridge-over-illustration',node,'transition-fill-illustration-collision'))
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
