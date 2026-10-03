#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Boundary ports and orthogonal routes around semantic node interiors."""

import heapq
import math


NORMALS = {"left": (-1, 0), "right": (1, 0), "top": (0, -1), "bottom": (0, 1)}
EPS = 1e-6


def anchor(box, side):
    x, y, w, h = box
    nx, ny = NORMALS[side]
    return [x + w * (1 + nx) / 2, y + h * (1 + ny) / 2]


def radial_anchor(box, toward, shape="rect"):
    """Intersect a center ray with a rectangular or elliptical object boundary."""
    x,y,w,h=box
    cx,cy=x+w/2,y+h/2
    dx,dy=toward[0]-cx,toward[1]-cy
    if abs(dx)+abs(dy)<EPS:
        raise ValueError("A radial edge needs distinct object centers")
    divisor=math.hypot(dx/(w/2),dy/(h/2)) if shape=="ellipse" else max(abs(dx)/(w/2),abs(dy)/(h/2))
    return [cx+dx/divisor,cy+dy/divisor]


def interior(point, box, inset=0):
    x, y, w, h = box
    return x+inset+EPS < point[0] < x+w-inset-EPS and y+inset+EPS < point[1] < y+h-inset-EPS


def segment_enters(a, b, box):
    """Open-interior intersection; exact contact/tangency is allowed."""
    x, y, w, h = box
    lo, hi = 0.0, 1.0
    for start, end, low, high in zip(a, b, (x+EPS, y+EPS), (x+w-EPS, y+h-EPS)):
        delta = end-start
        if abs(delta) < EPS:
            if not low < start < high:
                return False
        else:
            u, v = sorted(((low-start)/delta, (high-start)/delta))
            lo, hi = max(lo, u), min(hi, v)
            if hi-lo <= EPS:
                return False
    return hi-lo > EPS


def simplify(points):
    result = []
    for point in points:
        point = list(point)
        if result and math.dist(result[-1], point) < EPS:
            continue
        if len(result) >= 2:
            a, b = result[-2:]
            cross = (b[0]-a[0])*(point[1]-b[1])-(b[1]-a[1])*(point[0]-b[0])
            dot = (b[0]-a[0])*(point[0]-b[0])+(b[1]-a[1])*(point[1]-b[1])
            if abs(cross)<EPS and dot>=0:
                result.pop()
        result.append(point)
    return result


def collision_cost(a, b, previous):
    cost = 0
    for points in previous:
        for c, d in zip(points, points[1:]):
            vertical = abs(a[0]-b[0]) < EPS
            other_vertical = abs(c[0]-d[0]) < EPS
            if vertical == other_vertical:
                fixed, axis = (0, 1) if vertical else (1, 0)
                if abs(a[fixed]-c[fixed]) < 3:
                    overlap = min(max(a[axis],b[axis]),max(c[axis],d[axis]))-max(min(a[axis],b[axis]),min(c[axis],d[axis]))
                    if overlap > 2:
                        cost += 10000+overlap*2
            else:
                v1,v2,h1,h2 = (a,b,c,d) if vertical else (c,d,a,b)
                hit=(v1[0],h1[1])
                if min(v1[1],v2[1])-EPS <= hit[1] <= max(v1[1],v2[1])+EPS and min(h1[0],h2[0])-EPS <= hit[0] <= max(h1[0],h2[0])+EPS:
                    # Visibility-grid intersections often occur exactly at a
                    # candidate edge endpoint; those are still real crossings.
                    if all(math.dist(hit,p)>EPS for p in (points[0],points[-1])):
                        cost += 10000
    return cost


def validate_route(points, objects, endpoints):
    for name, obj in objects.items():
        if obj.get("kind", "node") == "container":
            continue
        if any(segment_enters(a, b, obj["box"]) for a,b in zip(points,points[1:])):
            raise ValueError(f"Connector enters object {name}; choose an outward port or reroute through free space")
    for end_index, neighbor_index, binding in ((0,1,endpoints[0]),(-1,-2,endpoints[1])):
        if not binding:
            continue
        end, neighbor = points[end_index], points[neighbor_index]
        nx, ny = NORMALS[binding["side"]]
        dx, dy = neighbor[0]-end[0], neighbor[1]-end[1]
        if dx*nx+dy*ny <= EPS or abs(dx*ny-dy*nx)>EPS:
            raise ValueError(f"Connector must approach {binding['object']} from outside its {binding['side']} side")


