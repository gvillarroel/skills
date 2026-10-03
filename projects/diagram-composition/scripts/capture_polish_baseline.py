#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render known visual defects against a supplied frozen skill implementation."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skill-root", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    scripts = args.skill_root.resolve()/"scripts"
    cases = {
        "line-inside-card": ('#f5f7f9', '<g data-relation-id="intrusion"><path d="M5 75H180" fill="none" stroke="#555d66" stroke-width="2"/></g>', ''),
        "conflicting-fill": ('#e99a88', '', ''),
        "covered-accent": ('#f5f7f9', '', '<rect x="38" y="48" width="264" height="124" fill="#ffffff"/>'),
        "low-contrast-label": ('#f5f7f9', '', ''),
        "floating-terminal": ('#f5f7f9', '<path d="M5 100H34" fill="none" stroke="#555d66" stroke-width="2" data-connector="native" data-open-start="Upstream input" data-to-node="source"/>', ''),
    }
    records = []
    for name, (fill, wire, cover) in cases.items():
        target = args.output/name
        target.mkdir(exist_ok=True)
        text_color = '#cbd3da' if name=='low-contrast-label' else '#26323d'
        (target/'panel.svg').write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240">'
            f'<rect x="40" y="50" width="260" height="120" rx="6" fill="{fill}" stroke="#276bc8" stroke-width="2.4" '
            'data-node-id="source" data-concept-id="source" data-color-concept="source" data-color-channel="stroke"/>'
            f'{cover}<text x="65" y="120" font-size="20" fill="{text_color}">Shared source</text>{wire}</svg>', encoding='utf-8')
        spec = {"version":1,"title":"Visual quality control","thesis":"A supplied defect must be detected.",
            "canvas":{"width":500,"height":400,"displayWidth":500,"minTextPx":14,"margin":20,"gap":20,"titleHeight":50,"footerHeight":20},
            "grid":{"columns":[1],"rows":[1]},"concepts":[{"id":"source","label":"Shared source","color":"#276bc8"}],
            "panels":[{"id":"view","title":"Shared source","question":"Which object?","claim":"A single source object.",
                "family":"boundary","reason":"One object boundary.","alternative":"No process is supplied.",
                "concepts":["source"],"source":"panel.svg","span":{"row":1,"column":1,"rows":1,"columns":1},"ports":{}}]}
        (target/'plan.json').write_text(json.dumps(spec,indent=2),encoding='utf-8')
        commands = [
            ['uv','run','--script',str(scripts/'compose_diagram.py'),'compose','--spec',str(target/'plan.json'),'--output',str(target/'figure.svg'),'--report',str(target/'report.json'),'--overwrite'],
            ['uv','run','--script',str(scripts/'audit_diagram.py'),'audit','--input',str(target/'figure.svg'),'--report',str(target/'audit.json'),'--screenshot',str(target/'preview.png'),'--inspect','--overwrite']]
        for command in commands:
            subprocess.run(command, check=True, capture_output=True, text=True)
        audit=json.loads((target/'audit.json').read_text(encoding='utf-8'))
        records.append({'case':name,'auditPassed':audit['ok'],'issues':audit['issues']})
    (args.output/'results.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(records))


if __name__=='__main__':
    main()
