#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare disclosed authored-layout refinement and distinct-emblem controls."""

import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]


def main():
    source=json.loads((ROOT/'projects/usefulcharts-style/artifacts/reviews/semantic-emblems-v32/native-context-frozen/source.json').read_text(encoding='utf-8'))
    source.pop('insets')
    prompt='''Refine the supplied fictional publishing-history poster into a more polished editorial composition. Keep its 70 institutions, all 97 typed relationships, exact names, dates, notes, category colors, illustration identities, type sizes, node positions and page dimensions. The local education branch has already been arranged; preserve that geometry. Use the open areas beside the origins to give the reader useful context.

Include the exact heading "From workshops to readers" and this exact paragraph: "Two workshops combine in The Common Press in 1471. Later branches serve science, schools and public readers." Accompany it with the supplied illustration-printing-press-bookman asset. Also show a compact, accurate overview of every category in the supplied data, where one small mark represents one institution actually shown. Its heading is "Institutions represented in this history". Do not invent population, sales, geographic assignments or additional institutions. Preserve the visible fictional-history disclosure. The additions should use the poster's paper naturally and remain subordinate to the overall history.

Deliver exactly result/source.json, result/poster.svg, result/poster.html, result/layout.json, result/browser.json, result/poster.png and result/review.md. Keep all diagram and contextual text editable. Open the final PNG with the image tool, inspect the whole page and a busy local group, repair problems and write a candid visual critique. A clean geometry report does not establish parity with UsefulCharts.

Use only the supplied usefulcharts-style bundle and normal local tools. The copied skills/usefulcharts-style/ directory is read-only. Keep all generated files in this workspace. Do not inspect acceptance examples, repository documents, other skills, earlier runs or external task directories. No network research is needed for this fictional source. The exact existing authored source follows.

```json
'''+json.dumps(source,indent=2)+'\n```\n'
    (ROOT/'evaluations/pi-prompts/usefulcharts-context-insets.md').write_text(prompt,encoding='utf-8')
    groups=[dict(id='sky',label='Sky and space',color='#F56550'),dict(id='instruments',label='Instruments',color='#F7CD26'),
            dict(id='light',label='Optical studies',color='#98BD92'),dict(id='places',label='Maritime and civic',color='#77BDDD')]
    records=[('star','Star Catalogue House','sky'),('sun','Solar Calendar Office','sky'),('compass','Compass Collection','instruments'),
             ('astrolabe','Astrolabe Cabinet','instruments'),('orbit','Orbital Studies Institute','sky'),('globe','Globe Collection','instruments'),
             ('wheel','Wheelwrights Archive','instruments'),('gear','Mechanical Transmission Room','instruments'),('lens','Optical Lens Collection','light'),
             ('prism','Spectrum Laboratory','light'),('anchor','Harbour Records Office','places'),('ship','Voyage Collection','places'),
             ('tower','Tower Records Room','places'),('observatory','Observatory Papers','sky')]
    smoke=dict(id='distinct-study-collections',title='MEASURING THE WORLD',design='editorial',mode='lineage',layout='authored',
               width=1400,height=1570,font_size=17,source_note='Fictional independent teaching collections. Original symbols are illustrative, not institutional logos.',
               reading_note='The independent collections imply no descent. Counts refer only to records shown.',groups=groups,nodes=[],edges=[])
    for i,(icon,label,group) in enumerate(records):
        smoke['nodes'].append(dict(id=icon,label=label,group=group,icon=icon,icon_width=65,width=260,style='emblem',
                                   x=215+(i%4)*323,y=590+(i//4)*235,size=18))
    smoke['insets']=[dict(id='instrument-story',kind='story',box=[80,180,470,240],title='Different ways of measuring',
                         text='These independent collections distinguish navigation, celestial observation and optical work.',
                         source_nodes=['compass','astrolabe','lens'],icon='astrolabe',art_width=110,art_height=110),
                     dict(id='collection-counts',kind='counts',box=[780,180,540,240],title='Collections represented here',columns=2)]
    text='''Run this exact command-contract control with the read-only usefulcharts-style bundle. Write the following JSON unchanged to draft.json, then execute the three commands in order.

```sh
uv run --script skills/usefulcharts-style/scripts/compose_context_insets.py draft.json --output result/source.json --report result/context.json
uv run --script skills/usefulcharts-style/scripts/render_chart.py result/source.json --svg result/poster.svg --html result/poster.html --report result/layout.json
uv run --script skills/usefulcharts-style/scripts/audit_chart.py result/poster.svg --source result/source.json --report result/browser.json --png result/poster.png
```

Keep all generated files in this workspace. Do not change the source JSON or the copied skill. Do not read acceptance examples, other skills, repository documents or external task directories. Image inspection is not required in this command control. The final audit must contain no hard findings.

```json
'''+json.dumps(smoke,indent=2)+'\n```\n'
    (ROOT/'evaluations/pi-prompts/usefulcharts-context-insets-contract.md').write_text(text,encoding='utf-8')
    control=ROOT/'projects/usefulcharts-style/artifacts/reviews/semantic-emblems-v32/contract-input.json'
    control.write_text(json.dumps(smoke,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(naturalistic_records=len(source['nodes']),relationships=len(source['edges']),control_emblems=len(smoke['nodes']),control=str(control))))


if __name__=='__main__':main()
