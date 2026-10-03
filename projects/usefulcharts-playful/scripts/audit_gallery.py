#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Exercise offline gallery, search, source focus, comparison and mobile controls."""
from pathlib import Path
import json
import sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'artifacts'
def main():
    revision=sys.argv[1] if len(sys.argv)>1 else 'revision-2';gallery='gallery-r3' if revision=='revision-3' else 'gallery'
    results=[];screens=OUT/'screenshots'/revision;screens.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as p:
        browser=p.chromium.launch();context=browser.new_context(viewport=dict(width=1440,height=1050))
        context.route('**/*',lambda r:r.abort() if r.request.url.startswith(('http://','https://')) else r.continue_())
        page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((OUT/gallery/'index.html').as_uri());page.locator('article').last.wait_for();page.screenshot(path=str(screens/'gallery-desktop.png'),full_page=True)
        assert page.locator('article').count()==5
        assert page.locator('img').evaluate_all('(els)=>els.every(e=>e.complete&&e.naturalWidth>0)')
        for case in ['instruments','starships','mars','bsd','civilizations']:
            page.goto((OUT/revision/case/'poster.html').as_uri());page.evaluate('document.fonts.ready')
            assert page.locator('#paper > svg').count()==1
            picture_count=page.locator('[data-art-id]').count();assert picture_count>0
            page.locator('#quests button').first.click();assert page.locator('.focus-box').count()==1
            focused=page.locator('#record-title').inner_text();assert focused!='Explore a record'
            page.locator('#search').fill(focused.split()[0]);assert page.locator('#results button').count()>0
            page.locator('#results button').first.click();assert page.locator('#sources a').count()>0
            before=page.locator('#paper').bounding_box()['width'];page.locator('#plus').click();assert page.locator('#paper').bounding_box()['width']>before
            page.locator('#compare').click();assert page.locator('#before').is_visible();assert page.locator('#before').evaluate('(e)=>e.complete&&e.naturalWidth>0')
            page.locator('#compare').click();assert page.locator('#paper > svg').is_visible();page.locator('#fit').click()
            if case=='instruments':page.screenshot(path=str(screens/'instruments-desktop.png'))
            page.set_viewport_size(dict(width=390,height=844));page.locator('#mobile-info').click();assert page.locator('#info').is_visible()
            overflow=page.evaluate('document.documentElement.scrollWidth>innerWidth+1')
            if overflow:raise AssertionError('Mobile horizontal overflow: '+case)
            page.locator('#quests button').first.click();page.locator('#mobile-info').click();assert not page.locator('#info').is_visible()
            if case=='instruments':page.screenshot(path=str(screens/'instruments-mobile.png'))
            results.append(dict(case=case,status='pass',body_images=picture_count,focus_record=focused,search=True,source_link=True,zoom=True,before_after=True,mobile=True,offline=True))
            page.set_viewport_size(dict(width=1440,height=1050))
        page.goto((OUT/gallery/'index.html').as_uri());page.set_viewport_size(dict(width=390,height=844));assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1');page.screenshot(path=str(screens/'gallery-mobile.png'),full_page=True)
        browser.close()
    report=dict(status='pass' if not errors else 'fail',cases=results,errors=errors)
    (OUT/(revision if revision=='revision-3' else 'reviews')/'gallery-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report));return bool(errors)
if __name__=='__main__':raise SystemExit(main())
