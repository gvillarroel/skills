#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Check visible shared-run warnings independently of saved route metadata."""

import argparse
import copy
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/usefulcharts-style/scripts'))
from audit_chart import AUDIT,check_source
from editorial_poster import EditorialPoster
from test_lineage_runs import crossed_brief


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=True);ns={'s':'http://www.w3.org/2000/svg'};ET.register_namespace('',ns['s'])
    automatic=crossed_brief();shared=copy.deepcopy(automatic)
    shared['edges'][0]['via']=[[200,430],[850,430]];shared['edges'][1]['via']=[[500,430],[1100,430]]
    crossing=copy.deepcopy(shared);crossing['edges'][1]['via']=[[500,470],[1100,470]]
    sibling=copy.deepcopy(automatic);sibling['nodes']=[n for n in sibling['nodes'] if n['id']!='c'];sibling['edges'][1]['source']='a'
    cases=[('automatic',automatic,False,False),('authored-shared',shared,True,False),('perpendicular-crossing',crossing,False,False),
           ('legitimate-siblings',sibling,False,False),('forged-route-metadata',shared,True,True)]
    results=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch();page=browser.new_page(viewport={'width':1400,'height':1000})
        for name,data,expected,forge in cases:
            svg,_=EditorialPoster(data).render()
            if forge:
                root=ET.fromstring(svg);element=root.find('s:metadata[@id="chart-data"]',ns);metadata=json.loads(element.text)
                metadata['routes']=[];metadata['crossings']=[];element.text=json.dumps(metadata);svg=ET.tostring(root,encoding='unicode')
            path=args.output/(name+'.svg');path.write_text(svg,encoding='utf-8')
            page.goto(path.resolve().as_uri());page.evaluate('document.fonts.ready');report=page.evaluate(AUDIT);check_source(report,data)
            warnings=[w for w in report['composition_warnings'] if w['type']=='unrelated-shared-run']
            result=dict(id=name,expected_warning=expected,warning_detected=bool(warnings),hard_findings=report['findings'],warnings=warnings)
            result['pass']=bool(warnings)==expected and not report['findings'];results.append(result)
            (args.output/(name+'.json')).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
            page.locator('svg').first.screenshot(path=str(args.output/(name+'.png')))
        browser.close()
    summary=dict(status='pass' if all(r['pass'] for r in results) else 'fail',cases=results,
        scope='Independent visible SVG command/transform inspection. Warnings do not establish aesthetic parity.')
    (args.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary))
    return summary['status']!='pass'


if __name__=='__main__':raise SystemExit(main())
