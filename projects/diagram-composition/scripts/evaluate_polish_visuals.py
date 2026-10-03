#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0"]
# ///
"""Compare the actual workspace figure and write a portable before/after review."""

import argparse
import copy
import hashlib
import html
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--skill-root',type=Path,required=True)
    ap.add_argument('--before',type=Path,required=True);ap.add_argument('--after',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    sys.dont_write_bytecode=True;sys.path.insert(0,str(args.skill_root.resolve()/'scripts'))
    from audit_diagram import launch_browser, root_to_text
    from compose_diagram import namespace, parse_svg, tag
    from visual_quality import QUALITY
    results=[];svgs={}
    with sync_playwright() as pw:
        browser=launch_browser(pw)
        try:
            for name,path in (('before',args.before),('after',args.after)):
                root,vb,digest=parse_svg(path)
                report=json.loads(root.find(tag('metadata')+"[@id='composition-report']").text)
                page=browser.new_page(viewport={'width':1280,'height':800})
                page.set_content(root_to_text(root))
                page.evaluate("document.body.style.margin='0'")
                page.evaluate("document.fonts.ready")
                # Evaluator annotations identify the same pre-existing physical icon
                # frames and topology wires in both figures. Saved inputs stay unchanged.
                page.evaluate("""() => {
                  const panel=document.querySelector('[data-panel-id="topology"]');
                  panel.querySelectorAll('rect[data-color-concept]').forEach((e,i)=>{
                    if(!e.dataset.nodeId)e.dataset.nodeId='reviewed-frame-'+e.dataset.colorConcept;
                    e.dataset.nodeKind='node';
                  });
                  panel.querySelectorAll('line').forEach(e=>e.dataset.connector='native');
                }""")
                audit=page.evaluate(QUALITY,{'report':report})
                intrusions=[i for i in audit['issues'] if i['kind']=='connector-object-intrusion' and i['object'].startswith('topology.')]
                contrast=next(c['ratio'] for c in audit['contrasts'] if c['label']=='Source + instructions')
                page.screenshot(path=str(args.output/(name+'.png')))
                page.screenshot(path=str(args.output/(name+'-detail.png')),clip={'x':45,'y':175,'width':490,'height':190})
                results.append({'version':name,'sourceSha256':digest,'visibleIconFrameIntrusions':len(intrusions),
                                'intrusions':intrusions,'secondaryLabelContrast':contrast,
                                'verifiedContacts':len(audit['contacts']),'issues':audit['issues']})
                svgs[name]=ET.tostring(namespace(copy.deepcopy(root),name+'-'),encoding='unicode')
                page.close()
        finally:browser.close()
    before,after=results
    passed=before['visibleIconFrameIntrusions']>0 and after['visibleIconFrameIntrusions']==0 and after['secondaryLabelContrast']>=4.5 and not after['issues']
    evidence={'ok':passed,'method':'Same browser audit with evaluator annotations on the existing topology icon frames and wires; original inputs preserved.','results':results}
    (args.output/'comparison.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Diagram composition quality review</title><style>
body{margin:0;background:#f4f6f8;color:#26323d;font:16px/1.5 system-ui,sans-serif}main{max-width:1320px;margin:30px auto;padding:0 20px}h1{font-size:28px;margin-bottom:6px}p{max-width:90ch}nav{display:flex;gap:12px;margin:24px 0}button{padding:10px 22px;border:1px solid #aebecb;border-radius:6px;background:white;color:#26323d;font:inherit;cursor:pointer}button[aria-pressed=true]{background:#26323d;color:white}table{border-collapse:collapse;background:white}th,td{padding:10px 20px;text-align:left;border:1px solid #cbd3da}.figure{overflow:auto;background:white;border:1px solid #cbd3da;border-radius:8px}.figure svg{display:block;width:1280px;height:800px}section[hidden]{display:none}.caption{color:#536575}a{color:#276bc8}
</style><main><h1>Diagram composition quality review</h1><p>The same illustrative workspace before and after the skill update. Switch views and inspect the icon boundaries, connection endpoints, and secondary labels.</p>
<table><tr><th>Measured behavior</th><th>Before</th><th>After</th></tr>
<tr><td>Visible wires inside topology icon frames</td><td>BEFORE_INTRUSIONS</td><td>AFTER_INTRUSIONS</td></tr>
<tr><td>Secondary label contrast</td><td>BEFORE_CONTRAST</td><td>AFTER_CONTRAST</td></tr>
<tr><td>Verified cross-view terminal contacts</td><td>BEFORE_CONTACTS</td><td>AFTER_CONTACTS</td></tr></table>
<nav aria-label="Comparison"><button data-view="before" aria-pressed="false">Before</button><button data-view="after" aria-pressed="true">After</button></nav>
<section id="before" hidden><p class="caption">Before: transparent icon enclosures reveal short wire segments; the secondary label falls below the chosen contrast threshold.</p><div class="figure">BEFORE_SVG</div></section>
<section id="after"><p class="caption">After: wires meet the actual surfaces, concept colors remain consistent, and secondary labels are darker.</p><div class="figure">AFTER_SVG</div></section>
<p>Labels are shown at the audited 1280px width; narrow windows can scroll horizontally. The four injected negative controls are retained separately to evaluate defect detection.</p></main>
<script>document.querySelectorAll('button[data-view]').forEach(button=>button.addEventListener('click',()=>{for(const item of document.querySelectorAll('button[data-view]')){const active=item===button;item.setAttribute('aria-pressed',String(active));document.getElementById(item.dataset.view).hidden=!active;}}));</script></html>'''
    substitutions={'BEFORE_INTRUSIONS':str(before['visibleIconFrameIntrusions']),'AFTER_INTRUSIONS':str(after['visibleIconFrameIntrusions']),
        'BEFORE_CONTRAST':f"{before['secondaryLabelContrast']:.2f}:1",'AFTER_CONTRAST':f"{after['secondaryLabelContrast']:.2f}:1",
        'BEFORE_CONTACTS':str(before['verifiedContacts']),'AFTER_CONTACTS':str(after['verifiedContacts']),
        'BEFORE_SVG':svgs['before'],'AFTER_SVG':svgs['after']}
    for token,value in substitutions.items():page=page.replace(token,value)
    (args.output/'index.html').write_text(page,encoding='utf-8')
    print(json.dumps({'ok':passed,'results':[{k:v for k,v in r.items() if k not in {'issues','intrusions'}} for r in results],'review':str(args.output/'index.html')}))
    return 0 if passed else 1


if __name__=='__main__':raise SystemExit(main())
