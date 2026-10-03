#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Keep orthogonal relationship arrows out of opaque annotation plaques."""
import re
import heapq
import math

def orthogonal_route(start,end,obstacles,bounds,preferred=(),clearance=4,occupied=()):
    """Find a clear rectilinear visibility route through actual backing gutters."""
    left,top,width,height=bounds;right,bottom=left+width,top+height
    boxes=[(x-clearance,y-clearance,w+2*clearance,h+2*clearance) for x,y,w,h in obstacles]
    preferred=[*preferred,*[(p[0]+dx,p[1]+dy) for segment in occupied for p in segment for dx,dy in [(0,0),(-3,-3),(3,3)]]]
    xs=sorted({start[0],end[0],left+4,right-4,*(p[0] for p in preferred),*(v for x,y,w,h in boxes for v in (x,x+w))})
    ys=sorted({start[1],end[1],top+4,bottom-4,*(p[1] for p in preferred),*(v for x,y,w,h in boxes for v in (y,y+h))})
    xs=[v for v in xs if left<=v<=right];ys=[v for v in ys if top<=v<=bottom]
    source=(xs.index(start[0]),ys.index(start[1]));target=(xs.index(end[0]),ys.index(end[1]))
    cache={}
    def valid(key):
        if key not in cache:
            x,y=xs[key[0]],ys[key[1]]
            cache[key]=not any(a<x<a+w and b<y<b+h for a,b,w,h in boxes)
        return cache[key]
    if not valid(source) or not valid(target):raise ValueError(f'Arrow port lies inside an opaque backing; move its port outside the silhouette: start={start}, end={end}, blocked={[box for box in boxes if any(box[0]<p[0]<box[0]+box[2] and box[1]<p[1]<box[1]+box[3] for p in (start,end))]}')
    queue=[(0,0,source,None)];cost={(source,None):0};parent={};last=None
    while queue:
        _,spent,key,direction=heapq.heappop(queue)
        if spent!=cost.get((key,direction)):continue
        if key==target:last=(key,direction);break
        for dx,dy,axis in [(1,0,0),(-1,0,0),(0,1,1),(0,-1,1)]:
            nxt=(key[0]+dx,key[1]+dy)
            if not(0<=nxt[0]<len(xs) and 0<=nxt[1]<len(ys)) or not valid(nxt):continue
            a,b=(xs[key[0]],ys[key[1]]),(xs[nxt[0]],ys[nxt[1]])
            if any(hits(a,b,box) for box in boxes) or any(overlaps(a,b,c,d) for c,d in occupied):continue
            distance=abs(a[0]-b[0])+abs(a[1]-b[1])
            bend=6 if direction is not None and axis!=direction else 0
            candidate=spent+distance+bend;state=(nxt,axis)
            if candidate>=cost.get(state,math.inf):continue
            cost[state]=candidate;parent[state]=(key,direction)
            heuristic=abs(b[0]-end[0])+abs(b[1]-end[1])
            heapq.heappush(queue,(candidate+heuristic,candidate,nxt,axis))
    if last is None:raise ValueError('No clear arrow gutter exists; expand the layout instead of covering the shaft/head')
    points=[]
    while last:
        key,_=last;points.append((xs[key[0]],ys[key[1]]));last=parent.get(last)
    points.reverse();result=[]
    for point in points:
        if len(result)>1 and ((result[-2][0]==result[-1][0]==point[0]) or (result[-2][1]==result[-1][1]==point[1])):result[-1]=point
        else:result.append(point)
    return result

def hits(a,b,box):
    x,y,w,h=box
    if a[1]==b[1]:return y<a[1]<y+h and max(min(a[0],b[0]),x)<min(max(a[0],b[0]),x+w)
    if a[0]==b[0]:return x<a[0]<x+w and max(min(a[1],b[1]),y)<min(max(a[1],b[1]),y+h)
    lo,hi=0.0,1.0
    for origin,delta,minimum,maximum in [(a[0],b[0]-a[0],x,x+w),(a[1],b[1]-a[1],y,y+h)]:
        entry,exit=sorted(((minimum-origin)/delta,(maximum-origin)/delta));lo,hi=max(lo,entry),min(hi,exit)
    return lo<hi and hi>0 and lo<1

