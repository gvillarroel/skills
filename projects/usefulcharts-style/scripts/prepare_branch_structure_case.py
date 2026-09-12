#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create disclosed development tasks from a fixed subset of synthetic records."""

import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]


def main():
    source=json.loads(subprocess.check_output(['git','show','0be67c64:skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.json'],cwd=ROOT))
    categories={'g5','g2','g3'}
    notes=set('chroniclers glass pumps glass-union pendulum pump-school mechanical metrology precision engines-west light spectrum photographic moving-image imaging'.split())
    records=[{k:n[k] for k in ('id','label','group','founded')}|{'detail':n['detail'] if n['id'] in notes else ''}
             for n in source['nodes'] if n['group'] in categories]
    ids={n['id'] for n in records}
    data=dict(groups=[g for g in source['groups'] if g['id'] in categories],nodes=records,
        edges=[{k:e[k] for k in ('id','source','target','kind')} for e in source['edges'] if e['source'] in ids and e['target'] in ids])
    prompt='''# Naturalistic development case: mechanical and optical traditions

Use the loaded UsefulCharts-style skill to create a polished educational poster titled **From Workshops to Optical Science** from the fictional data below. This case reuses a disclosed subset of an authored development study; it is not a blind or holdout evaluation.

Compose the history as related local chapters. Let the mechanical institutions form a coherent early history and let the later optical tradition expand where shorter mechanical stories finish. Follow causal predecessors, not a common proportional calendar: keep every exact founding date visible, but unrelated institutions with similar dates need not share a row. Keep the predecessors of a merger near its successor. Avoid equal persistent columns, widely scattered final mergers and unrelated edges sharing a visible trunk. Preserve a legitimate shared junction among siblings or the parents of a stated merger.

Keep every supplied record ID, name, founding year, category, visible note and typed relationship. Retain the three supplied category colors. The empty notes deliberately leave ordinary records with a name and date; do not add a generic sentence under every institution. Make the House of Inquiry, Academy of Mechanical Arts, College of Light and Institute of Optical Physics useful landmarks, with quieter supporting names. Include at least two appropriate bundled illustrations on selected landmarks. State clearly that all history is fictional and that vertical spacing is schematic.

Create exactly `result/source.json`, `result/poster.svg`, `result/poster.html`, `result/layout.json`, `result/browser.json`, and `result/poster.png`. Open the final PNG with an image-reading tool, criticize the whole page and a dense connection group, and repair visible problems. Review composition warnings as well as geometry failures. Write a short `result/review.md` stating the largest remaining differences from the intended poster grammar; do not claim indistinguishability without evidence.

The skill directory is read-only. Write generated work only inside this workspace. Use bundled resources without network research or repository discovery. Choose the composition and implementation yourself.

```json
'''+json.dumps(data,indent=2)+'\n```\n'
    (ROOT/'evaluations/pi-prompts/usefulcharts-branch-structure.md').write_text(prompt,encoding='utf-8')
    control=dict(id='independent-branches',title='INDEPENDENT INSTITUTIONAL HISTORIES',design='editorial',mode='lineage',
        width=1400,height=1000,source_note='Original synthetic test records.',groups=[dict(id='g',label='Institutions',color='#F56550')],
        nodes=[dict(id=nid,label=label,group='g',width=150,x=x,y=y,date_label=date,detail_position='outside')
            for nid,label,date,x,y in [('a','Western Workshop','1710',200,250),('b','Institute of Weights','1850',850,600),
                                     ('c','Eastern Workshop','1730',500,250),('d','Institute of Measures','1860',1100,600)]],
        edges=[dict(id='first',source='a',target='b',kind='branch'),dict(id='second',source='c',target='d',kind='branch')])
    command='''# Exact command control: independent institutional paths

Write the following JSON exactly to `draft.json`. Keep the copied skill read-only. This is a command control; image inspection is not required.

```json
'''+json.dumps(control,indent=2)+'''
```

Run these exact commands in order:

```sh
uv run --script skills/usefulcharts-style/scripts/render_chart.py draft.json --svg result/poster.svg --html result/poster.html --report result/layout.json
```

```sh
uv run --script skills/usefulcharts-style/scripts/audit_chart.py result/poster.svg --source draft.json --report result/browser.json --png result/poster.png
```

Required artifacts: `draft.json`, `result/poster.svg`, `result/poster.html`, `result/layout.json`, `result/browser.json`, `result/poster.png`. Preserve all supplied fields, dates and relationships. Verify that the browser audit has no hard findings and no `unrelated-shared-run` warning. Report the result without changing the source or the skill.
'''
    (ROOT/'evaluations/pi-prompts/usefulcharts-branch-structure-contract.md').write_text(command,encoding='utf-8')
    print(json.dumps(dict(nodes=len(records),edges=len(data['edges']),printed_notes=sum(bool(n['detail']) for n in records),source_revision='0be67c64',case_type='disclosed development subset')))


if __name__=='__main__':main()
