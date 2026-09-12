#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely>=2,<3"]
# ///
"""Regenerate the three original synthetic poster acceptance fixtures."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

from poster_briefs import genealogy, lineage, timeline


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renderer",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument("--only",choices=("aurelian-families","atlas-of-inquiry","five-regional-histories"))
    args=parser.parse_args()
    sys.path.insert(0,str(args.renderer.resolve().parent))
    args.output.mkdir(parents=True,exist_ok=True)
    manifest={"id":"usefulcharts-style","data_provenance":"Original synthetic fixtures; no UsefulCharts artwork is redistributed.","items":[]}
    cards=[]
    for data in (genealogy(),lineage(),timeline()):
        name=data["id"]
        source=args.output/f"{name}.json"
        if not args.only or name==args.only:
            source.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
            subprocess.run([sys.executable,str(args.renderer),str(source),"--svg",str(args.output/f"{name}.svg"),"--html",str(args.output/f"{name}.html")],check=True)
        manifest["items"].append({"id":name,"patternId":data["pattern_id"],"mode":data["mode"],"svg":f"{name}.svg","source":f"{name}.json"})
        cards.append(f'<article id="{data["pattern_id"]}" data-example-id="{name}" data-pattern-id="{data["pattern_id"]}"><a href="{name}.html"><img src="{name}.svg" alt="{html.escape(data["title"])} — synthetic {data["mode"]} poster" loading="lazy"></a><div><p class="type">{data["mode"]}</p><h2>{html.escape(data["title"].title())}</h2><p>{html.escape(data["subtitle"])}</p><nav><a href="{name}.html">Explore poster</a><a href="{name}.svg">SVG</a><a href="{name}.json">Source data</a></nav></div></article>')
    (args.output/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    (args.output/"index.html").write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="example-set-id" content="usefulcharts-style"><title>Educational Poster Studies</title><style>
*{box-sizing:border-box}body{margin:0;background:#f2efdf;color:#242720;font:17px/1.6 Arial,sans-serif}header,main,footer{max-width:1300px;margin:auto;padding:32px}header{padding-top:64px}h1{font-size:clamp(32px,5vw,62px);line-height:1.08;margin:12px 0 24px;letter-spacing:-1px}header p{max-width:820px}.eyebrow,.type{text-transform:uppercase;letter-spacing:2px;font-size:13px;font-weight:bold;color:#813b37}main{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}article{background:#fffdf4;border:1px solid #d4cdbc;border-radius:5px;overflow:hidden}article:target{outline:4px solid #813b37}article img{width:100%;display:block}article div{padding:24px}h2{font-size:24px;line-height:1.2}nav{display:flex;gap:18px;flex-wrap:wrap}a{color:#70332f;text-underline-offset:4px}article>a{display:block}article>a:focus{outline:4px solid #333}footer{font-size:15px;color:#575b50}@media(max-width:850px){main{grid-template-columns:1fr}article{max-width:600px;margin:auto}}
</style></head><body><header><a href="../../">All skill examples</a><p class="eyebrow">UsefulCharts-style · Original SVG studies</p><h1>Connected knowledge,<br>composed as a poster.</h1><p>Three original studies in genealogical structure, branching knowledge, and parallel history. They explore the spatial hierarchy, semantic colors, compact typography, and routed connections of educational wall charts.</p><p>All data is synthetic. These studies are inspired by the visual organization of <a href="https://usefulcharts.com/">UsefulCharts</a> and are independently authored; they are not UsefulCharts products.</p></header><main>'''+"".join(cards)+'''</main><footer>Open a poster to inspect the full-size SVG with zoom controls. Source JSON preserves the entities, relationships, category colors, and authored placements. The skill contains compact recipes and a browser geometry audit.</footer></body></html>''',encoding="utf-8")
    print(f"Built {len(cards)} original educational poster examples.")


if __name__=="__main__":
    main()
