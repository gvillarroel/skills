#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Dense, authored poster compositions with varied emphasis and contextual insets."""

from __future__ import annotations

import copy
import base64
import json
import html
import math
from pathlib import Path

from render_chart import Poster, require, number, color, ident, wrap, fmt, text_color, contrast, overlaps, segment_hits, route, compress, KINDS, automatic_lineage, text_width
from editorial_art import symbol
from cohort_layout import place_cohorts


def rounded_path(points, radius=9):
    if len(points)<3:return 'M '+' L '.join(f'{fmt(x)} {fmt(y)}' for x,y in points)
    parts=[f'M {fmt(points[0][0])} {fmt(points[0][1])}']
    for a,b,c in zip(points,points[1:],points[2:]):
        d1=abs(a[0]-b[0])+abs(a[1]-b[1]);d2=abs(c[0]-b[0])+abs(c[1]-b[1])
        r=min(radius,d1/2,d2/2)
        if not r:continue
        q=(b[0]+(a[0]-b[0])*r/d1,b[1]+(a[1]-b[1])*r/d1)
        t=(b[0]+(c[0]-b[0])*r/d2,b[1]+(c[1]-b[1])*r/d2)
        parts.append(f'L {fmt(q[0])} {fmt(q[1])} Q {fmt(b[0])} {fmt(b[1])} {fmt(t[0])} {fmt(t[1])}')
    parts.append(f'L {fmt(points[-1][0])} {fmt(points[-1][1])}')
    return ' '.join(parts)


