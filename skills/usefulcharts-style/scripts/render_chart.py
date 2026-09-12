#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render original, editable educational posters from an explicit data brief."""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import heapq
import html
import json
import math
import re
import sys
from pathlib import Path

INK = "#242720"
MUTED = "#575B50"
KINDS = {
    "descent": ("", "Descent"),
    "branch": ("", "Branch / continuation"),
    "succession": ("12 3 2 3", "Succession"),
    "influence": ("2 7", "Influence"),
    "uncertain": ("8 6", "Uncertain relationship"),
    "adopted": ("10 3 2 3 2 3", "Adoptive parentage"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, name):
    require(isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value), f"{name} must be a finite number.")
    return float(value)


def ident(value, canonical=False):
    pattern=r"[a-z0-9]+(?:-[a-z0-9]+)*" if canonical else r"[A-Za-z0-9][A-Za-z0-9_.:-]*"
    require(isinstance(value, str) and re.fullmatch(pattern, value)
            and len(value) <= (64 if canonical else 160), f"Invalid {'lowercase hyphen-case ' if canonical else ''}ID: {value!r}")
    return value


def color(value):
    require(isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value),
            f"Color must be #RRGGBB: {value!r}")
    return value.upper()


def luminance(paint):
    channels = [int(paint[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in channels]
    return sum(v * w for v, w in zip(linear, (.2126, .7152, .0722)))


def contrast(a, b):
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + .05) / (lo + .05)


def text_color(background):
    preferred = max((INK, "#FFFFFF"), key=lambda c: contrast(c, background))
    return preferred if contrast(preferred, background) >= 4.5 else "#000000"


def text_width(value, size, bold=False):
    # Conservative Arial advance estimates. Browser measurement is the final gate.
    total = 0
    for c in str(value):
        if c in " ilI.,:;'!|":
            total += .29
        elif c in "MW@%&":
            total += .91
        elif c.isupper():
            total += .70
        elif ord(c) > 255:
            total += 1.0
        else:
            total += .56
    return total * size * (1.035 if bold else 1)


def wrap(value, width, size, bold=False):
    result = []
    for paragraph in str(value).split("\n"):
        line = ""
        for word in paragraph.split():
            require(text_width(word, size, bold) <= width,
                    f"Word {word!r} cannot fit. Widen its node/page or add an explicit line break.")
            candidate = f"{line} {word}".strip()
            if line and text_width(candidate, size, bold) > width:
                result.append(line)
                line = word
            else:
                line = candidate
        if line:
            result.append(line)
    return result


def attr(value):
    return html.escape(str(value), quote=True)


def fmt(value):
    return f"{float(value):.2f}".rstrip("0").rstrip(".")


def overlaps(a, b, pad=0):
    return (a[0] < b[0] + b[2] + pad and a[0] + a[2] + pad > b[0]
            and a[1] < b[1] + b[3] + pad and a[1] + a[3] + pad > b[1])


def segment_hits(a, b, box, pad=0):
    x, y, w, h = box
    left, right, top, bottom = x - pad, x + w + pad, y - pad, y + h + pad
    if abs(a[0] - b[0]) < .001:
        return left + .01 < a[0] < right - .01 and max(min(a[1], b[1]), top) < min(max(a[1], b[1]), bottom) - .01
    if abs(a[1] - b[1]) < .001:
        return top + .01 < a[1] < bottom - .01 and max(min(a[0], b[0]), left) < min(max(a[0], b[0]), right) - .01
    raise ValueError("Route contains a non-orthogonal segment.")


def compress(points):
    result = []
    for p in points:
        if result and p == result[-1]:
            continue
        if len(result) >= 2:
            a, b = result[-2:]
            if (a[0] == b[0] == p[0]) or (a[1] == b[1] == p[1]):
                result[-1] = p
                continue
        result.append(p)
    return result


def proper_cross(a, b, c, d):
    if a[0] == b[0] and c[1] == d[1]:
        return min(c[0], d[0]) + .1 < a[0] < max(c[0], d[0]) - .1 and min(a[1], b[1]) + .1 < c[1] < max(a[1], b[1]) - .1
    if a[1] == b[1] and c[0] == d[0]:
        return proper_cross(c, d, a, b)
    return False


def route(start, end, boxes, bounds, existing):
    """Sparse visibility-grid A* with obstacle rejection and crossing penalties."""
    def clear(a, b):
        return not any(segment_hits(a, b, box, 7) for box in boxes)

    def crossing_cost(a, b):
        penalty = 90 * sum(proper_cross(a, b, c, d) for c, d in existing)
        for c, d in existing:
            if a[0] == b[0] == c[0] == d[0]:
                penalty += 6 * max(0, min(max(a[1],b[1]),max(c[1],d[1]))-max(min(a[1],b[1]),min(c[1],d[1])))
            if a[1] == b[1] == c[1] == d[1]:
                penalty += 6 * max(0, min(max(a[0],b[0]),max(c[0],d[0]))-max(min(a[0],b[0]),min(c[0],d[0])))
        return penalty

    mid = (start[1] + end[1]) / 2
    candidates = [compress([start, (start[0], mid), (end[0], mid), end])]
    for offset in (0, -18, 18, -36, 36):
        yy = mid + offset
        candidates.append(compress([start, (start[0], yy), (end[0], yy), end]))
    viable = [p for p in candidates if all(clear(a, b) for a, b in zip(p, p[1:]))]
    if viable:
        return min(viable, key=lambda p: sum(abs(a[0]-b[0])+abs(a[1]-b[1])+crossing_cost(a,b) for a,b in zip(p,p[1:])))

    xs = {start[0], end[0], bounds[0], bounds[2]}
    ys = {start[1], end[1], bounds[1], bounds[3], mid}
    for x, y, w, h in boxes:
        xs.update((x - 14, x + w + 14))
        ys.update((y - 14, y + h + 14))
    xs = sorted(x for x in xs if bounds[0] <= x <= bounds[2])
    ys = sorted(y for y in ys if bounds[1] <= y <= bounds[3])
    origin = (xs.index(start[0]), ys.index(start[1]), -1)
    goal = (xs.index(end[0]), ys.index(end[1]))
    queue = [(0, 0, origin)]
    best = {origin: 0}
    parent = {}
    visited = 0
    while queue:
        _, cost, state = heapq.heappop(queue)
        if cost != best.get(state):
            continue
        ix, iy, direction = state
        if (ix, iy) == goal:
            path = []
            while state in parent:
                path.append((xs[state[0]], ys[state[1]]))
                state = parent[state]
            path.append(start)
            return compress(list(reversed(path)))
        visited += 1
        require(visited < 180000, "Routing budget exceeded. Increase spacing or simplify branch ordering.")
        point = (xs[ix], ys[iy])
        for dx, dy, new_direction in ((1, 0, 0), (-1, 0, 0), (0, 1, 1), (0, -1, 1)):
            nx, ny = ix + dx, iy + dy
            if not (0 <= nx < len(xs) and 0 <= ny < len(ys)):
                continue
            next_point = (xs[nx], ys[ny])
            if not clear(point, next_point):
                continue
            distance = abs(point[0] - next_point[0]) + abs(point[1] - next_point[1])
            new_cost = cost + distance + (24 if direction not in (-1, new_direction) else 0) + crossing_cost(point, next_point)
            new_state = (nx, ny, new_direction)
            if new_cost >= best.get(new_state, math.inf):
                continue
            best[new_state] = new_cost
            parent[new_state] = state
            estimate = abs(next_point[0] - end[0]) + abs(next_point[1] - end[1])
            heapq.heappush(queue, (new_cost + estimate, new_cost, new_state))
    raise ValueError("No clear connector corridor. Separate nodes or increase the page size.")


def automatic_lineage(data):
    """Rank a structural DAG and keep descendant leaves in category order."""
    require(data.get("mode")=="lineage", "Automatic placement is available for lineage mode only.")
    nodes=data["nodes"]
    by_id={n["id"]:n for n in nodes}
    require(len(by_id)==len(nodes) and nodes,"Automatic placement requires unique nodes.")
    require(not data.get("unions"),"Automatic lineage does not infer partnerships.")
    children={nid:[] for nid in by_id};parents={nid:[] for nid in by_id}
    for edge in data.get("edges",[]):
        source,target=edge["source"],edge["target"]
        require(source in by_id and target in by_id,f"Unresolved relation {edge['id']}.")
        if edge["kind"]!="influence":
            children[source].append(target);parents[target].append(source)
    pending=set(by_id);rank={};order=[]
    while pending:
        ready=sorted(nid for nid in pending if all(p in rank for p in parents[nid]))
        require(ready,"Structural relations contain a cycle. Correct the source graph.")
        for nid in ready:
            rank[nid]=max((rank[p]+1 for p in parents[nid]),default=0)
            pending.remove(nid);order.append(nid)
    groups={g["id"]:i for i,g in enumerate(data["groups"])}
    require(all(n["group"] in groups for n in nodes),"Unknown node category.")
    leaf_ids=sorted((nid for nid in by_id if not children[nid]),key=lambda nid:(groups[by_id[nid]["group"]],nid))
    slots={nid:{i} for i,nid in enumerate(leaf_ids)}
    for nid in reversed(order):
        if children[nid]:slots[nid]=set().union(*(slots[child] for child in children[nid]))
    rank_count=max(rank.values())+1
    columns=max(2,len(leaf_ids),max(sum(r==i for r in rank.values()) for i in range(rank_count)))
    for row in range(rank_count):
        members=sorted((nid for nid in by_id if rank[nid]==row),key=lambda nid:(sum(slots[nid])/len(slots[nid]),nid))
        positions=[]
        for nid in members:
            desired=sum(slots[nid])/len(slots[nid])
            positions.append(max(desired,positions[-1]+1 if positions else 0))
        if positions and positions[-1]>columns-1:
            positions[-1]=columns-1
            for i in range(len(positions)-2,-1,-1):positions[i]=min(positions[i],positions[i+1]-1)
        for nid,col in zip(members,positions):by_id[nid].update(row=row,col=col)
    font=data.get("font_size",18)
    longest=max((text_width(word,font,True) for n in nodes for word in (n["label"]+" "+n.get("detail","")).split()),default=80)
    data.setdefault("width",math.ceil(max(1200,201+columns*max(170,(longest+24)/.84))/50)*50)
    data.setdefault("height",max(1400,560+rank_count*180))
    data["columns"]=columns
    data.setdefault("rows",[f"Stage {i+1}" for i in range(max(2,rank_count))])
    require(len(data["rows"])>=rank_count,"Not enough row labels for the inferred stages.")
    return data


class Poster:
    def __init__(self, data):
        self.source_data=copy.deepcopy(data)
        if isinstance(data,dict) and data.get("layout")=="auto":
            data=automatic_lineage(copy.deepcopy(data))
        self.data = data
        require(isinstance(data, dict), "Input must be a JSON object.")
        self.id = ident(data["id"],canonical=True)
        self.mode = data["mode"]
        require(self.mode in ("genealogy", "lineage", "timeline"), "Unknown poster mode.")
        self.w = number(data.get("width", 1600), "width")
        self.h = number(data.get("height", 2400), "height")
        minimum_height=600 if data.get('design')=='editorial' else 1200
        require(1000 <= self.w <= 8000 and minimum_height <= self.h <= 12000, f"Canvas must be 1000–8000 by {minimum_height}–12000 units.")
        self.font = number(data.get("font_size", 18), "font_size")
        require(16 <= self.font <= 40, "font_size must be between 16 and 40.")
        self.frame = color(data.get("frame_color", "#813B37"))
        self.paper = color(data.get("paper_color", "#F2EFDF"))
        self.ink = text_color(self.paper)
        self.muted = MUTED if contrast(MUTED, self.paper) >= 4.5 else self.ink
        require(str(data.get("title", "")).strip(), "A title is required.")
        require(str(data.get("source_note", "")).strip(), "A source_note is required.")
        self.groups = {}
        for group in data["groups"]:
            gid = ident(group["id"])
            require(gid not in self.groups, f"Duplicate group ID: {gid}")
            require(str(group["label"]).strip(), "Category labels must not be empty.")
            self.groups[gid] = dict(group, color=color(group["color"]))
        require(1 <= len(self.groups) <= 8, "Use between 1 and 8 groups.")
        require(len({g["color"] for g in self.groups.values()}) == len(self.groups), "Category colors must be distinct.")
        self.parts = []
        self.boxes = {}
        self.nodes = {}
        self.routes = []
        self.unions = {}
        self.expected_text = []
        self.relations = list(data.get("edges", []))
        # Barlow Condensed has narrower advances; use a conservative width budget.
        self.title_lines = wrap(data["title"].upper(), (self.w - 140) / .76, 70, True)
        self.title_height = 38 + 79 * len(self.title_lines) + (32 if data.get("subtitle") else 0)
        self.note_lines = wrap(data.get("reading_note", self.default_note()), self.w - 190, 18)
        self.source_lines = wrap(data["source_note"], self.w - 190, 16)
        self.footer_height = 98 + 24 * len(self.note_lines) + 21 * len(self.source_lines)
        self.left, self.right = 136, self.w - 65
        self.legend_rows = math.ceil(len(self.groups) / max(1, int((self.w - 130) / 260)))
        self.kinds = {e["kind"] for e in self.relations}
        require(self.kinds <= KINDS.keys(), f"Unknown edge kinds: {self.kinds - KINDS.keys()}")
        if data.get("unions"):
            self.kinds.add("partnership")
            if any(u.get("children") for u in data["unions"]):
                self.kinds.add("descent")
        self.key_rows = math.ceil(len(self.kinds) / max(1, int((self.w - 130) / 300)))
        self.top = self.title_height + 84 + 38 * self.legend_rows + 34 * self.key_rows + 70
        self.bottom = self.h - self.footer_height - 68
        if data.get('design')=='editorial':
            self.top,self.bottom=170,self.h-80
        else:
            require(self.bottom - self.top > 450, "Header/footer leave insufficient chart area. Enlarge the canvas or shorten notes.")

    def default_note(self):
        if self.mode == "timeline":
            return "Read down the shared year scale. Parallel columns show contemporaneous intervals."
        return "Read top to bottom. Vertical spacing represents schematic generations or stages, not elapsed time."

    def add(self, value):
        self.parts.append(value)

    def text(self, x, y, value, size=18, fill=None, anchor="middle", bold=False, owner=None, background=None, css=""):
        if not str(value).strip():
            return
        fill = fill or self.ink
        self.expected_text.append(str(value))
        self.add(f'<text x="{fmt(x)}" y="{fmt(y)}" font-size="{fmt(size)}" fill="{fill}" text-anchor="{anchor}" font-weight="{700 if bold else 400}" data-owner="{attr(owner or "page")}" data-background="{background or self.paper}" {css}>{html.escape(str(value))}</text>')

    def rect(self, box, fill, stroke="none", width=1, radius=0, extra=""):
        x, y, w, h = box
        self.add(f'<rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>')

    def line(self, points, paint, width=3, dash="", extra=""):
        path = "M " + " L ".join(f"{fmt(x)} {fmt(y)}" for x, y in points)
        self.add(f'<path d="{path}" fill="none" stroke="{paint}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="{dash}" {extra}/>')

    def frame_and_key(self):
        self.rect((0, 0, self.w, self.h), self.frame)
        self.rect((28, self.title_height, self.w - 56, self.h - self.title_height - 28), self.paper, "#FFFFFF", 2, 12)
        for i, line in enumerate(self.title_lines):
            self.text(self.w / 2, 83 + i * 79, line, 70, text_color(self.frame), bold=True,
                      background=self.frame, css='font-family="PosterTitle, Arial Narrow, Impact, sans-serif" letter-spacing="1.2"')
        if self.data.get("subtitle"):
            self.text(self.w / 2, self.title_height - 22, self.data["subtitle"], 19, text_color(self.frame), background=self.frame)
        cols = max(1, int((self.w - 130) / 260))
        pitch = (self.w - 130) / cols
        for i, group in enumerate(self.groups.values()):
            x, y = 65 + (i % cols) * pitch, self.title_height + 39 + (i // cols) * 38
            self.rect((x, y - 17, 25, 20), group["color"], self.muted, .7, 2)
            self.text(x + 36, y, group["label"], 18, anchor="start", bold=True)
        cols = max(1, int((self.w - 130) / 300))
        pitch = (self.w - 130) / cols
        for i, kind in enumerate(sorted(self.kinds)):
            x, y = 65 + (i % cols) * pitch, self.title_height + 54 + 38 * self.legend_rows + (i // cols) * 34
            if kind == "partnership":
                self.line([(x, y - 7), (x + 38, y - 7)], self.muted, 2)
                self.line([(x, y - 1), (x + 38, y - 1)], self.muted, 2)
                label = "Partnership"
            else:
                dash, label = KINDS[kind]
                self.line([(x, y - 4), (x + 38, y - 4)], self.muted, 3, dash)
                if kind in ("influence", "succession"):
                    self.add(f'<path d="M {x+30} {y-9} L {x+39} {y-4} L {x+30} {y+1}" fill="none" stroke="{self.muted}" stroke-width="2"/>')
            self.text(x + 48, y + 2, label, 16, anchor="start")
        self.line([(65, self.top - 68), (self.w - 65, self.top - 68)], "#BDB9A8", 1)

    def footer(self):
        yy = self.h - self.footer_height + 12
        self.line([(65, yy - 31), (self.w - 65, yy - 31)], "#BDB9A8", 1)
        self.text(80, yy, "HOW TO READ", 16, self.muted, anchor="start", bold=True)
        for i, line in enumerate(self.note_lines):
            self.text(80, yy + 30 + i * 24, line, 18, anchor="start")
        yy += 48 + len(self.note_lines) * 24
        for i, line in enumerate(self.source_lines):
            self.text(80, yy + i * 21, line, 16, self.muted, anchor="start")
        self.text(self.w - 68, self.h - 48, self.id.upper().replace("-", " "), 13, self.muted, anchor="end")

    def make_node(self, node, box):
        nid = node["id"]
        self.boxes[nid] = box
        self.nodes[nid] = node

    def node_content(self, node, width):
        names = wrap(node["label"], width - 16, self.font, True)
        details = wrap(node.get("detail", ""), width - 16, self.font - 2)
        height = 20 + len(names) * (self.font + 3) + len(details) * (self.font + 1)
        return names, details, height

    def draw_nodes(self):
        for nid, node in self.nodes.items():
            box = self.boxes[nid]
            x, y, w, h = box
            paint = self.groups[node["group"]]["color"]
            ink = text_color(paint)
            self.add(f'<g id="node-{nid}" data-node-id="{nid}" data-group="{node["group"]}"><title>{html.escape(node["label"])}</title>')
            if self.mode == "timeline":
                self.rect(box, "none", extra='data-node-box="true"')
                bar_width = min(54,w*.2)
                self.rect((x,y,bar_width,h),paint,self.paper,2,3)
                self.line([(x+bar_width+8,y),(x+w,y)],"#CCC8B7",1)
                label_width = w-bar_width-22
                names,details,height = self.node_content(node,label_width)
                label_x = x+bar_width+14+label_width/2
                ink,background = self.ink,self.paper
                self.rect((x+bar_width+8,y+(h-height)/2,label_width+12,height+4),self.paper)
            else:
                self.rect(box, paint, ink if node.get("emphasis") else paint, 2.8 if node.get("emphasis") else 1,
                          2, extra='data-node-box="true"')
                names, details, height = self.node_content(node, w)
                label_x,background = x+w/2,paint
            yy = y + (h - height) / 2 + 10 + self.font
            for line in names:
                self.text(label_x, yy, line, self.font, ink, bold=True, owner=nid, background=background)
                yy += self.font + 3
            for line in details:
                self.text(label_x, yy, line, self.font - 2, ink, owner=nid, background=background)
                yy += self.font + 1
            self.add('</g>')

    def graph_layout(self):
        d = self.data
        rows, columns = d["rows"], d["columns"]
        require(isinstance(rows, list) and len(rows) >= 2 and all(isinstance(v,str) and v.strip() for v in rows), "rows needs at least two nonempty labels.")
        require(isinstance(columns, int) and 2 <= columns <= 18, "columns must be an integer from 2 to 18.")
        pitch = (self.right - self.left) / columns
        widest_word=max((text_width(word,self.font,True)+20 for node in d["nodes"] for word in node["label"].split()),default=0)
        default_width=min(pitch*.88,max(pitch*.8,widest_word))
        width = number(d.get("node_width", default_width), "node_width")
        require(70 <= width <= pitch * .88, "node_width must be >=70 and <=88% of a column pitch. Use fewer columns or a wider page.")
        gap = (self.bottom - self.top) / (len(rows) - 1)
        for i, label in enumerate(rows):
            y = self.top + i * gap
            for j, line in enumerate(wrap(label, 86/.73, 14, True)):
                self.text(49, y - 8 + j * 17, line, 14, self.muted, anchor="start", bold=True,
                          css='font-family="PosterTitle, Arial Narrow, sans-serif"')
        for node in d["nodes"]:
            nid = ident(node["id"])
            require(nid not in self.nodes, f"Duplicate node ID: {nid}")
            require(node["group"] in self.groups, f"Unknown group for {nid}.")
            require(str(node["label"]).strip(), f"Empty label for {nid}.")
            row, col = node["row"], number(node["col"], f"{nid}.col")
            require(isinstance(row, int) and 0 <= row < len(rows), f"Invalid row for {nid}.")
            require(0 <= col <= columns - 1, f"Invalid column for {nid}.")
            _, _, height = self.node_content(node, width)
            require(height + 38 < gap, f"Node {nid} is too tall for its rank. Add page height, shorten detail, or widen nodes.")
            self.make_node(node, (self.left + pitch * (col + .5) - width / 2, self.top + row * gap - height / 2, width, height))
        require(self.nodes, "At least one node is required.")
        for lane in d.get("lanes", []):
            require(lane["group"] in self.groups, "Unknown lane group.")
            x = self.left + pitch * lane["col"]
            span = pitch * lane["span"]
            require(self.left <= x and x + span <= self.right + .1 and span > 0, "Lane heading exceeds chart width.")
            paint = self.groups[lane["group"]]["color"]
            self.rect((x + 5, self.top - 104, span - 10, 29), self.paper, paint, 2, 14)
            self.text(x + span / 2, self.top - 84, lane["label"].upper(), 15, bold=True)
        self.build_unions()
        self.check_boxes()
        self.build_routes()
        for union in self.unions.values():
            x,y=union["point"]
            self.add(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="4" fill="{self.muted}"/>')

    def check_boxes(self):
        items = list(self.boxes.items())
        for i, (nid, box) in enumerate(items):
            require(box[0] >= self.left - 1 and box[0]+box[2] <= self.right+1,
                    f"Node {nid} exceeds the chart field.")
            require(box[1] >= self.title_height and box[1]+box[3] < self.h-self.footer_height,
                    f"Node {nid} exceeds the chart field vertically.")
            for oid, other in items[i+1:]:
                require(not overlaps(box, other, 8), f"Nodes {nid} and {oid} overlap or lack an 8-unit gutter.")

    def build_unions(self):
        require(self.mode == "genealogy" or not self.data.get("unions"), "Only genealogy mode supports unions.")
        for union in self.data.get("unions", []):
            uid = ident(union["id"])
            require(uid not in self.nodes and uid not in self.unions, f"Duplicate union ID: {uid}")
            partners = union["partners"]
            require(len(partners) == 2 and partners[0] != partners[1] and all(p in self.nodes for p in partners), f"Union {uid} needs two distinct known partners.")
            partners = sorted(partners, key=lambda p: self.boxes[p][0])
            a, b = [self.boxes[p] for p in partners]
            require(self.nodes[partners[0]]["row"] == self.nodes[partners[1]]["row"], f"Partners in {uid} must share a row.")
            y = a[1] + a[3] / 2
            start, end = (a[0] + a[2], y), (b[0], y)
            require(end[0] - start[0] >= 16, f"Union {uid} needs at least a 16-unit gap.")
            require(not any(segment_hits(start, end, box, 4) for nid, box in self.boxes.items() if nid not in partners), f"Union {uid} crosses another person. Place partners next to one another.")
            self.unions[uid] = dict(union, partners=partners, point=((start[0]+end[0])/2, y))
            stroke,offset_size,dot=getattr(self,'union_mark',(2,3,4))
            for offset in (-offset_size,offset_size):
                self.line([(start[0], y+offset), (end[0], y+offset)], self.muted, stroke,
                          extra=f'data-union-id="{uid}"')
            self.add(f'<circle cx="{fmt((start[0]+end[0])/2)}" cy="{fmt(y)}" r="{dot}" fill="{self.muted}"/>')
            children = union.get("children", [])
            require(len(set(children)) == len(children), f"Union {uid} has duplicate children.")
            for child in children:
                self.relations.append({"id": f"{uid}-{child}", "source": uid, "target": child, "kind": "descent"})

    def build_routes(self):
        edge_ids = set()
        pairs = set()
        segments = []
        source_edges = {}
        target_edges = {}
        for edge in self.relations:
            source_edges.setdefault(edge["source"], []).append(edge["id"])
            target_edges.setdefault(edge["target"], []).append(edge["id"])

        def port_offset(mapping, node_id, edge_id, width):
            ids = mapping[node_id]
            return (ids.index(edge_id) - (len(ids) - 1)/2) * min(14, (width-24)/max(1,len(ids)-1))

        for edge in self.relations:
            eid, source, target, kind = edge["id"], edge["source"], edge["target"], edge["kind"]
            ident(eid)
            require(eid not in edge_ids, f"Duplicate edge ID: {eid}")
            edge_ids.add(eid)
            require((source, target, kind) not in pairs, f"Duplicate relation {source} → {target} ({kind}).")
            pairs.add((source, target, kind))
            require(kind in KINDS and target in self.nodes and source in (self.nodes | self.unions), f"Unresolved or invalid relation {eid}.")
            require(source != target, f"Self-link in {eid}.")
            source_row = self.nodes[source]["row"] if source in self.nodes else self.nodes[self.unions[source]["partners"][0]]["row"]
            if kind != "influence":
                require(source_row < self.nodes[target]["row"], f"Relation {eid} must lead to a later row.")
            target_box = self.boxes[target]
            end = (target_box[0] + target_box[2] / 2 + port_offset(target_edges,target,eid,target_box[2]), target_box[1])
            if source in self.unions:
                start = self.unions[source]["point"]
            else:
                box = self.boxes[source]
                start = (box[0] + box[2] / 2 + port_offset(source_edges,source,eid,box[2]), box[1] + box[3])
            # Escape ports by 14 units before searching; all boxes remain obstacles.
            a, b = (start[0], start[1] + 14), (end[0], end[1] - 14)
            path = compress([start] + route(a, b, list(self.boxes.values()),
                            (self.left - 20, self.top - 70, self.right + 20, self.bottom + 70), segments) + [end])
            require(not any(segment_hits(p, q, box, 0) for p,q in zip(path,path[1:]) for box in self.boxes.values()), f"Relation {eid} touches a label rectangle. Reorder the branch.")
            group = edge.get("group", self.nodes[target]["group"])
            require(group in self.groups, f"Unknown color group for edge {eid}.")
            paint = self.groups[group]["color"]
            # Thin under-stroke separates unrelated crossings without a false junction dot.
            self.line(path, self.paper, 7)
            self.line(path, paint, 3.3, KINDS[kind][0],
                      extra=f'data-edge-id="{eid}" data-source="{source}" data-target="{target}" data-kind="{kind}"')
            if kind in ("influence", "succession"):
                x, y = end
                self.add(f'<path d="M {fmt(x-5)} {fmt(y-9)} L {fmt(x)} {fmt(y-1)} L {fmt(x+5)} {fmt(y-9)}" fill="none" stroke="{paint}" stroke-width="3"/>')
            self.routes.append(dict(edge, points=path))
            segments.extend(zip(path, path[1:]))

    def year_label(self, year):
        if self.data["time"].get("notation") == "historical":
            return f"{fmt(1-year)} BCE" if year <= 0 else f"{fmt(year)} CE"
        return fmt(year)

    def timeline_layout(self):
        d = self.data
        require(not any(d.get(key) for key in ("nodes", "edges", "unions")), "Timeline mode accepts periods, not nodes, edges, or unions.")
        time = d["time"]
        start, end, step = [number(time[k], f"time.{k}") for k in ("start", "end", "step")]
        require(end > start and step > 0 and (end-start)/step <= 80, "Invalid time scale or more than 80 ticks.")
        lanes = {lane["id"]: i for i, lane in enumerate(d["lanes"])}
        require(lanes and len(lanes) == len(d["lanes"]), "Timeline lanes must have unique IDs.")
        pitch = (self.right - self.left) / len(lanes)
        scale = lambda year: self.top + (year-start)/(end-start)*(self.bottom-self.top)
        for lane in d["lanes"]:
            i = lanes[lane["id"]]
            x = self.left + pitch * i
            if i % 2 == 0:
                self.rect((x, self.top, pitch, self.bottom-self.top), self.ink, extra='opacity="0.025"')
            for j, line in enumerate(wrap(lane["label"].upper(), pitch-18, 18, True)):
                self.text(x + pitch/2, self.top - 33 + j*21, line, 18, bold=True)
        for i in range(math.floor((end-start)/step)+1):
            year = start + step*i
            y = scale(year)
            self.line([(self.left-8, y), (self.right, y)], "#CCC8B7", 1)
            self.text(self.left-20, y+5, self.year_label(year), 15, self.muted, anchor="end")
        track_counts = {}
        for period in d["periods"]:
            nid = ident(period["id"])
            require(nid not in self.nodes, f"Duplicate period ID: {nid}")
            require(period["group"] in self.groups and period["lane"] in lanes, f"Unknown category or lane for {nid}.")
            a, b = number(period["start"], f"{nid}.start"), number(period["end"], f"{nid}.end")
            require(start <= a < b <= end, f"Period {nid} has reversed or out-of-range dates.")
            tracks, track = period.get("tracks", 1), period.get("track", 0)
            require(isinstance(tracks,int) and isinstance(track,int) and 1 <= tracks <= 6 and 0 <= track < tracks, f"Invalid tracks for {nid}.")
            require(track_counts.setdefault(period["lane"], tracks) == tracks, "Use a consistent tracks count within each lane.")
            width = pitch / tracks - 20
            node = dict(period, detail=period.get("detail", f"{self.year_label(a)} – {self.year_label(b)}"))
            _, _, needed = self.node_content(node, width-min(54,width*.2)-22)
            height = scale(b) - scale(a)
            require(height >= needed + 12, f"Period {nid} is too short for its label. Enlarge the page or shorten text; do not alter dates.")
            x = self.left + pitch * lanes[period["lane"]] + (pitch / tracks) * track + 10
            self.make_node(node, (x, scale(a), width, height))
        require(self.nodes, "At least one period is required.")
        # Touching chronological bars are allowed; temporal overlap in one track is not.
        items = list(self.boxes.items())
        for i, (nid, box) in enumerate(items):
            for oid, other in items[i+1:]:
                require(not overlaps(box, other), f"Periods {nid} and {oid} overlap in one track. Use separate tracks.")

    def render(self):
        self.frame_and_key()
        if self.mode == "timeline":
            self.timeline_layout()
        else:
            self.graph_layout()
        self.draw_nodes()
        self.footer()
        crossings = []
        for i, first in enumerate(self.routes):
            for second in self.routes[i+1:]:
                if first["source"] == second["source"]:
                    continue
                for a,b in zip(first["points"], first["points"][1:]):
                    for c,d in zip(second["points"], second["points"][1:]):
                        if proper_cross(a,b,c,d):
                            crossings.append([first["id"], second["id"]])
        meta = {"schema_version": 1, "id": self.id, "mode": self.mode, "design": self.data.get("design","classic"), "canvas": [self.w,self.h],
                "node_ids": list(self.nodes), "edge_ids": [r["id"] for r in self.routes],
                "union_ids": list(self.unions), "boxes": self.boxes, "routes": self.routes,
                "expected_text": self.expected_text, "crossings": crossings,
                "data_sha256": hashlib.sha256(json.dumps(self.source_data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()}
        if self.mode == "timeline":
            meta["time"] = self.data["time"]
            meta["time_y"] = [self.top, self.bottom]
        title = html.escape(self.data["title"])
        description = html.escape(f'{self.data.get("subtitle", "")} {self.data["source_note"]} {self.data.get("reading_note",self.default_note())}')
        pattern = f' data-pattern-id="{ident(self.data["pattern_id"],canonical=True)}"' if self.data.get("pattern_id") else ""
        font_path = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "BarlowCondensed-Bold.ttf"
        font_data = base64.b64encode(font_path.read_bytes()).decode("ascii")
        font_license = html.escape(font_path.with_name("OFL.txt").read_text(encoding="utf-8"))
        font_style = '<style>@font-face{font-family:PosterTitle;font-style:normal;font-weight:700;src:url(data:font/ttf;base64,'+font_data+') format("truetype")}</style>\n'
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(self.w)}" height="{fmt(self.h)}" viewBox="0 0 {fmt(self.w)} {fmt(self.h)}" role="img" aria-labelledby="chart-title chart-desc" data-example-id="{self.id}"{pattern} font-family="Arial, Liberation Sans, sans-serif">\n'
               f'<title id="chart-title">{title}</title><desc id="chart-desc">{description}</desc>\n'
               +font_style+
               f'<metadata id="font-license">{font_license}</metadata>\n'
               f'<metadata id="chart-data">{html.escape(json.dumps(meta,ensure_ascii=False,separators=(",",":")))}</metadata>\n'
               + "\n".join(self.parts) + "\n</svg>\n")
        report = {"status": "pass", "id": self.id, "mode": self.mode, "design": meta["design"], "canvas": meta["canvas"],
                  "node_count": len(self.nodes), "edge_count": len(self.routes), "union_count": len(self.unions),
                  "node_collisions": 0, "connector_node_collisions": 0, "crossing_count": len(crossings),
                  "data_sha256": meta["data_sha256"], "visual_review": "Required; geometric preflight is not a visual quality score."}
        if self.data.get("layout")=="auto":
            report["resolved_layout"]={"columns":self.data["columns"],"rows":self.data["rows"],"nodes":[{"id":n["id"],"row":n["row"],"col":n["col"],"x":self.boxes[n['id']][0]+self.boxes[n['id']][2]/2,"y":self.boxes[n['id']][1]+self.boxes[n['id']][3]/2,"width":self.boxes[n['id']][2]} for n in self.nodes.values()]}
        elif self.data.get("layout")=="cohorts":
            report["resolved_layout"]={"layout":"cohorts","nodes":[{"id":nid,"x":b[0]+b[2]/2,"y":b[1]+b[3]/2,"width":b[2]} for nid,b in self.boxes.items()]}
        return svg, report


def viewer(svg, title):
    return f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#353833;color:#fff;font:16px Arial,sans-serif}}
header{{position:sticky;top:0;z-index:1;background:#242720;padding:12px 20px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}}
header strong{{margin-right:auto}}button{{font:inherit;padding:8px 14px;cursor:pointer}}main{{overflow:auto;padding:24px;height:calc(100vh - 75px)}}
#paper{{margin:auto;width:min(100%,1000px)}}#paper>svg{{display:block;width:100%;height:auto}}@media print{{header{{display:none}}main{{height:auto;padding:0;overflow:visible}}#paper{{width:100%}}}}
</style><header><strong>{html.escape(title)}</strong><button id="fit">Fit page</button><button id="full">100% detail</button><button id="minus" aria-label="Zoom out">−</button><button id="plus" aria-label="Zoom in">+</button></header>
<main><div id="paper">{svg}</div></main><script>
const paper=document.querySelector('#paper'), art=paper.querySelector('svg');
document.querySelector('#fit').onclick=()=>paper.style.width='min(100%,1000px)';
document.querySelector('#full').onclick=()=>paper.style.width=art.viewBox.baseVal.width+'px';
for(const [id,factor] of [['plus',1.25],['minus',.8]])document.getElementById(id).onclick=()=>paper.style.width=Math.max(320,paper.getBoundingClientRect().width*factor)+'px';
</script></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--svg", type=Path, required=True)
    parser.add_argument("--html", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        paths = [p.resolve() for p in (args.input,args.svg,args.html,args.report) if p]
        require(len(set(paths)) == len(paths), "Input and output paths must all be distinct.")
        data = json.loads(args.input.read_text(encoding="utf-8-sig"))
        if data.get("design") == "editorial":
            from editorial_poster import EditorialPoster
            svg, report = EditorialPoster(data).render()
        else:
            svg, report = Poster(data).render()
        contents = [(args.svg, svg)]
        if args.html:
            contents.append((args.html, viewer(svg, data["title"])))
        if args.report:
            contents.append((args.report,json.dumps(report,indent=2)+"\n"))
        for path, content in contents:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf-8")
        print(json.dumps(report))
        return 0
    except (ValueError,KeyError,TypeError,OSError) as error:
        print(f"Chart could not be rendered: {error}",file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
