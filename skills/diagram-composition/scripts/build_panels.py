#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render common native SVG subdiagrams at allocated size with measured budgets."""

import argparse
import copy
import json
import math
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.dont_write_bytecode = True
from compose_diagram import element, identity, namespace, parse_svg, plan, require, tag, write_target
from palette_contract import require_color, text_on_fill

INK, MUTED, LINE, ACCENT = "#363636", "#696969", "#9c9c9c", "#9e1b32"
ICON_PATHS = {
    "editor": "M3 4H21V18H3ZM7 22H17M9 18V22M15 18V22",
    "assistant": "M3 4H21V17H10L5 21V17H3ZM8 9H16M8 13H13",
    "runner": "M3 4H21V20H3ZM7 9L10 12L7 15M13 15H17",
    "library": "M4 3H20V21H4ZM8 3V21M12 7H17M12 11H17",
    "cloud": "M6 19H18C24 19 24 11 18 11C17 3 6 3 6 11C0 11 0 19 6 19Z",
    "person": "M16 6A4 4 0 1 1 8 6A4 4 0 1 1 16 6M4 22V19C4 13 20 13 20 19V22",
    "grain": "M12 22V3M12 8C3 8 3 2 12 4M12 13C21 13 21 7 12 9M12 18C3 18 3 12 12 14",
    "seed": "M4 18C0 6 15 0 21 5C24 15 15 23 4 18ZM6 17L18 7",
    "plant": "M12 22V11M12 14C2 14 2 4 4 3C12 3 14 8 12 14ZM12 10C21 10 22 2 20 2C13 2 11 6 12 10",
    "inspect": "M16 10A6 6 0 1 1 4 10A6 6 0 1 1 16 10M15 15L22 22",
    "shelf": "M3 3V22M21 3V22M3 10H21M3 19H21M7 4V9M11 4V9M15 4V9",
    "envelope": "M2 5H22V20H2ZM2 5L12 13L22 5",
    "jar": "M6 2H18V6H6ZM5 7H19V22H5ZM5 11H19",
    "review": "M4 2H17L21 6V22H4ZM8 12L11 15L17 9",
}


def width_estimate(text, font):
    return sum(1.0 if ch in "MW@#%" else 0.73 if ch.isupper() else
               0.32 if ch in " il.,:;!|'" else 0.61 for ch in text) * font


def wrap(text, width, font):
    result = []
    for paragraph in str(text).split("\n"):
        line = ""
        for word in paragraph.split():
            require(width_estimate(word, font) <= width, f"Word '{word}' exceeds its text budget; shorten the label or allocate more width")
            trial = f"{line} {word}".strip()
            if line and width_estimate(trial, font) > width:
                result.append(line); line = word
            else:
                line = trial
        if line: result.append(line)
    return result


