#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Full-frame composition contracts and an illustrative multi-view atlas."""
from __future__ import annotations

import copy
import math
import re
from attention_contract import DEFAULT_ATTENTION, validate_attention


def panel(kind, rect, producer="d3"):
    return {"kind": kind, "producer": producer, "rect": rect}


def m(kind, rect):
    return panel(kind, rect, "mermaid")


HALF = [[0, 0, .5, 1], [.5, 0, .5, 1]]
THIRDS = [[0, 0, 1/3, 1], [1/3, 0, 1/3, 1], [2/3, 0, 1/3, 1]]
QUADS = [[0, 0, .5, .5], [.5, 0, .5, .5], [0, .5, .5, .5], [.5, .5, .5, .5]]


def scene(sid, seconds, panels, question, pairing):
    return {"id": sid, "seconds": seconds, "panels": panels, "question": question, "pairing": pairing}


SCENES = [
    scene("process", 10, [m("flowchart", HALF[0]), panel("network", HALF[1])], "What connects the four stages?", "Recommended: dependency notation and a spatial network share node IDs."),
    scene("interactions", 11, [m("sequence", [0,0,.5,1]), panel("scatter", [.5,0,.5,.6]), panel("histogram", [.5,.6,.5,.4])], "How do message latencies vary?", "Recommended: message order, individual observations and their distribution."),
    scene("states", 10, [m("state", [0,0,.45,1]), panel("stacked-area", [.45,0,.55,.65]), panel("event-raster", [.45,.65,.55,.35])], "How do states accumulate over observations?", "Recommended: legal transitions and measured occupancy; raster preserves event timing."),
    scene("hierarchy", 11, [m("mindmap", THIRDS[0]), panel("radial-tree", THIRDS[1]), panel("circle-pack", THIRDS[2])], "Which stages belong to each branch?", "Conditional: mindmap and tree are redundant; packing adds magnitude."),
    scene("parts", 11, [m("treemap", [0,0,1,.45]), panel("sunburst", [0,.45,.5,.55]), panel("treemap", [.5,.45,.5,.55])], "How is the 42-day total divided?", "Comparison control: prefer one treemap plus a linked table for production."),
    scene("flows", 13, [m("sankey", [0,0,.5,1]), panel("chord", [.5,0,.5,.62]), panel("matrix", [.5,.62,.5,.38])], "Which directed transfers carry the most units?", "Recommended: Sankey for direction, matrix for precise cells; chord is a dense overview alternative."),
    scene("records", 14, [m("er", [0,0,.5,.48]), m("class", [.5,0,.5,.48]), panel("table-bars", [0,.48,1,.52])], "How do schemas connect to actual stage records?", "Recommended: schema or class contract with a linked table and bars; use both contracts only for comparison."),
    scene("schedule", 11, [m("gantt", [0,0,1,.46]), panel("bump", [0,.46,.5,.54]), panel("intervals", [.5,.46,.5,.54])], "Which stages occupy the schedule and change rank?", "Recommended: Gantt with actual intervals; bump adds rank, not duration."),
    scene("history", 11, [m("timeline", [0,0,1,.36]), panel("streamgraph", [0,.36,.5,.64]), panel("lines", [.5,.36,.5,.64])], "What happened when the histories changed?", "Recommended: event context with absolute lines; streamgraph is secondary because its baseline moves."),
    scene("tradeoffs", 11, [m("quadrant", [0,0,.5,.65]), panel("parallel", [.5,0,.5,.65]), panel("boxplot", [0,.65,1,.35])], "How do effort, impact and latency differ?", "Conditional: quadrant for decisions, parallel coordinates for tradeoffs, boxplot for spread."),
    scene("profiles", 11, [m("radar", [0,0,.5,1]), m("xy", [.5,0,.5,.5]), panel("dumbbell", [.5,.5,.5,.5])], "How do baseline and current values differ?", "Conditional: radar shows shape; aligned dumbbells support more precise comparisons."),
    scene("experience", 10, [m("journey", [0,0,1,.55]), m("kanban", [0,.55,1,.45])], "Where is work and how does the experience feel?", "Recommended only when tasks and actors refer to the same process."),
    scene("contracts", 11, [m("git", [0,0,1,.36]), m("requirement", [0,.36,.5,.64]), m("block", [.5,.36,.5,.64])], "Which revision satisfies the delivery constraint?", "Conditional: connect the revision, requirement and responsible component explicitly."),
    scene("deployment", 11, [m("architecture", HALF[0]), panel("globe", HALF[1])], "Where do the linked services run?", "Recommended: service topology and genuine geographic coordinates answer different questions."),
    scene("shares", 10, [m("pie", THIRDS[0]), panel("donut", THIRDS[1]), panel("lollipop", THIRDS[2])], "Which stage contributes the largest share?", "Comparison control: pie and donut repeat the encoding; lollipop is easier to compare precisely."),
    scene("space", 12, [panel("voronoi", QUADS[0]), panel("delaunay", QUADS[1]), panel("contours", QUADS[2]), panel("beeswarm", QUADS[3])], "How do the same spatial samples relate?", "Recommended for geometry: cells, neighbor graph, density and one-dimensional projection share samples."),
]

