#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regenerate the three original synthetic poster acceptance fixtures."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

COLORS = ["#F18C79", "#77BEDB", "#F4C948", "#A6C49B", "#BE9CCB", "#CDC7B3"]


def base(identifier, title, mode, labels):
    return {
        "id": identifier, "title": title, "mode": mode,
        "width": 1800, "height": 2400,
        "groups": [{"id": f"g{i}","label":label,"color":COLORS[i]} for i,label in enumerate(labels)],
        "source_note": "Synthetic study by Codex, 2026. All names, institutions, relationships, and dates are invented.",
    }


def genealogy():
    d = base("aurelian-families", "FAMILIES OF THE AURELIAN COAST", "genealogy", ["House Alder", "House Bay", "House Cress", "House Dell", "House Elm"])
    d.update(pattern_id="usefulcharts-dynastic-genealogy",subtitle="Five houses, seven generations, and their recorded partnerships",columns=10,
             rows=[f"Generation {i+1}" for i in range(7)],nodes=[],unions=[],edges=[],
             reading_note="Double lines join partners; children descend from the junction. Dashed descent is uncertain. Generations are schematic; unlinked spouses have no recorded ancestry here.")
    names = [
        ["Arden", "Mira", "Basil", "Nora", "Celia", "Orin", "Dorian", "Pia", "Elian", "Rosa"],
        ["Alaric", "Sera", "Brina", "Tarin", "Corin", "Una", "Dalia", "Vero", "Emil", "Willa"],
        ["Aster", "Yara", "Beren", "Zora", "Calla", "Ivo", "Dara", "Jorin", "Eris", "Kira"],
        ["Alden", "Liora", "Briar", "Marek", "Cora", "Neri", "Davin", "Opal", "Esme", "Perrin"],
        ["Ansel", "Rhea", "Bela", "Sorin", "Carys", "Tessa", "Demi", "Uria", "Evan", "Veda"],
        ["Ada", "Wren", "Bram", "Xara", "Ciro", "Ysol", "Dena", "Zeph", "Enid", "Isla"],
        ["Ari", "Jessa", "Bryn", "Kelan", "Cleo", "Luca", "Dion", "Mina", "Eira", "Nico"],
    ]
    houses = ["Alder","Bay","Cress","Dell","Elm"]
    for r,row_names in enumerate(names):
        for c,name in enumerate(row_names):
            d["nodes"].append({"id":f"p{r}-{c}","label":f"{name} {houses[c//2]}" if c%2==0 else name,
                "detail":f"b. {1640+r*28+(c%2)*3}","row":r,"col":c,"group":f"g{c//2}","emphasis":r in (0,6) and c%2==0})
        if r<6:
            for h in range(5):
                children = [f"p{r+1}-{h*2}"]
                if r==2 and h==1:
                    children = []
                d["unions"].append({"id":f"u{r}-{h}","partners":[f"p{r}-{h*2}",f"p{r}-{h*2+1}"],"children":children})
    # Two explicitly traced spouses create cross-house relationships; other spouses are untraced.
    d["unions"][5]["children"].append("p2-3")
    d["unions"][13]["children"].append("p3-9")
    d["edges"].append({"id":"uncertain-briar","source":"u2-1","target":"p3-2","kind":"uncertain"})
    d["lanes"] = [{"label":f"House {h}","group":f"g{i}","col":i*2,"span":2} for i,h in enumerate(houses)]
    return d


