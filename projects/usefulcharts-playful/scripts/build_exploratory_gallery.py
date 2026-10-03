#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package the third revision without replacing the earlier illustrated gallery."""
import html
import json
import shutil
import zipfile
from build_gallery import ROOT,OUT,CASES,VIEWER,records

def main():
    gallery=OUT/'gallery-r3';gallery.mkdir(parents=True,exist_ok=True);cards=[]
    checks=json.loads((OUT/'revision-3/verification.json').read_text(encoding='utf-8'))
    rows='\n'.join(f'| [{c["case"]}]({c["case"]}/poster.pdf) | {c["records"]} | {c["illustrations"]} | {c["area_change_percent"]:+.2f}% |' for c in checks)
    review='''# Five illustrated posters: revision 3

The evaluator and all five posters have been revised. Every selected source record and its complete notes remain: 384 records, 51 placed subject images and 384 clickable PDF source annotations. The files are oversized single-page posters intended for zooming or large-format printing.

| PDF | Records | Subject images | Area change from the previous illustrated revision |
| --- | ---: | ---: | ---: |
'''+rows+'''

Area changes compare each poster only with its own previous canvas. They do not establish knowledge-density parity with UsefulCharts. Three posters grow; the instrument and spacecraft compositions are smaller.

## What changed

- Instruments: a shared classification entrance, local discovery questions, exact category codes beside specimens and short colored leaf-to-image connections.
- BSD: all 51 typed relationships in one connected lineage, with separately identifiable code contributions and release-specific illustrative hardware captions.
- Mars: larger spacecraft in available calendar pockets; 52 exact X date marks and six separate orbiter/lander operation spans; direct ownership routes and a shared Mars 2/3 model.
- Star Trek spacecraft: 79 physical hulls and 90 state fragments, 157 exact X date marks, 21 reusable tracks and 13 larger locally bound views. A name reused by another hull is not treated as continuous operation by the first ship.
- Star Trek civilizations: 155 records, repeated numerical calendar strips, explicit approximate/retrospective anchors, inline subject images and a Dominion War coalition comparison in previously unused space.

## What the evaluator now requires

Information preservation, technical correctness, illustrated coverage, exploratory composition and the reference target are separate outcomes. The exploration check requires at least three source-answerable reading routes, two operations and two body regions, visible image ownership and no material unresolved composition defect. Hashes and stable SVG IDs bind the evidence to the actual artifacts; they cannot prove visual truth. Comparison reviews must identify exact images and visible titles before choosing a candidate, preventing mislabeled votes.

The two instrument/BSD feedback cohorts retained disagreement. The first favored the previous instrument panels; after visible codes and local connections were added, all three raw second-cohort instrument reviews favored the repaired tree (two also passed strict execution). Two BSD reviews mixed up candidate identities and were invalidated, rather than reinterpreted as favorable votes. A targeted labeled-image cohort then passed strict execution and correct identity binding in all three runs; each preferred the repaired connected BSD. That result is limited to this pair. One review still made an unsupported comparative-density statement, which was retained as a defect. No reviewer preference establishes reference-density parity or blind indistinguishability.

## Honest acceptance boundary

All five pass independent source, geometry and PDF checks. Instruments, BSD and spacecraft pass the narrower authored exploratory review. Mars still has a large quiet lower calendar and long picture routes. The civilization poster still reads predominantly as a repeated story matrix despite its useful coalition inset. Those two compositions remain unaccepted by the stricter visual evaluator.

None is certified indistinguishable from UsefulCharts. The full matched semantic reference-density census is still pending. Technical passes do not cancel these visual limitations.

## Files and evidence

Open the gallery at `../gallery-r3/index.html`, or each case's `poster.html`. The viewers work offline and offer search, source links, zoom and comparison against the previous illustrated version. Each folder includes the PDF, editable SVG, PNG and selected source inventory. The full archive also retains the geometry verification and authored visual review evidence. `verification.json` collects the five independent artifact checks.

All final SVG whole/detail views and actual PDF render previews were inspected. Numerical time is preserved for Mars and spacecraft. Dates absent from the source are not invented; approximate, retrospective, future and alternative-history wording remains explicit. Illustrative hardware and design-family images are qualified, and this iteration reuses existing inspected raster assets.
'''
    (OUT/'revision-3/review.md').write_text(review,encoding='utf-8')
    for original in CASES:
        c=dict(original);case=c['id'];path=OUT/'revision-3'/case;verification=json.loads((path/'verification.json').read_text());c['meta']=f'{verification["records"]} records · {verification["illustrations"]} subject images'
        if case=='starships':c['meta']+=' · 157 date marks · 21 shared tracks'
        if case=='civilizations':c['description']='Read the illustrated story bands and their repeated calendar; compare the changing powers through their complete notes.'
        shutil.copy2(OUT/'revision-2'/case/'preview.png',path/'before.png')
        data=json.loads((path/'source.json').read_text(encoding='utf-8'));svg=(path/'poster.svg').read_text(encoding='utf-8');viewer=VIEWER.replace('../../gallery/index.html','../../gallery-r3/index.html').replace('Previous text-focused composition','Previous illustrated composition')
        substitutions={'TITLE':html.escape(c['title']),'META':html.escape(c['meta']),'DESCRIPTION':html.escape(c['description']),'QUESTS':''.join(f'<button data-focus="{i}">{html.escape(t)} →</button>' for t,i in c['challenge']),'SVG':svg,'RECORDS':json.dumps(records(data),ensure_ascii=False).replace('</',r'<\/')}
        for key,value in substitutions.items():viewer=viewer.replace('__'+key+'__',value)
        (path/'poster.html').write_text(viewer,encoding='utf-8')
        cards.append(f'<article data-diagram-id="{case}"><a class="image" href="../revision-3/{case}/poster.html"><img src="../revision-3/{case}/preview.png" alt="{html.escape(c["title"])}"></a><div class="body"><small>{c["meta"]}</small><h2>{html.escape(c["title"])}</h2><p>{html.escape(c["description"])}</p><nav><a href="../revision-3/{case}/poster.html">Explore & compare</a><a href="../revision-3/{case}/poster.pdf">PDF</a><a href="../revision-3/{case}/poster.svg">SVG</a></nav></div></article>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Five illustrated diagrams · revision 3</title><style>*{box-sizing:border-box}body{margin:0;background:#F7F2E8;color:#243843;font:17px system-ui}header{padding:50px 6vw;background:#102637;color:#e8f1ed}h1{font-size:clamp(34px,4.4vw,68px);max-width:1100px;line-height:1.05}p{line-height:1.6;max-width:1100px}main{padding:35px 6vw;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:28px}article{border:1px solid #c9cbbf;border-radius:14px;overflow:hidden;background:#fffaf1}.image{display:block;height:355px;background:#112737}.image img{width:100%;height:100%;object-fit:cover;object-position:top}.body{padding:24px}h2{font-size:27px;margin:12px 0}small{color:#536975}a{color:#165772}nav{display:flex;gap:22px;flex-wrap:wrap;font-weight:650}footer{padding:20px 6vw 60px}footer a{margin-right:20px}@media(max-width:750px){main{grid-template-columns:1fr;padding:24px 16px}.image{height:310px}header{padding:32px 22px}}</style><header><small style="color:#d9c996">REVISION 3 · VISUAL EXPLORATION</small><h1>Follow the picture.<br>Follow the relationship.</h1><p>Five revised posters retain all 384 selected records and their full notes. Images belong to categories, releases, missions or spacecraft. Open a poster to search, zoom, inspect sources and compare the previous illustrated version.</p></header><main>'''+''.join(cards)+'''</main><footer><p>The evaluator separates illustrated coverage, exploratory composition and the reference target. The reference density census and indistinguishability remain unverified. The chronology story bands still have a regular editorial structure; technical preservation is not proof of aesthetic parity.</p><a href="../exploratory-diagrams.zip">Download the five posters</a><a href="../revision-3/review.md">Read the evaluation</a><a href="../gallery/index.html">Previous illustrated gallery</a></footer></html>'''
    (gallery/'index.html').write_text(page,encoding='utf-8')
    with zipfile.ZipFile(OUT/'exploratory-diagrams.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        z.writestr('gallery-r3/index.html',page.replace('<a href="../exploratory-diagrams.zip">Download the five posters</a>','').replace('<a href="../gallery/index.html">Previous illustrated gallery</a>',''))
        for c in CASES:
            for name in ['poster.html','poster.svg','poster.pdf','poster.png','preview.png','before.png','source.json','art-map.json','verification.json','illustrated-review.json','exploration-review.json','exploration-assessment.json','route-1.png','route-2.png','route-3.png']:
                path=OUT/'revision-3'/c['id']/name;z.write(path,str(path.relative_to(OUT)))
        for name in ['review.md','verification.json']:
            path=OUT/'revision-3'/name
            if path.exists():z.write(path,str(path.relative_to(OUT)))
    with zipfile.ZipFile(OUT/'exploratory-posters-pdf.zip','w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for c in CASES:z.write(OUT/'revision-3'/c['id']/'poster.pdf',c['id']+'.pdf')
    print(json.dumps(dict(diagrams=5,archive_bytes=(OUT/'exploratory-diagrams.zip').stat().st_size)))
if __name__=='__main__':main()