DEFAULT_ATLAS = {
    "schemaVersion": 1, "mode": "atlas", "width": 1920, "height": 1080, "fps": 30,
    "palette": "colorset1", "paletteReason": "Neutral geometry; red marks shared focus. No extra category hues are needed.",
    "dataStatus": "synthetic", "unit": "days", "presentation": {"contextLabels": {}},
    "attention": copy.deepcopy(DEFAULT_ATTENTION),
    "camera": {"columns": 4, "transitionSeconds": 1.8, "overviewSeconds": 7},
    "scenePlan": SCENES,
    "rows": [
        {"id": "intake", "label": "Intake", "before": 18, "after": 12, "trend": [18,17,16,15,13,12]},
        {"id": "review", "label": "Review", "before": 14, "after": 8, "trend": [14,13,12,10,9,8]},
        {"id": "build", "label": "Build", "before": 24, "after": 16, "trend": [24,22,23,20,18,16]},
        {"id": "release", "label": "Release", "before": 10, "after": 6, "trend": [10,10,9,8,7,6]},
    ],
    "flows": [[0,12,0,6],[0,0,8,0],[0,0,0,16],[0,0,0,0]],
    "schedule": [[0,2],[2,5],[5,9],[9,12]],
    "sites": [
        {"id":"intake","label":"New York","longitude":-74.006,"latitude":40.713},
        {"id":"review","label":"London","longitude":-.128,"latitude":51.507},
        {"id":"build","label":"Madrid","longitude":-3.704,"latitude":40.417},
        {"id":"release","label":"Santiago","longitude":-70.669,"latitude":-33.449}
    ],
    "assets": {"diagrams": {p["kind"]: f"assets/diagrams/{p['kind']}.svg" for s in SCENES for p in s["panels"] if p["producer"] == "mermaid"}}
}


def partition_check(panels):
    """Prove an axis-aligned partition by checking every induced elementary cell."""
    if not isinstance(panels, list) or not 1 <= len(panels) <= 4:
        raise ValueError("Each scene needs 1–4 full-frame panels.")
    xs, ys = {0., 1.}, {0., 1.}
    for p in panels:
        if not isinstance(p,dict):
            raise ValueError("Each panel must be an object.")
        rect = p.get("rect", [])
        if len(rect) != 4 or any(isinstance(v, bool) or not isinstance(v, (int,float)) or not math.isfinite(v) for v in rect):
            raise ValueError("Panel rect requires four finite normalized coordinates.")
        x,y,w,h = rect
        if min(x,y) < -1e-9 or min(w,h) <= 0 or x+w > 1+1e-9 or y+h > 1+1e-9:
            raise ValueError("Panel rect must stay inside the complete frame.")
        xs.update((x,x+w)); ys.update((y,y+h))
    xs,ys = sorted(xs),sorted(ys)
    for x0,x1 in zip(xs,xs[1:]):
        for y0,y1 in zip(ys,ys[1:]):
            if (x1-x0)*(y1-y0) < 1e-12:
                continue
            x,y = (x0+x1)/2,(y0+y1)/2
            count = sum(px-1e-10 <= x <= px+pw+1e-10 and py-1e-10 <= y <= py+ph+1e-10 for px,py,pw,ph in (p["rect"] for p in panels))
            if count != 1:
                raise ValueError("Panels must cover the entire frame exactly once, without gaps or overlap.")
    return {"coveredArea": sum(p["rect"][2]*p["rect"][3] for p in panels), "gaps": 0, "overlaps": 0}


