#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "Pillow>=11,<13"]
# ///
"""Qualify marker projection against actual browser pixels and adverse backing cases."""
import io,json
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright
from arrow_quality import ARROW_AUDIT
OUT=Path(__file__).resolve().parents[1]/'artifacts/projection';OUT.mkdir(parents=True,exist_ok=True)
cases=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True);page=browser.new_page(viewport={'width':500,'height':220})
    for units in ['userSpaceOnUse','strokeWidth']:
        svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 220" width="500" height="220"><rect width="500" height="220" fill="#ffffff"/><g transform="translate(20 40) scale(1.2)"><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="10" markerHeight="10" markerUnits="{units}" orient="auto"><path d="M1 1L9 5L1 9Z" fill="context-stroke"/></marker></defs><path d="M20 40H180" fill="none" stroke="#696969" stroke-width="4" marker-end="url(#arrow)"/></g></svg>'''
        page.set_content('<html><body style="margin:0">'+svg+'</body></html>')
        r=page.evaluate(ARROW_AUDIT,{})
        assert not r['issues'],r
        unit=4 if units=='strokeWidth' else 1
        centroid=(round(236-8*unit*1.2*2/3),88)
        png=page.screenshot();pixel=Image.open(io.BytesIO(png)).convert('RGB').getpixel(centroid)
        assert max(abs(v-105) for v in pixel)<=1,(units,centroid,pixel)
        (OUT/(units+'.png')).write_bytes(png);cases.append({'id':units,'passed':True,'headCentroid':centroid,'actualPixel':pixel,'audit':r})
    base='<svg xmlns="http://www.w3.org/2000/svg" width="500" height="220" viewBox="0 0 500 220"><rect width="500" height="220" fill="#ffffff"/>{back}<defs><marker id="a" viewBox="0 0 10 10" refX="{ref}" refY="5" markerWidth="20" markerHeight="20" markerUnits="userSpaceOnUse" orient="auto"><path d="M1 1L9 5L1 9Z" fill="context-stroke"/></marker></defs><path d="M40 110H300" stroke="#696969" stroke-width="4" fill="none" marker-end="url(#a)"/>{front}</svg>'
    for ident,back,front,ref,expected in [
        ('dark-region','<rect x="200" y="60" width="150" height="100" fill="#333e48"/>','',9,'arrow-low-contrast'),
        ('alpha-region','<rect x="200" y="60" width="150" height="100" fill="#333e48" fill-opacity=".5"/>','',9,'arrow-low-contrast'),
        ('head-covered','','<rect x="270" y="90" width="50" height="40" fill="#9e1b32"/>',9,'arrow-head-occluded'),
        ('tip-offset','','',7,'arrow-marker-tip-offset')]:
        page.set_content('<html><body style="margin:0">'+base.format(back=back,front=front,ref=ref)+'</body></html>')
        r=page.evaluate(ARROW_AUDIT,{})
        assert expected in {i['kind'] for i in r['issues']},(ident,r)
        page.screenshot(path=str(OUT/(ident+'.png')));cases.append({'id':ident,'passed':True,'expectedFailure':expected,'audit':r})
    # A stroked open head is real direction geometry, not an optional fill.
    page.set_content('<html><body style="margin:0">'+base.format(back='',front='',ref=9).replace('<path d="M1 1L9 5L1 9Z" fill="context-stroke"/>','<path d="M1 1L9 5L1 9" fill="none" stroke="context-stroke" stroke-width="2"/>')+'</body></html>')
    r=page.evaluate(ARROW_AUDIT,{});assert not r['issues'],r;assert any(x['channel']=='stroke' and x['kind']=='head' for x in r['records']);cases.append({'id':'open-stroke-head','passed':True,'audit':r})
    # URL/gradient arrow paint must not silently disappear from a passing report.
    gradient=base.format(back='<defs><linearGradient id="g"><stop stop-color="#000000"/><stop offset="1" stop-color="#ffffff"/></linearGradient></defs>',front='',ref=9).replace('stroke="#696969"','stroke="url(#g)"')
    page.set_content('<html><body style="margin:0">'+gradient+'</body></html>');r=page.evaluate(ARROW_AUDIT,{})
    assert 'arrow-unsupported-paint' in {x['kind'] for x in r['issues']},r;cases.append({'id':'gradient-arrow-rejected','passed':True,'expectedFailure':'arrow-unsupported-paint','audit':r})
    browser.close()
(OUT/'qualification.json').write_text(json.dumps({'passed':True,'cases':cases},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':True,'cases':len(cases)}))
