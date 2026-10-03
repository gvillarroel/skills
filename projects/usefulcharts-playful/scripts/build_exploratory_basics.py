#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2"]
# ///
"""Replace image rails with illustrated leaves and source-bound calendar records."""
import json
import re
import sys
import xml.etree.ElementTree as ET
from exploratory_core import Poster,ROOT,REPO,PAPER,INK,tag,line,wrap,pack_best,timeline_unit,unit_height,relation_route,intersects
from build_panels import INSTRUMENTS,INSTRUMENT_BOUNDS


def instruments():
    source=json.loads((REPO/'projects/usefulcharts-cross-domain/data/instruments.json').read_text(encoding='utf-8'))
    p=Poster('instruments',2200,'HOW INSTRUMENTS MAKE SOUND','Follow the branching mechanisms. Each pictured specimen sits at the category it exemplifies; the codes express classification, not rank.')
    p.text(p.root,1100,145,'WHAT VIBRATES?',18,'700',p.muted,**{'text-anchor':'middle'})
    nodes={n['id']:n for n in source['nodes']};children={i:[] for i in nodes}
    for e in source['edges']:children[e['source']].append(e['target'])
    y_end=[];positions={};sheet=ROOT/'artifacts/images/instruments-sheet.png'
    for column,group in enumerate(source['groups']):
        gid=group['id'];x=45+column*435;w=405;color=group['color'];node=nodes[gid]
        wash=ET.SubElement(p.edges,tag('rect'),dict(x=str(x-8),y='187',width=str(w+16),height='1000',fill=color,opacity='.045',rx='7'))
        root_group=ET.SubElement(p.body,tag('g'),dict(id='record-'+gid,**{'data-record-id':gid}))
        line(p.edges,[(1100,148),(1100,169),(x+180,169),(x+180,191)],color,2.5,'root-family-'+gid)
        p.text(root_group,x,217,gid,21,'700',color,**{'data-field':'date_label'})
        p.text(root_group,x+34,217,node['label'],32,'700',color,True,**{'data-field':'label'})
        p.text(root_group,x+34,247,node['detail'],18,color=p.muted,**{'data-field':'detail'})
        positions[gid]=(x+15,301);p.boxes.append(dict(id=gid,x=x,y=190,w=w,h=70));p.units.append(dict(id=gid,x=x,y=190,w=w,h=70,group=gid))
        images={}
        for cell,name,anchor,caption in INSTRUMENTS[gid]:images.setdefault(anchor,[]).append((cell,name,caption))
        questions={'1':'WHAT COUNTS AS A VIBRATING BODY?','2':'WHY IS A KAZOO HERE?','3':'WHICH STRING FRAME?','4':'WHAT STARTS THE AIR VIBRATING?','5':'HOW DOES THE SIGNAL BEGIN?'}
        p.text(root_group,x+6,282,questions[gid],17,'700',color,True)
        y=318

        def visit(ident,depth):
            nonlocal y
            n=nodes[ident];nx=x+depth*23;yy=y;g=ET.SubElement(p.body,tag('g'),dict(id='record-'+ident,**{'data-record-id':ident}));positions[ident]=(nx-9,yy-7)
            p.text(g,nx,yy,n['date_label'],16,'700',color,**{'data-field':'date_label'})
            yy=p.paragraph(g,nx+42,yy,n['label'],w-depth*23-46,20,'700' if children[ident] else '400',field='label')
            if n.get('detail'):yy=p.paragraph(g,nx+42,yy,n['detail'],w-depth*23-46,17,color=p.muted,field='detail')
            specimens=images.get(ident,[])
            if specimens:
                yy+=5
                cell_w=(w-depth*23-15)/len(specimens)
                for index,(cell,name,caption) in enumerate(specimens):
                    ax=nx+index*cell_w
                    spec=dict(path=sheet,crop=INSTRUMENT_BOUNDS[cell])
                    p.image(spec,(ax+8,yy,cell_w-20,98),'art-'+ident+'-'+str(cell),[ident],[gid],name+' — '+caption)
                    image=p.arts[-1]['box'];cx=image['x']+image['w']/2
                    line(p.edges,[(nx-9,positions[ident][1]),(nx-9,yy-7),(cx,yy-7),(cx,image['y']-2)],color,1.6,'specimen-owner-'+ident+'-'+str(cell))
                    p.text(g,ax+8,yy+117,name+' · '+ident,17,'700',color)
                    p.paragraph(g,ax+8,yy+139,caption,cell_w-15,15,color=p.muted)
                yy+=160
            h=yy-y+15;p.boxes.append(dict(id=ident,x=nx,y=y-21,w=w-depth*23,h=h+21));p.units.append(dict(id=ident,x=nx,y=y-21,w=w-depth*23,h=h+21,group=gid))
            y=yy+10
            for child in children[ident]:visit(child,depth+1)
        for child in children[gid]:visit(child,1)
        y_end.append(y);wash.set('height',str(y-180))
    for edge in source['edges']:
        sx,sy=positions[edge['source']];tx,ty=positions[edge['target']]
        color=next(g['color'] for g in source['groups'] if g['id']==nodes[edge['source']]['group'])
        line(p.edges,[(sx,sy),(sx,ty),(tx,ty)],color,1.8,'edge-'+edge['id'],**{'data-source':edge['source'],'data-target':edge['target'],'data-kind':edge['kind']})
    bottom=max(y_end)+20
    line(p.root,[(45,bottom),(2150,bottom)],'#A9ADA2',1)
    p.paragraph(p.root,45,bottom+30,'Read the physical cause: body → idiophones; membrane → membranophones; strings → chordophones; air → aerophones; electronic signal → electrophones. A kazoo belongs with membranes even though the player blows into it.',2100,18)
    p.paragraph(p.root,45,bottom+91,source.get('source_note','Source: MIMO Consortium, revised Hornbostel–Sachs classification (2011). Selected categories; deeper subdivisions omitted.'),2100,15,color=p.muted)
    return p.finish(bottom+135,source,(880,285,850,820))