def validate_atlas(raw):
    s = copy.deepcopy(raw)
    if not isinstance(s,dict):
        raise ValueError("Atlas story must be an object.")
    if s.get("schemaVersion") != 1 or s.get("mode") != "atlas":
        raise ValueError("Expected the version-1 atlas story.")
    for key in ("width","height"):
        v = s.get(key)
        if not isinstance(v,int) or isinstance(v,bool) or v < 320 or v%2:
            raise ValueError("Atlas dimensions must be even integers >=320.")
    if s["width"]*9 != s["height"]*16 or s.get("fps") not in (24,25,30,60):
        raise ValueError("Atlas requires 16:9 and 24, 25, 30 or 60 fps.")
    if s.get("palette") not in ("colorset1","colorset2") or (s["palette"]=="colorset2" and not s.get("paletteReason","").strip()):
        raise ValueError("Choose a supported palette and explain colorset2 when needed.")
    if s.get("dataStatus") not in ("synthetic","supplied") or not isinstance(s.get("unit"),str) or not s["unit"].strip():
        raise ValueError("Specify dataStatus and a nonempty unit.")
    # These illustrative native diagrams use these exact shared semantic records.
    # A new dataset must regenerate its native diagrams and adapt the scene contract.
    for key in ("rows","flows","schedule","sites"):
        if s.get(key) != DEFAULT_ATLAS[key]:
            raise ValueError(f"The atlas template's {key} must match its native diagrams; adapt the data contract and regenerate the diagram set for new data.")
    plan = s.get("scenePlan",[])
    ids, supported = set(), {p["producer"]+":"+p["kind"] for scene in SCENES for p in scene["panels"]}
    camera=s.get("camera",{})
    if not isinstance(camera,dict):
        raise ValueError("camera must be an object.")
    transition, overview=camera.get("transitionSeconds"),camera.get("overviewSeconds")
    if camera.get("columns") != 4:
        raise ValueError("The atlas template requires four world columns.")
    for value in (transition,overview):
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value < .5:
            raise ValueError("Camera timing must be finite and at least .5 seconds.")
    if overview < 4:
        raise ValueError("The overview needs at least four seconds.")
    if not isinstance(plan,list) or not 1 <= len(plan) <= 16:
        raise ValueError("Choose 1–16 atlas scenes.")
    start, beats = 0., []
    for i,sc in enumerate(plan):
        if not isinstance(sc,dict):
            raise ValueError("Every scene must be an object.")
        sid=sc.get("id","")
        if not isinstance(sid,str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,39}",sid) or sid in ids or sid=="overview":
            raise ValueError("Scene IDs must be unique lowercase hyphen-case identifiers.")
        ids.add(sid)
        part=partition_check(sc.get("panels"))
        for p in sc["panels"]:
            if p.get("producer","")+":"+p.get("kind","") not in supported:
                raise ValueError("Unsupported atlas panel kind/producer.")
        dur=sc.get("seconds")
        if isinstance(dur,bool) or not isinstance(dur,(int,float)) or not math.isfinite(dur) or dur < transition+5:
            raise ValueError("Each scene needs its camera transition plus at least five seconds for reading.")
        row=i//4; column=i%4 if row%2==0 else 3-i%4
        beats.append({"id":sid,"start":start,"duration":dur,"end":start+dur,"cell":[column,row],"partition":part})
        start+=dur
    beats.append({"id":"overview","start":start,"duration":overview,"end":start+overview})
    start+=overview
    if abs(start*s["fps"]-round(start*s["fps"])) > 1e-7:
        raise ValueError("Total duration must contain an integral number of frames.")
    presentation=s.setdefault("presentation",{})
    if not isinstance(presentation,dict):
        raise ValueError("presentation must be an object.")
    context=presentation.setdefault("contextLabels",{})
    if not isinstance(context,dict) or any(key not in ids|{"overview"} for key in context) or any(not isinstance(v,str) or not v.strip() or len(v)>48 or len(v.split())>6 for v in context.values()):
        raise ValueError("Context labels require explicit short text for existing scene IDs.")
    s.update(beats=beats,duration=start)
    return validate_attention(s)


def coverage(story):
    panels=[p for s in story["scenePlan"] for p in s["panels"]]
    return {"mermaidFamilies":sorted({p["kind"] for p in panels if p["producer"]=="mermaid"}),
            "d3Forms":sorted({p["kind"] for p in panels if p["producer"]=="d3"}),
            "panels":len(panels),"scenes":len(story["scenePlan"]),"scope":"Distinct forms in this atlas, not all D3 APIs or every Mermaid version.",
            "pairings":[{"id":s["id"],"question":s.get("question"),"assessment":s.get("pairing")} for s in story["scenePlan"]]}
