#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2"]
# ///
"""Render an explicitly sectioned graph as compact linked outline panels."""
from pathlib import Path
import argparse
import base64
import copy
import html
import json
import math
import re
import itertools

from playwright.sync_api import sync_playwright
from render_chart import wrap, text_width, contrast, viewer, color

PAPER = '#f7f7f7'
INK = '#363636'
MUTED = '#696969'

def require(condition, message):
    if not condition:
        raise ValueError(message)

def forest_order(nodes, edges):
    """Retain source sibling order; never infer relationships from group membership."""
    by = {n['id']: n for n in nodes}
    children = {i: [] for i in by}
    parents = {i: [] for i in by}
    for e in edges:
        parents[e['target']].append(e['source'])
        children[e['source']].append(e['target'])
    require(all(len(p) <= 1 for p in parents.values()),
            'A local outline requires at most one incoming structural edge per record; use explicit cross references for additional links.')
    order=[];levels={};active=set();seen=set()
    def visit(i, depth):
        require(i not in active, 'Local structural relations must be acyclic.')
        if i in seen:return
        active.add(i);seen.add(i);order.append(i);levels[i]=depth
        for c in children[i]:visit(c, depth+(1 if len(children[i]) > 1 else 0))
        active.remove(i)
    for n in nodes:
        if not parents[n['id']]:visit(n['id'],0)
    require(len(order)==len(nodes), 'Local structural relations must be acyclic.')
    return order, levels

def assign_columns(heights, columns):
    """Balance panel heights while retaining source order inside each column."""
    if columns**len(heights)<=100000:
        best=None
        for assignment in itertools.product(range(columns),repeat=max(0,len(heights)-1)):
            assignment=(0,)+assignment
            loads=[sum(h+24 for h,c in zip(heights,assignment) if c==i) for i in range(columns)]
            score=(max(loads),sum((max(loads)-x)**2 for x in loads),assignment)
            if best is None or score<best[0]:best=(score,assignment)
        return list(best[1])
    loads=[0]*columns;assignment=[0]*len(heights)
    for i in sorted(range(len(heights)),key=lambda i:(-heights[i],i)):
        column=min(range(columns),key=lambda c:(loads[c],c));assignment[i]=column;loads[column]+=heights[i]+24
    return assignment

