#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Apply compact panel composition to the unchanged factual inventories."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT.parents[1]/'skills/usefulcharts-style/scripts'))
from create_panel_poster import build

def main():
    for case,cols in [('bsd',2),('instruments',2)]:
        data=json.loads((ROOT/'data'/f'{case}.json').read_text(encoding='utf-8'))
        data['position_semantics']='Panels group related records. Vertical order follows local branches; neither axis measures elapsed time.' if case=='bsd' else 'Panels group sound-production mechanisms. Indented branches mean contains; these codes are not dates.'
        if case=='bsd':
            data['reading_note']='Solid branches show local lineage. Numbered arrows are paired links with named endpoints and explicit types: lineage or code contribution. Year ranges retain disputed dates; 4.1bBSD remains undated.'
        else:
            data['eyebrow']='A CLASSIFICATION OF SOUND'
        out=ROOT/'artifacts'/'revision-2'/case
        try:result=build(data,out,cols,520);print(json.dumps(dict(case=case,**result)))
        except ValueError as error:print(json.dumps(dict(case=case,status='fail',error=str(error))))

if __name__=='__main__':main()