def route(start, end, objects, endpoints=(None, None), canvas=(1200, 800), previous=(), via=None, clearance=6, preferred=None):
    """Find a short route with outward terminal stubs and object clearance."""
    if math.dist(start,end)<EPS:
        raise ValueError("A connector needs distinct endpoints")
    if via is not None:
        points=simplify([start,*via,end])
        validate_route(points,objects,endpoints)
        return points
    boxes = [o["box"] for o in objects.values() if o.get("kind", "node")=="node"]
    stubs=[]
    for point, binding in zip((start,end),endpoints):
        normal=NORMALS[binding["side"]] if binding else (0,0)
        stubs.append(tuple(point[i]+normal[i]*clearance for i in (0,1)))
    a,b=stubs
    preferred=preferred or [(a[0]+b[0])/2,(a[1]+b[1])/2]
    inflated=[[x-clearance,y-clearance,w+2*clearance,h+2*clearance] for x,y,w,h in boxes]
    # Exact boundary stubs lie on inflated boxes. Crossing a node is never a fallback.
    if any(interior(p,box) for p in stubs for box in inflated):
        raise ValueError("Port has no clear outward exit; choose another side or increase spacing")
    xs={a[0],b[0],preferred[0],clearance,canvas[0]-clearance}
    ys={a[1],b[1],preferred[1],clearance,canvas[1]-clearance}
    for x,y,w,h in inflated:
        xs.update((x,x+w));ys.update((y,y+h))
    for path in previous:
        for x,y in path:
            xs.update((x-6,x+6));ys.update((y-6,y+6))
    xs=sorted(x for x in xs if 0<=x<=canvas[0])
    ys=sorted(y for y in ys if 0<=y<=canvas[1])
    if a[0] not in xs or b[0] not in xs or a[1] not in ys or b[1] not in ys:
        raise ValueError("Outward port exit leaves the canvas; allocate a small outer margin")
    if len(xs)*len(ys)>60000:
        raise ValueError("Routing grid is too dense; simplify the composition or supply valid waypoints")
    points={(i,j):(x,y) for i,x in enumerate(xs) for j,y in enumerate(ys)
            if not any(interior((x,y),box) for box in inflated)}
    begin=(xs.index(a[0]),ys.index(a[1])); goal=(xs.index(b[0]),ys.index(b[1]))
    if begin not in points or goal not in points:
        raise ValueError("Port exit is obstructed")
    start_direction=(0 if endpoints[0]["side"] in {"left","right"} else 1) if endpoints[0] else -1
    end_direction=(0 if endpoints[1]["side"] in {"left","right"} else 1) if endpoints[1] else -1
    initial=(begin, start_direction)
    costs={initial:0};parents={};queue=[(0,begin,start_direction)]
    final=None
    while queue:
        cost,key,direction=heapq.heappop(queue)
        state=(key,direction)
        if cost>costs[state]+EPS:
            continue
        if key==goal:
            final=state;break
        for di,dj,new_direction in ((1,0,0),(-1,0,0),(0,1,1),(0,-1,1)):
            neighbor=(key[0]+di,key[1]+dj)
            if neighbor not in points:
                continue
            p,q=points[key],points[neighbor]
            if any(segment_enters(p,q,box) for box in inflated):
                continue
            bend=direction>=0 and direction!=new_direction
            amount=math.dist(p,q)+(18+.005*math.dist(p,preferred) if bend else 0)+collision_cost(p,q,previous)
            if neighbor==goal and end_direction>=0 and new_direction!=end_direction:
                amount+=18+.005*math.dist(q,preferred)
            candidate=cost+amount
            next_state=(neighbor,new_direction)
            if candidate+EPS<costs.get(next_state,math.inf):
                costs[next_state]=candidate;parents[next_state]=state
                heapq.heappush(queue,(candidate,neighbor,new_direction))
    if final is None:
        raise ValueError("No unobstructed connector route; increase gutters or choose outward-facing ports")
    middle=[]
    state=final
    while True:
        middle.append(points[state[0]])
        if state==initial:
            break
        state=parents[state]
    result=simplify([start,*reversed(middle),end])
    validate_route(result,objects,endpoints)
    return result
