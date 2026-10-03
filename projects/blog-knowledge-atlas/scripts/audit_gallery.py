#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Exercise the actual offline viewer, including source selection and mobile UI."""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'


def main():
    shots=OUT/'screenshots'
    shots.mkdir(parents=True,exist_ok=True)
    reports=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch()
        for width,height,label in [(1440,1020,'desktop'),(390,844,'mobile')]:
            page=browser.new_page(viewport=dict(width=width,height=height))
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.goto((OUT/'index.html').as_uri(),wait_until='load')
            page.evaluate('document.fonts.ready')
            checks=[]
            for case,term,expected in [('01-history','LoRA','LoRA'),('02-agent','compaction','Compaction / restart'),('03-evaluation','withheld','Skill withheld')]:
                page.locator('nav button[data-case="'+case+'"]').click()
                assert page.locator('#canvas>svg').count()==1
                source=json.loads((OUT/case/'manifest.json').read_text(encoding='utf-8'))
                assert page.locator('#canvas [data-record-id]').count()==len(source['records'])
                page.locator('#query').fill(term)
                assert page.locator('#hits button').count()>0
                page.locator('#hits button').get_by_text(expected,exact=True).click() if page.locator('#hits button').get_by_text(expected,exact=True).count() else page.locator('#hits button',has_text=expected).first.click()
                assert page.locator('#record-title').inner_text()==expected
                href=page.locator('#source').get_attribute('href')
                assert href.startswith('https://')
                assert page.locator('#selection-frame').count()==1
                assert float(page.locator('#zoom').input_value())>=90
                page.locator('#fit').click()
                measured=page.evaluate('''() => {const v=document.querySelector('#viewport');const s=document.querySelector('#canvas>svg');return {poster:s.getBoundingClientRect().width,viewport:v.clientWidth,body:document.body.scrollWidth,window:innerWidth}}''')
                assert measured['poster']<=measured['viewport']
                assert measured['body']<=width+1
                assert page.locator('#download-pdf').get_attribute('href')==case+'/poster.pdf'
                page.screenshot(path=str(shots/f'{label}-{case}.png'),full_page=True)
                image=page.locator('#canvas .art-hit').first
                owner=image.get_attribute('data-owner')
                image.click()
                assert page.locator('#record-title').inner_text()==next(r['title'] for r in source['records'] if r['id']==owner)
                checks.append(dict(case=case,records=len(source['records']),search=term,selected=expected,source=href,fit=measured,image_owner=owner,pass_status=True))
            page.locator('#query').fill('no-such-knowledge-record-92876')
            assert page.locator('#result-count').inner_text()=='0 matches'
            page.reload();page.evaluate('document.fonts.ready')
            assert page.locator('nav button[aria-selected=true]').get_attribute('data-case')=='03-evaluation'
            reports.append(dict(viewport=[width,height],cases=checks,page_errors=errors,pass_status=not errors))
            page.close()
        browser.close()
    (OUT/'reviews/gallery-audit.json').write_text(json.dumps(reports,indent=2)+'\n',encoding='utf-8')
    assert all(r['pass_status'] for r in reports)
    print(json.dumps(dict(viewports=len(reports),poster_checks=sum(len(r['cases']) for r in reports),status='pass')))


if __name__=='__main__':main()
