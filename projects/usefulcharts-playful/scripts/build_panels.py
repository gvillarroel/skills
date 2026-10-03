#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.55,<2", "pillow>=11"]
# ///
"""Compose illustrated specimen neighborhoods around unchanged selected records."""
from pathlib import Path
import base64
import copy
import html
import json
import sys
import xml.etree.ElementTree as ET
from PIL import Image

ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
sys.path.insert(0,str(REPO/'skills/usefulcharts-style/scripts'))
from create_panel_poster import compose,render
from render_chart import wrap,viewer
from audit_panel_poster import audit

NS='http://www.w3.org/2000/svg';ET.register_namespace('',NS)
def tag(name):return '{'+NS+'}'+name
def text(parent,x,y,value,size=16,fill='#192F39',weight='400',extra=None):
    attrs=dict(x=str(x),y=str(y),fill=fill,**{'font-size':str(size),'font-weight':weight,'data-background':'#F7F2E8'})
    attrs.update(extra or {});el=ET.SubElement(parent,tag('text'),attrs);el.text=str(value);return el

INSTRUMENTS={
 '1':[(0,'Handbell','111','Strike the body'),(1,'Kalimba','122','Pluck a metal tongue'),(2,'Cymbals','111','Bodies strike together')],
 '2':[(3,'Snare drum','211','A stretched skin'),(4,'Conga','211','A different drum body'),(5,'Kazoo','242','A singing membrane')],
 '3':[(6,'Violin','321','Strings on a lute'),(7,'Harp','322','A frame of strings'),(8,'Zither','314','Strings across a board')],
 '4':[(9,'Flute','421','Air meets an edge'),(10,'Clarinet','422','A reed starts vibration'),(11,'Trumpet','423','The player’s lips vibrate')],
 '5':[(12,'Analog synthesizer','53','Electronic oscillations'),(13,'Tonewheel organ','521','A rotating mechanism'),(14,'Audio software','56','A software instrument')],
}
BSD={
 'research':(0,'AT THE TERMINAL','v3','Trace the pipes','Find UNIX V3: pipes connect programs. V4 then marks the rewrite in C.'),
 'berkeley':(1,'THE MINICOMPUTER ERA','b3','Follow the changing hardware','The first BSD tools target PDP-11 UNIX; 3BSD brings virtual memory on the VAX.'),
 '386bsd':(2,'THE PERSONAL COMPUTER','386a','A branch on the desktop','Follow the numbered links between NET/2, 386BSD and the first FreeBSD release.'),
 'freebsd':(3,'SOFTWARE THAT TRAVELS','f1','Find the inherited code','Look for 4.4BSD Lite in the notes and trace its contributions across families.'),
 'netbsd':(4,'A CONNECTED FAMILY','n08','Read both arrow directions','Named paired arrows distinguish lineage from a contribution of code.'),
 'bsdi':(5,'THE WORKSTATION ERA','osalpha','Compare the cousins','BSDI is a commercial branch; the other panels retain their separate identities.'),
}

# Object bounds were measured from the inspected generated sheet. Its spacing is
# intentionally organic, so mathematically equal cells are not safe crops.
INSTRUMENT_BOUNDS=[(0,0,323,315),(332,0,300,318),(643,0,328,315),
 (0,330,320,275),(345,320,290,290),(641,360,330,230),
 (0,620,320,320),(342,620,285,320),(635,675,330,240),
 (0,966,310,279),(349,940,275,307),(633,970,335,267),
 (0,1260,327,302),(332,1260,300,310),(638,1260,333,305)]

