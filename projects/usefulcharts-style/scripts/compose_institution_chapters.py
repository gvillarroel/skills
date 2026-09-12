#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["ortools>=9.15,<10", "osqp>=1,<2", "numpy>=2,<3", "scipy>=1.14,<2"]
# ///
"""Prototype editorial chapters for the authored synthetic institution study."""

import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from ortools.sat.python import cp_model

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'skills/usefulcharts-style/scripts'))
from editorial_poster import EditorialPoster, measured_content
from render_chart import viewer, wrap

# Editorial selection applies only to this author-created fictional example.
# All original notes remain in research_note; user-supplied records are not edited.
PRINT_NOTES = set('''chroniclers glass pumps glass-union pendulum pump-school
mechanical metrology precision engines-west nightbooks newcalendar reformers
observatories meridian-net instruments-lab astronomical sky-data open-sky
pilot-union ocean-voyage merchant naval rescue maritime sea-college ocean-safety
light spectrum photographic moving-image imaging earth-data'''.split())


def facts(data):
    return dict(nodes=[{key: n.get(key) for key in ('id', 'label', 'founded', 'group', 'icon')}
                       | {'note': n.get('research_note', n.get('detail', ''))} for n in data['nodes']],
                edges=[{key: e.get(key) for key in ('id', 'source', 'target', 'kind')} for e in data['edges']],
                groups=data['groups'])


def relax(data, active, geometry, heights, targets):
    import numpy as np
    import osqp
    from scipy import sparse
    order=sorted(active,key=lambda n:n['id']);count=len(order);indices={n['id']:i for i,n in enumerate(order)}
    matrix=sparse.lil_matrix((2*count,2*count));linear=np.zeros(2*count)
    terms=[];low=[];high=[]
    def constraint(coefficients,lo,hi=float('inf')):
        terms.append(coefficients);low.append(lo);high.append(hi)
    for i,a in enumerate(order):
        al,at,ar,ab=geometry[a['id']]
        constraint({i:1},72-al,1548-ar);constraint({i+count:1},597-at,2170-ab)
        for j,b in enumerate(order[i+1:],i+1):
            bl,bt,br,bb=geometry[b['id']]
            if a['y']+ab+20<=b['y']+bt+.002:constraint({i+count:-1,j+count:1},ab-bt+20)
            elif b['y']+bb+20<=a['y']+at+.002:constraint({j+count:-1,i+count:1},bb-at+20)
            elif a['x']+ar+20<=b['x']+bl+.002:constraint({i:-1,j:1},ar-bl+20)
            elif b['x']+br+20<=a['x']+al+.002:constraint({j:-1,i:1},br-al+20)
            else:raise ValueError('The relaxation seed is not fully separated: '+a['id']+', '+b['id'])
        for offset,weight,target in ((0,8,targets[a['id']][0]),(count,6,targets[a['id']][1]-90)):
            k=i+offset;matrix[k,k]+=2*weight;linear[k]-=2*weight*target
    for e in data['edges']:
        a,b=e['source'],e['target']
        if a not in indices or b not in indices:continue
        i,j=indices[a],indices[b]
        if e['kind']!='influence':constraint({i+count:-1,j+count:1},heights[a]/2-geometry[b][1]+26)
        for offset,weight in ((0,4),(count,0.3)):
            x,y=i+offset,j+offset
            matrix[x,x]+=2*weight;matrix[y,y]+=2*weight;matrix[x,y]-=2*weight;matrix[y,x]-=2*weight
    rows=[];cols=[];values=[]
    for k,row in enumerate(terms):
        for idx,value in row.items():rows.append(k);cols.append(idx);values.append(value)
    constraints=sparse.coo_matrix((values,(rows,cols)),shape=(len(terms),2*count)).tocsc()
    solver=osqp.OSQP();solver.setup(P=matrix.tocsc(),q=linear,A=constraints,l=np.array(low),u=np.array(high),
        verbose=False,eps_abs=1e-4,eps_rel=1e-7,max_iter=100000,polishing=True)
    solver.warm_start(x=np.array([n['x'] for n in order]+[n['y'] for n in order]))
    solution=solver.solve(raise_error=False);positions=solution.x;result=constraints@positions
    violation=float(max(0,max(np.array(low)-result),max(result-np.array(high))))
    if violation>.01:raise ValueError(f'Chapter relaxation retains a violated envelope constraint: {violation} ({solution.info.status}).')
    for i,n in enumerate(order):n.update(x=round(float(positions[i]),3),y=round(float(positions[i+count]),3))
    return dict(status=solution.info.status,iterations=solution.info.iter,maximum_violation=violation,method='Feasible local quadratic relaxation of a complete seed; not a global optimum.')


