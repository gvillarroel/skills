#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pypdf>=5,<7"]
# ///
"""Build an offline zoom/search reader and the three-page PDF collection."""
from pathlib import Path
import json
import zipfile
from pypdf import PdfReader, PdfWriter

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'
CASES=['01-history','02-agent','03-evaluation']

CSS='''
:root{color-scheme:light;--paper:#f7f2e8;--ink:#20343b;--muted:#526369;--accent:#267a7b}*{box-sizing:border-box}
body{margin:0;background:#dfd9cc;color:var(--ink);font:15px/1.5 system-ui,sans-serif}button,input,select{font:inherit}button,a{touch-action:manipulation}button{cursor:pointer}
header{background:var(--paper);padding:15px 22px 12px;border-bottom:1px solid #b8b4a9}h1{margin:0;font-size:25px;letter-spacing:-.5px}header p{margin:3px 0 10px;color:var(--muted)}nav,.tools{display:flex;gap:9px;align-items:center;flex-wrap:wrap}nav{margin:11px 0}
button,.download{border:1px solid #acb4ae;background:#fffaf0;color:var(--ink);padding:7px 12px;border-radius:5px;text-decoration:none}button[aria-selected=true]{background:var(--ink);color:white;border-color:var(--ink)}button:hover,.download:hover{border-color:var(--accent)}
.tools{font-size:14px}input[type=search]{width:240px;max-width:60vw;padding:8px;border:1px solid #a1aaa5;border-radius:5px}input[type=range]{width:125px}#zoom-label{font-variant-numeric:tabular-nums;min-width:44px}.quiet{color:var(--muted)}
.workspace{display:grid;grid-template-columns:minmax(0,1fr) 320px;height:calc(100vh - 218px);min-height:400px}#viewport{overflow:auto;overscroll-behavior:contain;padding:16px;outline:none}#canvas{width:max-content;box-shadow:0 2px 15px #22333b26}#canvas>svg{display:block;height:auto;background:var(--paper)}
aside{overflow:auto;border-left:1px solid #b8b4a9;background:var(--paper);padding:19px}aside h2{font-size:22px;line-height:1.15;margin:0 0 12px}aside p{white-space:pre-line}aside a{color:#17636c;overflow-wrap:anywhere}#hits{display:grid;gap:7px}#hits button{text-align:left}small{font-size:12px;color:var(--muted)}[data-record-id]:focus{outline:none}[data-record-id]:hover{filter:drop-shadow(0 0 2px #14767b55)}#selection-frame{fill:#fff4c822;stroke:#9a6b22;stroke-width:4;pointer-events:none}
footer{background:var(--paper);border-top:1px solid #b8b4a9;padding:9px 22px;font-size:12px;color:var(--muted)}:focus-visible{outline:3px solid #c27636;outline-offset:3px}
@media(max-width:760px){header{padding:10px 12px}h1{font-size:21px}.workspace{display:block;height:auto;min-height:0}#viewport{height:65vh;padding:8px}aside{border-left:0;border-top:1px solid #b8b4a9;max-height:45vh}nav{gap:5px}nav button{padding:6px 8px;font-size:12px}.tools{gap:6px}header p{font-size:13px}footer{padding:10px 12px}}
'''