def clear_path(path, plaques, modules, bounds, occupied=()):
    """Detour only an obstructed span; preserve endpoint/port identity."""
    points=[];x=y=0
    for command,a,b in re.findall(r'([MLHV])\s*(-?\d+(?:\.\d+)?)(?:[ ,]+(-?\d+(?:\.\d+)?))?',path):
        if command in 'ML':x,y=float(a),float(b)
        elif command=='H':x=float(a)
        else:y=float(a)
        points.append((x,y))
    def replan(routepoints):
        def port_and_stub(port,next_point):
            dx,dy=next_point[0]-port[0],next_point[1]-port[1];distance=math.hypot(dx,dy)
            normal=(dx/distance,dy/distance)
            owner=next((box for box in modules if box[0]-.01<=port[0]<=box[0]+box[2]+.01 and box[1]-.01<=port[1]<=box[1]+box[3]+.01),None)
            candidates=[(port,normal)]
            if owner:
                x,y,w,h=owner
                fx=min(1,max(0,(port[0]-x)/w));fy=min(1,max(0,(port[1]-y)/h))
                fraction=fx if abs(normal[1])>abs(normal[0]) else fy
                for fraction in [fraction, .2, .4, .6, .8]:
                    candidates += [((x-3,y+h*fraction),(-1,0)),((x+w+3,y+h*fraction),(1,0)),
                                   ((x+w*fraction,y-3),(0,-1)),((x+w*fraction,y+h+3),(0,1))]
            choices=[]
            for candidate,vector in candidates:
                stub=(candidate[0]+vector[0]*12,candidate[1]+vector[1]*12)
                if any(a-4<stub[0]<a+w+4 and b-4<stub[1]<b+h+4 for a,b,w,h in [*modules,*plaques]):continue
                if any(hits(candidate,stub,box) for box in plaques) or any(overlaps(candidate,stub,c,d) for c,d in occupied):continue
                choices.append((math.dist(candidate,port),candidate,stub))
            if not choices:raise ValueError('No visible body port remains outside annotation plaques; expand its gutter')
            _,candidate,stub=min(choices)
            return candidate,stub
        first,source_stub=port_and_stub(routepoints[0],routepoints[1])
        last,target_stub=port_and_stub(routepoints[-1],routepoints[-2])
        return [first,*orthogonal_route(source_stub,target_stub,[*modules,*plaques],bounds,routepoints,clearance=4,occupied=occupied),last]
    for _ in range(max(1,len(plaques)*3)):
        collision=next(((i,box) for i,(a,b) in enumerate(zip(points,points[1:])) for box in plaques if hits(a,b,box)),None)
        if not collision:break
        i,(left,top,width,height)=collision;a,b=points[i:i+2];right,bottom=left+width,top+height
        candidates=[]
        if a[1]==b[1]:
            forward=b[0]>a[0];entry=left-4 if forward else right+4;exit=right+4 if forward else left-4
            for lane in (top-4,bottom+4):candidates.append([a,(entry,a[1]),(entry,lane),(exit,lane),(exit,b[1]),b])
        else:
            forward=b[1]>a[1];entry=top-4 if forward else bottom+4;exit=bottom+4 if forward else top-4
            for lane in (left-4,right+4):candidates.append([a,(a[0],entry),(lane,entry),(lane,exit),(b[0],exit),b])
        safe=[p for p in candidates if not any(hits(u,v,box) for u,v in zip(p,p[1:]) for box in [*plaques,*modules])]
        if not safe:
            # Escape real node ports before searching the expanded visibility
            # grid; a route on a body's boundary would lose half its shaft.
            points=replan(points)
            break
        choice=min(safe,key=lambda p:sum(abs(u[0]-v[0])+abs(u[1]-v[1]) for u,v in zip(p,p[1:])))
        points[i:i+2]=choice
    if any(overlaps(a,b,c,d) for a,b in zip(points,points[1:]) for c,d in occupied):points=replan(points)
    if any(hits(a,b,box) for a,b in zip(points,points[1:]) for box in plaques):
        raise ValueError('Arrow routing still intersects an opaque focus label')
    number=lambda n:f'{n:.6f}'.rstrip('0').rstrip('.') or '0'
    output=f'M{number(points[0][0])} {number(points[0][1])}'
    for a,b in zip(points,points[1:]):
        output += f' H{number(b[0])}' if a[1]==b[1] else f' V{number(b[1])}' if a[0]==b[0] else f' L{number(b[0])} {number(b[1])}'
    return output


def overlaps(a,b,c,d):
    """Reject coincident route spans while permitting perpendicular crossings."""
    if a[1]==b[1] and c[1]==d[1] and abs(a[1]-c[1])<1e-5:
        return min(max(a[0],b[0]),max(c[0],d[0]))-max(min(a[0],b[0]),min(c[0],d[0]))>1
    if a[0]==b[0] and c[0]==d[0] and abs(a[0]-c[0])<1e-5:
        return min(max(a[1],b[1]),max(c[1],d[1]))-max(min(a[1],b[1]),min(c[1],d[1]))>1
    return False

def path_points(path):
    points=[];x=y=0
    for command,a,b in re.findall(r'([MLHV])\s*(-?\d+(?:\.\d+)?)(?:[ ,]+(-?\d+(?:\.\d+)?))?',path):
        if command in 'ML':x,y=float(a),float(b)
        elif command=='H':x=float(a)
        else:y=float(a)
        points.append((x,y))
    return points