def place_cell(parent,asset,cell,columns,rows,x,y,w,h,identifier,anchor,group,caption):
    iw,ih=Image.open(asset).size;cw,ch=iw/columns,ih/rows
    row,col=divmod(cell,columns)
    sx,sy=col*cw,row*ch
    if asset.stem=='instruments-sheet':sx,sy,cw,ch=INSTRUMENT_BOUNDS[cell]
    # Match viewport and cell aspect ratios: a meet letterbox otherwise reveals neighbors.
    placed_width=min(w,h*cw/ch);x+=(w-placed_width)/2;w=placed_width;h=w*ch/cw
    viewport=ET.SubElement(parent,tag('svg'),dict(x=str(x),y=str(y),width=str(w),height=str(h),viewBox=f'{sx} {sy} {cw} {ch}',
       overflow='hidden',preserveAspectRatio='xMidYMid meet',**{'data-art-id':identifier,'data-art-anchor':anchor,'data-art-group':group,'data-art-role':'subject','aria-label':caption}))
    ET.SubElement(viewport,tag('image'),dict(width=str(iw),height=str(ih),href='data:image/png;base64,'+base64.b64encode(asset.read_bytes()).decode()))
    return dict(placement_id=identifier,asset_id=asset.stem+'-'+str(cell),path=str(asset.relative_to(ROOT)),anchors=[anchor],groups=[group],box=dict(x=x,y=y,w=w,h=h),explanation=caption)