JS=r'''
const data=JSON.parse(document.querySelector('#atlas-data').textContent);
const view=document.querySelector('#viewport'), canvas=document.querySelector('#canvas');
let current=data[0],scale=1,selected=null,matching=[],matchIndex=0;
const $=s=>document.querySelector(s);
function zoom(value){scale=Math.max(.02,Math.min(2,value));canvas.querySelector('svg').style.width=(current.canvas[0]*scale)+'px';$('#zoom').value=Math.round(scale*100);$('#zoom-label').textContent=Math.round(scale*100)+'%';}
function fit(){zoom((view.clientWidth-40)/current.canvas[0]);view.scrollTo(0,0)}
function showRecord(id,move=true){const r=current.records.find(r=>r.id===id);if(!r)return;selected=r;$('#selection-frame')?.remove();const rect=document.createElementNS('http://www.w3.org/2000/svg','rect');Object.entries({id:'selection-frame',x:r.x-7,y:r.y-7,width:r.w+14,height:r.h+14,rx:4}).forEach(([k,v])=>rect.setAttribute(k,v));canvas.querySelector('svg').append(rect);
$('#record-title').textContent=r.title;$('#record-detail').textContent=(r.kicker?r.kicker+'\n\n':'')+r.detail;$('#source').hidden=false;$('#source').href=r.url;$('#source').textContent='Open this record’s source ↗';$('#provenance').textContent=r.source+(r.source_line?' · source line '+r.source_line:'')+' · '+r.id;
if(move){zoom(Math.max(scale,.9));view.scrollTo({left:Math.max(0,(r.x+r.w/2)*scale-view.clientWidth/2),top:Math.max(0,(r.y+r.h/2)*scale-view.clientHeight/2),behavior:'instant'});}history.replaceState(null,'','#'+current.case+'/'+r.id);}
function loadCase(key,autofit=true){current=data.find(d=>d.case===key)||data[0];selected=null;canvas.replaceChildren(document.querySelector('#svg-'+current.case).content.cloneNode(true));$('#poster-name').textContent=current.title;$('#record-title').textContent='Explore the poster';$('#record-detail').textContent='Select any record to read its complete note and open its source. Use Fit to see the structure; use Read or a search result for readable type.';$('#source').hidden=true;$('#provenance').textContent=current.records.length+' source-linked records · '+current.images.length+' illustration placements';$('#download-pdf').href=current.case+'/poster.pdf';$('#download-svg').href=current.case+'/poster.svg';document.querySelectorAll('nav button').forEach(b=>b.setAttribute('aria-selected',b.dataset.case===current.case));
canvas.querySelectorAll('[data-record-id]').forEach(g=>{g.setAttribute('tabindex','0');g.setAttribute('role','button');g.addEventListener('click',()=>showRecord(g.dataset.recordId,false));g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();showRecord(g.dataset.recordId,false)}})});
current.images.forEach(im=>{const hit=document.createElementNS('http://www.w3.org/2000/svg','rect');Object.entries({class:'art-hit',x:im.x,y:im.y,width:im.w,height:im.h,fill:'transparent','pointer-events':'all',tabindex:0,role:'button','aria-label':im.caption,'data-owner':im.owner,style:'cursor:pointer'}).forEach(([k,v])=>hit.setAttribute(k,v));hit.addEventListener('click',()=>showRecord(im.owner,false));hit.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();showRecord(im.owner,false)}});canvas.querySelector('svg').append(hit)});
$('#query').value='';$('#hits').replaceChildren();$('#result-count').textContent='';if(autofit)fit();history.replaceState(null,'','#'+current.case);}
function search(){const query=$('#query').value.trim().toLowerCase();matching=query?current.records.filter(r=>(r.title+' '+r.detail+' '+(r.kicker||'')).toLowerCase().includes(query)):[];matchIndex=0;$('#result-count').textContent=query?matching.length+' matches':'';$('#hits').replaceChildren();matching.forEach(r=>{const b=document.createElement('button');b.type='button';b.textContent=r.title;b.addEventListener('click',()=>showRecord(r.id));$('#hits').append(b)});if(matching.length)showRecord(matching[0].id);}
document.querySelectorAll('nav button').forEach(b=>b.addEventListener('click',()=>loadCase(b.dataset.case)));
$('#fit').addEventListener('click',fit);$('#read').addEventListener('click',()=>{zoom(1);if(selected)showRecord(selected.id)});$('#plus').addEventListener('click',()=>zoom(scale*1.3));$('#minus').addEventListener('click',()=>zoom(scale/1.3));$('#zoom').addEventListener('input',e=>zoom(+e.target.value/100));$('#query').addEventListener('input',search);$('#next').addEventListener('click',()=>{if(matching.length)showRecord(matching[++matchIndex%matching.length].id)});
const [initial,record]=location.hash.slice(1).split('/');loadCase(initial);if(record)showRecord(record);
'''