class Renderer:
    def __init__(self, width, height, font, directory, colors=None):
        self.w, self.h, self.f, self.directory = width, height, font, directory
        self.colors = colors or {}
        self.root = ET.Element(tag("svg"), {"viewBox": f"0 0 {width} {height}",
            "font-family": "Arial, sans-serif", "font-size": str(font), "fill": INK})
        self.ports, self.bindings, self.objects, self.count = {}, {}, {}, 0
        defs = element(self.root, "defs")
        marker = element(defs, "marker", {"id": "arrow", "viewBox": "0 0 10 10", "refX": 9, "refY": 5,
            "markerWidth": 7, "markerHeight": 7, "markerUnits": "userSpaceOnUse", "orient": "auto-start-reverse"})
        element(marker, "path", {"d": "M1 1L9 5L1 9Z", "fill": MUTED, "stroke": "none"})

    def rect(self, x, y, w, h, fill="#f7f7f7", stroke="none", radius=5):
        for paint in (fill, stroke):
            if paint != "none":
                require_color(paint)
        return element(self.root, "rect", {"x": x, "y": y, "width": w, "height": h, "rx": radius, "fill": fill, "stroke": stroke, "stroke-width": 1.2})

    def concept_color(self, data):
        cid = data.get("concept")
        if cid is None:
            return require_color(data["color"]) if "color" in data else None
        require(cid in self.colors, f"Unknown or undeclared colored concept: {cid}")
        color = self.colors[cid]
        require("color" not in data or (isinstance(data["color"], str) and data["color"].lower() == color),
                f"Local color overrides shared concept {cid}; use its canonical color")
        return color

    def bind_color(self, mark, data, channel):
        if data.get("concept") is not None:
            mark.set("data-color-concept", data["concept"])
            mark.set("data-color-channel", channel)
            if data.get("id"):
                mark.set("data-color-owner", data["id"])
            if channel == "stroke":
                mark.set("stroke-width", "2.4")
        return mark

    def label(self, text, x, y, width, height, bold=False, color=INK, center=False, top=False):
        lines = wrap(text, width, self.f)
        leading = self.f * 1.3
        require(len(lines) * leading <= height + 0.1, f"Text '{text}' needs {len(lines)*leading:.0f}px height but has {height:.0f}px; shorten or rebalance tracks")
        baseline = y + (0 if top else (height - len(lines) * leading) / 2) + self.f
        for line in lines:
            element(self.root, "text", {"x": x + width / 2 if center else x, "y": baseline,
                "font-size": self.f, "font-weight": 600 if bold else 400,
                "fill": color, "text-anchor": "middle" if center else "start"}, line)
            baseline += leading

    def icon(self, value, x, y, size, label, color=MUTED):
        self.count += 1
        if not value: return
        if value in ICON_PATHS:
            group = element(self.root, "svg", {"x": x, "y": y, "width": size, "height": size,
                "viewBox": "0 0 24 24", "role": "img", "aria-label": label, "data-icon": value})
            element(group, "title", text=label)
            element(group, "path", {"d": ICON_PATHS[value], "fill": "none", "stroke": color,
                "stroke-width": 1.6, "stroke-linecap": "round", "stroke-linejoin": "round"})
        else:
            path = Path(value)
            source, _, _ = parse_svg(path if path.is_absolute() else self.directory / path)
            source = namespace(source, f"icon-{self.count}-")
            for key, val in {"x": x, "y": y, "width": size, "height": size, "preserveAspectRatio": "xMidYMid meet", "aria-label": label}.items():
                source.set(key, str(val))
            source.set("data-brand-artwork", "true")
            self.root.append(source)

    def ports_for(self, nid, x, y, w, h, mark=None, kind="node", concept=None):
        identity(nid, "Node ID")
        self.objects[nid] = {"box":[x/self.w,y/self.h,w/self.w,h/self.h], "kind":kind}
        if mark is not None and mark.tag in {tag('ellipse'),tag('circle')}:
            self.objects[nid]['shape']='ellipse'
        if mark is None:
            mark=self.rect(x,y,w,h,"none","none",0)
        mark.set("data-node-id", nid)
        mark.set("data-node-kind", kind)
        if concept:
            mark.set("data-concept-id", concept)
        for suffix, point in {"left": [x, y+h/2], "right": [x+w, y+h/2], "top": [x+w/2, y], "bottom": [x+w/2, y+h]}.items():
            key = f"{nid}-{suffix}"
            require(key not in self.ports, f"Duplicate node ID: {nid}")
            self.ports[key] = [point[0] / self.w, point[1] / self.h]
            self.bindings[key] = {"object":nid,"side":suffix}

    def card_metrics(self, node, w):
        icon = node.get("icon")
        indent = 36 if icon else 0
        lines = wrap(node["label"], w-20-indent, self.f)
        details = wrap(node.get("detail", ""), w-20, self.f)
        label_h = max(28 if icon else 0, len(lines)*self.f*1.3)
        needed = 14 + label_h + (6+len(details)*self.f*1.3 if details else 0)
        return needed, label_h, details

    def card(self, node, x, y, w, h, color=None):
        icon = node.get("icon")
        indent = 36 if icon else 0
        shape=node.get('shape','rect')
        require(shape in {'rect','ellipse'},'Native node shape must be rect or ellipse')
        pad_x,pad_y=(w*.15,h*.15) if shape=='ellipse' else (10,0)
        text_w,text_h=w-2*pad_x,h-2*pad_y
        needed, label_h, details = self.card_metrics(node,text_w+20)
        require(needed <= text_h, f"Node '{node['label']}' needs {needed:.0f}px text height, has {text_h:.0f}px; shorten detail or increase its panel")
        accent = self.concept_color(node)
        fill = node.get('fill', accent or color or '#9c9c9c')
        stroke = node.get('stroke', 'none')
        foreground = text_on_fill(fill)
        box=element(self.root,'ellipse',{'cx':x+w/2,'cy':y+h/2,'rx':w/2,'ry':h/2,'fill':fill,'stroke':stroke,'stroke-width':1.2}) if shape=='ellipse' else self.rect(x,y,w,h,fill,stroke)
        self.bind_color(box,node,'fill')
        yy = y + pad_y + (text_h-needed)/2 + 7
        self.icon(icon, x+pad_x, yy+(label_h-26)/2, 26, node["label"], color=foreground)
        self.label(node["label"], x+pad_x+indent, yy, text_w-indent, label_h, bold=True, center=not bool(icon), color=foreground)
        if details: self.label(node["detail"], x+pad_x, yy+label_h+6, text_w, len(details)*self.f*1.3, center=True, color=foreground)
        self.ports_for(node["id"], x, y, w, h, mark=box, concept=node.get("concept"))

    def path(self, points, directed=False, label=None, owners=None):
        attrs = {"d": "M " + " L ".join(f"{x},{y}" for x,y in points), "fill": "none", "stroke": MUTED, "stroke-width": 1.8, "data-connector":"native"}
        if owners:
            attrs.update({"data-from-node":owners[0],"data-to-node":owners[1]})
        if directed: attrs["marker-end"] = "url(#arrow)"
        element(self.root, "path", attrs)
        # Labels are authored on cards or in the matrix; they never sit across a line.

    def point(self, name):
        p = self.ports[name]
        return [p[0]*self.w, p[1]*self.h]

    def hub(self, data):
        if data.get('enclosure'):
            enclosure=data['enclosure'];top=24+self.f*1.6
            outer=self.rect(4,4,self.w-8,self.h-8,'#f7f7f7','none')
            self.label(enclosure['label'],16,10,self.w-32,self.f*1.6,bold=True)
            child=Renderer(self.w-32,self.h-top-16,self.f,self.directory,self.colors)
            child.hub({k:v for k,v in data.items() if k!='enclosure'})
            fragment=namespace(child.root,'enclosed-')
            for key,value in {'x':16,'y':top,'width':child.w,'height':child.h}.items():fragment.set(key,str(value))
            self.root.append(fragment)
            for nid,obj in child.objects.items():
                x,y,w,h=obj['box'];self.objects[nid]={**obj,'box':[(16+x*child.w)/self.w,(top+y*child.h)/self.h,w*child.w/self.w,h*child.h/self.h]}
            for key,(x,y) in child.ports.items():self.ports[key]=[(16+x*child.w)/self.w,(top+y*child.h)/self.h]
            self.bindings.update(child.bindings)
            self.ports_for(enclosure['id'],4,4,self.w-8,self.h-8,mark=outer,kind='container')
            return
        peers, center = data["peers"], data["center"]
        require(2 <= len(peers) <= 4, "Native hub supports 2-4 peers; use a specialist for larger networks")
        h = min(76, self.h*0.29)
        cw, pw = self.w*0.30, self.w*0.28
        cx, cy = self.w*0.52, self.h*0.50
        spots = [(0.145,0.17),(0.145,0.83),(0.855,0.83),(0.855,0.17)][:len(peers)]
        if len(peers)==2:
            cw,pw=self.w*.33,self.w*.35
            cx=self.w*.77
            spots=[(.2,.23),(.2,.77)]
            h=min(96,self.h*.30)
        # Edges are below cards and touch the card boundaries, never their label centers.
        for peer,(px,py) in zip(peers,spots):
            x,y = px*self.w, py*self.h
            start = [x+pw/2 if x<cx else x-pw/2,y]
            end = [cx-cw/2 if x<cx else cx+cw/2,cy]
            self.path([start,end],owners=(peer["id"],center["id"]))
        self.card(center, cx-cw/2, cy-h/2, cw, h)
        for peer,(px,py) in zip(peers,spots): self.card(peer, px*self.w-pw/2, py*self.h-h/2, pw,h)

    def matrix(self, data):
        columns, rows = data["columns"], data["rows"]
        require(columns and rows and all(len(r["values"]) == len(columns)-1 for r in rows), "Matrix values must match columns after the row heading")
        note = data.get("note", "")
        note_h = self.f*2.6 if note else 0
        x,y,w,h = 4,4,self.w-8,self.h-8-note_h
        rh = h/(len(rows)+1)
        weights = data.get("columnWeights", [1.3]+[1]*(len(columns)-1))
        require(len(weights)==len(columns) and all(v>0 for v in weights), "Invalid matrix columnWeights")
        widths = [w*v/sum(weights) for v in weights]
        xx=x
        for col,cw in zip(columns,widths):
            self.rect(xx,y,cw,rh,"#f7f7f7",radius=0)
            self.label(col,xx+9,y+4,cw-18,rh-8,bold=True)
            xx+=cw
        for i,row in enumerate(rows):
            yy=y+(i+1)*rh
            xx=x
            row_box=self.rect(x,yy,w,rh,"#ffffff",radius=0)
            for j,(value,cw) in enumerate(zip([row["label"],*row["values"]],widths)):
                cell = {"text":row["label"], "id":row["id"], **{k:row[k] for k in ("concept","color") if k in row}} if j==0 else value if isinstance(value,dict) else {"text":str(value)}
                icon = row.get("icon") if j==0 else cell.get("icon")
                swatch = self.concept_color(cell)
                # Bound accents remain visible beside icons; official icon artwork is unchanged.
                show_swatch = swatch and (not icon or cell.get("concept"))
                indent = (32 if icon else 0) + (18 if show_swatch else 0)
                self.icon(icon,xx+7+(18 if show_swatch else 0),yy+(rh-24)/2,24,str(cell["text"]))
                if show_swatch:
                    self.bind_color(self.rect(xx+8,yy+(rh-11)/2,11,11,swatch,"none",1),cell,"fill")
                self.label(cell["text"],xx+9+indent,yy+4,cw-18-indent,rh-8,bold=j==0,color=INK)
                xx+=cw
            self.ports_for(row["id"],x,yy,w,rh,mark=row_box,concept=row.get("concept"))
        if note: self.label(note,4,self.h-note_h,self.w-8,note_h,color=MUTED)
        self.ports_for(data.get("id","matrix"),x,y,w,h,kind="container")

    def taxonomy(self, data):
        groups = data["groups"]
        require(1 <= len(groups) <= 4, "Native taxonomy supports 1-4 peer groups")
        gy = 20+self.f*1.6
        gap = 16
        gw = (self.w-32-gap*(len(groups)-1))/len(groups)
        title_h=self.f*1.6
        content_h=max(len(wrap("\n".join(g["items"]),gw-20,self.f))*self.f*1.3 for g in groups)
        gh = min(self.h-gy-14, title_h+content_h+34)
        outer_h=gy+gh+10
        outer=self.rect(4,4,self.w-8,outer_h,"#f7f7f7")
        self.label(data["root"],16,10,self.w-32,self.f*1.6,bold=True)
        for i,g in enumerate(groups):
            gx=16+i*(gw+gap)
            accent = self.concept_color(g)
            paint = accent or "#9c9c9c"
            group_box=self.bind_color(self.rect(gx,gy,gw,gh,paint,"none"),g,"fill")
            foreground = text_on_fill(paint)
            self.label(g["label"],gx+10,gy+8,gw-20,title_h,bold=True,color=foreground)
            items="\n".join(g["items"])
            self.label(items,gx+10,gy+title_h+12,gw-20,gh-title_h-22,top=True,color=foreground)
            self.ports_for(g["id"],gx,gy,gw,gh,mark=group_box,concept=g.get("concept"))
        self.ports_for(data.get("id","taxonomy"),4,4,self.w-8,outer_h,mark=outer,kind="container")

    def cycle(self, data):
        steps=data["steps"]
        require(3 <= len(steps) <= 8, "Native recurring process supports 3-8 steps")
        require(data.get("closed") is True, "Use cycle only for an explicit recurrence")
        cols=min(3,max(2,int(self.w/190)))
        rows=math.ceil(len(steps)/cols)
        pad,gx,gy=18,20,40
        cw=(self.w-2*pad-gx*(cols-1))/cols
        ch=(self.h-2*pad-gy*(rows-1))/rows
        positions=[]
        for i,step in enumerate(steps):
            row,col=divmod(i,cols)
            if row%2: col=cols-1-col
            x,y=pad+col*(cw+gx),pad+row*(ch+gy)
            positions.append((x,y,cw,ch))
            self.card(step,x,y,cw,ch)
        for i in range(len(steps)-1):
            a,b=positions[i],positions[i+1]
            if a[1]==b[1]:
                side_a,side_b=("right","left") if b[0]>a[0] else ("left","right")
            else: side_a,side_b="bottom","top"
            self.path([self.point(steps[i]["id"]+"-"+side_a),self.point(steps[i+1]["id"]+"-"+side_b)],True,owners=(steps[i]["id"],steps[i+1]["id"]))
        start=self.point(steps[-1]["id"]+"-bottom")
        end=self.point(steps[0]["id"]+"-left")
        self.path([start,[start[0],self.h-5],[5,self.h-5],[5,end[1]],end],True,owners=(steps[-1]["id"],steps[0]["id"]))

    def boundary(self, data):
        nodes=data["nodes"]
        require(1<=len(nodes)<=5,"Native boundary supports 1-5 semantic objects")
        outer=self.rect(4,4,self.w-8,self.h-8,"#f7f7f7","none")
        paint=self.concept_color(data) or "#9c9c9c"
        self.bind_color(self.rect(8,8,self.w-16,self.f*1.7+10,paint,"none"),data,"fill")
        self.label(data["label"],16,12,self.w-32,self.f*1.7,bold=True,color=text_on_fill(paint))
        relations=data.get("relations",[])
        ids=[n["id"] for n in nodes]
        groups=data.get("groups",[])
        reserved=set(); group_ranges=[]
        for group in groups:
            require(group.get("nodes") and all(n in ids for n in group["nodes"]),"Boundary group references unknown nodes")
            indices=sorted(ids.index(n) for n in group["nodes"])
            require(indices==list(range(indices[0],indices[-1]+1)),"Boundary group nodes must be contiguous in reading order")
            require(not reserved.intersection(indices),"Boundary groups cannot overlap")
            reserved.update(indices); group_ranges.append((group,indices[0],indices[-1]))
        lane=35+12*len(relations)
        x=lane+14; width=self.w-2*x
        top=24+self.f*1.7
        gap=26
        group_head=self.f*1.6+12
        height=(self.h-top-18-gap*(len(nodes)-1)-len(groups)*group_head)/len(nodes)
        height=min(height,max(70,max(self.card_metrics(node,width)[0] for node in nodes)+12))
        positions=[]; cursor=top
        for i,node in enumerate(nodes):
            if any(first==i for _,first,_ in group_ranges): cursor+=group_head
            positions.append(cursor);cursor+=height+gap
        for group,first,last in group_ranges:
            gy=positions[first]-group_head+3
            box=self.rect(x-12,gy,width+24,positions[last]+height+9-gy,"#ffffff","none",5)
            paint=self.concept_color(group) or ACCENT
            self.bind_color(self.rect(x-8,gy,width+16,group_head-4,paint,"none"),group,"fill")
            self.label(group["label"],x,gy+2,width,group_head-7,bold=True,color=text_on_fill(paint))
            self.ports_for(group["id"],x-12,gy,width+24,positions[last]+height+9-gy,mark=box,kind="container",concept=group.get("concept"))
        for i,node in enumerate(nodes): self.card(node,x,positions[i],width,height)
        outer_height=positions[-1]+height+14
        outer.set("height",str(outer_height))
        for i,rel in enumerate(relations):
            require(rel["from"] in ids and rel["to"] in ids,"Boundary relation references unknown node")
            a,b=ids.index(rel["from"]),ids.index(rel["to"])
            if b==a+1:
                self.path([self.point(rel["from"]+"-bottom"),self.point(rel["to"]+"-top")],rel.get("directed",True),owners=(rel["from"],rel["to"]))
            else:
                start,end=self.point(rel["from"]+"-left"),self.point(rel["to"]+"-left")
                xx=16+i*12
                self.path([start,[xx,start[1]],[xx,end[1]],end],rel.get("directed",True),owners=(rel["from"],rel["to"]))
        self.ports_for(data.get("id","boundary"),4,4,self.w-8,outer_height,mark=outer,kind="container",concept=data.get("concept"))


