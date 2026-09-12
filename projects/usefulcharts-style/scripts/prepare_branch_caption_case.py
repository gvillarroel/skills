#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare a complete, data-first publishing case with supplied local captions."""

import json
from pathlib import Path

from prepare_publishing_case import data

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / 'projects/usefulcharts-style/artifacts/reviews/full-branches-v33'


def captioned_history():
    source = data()
    captions = [
        ('bookhall', 'BOOKS FOR A PUBLIC', 'books'),
        ('university', 'SCIENTIFIC PUBLICATION', 'science'),
        ('gazette', 'THE CIVIC PRESS', 'news'),
        ('school', 'LEARNING IN PRINT', 'learning'),
        ('engravers', 'ILLUSTRATED ARTS', 'arts'),
    ]
    source['annotations'] = [dict(node=node, kind='pill', label=label, width=300, size=16, group=group)
                             for node, label, group in captions]
    return source


def main():
    source = captioned_history()
    ART.mkdir(parents=True, exist_ok=True)
    (ART/'caption-case.json').write_text(json.dumps(source, indent=2)+'\n', encoding='utf-8')
    task_data = {key: value for key, value in source.items() if key not in ('design', 'mode', 'layout')}
    prompt = '''Create a polished, editable educational wall chart of the supplied fictional history of Northbridge publishing. Use clear local histories, semantic colors, varied emphasis and legible institutional connections in the visual tradition of UsefulCharts. The five supplied family captions should help a reader recognize the main publishing traditions beside their named institutions. Compose their complete lettering together with the records; preserve their specified widths, sizes, colors and anchor identities.

Preserve all 70 institutions, their exact names, dates, notes, categories, illustration identities and emphasis choices, and all 97 typed relationships. Preserve every supplied field. Do not invent records, omit visible notes or confuse influence with institutional succession or merger. The seven category colors are fixed. Make the fictional status visible. Main names must be at least 16 SVG units and notes at least 12 units; choose a suitable canvas rather than shrinking text. Positions are not supplied: create the composition from the records. The result must include all five family captions with no overlap or unrelated path hidden behind a caption.

Deliver exactly result/source.json, result/poster.svg, result/poster.html, result/layout.json, result/browser.json, result/poster.png and result/review.md. Keep draft or intermediate files elsewhere in this workspace. The final result directory must contain only these seven deliverables. Inspect the final full-page PNG with the image-reading tool and inspect a busy region at a larger scale. Repair visible problems, then write a candid review identifying the three largest remaining compositional weaknesses. A clean geometry report is not evidence of equivalent aesthetic quality.

Use only the supplied skill and normal local tools. Treat skills/usefulcharts-style/ as read-only. Keep generated files inside this workspace. Do not inspect acceptance fixtures, repository files, other skills, earlier evaluations or external task directories. No network research is needed for this explicitly fictional source.

The complete source data follows.

```json
'''+json.dumps(task_data, indent=2)+'\n```\n'
    (ROOT/'evaluations/pi-prompts/usefulcharts-branch-captions.md').write_text(prompt, encoding='utf-8')
    tiny = dict(id='captioned-collections', title='THE PUBLIC COLLECTIONS', design='editorial', mode='lineage', layout='branches',
                source_note='Fictional command control.', groups=[dict(id='civic',label='Civic collections',color='#77BDDD')],
                nodes=[dict(id=nid,label=label,founded=year,date_label=str(year),group='civic',detail=detail)
                       for nid,label,year,detail in [('cabinet','Common Cabinet',1700,''),('east','Eastern Reading Room',1730,''),
                           ('west','Western Book Society',1741,''),('library','United Public Library',1780,'The two bodies unite')]],
                edges=[dict(id=f'e{i}',source=a,target=b,kind='branch') for i,(a,b) in enumerate([
                    ('cabinet','east'),('cabinet','west'),('east','library'),('west','library')])],
                annotations=[dict(node='east',kind='pill',label='EASTERN READING TRADITIONS',group='civic',width=320,size=18)])
    control = '''Run this exact command control with the read-only usefulcharts-style skill. Write the JSON below unchanged to draft.json. Execute these commands in order:

```sh
uv run --script skills/usefulcharts-style/scripts/create_branch_poster.py draft.json --output-dir result
```

Keep generated files inside this workspace. Do not read acceptance examples, sibling skills, repository files or external task directories. Do not modify the JSON or the skill. Image inspection is not required for this command control. Report any findings honestly.

```json
'''+json.dumps(tiny, indent=2)+'\n```\n'
    (ROOT/'evaluations/pi-prompts/usefulcharts-branch-captions-contract.md').write_text(control, encoding='utf-8')
    print(json.dumps(dict(nodes=len(source['nodes']), edges=len(source['edges']), captions=len(source['annotations']))))


if __name__ == '__main__':
    main()
