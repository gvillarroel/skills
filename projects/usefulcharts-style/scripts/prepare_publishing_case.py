#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Author a new fictional publishing history before laying out its branches."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

# id | institution | founded | group | predecessors (~ means influence) | note | image
# Each record is authored individually. Dates and relationships do not come
# from coordinates, generated stages, or a repeated succession template.
RECORDS = '''
scribes|Northbridge Scribes|1428|origins|||book
cutters|St Anne's Blockcutters|1446|origins||A workshop tradition|
paper|Riverside Papermakers|1452|origins|||
common|The Common Press|1471|books|scribes,cutters|The two workshops combine|illustration-printing-press-bookman
ragmill|Rag Mill Fellowship|1478|origins|paper||
type|Founders of St Anne|1493|books|common|Typecasting becomes a separate trade|
river|Rivergate Press|1504|books|common,~ragmill||
university|University Press|1521|science|common||book
gazette|The City Gazette|1534|news|river|A weekly civic paper begins|
bindery|Northbridge Bindery|1549|books|river||
herbal|Herbal House|1556|science|university||
school|Schoolbook Society|1562|learning|university||
engravers|Copperplate Fellowship|1580|arts|cutters,~type||
almanac|Almanac Office|1587|science|university,~gazette||
chapbooks|The Penny Library|1603|books|river||
anatomy|Anatomists' Press|1619|science|herbal||
eastpaper|Eastern Paper Company|1628|origins|ragmill|The old mill closes in 1640|
newsroom|Gazette Newsroom|1636|news|gazette||
private|Private Press Circle|1647|arts|engravers||
maps|Atlas Workshop|1661|arts|engravers,~almanac||illustration-theodolite-psf
teachers|Teachers' Publishing Guild|1668|learning|school||
bookhall|Bookhall Company|1675|books|chapbooks,bindery|Printing and binding reunite|
observatory|Observatory Papers|1686|science|almanac||illustration-telescope-observer
evening|The Evening Messenger|1694|news|newsroom||
review|Northbridge Review|1702|arts|private||
medical|Medical Transactions|1711|science|anatomy||
children|Children's Book Room|1718|learning|teachers||
county|County Chronicle|1724|news|newsroom||
geography|Geographical Editions|1733|arts|maps||
readers|Readers' Subscription Library|1742|books|bookhall||
languages|Language Readers Office|1751|learning|teachers||
botany|Botanical Register|1758|science|herbal,~geography||
correspondents|Associated Correspondents|1766|news|evening,county|The two papers share a newsroom|
craft|Craft Book Studio|1774|arts|private||
mechanical|Mechanical Transactions|1781|science|observatory||illustration-cogwheel-psf
public|Public Editions|1788|books|bookhall,readers|A common publishing catalogue|
normal|Normal School Press|1795|learning|languages||
lithography|Lithographic Rooms|1803|arts|maps,craft|Two studios share the new workshop|
dispatch|The Daily Dispatch|1811|news|correspondents||
bulletin|District Bulletin|1817|news|county|An independent local paper|
primer|The Primer Company|1824|learning|children,normal||
learned|Learned Journals Union|1832|science|medical,mechanical|Medical and mechanical journals unite|
pictures|Illustrated Editions|1839|arts|lithography,~review||
cheap|Cheap Books Cooperative|1846|books|public||
rail|Roadside News Service|1854|news|dispatch||illustration-stagecoach
schoolatlas|School Atlas Office|1861|learning|primer,~geography||
naturalhistory|Natural History Monographs|1868|science|botany||
photo|Photogravure House|1876|arts|pictures|Image reproduction becomes its principal work|
regional|Regional News Agency|1882|news|rail,bulletin||
reference|Northbridge Reference Works|1889|books|public,~schoolatlas||
textbooks|United Textbook Press|1896|learning|primer,schoolatlas|The teaching lists combine|
research|Research Publications Trust|1904|science|learned,naturalhistory||
pocket|Pocket Editions|1912|books|cheap||
magazine|The Illustrated Monthly|1919|arts|pictures,~dispatch||
wire|The Wire Service|1927|news|regional||
audio|Spoken Book Library|1935|learning|textbooks||
facsimile|Facsimile Studio|1943|arts|photo||
universitybooks|University Books Group|1951|books|reference,~research||
scienceindex|Scientific Index Bureau|1958|science|research|Bibliographies become a separate service|
learning|Learning Media Trust|1966|learning|textbooks,audio||
syndicate|Independent News Syndicate|1973|news|wire,~magazine||
archive|Print Heritage Archive|1981|arts|facsimile|The studio becomes a preservation archive|
electronic|Electronic Editions Lab|1987|digital|universitybooks,~scienceindex||
openjournals|Open Journals Collective|1993|science|research,~electronic||
network|Network News Desk|1998|digital|syndicate,~electronic||
ebooks|Public E-book Library|2003|digital|electronic,pocket|The print and electronic lists join|
learningnet|Open Learning Network|2008|learning|learning,~ebooks||
digitalarchive|Digital Heritage Library|2013|digital|archive,~electronic||
commons|Northbridge Knowledge Commons|2019|digital|ebooks,digitalarchive,~openjournals|Two public collections unite|
localdesk|Local News Cooperative|2024|news|network|The local desk becomes independent|
'''


