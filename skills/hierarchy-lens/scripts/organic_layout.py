#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Pack one equal square per record along a connected procedural growth front."""

from __future__ import annotations

import heapq
import math
import random
from collections import defaultdict, deque

NEIGHBORS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def flood_shape(count, seed):
    """Use positive arrival increments so generations follow the growth front."""
    rng = random.Random(seed)
    phases = [rng.random() * math.tau for _ in range(3)]

    def potential(x, y):
        angle = math.atan2(x, -y)
        boundary = 1 + .15*math.cos(3*angle+phases[0]) + .09*math.cos(5*angle+phases[1]) + .04*math.cos(2*angle+phases[2])
        return math.hypot(x, y)/boundary

    queue = [(0.0, 0, 0)]
    best, used, sites = {(0, 0): 0.0}, set(), []
    while len(sites) < count:
        arrival, x, y = heapq.heappop(queue)
        point = x, y
        if point in used or arrival != best[point]:
            continue
        used.add(point)
        sites.append((x, y, arrival))
        for dx, dy in NEIGHBORS:
            adjacent = x+dx, y+dy
            if adjacent in used:
                continue
            score = max(arrival+.05, potential(*adjacent))
            if score < best.get(adjacent, math.inf):
                best[adjacent] = score
                heapq.heappush(queue, (score, *adjacent))
    return sites


def shape_quality(points):
    """Check orthogonal connectedness and enclosed background independently."""
    occupied = set(points)
    reached, queue = {next(iter(occupied))}, deque([next(iter(occupied))])
    while queue:
        x, y = queue.popleft()
        for dx, dy in NEIGHBORS:
            p = x+dx, y+dy
            if p in occupied and p not in reached:
                reached.add(p)
                queue.append(p)
    xs, ys = zip(*occupied)
    left, right, top, bottom = min(xs)-1, max(xs)+1, min(ys)-1, max(ys)+1
    outside, queue = {(left, top)}, deque([(left, top)])
    while queue:
        x, y = queue.popleft()
        for dx, dy in NEIGHBORS:
            p = x+dx, y+dy
            if left <= p[0] <= right and top <= p[1] <= bottom and p not in occupied and p not in outside:
                outside.add(p)
                queue.append(p)
    holes = (right-left+1)*(bottom-top+1)-len(occupied)-len(outside)
    return len(reached) == len(occupied), holes


def align_generation(nodes, sites):
    """Preserve circular tree order and choose a nearby angular alignment."""
    nodes = sorted(nodes, key=lambda n: (n[1]["x0"], n[1]["x1"]))
    sites = sorted(sites, key=lambda p: math.atan2(p[0], -p[1]) % math.tau)
    n = len(nodes)
    targets = [(math.sin((v["x0"]+v["x1"])/2), -math.cos((v["x0"]+v["x1"])/2)) for _,v in nodes]
    directions = [(x/math.hypot(x,y), y/math.hypot(x,y)) if x or y else (0,0) for x,y,_ in sites]

    def cost(offset):
        return sum(1-a*directions[(i+offset)%n][0]-b*directions[(i+offset)%n][1] for i,(a,b) in enumerate(targets))

    step = max(1, math.ceil(n/64))
    offset = min(range(0,n,step), key=lambda k:(cost(k),k))
    while step > 1:
        stride = max(1,step//4)
        candidates = {(offset+k)%n for k in range(-step,step+1,stride)}
        offset = min(candidates,key=lambda k:(cost(k),k))
        step = stride
    return [(index,node,sites[(i+offset)%n]) for i,(index,node) in enumerate(nodes)]


def organic_layout(data, cell_pixels=2, seed=73021):
    if isinstance(cell_pixels,bool) or not isinstance(cell_pixels,int) or cell_pixels not in {1,2,3,4}:
        raise ValueError("cell-pixels must be an integer from 1 to 4")
    if isinstance(seed,bool) or not isinstance(seed,int) or not 0 <= seed <= 4294967295:
        raise ValueError("seed must be an integer from 0 to 4294967295")
    sites = flood_shape(len(data["nodes"]),seed)
    birth = {(x,y):i for i,(x,y,_) in enumerate(sites)}
    connected, holes = shape_quality((x,y) for x,y,_ in sites)
    if not connected or holes:
        raise ValueError("The growth front did not form one solid connected region")
    radius = max(max(abs(x),abs(y)) for x,y,_ in sites)
    size = 2**math.ceil(math.log2(max(32,2*(radius+3)*cell_pixels)))
    origin = size//2-cell_pixels//2
    generations = defaultdict(list)
    for index,node in enumerate(data["nodes"]):
        generations[node["depth"]].append((index,node))
    cursor, cells = 0, [None]*len(data["nodes"])
    for depth in sorted(generations):
        level = generations[depth]
        allocation = sites[cursor:cursor+len(level)]
        cursor += len(level)
        for index,node,(x,y,arrival) in align_generation(level,allocation):
            cells[index] = {"node":index,"x":origin+x*cell_pixels,"y":origin+y*cell_pixels,
                            "tileX":x,"tileY":y,"arrival":arrival,"birth":birth[x,y]}
    rows = [[] for _ in range(size)]
    for cell in cells:
        for dy in range(cell_pixels):
            rows[cell["y"]+dy].append([cell["x"],cell_pixels,cell["node"]])
    for row in rows:
        row.sort()
    return {"mode":"organic","size":size,"rows":rows,"coverage":[cell_pixels**2]*len(cells),
            "cellPixels":cell_pixels,"seed":seed,"cells":cells,"connected":connected,"holes":holes,
            "rootCenter":[origin+cell_pixels/2,origin+cell_pixels/2],"displayScale":3,
            "bounds":[min(c["x"] for c in cells),min(c["y"] for c in cells),
                      max(c["x"]+cell_pixels for c in cells),max(c["y"]+cell_pixels for c in cells)]}
