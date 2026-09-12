#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["osqp>=1,<2", "numpy>=2,<3", "scipy>=1.14,<2", "ortools>=9.15,<10"]
# ///
"""Compare complete institutional compositions with dated, changing neighborhoods."""

import argparse
import copy
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import osqp
from scipy import sparse

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'skills/usefulcharts-style/scripts'))
from editorial_poster import EditorialPoster, measured_content
from render_chart import viewer, wrap


YEARS=[1180,1400,1550,1700,1850,2020]
Y_VALUES=[660,1090,1380,1710,2070,2540]
REGIONS={
    'g2':[(85,550),(85,550),(85,390),(85,330),(85,280),(85,270)],
    'g3':[(420,570),(450,590),(420,790),(380,755),(315,740),(90,640)],
    'g0':[(625,1160),(625,1160),(845,1190),(810,1175),(800,1155),(705,1145)],
    'g4':[(1200,1360),(1200,1360),(1240,1380),(1240,1380),(1200,1360),(1190,1380)],
    'g1':[(1240,1700),(1240,1700),(1430,1700),(1430,1700),(1430,1700),(1440,1700)],
}


def fit_greedy(data,active,heights,parts,page_scale,early_bias=0,padding=12,horizontal_cost=8,vertical_cost=6):
    """Place complete units in free vertical intervals, with room for descendants."""
    nodes={n['id']:n for n in active};ordered=sorted(active,key=lambda n:(n['founded'],n['id']))
    geometry={}
    for n in active:
        p=parts[n['id']];geometry[n['id']]=(math.floor(min(a['left'] for a in p)-n['x'])-padding,
            math.floor(min(a['top'] for a in p))-padding,math.ceil(max(a['right'] for a in p)-n['x'])+padding,
            math.ceil(max(a['bottom'] for a in p))+padding)
    parents={n['id']:[] for n in active};children={n['id']:[] for n in active}
    for edge in data['edges']:
        a,b=edge['source'],edge['target']
        if edge['kind']=='influence' or a not in nodes or b not in nodes:continue
        gap=math.ceil((heights[a]+heights[b])/2+34);parents[b].append((a,gap));children[a].append((b,gap))
    upper={n['id']:data['height']-110-geometry[n['id']][3] for n in active}
    for n in reversed(ordered):
        for child,gap in children[n['id']]:upper[n['id']]=min(upper[n['id']],upper[child]-gap)
    placed={};rectangles=[]
    for n in ordered:
        nid=n['id'];left,top,right,bottom=geometry[nid]
        xmin,xmax=65-left,data['width']-65-right
        ymin=max([round(118+(620-118)*page_scale)-top]+[placed[a][1]+gap for a,gap in parents[nid]])
        ymax=upper[nid]
        if ymin>ymax:raise ValueError(f'Greedy placement has no descendant room at {nid}.')
        px=round(n['x']);py=round(118+(float(np.interp(n['founded'],YEARS,Y_VALUES))-118)*page_scale-early_bias)
        x_values={min(xmax,max(xmin,px)),xmin,xmax}
        x_values.update(min(xmax,max(xmin,placed[a][0])) for a,_ in parents[nid])
        x_values.update(float(x) for x in range(math.ceil(xmin),math.floor(xmax)+1,12))
        for r in rectangles:x_values.update((min(xmax,max(xmin,r[0]-right)),min(xmax,max(xmin,r[2]-left))))
        best=None
        for x in sorted(x_values):
            blocked=sorted((r[1]-bottom,r[3]-top) for r in rectangles if min(x+right,r[2])>max(x+left,r[0])+.001)
            intervals=[];cursor=ymin
            for lo,hi in blocked:
                if hi<=cursor:continue
                if lo>cursor:intervals.append((cursor,min(lo,ymax)))
                cursor=max(cursor,hi)
                if cursor>ymax:break
            if cursor<=ymax:intervals.append((cursor,ymax))
            for lo,hi in intervals:
                if hi<lo-.001:continue
                y=min(hi,max(lo,py))
                cost=horizontal_cost*abs(x-px)+vertical_cost*abs(y-py)+sum(abs(x-placed[a][0])*2 for a,_ in parents[nid])
                option=(cost,abs(y-py),abs(x-px),x,y)
                if best is None or option<best:best=option
        if best is None:raise ValueError(f'Greedy placement found no complete local envelope for {nid}.')
        _,_,_,x,y=best;placed[nid]=(x,y);rectangles.append((x+left,y+top,x+right,y+bottom))
    for nid,(x,y) in placed.items():nodes[nid].update(x=round(x,3),y=round(y,3))
    return data,dict(method='greedy',complete_units=len(placed),remaining_descendant_space=True,early_bias=early_bias,padding=padding,
        horizontal_cost=horizontal_cost,vertical_cost=vertical_cost,coordinates='Integral with outward-rounded complete envelopes and attachment gaps.')


