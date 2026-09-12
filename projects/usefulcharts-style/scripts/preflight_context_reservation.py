#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["osqp>=1,<2", "numpy>=2,<3", "scipy>=1.14,<2"]
# ///
"""Replay the complete failing family with context reserved before placement."""

import json
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[3];sys.path.insert(0,str(root/'skills/usefulcharts-style/scripts'))
from space_family_branches import space_branches
from editorial_poster import EditorialPoster
from render_chart import viewer

run=root/'evaluations/runs/usefulcharts-v21-family-landmarks-20260912-gpt55-1/workspace/result/source.json'
source=json.loads(run.read_text(encoding='utf-8'));source['layout']='cohorts'
for key in ['width','height','cohort_top','cohort_bottom','cohort_weights','_cohort_key','font_size','cohort_gap','partner_gap']:source.pop(key,None)
for node in source['nodes']:
    for key in ['x','y','width','height','style','size','detail_size','detail_position','icon_width']:node.pop(key,None)
for annotation in source['annotations']:
    for key in ['dx','dy']:annotation.pop(key,None)
data,spacing=space_branches(source,reserve_context=True)
svg,layout=EditorialPoster(data).render()
out=root/'projects/usefulcharts-style/artifacts/reviews/reserved-context-preflight';out.mkdir(parents=True,exist_ok=True)
for name,value in [('draft.json',source),('source.json',data),('spacing.json',spacing),('layout.json',layout)]:
    (out/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
(out/'poster.svg').write_text(svg,encoding='utf-8');(out/'poster.html').write_text(viewer(svg,data['title']),encoding='utf-8')
print(json.dumps(layout))