def build(spec, directory):
    geometry_spec=copy.deepcopy(spec); geometry_spec["links"]=[]
    geometry=plan(geometry_spec)
    result=copy.deepcopy(spec)
    assets=[]
    font=max(15,spec["canvas"]["minTextPx"]*spec["canvas"]["width"]/spec["canvas"]["displayWidth"])
    for p,g in zip(result["panels"],geometry["panels"]):
        if "diagram" not in p: continue
        colors={cid:color for cid,color in geometry.get("semanticColors",{}).items() if cid in p.get("concepts",[])}
        renderer=Renderer(*g["body"][2:],font,directory,colors=colors)
        kind=p["diagram"]["type"]
        require(kind in {"hub","matrix","taxonomy","cycle","boundary"},f"Unsupported native type: {kind}")
        element(renderer.root,"title",text=p["question"])
        element(renderer.root,"desc",text=p["claim"])
        getattr(renderer,kind)(p["diagram"])
        p["ports"]={**p.get("ports",{}),**renderer.bindings}
        p["objects"]={**p.get("objects",{}),**renderer.objects}
        path=Path(p["source"])
        assets.append((path if path.is_absolute() else directory/path,ET.tostring(renderer.root,encoding="unicode")))
    plan(result)
    return result,assets,font


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec",type=Path,required=True)
    ap.add_argument("--output-spec",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--overwrite",action="store_true")
    args=ap.parse_args()
    report_writable=False
    try:
        require(args.spec.resolve()!=args.output_spec.resolve(),"Keep the authored brief separate from the generated plan")
        spec=json.loads(args.spec.read_text(encoding="utf-8-sig"))
        sources={(args.spec.parent/p["source"]).resolve() for p in spec["panels"]}
        require(args.report.resolve() not in sources|{args.spec.resolve(),args.output_spec.resolve()},
                "Diagnostic report cannot replace a brief, plan, or source SVG")
        write_target(args.report,args.overwrite)
        report_writable=True
        result,assets,font=build(spec,args.spec.parent)
        for p in result["panels"]:
            path=(args.spec.parent/p["source"]).resolve()
            p["source"]=os.path.relpath(path,args.output_spec.parent.resolve()).replace("\\","/")
        destinations=[args.output_spec,args.report]+[a[0] for a in assets]
        require(len(set(p.resolve() for p in destinations))==len(destinations),"Generated output paths collide")
        require(args.spec.resolve() not in {p.resolve() for p in destinations},"An output would replace the authored brief")
        for path in destinations: write_target(path,args.overwrite)
        for path,svg in assets: path.write_text(svg,encoding="utf-8")
        args.output_spec.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        report={"ok":True,"panels":len(assets),"sourceFontPx":font,"outputSpec":str(args.output_spec),
                "ports":{p["id"]:list(p.get("ports",{})) for p in result["panels"]}}
        args.report.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report))
        return 0
    except (ValueError,KeyError,TypeError,OSError,ET.ParseError) as exc:
        # Expected authoring findings publish diagnostics, never an invalid plan/SVG.
        report={"ok":False,"error":str(exc)}
        if report_writable:
            try:
                args.report.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
            except OSError as report_error:
                report["reportError"]=str(report_error)
        print(json.dumps(report))
        return 0


if __name__=="__main__":
    raise SystemExit(main())