def main():
    manifests=[json.loads((OUT/c/'manifest.json').read_text(encoding='utf-8')) for c in CASES]
    collection=PdfWriter()
    for m in manifests:
        check=json.loads((OUT/m['case']/'checks.json').read_text())
        assert check['technical_pass'], m['case']+' has unresolved technical defects'
        collection.append(OUT/m['case']/'poster.pdf',outline_item=m['title'])
    collection.add_metadata({'/Title':'The Blog Knowledge Atlas','/Author':'Source texts: Guillermo Villarroel and Gerardo Villarroel','/Subject':'Three illustrated, source-linked educational posters'})
    with (OUT/'blog-knowledge-atlas.pdf').open('wb') as f:collection.write(f)
    reader=PdfReader(OUT/'blog-knowledge-atlas.pdf')
    assert len(reader.pages)==3
    assert sum(len(p.get('/Annots',[])) for p in reader.pages)==130
    nav=''.join(f'<button role="tab" data-case="{m["case"]}" aria-selected="false">{i+1:02d} · {label}</button>' for i,(m,label) in enumerate(zip(manifests,['Architecture history','Inside an agent','Skill evolution'])))
    templates=''.join('<template id="svg-'+m['case']+'">'+(OUT/m['case']/'poster.svg').read_text(encoding='utf-8')+'</template>' for m in manifests)
    small_data=[{k:m[k] for k in ['case','title','canvas','records','images']} for m in manifests]
    html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Blog Knowledge Atlas</title><style>'''+CSS+'''</style><header><h1>The Blog Knowledge Atlas</h1><p>Three illustrated maps of the public material in ~/dev/blog. Select a record for its note and source.</p><nav role="tablist" aria-label="Posters">'''+nav+'''</nav><div class="tools"><button id="fit">Fit</button><button id="read">Read · 100%</button><button id="minus" aria-label="Zoom out">−</button><input id="zoom" aria-label="Zoom" type="range" min="2" max="200" value="100"><button id="plus" aria-label="Zoom in">+</button><span id="zoom-label"></span><input id="query" type="search" placeholder="Find a concept or year…" aria-label="Search records"><button id="next">Next match</button><span id="result-count" role="status"></span><a class="download" id="download-pdf" download>Poster PDF</a><a class="download" id="download-svg" download>Editable SVG</a><a class="download" href="blog-knowledge-atlas.pdf" download>All 3 · PDF</a></div></header><main class="workspace"><div id="viewport" tabindex="0" aria-label="Scrollable poster canvas"><div id="canvas"></div></div><aside aria-label="Selected record"><small id="poster-name"></small><h2 id="record-title"></h2><p id="record-detail"></p><a id="source" href="#" target="_blank" rel="noopener noreferrer" hidden></a><p><small id="provenance"></small></p><div id="hits" aria-label="Search results"></div></aside></main><footer>Text, dates and routes remain vector-editable. Conceptual illustrations do not depict documented historical hardware. The framework selection is an August 2026 snapshot. For print: A0 is suitable for the timeline; A1 for the two mechanism posters. <a href="reviews/visual-review.md">Review notes</a> · <a href="data/sources.json">Source inventory</a></footer>'''+templates+'<script type="application/json" id="atlas-data">'+json.dumps(small_data,ensure_ascii=False).replace('<','\\u003c')+'</script><script>'+JS+'</script></html>'
    (OUT/'index.html').write_text(html,encoding='utf-8')
    with zipfile.ZipFile(OUT/'blog-knowledge-atlas.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        keep=[OUT/'index.html',OUT/'blog-knowledge-atlas.pdf',OUT/'reviews/visual-review.md',OUT/'images/provenance.json',OUT/'images/specimen-sheet.png']
        keep.extend((OUT/'reviews').glob('*.json'))
        keep.extend((OUT/'data').glob('*.json'))
        for case in CASES:
            keep.extend(OUT/case/name for name in ['poster.pdf','poster.svg','preview.png','detail.png','manifest.json','checks.json'])
        for f in keep:
            if f.exists():z.write(f,f.relative_to(OUT).as_posix())
    print(json.dumps(dict(posters=3,pdf_pages=len(reader.pages),records=130,pdf_source_links=130,illustration_placements=sum(len(m['images']) for m in manifests),gallery_bytes=(OUT/'index.html').stat().st_size,package_bytes=(OUT/'blog-knowledge-atlas.zip').stat().st_size)))


if __name__=='__main__':main()