def lineage():
    labels = ["Astronomy", "Navigation", "Mechanics", "Optics", "Cartography", "Common origins"]
    d = base("atlas-of-inquiry", "AN ATLAS OF SHARED INQUIRY", "lineage", labels)
    d.update(pattern_id="usefulcharts-branching-lineage",subtitle="A fictional history of five traditions of knowledge",columns=10,
             node_width=140,
             rows=["Origins", "Traditions", "Early schools", "Branches", "Workshops", "Institutes", "Networks", "Modern schools", "New directions"],
             nodes=[{"id":"origin","label":"Common Inquiry","detail":"Observing • making • recording","row":0,"col":4.5,"group":"g5","emphasis":True}],edges=[],
             reading_note="Solid paths show an institutional branch. Dotted arrows show influence between traditions. Rows are schematic stages, not a uniform measure of time.")
    trunks = ["Sky Records","Coastal Pilots","Practical Arts","Study of Light","Land Surveys"]
    branches = [
        ["Star Tables","Lunar School","Open-Sky Hall","Calendar House","Meridian Circle","Night Observatory","Orbit Institute","Variable Stars","Sky Network","Deep-Sky Lab","Stellar Commons","Timekeeping Lab","Orbital Mapping","Night-Sky Archive"],
        ["Tidal Pilots","Bluewater School","Coastal Routes","Ocean Workshop","Current Institute","Compass Hall","Sea Academy","Harbor Network","Open Passage","Pelagic Institute","Route Commons","Voyage Archive","Current Atlas","Navigation Lab"],
        ["Lever School","Water Engines","Wheel Workshop","Clockmakers","Motion Institute","Engine School","Power Network","Precision Hall","Kinetic Lab","Systems College","Open Machines","Mechanism Archive","Resilient Motion","Energy Workshop"],
        ["Mirror School","Lens Makers","Prism Workshop","Glass Institute","Spectrum Hall","Imaging School","Wave Institute","Light Network","Photon Lab","Visual College","Open Optics","Lens Archive","Coherent Light","Adaptive Imaging"],
        ["Survey School","Map Scribes","Terrain Guild","Coast Atlas","Geodesy Hall","Map Institute","Grid Network","Relief School","Earth Lab","Spatial College","Open Maps","Regional Archive","Shared Terrain","Living Atlas"],
    ]
    for g in range(5):
        tid=f"t{g}"
        d["nodes"].append({"id":tid,"label":trunks[g],"detail":"Early tradition","row":1,"col":2*g+.5,"group":f"g{g}","emphasis":True})
        d["edges"].append({"id":f"root-{g}","source":"origin","target":tid,"kind":"branch"})
        for r in range(2,9):
            for branch in range(2):
                nid=f"n{r}-{g}-{branch}"
                d["nodes"].append({"id":nid,"label":branches[g][(r-2)*2+branch],"detail":f"c. {1420+r*55+g*7+branch*9}","row":r,"col":g*2+branch,"group":f"g{g}","emphasis":r==8})
                d["edges"].append({"id":f"e{r}-{g}-{branch}","source":tid if r==2 else f"n{r-1}-{g}-{branch}","target":nid,"kind":"branch"})
    for source,target in [("n3-0-1","n4-1-0"),("n5-2-1","n6-3-0"),("n6-3-1","n7-4-0")]:
        d["edges"].append({"id":f"influence-{source}","source":source,"target":target,"kind":"influence"})
    return d


def timeline():
    labels=["Riverlands","Highlands","Coastlands","Islands","Northlands"]
    d=base("five-regional-histories","FIVE REGIONS THROUGH TIME","timeline",labels)
    d.update(pattern_id="usefulcharts-parallel-history",subtitle="Comparing the same 1,000 years across five fictional regions",frame_color="#575444",
             time={"start":1000,"end":2000,"step":100},lanes=[{"id":f"l{i}","label":v} for i,v in enumerate(labels)],periods=[],
             reading_note="All intervals use one linear year scale. Matching horizontal positions in time are contemporaneous. Adjacent phases do not imply descent or political continuity.")
    names=[
        ["River Settlements","Canal League","Delta Cities","Valley Union","River Republic"],
        ["Hill Communities","Mountain Houses","Highland Council","Ridge Federation","Plateau Assembly"],
        ["Coastal Harbors","Maritime League","Port Cities","Coastal Union","Harbor Republic"],
        ["Island Villages","Voyaging Houses","Island Council","Archipelago League","Island Assembly"],
        ["Northern Camps","Forest Towns","Northern Council","Lake Federation","Northern Commons"],
    ]
    years=[[1000,1180,1390,1580,1780,2000],[1000,1230,1420,1660,1840,2000],[1000,1160,1380,1620,1810,2000],[1000,1220,1450,1640,1850,2000],[1000,1190,1410,1670,1830,2000]]
    for g in range(5):
        for i,label in enumerate(names[g]):
            d["periods"].append({"id":f"era-{g}-{i}","label":label,"group":f"g{g}","lane":f"l{g}","start":years[g][i],"end":years[g][i+1]})
    return d


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--renderer",type=Path,required=True)
    parser.add_argument("--output",type=Path,default=Path(__file__).resolve().parent)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    manifest={"id":"usefulcharts-style","data_provenance":"Original synthetic fixtures; no UsefulCharts artwork is redistributed.","items":[]}
    cards=[]
    for data in (genealogy(),lineage(),timeline()):
        name=data["id"]
        source=args.output/f"{name}.json"
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
