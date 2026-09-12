#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Capture equal-width critique and an interactive detail of changed corridors."""

import hashlib
import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
NS = {'s': 'http://www.w3.org/2000/svg'}
ET.register_namespace('', NS['s'])


def scoped_svg(path, prefix, changed):
    root = ET.parse(path).getroot()
    root.set('viewBox', '200 1430 1120 630')
    root.set('width', '1120')
    root.set('height', '630')
    names = {node.get('id'): prefix + '-' + node.get('id') for node in root.iter() if node.get('id')}
    for node in root.iter():
        if node.get('id'):
            node.set('id', names[node.get('id')])
        for key, value in list(node.attrib.items()):
            if value.startswith('#') and value[1:] in names:
                node.set(key, '#' + names[value[1:]])
            for old, new in names.items():
                if 'url(#' + old + ')' in value:
                    node.set(key, value.replace('url(#' + old + ')', 'url(#' + new + ')'))
        if node.get('data-edge-id') in changed:
            node.set('data-revised-corridor', 'true')
    return ET.tostring(root, encoding='unicode')


def main():
    review = ROOT / 'projects/usefulcharts-style/artifacts/reviews/local-stories-v31'
    output = review / 'comparison'
    output.mkdir(exist_ok=True)
    examples = ROOT / 'skills/usefulcharts-style/assets/examples/usefulcharts-style'
    old = json.loads((review / 'baseline-institution/poster.json').read_text(encoding='utf-8'))
    new = json.loads((examples / 'atlas-of-inquiry.json').read_text(encoding='utf-8'))
    assert {k: v for k, v in old.items() if k != 'edges'} == {k: v for k, v in new.items() if k != 'edges'}
    assert [{k: v for k, v in e.items() if k != 'via'} for e in old['edges']] == [{k: v for k, v in e.items() if k != 'via'} for e in new['edges']]
    changed = json.loads((review / 'promoted-corridors.json').read_text(encoding='utf-8'))['edges']
    pictures = [('UsefulCharts reference', ROOT / 'projects/usefulcharts-style/artifacts/images/reference-denominations.png'),
                ('Published baseline · 13 painted overlaps', review / 'baseline-institution/poster.svg'),
                ('Revised mural · 0 painted overlaps', examples / 'atlas-of-inquiry.svg')]
    style = '''<style>*{box-sizing:border-box}body{font:17px/1.5 Arial;background:#eee9dc;color:#242722;margin:24px}h1{font-size:27px}h2{font-size:18px}p{max-width:1200px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}figure{margin:0}img,svg{width:100%;height:auto;display:block}.two{grid-template-columns:repeat(2,minmax(0,1fr))}label{display:block;margin:16px 0}.focus [data-edge-id]:not([data-revised-corridor]){opacity:.12}@media(max-width:850px){.grid{grid-template-columns:1fr}}</style>'''
    page = output / 'comparison.html'
    page.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Branch composition critique</title>'+style+
                   '<h1>Composition and painted connections</h1><p>Private, unblinded author comparison at equal display width. All 141 institutions, 171 typed relationships, 133 printed notes, type sizes, colors, illustrations and node positions remain unchanged in the revised mural. Thirteen eight-unit shifts affect twelve corridors. The complete goal of equivalent UsefulCharts quality remains unproven.</p><div class="grid">'+
                   ''.join('<figure><h2>'+html.escape(title)+'</h2><img src="'+path.as_uri()+'"></figure>' for title,path in pictures)+
                   '</div><h2>Direct critique</h2><p>The corrected paths are easier to distinguish in dense groups. Persistent large families, repeated illustration motifs and limited intermediate hierarchy still separate the composition from the reference. Source-correct routing is a necessary improvement, not a visual acceptance score.</p><p><a href="detail.html">Inspect the changed corridors at a larger scale</a> · <a href="publishing.html">Inspect the new publishing subject</a></p></html>', encoding='utf-8')
    detail = output / 'detail.html'
    detail.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Institutional corridor detail</title>'+style+
                     '<h1>Local corridor repair</h1><p>Identical crop and scale. Toggle the emphasis to trace the twelve changed relationships; node positions and typography are unchanged.</p><label><input type="checkbox" id="focus"> Emphasize changed relationships</label><main class="grid two">'+
                     '<figure><h2>Before</h2>'+scoped_svg(pictures[1][1], 'before', changed)+'</figure><figure><h2>After</h2>'+scoped_svg(pictures[2][1], 'after', changed)+
                     '</figure></main><script>document.querySelector("#focus").onchange=e=>document.body.classList.toggle("focus",e.target.checked)</script></html>', encoding='utf-8')
    publishing = output / 'publishing.html'
    publishing.write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>New-subject composition</title>'+style+
                         '<h1>One new subject, revised connection choices</h1><p>Original fictional development material: 70 institutions, 97 typed relationships and every supplied note. The first version has a narrower, unrelated centerline collision exposed by painted-stroke inspection. The composed version selects lateral influence attachments before rendering. Neither is a blind evaluation or proof of reference-quality parity.</p><main class="grid two">'+
                         ''.join('<figure><h2>'+label+'</h2><img src="'+path.as_uri()+'"></figure>' for label,path in [
                             ('Ordered placement, bottom-to-top influences', review / 'publishing-ordered/poster.png'),
                             ('Composed placement and influence attachments', review / 'publishing-final/poster.png')])+
                         '</main><p>The earlier prototype calls one institution Railway News Service; the final fictional source corrects this to Roadside News Service so the supplied coach illustration matches the subject. The headline is also corrected from five to six centuries because the source spans 1428–2024. These disclosed source edits are separate from route quality. The broad upper-right pocket, limited art variety and several long cross-family paths still need editorial work.</p></html>', encoding='utf-8')
    records = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        tab = browser.new_page(viewport={'width': 2000, 'height': 1200})
        for name, path in [('comparison', page), ('detail', detail), ('publishing', publishing)]:
            tab.goto(path.as_uri())
            tab.evaluate('document.fonts.ready')
            tab.wait_for_function('[...document.images].every(i=>i.complete&&i.naturalWidth>0)')
            png = output / (name + '.png')
            tab.screenshot(path=str(png), full_page=True)
            records.append(dict(id=name, png_sha256=hashlib.sha256(png.read_bytes()).hexdigest()))
            if name == 'detail':
                tab.locator('#focus').check()
                assert tab.locator('body.focus').count() == 1
                assert tab.locator('[data-revised-corridor]').count() == 2 * len(changed)
                tab.screenshot(path=str(output / 'detail-emphasis.png'), full_page=True)
        browser.close()
    report = dict(status='pass', all_node_fields_unchanged=True, non_geometry_edge_fields_unchanged=True,
                  changed_edges=changed, printed_notes=sum(bool(n.get('detail')) for n in new['nodes']), captures=records)
    (output / 'comparison.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