def bsd_calendar_draft():
    source=json.loads((REPO/'projects/usefulcharts-cross-domain/data/bsd.json').read_text(encoding='utf-8'));W=2300
    p=Poster('bsd',W,'UNIX & BSD · FOLLOW THE INHERITANCE','Solid arrows show lineage; dashed arrows show code contributions. Images identify illustrative computing contexts at specific release records.')
    colors={g['id']:g['color'] for g in source['groups']};groups={g['id']:i for i,g in enumerate(source['groups'])}
    sheet=ROOT/'artifacts/images/bsd-sheet.png'
    specs={ident:dict(path=sheet,crop=((i%3)*512,(i//3)*512,512,512),height=126,caption=caption) for i,ident,caption in [(0,'v3','Pipes connect programs.'),(1,'b3','Virtual memory on the VAX.'),(2,'386a','An early PC release.'),(3,'f1','A new FreeBSD branch.'),(4,'n08','The NetBSD branch begins.'),(5,'osalpha','A commercial BSD branch.') ]}
    def px(t):return 80+(t-1971)*42 if t<=1989 else 836+(t-1989)*218
    records=[]
    for n in source['nodes']:
        years=[int(v) for v in re.findall(r'(?:19|20)\d\d',n['date_label'])]
        if not years:years=[1982]
        first,last=min(years),max(years);spec=specs.get(n['id']);w=255
        records.append(dict(id=n['id'],node=n,year=first if n['date_label']!='Undated' else None,start=px(first),end=px(last),group=n['group'],w=w,h=unit_height(n,w,body=17,title=25,small=16,spec=spec),body_size=17,title_size=25,small=16))
    # Earliest events enter first; short paths can reuse rows after a source stops.
    records.sort(key=lambda r:(r['year'] or 1982,groups[r['group']],r['id']))
    selected,occupied=pack_best(records,W,top=280,gap=22);boxes={r['id']:r for r in selected}
    bottom=max(b['y']+b['h'] for b in occupied)
    for year in [1971,1975,1980,1985,1989,1990,1991,1992,1993,1994,1995]:
        x=px(year);p.text(p.root,x,227,year,17,'700',p.muted,**{'text-anchor':'middle'});line(p.edges,[(x,245),(x,bottom+10)],'#CAD0C5',1)
    p.text(p.root,75,184,'CALENDAR X · 1971–1989 compressed; 1989–1995 expanded',17,'700',p.muted)
    for i,g in enumerate(source['groups']):p.text(p.root,75+i*365,155,g['label'],20,'700',g['color'])
    for e in source['edges']:
        a,b=boxes[e['source']],boxes[e['target']]
        ax=a['tx']+a['w'] if b['tx']>=a['tx'] else a['tx'];bx=b['tx'] if b['tx']>=a['tx'] else b['tx']+b['w']
        start=(ax+(3 if bx>=ax else -3),a['y']+53);end=(bx+(-3 if bx>=ax else 3),b['y']+53)
        obstacles=[o for o in occupied if o['owner'] not in (a['id'],b['id'])]
        points=relation_route(start,end,obstacles,W,245)
        col=colors[a['group']];line(p.edges,points,PAPER,8);line(p.edges,points,col,2.6,'edge-'+e['id'],'6 5' if e['kind']=='influence' else None,**{'data-source':e['source'],'data-target':e['target'],'data-kind':e['kind']})
        x,y=end;direction=-1 if bx<ax else 1
        line(p.edges,[(x-direction*8,y-5),(x,y),(x-direction*8,y+5)],col,2.2)
        p.routes.append(dict(**e,points=points))
    for r in selected:
        g,_=timeline_unit(p,r,colors[r['group']],source,specs.get(r['id']))
        if r['year'] is None:
            for circle in list(g.findall(tag('circle'))):g.remove(circle)
            p.text(g,r['tx']+5,r['y']+r['h']+12,'Sequence placement only · no date point',13,color=p.muted)
        else:
            circle=g.find(tag('circle'));circle.set('data-year',str(r['year']));circle.set('data-date-owner',r['id']);p.marks.append(dict(owner=r['id'],year=r['year'],x=r['start']))
    bottom+=65
    p.paragraph(p.root,45,bottom,'4.4BSD Lite supplies the FreeBSD 2.0 lineage and contributes code to NetBSD 1.0 and BSD/OS 2.0. Trace the solid and dashed paths directly. 4.1bBSD has no stated date; its position follows the source sequence without a calendar dot.',W-90,18)
    p.paragraph(p.root,45,bottom+77,'Source: FreeBSD UNIX system family tree. All 47 selected releases and 51 typed relationships are retained. Year ranges keep the source wording. Hardware is illustrative period context, not an exact historical specimen.',W-90,15,color=p.muted)
    return p.finish(bottom+135,source,(900,250,1300,950))


def bsd():
    source=json.loads((REPO/'projects/usefulcharts-cross-domain/data/bsd.json').read_text(encoding='utf-8'));W=2100
    p=Poster('bsd',W,'UNIX & BSD · ONE HISTORY, MANY BRANCHES','Follow the continuous arrows from Research UNIX through Berkeley to the later BSD families. Dates stay with each release; spacing expresses inheritance, not elapsed time.')
    colors={g['id']:g['color'] for g in source['groups']};sheet=ROOT/'artifacts/images/bsd-sheet.png'
    specs={ident:dict(path=sheet,crop=((i%3)*512,(i//3)*512,512,512),height=108) for i,ident in enumerate(['v3','b3','386a','f1','n08','osalpha'])}
    specs['b3']['height']=88
    image_captions={'v3':'UNIX V3 · period terminal','b3':'3BSD · VAX-era hardware','386a':'386BSD 0.0 · PC context','f1':'FreeBSD 1.0 · distribution media','n08':'NetBSD 0.8 · networked systems','osalpha':'BSD/386 Alpha · workstation context'}
    groups={g['id']:[n for n in source['nodes'] if n['group']==g['id']] for g in source['groups']};records={};end=0

    def draw_node(n,x,y,w):
        nonlocal end
        color=colors[n['group']];g=ET.SubElement(p.body,tag('g'),dict(id='record-'+n['id'],**{'data-record-id':n['id']}))
        head=max(len(wrap(n['label'],w-86,25,'700',True))*31.75,len(wrap(n['date_label'],74,15,'700'))*19.05)
        h=head+len(wrap(n['detail'],w-16,17))*21.59+24
        if n['id'] in specs:h+=specs[n['id']]['height']+16
        ET.SubElement(g,tag('rect'),dict(x=str(x),y=str(y),width=str(w),height=str(head+13),fill=color,opacity='.17',rx='4'))
        p.paragraph(g,x+8,y+27,n['label'],w-86,25,'700',color,True,field='label')
        p.paragraph(g,x+w-78,y+25,n['date_label'],74,15,'700',color,field='date_label')
        yy=p.paragraph(g,x+8,y+head+34,n['detail'],w-16,17,field='detail')
        if n['id'] in specs:
            iw=100 if w<260 else 136
            p.image(specs[n['id']],(x+10,yy+5,iw,specs[n['id']]['height']),'art-'+n['id'],[n['id']],[n['group']],'Illustrative period hardware associated with '+n['label'])
            line(g,[(x+w/2,yy-6),(x+10+iw/2,yy-6),(x+10+iw/2,yy+3)],color,1.7,'specimen-owner-'+n['id'])
            p.paragraph(g,x+iw+18,yy+26,image_captions[n['id']],w-iw-24,14,'700',color)
            p.text(g,x+iw+18,yy+87,'Illustrative',13,color=p.muted)
        box=dict(id=n['id'],x=x,y=y,w=w,h=h,group=n['group']);records[n['id']]=box;p.boxes.append(box);p.units.append(box);end=max(end,y+h)
        return h

    p.text(p.root,50,193,'RESEARCH UNIX',27,'700',colors['research'],True)
    for i,n in enumerate(groups['research']):draw_node(n,50+i*254,219,224)
    p.text(p.root,50,477,'BERKELEY / CSRG',28,'700',colors['berkeley'],True)
    for i,n in enumerate(groups['berkeley']):
        row,col=divmod(i,9)
        # The second row reverses direction, making the main line continuous.
        if row%2:col=8-col
        draw_node(n,50+col*224,502+row*215,198)
    p.text(p.root,50,695,'LATER BERKELEY RELEASES ←',20,'700',colors['berkeley'],True)
    layouts=[('386bsd',50,420),('freebsd',550,465),('netbsd',1090,420),('bsdi',1590,450)]
    for gid,x,w in layouts:
        color=colors[gid];p.text(p.root,x,907,next(g['label'] for g in source['groups'] if g['id']==gid),31,'700',color,True)
        y=932
        for n in groups[gid]:y+=draw_node(n,x,y,w)+12
    obstacles=[dict(x=b['x']-2,y=b['y']-2,w=b['w']+4,h=b['h']+4,owner=b['id']) for b in records.values()]
    for edge in source['edges']:
        a,b=records[edge['source']],records[edge['target']]
        if abs(a['y']-b['y'])<2:
            right=b['x']>a['x'];start=(a['x']+a['w']+4 if right else a['x']-4,a['y']+22);stop=(b['x']-4 if right else b['x']+b['w']+4,b['y']+22)
        else:start=(a['x']+a['w']/2,a['y']+a['h']+4);stop=(b['x']+b['w']/2,b['y']-4)
        points=relation_route(start,stop,[o for o in obstacles if o['owner'] not in [a['id'],b['id']]],W,170)
        color=colors[a['group']];line(p.edges,points,PAPER,8);line(p.edges,points,color,2.8,'edge-'+edge['id'],'7 5' if edge['kind']=='influence' else None,**{'data-source':edge['source'],'data-target':edge['target'],'data-kind':edge['kind']})
        sx,sy=points[-2];tx,ty=stop
        if abs(sx-tx)<.1:
            d=1 if ty>sy else -1;arrow=[(tx-5,ty-d*9),(tx,ty),(tx+5,ty-d*9)]
        else:
            d=1 if tx>sx else -1;arrow=[(tx-d*9,ty-5),(tx,ty),(tx-d*9,ty+5)]
        line(p.edges,arrow,color,2.3);p.routes.append(dict(**edge,points=points))
    end+=55;line(p.root,[(50,end),(2050,end)],'#ABB7B7',1)
    p.paragraph(p.root,50,end+31,'SOLID = lineage     DASHED = code contribution. Trace NET/2 into three daughter branches, then follow 4.4BSD Lite into FreeBSD 2.0 and its separate contributions to NetBSD and BSD/OS.',2000,18)
    p.paragraph(p.root,50,end+83,'Source: FreeBSD UNIX system family tree. All 47 selected releases and 51 relationships retained. 4.1bBSD remains undated. Hardware pictures are illustrative period contexts; the exact record facts are printed beside them.',2000,15,color=p.muted)
    return p.finish(end+128,source,(25,440,2040,620))


def mars():
    source=json.loads((REPO/'projects/usefulcharts-cross-domain/artifacts/revision-2/mars/source.json').read_text(encoding='utf-8'));W=source['width']
    p=Poster('mars',W,'THE LONG ROAD TO MARS','32 launch campaigns · four national programs · spacecraft attached to their mission records · a shared calendar with reusable tracks',True)
    colors={g['id']:g['color'] for g in source['groups']};px=lambda y:105+(y-1960)*85
    sheet=ROOT/'artifacts/images/mars-sheet.png'
    specs={ident:dict(path=sheet,crop=((i%2)*627,(i//2)*627,627,627),height=182,caption=caption) for i,ident,caption in [(0,'mariner9','An orbiter maps Mars.'),(1,'viking1','Cruise assembly: orbiter + protected lander.'),(2,'viking2','A lander explores the surface.'),(3,'pathfinder','Petals open after the airbag landing.') ]}
    specs['mariner9']['clip']='M0 0H610V370H627V627H0Z'
    specs.update(mars2=dict(path=ROOT/'artifacts/references/soviet-43.jpg',height=172,caption='Mars 2/3 museum model · NASA history.'),mars3=dict(path=ROOT/'artifacts/references/soviet-43.jpg',height=172,caption='The same design family; a different outcome.'),nozomi=dict(path=ROOT/'artifacts/references/nozomi-39.jpg',height=176,caption='ISAS/JAXA concept · Mars orbit was never achieved.'),mars96=dict(path=ROOT/'artifacts/references/mars96-dlr.jpg',crop=(0,345,1000,325),height=120,caption='DLR model · five planned probes; launch failed.'))
    for spec in specs.values():spec['height']=130
    records=[]
    for n in source['nodes']:
        years=[n['launch']]+[n[k] for k in ['arrival','outcome'] if n.get(k)]+[s['end'] for s in n['spans']]
        w=280;spec=None
        records.append(dict(id=n['id'],node=n,year=n['launch'],start=px(min(years)),end=px(max(years)),group=n['group'],w=w,h=unit_height(n,w,18,26,16,spec),body_size=18,title_size=26,small=16,span_height=42*len(n['spans'])+15 if n['spans'] else 0))
    records.sort(key=lambda r:(r['year'],r['group'],r['id']))
    selected,occupied=pack_best(records,W,top=285,gap=23);bottom=max(o['y']+o['h'] for o in occupied)
    for i,g in enumerate(source['groups']):p.text(p.root,48+i*240,161,g['label'],24,'700',g['color'])
    p.text(p.root,1150,161,'● Launch     ◇ Mars encounter     × Dated loss     ━ Supported operations',22,color=p.muted)
    p.text(p.root,48,208,'X = calendar year. Equal distances mean equal elapsed years. Images identify spacecraft; only the marks encode dates.',21,color=p.muted)
    for year in range(1960,2008):
        x=px(year);line(p.edges,[(x,260),(x,bottom+25)],'#243C4D',1)
        if year%5==0:p.text(p.root,x,246,year,22,'700',p.muted,**{'text-anchor':'middle'})
    for r in selected:
        n=r['node'];color=colors[r['group']];g,_=timeline_unit(p,r,color,source)
        for circle in list(g.findall(tag('circle'))):g.remove(circle)
        for key,kind in [('launch','launch'),('arrival','arrival'),('outcome','loss')]:
            if n.get(key) is None:continue
            x,y=px(n[key]),r['y'];attrs={'data-year':str(n[key]),'data-kind':kind,'data-date-owner':n['id'],'id':'date-'+n['id']+'-'+kind}
            if kind=='launch':ET.SubElement(g,tag('circle'),dict(cx=str(x),cy=str(y),r='6',fill=color,**attrs))
            elif kind=='arrival':line(g,[(x,y-7),(x+7,y),(x,y+7),(x-7,y),(x,y-7)],color,2.3,**attrs)
            else:
                # A coincident dated loss has a second Y position but the same exact X.
                if n['outcome']==n['launch']:y+=13
                mark=ET.SubElement(g,tag('g'),attrs);line(mark,[(x-6,y-6),(x+6,y+6)],color,2);line(mark,[(x-6,y+6),(x+6,y-6)],color,2)
            p.marks.append(dict(owner=n['id'],kind=kind,year=n[key],x=x))
        for j,s in enumerate(n['spans']):
            yy=r['y']+r['h']+52+j*42;xs,xe=px(s['start']),px(s['end'])
            line(g,[(xs,yy),(xe,yy)],color,5,'span-'+n['id']+'-'+str(j),**{'data-span-owner':n['id'],'data-start':str(s['start']),'data-end':str(s['end'])})
            p.text(g,xs,yy-10,s['label']+' · '+str(s['start'])+'–'+str(s['end']),17,'700',color)
    # Reuse free calendar pockets for directly linked images. The picture itself
    # has no temporal coordinate; only the exact-X mission marks encode years.
    specs.pop('mars3')
    bindings=[]
    for ident,spec in specs.items():
        r=next(r for r in selected if r['id']==ident);iw,ih=390,285
        choices=[]
        for yy in range(290,int(bottom-ih)+1,25):
            for xx in range(45,int(W-iw-45),45):
                box=dict(x=xx,y=yy,w=iw,h=ih)
                if all(not intersects(box,o,20) for o in occupied):
                    distance=abs(xx+iw/2-r['tx']-140)+abs(yy-r['y'])*1.1
                    choices.append((distance,yy,xx,box))
        if not choices:raise ValueError('No released image pocket for '+ident)
        _,yy,xx,box=min(choices,key=lambda v:v[:3]);occupied.append(dict(box,owner='art-'+ident))
        anchors=[ident,'mars3'] if ident=='mars2' else [ident]
        p.image(spec,(xx+6,yy+29,iw-12,200),'art-'+ident,anchors,[r['group']],spec['caption'])
        p.text(p.root,xx+8,yy+22,'Mars 2 / 3' if ident=='mars2' else r['node']['label'],24,'700',colors[r['group']],True)
        p.paragraph(p.root,xx+8,yy+250,spec['caption'],iw-16,16,color=p.muted)
        for owner in anchors:
            bindings.append((owner,ident,xx,yy,iw,r['group']))
    for owner,ident,xx,yy,iw,gid in bindings:
        target=next(q for q in selected if q['id']==owner)
        start=(target['tx']+target['w']+3,target['y']+80);end=(xx+iw/2,yy-3)
        route=relation_route(start,end,occupied,W,265)
        line(p.edges,route,p.bg,7);line(p.edges,route,colors[gid],2,'image-owner-'+owner)
        p.routes.append(dict(id='image-owner-'+owner,source=owner,target='art-'+ident,kind='illustrates',points=route))
    bottom+=80
    p.paragraph(p.root,45,bottom,source['reading_note'],W-90,19,color=p.muted)
    p.paragraph(p.root,45,bottom+66,source['source_note'],W-90,17,color=p.muted)
    return p.finish(bottom+115,source,(980,280,1600,1050))


if __name__=='__main__':
    for case in sys.argv[1:] or ['instruments','bsd','mars']:globals()[case]()