def data():
    groups = [
        ('origins', 'Early crafts', '#A6A18B'), ('books', 'General publishing', '#F7CD26'),
        ('science', 'Scientific publishing', '#77BDDD'), ('learning', 'Education', '#B58CC9'),
        ('arts', 'Art and illustration', '#F56550'), ('news', 'News', '#98BD92'),
        ('digital', 'Digital collections', '#FF9D28')]
    result = dict(id='northbridge-publishing', title='Six Centuries of Northbridge Publishing',
                  design='editorial', mode='lineage', layout='branches',
                  groups=[dict(id=i, label=label, color=color) for i, label, color in groups], nodes=[], edges=[],
                  source_note='Original fictional history. All institutions, dates and relationships are invented; source drawings are illustrative.',
                  reading_note='Solid paths: institutional descent or a stated merger. Dotted arrows: influence. Dates: founding or reorganisation. Spacing is schematic.')
    landmarks = {'common', 'university', 'bookhall', 'correspondents', 'public', 'lithography', 'learned', 'textbooks', 'research', 'electronic', 'commons'}
    for line in RECORDS.strip().splitlines():
        nid, label, founded, group, predecessors, detail, icon = line.split('|')
        record = dict(id=nid, label=label, founded=int(founded), date_label=founded, group=group, detail=detail)
        if nid in landmarks:
            record['emphasis'] = True
        if icon.strip():
            record['icon'] = icon.strip()
        result['nodes'].append(record)
        for parent in filter(None, predecessors.split(',')):
            source = parent.lstrip('~')
            result['edges'].append(dict(id=source+'-to-'+nid, source=source, target=nid,
                                        kind='influence' if parent.startswith('~') else 'branch'))
    by_id = {n['id']: n for n in result['nodes']}
    assert all(by_id[e['source']]['founded'] < by_id[e['target']]['founded'] for e in result['edges'])
    return result


def main():
    result = data()
    output = ROOT / 'projects/usefulcharts-style/artifacts/reviews/local-stories-v31/publishing-input.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    task_data = {key: value for key, value in result.items() if key not in ('design', 'mode', 'layout')}
    prompt = '''Create a polished, editable educational poster about the fictional history of Northbridge publishing using the supplied records. It should have the compact spatial hierarchy, branching histories, semantic colors, varied emphasis and legible connections associated with UsefulCharts. Give the subject a coherent overall composition, with complete individual stories and clearly distinguishable influence arrows.

Keep all 70 institutions, every supplied name, founding year, explanatory note, category, emphasis choice, illustration identity and all 97 typed relationships. The seven categories and their colors are fixed. The history is fictional and that must remain visible. Preserve the distinction between structural descent or stated mergers and influence. Spacing can be schematic. Do not invent extra records, remove notes, or turn unknown facts into assertions.

Deliver exactly result/source.json, result/poster.svg, result/poster.html, result/layout.json, result/browser.json, result/poster.png and result/review.md. The source must remain editable, and visible names and notes must remain editable SVG text. Open the final PNG with the image tool, inspect the composition and a busy merger, repair any problems you find, then write a candid critique in result/review.md. Correct geometry alone does not prove visual parity.

Use only the supplied skill bundle and normal local tools. Treat skills/usefulcharts-style/ as read-only. Keep all generated files inside this workspace. Do not inspect repository files, acceptance examples, other skills, earlier runs or external task directories. No network research is needed for this explicitly fictional source. The exact task data follows.

```json
'''+json.dumps(task_data,indent=2)+'''\n```
'''
    (ROOT / 'evaluations/pi-prompts/usefulcharts-data-first-publishing.md').write_text(prompt, encoding='utf-8')
    tiny = dict(id='unplaced-collections', title='THE PUBLIC COLLECTIONS', design='editorial', mode='lineage', layout='branches',
                source_note='Fictional test history.', groups=[dict(id='g',label='Collections',color='#77BDDD')],
                nodes=[dict(id=nid,label=label,founded=year,date_label=str(year),group='g',detail=detail)
                       for nid,label,year,detail in [('cabinet','Common Cabinet',1700,''),('east','Eastern Reading Room',1730,''),
                           ('west','Western Book Society',1741,''),('library','United Public Library',1780,'The two bodies unite')]],
                edges=[dict(id=f'e{i}',source=a,target=b,kind='branch') for i,(a,b) in enumerate([
                    ('cabinet','east'),('cabinet','west'),('east','library'),('west','library')])])
    smoke='''Run this exact command-contract control with the read-only usefulcharts-style bundle. Write the JSON below unchanged to draft.json, then execute these commands in order:

```sh
uv run --script skills/usefulcharts-style/scripts/compose_branching_history.py draft.json --output result/source.json --report result/composition.json
uv run --script skills/usefulcharts-style/scripts/render_chart.py result/source.json --svg result/poster.svg --html result/poster.html --report result/layout.json
uv run --script skills/usefulcharts-style/scripts/audit_chart.py result/poster.svg --source result/source.json --report result/browser.json --png result/poster.png
```

Keep all files in this workspace. Do not read acceptance examples, other skills, repository files or external task directories. Do not change the JSON or the skill. This is a command control: image inspection is not required. The final report must have no hard findings and no unrelated-shared-run warning.

```json
'''+json.dumps(tiny,indent=2)+'\n```\n'
    (ROOT / 'evaluations/pi-prompts/usefulcharts-data-first-contract.md').write_text(smoke, encoding='utf-8')
    print(json.dumps(dict(nodes=len(result['nodes']), edges=len(result['edges']), output=str(output))))


if __name__ == '__main__':
    main()
