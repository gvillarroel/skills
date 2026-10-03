#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build an offline comparison gallery and a compact deliverable archive."""
from pathlib import Path
import html
import json
import zipfile

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts'
CASES=[
 dict(id='bsd',name='UNIX and the BSD family',before='baseline/bsd',
      failure='The branching renderer passed geometry, but a long central chain wasted most of the width.',
      repair='47 records and 51 typed relationships now occupy balanced family panels. Short dates share a line with names; 11 paired references retain links between families.',
      limit='Following a distant path requires a numbered lookup. This is a compact reference guide, not a continuous family-tree poster.',
      source='https://cgit.freebsd.org/src/tree/share/misc/bsd-family-tree'),
 dict(id='instruments',name='How instruments make sound',before='revision-1/instruments',
      failure='The initial 71-record tree exceeded the canvas limit. The first printable outline, shown here as Before, still wasted lines and left a large blank column tail.',
      repair='71 categories and 66 connections remain visible. Codes sit beside names, family heights are balanced, and the reading guide occupies the released pocket.',
      limit='This is a selection from MIMO 2011. Deeper subdivisions are omitted; electrical subcategories are less detailed than several acoustic branches.',
      source='https://biblio.ugent.be/publication/01HN30DTX2BZYYEVXRG7Q7M06Q'),
 dict(id='mars',name='The long road to Mars',before='baseline/mars',
      failure='Separate program tracks and a short x scale stacked neighboring launches into 15 rows. A tidy geometry report hid a weak full-page composition.',
      repair='32 launch campaigns share 9 tracks, including 5 tracks reused across programs. All 52 event marks keep a uniform calendar x; 6 component intervals retain their distinct endpoints.',
      limit='The final page remains unevenly occupied. It is a useful chronology prototype, not an accepted reference-density or aesthetic-parity result.',
      source='https://mars.nasa.gov/system/downloadable_items/45585_mars_2020_landing_press_kit.pdf'),
]

def main():
    cards=[];metrics=[]
    checks={r['case']:r for r in json.loads((OUT/'reviews/independent-checks.json').read_text())}
    for c in CASES:
        a=json.loads((OUT/c['before']/'browser.json').read_text());b=checks[c['id']]
        area_a=a['canvas'][0]*a['canvas'][1];area_b=b['canvas'][0]*b['canvas'][1]
        reduction=100*(1-area_b/area_a)
        metrics.append(dict(case=c['id'],before_canvas=a['canvas'],after_canvas=b['canvas'],area_reduction_percent=reduction,inventory_retained=True,reference_density='pending',visual_parity='unproven'))
        before=c['before'];after='revision-2/'+c['id']
        cards.append(f'''<section id="{c['id']}" class="case"><div class="case-head"><div><p class="eyebrow">{c['id'].upper()} / DESIGN STUDY</p><h2>{c['name']}</h2></div><div class="measure"><strong>{reduction:.1f}%</strong><span>less total canvas area</span></div></div>
<div class="comparison"><article><h3>Before</h3><a href="{before}/poster.html"><img src="{before}/poster.png" alt="Earlier {html.escape(c['name'])} composition" loading="lazy"></a><p>{c['failure']}</p></article><article><h3>After</h3><a href="{after}/poster.html"><img src="{after}/poster.png" alt="Revised {html.escape(c['name'])} composition" loading="lazy"></a><p>{c['repair']}</p></article></div>
<p class="limit">Still open: {c['limit']}</p><nav><a class="button" href="{after}/poster.html">Explore full detail</a><a href="{after}/poster.pdf">PDF</a><a href="{after}/poster.svg">Editable SVG</a><a href="{after}/source.json">Source data</a><a href="{c['source']}">Primary source</a></nav></section>''')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Three diagram studies · critique and repair</title><style>
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f7f2e8;color:#192f39;font:17px/1.55 Arial,sans-serif}header{padding:50px max(5vw,24px);background:#192f39;color:white}h1{font-size:clamp(34px,4vw,62px);line-height:1.05;max-width:1000px;margin:8px 0 25px}header p{max-width:960px;color:#dce7e5}.eyebrow{font-size:12px;font-weight:700;letter-spacing:2px}header nav a{color:#ffe0a0}nav{display:flex;gap:24px;align-items:center;flex-wrap:wrap}main{max-width:1440px;margin:auto;padding:20px 28px 60px}.case{padding:42px 0;border-bottom:1px solid #c1c9c3}.case-head{display:flex;gap:30px;justify-content:space-between;align-items:center}h2{font-size:30px;line-height:1.2;margin-top:0}.measure{display:flex;flex-direction:column;text-align:right;white-space:nowrap}.measure strong{font-size:36px}.measure span{font-size:13px}.comparison{display:grid;grid-template-columns:1fr 1fr;gap:25px}.comparison article{min-width:0}.comparison img{display:block;width:100%;height:540px;object-fit:contain;background:#e2e1d8;border:1px solid #c1c9c3}.comparison a:hover img{border-color:#192f39}.limit{border-left:4px solid #8a4935;padding:12px 20px;background:#ebe6db}a{color:#305b71;text-underline-offset:3px}.button{background:#192f39;color:white;padding:10px 18px;border-radius:4px;text-decoration:none}footer{padding-top:30px;color:#4e6268;font-size:14px}@media(max-width:720px){.comparison{grid-template-columns:1fr}.comparison img{height:430px}.case-head{align-items:flex-start}.measure strong{font-size:25px}.measure span{white-space:normal;max-width:100px}nav{gap:14px}}
</style><header><p class="eyebrow">USEFULCHARTS-STYLE / CROSS-DOMAIN CRITIQUE</p><h1>Better use of space starts with a different arrangement.</h1><p>Three sourced subjects test long release chains, unequal classification branches, and historical missions. Every comparison retains the selected records. Technical checks and visible improvements are reported separately from the still-unproven reference-density and stylistic-parity requirements.</p><nav><a href="#bsd">BSD</a><a href="#instruments">Instruments</a><a href="#mars">Mars</a><a data-download href="diagram-studies.zip">Download all final files</a></nav></header><main>'''+''.join(cards)+'''<footer>All final SVGs are editable and self-contained. PDFs retain selectable text. HTML viewers support zoom and offline use; paired references in the BSD viewer can be followed in both directions. Full-source snapshots and rejected experiments are retained in the local project, outside the distribution ZIP.</footer></main><script>document.querySelector('[data-download]').hidden=location.protocol==='file:';</script></html>'''
    (OUT/'index.html').write_text(page,encoding='utf-8');(OUT/'reviews/comparison-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(OUT/'diagram-studies.zip','w',zipfile.ZIP_DEFLATED) as z:
        z.write(OUT/'index.html','index.html')
        for folder in [OUT/'revision-2'/c['id'] for c in CASES]:
            for file in sorted(folder.iterdir()):
                if file.suffix in ['.json','.html','.svg','.png','.pdf']:z.write(file,file.relative_to(OUT))
        for c in CASES:
            for name in ['poster.png','poster.html','poster.svg']:
                file=OUT/c['before']/name;z.write(file,file.relative_to(OUT))
        for name in ['independent-checks.json','comparison-metrics.json']:z.write(OUT/'reviews'/name,'reviews/'+name)
        z.write(ROOT.parents[1]/'skills/usefulcharts-style/assets/fonts/OFL.txt','licenses/Barlow-OFL.txt')
    print(json.dumps(dict(gallery=str(OUT/'index.html'),zip_bytes=(OUT/'diagram-studies.zip').stat().st_size,comparisons=metrics)))

if __name__=='__main__':main()
