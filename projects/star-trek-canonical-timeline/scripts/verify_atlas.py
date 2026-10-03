#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.58", "pymupdf>=1.25"]
# ///
"""Verify the delivered viewer, source coverage, PDF links and preserved labels."""
from pathlib import Path
import hashlib
import json
import re
import unicodedata
from playwright.sync_api import sync_playwright
import pymupdf

PROJECT=Path(__file__).resolve().parents[1]
OUT=PROJECT/'artifacts'

def normalize(s):return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFKD',s).lower())
def main():
    data=json.loads((PROJECT/'data/timeline.json').read_text(encoding='utf-8'))
    layout=json.loads((OUT/'reviews/layout.json').read_text())
    records=[e for key in ['events','origins','future','branches'] for e in data[key]]
    assert hashlib.sha256((PROJECT/'data/timeline.json').read_bytes()).hexdigest()==layout['data_sha256']
    assert hashlib.sha256((OUT/'svgs/star-trek-timeline.svg').read_bytes()).hexdigest()==layout['svg_sha256']
    audit=json.loads((OUT/'reviews/final/browser-audit.json').read_text())
    assert not audit['outside'] and not audit['overlaps'] and not audit['envelope_overflow']
    report={'records':len(records),'source_coverage':sum(e['source'] in data['sources'] and bool(e['credit']) for e in records),'geometry':'pass','errors':[]}
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chrome',headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1050},device_scale_factor=1)
        page.on('pageerror',lambda error:report['errors'].append(str(error)))
        page.goto((OUT/'viewer/index.html').as_uri(),wait_until='load')
        page.evaluate('document.fonts.ready')
        assert page.locator('.record').count()==len(records)
        page.locator('#search').fill('Dominion')
        count=page.locator('#results button').count();assert count>=10
        page.locator('#results button').filter(has_text='THE DOMINION WAR BEGINS').click()
        assert 'Call to Arms' in page.locator('#selection').inner_text()
        report['selection_source']=page.locator('#selection a').get_attribute('href')
        assert report['selection_source'].startswith('https://www.startrek.com/')
        assert page.locator('.record.selected').count()==1
        before=page.locator('#zoomvalue').inner_text();page.locator('#plus').click();after=page.locator('#zoomvalue').inner_text();assert before!=after
        page.locator('#fit').click()
        page.screenshot(path=str(OUT/'reviews/final/viewer-overview.png'))
        page.locator('#search').fill('')
        page.locator('#jump').select_option('future')
        assert page.locator('#viewport').evaluate('(e)=>e.scrollTop')>500
        page.locator('#jump').select_option('bajor-dominion')
        assert page.locator('#viewport').evaluate('(e)=>e.scrollLeft')>0
        page.screenshot(path=str(OUT/'reviews/final/viewer-reading.png'))
        assert page.locator('a[href="../documents/sources.html"]').count()==1
        # Every selectable event resolves to the same source catalog used by the poster.
        js_data=page.locator('#data').text_content()
        got=json.loads(js_data)
        assert {e['id'] for e in got['entries']}==set(layout['record_ids'])
        assert all(e['source'] in got['sources'] for e in got['entries'])
        report['dominion_search_results']=count;report['viewer']='pass'
        browser.close()
    pdf=pymupdf.open(OUT/'documents/star-trek-timeline.pdf')
    assert len(pdf)==1
    pdftext=normalize(pdf[0].get_text())
    missing=[e['label'] for e in records if normalize(e['label']) not in pdftext]
    assert not missing,missing
    hyperlinks=pdf[0].get_links();assert len(hyperlinks)==len(records)
    report['pdf']={'pages':1,'record_labels_preserved':len(records),'source_hyperlinks':len(hyperlinks),'print_size_inches':[round(pdf[0].rect.width/72,2),round(pdf[0].rect.height/72,2)]}
    report['rendered_text_nodes']=audit['text_count']
    report['historical_categories']={key:len(data[key]) for key in ['events','origins','future','branches']}
    assert not report['errors'],report['errors']
    (OUT/'reviews/final/verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