def fit_plane(data,active,heights,parts,window_x,window_y,seconds,hint=None,workers=1,page_scale=1,
              early_bias=0,horizontal_cost=8,vertical_cost=6,route_cost=1,crossing_cost=0):
    from ortools.sat.python import cp_model
    model=cp_model.CpModel();xs={};ys={};xi=[];yi=[];cost=[]
    for n in active:
        nid=n['id'];pr=parts[nid]
        left=math.floor(min(p['left'] for p in pr)-n['x'])-12
        right=math.ceil(max(p['right'] for p in pr)-n['x'])+12
        top=math.floor(min(p['top'] for p in pr))-12
        bottom=math.ceil(max(p['bottom'] for p in pr))+12
        target_x=round(n['x']);target_y=round(118+(float(np.interp(n['founded'],YEARS,Y_VALUES))-118)*page_scale-early_bias)
        xs[nid]=model.new_int_var(max(65-left,target_x-window_x),min(data['width']-65-right,target_x+window_x),f'x-{nid}')
        ys[nid]=model.new_int_var(max(round(118+(620-118)*page_scale)-top,target_y-window_y),min(data['height']-110-bottom,target_y+window_y),f'y-{nid}')
        xi.append(model.new_fixed_size_interval_var(xs[nid]+left,right-left,f'width-{nid}'))
        yi.append(model.new_fixed_size_interval_var(ys[nid]+top,bottom-top,f'height-{nid}'))
        dx=model.new_int_var(0,data['width'],f'dx-{nid}');dy=model.new_int_var(0,data['height'],f'dy-{nid}')
        model.add_abs_equality(dx,xs[nid]-target_x);model.add_abs_equality(dy,ys[nid]-target_y)
        cost.extend([dx*round(horizontal_cost),dy*round(vertical_cost)]);model.add_hint(xs[nid],round(hint[nid]['x']*page_scale) if hint else target_x)
        model.add_hint(ys[nid],round(118+(hint[nid]['y']-118)*page_scale) if hint else target_y)
    model.add_no_overlap_2d(xi,yi)
    for edge in data['edges']:
        a,b=edge['source'],edge['target']
        if a not in xs or b not in xs:continue
        if edge['kind']!='influence':model.add(ys[b]-ys[a]>=math.ceil((heights[a]+heights[b])/2+34))
        distance=model.new_int_var(0,data['width'],f'edge-{edge["id"]}')
        model.add_abs_equality(distance,xs[b]-xs[a]);cost.append(distance*route_cost)
        if route_cost>1:
            vertical=model.new_int_var(0,data['height'],f'edge-height-{edge["id"]}')
            model.add_abs_equality(vertical,ys[b]-ys[a]);cost.append(vertical)
    crossing_pairs=0
    if crossing_cost:
        nodes={n['id']:n for n in active};edges=[e for e in data['edges'] if e['kind']!='influence' and e['source'] in xs and e['target'] in xs]
        for i,e in enumerate(edges):
            for f in edges[i+1:]:
                a,b,c,d=e['source'],e['target'],f['source'],f['target']
                if len({a,b,c,d})<4:continue
                if max(nodes[a]['founded'],nodes[c]['founded'])>=min(nodes[b]['founded'],nodes[d]['founded']):continue
                first=model.new_bool_var(f'start-left-{crossing_pairs}');last=model.new_bool_var(f'end-left-{crossing_pairs}')
                model.add(xs[a]<=xs[c]).only_enforce_if(first);model.add(xs[a]>xs[c]).only_enforce_if(first.Not())
                model.add(xs[b]<=xs[d]).only_enforce_if(last);model.add(xs[b]>xs[d]).only_enforce_if(last.Not())
                crossing=model.new_bool_var(f'cross-{crossing_pairs}')
                model.add(first!=last).only_enforce_if(crossing);model.add(first==last).only_enforce_if(crossing.Not())
                cost.append(crossing*crossing_cost);crossing_pairs+=1
    model.minimize(sum(cost));solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=workers;solver.parameters.random_seed=26
    status=solver.solve(model)
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):raise ValueError(f'Plane search ended with {solver.status_name(status)}; no complete placement is accepted.')
    for n in active:n.update(x=solver.value(xs[n['id']]),y=solver.value(ys[n['id']]))
    return data,dict(method='cp',solver_status=solver.status_name(status),seconds=solver.wall_time,
        objective=solver.objective_value,best_bound=solver.best_objective_bound,window_x=window_x,window_y=window_y,workers=workers,
        route_cost=route_cost,crossing_cost=crossing_cost,crossing_proxy_pairs=crossing_pairs,
        warning='Endpoint-order penalties are a layout proxy; actual routed crossings and the final image must be inspected.')


