#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2"]
# ///
"""Measured project composition primitives for the third illustrated revision."""
from pathlib import Path
import base64
import copy
import json
import math
import sys
import xml.etree.ElementTree as ET
from PIL import ImageFont
from artwork import ROOT, REPO, tag, art, save

PAPER='#F7F2E8'; INK='#20343B'; DARK='#081829'; MUTED='#60727B'
FONT=REPO/'skills/usefulcharts-style/assets/fonts/BarlowCondensed-Bold.ttf'
ARIAL=Path('C:/Windows/Fonts/arial.ttf'); BOLD=Path('C:/Windows/Fonts/arialbd.ttf')


def font(size,weight='400',display=False):
    return ImageFont.truetype(str(FONT if display else BOLD if str(weight)=='700' else ARIAL),size=round(size*4))


def wrap(value,width,size=18,weight='400',display=False):
    f=font(size,weight,display); lines=[]; current=''
    for word in str(value).split():
        trial=(current+' '+word).strip()
        if current and f.getlength(trial)/4>width*.975:
            lines.append(current);current=word
        else:current=trial
    if current:lines.append(current)
    return lines


def line(root,points,color=INK,width=2,identifier=None,dash=None,**extra):
    a=dict(d='M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in points),fill='none',stroke=color,**{'stroke-width':str(width),'stroke-linejoin':'round','stroke-linecap':'round'})
    if identifier:a['id']=identifier
    if dash:a['stroke-dasharray']=dash
    a.update(extra);return ET.SubElement(root,tag('path'),a)


class Poster:
    def __init__(self,case,width,title,subtitle,dark=False):
        self.case=case;self.width=width;self.dark=dark;self.bg=DARK if dark else PAPER;self.ink='#EDF4F4' if dark else INK;self.muted='#B4C8D1' if dark else MUTED
        self.root=ET.Element(tag('svg'),dict(width=str(width),height='2000',viewBox=f'0 0 {width} 2000',role='img'))
        ET.SubElement(self.root,tag('title')).text=title
        defs=ET.SubElement(self.root,tag('defs'));ET.SubElement(defs,tag('style')).text='@font-face{font-family:Barlow;src:url(data:font/ttf;base64,'+base64.b64encode(FONT.read_bytes()).decode()+');font-weight:700}text{font-family:Arial,sans-serif}g[data-record-id]{cursor:pointer}'
        self.background=ET.SubElement(self.root,tag('rect'),dict(width=str(width),height='2000',fill=self.bg))
        self.edges=ET.SubElement(self.root,tag('g'),dict(id='relationships'))
        self.body=ET.SubElement(self.root,tag('g'),dict(id='records'))
        self.arts=[];self.boxes=[];self.routes=[];self.marks=[];self.units=[]
        self.text(self.root,40,72,title,58,'700',display=True)
        self.paragraph(self.root,42,111,subtitle,width-84,18,color=self.muted)

    def text(self,parent,x,y,value,size=18,weight='400',color=None,display=False,**attrs):
        a=dict(x=str(x),y=str(y),fill=color or self.ink,**{'font-size':str(size),'font-weight':str(weight),'data-background':self.bg})
        if display:a['style']='font-family:Barlow'
        a.update(attrs);e=ET.SubElement(parent,tag('text'),a);e.text=str(value);return e

    def paragraph(self,parent,x,y,value,width,size=18,weight='400',color=None,display=False,field=None):
        for row in wrap(value,width,size,weight,display):
            self.text(parent,x,y,row,size,weight,color,display,**({'data-field':field} if field else {}));y+=size*1.27
        return y

    def image(self,spec,box,identifier,anchors,groups,caption):
        a=art(self.root,spec['path'],box,identifier,anchors,groups,caption,spec.get('crop'))
        element=self.root[-1];element.set('id',identifier)
        element.set('style','mix-blend-mode:screen' if self.dark else 'isolation:isolate')
        if spec.get('clip'):
            defs=self.root.find(tag('defs'));clip=ET.SubElement(defs,tag('clipPath'),dict(id=identifier+'-clip',clipPathUnits='userSpaceOnUse'))
            ET.SubElement(clip,tag('path'),dict(d=spec['clip']));element.find(tag('use')).set('clip-path','url(#'+identifier+'-clip)')
        self.arts.append(a);return a

    def finish(self,height,source,detail):
        height=math.ceil(height);self.root.set('height',str(height));self.root.set('viewBox',f'0 0 {self.width} {height}');self.background.set('height',str(height))
        out=ROOT/'artifacts/revision-3'/self.case
        save(self.root,out,self.arts,source)
        (out/'layout.json').write_text(json.dumps(dict(width=self.width,height=height,boxes=self.boxes,routes=self.routes,marks=self.marks,units=self.units,detail=detail),indent=2)+'\n',encoding='utf-8')
        print(json.dumps(dict(case=self.case,records=len(self.boxes),images=len(self.arts),canvas=[self.width,height])))
        return out


def intersects(a,b,gap=0):
    return a['x']<b['x']+b['w']+gap and a['x']+a['w']+gap>b['x'] and a['y']<b['y']+b['h']+gap and a['y']+a['h']+gap>b['y']


def pack(records,width,top=245,gap=19):
    placed=[];output=[];family_rows={}
    for r in records:
        options=[]
        variants=[r['start']+12,r['end']-r['w']-12,r['start']-r['w']-12,r['start']-r['w']/2,r['end']+12]
        if r.get('roam'):
            variants.extend(r['start']+offset*r['w'] for offset in [-4,-3,-2,1,2,3,4])
        for tx in sorted(set(max(35,min(width-r['w']-35,v)) for v in variants)):
            parts=[dict(x=tx,y=25,w=r['w'],h=r['h']),dict(x=r['start']-7,y=-7,w=max(14,r['end']-r['start']+14),h=27)]
            if r.get('span_height'):parts.append(dict(x=r['start']-8,y=r['h']+35,w=max(r['w']+16,r['end']-r['start']+16),h=r['span_height']))
            port=max(tx+12,min(tx+r['w']-12,r['start']))
            parts.append(dict(x=min(r['start'],port)-3,y=0,w=max(6,abs(port-r['start'])+6),h=28))
            preferred=family_rows.get(r['group'],[])
            ys={top,*preferred}
            for part in parts:
                for prior in placed:
                    if part['x']<prior['x']+prior['w']+gap and part['x']+part['w']+gap>prior['x']:
                        ys.add(math.ceil((prior['y']+prior['h']+gap-part['y'])/5)*5)
            for y in sorted(ys):
                actual=[dict(p,y=p['y']+y,owner=r['id']) for p in parts]
                if all(not intersects(p,b,gap) for p in actual for b in placed):
                    options.append((y+r['h']+(0 if y in preferred else 25),abs(tx-r['start']),y,tx,actual));break
        if not options:raise ValueError('No packing position '+r['id'])
        _,_,y,tx,actual=min(options,key=lambda a:a[:2]);placed.extend(actual);family_rows.setdefault(r['group'],[]).append(y)
        output.append(dict(r,y=y,tx=tx,occupied=actual))
    return output,placed


def pack_best(records,width,top=245,gap=19):
    orders=[records,sorted(records,key=lambda r:(r['group'],r.get('year') or 0,r['id'])),sorted(records,key=lambda r:(-r['h'],r['start'])),sorted(records,key=lambda r:(-(r['end']-r['start']),-r['h']))]
    options=[pack(order,width,top,gap) for order in orders]
    return min(options,key=lambda pair:max(b['y']+b['h'] for b in pair[1]))


def relation_route(a,b,obstacles,width,top=180):
    sys.path.insert(0,str(REPO/'projects/star-trek-starships/scripts'))
    import build_flow_atlas as flow
    flow.W=width;flow.TOP=top;flow.M=30
    return flow.route_relation(a,b,obstacles)


def timeline_unit(p,r,color,source,art_spec=None):
    n=r['node'];y=r['y'];tx=r['tx'];g=ET.SubElement(p.body,tag('g'),dict(id='record-'+n['id'],**{'data-record-id':n['id']}))
    if r['end']>r['start']:
        line(g,[(r['start'],y),(r['end'],y)],color,2,'duration-'+n['id'],'4 6')
    ET.SubElement(g,tag('circle'),dict(cx=str(r['start']),cy=str(y),r='5',fill=color))
    port=max(tx+12,min(tx+r['w']-12,r['start']))
    line(g,[(r['start'],y),(r['start'],y+14),(port,y+14),(port,y+25)],color,1.6,'owner-'+n['id'])
    yy=y+45
    if n.get('date_label'):
        yy=p.paragraph(g,tx+4,yy,n['date_label'],r['w']-8,r.get('small',16),'700',color,field='date_label')
    yy=p.paragraph(g,tx+4,yy+14,n['label'],r['w']-8,r.get('title_size',24),'700',color,True,field='label')
    yy=p.paragraph(g,tx+4,yy+4,n.get('detail',''),r['w']-8,r.get('body_size',18),field='detail')
    if n.get('credit'):
        yy=p.paragraph(g,tx+4,yy+3,n['credit'],r['w']-8,r.get('small',16),color=p.muted,field='credit')
    if art_spec:
        # The picture is in the same measured group footprint as its date and facts.
        yy+=5;ih=art_spec.get('height',130)
        a=p.image(art_spec,(tx+8,yy,r['w']-16,ih),'art-'+n['id'],[n['id']],[r['group']],art_spec.get('caption',n['label']))
        yy+=ih+18
        if art_spec.get('caption'):yy=p.paragraph(g,tx+5,yy,art_spec['caption'],r['w']-10,r.get('small',16),color=p.muted)
    p.boxes.append(dict(id=n['id'],x=tx,y=y+25,w=r['w'],h=r['h']))
    p.units.append(dict(id=n['id'],x=tx,y=y+25,w=r['w'],h=r['h'],group=r['group'],year=r.get('year')))
    return g,yy


def unit_height(n,width,body=18,title=24,small=16,spec=None):
    h=39
    for value,size,weight,display in [(n.get('date_label',''),small,'700',False),(n['label'],title,'700',True),(n.get('detail',''),body,'400',False),(n.get('credit',''),small,'400',False)]:
        h+=len(wrap(value,width-8,size,weight,display))*size*1.27+5
    if spec:h+=spec.get('height',130)+23+len(wrap(spec.get('caption',''),width-10,small))*small*1.27
    return math.ceil(h)