def compose(source, profile, seconds, method):
    data = copy.deepcopy(source)
    for n in data['nodes']:
        n['research_note'] = n.get('detail', '')
        if n['id'] not in PRINT_NOTES:
            n['detail'] = ''
    data['editorial_note'] = ('The complete original fictional record notes remain in research_note. '
        'The poster prints selected consequences; no supplied historical dataset was abbreviated.')
    if profile == 'edited':
        return data, {'method': 'Original centers with selected fictional captions.'}
    data['height'] = 2300
    nodes = {n['id']: n for n in data['nodes']}
    active = [n for n in data['nodes'] if n['group'] != 'g5']
    # These local stages are schematic chapters, not a common numeric time scale.
    regions = {
        'g2': (668, 1771, 640, 1360, (110, 580), (110, 465)),
        'g0': (672, 2235, 640, 2160, (645, 1050), (700, 1050)),
        'g1': (668, 2074, 640, 1925, (1130, 1500), (1350, 1490)),
        'g3': (1154, 2084, 1150, 2110, (420, 680), (155, 655)),
        'g4': (1254, 1978, 1350, 2130, (1140, 1190), (1110, 1350)),
    }
    if profile == 'expanded':
        regions['g0'] = (672, 2235, 640, 2160, (645, 1050), (650, 1270))
        regions['g1'] = (668, 2074, 640, 2050, (1130, 1500), (1360, 1490))
    for g, (old_top, old_end, top, end, start_x, end_x) in regions.items():
        members = [n for n in active if n['group'] == g]
        low, high = min(n['x'] for n in members), max(n['x'] for n in members)
        for n in members:
            t = max(0, min(1, (n['y'] - old_top) / (old_end - old_top)))
            fraction = (n['x'] - low) / (high - low)
            lo, hi = [a + t * (b - a) for a, b in zip(start_x, end_x)]
            n.update(x=lo + fraction * (hi - lo), y=top + t * (end - top))
    if profile == 'expanded':
        # Terminal groups open out after shorter histories finish, retaining identity.
        for nid, x in {'stellar-centre': 620, 'sky-data': 685, 'southern-array': 1070,
                       'open-sky': 835, 'orbital': 1250, 'earth-data': 1410}.items():
            nodes[nid]['x'] = x
    targets={n['id']:(n['x'],n['y']) for n in active}
    heights = {nid: measured_content(n, n['width'], data['font_size'])[2] for nid, n in nodes.items()}
    geometry = {nid: [-n['width']/2, -heights[nid]/2, n['width']/2, heights[nid]/2] for nid, n in nodes.items()}
    for a in data['annotations']:
        nid = a['node']; size = a.get('size', 12)
        h = len(wrap(a['label'], a['width']-12, size, True))*size*1.24+9
        dx, dy = a.get('dx', 0), a.get('dy', -60)
        a['dy'] = max(dy, -heights[nid]/2-h/2-20)
        l, t, r, b = geometry[nid]
        geometry[nid] = [min(l, dx-a['width']/2), min(t, a['dy']-h/2), max(r, dx+a['width']/2), b]
    if method in ('greedy','greedy-relax'):
        active_ids={n['id'] for n in active}; parents={nid:[] for nid in active_ids}; children={nid:[] for nid in active_ids}
        for e in data['edges']:
            a,b=e['source'],e['target']
            for key in ('via','corridor_y','source_port','target_port'):e.pop(key,None)
            if a in active_ids and b in active_ids and e['kind']!='influence':
                gap=heights[a]/2-geometry[b][1]+26
                parents[b].append((a,gap)); children[a].append((b,gap))
        ordered=[];remaining=set(active_ids);completed=set()
        while remaining:
            ready=[nodes[nid] for nid in remaining if all(a in completed for a,_ in parents[nid])]
            if not ready:raise ValueError('The institutional graph contains a structural cycle.')
            n=min(ready,key=lambda n:(n['y'],n['x'],n['id']))
            ordered.append(n);remaining.remove(n['id']);completed.add(n['id'])
        upper={nid:2180-geometry[nid][3] for nid in active_ids}
        for n in reversed(ordered):
            for b,gap in children[n['id']]:upper[n['id']]=min(upper[n['id']],upper[b]-gap)
        placed={}; obstacles=[]
        for n in ordered:
            nid=n['id'];l,t,r,b=geometry[nid];l-=10;r+=10;t-=10;b+=10
            xmin,xmax=62-l,1558-r; ymin=max([587-t]+[placed[a][1]+gap for a,gap in parents[nid]])
            ymax=upper[nid]-10;px,py=n['x'],n['y']-90;best=None
            candidates={min(xmax,max(xmin,px)),xmin,xmax}
            candidates.update(min(xmax,max(xmin,placed[a][0])) for a,_ in parents[nid])
            candidates.update(range(int(xmin)+1,int(xmax),12))
            for x in sorted(candidates):
                blocked=sorted((rect[1]-b,rect[3]-t) for rect in obstacles if min(x+r,rect[2])>max(x+l,rect[0])+.001)
                free=[];cursor=ymin
                for lo,hi in blocked:
                    if hi<=cursor:continue
                    if lo>cursor:free.append((cursor,min(lo,ymax)))
                    cursor=max(cursor,hi)
                    if cursor>ymax:break
                if cursor<=ymax:free.append((cursor,ymax))
                for lo,hi in free:
                    if hi<lo:continue
                    y=min(hi,max(lo,py));cost=8*abs(x-px)+6*abs(y-py)+sum(abs(x-placed[a][0]) for a,_ in parents[nid])
                    option=(cost,abs(y-py),x,y)
                    if best is None or option<best:best=option
            if best is None:raise ValueError('No complete greedy chapter placement for '+nid)
            _,_,x,y=best;n.update(x=round(x,3),y=round(y,3));placed[nid]=(n['x'],n['y']);obstacles.append((x+l,y+t,x+r,y+b))
        result=dict(method='Greedy chapter preferences with complete content, descendant room and causal order.',global_calendar_alignment=False)
        if method=='greedy-relax':result['relaxation']=relax(data,active,geometry,heights,targets)
        return data,result
    model = cp_model.CpModel(); xs = {}; ys = {}; rects_x = []; rects_y = []; cost = []
    import math
    for n in active:
        nid = n['id']; l,t,r,b = geometry[nid]
        l,t,r,b = math.floor(l)-10, math.floor(t)-10, math.ceil(r)+10, math.ceil(b)+10
        px,py = round(n['x']),round(n['y'])
        xs[nid] = model.new_int_var(max(62-l,px-145), min(1558-r,px+145), 'x-'+nid)
        ys[nid] = model.new_int_var(max(587-t,py-190), min(2180-b,py+190), 'y-'+nid)
        rects_x.append(model.new_fixed_size_interval_var(xs[nid]+l,r-l,'rx-'+nid))
        rects_y.append(model.new_fixed_size_interval_var(ys[nid]+t,b-t,'ry-'+nid))
        dx=model.new_int_var(0,1620,'dx-'+nid); dy=model.new_int_var(0,2300,'dy-'+nid)
        model.add_abs_equality(dx,xs[nid]-px); model.add_abs_equality(dy,ys[nid]-py)
        cost.extend((dx*8,dy*6)); model.add_hint(xs[nid],px); model.add_hint(ys[nid],py)
    model.add_no_overlap_2d(rects_x,rects_y)
    for e in data['edges']:
        a,b=e['source'],e['target']
        for key in ('via','corridor_y','source_port','target_port'): e.pop(key,None)
        if a in xs and b in xs:
            if e['kind'] != 'influence':
                gap=math.ceil(heights[a]/2-geometry[b][1]+26)
                model.add(ys[b]-ys[a]>=gap)
            dist=model.new_int_var(0,1620,'route-'+e['id'])
            model.add_abs_equality(dist,xs[a]-xs[b]); cost.append(dist)
    model.minimize(sum(cost)); solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=seconds; solver.parameters.num_search_workers=1
    solver.parameters.random_seed=30
    status=solver.solve(model)
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        raise ValueError('No complete chapter placement: '+solver.status_name(status))
    for n in active: n.update(x=solver.value(xs[n['id']]),y=solver.value(ys[n['id']]))
    return data, dict(method='Declared chapter preferences with full measured envelopes.',
        solver_status=solver.status_name(status),objective=solver.objective_value,bound=solver.best_objective_bound,
        seconds=solver.wall_time,global_calendar_alignment=False)


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--before',default='0be67c64')
    p.add_argument('--profile',choices=('edited','chapters','expanded'),required=True)
    p.add_argument('--seconds',type=float,default=35);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--method',choices=('greedy','greedy-relax','cp'),default='greedy')
    args=p.parse_args(); args.output.mkdir(parents=True,exist_ok=True)
    path='skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.json'
    original=json.loads(subprocess.check_output(['git','show',args.before+':'+path],cwd=ROOT))
    report=dict(before=args.before,profile=args.profile,driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (args.output/'driver.py').write_bytes(Path(__file__).read_bytes())
    try:
        data,placement=compose(original,args.profile,args.seconds,args.method)
        assert facts(original)==facts(data), 'The complete institution records changed.'
        report.update(placement=placement,record_inventory_preserved=True,
            printed_captions=sum(bool(n.get('detail')) for n in data['nodes']),
            complete_record_notes=sum(bool(n.get('research_note')) for n in data['nodes']))
        (args.output/'source.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        svg,layout=EditorialPoster(data).render()
        (args.output/'poster.svg').write_text(svg,encoding='utf-8')
        (args.output/'poster.html').write_text(viewer(svg,data['title']),encoding='utf-8')
        report.update(status='pass',layout=layout)
    except (ValueError,AssertionError) as e: report.update(status='fail',error=str(e))
    (args.output/'prototype.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='layout'})); return report['status']!='pass'


if __name__=='__main__': raise SystemExit(main())
