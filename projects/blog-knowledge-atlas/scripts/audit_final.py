#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2", "pypdf>=5,<7"]
# ///
"""Bind final checks to current artifacts and check the text-color palette."""
import hashlib
import json
from atlas_core import OUT, PAPER, INK, MUTED, COLORS, pale
from pypdf import PdfReader

def luminance(color):
    rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    return sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))

def contrast(a,b):
    x,y=sorted([luminance(a),luminance(b)])
    return (y+.05)/(x+.05)

if __name__=='__main__':
    color_checks=[dict(color=c,on_paper=contrast(c,PAPER),on_own_tint=contrast(c,pale(c))) for c in [INK,MUTED,*COLORS]]
    assert min(v for c in color_checks for k,v in c.items() if k!='color')>=4.5
    checks=[]
    for case in ['01-history','02-agent','03-evaluation']:
        result=json.loads((OUT/case/'checks.json').read_text())
        assert result['technical_pass']
        for extension in ['svg','pdf']:
            assert hashlib.sha256((OUT/case/('poster.'+extension)).read_bytes()).hexdigest()==result[extension+'_sha256']
        checks.append(result)
    gallery=json.loads((OUT/'reviews/gallery-audit.json').read_text())
    assert all(r['pass_status'] for r in gallery)
    combined=PdfReader(OUT/'blog-knowledge-atlas.pdf')
    assert len(combined.pages)==3
    links=sum(len(p.get('/Annots',[])) for p in combined.pages)
    assert links==130
    result=dict(status='pass',posters=3,records=sum(c['records'] for c in checks),image_placements=sum(c['illustrations'] for c in checks),calendar_dates=sum(c['dates'] for c in checks),pdf_source_links=links,minimum_checked_text_contrast=round(min(v for c in color_checks for k,v in c.items() if k!='color'),2),color_checks=color_checks,viewer_cases=sum(len(g['cases']) for g in gallery),combined_pdf_sha256=hashlib.sha256((OUT/'blog-knowledge-atlas.pdf').read_bytes()).hexdigest(),visual_review='visual-review.md',reference_density_parity='not established')
    (OUT/'reviews/final-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='color_checks'}))
