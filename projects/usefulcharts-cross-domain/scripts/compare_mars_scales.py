#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Compare page geometry while keeping typography and dates constant."""
import json
from build_mars import inventory, make, ROOT
rows=[]
for scale in [58,70,85,100,120,140,160]:
    source=inventory();source['scale']['pixels_per_year']=scale;source['width']=105+47*scale+185
    _,packed=make(source,True);layout=packed['layout'];height=layout['height']+180
    rows.append(dict(scale=scale,width=source['width'],height=height,area=round(source['width']*height),tracks=layout['row_count'],aspect=round(source['width']/height,2)))
(ROOT/'artifacts/mars-scale-study.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf-8')
print(json.dumps(rows))