def compose(source, columns=2, panel_width=520):
    data=copy.deepcopy(source)
    require(data.get('position_semantics'), 'State position_semantics: outline panels have no numeric time axis.')
    require(not data.get('unions') and not data.get('events') and not data.get('insets') and not data.get('annotations'),
            'This focused route does not render unions, events, insets or annotations. Use the corresponding graph or calendar route.')
    require(isinstance(columns,int) and 1 <= columns <= 4, 'Use one to four panel columns.')
    require(isinstance(panel_width,(int,float)) and math.isfinite(panel_width) and 420 <= panel_width <= 1000,
            'Panel width must be 420–1000 units; the measured hierarchy must also fit.')
    nodes=data.get('nodes',[]);groups=data.get('groups',[]);edges=data.get('edges',[])
    by={n['id']:n for n in nodes};group_by={g['id']:g for g in groups}
    require(nodes and len(by)==len(nodes) and groups and len(group_by)==len(groups), 'Record and group IDs must be unique and nonempty.')
    require(all(isinstance(i,str) and i for i in list(by)+list(group_by)), 'IDs must be nonempty strings.')
    require(all(n.get('label') and n.get('group') in group_by for n in nodes), 'Every record needs a label and a known group.')
    require(all(any(n['group']==g['id'] for n in nodes) for g in groups), 'Groups must not be empty.')
    require(all(re.fullmatch(r'#[0-9A-Fa-f]{6}',g.get('color','')) for g in groups), 'Group colors must use six-digit hex values.')
    for group in groups:
        color(group['color'])
    require(all(contrast(g['color'],PAPER)>=4.5 for g in groups), 'Group colors need 4.5:1 contrast on the paper.')
    require(len({e['id'] for e in edges})==len(edges), 'Relationship IDs must be unique.')
    local=[];portals=[]
    for e in edges:
        require(e.get('source') in by and e.get('target') in by and e['source']!=e['target'], 'Relationship endpoints must resolve to different records.')
        require(e.get('kind') in ('branch','succession','influence','uncertain','contains'), 'Unsupported relationship kind.')
        if by[e['source']]['group']==by[e['target']]['group'] and e['kind'] in ('branch','contains') and not e.get('portal'):
            local.append(e)
        else:portals.append(e)
    port_by={i:[] for i in by}
    names={'branch':'lineage','succession':'successor','influence':'contribution','uncertain':'uncertain link','contains':'contains'}
    for index,e in enumerate(portals,1):
        for role,owner,other,arrow in [('out',e['source'],e['target'],'→'),('in',e['target'],e['source'],'←')]:
            port_by[owner].append(dict(edge=e['id'],role=role,other=other,number=index,
                text=f'{index:02d} {arrow} {by[other]["label"]} · {names[e["kind"]]}'))
    panels=[];node_layout={};header_bottom=230
    for group in groups:
        selected=[n for n in nodes if n['group']==group['id']]
        local_edges=[e for e in local if by[e['source']]['group']==group['id']]
        order,levels=forest_order(selected,local_edges)
        group_lines=wrap(group['label'],panel_width-64,31,True)
        root_is_heading=bool(order) and by[order[0]]['label']==group['label']
        if root_is_heading:group_lines=[]
        yy=34+len(group_lines)*36+20
        records=[]
        kickers=[str(n.get('date_label',n.get('code',''))) for n in selected]
        rail=max((text_width(k,15,True) for k in kickers),default=0)+14
        inline=rail<=120
        for i in order:
            n=by[i];indent=levels[i]*19
            usable=panel_width-110-indent
            require(usable>=240, 'This hierarchy is too deep for an outline panel; split at an explicit source boundary.')
            lines=[]
            kicker=str(n.get('date_label',n.get('code','')))
            name_x=rail if inline and any(kickers) else 0
            if kicker and not inline:
                for line in wrap(kicker,usable,15,True):lines.append((line,15,'kicker',0))
            label_size=25 if root_is_heading and i==order[0] else 21
            for line in wrap(n['label'],usable-name_x,label_size,True):lines.append((line,label_size,'label',name_x))
            if n.get('detail'):
                for line in wrap(n['detail'],usable-name_x,16):lines.append((line,16,'detail',name_x))
            entries=[];offset=0
            if kicker and inline:entries.append(dict(text=kicker,size=15,role='kicker',dx=0,dy=label_size))
            for line,size,role,dx in lines:
                entries.append(dict(text=line,size=size,role=role,dx=dx,dy=offset+size))
                offset+=size*1.24
            links=[]
            if port_by[i]:offset+=5
            for p in port_by[i]:
                for j,line in enumerate(wrap(p['text'],usable,14)):
                    links.append({**p,'text':line,'line':j,'dy':offset+14})
                    offset+=18
            height=offset+12
            records.append(dict(id=i,x=62+indent,y=yy,w=usable,h=height,level=levels[i],entries=entries,links=links))
            yy+=height
        panels.append(dict(id=group['id'],w=panel_width,h=yy+18,records=records,headings=group_lines))
    ends=[header_bottom]*columns
    assignments=assign_columns([p['h'] for p in panels],columns)
    for panel,column in zip(panels,assignments):
        panel.update(x=42+column*(panel_width+24),y=ends[column],column=column)
        ends[column]+=panel['h']+24
        for r in panel['records']:
            r['x']+=panel['x'];r['y']+=panel['y'];node_layout[r['id']]=r
    width=84+columns*panel_width+(columns-1)*24
    footer_lines=[]
    notes=[data['position_semantics'],data.get('reading_note',''),data.get('source_note','')]
    pocket=None
    pocket_lines=wrap(' '.join(notes[:2]),panel_width-52,16)
    pocket_height=90+len(pocket_lines)*21
    short=min(range(columns),key=lambda c:ends[c])
    if max(ends)-ends[short]>=pocket_height+12:
        pocket=dict(x=42+short*(panel_width+24),y=ends[short],w=panel_width,h=pocket_height,lines=pocket_lines)
        notes=notes[2:]
    for note in notes:
        footer_lines.extend(wrap(note,width-90,15))
    height=max(ends)+30+len(footer_lines)*20+24
    return data,dict(width=width,height=height,panels=panels,nodes=node_layout,local=local,portals=portals,footer_lines=footer_lines,reading_pocket=pocket)

