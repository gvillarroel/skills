#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Verify the local before/after review navigation and embedded vector figures."""

import argparse
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skill-root',type=Path,required=True)
    ap.add_argument('--review',type=Path,required=True)
    args=ap.parse_args()
    sys.dont_write_bytecode=True
    sys.path.insert(0,str(args.skill_root.resolve()/'scripts'))
    from audit_diagram import launch_browser
    records=[]
    with sync_playwright() as pw:
        browser=launch_browser(pw)
        try:
            for width in (1440,500):
                page=browser.new_page(viewport={'width':width,'height':1000})
                errors=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(args.review.resolve().as_uri())
                page.evaluate('document.fonts.ready')
                assert page.locator('#after').is_visible()
                assert not page.locator('#before').is_visible()
                for label in ('Before','After'):
                    button=page.get_by_role('button',name=label,exact=True)
                    button.click()
                    assert button.get_attribute('aria-pressed')=='true'
                    assert page.locator('#'+label.lower()).is_visible()
                checks=page.evaluate('''() => {
                    const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
                    return {uniqueIds:new Set(ids).size===ids.length,
                            svgCount:document.querySelectorAll('.figure > svg').length,
                            documentOverflow:document.documentElement.scrollWidth>innerWidth+1,
                            textCount:document.querySelectorAll('#after svg text').length};
                }''')
                assert checks['uniqueIds'] and checks['svgCount']==2 and checks['textCount']>20,checks
                assert not checks['documentOverflow'],checks
                assert not errors,errors
                page.screenshot(path=str(args.review.parent/f'review-{width}.png'),full_page=True)
                records.append({'width':width,**checks,'errors':errors,'togglePassed':True})
                page.close()
        finally:browser.close()
    result={'ok':True,'views':records}
    (args.review.parent/'browser-check.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