def fit_relax(data,active,heights,parts,hint,page_scale,early_bias,horizontal_cost,vertical_cost,route_cost):
    """Smooth a complete composition while keeping a feasible separation for each pair."""
    if not hint:raise ValueError('Relaxation needs a complete, validated layout hint.')
    ordered=sorted(active,key=lambda n:n['id']);count=len(ordered);index={n['id']:i for i,n in enumerate(ordered)}
    old={n['id']:(hint[n['id']]['x']*page_scale,118+(hint[n['id']]['y']-118)*page_scale) for n in ordered}
    geometry={};terms=[];low=[];high=[]
    for n in ordered:
        pr=parts[n['id']];geometry[n['id']]=(math.floor(min(p['left'] for p in pr)-n['x'])-12,
            math.floor(min(p['top'] for p in pr))-12,math.ceil(max(p['right'] for p in pr)-n['x'])+12,
            math.ceil(max(p['bottom'] for p in pr))+12)
    def difference(a,b,gap):
        terms.append({a:-1.,b:1.});low.append(gap);high.append(np.inf)
    for i,a in enumerate(ordered):
        aid=a['id'];ax,ay=old[aid];al,at,ar,ab=geometry[aid]
        for j,b in enumerate(ordered[i+1:],i+1):
            bid=b['id'];bx,by=old[bid];bl,bt,br,bb=geometry[bid]
            xorder=(i,j,ar-bl) if ax<=bx else (j,i,br-al)
            yorder=(i+count,j+count,ab-bt) if ay<=by else (j+count,i+count,bb-at)
            clearx=abs(ax-bx)>=xorder[2]-.001;cleary=abs(ay-by)>=yorder[2]-.001
            if not clearx and not cleary:raise ValueError(f'The hint has overlapping complete units: {aid}, {bid}.')
            usex=clearx and (not cleary or abs(ax-bx)/xorder[2]>abs(ay-by)/yorder[2])
            difference(*(xorder if usex else yorder))
    for i,n in enumerate(ordered):
        l,t,r,b=geometry[n['id']]
        terms.append({i:1});low.append(65-l);high.append(data['width']-65-r)
        terms.append({i+count:1});low.append(round(118+(620-118)*page_scale)-t);high.append(data['height']-110-b)
    matrix=sparse.lil_matrix((count*2,count*2));linear=np.zeros(count*2)
    for i,n in enumerate(ordered):
        targets=[n['x'],118+(float(np.interp(n['founded'],YEARS,Y_VALUES))-118)*page_scale-early_bias]
        for offset,weight,target in ((0,horizontal_cost,targets[0]),(count,vertical_cost,targets[1])):
            k=i+offset;matrix[k,k]+=2*weight;linear[k]-=2*weight*target
    for edge in data['edges']:
        a,b=edge['source'],edge['target']
        if a not in index or b not in index:continue
        i,j=index[a],index[b]
        if edge['kind']!='influence':difference(i+count,j+count,math.ceil((heights[a]+heights[b])/2+34))
        for offset,weight in ((0,route_cost),(count,.25)):
            ia,ib=i+offset,j+offset;matrix[ia,ia]+=2*weight;matrix[ib,ib]+=2*weight
            matrix[ia,ib]-=2*weight;matrix[ib,ia]-=2*weight
    rows=[];cols=[];values=[]
    for k,term in enumerate(terms):
        for index_,value in term.items():rows.append(k);cols.append(index_);values.append(value)
    constraints=sparse.coo_matrix((values,(rows,cols)),shape=(len(terms),count*2)).tocsc()
    model=osqp.OSQP();model.setup(P=matrix.tocsc(),q=linear,A=constraints,l=np.array(low),u=np.array(high),
        verbose=False,eps_abs=1e-6,eps_rel=1e-9,max_iter=100000,polishing=True)
    model.warm_start(x=np.array([old[n['id']][0] for n in ordered]+[old[n['id']][1] for n in ordered]))
    fit=model.solve(raise_error=True);positions=fit.x;applied=constraints@positions
    violation=float(max(0,max(np.array(low)-applied),max(applied-np.array(high))))
    if violation>.001:raise ValueError(f'The relaxed layout has unresolved constraints: {violation}')
    for i,n in enumerate(ordered):n.update(x=round(float(positions[i]),3),y=round(float(positions[i+count]),3))
    return data,dict(method='relax',iterations=fit.info.iter,maximum_violation=violation,
        separation_constraints=len(terms),scope='Local optimum within the complete hint\'s chosen separation directions; not a global crossing optimum.')