def render(data,layout):
    esc=lambda x:html.escape(str(x),quote=True)
    width,height=layout['width'],layout['height'];groups={g['id']:g for g in data['groups']}
    by={n['id']:n for n in data['nodes']};pieces=[]
    font=base64.b64encode((Path(__file__).resolve().parents[1]/'assets/fonts/BarlowCondensed-Bold.ttf').read_bytes()).decode()
    pieces.append(f'<svg xmlns="http://www.w3.org/2000/svg" data-colorset="colorset2" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">')
    pieces.append(f'<title id="title">{esc(data["title"])}</title><desc id="desc">{esc(data["position_semantics"])}</desc>')
    pieces.append(f'<style>@font-face{{font-family:Poster;src:url(data:font/ttf;base64,{font})}}text{{font-family:Arial,sans-serif}}.display{{font-family:Poster,Arial,sans-serif;font-weight:700}}a:hover text{{text-decoration:underline}}a:hover circle{{stroke-width:4}}</style>')
    pieces.append(f'<rect width="{width}" height="{height}" fill="{PAPER}"/>')
    pieces.append('<rect width="100%" height="188" fill="#363636"/>')
    def txt(x,y,value,size=16,fill=INK,bg=PAPER,extra=''):
        pieces.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{fill}" data-background="{bg}" {extra}>{esc(value)}</text>')
    txt(42,43,data.get('eyebrow','A CONNECTED FIELD GUIDE'),15,'#cfcfcf','#363636','letter-spacing="3"')
    title_size=min(64,(width-84)/max(1,text_width(data['title'],1,True)))
    require(title_size>=28,'Shorten the poster title; it cannot be rendered legibly.')
    txt(42,118,data['title'],title_size,'#FFFFFF','#363636','class="display"')
    facts=f'{len(by)} records   /   {len(data["edges"])} relationships   /   {len(groups)} families'
    txt(44,157,facts,17,'#e7e7e7','#363636')
    for panel in layout['panels']:
        group=groups[panel['id']];x,y=panel['x'],panel['y'];color=group['color']
        pieces.append(f'<g data-panel-id="{esc(panel["id"])}"><rect data-panel-box="true" x="{x}" y="{y}" width="{panel["w"]}" height="{panel["h"]}" rx="7" fill="#f7f7f7" stroke="none"/>')
        pieces.append(f'<path d="M {x+18} {y+18} H {x+panel["w"]-18}" stroke="{color}" stroke-width="5"/>')
        for j,line in enumerate(panel['headings']):txt(x+26,y+52+j*36,line,31,color,PAPER,'class="display"')
        for r in panel['records']:
            n=by[r['id']];rx,ry=r['x'],r['y']
            pieces.append(f'<g id="record-{esc(r["id"])}" data-record-id="{esc(r["id"])}"><rect data-record-box="true" x="{rx-10}" y="{ry-2}" width="{r["w"]+15}" height="{r["h"]-9}" fill="none"/>')
            for line in r['entries']:
                fill=color if line['role']=='kicker' else INK if line['role']=='label' else MUTED
                txt(rx+line['dx'],ry+line['dy'],line['text'],line['size'],fill,PAPER,
                    f'data-role="{line["role"]}"'+(' font-weight="700"' if line['role'] in ('label','kicker') else ''))
            for line in r['links']:
                pieces.append(f'<a href="#record-{esc(line["other"])}" data-portal-id="{esc(line["edge"])}" data-portal-role="{line["role"]}" data-line="{line["line"]}">')
                txt(rx,ry+line['dy'],line['text'],14,color);pieces.append('</a>')
            pieces.append('</g>')
        pieces.append('</g>')
    for edge in layout['local']:
        a=layout['nodes'][edge['source']];b=layout['nodes'][edge['target']]
        ax,ay=a['x']-24,a['y']+12;bx,byy=b['x']-24,b['y']+12
        color=groups[by[edge['source']]['group']]['color']
        pieces.append(f'<path data-link-id="{esc(edge["id"])}" data-source="{esc(edge["source"])}" data-target="{esc(edge["target"])}" data-kind="{esc(edge["kind"])}" d="M {ax} {ay} V {byy} H {bx}" fill="none" stroke="{color}" stroke-width="1.6"/>')
    for i,r in layout['nodes'].items():
        color=groups[by[i]['group']]['color']
        pieces.append(f'<circle cx="{r["x"]-24}" cy="{r["y"]+12}" r="3.6" fill="{color}" stroke="none"/>')
    if layout['reading_pocket']:
        pocket=layout['reading_pocket'];x,y=pocket['x'],pocket['y']
        pieces.append(f'<rect data-reading-pocket="true" x="{x}" y="{y}" width="{pocket["w"]}" height="{pocket["h"]}" rx="7" fill="{PAPER}" stroke="none"/>')
        txt(x+26,y+41,'READING THE CONNECTIONS',26,INK,PAPER,'class="display"')
        for j,line in enumerate(pocket['lines']):txt(x+26,y+77+j*21,line,16)
    yy=height-24-len(layout['footer_lines'])*20
    for line in layout['footer_lines']:txt(44,yy,line,15);yy+=20
    pieces.append(f'<metadata id="poster-source">{esc(json.dumps(data,ensure_ascii=False))}</metadata></svg>')
    return '\n'.join(pieces)

def build(source,directory,columns=2,panel_width=520):
    data,layout=compose(source,columns,panel_width);svg=render(data,layout)
    directory.mkdir(parents=True,exist_ok=True)
    (directory/'poster.svg').write_text(svg,encoding='utf-8')
    (directory/'source.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (directory/'layout.json').write_text(json.dumps(layout,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (directory/'poster.html').write_text(viewer(svg,data['title']),encoding='utf-8')
    from audit_panel_poster import audit
    report=audit(directory/'poster.svg',directory/'source.json',directory/'poster.png',directory/'poster.pdf')
    (directory/'browser.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    require(report['status']=='pass','The poster failed its browser audit; inspect browser.json and the retained preview.')
    return dict(status='pass',records=len(data['nodes']),relationships=len(data['edges']),canvas=[layout['width'],layout['height']],
        files=['poster.svg','poster.html','poster.png','poster.pdf','source.json','layout.json','browser.json'],
        visual_review='Inspect the full poster and its busiest panels; geometry does not establish editorial quality or reference parity.')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path)
    p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--columns',type=int,default=2);p.add_argument('--panel-width',type=float,default=520)
    args=p.parse_args()
    try:
        print(json.dumps(build(json.loads(args.input.read_text(encoding='utf-8-sig')),args.output_dir,args.columns,args.panel_width)))
    except (ValueError,KeyError,TypeError,OSError) as error:p.exit(2,f'Panel poster could not be completed: {error}\n')

if __name__=='__main__':main()
