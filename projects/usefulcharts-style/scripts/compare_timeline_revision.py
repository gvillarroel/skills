#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Compare exact chronology facts and equal-width reference/before/after views."""

import argparse
import json
import shutil
import statistics
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from playwright.sync_api import sync_playwright

NS={'s':'http://www.w3.org/2000/svg'}
SOURCE='skills/usefulcharts-style/assets/examples/usefulcharts-style/five-regional-histories'


def meaning(data):
    fields={'periods':('id','label','start','end','lane','group'),'transitions':('id','source','target','kind'),
        'events':('id','label','detail','year','lane','group')}
    return {**{key:sorted(tuple(item.get(field) for field in columns) for item in data[key]) for key,columns in fields.items()},
        'time':data['time'],'groups':data['groups'],'lanes':[{k:v for k,v in lane.items() if k!='weight'} for lane in data['lanes']]}


def metrics(raw):
    root=ET.fromstring(raw);events=root.findall('.//s:g[@data-event-id]',NS)
    areas=[];stems=0
    for node in root.findall('.//s:g[@data-node-id]',NS):
        body=node.find('s:rect[@data-node-box]',NS);stem=node.find('s:rect[@data-period-stem]',NS)
        if stem is None:areas.append(float(body.get('width'))*float(body.get('height')))
        else:
            label=node.find('s:rect[@data-period-label]',NS);stems+=1
            sw,sh=float(stem.get('width')),float(stem.get('height'))
            lw,lh=float(label.get('width')),float(label.get('height'))
            areas.append(sw*sh+(lw-sw)*lh)
    sizes=[float(e.find('s:text',NS).get('font-size')) for e in events]
    return dict(colored_period_area=sum(areas),area_method='Union of painted rectangular bounds; rounded corners excluded from the approximation.',duration_stems=stems,median_event_heading_size=statistics.median(sizes),
        illustrated_events=sum(any(element.get('data-artwork') for element in event.iter()) for event in events))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',default='47927dfb');parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();root=Path(__file__).resolve().parents[3];folder=args.output.resolve();folder.mkdir(parents=True,exist_ok=True)
    before={ext:subprocess.check_output(['git','show',f'{args.before}:{SOURCE}.{ext}'],cwd=root) for ext in ('json','svg')}
    after={ext:(root/f'{SOURCE}.{ext}').read_bytes() for ext in ('json','svg')}
    for name,values in [('before',before),('after',after)]:
        for ext,content in values.items():(folder/f'{name}.{ext}').write_bytes(content)
    old,new=json.loads(before['json']),json.loads(after['json']);assert meaning(old)==meaning(new),'Exact history changed.'
    first,last=metrics(before['svg']),metrics(after['svg'])
    sizes=lambda data:{key:{item['id']:(item.get('size'),item.get('detail_size')) for item in data[key]} for key in ('periods','events')}
    result=dict(status='pass',before_revision=args.before,exact_source_facts_preserved=True,periods=50,transitions=55,events=60,
        before=first,after=last,colored_area_change_percent=100*(last['colored_period_area']/first['colored_period_area']-1),
        all_type_sizes_preserved=sizes(old)==sizes(new),before_canvas=[old['width'],old['height']],after_canvas=[new['width'],new['height']],
        limitation='Area and typography measurements describe changes, not aesthetic similarity. All three pictures retain their natural aspect ratio at an equal display width.')
    (folder/'comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    reference=root/'projects/usefulcharts-style/artifacts/images/reference-history.png'
    page=folder/'index.html'
    page.write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Chronology composition critique</title><style>body{background:#eee9da;color:#252923;font:17px Arial;margin:24px}main{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}h1{font-size:30px}h2{font-size:17px}img{width:100%;height:auto;display:block}p{max-width:1200px;line-height:1.5}</style><h1>Chronology: reference, previous publication, revised composition</h1><p>Compare the balance of colored intervals and horizontal explanation, visual hierarchy, corridor clearance and illustration integration. The fictional study has fewer periods than the reference; matching the frame or passing geometry checks does not prove parity.</p><main><section><h2>UsefulCharts reference · private critique copy</h2><img src="'''+reference.as_uri()+'''"></section><section><h2>Previously published · '''+args.before+'''</h2><img src="before.svg"></section><section><h2>Revised chronology</h2><img src="after.svg"></section></main></html>''',encoding='utf-8')
    with sync_playwright() as p:
        browser=p.chromium.launch();tab=browser.new_page(viewport={'width':1800,'height':1100});tab.goto(page.as_uri())
        tab.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
        tab.screenshot(path=str(folder/'comparison.png'),full_page=True);browser.close()
    print(json.dumps(result))


if __name__=='__main__':main()