def compose(original,profile,stage_weight=1,method='qp',window_x=200,window_y=300,seconds=45,hint=None,workers=1,page_scale=1,early_bias=0,anchors=None,padding=12,horizontal_cost=8,vertical_cost=6,route_cost=1,crossing_cost=0):
    data=copy.deepcopy(original);nodes={n['id']:n for n in data['nodes']}
    active=[n for n in data['nodes'] if n['group']!='g5']
    old_extents={g:(min(n['x'] for n in active if n['group']==g),max(n['x'] for n in active if n['group']==g)) for g in REGIONS}
    for n in active:
        if profile=='stages':
            lo,hi=old_extents[n['group']];fraction=(n['x']-lo)/(hi-lo)
            limits=REGIONS[n['group']]
            left=float(np.interp(n['founded'],YEARS,[r[0] for r in limits]))
            right=float(np.interp(n['founded'],YEARS,[r[1] for r in limits]))
            n['x']=(1-stage_weight)*n['x']+stage_weight*(left+fraction*(right-left))
    for nid,x in (anchors or {}).items():
        if nid not in nodes:raise ValueError(f'Unknown authored spine anchor: {nid}')
        nodes[nid]['x']=float(x)
    if page_scale!=1:
        assert method in ('cp','greedy','relax'),'Page-scale prototypes require both-axis placement.'
        data['width']=round(data['width']*page_scale);data['height']=round(data['height']*page_scale)
        for n in data['nodes']:n.update(x=n['x']*page_scale,y=118+(n['y']-118)*page_scale)
        for inset in data['insets']:
            x,y,w,h=inset['box'];inset['box']=[x*page_scale,118+(y-118)*page_scale,w*page_scale,h*page_scale]
    heights={n['id']:measured_content(n,n['width'],data['font_size'])[2] for n in data['nodes']}
    parts={n['id']:[dict(left=n['x']-n['width']/2,right=n['x']+n['width']/2,
        top=-heights[n['id']]/2,bottom=heights[n['id']]/2,kind='node')] for n in active}
    for a in data['annotations']:
        if a.get('node') not in parts:continue
        n=nodes[a['node']];size=a.get('size',12);width=a['width']
        h=len(wrap(a['label'],width-12,size,True))*size*1.24+9
        dy=a.get('dy',-60);dx=a.get('dx',0)
        parts[n['id']].append(dict(left=n['x']+dx-width/2,right=n['x']+dx+width/2,
            top=dy-h/2,bottom=dy+h/2,kind='label'))
    if method in ('cp','greedy','relax'):
        for e in data['edges']:e.pop('via',None);e.pop('corridor_y',None)
        if method=='greedy':return fit_greedy(data,active,heights,parts,page_scale,early_bias,padding,horizontal_cost,vertical_cost)
        if method=='relax':return fit_relax(data,active,heights,parts,hint,page_scale,early_bias,horizontal_cost,vertical_cost,route_cost)
        return fit_plane(data,active,heights,parts,window_x,window_y,seconds,hint,workers,page_scale,
            early_bias,horizontal_cost,vertical_cost,route_cost,crossing_cost)
    ordered=sorted(active,key=lambda n:(n['founded'],n['id']));index={n['id']:i for i,n in enumerate(ordered)}
    pairs={}
    for i,a in enumerate(ordered):
        for j,b in enumerate(ordered[i+1:],i+1):
            gaps=[p['bottom']-q['top']+(12 if 'label' in (p['kind'],q['kind']) else 22)
                for p in parts[a['id']] for q in parts[b['id']]
                if min(p['right'],q['right'])+12>max(p['left'],q['left'])]
            if gaps:pairs[(i,j)]=max(gaps)
    for e in data['edges']:
        e.pop('corridor_y',None);e.pop('via',None)
        if e['kind']=='influence' or e['source'] not in index or e['target'] not in index:continue
        i,j=index[e['source']],index[e['target']]
        assert i<j
        gap=heights[e['source']]/2+heights[e['target']]/2+34
        pairs[(i,j)]=max(pairs.get((i,j),0),gap)
    pairs=sorted((i,j,g) for (i,j),g in pairs.items());count=len(ordered)
    low=np.array([620-min(p['top'] for p in parts[n['id']]) for n in ordered])
    high=np.array([data['height']-120-max(p['bottom'] for p in parts[n['id']]) for n in ordered])
    earliest=low.copy()
    for i,j,gap in pairs:earliest[j]=max(earliest[j],earliest[i]+gap)
    if np.any(earliest>high):raise ValueError(f'The requested neighborhoods need {max(earliest-high):.2f} more vertical units.')
    rows=[];cols=[];values=[]
    for k,(i,j,g) in enumerate(pairs):rows.extend((k,k));cols.extend((i,j));values.extend((-1.,1.))
    constraints=sparse.coo_matrix((values,(rows,cols)),shape=(len(pairs),count)).tocsc()
    constraints=sparse.vstack((constraints,sparse.eye(count,format='csc')),format='csc')
    target=np.array([np.interp(n['founded'],YEARS,Y_VALUES) for n in ordered])
    model=osqp.OSQP();model.setup(P=sparse.eye(count,format='csc'),q=-target,A=constraints,
        l=np.r_[[g for _,_,g in pairs],low],u=np.r_[[np.inf]*len(pairs),high],
        verbose=False,eps_abs=1e-6,eps_rel=1e-9,max_iter=100000,polishing=True)
    fit=model.solve(raise_error=True);ys=fit.x
    violation=max([max(0,ys[i]+g-ys[j]) for i,j,g in pairs]+[max(low-ys),max(ys-high)])
    if violation>.001:raise ValueError(f'Unresolved separation: {violation:.6f}')
    for n,y in zip(ordered,ys):n['y']=round(float(y),3);n['x']=round(n['x'],3)
    return data,dict(profile=profile,stage_weight=stage_weight,iterations=fit.info.iter,
        constraints=len(pairs),maximum_violation=violation,maximum_date_preference_shift=float(max(abs(ys-target))))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--before',default='2b9f6595');parser.add_argument('--profile',choices=['chronology','stages'],default='stages')
    parser.add_argument('--stage-weight',type=float,default=1);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--method',choices=['qp','cp','greedy','relax'],default='qp');parser.add_argument('--window-x',type=int,default=200)
    parser.add_argument('--window-y',type=int,default=300);parser.add_argument('--seconds',type=float,default=45)
    parser.add_argument('--hint',type=Path);parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--page-scale',type=float,default=1)
    parser.add_argument('--early-bias',type=float,default=0)
    parser.add_argument('--anchors',type=Path)
    parser.add_argument('--padding',type=float,default=12)
    parser.add_argument('--horizontal-cost',type=float,default=8);parser.add_argument('--vertical-cost',type=float,default=6)
    parser.add_argument('--route-cost',type=int,default=1);parser.add_argument('--crossing-cost',type=int,default=0)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    driver=Path(__file__).read_bytes();(args.output/'driver.py').write_bytes(driver)
    filename='skills/usefulcharts-style/assets/examples/usefulcharts-style/atlas-of-inquiry.json'
    source=json.loads(subprocess.check_output(['git','show',f'{args.before}:{filename}'],cwd=ROOT))
    report=dict(before=args.before,profile=args.profile,stage_weight=args.stage_weight,method=args.method,
        driver_sha256=hashlib.sha256(driver).hexdigest(),
        window_x=args.window_x,window_y=args.window_y,seconds=args.seconds,workers=args.workers,
        page_scale=args.page_scale,early_bias=args.early_bias,padding=args.padding,horizontal_cost=args.horizontal_cost,
        vertical_cost=args.vertical_cost,route_cost=args.route_cost,crossing_cost=args.crossing_cost,anchors=str(args.anchors) if args.anchors else None,
        hint=str(args.hint) if args.hint else None)
    try:
        hint=None
        if args.hint:
            h=json.loads(args.hint.read_text(encoding='utf-8'));factor=source['width']/h['width']
            hint={n['id']:n|dict(x=n['x']*factor,y=118+(n['y']-118)*factor) for n in h['nodes']}
        anchors=json.loads(args.anchors.read_text(encoding='utf-8')) if args.anchors else None
        data,placement=compose(source,args.profile,args.stage_weight,args.method,args.window_x,args.window_y,args.seconds,hint,args.workers,args.page_scale,args.early_bias,anchors,args.padding,args.horizontal_cost,args.vertical_cost,args.route_cost,args.crossing_cost)
        visual={'x','y','width','height','size','detail_size','icon_width'}
        facts=lambda d:[{k:v for k,v in n.items() if k not in visual} for n in d['nodes']]
        assert facts(data)==facts(source)
        edges=lambda d:[{k:v for k,v in e.items() if k not in ('corridor_y','via')} for e in d['edges']]
        assert edges(data)==edges(source)
        assert all(data[k]==source[k] for k in ('groups','annotations','title','subtitle','source_note','reading_note'))
        insets=lambda d:[{k:v for k,v in a.items() if k!='box'} for a in d['insets']]
        assert insets(data)==insets(source)
        report.update(placement=placement,all_facts_preserved=True)
        (args.output/'source.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        svg,layout=EditorialPoster(data).render()
        (args.output/'poster.svg').write_text(svg,encoding='utf-8');(args.output/'poster.html').write_text(viewer(svg,data['title']),encoding='utf-8')
        report.update(status='pass',placement=placement,layout=layout,all_facts_preserved=True)
    except (AssertionError,ValueError) as error:report.update(status='fail',error=str(error))
    (args.output/'prototype.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report));return 0 if report['status']=='pass' else 1


if __name__=='__main__':raise SystemExit(main())
