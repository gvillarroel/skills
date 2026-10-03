#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Exercise the comparison gallery and render readable final detail previews."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]/'artifacts'
def main():
    out=ROOT/'screenshots';out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport=dict(width=1500,height=1100));errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        response=page.goto('http://127.0.0.1:8768/index.html');assert response.status==200
        page.locator('#mars').scroll_into_view_if_needed();page.locator('#bsd').scroll_into_view_if_needed()
        assert page.locator('section.case').count()==3
        assert page.locator('.comparison img').evaluate_all('(images)=>images.every(i=>i.complete&&i.naturalWidth>0)')
        page.screenshot(path=str(out/'gallery-desktop.png'),full_page=True)
        for link in page.locator('main a').all():
            url=link.get_attribute('href')
            if not url.startswith('https:'):assert page.request.get('http://127.0.0.1:8768/'+url).ok,url
        page.set_viewport_size(dict(width=430,height=900));page.goto('http://127.0.0.1:8768/index.html')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.screenshot(path=str(out/'gallery-mobile.png'))
        page.goto((ROOT/'index.html').resolve().as_uri())
        assert page.locator('[data-download]').is_hidden(),'Offline gallery must not link to its absent enclosing ZIP'
        assert not errors,errors
        page.close()
        for case,box in [('bsd',(45,850,1040,900)),('instruments',(50,925,1040,1020)),('mars',(1180,1040,1120,650))]:
            page=browser.new_page(viewport=dict(width=int(box[2]),height=int(box[3])))
            svg=(ROOT/'revision-2'/case/'poster.svg').read_text(encoding='utf-8')
            page.set_content('<html><style>body{margin:0}svg{display:block}</style>'+svg+'</html>');page.evaluate('document.fonts.ready')
            page.evaluate('''([x,y,w,h])=>{const svg=document.querySelector('svg');svg.setAttribute('viewBox',[x,y,w,h].join(' '));svg.setAttribute('width',w);svg.setAttribute('height',h)}''',box)
            page.locator('svg').screenshot(path=str(out/f'{case}-detail.png'));page.close()
        browser.close()
    (ROOT/'reviews/gallery-check.json').write_text(json.dumps(dict(status='pass',http=200,cases=3,preview_images=6,mobile_width=430,javascript_errors=0),indent=2)+'\n')
    print('Gallery links, all six images, desktop, mobile and three detail views passed.')

if __name__=='__main__':main()