def build(case):
    source=json.loads((REPO/'projects/usefulcharts-cross-domain/artifacts/revision-2'/case/'source.json').read_text(encoding='utf-8'))
    data,layout=compose(source,2,520)
    gap_art=228;original_width=layout['width'];layout['width']+=gap_art*2
    for panel in layout['panels']:
        dx=panel['column']*gap_art;panel['x']+=dx;panel['w']+=gap_art
        for record in panel['records']:record['x']+=dx
    if layout['reading_pocket']:
        pocket=layout['reading_pocket'];pocket['x']+=gap_art*(1 if pocket['x']>100 else 0);pocket['w']+=gap_art
    root=ET.fromstring(render(data,layout));new=[]
    # Distinct subject color tabs and open specimen areas replace a plain list field.
    panels={p['id']:p for p in layout['panels']};groups={g['id']:g for g in data['groups']}
    for panel_group in root.findall('.//'+tag('g')):
        if 'data-panel-id' not in panel_group.attrib:continue
        pid=panel_group.get('data-panel-id');p=panels[pid];color=groups[pid]['color']
        frame=panel_group.find(tag('rect'));frame.set('rx','20');frame.set('stroke','#CFCBBE')
        # Keep a visible separation between the complete text field and specimen rail.
        x=p['x']+520;y=p['y'];w=gap_art-22
        ET.SubElement(panel_group,tag('path'),dict(d=f'M{x-10} {y+72}V{y+p["h"]-22}',stroke=color,**{'stroke-opacity':'.18','stroke-width':'1.4'}))
        if case=='instruments':
            examples=INSTRUMENTS[pid];step=(p['h']-92)/3;art_size=min(180,step-58)
            for j,(cell,name,anchor,meaning) in enumerate(examples):
                yy=y+65+j*step
                new.append(place_cell(panel_group,ROOT/'artifacts/images/instruments-sheet.png',cell,3,5,x,yy,w,art_size,'instrument-'+str(cell),anchor,pid,name+' — '+meaning))
                link=ET.SubElement(panel_group,tag('a'),dict(href='#record-'+anchor))
                text(link,x+8,yy+art_size+15,name,17,color,'700')
                text(link,x+8,yy+art_size+36,'Example → '+anchor,14,color)
                text(link,x+8,yy+art_size+55,meaning,14,'#4E6268')
            # Keep a mechanism visible at page scale without repeating the full prose.
            invitation={'1':'STRIKE OR PLUCK?','2':'WHY IS A KAZOO HERE?','3':'WHICH STRING FRAME?','4':'WHAT STARTS THE AIR?','5':'WHERE IS THE SIGNAL?'}[pid]
            text(panel_group,x+8,y+43,invitation,14,color,'700',{'letter-spacing':'.6'})
        else:
            cell,caption,anchor,question,explanation=BSD[pid]
            known={n['id'] for n in data['nodes']}
            assert anchor in known,anchor
            art_height=min(205,p['h']-188)
            new.append(place_cell(panel_group,ROOT/'artifacts/images/bsd-sheet.png',cell,3,2,x,y+75,w,art_height,'bsd-'+pid,anchor,pid,'Period-inspired archetype: '+caption.lower()))
            yy=y+75+art_height+28
            for line in wrap(caption,w-15,18,True):text(panel_group,x+6,yy,line,18,color,'700');yy+=23
            questions=wrap(question,w-15,16,True);explanations=wrap(explanation,w-15,15)
            if yy+26+len(questions)*21+len(explanations)*20<y+p['h']-40:
                yy+=21
                for line in questions:text(panel_group,x+6,yy,line,16,color,'700');yy+=21
                for line in explanations:text(panel_group,x+6,yy+8,line,15);yy+=20
            text(panel_group,x+6,y+p['h']-17,'Illustrative period hardware',14,'#4E6268')
            if pid=='berkeley':
                by=y+int(p['h']*.59)
                text(panel_group,x+6,by,'ONE SOURCE, THREE PATHS',14,color,'700')
                text(panel_group,x+6,by+31,'4.4BSD Lite',19,color,'700')
                for j,(label,target,kind) in enumerate([('FreeBSD 2.0','f2','lineage'),('NetBSD 1.0','n1','contribution'),('BSD/OS 2.0','os2','contribution')]):
                    ty=by+95+j*85
                    ET.SubElement(panel_group,tag('path'),dict(d=f'M{x+17} {by+42}V{ty-7}H{x+38}',fill='none',stroke=color,**{'stroke-width':'1.5'}))
                    link=ET.SubElement(panel_group,tag('a'),dict(href='#record-'+target))
                    text(link,x+42,ty,label,17,color,'700');text(link,x+42,ty+22,kind,14,color)
    # Preserve the source title while giving the reader an actual invitation.
    header=[e for e in root.findall(tag('text')) if float(e.get('y','0'))==157]
    if header:header[0].text=('Find the family by what vibrates. Follow the codes to compare 71 sound-making categories.' if case=='instruments' else 'From shared tools to branching systems. Follow 47 releases and 51 named relationships.')
    for el in root.findall(tag('text')):
        if el.get('letter-spacing')=='3':el.text='AN ILLUSTRATED FIELD GUIDE TO '+('SOUND' if case=='instruments' else 'SOFTWARE HISTORY')
    width,height=layout['width'],layout['height']
    definitions=ET.SubElement(root,tag('defs'));cache={}
    for parent in list(root.iter()):
        if parent is definitions:continue
        for child in list(parent):
            if child.tag!=tag('image'):continue
            href=child.get('href')
            if href not in cache:
                identifier='image-sheet-'+str(len(cache));cache[href]=identifier
                definition=copy.deepcopy(child);definition.set('id',identifier);definitions.append(definition)
            index=list(parent).index(child);parent.remove(child)
            parent.insert(index,ET.Element(tag('use'),dict(href='#'+cache[href])))
    for a in new:a['region']=['upper','middle','lower'][min(2,int(3*(a['box']['y']-230)/max(1,height-310)))];a['recognized_at_placed_size']=False
    output=ROOT/'artifacts/revision-2'/case;output.mkdir(parents=True,exist_ok=True)
    svg=ET.tostring(root,encoding='unicode')
    (output/'poster.svg').write_text(svg,encoding='utf-8');(output/'source.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (output/'layout.json').write_text(json.dumps(layout,indent=2)+'\n');(output/'art-map.json').write_text(json.dumps(new,indent=2)+'\n')
    (output/'poster.html').write_text(viewer(svg,data['title']),encoding='utf-8')
    report=audit(output/'poster.svg',output/'source.json',output/'poster.png',output/'poster.pdf')
    (output/'browser.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(case=case,size=[width,height],illustrations=len(new),technical=report['status'],findings=report['findings'][:8])))

if __name__=='__main__':
    for case in ('instruments','bsd'):build(case)
