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

from render_chart import Poster, require, number, color, ident, wrap, fmt, attr, text_color, contrast, overlaps, segment_hits, route_regions, compress, KINDS, automatic_lineage, text_width, collinear_overlap
from editorial_art import symbol
from cohort_layout import place_cohorts, compact_cohort_defaults
from story_layout import pack_stories
from editorial_landmarks import landmark_content
from timeline_geometry import lane_geometry, duration_width, transition_geometry, period_parts
from timeline_annotations import event_content


def separated_content(node,width,font):
    """Measure a named panel with an independent date and contextual caption."""
    size=node.get('size',font);small=node.get('detail_size',size*.77)
    icon_width=node.get('icon_width',30) if node.get('icon') else 0
    names=wrap(node['label'],width-icon_width-10,size,True)
    details=wrap(node.get('detail',''),width-12,small)
    dates=wrap(str(node.get('date_label','')),width-12,small)
    date_height=len(dates)*small*1.25+3 if dates else 0
    panel_height=max(6+len(names)*size*1.18,icon_width+4 if icon_width else 0)
    caption_height=3+len(details)*small*1.25 if details else 0
    return dict(names=names,details=details,dates=dates,date_height=date_height,
        panel_height=panel_height,caption_height=caption_height,height=date_height+panel_height+caption_height+2)


def measured_content(node, width, font):
    require(node.get('detail_position','inside') in ('inside','outside'),'Node detail_position must be inside or outside.')
    require('date_label' not in node or node.get('detail_position')=='outside','A separate date_label requires detail_position: outside.')
    if node.get('detail_position')=='outside':
        parts=separated_content(node,width,font)
        return parts['names'],parts['details'],parts['height']
    size=node.get('size',font)
    icon_width=node.get('icon_width',30) if node.get('icon') else 0
    usable=width-icon_width-10
    name=wrap(node['label'],usable,size,True)
    detail=wrap(node.get('detail',''),usable,node.get('detail_size',size*.77))
    height=13+len(name)*size*1.18+len(detail)*size*.94
    return name,detail,max(height,icon_width+4 if icon_width else 0)


def attachment_port(box,side):
    """Return the exact content-envelope attachment and its outward search point."""
    require(side in ('top','bottom','left','right'),'Unknown relationship attachment side.')
    x,y,w,h=box
    point={'top':(x+w/2,y),'bottom':(x+w/2,y+h),'left':(x,y+h/2),'right':(x+w,y+h/2)}[side]
    normal={'top':(0,-1),'bottom':(0,1),'left':(-1,0),'right':(1,0)}[side]
    return point,tuple(point[i]+10*normal[i] for i in (0,1))


