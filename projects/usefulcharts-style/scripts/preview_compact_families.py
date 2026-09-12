#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare author repairs against preserved small-family v11 forward outputs."""

import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
DEST=ROOT/'projects/usefulcharts-style/artifacts/compact-families'
SKILL=ROOT/'skills/usefulcharts-style'


def main():
    cases=[('cohorts','usefulcharts-cohorts-v11-20260911-gpt55-1','result/source.json'),
           ('transport','usefulcharts-transport-v11-20260911-gpt55-1','museum/data.json')]
    for name,run,source in cases:
        data=json.loads((ROOT/'evaluations/runs'/run/'workspace'/source).read_text(encoding='utf-8'))
        for key in ('width','height','font_size','imprint','cohort_top','cohort_bottom','cohort_gap','partner_gap','cohort_weights','annotations'):
            data.pop(key,None)
        if name=='cohorts':
            data['title']='The Alder and Vey Families'
            data['groups']=[g for g in data['groups'] if g['id']!='convergence']
            for node in data['nodes']:
                if node['label'] in ('June','Leo','Iris'):node['group']='vey'
                node['detail']=node['detail'].split(';')[0]
                for key in ('width','style','size','detail_size','x','y'):node.pop(key,None)
            data['source_note']='Synthetic people and dates supplied for a family study.'
            data['reading_note']='Double lines: partners. Descendants begin at the parental union. Coral: Alder; blue: Vey. Spacing is schematic.'
        else:
            data['layout']='compact'
            for period in data['periods']:
                for key in ('offset','bar_width','size','detail'):period.pop(key,None)
            data['source_note']='Synthetic Riverton transport phases and dates.'
            data['reading_note']='All networks use the same year scale. Colored ribbons show duration; phases do not assert genealogical descent.'
        folder=DEST/name;folder.mkdir(parents=True,exist_ok=True)
        brief=folder/'source.json';brief.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        subprocess.run(['uv','run','--script',str(SKILL/'scripts/render_chart.py'),str(brief),'--svg',str(folder/'poster.svg'),'--html',str(folder/'poster.html'),'--report',str(folder/'layout.json')],check=True)
        subprocess.run(['uv','run','--script',str(SKILL/'scripts/audit_chart.py'),str(folder/'poster.svg'),'--source',str(brief),'--report',str(folder/'browser.json'),'--png',str(folder/'poster.png')],check=True)
    print('Author repairs rendered; the preserved forward outputs are unchanged.')


if __name__=='__main__':main()