class EditorialPoster(Poster):
    def __init__(self,data):
        original=copy.deepcopy(data)
        adjusted=copy.deepcopy(data)
        if adjusted.get('layout')=='auto':
            adjusted=automatic_lineage(adjusted)
            font=original.get('font_size',13)
            width=max(104,max(text_width(word,font,True)+16 for n in adjusted['nodes'] for word in n['label'].split()))
            adjusted['width']=original.get('width',max(1200,160+adjusted['columns']*(width+24)))
            adjusted['height']=original.get('height',max(1200,300+len(adjusted['rows'])*135))
            counts={n['id']:sum(e['source']==n['id'] and e['kind']!='influence' for e in adjusted['edges']) for n in adjusted['nodes']}
            for n in adjusted['nodes']:
                n.setdefault('width',width)
                n.setdefault('style','pill' if n['row']==0 else 'plain' if counts[n['id']]==1 and not n.get('emphasis') else 'card')
            adjusted['layout']='resolved'
        else:
            adjusted.setdefault('width',1800);adjusted.setdefault('height',2700)
        adjusted.setdefault('frame_color','#902F29');adjusted.setdefault('paper_color','#EDEAD8')
        adjusted['font_size']=16
        super().__init__(adjusted)
        if original.get('layout')=='auto':self.data['layout']='auto'
        self.source_data=original
        self.font=number(original.get('font_size',13),'font_size')
        require(10<=self.font<=24,'Editorial body type must be 10–24 units; inspect it at intended print size.')
        self.title_height=118
        self.footer_height=44
        self.title_size=min(82,(self.w-300)/max(1,text_width(data['title'].upper(),1,True)*.74))
        require(self.title_size>=30,'The title is too long for a legible single-line header.')
        self.title_lines=[data['title'].upper()]
        self.left,self.right=65,self.w-65
        self.top,self.bottom=170,self.h-80
        self.annotation_boxes=[]
        self.image_sources=set()
        self.union_mark=(1.05,1.9,1.55)

    def line(self,points,paint,width=3,dash='',extra=''):
        d=rounded_path(compress(points),8)
        self.add(f'<path d="{d}" fill="none" stroke="{paint}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="{dash}" {extra}/>')

    def artwork(self,kind,x,y,w,h,paint,variant=0):
        if kind.startswith(('museum-','object-')):
            filename=kind.split('-',1)[1]+'.jpg'
            require(filename[:-4].isdigit(),'Museum sample IDs must be numeric.')
            source=Path(__file__).resolve().parent.parent/'assets'/('objects' if kind.startswith('object-') else 'portraits')/filename
            if filename not in self.image_sources:
                records=json.loads(source.with_name('provenance.json').read_text(encoding='utf-8'))
                item=next(row for row in records['items'] if row['file']==filename)
                self.add('<metadata data-artwork-source="'+filename+'">'+html.escape(json.dumps(item))+'</metadata>')
                self.image_sources.add(filename)
            encoded=base64.b64encode(source.read_bytes()).decode('ascii')
            fit='xMidYMid meet' if kind.startswith('object-') else 'xMidYMin slice'
            self.add(f'<svg data-artwork="public-domain-museum-image" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" viewBox="0 0 100 100"><image href="data:image/jpeg;base64,{encoded}" width="100" height="100" preserveAspectRatio="{fit}"/></svg>')
            return
        require(kind in ('shield','crown','star','sun','compass','globe','astrolabe','orbit','book','archive','wheel','gear','lens','prism','ship','anchor','tower','observatory','press','machine','obelisk','monument','leaf','branch','portrait','bust'),'Unknown original artwork type.')
        self.add(f'<g data-artwork="{kind}" transform="translate({fmt(x)} {fmt(y)}) scale({fmt(w/100)} {fmt(h/100)})">{symbol(kind,paint,variant)}</g>')

    def frame_and_key(self):
        self.rect((0,0,self.w,self.h),self.frame)
        self.rect((34,self.title_height,self.w-68,self.h-self.title_height-34),self.paper,'#FFFFFF',3,13)
        self.text(self.w/2,87,self.title_lines[0],self.title_size,text_color(self.frame),bold=True,background=self.frame,
                  css='font-family="PosterTitle, Arial Narrow, sans-serif" letter-spacing="0.8"')
        # A neutral folio mark provides balance without reproducing another publisher's logo.
        self.artwork('book',37,21,73,70,'#E0BE69')
        imprint=self.data.get('imprint',['ORIGINAL STUDY','Source notes below','Editable poster'])
        require(len(imprint)<=3 and all(isinstance(s,str) and text_width(s,10)<145 for s in imprint),'Use up to three short imprint lines.')
        for i,line in enumerate(imprint):
            self.text(self.w-45,38+i*16,line,10 if i==0 else 9.5,'#FFFFFF',anchor='end',bold=i==0,background=self.frame)

    def footer(self):
        lines=wrap(self.data['source_note']+' '+self.data.get('reading_note',self.default_note()),self.w-155,10)
        require(len(lines)<=2,'Keep editorial source and reading notes to two compact lines.')
        for i,line in enumerate(lines):self.text(self.w/2,self.h-63+i*13,line,10)

    def node_content(self,node,width):
        size=node.get('size',self.font)
        icon_width=node.get('icon_width',30) if node.get('icon') else 0
        usable=width-icon_width-10
        name=wrap(node['label'],usable,size,True)
        detail=wrap(node.get('detail',''),usable,node.get('detail_size',size*.77))
        height=13+len(name)*size*1.18+len(detail)*size*.94
        if icon_width:height=max(height,icon_width+4)
        return name,detail,height

    def graph_layout(self):
        data=self.data
        if data.get('layout')=='cohorts':
            require(self.mode=='genealogy','Cohort layout is for explicit genealogical relationships.')
            data['nodes']=place_cohorts(data,self.node_content,self.left,self.right,data.get('cohort_top',225),data.get('cohort_bottom',self.bottom-45))
        for node in data['nodes']:
            n=copy.deepcopy(node);nid=ident(n['id'])
            require(nid not in self.nodes,f'Duplicate node ID: {nid}')
            require(n['group'] in self.groups,f'Unknown group for {nid}')
            width=number(n.get('width',90),f'{nid}.width')
            _,_,height=self.node_content(n,width)
            if 'x' in n and 'y' in n:
                x,y=number(n['x'],f'{nid}.x'),number(n['y'],f'{nid}.y')
            else:
                columns=data['columns'];rows=data['rows']
                x=self.left+(self.right-self.left)*(n['col']+.5)/columns
                y=self.top+55+(self.bottom-self.top-120)*n['row']/max(1,len(rows)-1)
            n['row']=y
            self.make_node(n,(x-width/2,y-height/2,width,height))
        require(self.nodes,'At least one node is required.')
        self.check_boxes()
        self.build_unions()
        self.build_routes()
        self.draw_annotations()
        self.draw_insets()

    def check_boxes(self):
        items=list(self.boxes.items())
        for i,(nid,b) in enumerate(items):
            require(b[0]>=self.left-15 and b[0]+b[2]<=self.right+15,f'Node {nid} exceeds chart width.')
            require(b[1]>=self.title_height+12 and b[1]+b[3]<=self.bottom+8,f'Node {nid} exceeds chart height.')
            for oid,other in items[i+1:]:require(not overlaps(b,other,5),f'Nodes {nid} and {oid} overlap or lack a 5-unit gutter.')

    def build_routes(self):
        seen=set();pairs=set();segments=[]
        row_bands={}
        for box in self.boxes.values():
            row=round(box[1]+box[3]/2,3)
            lo,hi=row_bands.get(row,(box[1],box[1]+box[3]))
            row_bands[row]=(min(lo,box[1]),max(hi,box[1]+box[3]))
        for edge in self.relations:
            eid,source,target,kind=(edge[k] for k in ('id','source','target','kind'))
            ident(eid)
            require(eid not in seen and (source,target,kind) not in pairs,f'Duplicate relationship {eid}')
            seen.add(eid);pairs.add((source,target,kind))
            require(kind in KINDS and target in self.nodes and source in (self.nodes|self.unions),f'Unresolved relation {eid}')
            require(source!=target,f'Self-link {eid}')
            t=self.boxes[target]
            end=(t[0]+t[2]/2,t[1])
            if source in self.unions:
                start=self.unions[source]['point'];source_y=start[1]
            else:
                b=self.boxes[source];start=(b[0]+b[2]/2,b[1]+b[3]);source_y=self.nodes[source]['row']
            require(kind=='influence' or source_y<self.nodes[target]['row'],f'Relation {eid} goes backward.')
            a,b=(start[0],start[1]+10),(end[0],end[1]-10)
            if edge.get('via'):
                path=compress([start]+[tuple(map(float,p)) for p in edge['via']]+[end])
                require(all(p[0]==q[0] or p[1]==q[1] for p,q in zip(path,path[1:])),f'Non-orthogonal authored corridor for {eid}')
            else:
                default_middle=(a[1]+b[1])/2
                if self.data.get('layout')=='cohorts':
                    prior=row_bands.get(round(source_y,3));following=row_bands.get(round(self.nodes[target]['row'],3))
                    if prior and following and following[0]>prior[1]:default_middle=(prior[1]+following[0])/2
                middle=edge.get('corridor_y',default_middle)
                trial=compress([start,(start[0],middle),(end[0],middle),end])
                # Ports touch their own boxes; every other part must stay outside,
                # including a corridor that was requested beyond the target top.
                if not any(segment_hits(p,q,box,0) for p,q in zip(trial,trial[1:]) for box in self.boxes.values()):
                    path=trial
                else:
                    path=None;last_error=None
                    world=(self.left-12,self.top-26,self.right+12,self.bottom+12)
                    for margin in (30,90,220,600,max(self.w,self.h)):
                        bounds=(max(world[0],min(a[0],b[0])-margin),max(world[1],min(a[1],b[1])-margin),min(world[2],max(a[0],b[0])+margin),min(world[3],max(a[1],b[1])+margin))
                        nearby=[box for box in self.boxes.values() if box[0]-14<bounds[2] and box[0]+box[2]+14>bounds[0] and box[1]-14<bounds[3] and box[1]+box[3]+14>bounds[1]]
                        try:
                            path=compress([start]+route(a,b,nearby,bounds,segments)+[end]);break
                        except ValueError as error:last_error=error
                    require(path is not None,f'Cannot route relationship {eid}: {last_error}')
            require(not any(segment_hits(p,q,box,0) for p,q in zip(path,path[1:]) for box in self.boxes.values()),f'Relationship {eid} crosses a node, including its own source or target.')
            group=edge.get('group',self.nodes[target]['group']);paint=self.groups[group]['color']
            width=edge.get('weight',2.8 if kind in ('branch','descent') else 1.8)
            dash={'influence':'1 5','uncertain':'1 4','adopted':'7 3 1 3','succession':'8 3 1 3'}.get(kind,'')
            self.line(path,self.paper,width+2.4)
            self.line(path,paint,width,dash,extra=f'data-edge-id="{eid}" data-source="{source}" data-target="{target}" data-kind="{kind}" data-route-style="rounded"')
            if kind=='influence':
                x,y=end
                self.add(f'<path d="M {fmt(x-3)} {fmt(y-6)} L {fmt(x)} {fmt(y)} L {fmt(x+3)} {fmt(y-6)}" fill="none" stroke="{paint}" stroke-width="1.5"/>')
            self.routes.append(dict(edge,points=path));segments.extend(zip(path,path[1:]))

    def draw_nodes(self):
        if self.mode=='timeline':return self.draw_intervals()
        for nid,n in self.nodes.items():
            x,y,w,h=self.boxes[nid];paint=self.groups[n['group']]['color'];style=n.get('style','card')
            require(style in ('plain','card','pill','emblem','hero'),'Unknown editorial node treatment.')
            fill=self.paper if style=='plain' else '#FFFEF7' if style=='pill' else paint
            ink=text_color(fill)
            self.add(f'<g id="node-{nid}" data-node-id="{nid}" data-group="{n["group"]}" data-treatment="{style}">')
            self.rect((x,y,w,h),fill,paint if style=='pill' else 'none',2.5,12 if style=='pill' else 1,extra='data-node-box="true"')
            iconw=n.get('icon_width',30) if n.get('icon') else 0
            if iconw:
                self.rect((x+2,y+2,iconw,h-4),'#FFFEF7')
                self.artwork(n['icon'],x+2,y+(h-iconw)/2,iconw,iconw,paint,n.get('variant',0))
            names,details,needed=self.node_content(n,w)
            size=n.get('size',self.font);small=n.get('detail_size',size*.77)
            xx=x+iconw+(w-iconw)/2
            yy=y+(h-needed)/2+4+size*.86
            for line in names:
                self.text(xx,yy,line,size,ink,bold=True,owner=nid,background=fill);yy+=size*1.18
            for line in details:
                self.text(xx,yy,line,small,ink,owner=nid,background=fill);yy+=size*.94
            self.add('</g>')
        for u in self.unions.values():
            x,y=u['point'];self.add(f'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="1.8" fill="{self.muted}"/>')

    def draw_annotations(self):
        for a in self.data.get('annotations',[]):
            if a.get('node'):
                require(a['node'] in self.boxes,'Annotation references an unknown node.')
                anchor=self.boxes[a['node']]
                x,y=anchor[0]+anchor[2]/2+a.get('dx',0),anchor[1]+anchor[3]/2+a.get('dy',0)
            else:x,y=a['x'],a['y']
            w=a.get('width',130);size=a.get('size',13)
            paint=self.groups[a['group']]['color'] if a.get('group') else self.ink
            lines=wrap(a['label'],w-10,size,True)
            h=len(lines)*size*1.12+7
            if a.get('kind')=='pill':
                moves=sorted(((dx,dy) for dy in range(-90,91,10) for dx in range(-60,61,20)),key=lambda p:abs(p[0])+abs(p[1])*1.2)
                candidates=[(x+dx,y+dy) for dx,dy in moves]
                safe=[]
                for xx,yy in candidates:
                    box=(xx-w/2,yy-h/2,w,h)
                    if box[0]<48 or box[0]+w>self.w-48:continue
                    if any(overlaps(box,b,5) for b in self.boxes.values()):continue
                    if any(overlaps(box,b,5) for b in self.annotation_boxes):continue
                    safe.append((xx,yy,box))
                require(safe,f'No clear placement for annotation {a["label"]!r}. Move its anchor.')
                x,y,placed=safe[0];self.annotation_boxes.append(placed)
            if a.get('kind')=='pill':self.rect((x-w/2,y-h/2,w,h),'#FFFEF7',paint,2.5,12)
            if a.get('kind')=='heading':
                if a.get('icon'):self.artwork(a['icon'],x-22,y-64,44,49,paint,a.get('variant',0))
            yy=y-h/2+size
            for line in lines:
                css='font-family="Georgia, serif" font-style="italic"' if a.get('kind')=='heading' else ''
                self.text(x,yy,line,size,bold=a.get('kind')!='heading',css=css,background='#FFFEF7' if a.get('kind')=='pill' else self.paper);yy+=size*1.12

    def map_art(self,x,y,w,h,mapping=None,opacity=1):
        source=json.loads((Path(__file__).resolve().parent.parent/'assets/maps/world-countries.json').read_text(encoding='utf-8'))
        self.add(f'<g data-artwork="map" transform="translate({fmt(x)} {fmt(y)}) scale({fmt(w/720)} {fmt(h/290)})" opacity="{opacity}">')
        for country in source['countries']:
            group=(mapping or {}).get(country['id'])
            paint=self.groups[group]['color'] if group in self.groups else '#C9C8B9'
            self.add(f'<path d="{country["d"]}" fill="{paint}" stroke="{self.paper}" stroke-width="0.35"/>')
        self.add('</g>')

    def draw_insets(self):
        for item in self.data.get('insets',[]):
            x,y,w,h=item['box']
            self.text(x+w/2,y+14,item['title'],18,bold=True)
            if item['kind']=='map':
                self.map_art(x,y+40,w,h-65,item.get('countries',{}))
                self.text(x+w/2,y+h-4,item.get('note','Illustrative geography'),10,self.muted)
            elif item['kind']=='isotype':
                groups=list(self.groups.values())
                totals={gid:sum(n['group']==gid for n in self.data['nodes']) for gid in self.groups}
                selected=[g for g in groups if totals[g['id']]>12]
                pitch=(h-55)/max(1,len(selected))
                for i,g in enumerate(selected):
                    yy=y+43+i*pitch
                    self.text(x+5,yy,g['label'],12,anchor='start',bold=True)
                    count=totals[g['id']]
                    for j in range(count):
                        xx=x+8+(j%24)*12;dy=yy+9+(j//24)*15
                        self.add(f'<circle cx="{xx+2.5}" cy="{dy+2}" r="2.5" fill="{g["color"]}"/><path d="M{xx} {dy+5}h5l1 6h-7Z" fill="{g["color"]}"/>')
                    self.text(x+w-8,yy+28,str(count),11,anchor='end')
                self.text(x+w/2,y+h-4,'One symbol = one named institution',10,self.muted)

    def timeline_layout(self):
        d=self.data
        require(not any(d.get(k) for k in ('nodes','edges','unions')),'Timeline uses periods, events, and explicit transitions.')
        time=d['time'];start,end,step=[number(time[k],f'time.{k}') for k in ('start','end','step')]
        require(end>start and step>0 and (end-start)/step<=100,'Invalid time scale.')
        self.top=190;self.bottom=self.h-112;self.left=110;self.right=self.w-65
        scale=lambda year:self.top+(year-start)/(end-start)*(self.bottom-self.top)
        lanes={l['id']:i for i,l in enumerate(d['lanes'])}
        pitch=(self.right-self.left)/len(lanes)
        if d.get('map_texture'):
            self.add(f'<defs><clipPath id="chronology-field"><rect x="{self.left-40}" y="{self.top-10}" width="{self.right-self.left+55}" height="{self.bottom-self.top+20}"/></clipPath></defs><g clip-path="url(#chronology-field)">')
            require(d['map_texture'] in (True,'natural-earth','milner-1850'),'Unknown map texture.')
            if d['map_texture']=='milner-1850':
                source=Path(__file__).resolve().parent.parent/'assets/maps/milner-1850.jpg'
                record=json.loads(source.with_suffix('.json').read_text(encoding='utf-8'))
                encoded=base64.b64encode(source.read_bytes()).decode('ascii')
                self.add('<metadata data-artwork-source="milner-1850.jpg">'+html.escape(json.dumps(record))+'</metadata>')
                self.add(f'<image data-artwork="historical-map" href="data:image/jpeg;base64,{encoded}" x="-700" y="135" width="3380" height="2630" opacity=".12" preserveAspectRatio="xMidYMid meet"/>')
            else:
                for i in range(3):self.map_art(-480+(i%2)*240,self.top-160+i*850,2700,1087.5,opacity=.14)
            self.add('</g>')
        for i,l in enumerate(d['lanes']):
            x=self.left+i*pitch
            for j,line in enumerate(wrap(l['label'].upper(),pitch-14,13,True)):self.text(x+pitch/2,self.top-24+j*14,line,13,bold=True)
        for i in range(math.floor((end-start)/step)+1):
            yy=scale(start+i*step)
            self.line([(self.left-26,yy),(self.right+9,yy)],'#FFFEF6',2)
            self.text(self.left-31,yy+4,self.year_label(start+i*step),10.5,anchor='end',bold=True)
        for era in d.get('eras',[]):
            yy=scale(era['start']);hh=scale(era['end'])-yy
            self.line([(45,yy),(self.right+9,yy)],'#8F8874',2)
            cx,cy=53,yy+hh/2
            self.text(cx,cy,era['label'].upper(),14,bold=True,css=f'transform="rotate(-90 {cx} {cy})" letter-spacing="2"')
        for period in d['periods']:
            n=copy.deepcopy(period);nid=ident(n['id'])
            require(nid not in self.nodes and n['lane'] in lanes and n['group'] in self.groups,f'Invalid period {nid}')
            a,b=number(n['start'],f'{nid}.start'),number(n['end'],f'{nid}.end')
            require(start<=a<b<=end,f'Invalid period dates {nid}')
            width=n.get('bar_width',32)
            x=self.left+pitch*lanes[n['lane']]+n.get('offset',18)
            height=scale(b)-scale(a)
            size=n.get('size',13)
            names=wrap(n['label'],height-14,size,True)
            require(len(names)*size*1.1<=width-4,f'Period {nid} label needs a wider ribbon or shorter wording.')
            n['_vertical_lines']=names
            self.make_node(n,(x,scale(a),width,height))
        for nid,a in self.boxes.items():
            for oid,b in self.boxes.items():
                if nid<oid:require(not overlaps(a,b),f'Periods {nid} and {oid} overlap.')
        transition_ids=set()
        for edge in d.get('transitions',[]):
            ident(edge['id'])
            require(edge['id'] not in transition_ids,'Duplicate timeline transition ID.')
            transition_ids.add(edge['id'])
            require(edge['source'] in self.nodes and edge['target'] in self.nodes and edge['kind'] in ('succession','division','union','uncertain'),'Timeline transitions require known periods and an explicit succession, division, union, or uncertain relation.')
            a,b=self.boxes[edge['source']],self.boxes[edge['target']]
            source_port=number(edge.get('source_port',.5),'source_port')
            target_port=number(edge.get('target_port',.5),'target_port')
            require(5<=a[2]*source_port<=a[2]-5 and 5<=b[2]*target_port<=b[2]-5,'Timeline ports must remain at least 5 units inside their ribbon edges.')
            start_point=(a[0]+a[2]*source_port,a[1]+a[3]);end_point=(b[0]+b[2]*target_port,b[1])
            require(end_point[1]>=start_point[1]-.01,'A timeline continuation must not go backward.')
            mid=(start_point[1]+end_point[1])/2
            points=compress([start_point,(start_point[0],mid),(end_point[0],mid),end_point])
            paint=self.groups[self.nodes[edge['target']]['group']]['color']
            require(edge.get('style','dotted') in ('dotted','ribbon'),'Unknown timeline transition style.')
            if edge.get('style')=='ribbon':
                # An explicitly supplied transition occupies its own dated gap.
                # It joins full-width ribbons without changing either period.
                flow=number(edge.get('ribbon_width',0),'ribbon_width')
                if flow:
                    require(flow>0 and flow/2<=min(a[2]*source_port,a[2]*(1-source_port),b[2]*target_port,b[2]*(1-target_port)),'Transition width exceeds its attachment port.')
                    left_a,right_a=start_point[0]-flow/2,start_point[0]+flow/2
                    left_b,right_b=end_point[0]-flow/2,end_point[0]+flow/2
                else:left_a,right_a,left_b,right_b=a[0],a[0]+a[2],b[0],b[0]+b[2]
                self.add(f'<path data-transition-fill="{edge["id"]}" d="M {fmt(left_a)} {fmt(start_point[1])} L {fmt(right_a)} {fmt(start_point[1])} L {fmt(right_b)} {fmt(end_point[1])} L {fmt(left_b)} {fmt(end_point[1])} Z" fill="{paint}"/>')
                # The semantic path follows the center of the filled bridge.
                # Drawing an orthogonal elbow as well creates a false second fork.
                points=[start_point,end_point]
            self.line(points,paint,2,'1 4' if edge.get('style','dotted')=='dotted' else '',extra=f'data-edge-id="{edge["id"]}" data-source="{edge["source"]}" data-target="{edge["target"]}" data-kind="{edge["kind"]}" data-route-style="rounded"')
            self.routes.append(dict(edge,points=points))
        # Event annotations are supplied data. Their dates use the same numeric scale.
        for index,event in enumerate(d.get('events',[])):
            require(event['lane'] in lanes and start<=event['year']<=end,'Invalid event lane or date.')
            x=self.left+pitch*lanes[event['lane']]+event.get('offset',64)
            yy=scale(event['year']);width=event.get('width',pitch-78)
            event_id=ident(event.get('id',f'event-{index}'))
            self.add(f'<g data-event-id="{event_id}" data-year="{event["year"]}" data-origin-y="{fmt(yy)}">')
            size=event.get('size',10.5)
            for line in wrap(event['label'],width,size,True):
                self.text(x,yy+size,line,size,anchor='start',bold=True);yy+=size*1.18
            small=event.get('detail_size',size*.88)
            for line in wrap(event.get('detail',''),width,small):
                self.text(x,yy+small,line,small,anchor='start');yy+=small*1.18
            if event.get('icon'):
                art_size=event.get('art_size',56)
                self.artwork(event['icon'],x+(width-art_size)/2,yy+5,art_size,art_size,self.groups[event.get('group',d['groups'][0]['id'])]['color'],event.get('variant',0))
            self.add('</g>')
        self.draw_annotations()

    def draw_intervals(self):
        for nid,n in self.nodes.items():
            x,y,w,h=self.boxes[nid];paint=self.groups[n['group']]['color'];ink=text_color(paint)
            self.add(f'<g id="node-{nid}" data-node-id="{nid}" data-group="{n["group"]}">')
            self.rect((x,y,w,h),paint,self.paper,1,5,extra='data-node-box="true"')
            size=n.get('size',13);lines=n['_vertical_lines'];cx=x+w/2;cy=y+h/2
            for i,line in enumerate(lines):
                self.text(cx,cy+(i-(len(lines)-1)/2)*size*1.1+size*.3,line,size,ink,bold=True,owner=nid,background=paint,
                    css=f'transform="rotate(-90 {fmt(cx)} {fmt(cy)})"')
            self.add('</g>')


if __name__=='__main__':
    print('Use render_chart.py with design: editorial to render an authored poster.')