def cohort_key(data,width):
    """Keep category identification in a key, clear of genealogical branches."""
    rows=[[]];used=0
    for group in data['groups']:
        w=min(260,text_width(group['label'],13,True)+32)
        if rows[-1] and used+w+18>width-130:rows.append([]);used=0
        rows[-1].append((group,w));used+=w+18
    cells=[];y=140
    for row in rows:
        total=sum(w for _,w in row)+18*(len(row)-1);x=(width-total)/2
        height=max(len(wrap(g['label'],w-22,13,True))*15+10 for g,w in row)
        for group,w in row:
            cells.append(dict(group=group['id'],label=group['label'],box=[x,y,w,height]));x+=w+18
        y+=height+10
    return dict(cells=cells,height=y-140-10)


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
        packed=adjusted.get('layout')=='packed'
        compact=(adjusted.get('layout') in ('auto','cohorts') and len(adjusted.get('nodes',[]))<=30) or packed
        compact_time=adjusted.get('mode')=='timeline' and adjusted.get('layout')=='compact'
        compact=compact or compact_time
        font=original.get('font_size',18 if compact else 13)
        if packed:
            structural=[e for e in adjusted.get('edges',[]) if e['kind']!='influence']
            for n in adjusted['nodes']:
                n.setdefault('detail_position','outside')
                major=n.get('emphasis') or sum(e['target']==n['id'] for e in structural)>1
                count=sum(e['source']==n['id'] for e in structural)
                n.setdefault('style','hero' if major else 'emblem' if n.get('icon') else 'plain' if count<=1 else 'card')
                n.setdefault('size',font+2 if major else font)
                if n.get('icon'):n.setdefault('icon_width',50)
                n.setdefault('width',max(176,max(text_width(word,n['size'],True)+18 for word in n['label'].split()))+(24 if major else 0)+n.get('icon_width',0))
            first=pack_stories(adjusted,lambda n,w:measured_content(n,w,font))
            if adjusted.get('legend',True):
                key=cohort_key(first,first['width']);extra=max(0,key['height']-25)
                adjusted=pack_stories(adjusted,lambda n,w:measured_content(n,w,font),top=190+extra)
                adjusted['_cohort_key']=key
            else:adjusted=first
        elif adjusted.get('layout')=='auto':
            adjusted=automatic_lineage(adjusted)
            width=max(176 if compact else 104,max(text_width(word,font,True)+16 for n in adjusted['nodes'] for word in n['label'].split()))
            counts={n['id']:sum(e['source']==n['id'] and e['kind']!='influence' for e in adjusted['edges']) for n in adjusted['nodes']}
            parents={n['id']:sum(e['target']==n['id'] and e['kind']!='influence' for e in adjusted['edges']) for n in adjusted['nodes']}
            for n in adjusted['nodes']:
                major=n.get('emphasis') or parents[n['id']]>1
                n.setdefault('style','pill' if n['row']==0 else 'hero' if major else 'emblem' if n.get('icon') else 'plain' if counts[n['id']]==1 else 'card')
                if compact:
                    n.setdefault('size',font+2 if major else font)
                    n.setdefault('icon_width',50 if n.get('icon') else 0)
                n.setdefault('width',width+(35 if major else 0)+(n.get('icon_width',30) if n.get('icon') else 0))
            column_width=max(n['width'] for n in adjusted['nodes'])
            adjusted['width']=original.get('width',max(1000 if compact else 1200,130+adjusted['columns']*(column_width+26)))
            row_heights=[max((measured_content(n,n['width'],font)[2] for n in adjusted['nodes'] if n['row']==r),default=0) for r in range(len(adjusted['rows']))]
            natural_height=290+sum(row_heights)+52*(len(row_heights)-1)
            adjusted['height']=original.get('height',max(720 if compact else 1200,natural_height))
            # Measure the records first. Uniformly stretching a sparse graph over
            # a wall-poster canvas creates long empty connectors and tiny labels.
            spare=max(0,adjusted['height']-natural_height)
            cursor=190
            for row,h in enumerate(row_heights):
                for n in adjusted['nodes']:
                    if n['row']==row:
                        n['x']=65+(adjusted['width']-130)*(n['col']+.5)/adjusted['columns']
                        n['y']=cursor+h/2
                cursor+=h+52+spare/max(1,len(row_heights)-1)
            adjusted['layout']='resolved'
        elif adjusted.get('layout')=='cohorts' and compact:
            adjusted=compact_cohort_defaults(adjusted,lambda n,w:measured_content(n,w,font))
            if adjusted.get('legend',True):
                adjusted['_cohort_key']=cohort_key(adjusted,adjusted['width'])
                extra=max(0,adjusted['_cohort_key']['height']-25)
                if 'cohort_top' not in original:adjusted['cohort_top']+=extra
                if 'cohort_bottom' not in original:adjusted['cohort_bottom']+=extra
                if 'height' not in original:adjusted['height']+=extra
        elif compact_time:
            require(adjusted.get('lanes') and adjusted.get('periods'),'Compact timelines require named lanes and periods.')
            lane_count=len(adjusted['lanes'])
            adjusted.setdefault('width',max(1000,175+lane_count*275))
            lane_boxes=lane_geometry(adjusted['lanes'],adjusted['width'])
            span=adjusted['time']['end']-adjusted['time']['start']
            require(span>0,'Invalid time scale.')
            scale_needed=0
            for period in adjusted['periods']:
                require(period['lane'] in lane_boxes,'Timeline periods require known lanes.')
                require(period.get('treatment','ribbon')=='ribbon','Compact timelines already use separate horizontal labels; omit stem treatment.')
                pitch=lane_boxes[period['lane']][1]
                period.setdefault('size',font)
                period.setdefault('bar_width',22)
                period.setdefault('offset',12)
                period.setdefault('label_width',pitch-period['offset']-period['bar_width']-30)
                label_height=12+len(wrap(period['label'],period['label_width'],period['size'],True))*period['size']*1.18+period['size']*.82
                duration=period['end']-period['start']
                require(duration>0,'Compact timeline periods require positive duration.')
                scale_needed=max(scale_needed,(label_height+30)/duration)
            adjusted.setdefault('height',max(760,302+span*scale_needed))
        else:
            adjusted.setdefault('width',1800);adjusted.setdefault('height',2700)
        adjusted.setdefault('frame_color','#902F29');adjusted.setdefault('paper_color','#EDEAD8')
        adjusted['font_size']=16
        super().__init__(adjusted)
        if original.get('layout')=='auto':self.data['layout']='auto'
        self.source_data=original
        self.font=number(font,'font_size')
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
        if kind.startswith('illustration-'):
            art_id=kind.removeprefix('illustration-')
            folder=Path(__file__).resolve().parent.parent/'assets/illustrations'
            records=json.loads((folder/'provenance.json').read_text(encoding='utf-8'))['items']
            item=next((r for r in records if r['id']==art_id),None)
            require(item is not None,'Unknown source illustration ID.')
            filename=item['file']
            require(Path(filename).name==filename and Path(filename).suffix in ('.svg','.png'),'Invalid bundled illustration filename.')
            if kind not in self.image_sources:
                self.add('<metadata data-artwork-source="'+filename+'">'+html.escape(json.dumps(item))+'</metadata>')
                encoded=base64.b64encode((folder/filename).read_bytes()).decode('ascii')
                iw,ih=item['width'],item['height']
                self.add(f'<defs><symbol id="asset-{kind}" viewBox="0 0 {iw} {ih}"><image href="data:{item["mime_type"]};base64,{encoded}" width="{iw}" height="{ih}" preserveAspectRatio="xMidYMid meet"/></symbol></defs>')
                self.image_sources.add(kind)
            self.add(f'<svg data-artwork="source-illustration" data-illustration-id="{art_id}" x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" viewBox="0 0 {fmt(w)} {fmt(h)}"><use href="#asset-{kind}" width="{fmt(w)}" height="{fmt(h)}"/></svg>')
            return
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
        require(kind in ('heraldry','shield','crown','star','sun','compass','globe','astrolabe','orbit','book','archive','wheel','gear','lens','prism','ship','anchor','tower','observatory','press','machine','obelisk','monument','leaf','branch','portrait','bust'),'Unknown original artwork type.')
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
        for item in self.data.get('_cohort_key',{}).get('cells',[]):
            x,y,w,h=item['box'];paint=self.groups[item['group']]['color']
            self.rect((x,y,w,h),'#FFFEF7',paint,2,12)
            for i,line in enumerate(wrap(item['label'],w-22,13,True)):
                self.text(x+w/2,y+17+i*15,line,13,bold=True,background='#FFFEF7')

    def footer(self):
        lines=wrap(self.data['source_note']+' '+self.data.get('reading_note',self.default_note()),self.w-155,10)
        require(len(lines)<=2,'Keep editorial source and reading notes to two compact lines.')
        for i,line in enumerate(lines):self.text(self.w/2,self.h-63+i*13,line,10)

    def node_content(self,node,width):
        return measured_content(node,width,self.font)

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
        context_boxes={}
        for i,annotation in enumerate(self.data.get('annotations',[])):
            if annotation.get('kind')!='landmark':continue
            require(annotation.get('node') in self.boxes,'A landmark requires a known person or institution anchor.')
            anchor=self.boxes[annotation['node']];content=landmark_content(annotation,self.nodes[annotation['node']])
            x=anchor[0]+anchor[2]/2+annotation.get('dx',0);y=anchor[1]+anchor[3]/2+annotation.get('dy',0)
            context_boxes[f'context-{i}']=(x-content['width']/2,y-content['height']/2,content['width'],content['height'])
            require(not any(overlaps(context_boxes[f'context-{i}'],box,4) for box in self.boxes.values()),
                'A landmark covers a person or institution. Move it into a nearby open pocket.')
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
            source_port=edge.get('source_port','bottom');target_port=edge.get('target_port','top')
            require((source_port,target_port)==('bottom','top') or
                (self.mode=='lineage' and kind=='influence' and source in self.nodes),
                'Lateral or reversed attachments require an institutional influence between nodes.')
            end,b=attachment_port(self.boxes[target],target_port)
            if source in self.unions:
                start=self.unions[source]['point'];source_y=start[1]
                a=(start[0],start[1]+10)
            else:
                start,a=attachment_port(self.boxes[source],source_port);source_y=self.nodes[source]['row']
            require(kind=='influence' or source_y<self.nodes[target]['row'],f'Relation {eid} goes backward.')
            reserved=[(p,q) for prior in self.routes if not {source,target}&{prior['source'],prior['target']}
                      for p,q in zip(prior['points'],prior['points'][1:])] if self.mode=='lineage' else []
            if edge.get('via'):
                path=compress([start]+[tuple(map(float,p)) for p in edge['via']]+[end])
                require(all(p[0]==q[0] or p[1]==q[1] for p,q in zip(path,path[1:])),f'Non-orthogonal authored corridor for {eid}')
            else:
                default_middle=(a[1]+b[1])/2
                if self.data.get('layout')=='cohorts':
                    prior=row_bands.get(round(source_y,3));following=row_bands.get(round(self.nodes[target]['row'],3))
                    if prior and following and following[0]>prior[1]:default_middle=(prior[1]+following[0])/2
                middle=edge.get('corridor_y',default_middle)
                trial=compress([start,(start[0],middle),(end[0],middle),end]) if (source_port,target_port)==('bottom','top') else \
                    compress([start,a,(a[0],b[1]),b,end])
                # Ports touch their own boxes; every other part must stay outside,
                # including a corridor that was requested beyond the target top.
                if not any(segment_hits(p,q,box,0) for p,q in zip(trial,trial[1:]) for box in self.boxes.values()) and not any(
                    collinear_overlap(p,q,r,s)>.05 for p,q in zip(trial,trial[1:]) for r,s in reserved):
                    path=trial
                else:
                    # An occupied search endpoint cannot be repaired by a larger
                    # search window. Explain the actual neighbouring obstruction.
                    for port,point in (('source',a),('target',b)):
                        blocked=[nid for nid,(x,y,w,h) in self.boxes.items() if x-7<point[0]<x+w+7 and y-7<point[1]<y+h+7]
                        require(not blocked,f'Relationship {eid} has a crowded {port} port near {", ".join(blocked)}. Reserve at least 18 units at the attachment.')
                    world=(self.left-12,self.top-26,self.right+12,self.bottom+12)
                    regions=[]
                    for margin in (30,90,220,600,max(self.w,self.h)):
                        bounds=(max(world[0],min(a[0],b[0])-margin),max(world[1],min(a[1],b[1])-margin),min(world[2],max(a[0],b[0])+margin),min(world[3],max(a[1],b[1])+margin))
                        regions.append(bounds)
                    try:path=compress([start]+route_regions(a,b,list(self.boxes.values()),regions,segments,reserved=reserved)+[end])
                    except ValueError as error:raise ValueError(f'Cannot route relationship {eid}: {error}') from error
            if any(segment_hits(p,q,box,4) for p,q in zip(path,path[1:]) for box in context_boxes.values()):
                obstacles=self.boxes|context_boxes
                for port,point in (('source',a),('target',b)):
                    blocked=[nid for nid,(x,y,w,h) in obstacles.items() if x-7<point[0]<x+w+7 and y-7<point[1]<y+h+7]
                    require(not blocked,f'Relationship {eid} has a crowded {port} port near {", ".join(blocked)}. Reserve at least 18 units at the attachment.')
                world=(self.left-12,self.top-26,self.right+12,self.bottom+12);regions=[]
                for margin in (30,90,220,600,max(self.w,self.h)):
                    bounds=(max(world[0],min(a[0],b[0])-margin),max(world[1],min(a[1],b[1])-margin),min(world[2],max(a[0],b[0])+margin),min(world[3],max(a[1],b[1])+margin))
                    regions.append(bounds)
                try:path=compress([start]+route_regions(a,b,list(obstacles.values()),regions,segments,reserved=reserved)+[end])
                except ValueError as error:raise ValueError(f'Cannot route relationship {eid} around its context: {error}') from error
            require(not any(segment_hits(p,q,box,0) for p,q in zip(path,path[1:]) for box in self.boxes.values()),f'Relationship {eid} crosses a node, including its own source or target.')
            group=edge.get('group',self.nodes[target]['group']);paint=self.groups[group]['color']
            width=edge.get('weight',2.8 if kind in ('branch','descent') else 1.8)
            dash={'influence':'1 5','uncertain':'1 4','adopted':'7 3 1 3','succession':'8 3 1 3'}.get(kind,'')
            self.line(path,self.paper,width+2.4)
            ports=''.join(f' data-{key.replace("_","-")}="{edge[key]}"' for key in ('source_port','target_port') if key in edge)
            self.line(path,paint,width,dash,extra=f'data-edge-id="{eid}" data-source="{source}" data-target="{target}" data-kind="{kind}" data-route-style="rounded"{ports}')
            if kind=='influence':
                x,y=end
                if target_port=='top':
                    self.add(f'<path d="M {fmt(x-3)} {fmt(y-6)} L {fmt(x)} {fmt(y)} L {fmt(x+3)} {fmt(y-6)}" fill="none" stroke="{paint}" stroke-width="1.5"/>')
                else:
                    dx,dy={'left':(1,0),'right':(-1,0),'bottom':(0,-1)}[target_port]
                    self.add(f'<path d="M {fmt(x-6*dx-3*dy)} {fmt(y-6*dy+3*dx)} L {fmt(x)} {fmt(y)} L {fmt(x-6*dx+3*dy)} {fmt(y-6*dy-3*dx)}" fill="none" stroke="{paint}" stroke-width="1.5"/>')
            self.routes.append(dict(edge,points=path));segments.extend(zip(path,path[1:]))

    def draw_nodes(self):
        if self.mode=='timeline':return self.draw_intervals()
        for nid,n in self.nodes.items():
            x,y,w,h=self.boxes[nid];paint=self.groups[n['group']]['color'];style=n.get('style','card')
            require(style in ('plain','card','pill','emblem','hero'),'Unknown editorial node treatment.')
            fill=self.paper if style=='plain' else '#FFFEF7' if style=='pill' else paint
            ink=text_color(fill)
            self.add(f'<g id="node-{nid}" data-node-id="{nid}" data-group="{n["group"]}" data-treatment="{style}">')
            if n.get('detail_position')=='outside':
                self.draw_separated_node(nid,n,(x,y,w,h),fill,paint)
                self.add('</g>');continue
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

    def draw_separated_node(self,nid,node,box,fill,paint):
        x,y,w,h=box;parts=separated_content(node,w,self.font)
        size=node.get('size',self.font);small=node.get('detail_size',size*.77)
        iconw=node.get('icon_width',30) if node.get('icon') else 0
        self.rect(box,self.paper,extra='data-node-box="true" data-content-envelope="true"')
        for i,line in enumerate(parts['dates']):
            self.text(x+w/2,y+small+3+i*small*1.25,line,small,owner=nid,css='data-content-role="date"')
        py=y+parts['date_height'];ph=parts['panel_height']
        self.rect((x,py,w,ph),fill,paint if node.get('style')=='pill' else 'none',2.5,12 if node.get('style')=='pill' else 1,extra='data-name-panel="true"')
        if iconw:
            self.rect((x+2,py+2,iconw,ph-4),'#FFFEF7')
            self.artwork(node['icon'],x+2,py+(ph-iconw)/2,iconw,iconw,paint,node.get('variant',0))
        xx=x+iconw+(w-iconw)/2
        yy=py+(ph-len(parts['names'])*size*1.18)/2+size*.92
        for line in parts['names']:
            self.text(xx,yy,line,size,text_color(fill),bold=True,owner=nid,background=fill,css='data-content-role="name"');yy+=size*1.18
        yy=py+ph+small+2
        for line in parts['details']:
            self.text(x+w/2,yy,line,small,owner=nid,css='data-content-role="caption"');yy+=small*1.25

    def draw_annotations(self):
        for annotation_index,a in enumerate(self.data.get('annotations',[])):
            if a.get('kind')=='landmark':require(a.get('node') in self.nodes,'A landmark requires a known person or institution anchor.')
            if a.get('node'):
                require(a['node'] in self.boxes,'Annotation references an unknown node.')
                anchor=self.boxes[a['node']]
                x,y=anchor[0]+anchor[2]/2+a.get('dx',0),anchor[1]+anchor[3]/2+a.get('dy',0)
            else:x,y=a['x'],a['y']
            if a.get('kind')=='landmark':
                require(a.get('node') in self.nodes,'A landmark requires a known person or institution anchor.')
                node=self.nodes[a['node']];content=landmark_content(a,node)
                group=a.get('group',node['group'])
                require(group==node['group'],'A landmark must retain the category of its named source node.')
                paint=self.groups[group]['color'];w=content['width'];h=content['height']
                box=(x-w/2,y-h/2,w,h)
                require(box[0]>=48 and box[0]+w<=self.w-48 and box[1]>=130 and box[1]+h<=self.h-85,
                    'A landmark must remain inside the printable field.')
                require(not any(overlaps(box,b,4) for b in self.boxes.values()),'A landmark covers a person or institution. Move it into a nearby open pocket.')
                require(not any(overlaps(box,b,4) for b in self.annotation_boxes),'Landmarks and family captions require separate space.')
                require(not any(segment_hits(p,q,box,3) for edge in self.routes for p,q in zip(edge['points'],edge['points'][1:])),
                    'A landmark covers a relationship corridor. Move it without changing the source data.')
                for union in self.unions.values():
                    first,last=[self.boxes[n] for n in union['partners']]
                    middle=first[1]+first[3]/2
                    for offset in (-3,3):
                        require(not segment_hits((first[0]+first[2],middle+offset),(last[0],middle+offset),box,3),'A landmark covers a partnership bar.')
                self.annotation_boxes.append(box)
                self.add(f'<g data-annotation-id="annotation-{annotation_index}" data-annotation-kind="landmark" data-context-node="{attr(a["node"])}" data-context-group="{attr(group)}" data-source-field="{attr(content["field"])}" data-source-value="{attr(content["label"])}">')
                self.rect(box,'none',extra='data-annotation-box="true"')
                top=box[1]+4
                tx=x;art_x=x-content['art']/2;art_y=top
                if content['art_position']=='beside':
                    art_x=x-(content['art']+4+content['ink_width'])/2;art_y=box[1]+(h-content['art'])/2
                    tx=art_x+content['art']+4+content['ink_width']/2 if content['art'] else x
                    top=box[1]+(h-content['text_height'])/2
                if content['art']:
                    self.artwork(a['icon'],art_x,art_y,content['art'],content['art'],paint,a.get('variant',0))
                yy=top+content['art_height']
                for line in content['eyebrows']:
                    self.text(tx,yy+content['eyebrow_size'],line,content['eyebrow_size'],bold=True);yy+=content['eyebrow_size']*1.2
                if content['eyebrows']:yy+=3
                for line in content['lines']:
                    self.text(tx,yy+content['size'],line,content['size'],css='font-family="Georgia, serif" font-style="italic" data-content-role="landmark-label"');yy+=content['size']*1.2
                self.add('</g>');continue
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
            self.add(f'<g data-annotation-id="annotation-{annotation_index}" data-annotation-kind="{attr(a.get("kind","note"))}">')
            if a.get('kind')=='pill':self.rect((x-w/2,y-h/2,w,h),'#FFFEF7',paint,2.5,12)
            if a.get('kind')=='heading':
                if a.get('icon'):self.artwork(a['icon'],x-22,y-h/2-57,44,49,paint,a.get('variant',0))
            yy=y-h/2+size
            for line in lines:
                css='font-family="Georgia, serif" font-style="italic"' if a.get('kind')=='heading' else ''
                self.text(x,yy,line,size,bold=a.get('kind')!='heading',css=css,background='#FFFEF7' if a.get('kind')=='pill' else self.paper);yy+=size*1.12
            self.add('</g>')

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
                mapping=item.get('countries',{})
                require(all(g in self.groups for g in mapping.values()),'Map assignments reference an unknown group.')
                legend_height=0
                if item.get('legend'):
                    selected=[g for g in self.groups.values() if g['id'] in set(mapping.values())]
                    columns=min(3,len(selected))
                    for i,g in enumerate(selected):
                        xx=x+(i%columns)*w/columns
                        yy=y+42+(i//columns)*22
                        self.rect((xx,yy-9,10,10),g['color'])
                        self.text(xx+16,yy,g['label'],10,anchor='start')
                    legend_height=math.ceil(len(selected)/max(1,columns))*22
                require(h>90+legend_height,'Map inset is too short for its key and outline.')
                self.map_art(x,y+40+legend_height,w,h-65-legend_height,mapping)
                self.text(x+w/2,y+h-4,item.get('note','Illustrative geography'),10,self.muted)
            elif item['kind']=='isotype':
                groups=list(self.groups.values())
                totals={gid:sum(n['group']==gid for n in self.data['nodes']) for gid in self.groups}
                if 'groups' in item:
                    require(len(set(item['groups']))==len(item['groups']) and all(g in self.groups for g in item['groups']),'Isotype selection must contain unique known groups.')
                    selected=[self.groups[g] for g in item['groups']]
                else:selected=[g for g in groups if totals[g['id']]>12]
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
        lanes=lane_geometry(d['lanes'],self.w)
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
        for l in d['lanes']:
            x,pitch=lanes[l['id']]
            for j,line in enumerate(wrap(l['label'].upper(),pitch-14,13,True)):self.text(x+pitch/2,self.top-24+j*14,line,13,bold=True)
        for i in range(math.floor((end-start)/step)+1):
            yy=scale(start+i*step)
            self.line([(self.left-26,yy),(self.right+9,yy)],'#FFFEF6',2)
            self.text(self.left-31,yy+4,self.year_label(start+i*step),10.5,anchor='end',bold=True)
        for era in d.get('eras',[]):
            yy=scale(era['start']);hh=scale(era['end'])-yy
            spans=[(self.left-24,self.right+9)]
            for event in d.get('events',[]):
                lane_x,pitch=lanes[event['lane']]
                ex=lane_x+event.get('offset',64)
                ew=event.get('width',pitch-78);content=event_content(event,ew)
                if scale(event['year'])+content['top']-2<=yy<=scale(event['year'])+content['bottom']+2:
                    spans=[part for a,b in spans for part in [(a,min(b,ex-4)),(max(a,ex+ew+4),b)] if part[1]>part[0]]
            for a,b in spans:self.line([(a,yy),(b,yy)],'#8F8874',2,extra=f'data-era-rule="{era["start"]}"')
            cx,cy=53,yy+hh/2
            self.text(cx,cy,era['label'].upper(),14,bold=True,css=f'transform="rotate(-90 {cx} {cy})" letter-spacing="2"')
        for period in d['periods']:
            n=copy.deepcopy(period);nid=ident(n['id'])
            require(nid not in self.nodes and n['lane'] in lanes and n['group'] in self.groups,f'Invalid period {nid}')
            a,b=number(n['start'],f'{nid}.start'),number(n['end'],f'{nid}.end')
            require(start<=a<b<=end,f'Invalid period dates {nid}')
            width=number(n.get('bar_width',32),'bar_width')
            require(width>0,'A timeline interval needs positive width.')
            n['_duration_width']=duration_width(n,width)
            x=lanes[n['lane']][0]+n.get('offset',18)
            height=scale(b)-scale(a)
            size=n.get('size',13)
            if d.get('layout')=='compact':
                names=wrap(n['label'],n['label_width'],size,True)
                label_height=len(names)*size*1.18+size*.82+10
                require(label_height<=height-12,f'Period {nid} needs more vertical space for its horizontal label; increase page height.')
                n['_horizontal_lines']=names
                n['_label_box']=(x+width+12,scale(a)+(height-label_height)/2,n['label_width'],label_height)
            else:
                names=wrap(n['label'],height-14,size,True)
                require(len(names)*size*1.1<=width-4,f'Period {nid} label needs a wider ribbon or shorter wording.')
                n['_vertical_lines']=names
                if n.get('treatment')=='stem':
                    n['_label_box']=period_parts(n,(x,scale(a),width,height))[1]
            self.make_node(n,(x,scale(a),width,height))
        for nid,a in self.boxes.items():
            for oid,b in self.boxes.items():
                if nid<oid:require(not any(overlaps(pa,pb) for pa in period_parts(self.nodes[nid],a) for pb in period_parts(self.nodes[oid],b)),f'Periods {nid} and {oid} overlap.')
        transition_ids=set()
        for edge in d.get('transitions',[]):
            ident(edge['id'])
            require(edge['id'] not in transition_ids,'Duplicate timeline transition ID.')
            transition_ids.add(edge['id'])
            require(edge['source'] in self.nodes and edge['target'] in self.nodes and edge['kind'] in ('succession','division','union','uncertain'),'Timeline transitions require known periods and an explicit succession, division, union, or uncertain relation.')
            a,b=self.boxes[edge['source']],self.boxes[edge['target']]
            start_point,end_point,spans=transition_geometry(edge,self.nodes[edge['source']],self.nodes[edge['target']],a,b)
            mid=(start_point[1]+end_point[1])/2
            points=compress([start_point,(start_point[0],mid),(end_point[0],mid),end_point])
            paint=self.groups[self.nodes[edge['target']]['group']]['color']
            require(edge.get('style','dotted') in ('dotted','ribbon'),'Unknown timeline transition style.')
            if edge.get('style')=='ribbon':
                (left_a,right_a),(left_b,right_b)=spans
                self.add(f'<path data-transition-fill="{edge["id"]}" d="M {fmt(left_a)} {fmt(start_point[1])} L {fmt(right_a)} {fmt(start_point[1])} L {fmt(right_b)} {fmt(end_point[1])} L {fmt(left_b)} {fmt(end_point[1])} Z" fill="{paint}"/>')
                # The semantic path follows the center of the filled bridge.
                # Drawing an orthogonal elbow as well creates a false second fork.
                points=[start_point,end_point]
            self.line(points,paint,2,'1 4' if edge.get('style','dotted')=='dotted' else '',extra=f'data-edge-id="{edge["id"]}" data-source="{edge["source"]}" data-target="{edge["target"]}" data-kind="{edge["kind"]}" data-route-style="rounded"')
            self.routes.append(dict(edge,points=points))
        # Event annotations are supplied data. Their dates use the same numeric scale.
        for index,event in enumerate(d.get('events',[])):
            require(event['lane'] in lanes and start<=event['year']<=end,'Invalid event lane or date.')
            lane_x,pitch=lanes[event['lane']]
            x=lane_x+event.get('offset',64)
            yy=scale(event['year']);width=event.get('width',pitch-78)
            content=event_content(event,width);anchor_y=yy
            event_id=ident(event.get('id',f'event-{index}'))
            self.add(f'<g data-event-id="{event_id}" data-year="{event["year"]}" data-origin-y="{fmt(yy)}">')
            for line in content['lines']:
                if line.get('runs'):
                    self.expected_text.append(line['text'])
                    spans=''.join(f'<tspan data-event-run-role="{run["role"]}" font-size="{fmt(run["font"])}" font-weight="{700 if run["bold"] else 400}">{html.escape(run["text"])}</tspan>' for run in line['runs'])
                    self.add(f'<text x="{fmt(x+line["x"])}" y="{fmt(yy+line["font"])}" font-size="{fmt(line["font"])}" fill="{self.ink}" text-anchor="start" font-weight="400" data-owner="page" data-background="{self.paper}" data-event-text-role="paragraph" xml:space="preserve">{spans}</text>')
                else:
                    self.text(x+line['x'],yy+line['font'],line['text'],line['font'],anchor='start',bold=line['bold'],css=f'data-event-text-role="{line["role"]}"')
                yy+=line['font']*1.18
            if content['art']:
                ax,ay,aw,ah=content['art'];art_box=(x+ax,anchor_y+ay,aw,ah)
                blocked=[nid for nid,box in self.boxes.items() if any(overlaps(art_box,part,0) for part in period_parts(self.nodes[nid],box))]
                require(not blocked,f'Event {event_id} artwork overlaps period {", ".join(blocked)}. Reserve its full height or recompose the event.')
                self.artwork(event['icon'],*art_box,self.groups[event.get('group',d['groups'][0]['id'])]['color'],event.get('variant',0))
            self.add('</g>')
        self.draw_annotations()

    def draw_intervals(self):
        for nid,n in self.nodes.items():
            x,y,w,h=self.boxes[nid];paint=self.groups[n['group']]['color'];ink=text_color(paint)
            self.add(f'<g id="node-{nid}" data-node-id="{nid}" data-group="{n["group"]}">')
            if n.get('treatment')=='stem':
                self.rect((x,y,w,h),'none',extra='data-node-box="true"')
                sw=n['_duration_width']
                self.rect((x+(w-sw)/2,y,sw,h),paint,extra='data-period-stem="true"')
                self.rect(n['_label_box'],paint,self.paper,1,4,extra='data-label-box="true" data-period-label="true"')
            else:self.rect((x,y,w,h),paint,self.paper,1,5,extra='data-node-box="true"')
            if '_horizontal_lines' in n:
                lx,ly,lw,lh=n['_label_box'];size=n['size']
                self.rect((lx,ly,lw,lh),self.paper,extra='data-label-box="true"')
                for i,line in enumerate(n['_horizontal_lines']):
                    self.text(lx+3,ly+size+i*size*1.18,line,size,bold=True,anchor='start',owner=nid)
                dates=self.year_label(n['start'])+'\u2013'+self.year_label(n['end'])
                self.text(lx+3,ly+lh-7,dates,size*.77,anchor='start',owner=nid)
                self.add('</g>')
                continue
            size=n.get('size',13);lines=n['_vertical_lines'];cx=x+w/2;cy=y+h/2
            if n.get('treatment')=='stem':
                label=n['_label_box'];cy=label[1]+label[3]/2
            for i,line in enumerate(lines):
                self.text(cx,cy+(i-(len(lines)-1)/2)*size*1.1+size*.3,line,size,ink,bold=True,owner=nid,background=paint,
                    css=f'transform="rotate(-90 {fmt(cx)} {fmt(cy)})"')
            self.add('</g>')


if __name__=='__main__':
    print('Use render_chart.py with design: editorial to render an authored poster.')
