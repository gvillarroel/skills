#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Export the source catalog, editable data, and a portable offline atlas package."""
from pathlib import Path
from collections import Counter
from html import escape
import csv
import io
import json
import shutil
import zipfile

PROJECT=Path(__file__).resolve().parents[1]
OUT=PROJECT/'artifacts'

def main():
    data=json.loads((PROJECT/'data/timeline.json').read_text(encoding='utf-8'))
    records=[dict(e,section=key) for key in ['events','origins','future','branches'] for e in data[key]]
    sources=data['sources']
    used=Counter(e['source'] for e in records)
    (OUT/'data').mkdir(exist_ok=True)
    shutil.copy2(PROJECT/'data/timeline.json',OUT/'data/timeline.json')
    shutil.copy2(PROJECT.parents[1]/'skills/usefulcharts-style/assets/fonts/OFL.txt',OUT/'documents/font-license.txt')
    fields=['id','section','year','date','lane','actor','kind','label','detail','credit','source','source_url']
    with (OUT/'data/timeline.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for e in records:writer.writerow({**e,'source_url':sources[e['source']]['url']})
    rows=[]
    for index,(key,source) in enumerate(sources.items(),1):
        anchors=[f"<li><b>{escape(e['date'])} — {escape(e['label'])}</b><br>{escape(e['credit'])}</li>" for e in records if e['source']==key]
        rows.append(f'<section id="source-{index}"><h2>[{index}] {escape(source["title"])}</h2><p><a href="{escape(source["url"],quote=True)}">{escape(source["url"])}</a></p><p class="muted">{source["type"]} · {used[key]} chart entries</p><ul>'+''.join(anchors)+'</ul></section>')
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Star Trek Atlas — Sources</title><style>body{font:16px/1.55 Arial,sans-serif;color:#24352f;background:#f7f3e8;max-width:980px;margin:auto;padding:35px}h1{font-size:38px;line-height:1.1}h2{font-size:21px;margin-bottom:8px}section{border-top:1px solid #b9beb0;padding:17px 0;break-inside:avoid}a{color:#215c80;overflow-wrap:anywhere}li{margin:8px 0}.muted{font-size:13px;color:#626d61}@media print{body{font-size:10pt;padding:0;background:white}h2{font-size:14pt}a{color:black}.nav{display:none}@page{margin:16mm}}</style><h1>Star Trek / Civilizations & Wars</h1><p>Source catalog for the 152-entry poster. Numbers match the episode credits on the SVG, PNG and PDF. Compiled 12 September 2026.</p><p class="nav"><a href="../viewer/index.html">Open the interactive atlas</a> · <a href="star-trek-timeline.pdf">Poster PDF</a> · <a href="../data/timeline.json">Editable JSON</a> · <a href="../data/timeline.csv">CSV</a></p><p>On-screen works are the primary narrative anchors. StarTrek.com supplies official summaries; Memory Alpha is a secondary index used for episode attribution and chronology. Only its screen-history passages were used, excluding apocryphal novels, games and speculative continuations. Broad reference entries and more specific episode sources have different levels of precision; uncertain dates are marked on the chart.</p>'''+''.join(rows)+'</html>'
    html=html.replace('152-entry',f'{len(records)}-entry')
    (OUT/'documents/sources.html').write_text(html,encoding='utf-8')
    viewer=OUT/'viewer/index.html'
    content=viewer.read_text(encoding='utf-8')
    if 'Numbered source catalog' not in content:
        content=content.replace('</aside>', '<p class="small"><a href="../documents/sources.html" target="_blank">Numbered source catalog ↗</a><br><a href="../data/timeline.json" download>Editable JSON</a> · <a href="../data/timeline.csv" download>CSV</a></p></aside>')
    content=content.replace('Jump to era…','Jump to section…').replace('aria-label="Jump to era"','aria-label="Jump to section"')
    content=content.replace("setScale(.40);viewport.scrollTop=r.y*scale;viewport.scrollLeft=0;", "setScale(r.x === undefined ? 0.4 : 0.62);viewport.scrollTop=r.y*scale;viewport.scrollLeft=Math.max(0,(r.x||0)*scale-40);")
    viewer.write_text(content,encoding='utf-8')
    portable=[OUT/'viewer/index.html',OUT/'svgs/star-trek-timeline.svg',OUT/'images/star-trek-timeline.png',OUT/'images/star-trek-preview.png',OUT/'documents/star-trek-timeline.pdf',OUT/'documents/sources.html',OUT/'data/timeline.json',OUT/'data/timeline.csv']
    portable.append(OUT/'documents/font-license.txt')
    if (OUT/'reviews/review.md').exists():portable.append(OUT/'reviews/review.md')
    with zipfile.ZipFile(OUT/'star-trek-atlas.zip','w',zipfile.ZIP_DEFLATED) as bundle:
        for path in portable:bundle.write(path,path.relative_to(OUT))
    print(json.dumps(dict(records=len(records),cited_sources=len(used),catalog_sources=len(sources),actors=sorted({e.get('actor') for e in records if e.get('actor')}),bundle=str(OUT/'star-trek-atlas.zip'))))

if __name__=='__main__':main()
