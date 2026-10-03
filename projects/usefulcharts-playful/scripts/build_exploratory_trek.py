#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2"]
# ///
"""Compose source-bound Trek imagery inside reusable calendar neighborhoods."""
import copy
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from exploratory_core import Poster,ROOT,REPO,tag,line,wrap,pack_best,unit_height,timeline_unit,intersects,relation_route
from artwork import art,save


def starships():
    sys.path.insert(0,str(REPO/'projects/star-trek-starships/scripts'))
    import build_flow_atlas as f
    f.OUT=ROOT/'artifacts/revision-3/starships/native'
    f.ASSET_IDS['enterprise-1701']='classic'
    original_card,original_paint,original_pack=f.card,f.paint,f.pack_shapes
    def illustrated_card(*args,**kwargs):
        c=original_card(*args,**kwargs)
        if c['has_art']:
            c['pieces'][2].update(x=c['end']+8,y=-226,w=326,h=218)
        return c
    def paint_without_old_art(s,c,b):
        original_paint(s,dict(c,has_art=False),b)
    candidates=[]
    def choose_packing(records,order):
        result=original_pack(records,order);candidates.append(result)
        return min(candidates,key=lambda c:c['height']) if order=='families' else result
    f.card=illustrated_card;f.paint=paint_without_old_art;f.pack_shapes=choose_packing
    f.main()
    out=ROOT/'artifacts/revision-3/starships';native=f.OUT
    root=ET.parse(native/'svgs/star-trek-starships.svg').getroot()
    layout=json.loads((native/'reviews/layout.json').read_text());packed=json.loads((native/'reviews/shared-row-layout.json').read_text())['layout']
    defs=root.find(tag('defs'))
    for symbol in list(defs.findall(tag('symbol'))):
        if symbol.get('id','').startswith('art-'):defs.remove(symbol)
    arts=[];boxes={b['id']:b for b in packed['boxes']}
    for c in packed['selected']:
        if not c['has_art']:continue
        ident=c['owner'];asset=f.ASSET_IDS[ident]
        path=(f.draw.ART/f.draw.ASSETS[asset]) if asset!='classic' else REPO/'projects/star-trek-starships/artifacts/images/reference/enterprise-original.jpg'
        crop=(0,295,1600,665) if asset=='classic' else None
        y=boxes[c['id']]['y'];identifier='art-'+ident
        a=art(root,path,(c['end']+10,y-222,320,204),identifier,[ident],[c['family']],'Design-family illustration attached to '+f.BY[ident]['name']+'; dates remain in the vector marks.',crop)
        root[-1].set('id',identifier);root[-1].set('style','mix-blend-mode:screen');arts.append(a)
        line(root,[(c['end'],y+12),(c['end']+7,y-9),(c['end']+28,y-22)],f.FAMILY_COLORS[c['family']],1.5,'image-owner-'+ident)
    by_card={c['id']:c for c in packed['selected']};routes=[]
    for g in root.findall(tag('g')):
        if g.get('class')!='typed-link':continue
        source_id,target_id=g.get('data-source'),g.get('data-target');a,b=by_card[source_id],by_card[target_id]
        start=(a['tx']+f.LABEL_W+12,boxes[a['id']]['y']+28+a['title_h']/2)
        stop=(b['tx']-12,boxes[b['id']]['y']+28+b['title_h']/2)
        points=f.route_relation(start,stop,packed['pieces']);identifier='relation-'+source_id+'-'+target_id
        g.set('id',identifier)
        for child in list(g):g.remove(child)
        color=f.FAMILY_COLORS[a['family']];line(g,points,'#020711',7);line(g,points,color,2.8,dash='5 6' if g.get('data-kind')!='name-succession' else None)
        ET.SubElement(g,tag('circle'),dict(cx=str(stop[0]),cy=str(stop[1]),r='4.5',fill=color))
        routes.append(dict(id=identifier,source=source_id,target=target_id,kind=g.get('data-kind'),points=points))
    layout['routes']=routes
    layout['units']=layout['boxes'];layout['marks']=layout['anchors'];layout['detail']=[1050,700,1700,1300]
    layout['packing_strategy']=packed['strategy'];layout['illustrations']=arts
    (out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
    save(root,out,arts,f.DATA)
    print(json.dumps(dict(case='starships',canvas=[layout['width'],layout['height']],images=len(arts),strategy=packed['strategy'])))


def civilizations_rejected_global():
    source=json.loads((REPO/'projects/star-trek-canonical-timeline/data/timeline.json').read_text(encoding='utf-8'))
    W=8000;p=Poster('civilizations',W,'STAR TREK · CIVILIZATIONS, CONTACTS & WARS','155 source-bound historical entries · Prime continuity · exact horizontal years in the calendar field · separate context for origins, alternate histories and the distant future',True)
    palette={'Federation':'#8BD9F1','Vulcan':'#D5AE7C','Andorian':'#A6C9F1','Romulan':'#BAA8E0','Klingon':'#F59C88','Cardassian':'#E2B86B','Dominion':'#CBABDE','Bajoran':'#95D3BB','Borg':'#C9D77F','Ferengi':'#ECC98F','Xindi':'#DCB4A1','Other':'#BFCBD4','Breen':'#94CEC3'}
    segments=[dict(start=2060,end=2165,x=100,width=1450,ticks=[2063,2100,2150,2161]),dict(start=2200,end=2300,x=1660,width=1400,ticks=[2200,2220,2240,2250,2260,2270,2280,2290,2300]),dict(start=2300,end=2360,x=3060,width=760,ticks=[2320,2340]),dict(start=2360,end=2378,x=3820,width=2320,ticks=list(range(2360,2378,2))),dict(start=2378,end=2405,x=6140,width=1710,ticks=[2378,2385,2390,2395,2400,2405])]
    def px(year):
        for s in segments:
            if s['start']<=year<=s['end']:return s['x']+(year-s['start'])/(s['end']-s['start'])*s['width']
        raise ValueError(year)
    records=[]
    for n in source['events']:
        record=dict(n,date_label=n['date']+' · '+n['actor']+' · '+n['kind'])
        years=[int(v) for v in re.findall(r'\b\d{4}\b',n['date'])];end=max(years or [n['year']])
        w=360
        records.append(dict(id=n['id'],node=record,year=n['year'],start=px(n['year']),end=px(end),group=n['actor'],w=w,h=unit_height(record,w,20,29,17),body_size=20,title_size=29,small=17,roam=True))
    records.sort(key=lambda r:(r['year'],r['group'],r['id']))
    selected,occupied=pack_best(records,W,top=340,gap=24);bottom=max(o['y']+o['h'] for o in occupied)
    for i,(name,color) in enumerate(palette.items()):p.text(p.root,45+i*550,168,name,25,'700',color,True)
    p.text(p.root,45,221,'X = year. All rows share the same calendar. The dense 2360–2378 window is expanded; // omits 2165–2200. Colored lines connect dated evidence within one record.',24,color=p.muted)
    p.text(p.root,45,265,'Find a contact, follow the consequences, compare neighboring powers. Color identifies the actor, not a permanent alliance.',23,color=p.muted)
    for index,s in enumerate(segments):
        label=str(s['start'])+'–'+str(s['end'])+(' · EXPANDED' if index==3 else '')
        p.text(p.root,s['x']+s['width']/2,303,label,24,'700','#8AC5E6',True,**{'text-anchor':'middle'})
        for year in s['ticks']:
            x=px(year);p.text(p.root,x,330,year,18,'700',p.muted,**{'text-anchor':'middle'});line(p.edges,[(x,342),(x,bottom+15)],'#284252',1)
    p.text(p.root,1605,310,'//',35,'700','#E7C597')
    by={r['id']:r for r in selected}
    for r in selected:
        g,_=timeline_unit(p,r,palette.get(r['group'],'#BFCBD4'),source)
        circle=g.find(tag('circle'));circle.set('id','date-'+r['id']);circle.set('data-year',str(r['year']));circle.set('data-date-owner',r['id'])
        p.marks.append(dict(owner=r['id'],year=r['year'],x=r['start']))
        if r['end']>r['start']:
            duration=g.find(".//*[@id='duration-"+r['id']+"']");duration.set('data-start',str(r['year']));duration.set('data-end',str(max(int(v) for v in re.findall(r'\b\d{4}\b',r['node']['date']))))
    # The sample portraits identify species, never named individuals. Place each
    # in a free pocket with a direct visible connector to the relevant event.
    image_defs=[('st-001',0,'Human · first contact'),('st-011',1,'Vulcan · the Kir’Shara'),('st-003',2,'Klingon · Broken Bow')]
    for actor,cell,caption in [('Cardassian',3,'Cardassian · shifting power'),('Borg',4,'Borg · collective threat'),('Ferengi',5,'Ferengi · contact and commerce')]:
        options=[r for r in selected if r['group']==actor];image_defs.append((options[len(options)//2]['id'],cell,caption))
    image_specs=[]
    for ident,cell,caption in image_defs:image_specs.append((ident,dict(path=ROOT/'artifacts/images/species-sheet.png',crop=((cell%3)*512,(cell//3)*512,512,512)),caption))
    for ident,filename in [('st-002','enterprise-nx.png')]:image_specs.append((ident,dict(path=REPO/'projects/star-trek-starships/artifacts/images/space-edition'/filename),'Enterprise NX-01 · exploration'))
    for ident,spec,caption in image_specs:
        r=by[ident];iw,ih=340,260;choices=[]
        for yy in range(360,int(bottom-ih),40):
            for xx in range(45,W-iw-45,60):
                box=dict(x=xx,y=yy,w=iw,h=ih)
                if all(not intersects(box,o,22) for o in occupied):choices.append((abs(xx-r['tx'])+abs(yy-r['y']),yy,xx,box))
        if not choices:raise ValueError('No illustrated pocket '+ident)
        _,yy,xx,box=min(choices,key=lambda v:v[:3]);occupied.append(dict(box,owner='art-'+ident))
        p.image(spec,(xx+6,yy+3,iw-12,215),'art-'+ident,[ident],[r['group']],caption+'; illustrative representative, not a named portrait.')
        p.text(p.root,xx+8,yy+246,caption,22,'700',palette.get(r['group'],'#BFCBD4'),True)
        start=(r['tx']+180,r['y']+25+r['h']+3);end=(xx+iw/2,yy-3)
        points=relation_route(start,end,[o for o in occupied if o['owner'] not in [ident,'art-'+ident]],W,342)
        line(p.edges,points,p.bg,7);line(p.edges,points,palette.get(r['group'],'#BFCBD4'),2.5,'image-owner-'+ident)
        p.routes.append(dict(id='image-owner-'+ident,source=ident,target='art-'+ident,kind='illustrates',points=points))
    # Separate contextual sequences are deliberately outside the numeric field.
    y=bottom+75
    p.text(p.root,45,y,'CONTEXT BEYOND THE MAIN CALENDAR',43,'700','#8BD9F1',True)
    p.text(p.root,45,y+42,'These records retain the source’s approximate, unstated, future or alternate dates. Their positions express reading order and carry no numeric X coordinate.',23,color=p.muted)
    top=y+95;columns=12;cw=(W-90)/columns;ends=[top]*columns
    for section,items,color in [('ORIGINS',source['origins'],'#D8BD91'),('DISTANT FUTURE',source['future'],'#9DCDBF'),('ALTERNATE HISTORIES',source['branches'],'#C3AADF')]:
        startcol={'ORIGINS':0,'DISTANT FUTURE':4,'ALTERNATE HISTORIES':8}[section]
        for col in range(startcol,startcol+4):p.text(p.root,45+col*cw,top-7,section if col==startcol else 'CONTINUED',25,'700',color,True);ends[col]+=24
        previous=None
        for i,n in enumerate(items):
            col=startcol+min(3,i*4//len(items));x=45+col*cw;yy=ends[col];g=ET.SubElement(p.body,tag('g'),dict(id='record-'+n['id'],**{'data-record-id':n['id']}))
            p.text(g,x+9,yy+24,n['date'],19,'700',color,**{'data-field':'date'})
            ay=p.paragraph(g,x+9,yy+59,n['label'],cw-38,29,'700',color,True,field='label')
            ay=p.paragraph(g,x+9,ay+4,n['detail'],cw-38,20,field='detail')
            ay=p.paragraph(g,x+9,ay+6,n['credit'],cw-38,17,color=p.muted,field='credit')
            line(g,[(x,yy),(x,ay+4)],color,3,'context-stem-'+n['id'])
            b=dict(id=n['id'],x=x,y=yy,w=cw-20,h=ay-yy+15);p.boxes.append(b);p.units.append(b);ends[col]=ay+36
            if previous and previous[0]==col:line(p.edges,[(x,previous[1]),(x,yy)],color,1.8,'sequence-'+n['id'])
            previous=(col,ay+4)
    end=max(ends)+20
    p.paragraph(p.root,45,end,'Independent educational fan atlas. Source notes and original selection are retained for every entry. Dates follow the cited screen stories; conflicts and changes of allegiance belong to their named events. Portraits are generic illustrative representatives. Ship images identify design families.',W-90,21,color=p.muted)
    out=p.finish(end+80,source,(3820,340,2000,1400))
    layout=json.loads((out/'layout.json').read_text());layout['segments']=segments;(out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')


def civilizations_rejected_chapters():
    source=json.loads((REPO/'projects/star-trek-canonical-timeline/data/timeline.json').read_text(encoding='utf-8'))
    W=4800;p=Poster('civilizations',W,'STAR TREK · CIVILIZATIONS, CONTACTS & WARS','155 historical entries · five chronological chapters · follow contacts, conflicts and political changes · full source notes retained',True)
    palette={'Federation':'#8BD9F1','Vulcan':'#D5AE7C','Andorian':'#A6C9F1','Romulan':'#BAA8E0','Klingon':'#F59C88','Cardassian':'#E2B86B','Dominion':'#CBABDE','Bajoran':'#95D3BB','Borg':'#C9D77F','Ferengi':'#ECC98F','Other':'#BFCBD4'}
    p.text(p.root,45,166,'X = calendar year within each labeled chapter. All rows in that chapter share its scale. Chapter scales differ; the first chapter explicitly breaks the long early gap.',22,color=p.muted)
    for i,(actor,color) in enumerate(palette.items()):p.text(p.root,45+i*425,208,actor,25,'700',color,True)
    chapters=[(2063,2161,'01 · FIRST CONTACT TO FEDERATION',[2063,2151,2153,2155,2157,2159,2161]),(2223,2293,'02 · EXPLORATION, CONFRONTATION & PEACE',[2223,2240,2250,2260,2270,2280,2293]),(2311,2368,'03 · A NEW GENERATION',[2311,2330,2340,2350,2360,2368]),(2369,2375,'04 · THE DOMINION WAR & PARALLEL STRUGGLES',list(range(2369,2376))),(2376,2402,'05 · AFTERMATH, FRACTURE & RECONSTRUCTION',[2376,2380,2385,2390,2395,2400,2402])]
    art_owners={'st-001':(0,'Human · first contact'),'st-011':(1,'Vulcan · Surak’s legacy'),'st-003':(2,'Klingon · first contact')}
    for actor,cell,caption in [('Cardassian',3,'Cardassian · a changing order'),('Borg',4,'Borg · collective threat'),('Ferengi',5,'Ferengi · commerce and reform')]:
        ns=[n for n in source['events'] if n['actor']==actor];art_owners[ns[len(ns)//2]['id']]=(cell,caption)
    sheet=ROOT/'artifacts/images/species-sheet.png';y=275;windows=[]
    for ci,(first,last,title,ticks) in enumerate(chapters):
        chapter_top=y;p.text(p.root,45,y,title,43,'700','#8BD9F1',True);y+=71
        def px(year):
            if ci==0:return 100 if year==2063 else 650+(year-2151)/(2161-2151)*(W-780)
            return 100+(year-first)/(last-first)*(W-230)
        records=[]
        for n in source['events']:
            if not first<=n['year']<=last:continue
            nn=dict(n,date_label=n['date']+' · '+n['actor']);w=380
            # Some dates describe an earlier war recalled later, or an interval
            # followed by a treaty. Only the explicit source year gets a point;
            # preserve the entire qualified wording beside it.
            records.append(dict(id=n['id'],node=nn,year=n['year'],start=px(n['year']),end=px(n['year']),group=n['actor'],w=w,h=unit_height(nn,w,18,27,16),body_size=18,title_size=27,small=16,roam=True))
        records.sort(key=lambda r:(r['year'],r['group'],r['id']))
        selected,occupied=pack_best(records,W,top=y+35,gap=20);bottom=max(o['y']+o['h'] for o in occupied)
        for year in ticks:
            x=px(year);p.text(p.root,x,y+15,year,21,'700',p.muted,**{'text-anchor':'middle'});line(p.edges,[(x,y+26),(x,bottom+8)],'#264252',1.2)
        if ci==0:p.text(p.root,375,y+16,'// 2064–2150 omitted',20,'700','#D5AE7C',**{'text-anchor':'middle'})
        for r in selected:
            g,_=timeline_unit(p,r,palette.get(r['group'],'#BFCBD4'),source);g.set('data-calendar-window',str(ci))
            circle=g.find(tag('circle'));circle.set('id','date-'+r['id']);circle.set('data-year',str(r['year']));circle.set('data-date-owner',r['id'])
            p.marks.append(dict(owner=r['id'],year=r['year'],x=r['start'],window=ci))
        # Inline visual anchors occupy released pockets inside this chapter.
        chapter_art=[(r,art_owners[r['id']]) for r in selected if r['id'] in art_owners]
        if ci in [0,1,3,4]:
            r=next((r for r in selected if r['id']=='st-002'),selected[-1])
            chapter_art.append((r,(-1,['Enterprise NX-01','Exploration era','Defiant design family','Voyager design family'][[0,1,3,4].index(ci)])))
        for r,(cell,caption) in chapter_art:
            if cell>=0:spec=dict(path=sheet,crop=((cell%3)*512,(cell//3)*512,512,512))
            else:
                filename={0:'enterprise-nx.png',1:'discovery.png',3:'defiant.png',4:'voyager.png'}[ci]
                spec=dict(path=REPO/'projects/star-trek-starships/artifacts/images/space-edition'/filename)
                # Context design images have a named story association, not an
                # invented actor portrait or physical ship in an unrelated event.
                if ci==1:r=next(q for q in selected if q['id']=='st-023');caption='Discovery design family · wartime Starfleet'
                elif ci==3:r=next(q for q in selected if 'Dominion' in q['node']['label'] or 'DOMINION' in q['node']['label']);caption='Defiant design family · war-era Starfleet'
                elif ci==4:r=next(q for q in selected if q['id']=='st-103');caption='Voyager design family · the return'
            iw,ih=310,240;choices=[]
            for yy in range(int(y+40),int(bottom-ih)+1,25):
                for xx in range(45,W-iw-45,50):
                    box=dict(x=xx,y=yy,w=iw,h=ih)
                    if all(not intersects(box,o,18) for o in occupied):choices.append((abs(xx-r['tx'])+abs(yy-r['y']),yy,xx,box))
            if not choices:
                # Extend only a local visual pocket, without suppressing facts.
                xx,yy=45,bottom+20;box=dict(x=xx,y=yy,w=iw,h=ih);bottom=yy+ih
            else:_,yy,xx,box=min(choices,key=lambda v:v[:3])
            identifier='art-'+r['id']+('-ship' if cell<0 else '-species');occupied.append(dict(box,owner=identifier))
            p.image(spec,(xx+6,yy+2,iw-12,182),identifier,[r['id']],[r['group']],caption+'; illustrative subject context.')
            p.paragraph(p.root,xx+8,yy+208,caption,iw-16,21,'700',palette.get(r['group'],'#BFCBD4'),True)
            a=(r['tx']+r['w']/2,r['y']+25+r['h']+3);b=(xx+iw/2,yy-3)
            points=relation_route(a,b,[o for o in occupied if o['owner'] not in [r['id'],identifier]],W,y+26)
            line(p.edges,points,p.bg,7);line(p.edges,points,palette.get(r['group'],'#BFCBD4'),2,'image-owner-'+identifier)
            p.routes.append(dict(id='image-owner-'+identifier,source=r['id'],target=identifier,kind='illustrates',points=points))
        windows.append(dict(id=ci,first=first,last=last,top=chapter_top,bottom=bottom,ticks=[dict(year=t,x=px(t)) for t in ticks]))
        y=bottom+100;line(p.root,[(45,y-48),(W-45,y-48)],'#496171',1.4)
    p.text(p.root,45,y,'ORIGINS · DISTANT FUTURE · ALTERNATE HISTORIES',42,'700','#C6B2DE',True)
    p.text(p.root,45,y+42,'Separate contextual sequences, outside the numerical calendar. Approximate and conditional dates retain the original wording.',22,color=p.muted)
    start=y+87;cw=(W-90)/8;ends=[start]*8
    for section,items,color,startcol,count in [('ORIGINS',source['origins'],'#D8BD91',0,3),('DISTANT FUTURE',source['future'],'#9DCDBF',3,3),('ALTERNATE HISTORIES',source['branches'],'#C3AADF',6,2)]:
        for col in range(startcol,startcol+count):p.text(p.root,45+col*cw,start,section if col==startcol else 'CONTINUED',24,'700',color,True);ends[col]+=23
        for i,n in enumerate(items):
            col=startcol+min(count-1,i*count//len(items));x=45+col*cw;yy=ends[col];g=ET.SubElement(p.body,tag('g'),dict(id='record-'+n['id'],**{'data-record-id':n['id']}))
            ay=p.paragraph(g,x+9,yy+25,n['date'],cw-30,17,'700',color,field='date')
            ay=p.paragraph(g,x+9,ay+10,n['label'],cw-30,27,'700',color,True,field='label')
            ay=p.paragraph(g,x+9,ay+4,n['detail'],cw-30,18,field='detail');ay=p.paragraph(g,x+9,ay+6,n['credit'],cw-30,16,color=p.muted,field='credit')
            line(g,[(x,yy+5),(x,ay+4)],color,3,'context-stem-'+n['id']);b=dict(id=n['id'],x=x,y=yy,w=cw-15,h=ay-yy+16);p.boxes.append(b);p.units.append(b);ends[col]=ay+33
    end=max(ends)+25;p.paragraph(p.root,45,end,'Independent educational fan atlas. Every selected source entry remains in the poster. Portraits are generic species representatives; spacecraft identify design families. The chapter calendar marks only each source entry’s anchor year; the complete date wording explains intervals, recollections and uncertainty.',W-90,20,color=p.muted)
    out=p.finish(end+90,source,(2250,350,1800,1250));layout=json.loads((out/'layout.json').read_text());layout['windows']=windows;(out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')


def civilizations():
    """Pack chronological story bands; each band has the same numeric calendar."""
    source=json.loads((REPO/'projects/star-trek-canonical-timeline/data/timeline.json').read_text(encoding='utf-8'))
    W=4800;p=Poster('civilizations',W,'STAR TREK · CIVILIZATIONS, CONTACTS & WARS','155 source-bound entries · illustrated story bands · a repeated, shared calendar · origins, distant futures and alternate histories remain separate',True)
    palette={'Federation':'#8BD9F1','Vulcan':'#D5AE7C','Andorian':'#A6C9F1','Romulan':'#BAA8E0','Klingon':'#F59C88','Cardassian':'#E2B86B','Dominion':'#CBABDE','Bajoran':'#95D3BB','Borg':'#C9D77F','Ferengi':'#ECC98F','Other':'#BFCBD4'}
    p.text(p.root,45,158,'Read the stories left to right, then down. In the calendar strip above each band, X = year on the same labeled scale. A colored leader binds every story to its date.',20,color=p.muted)
    p.text(p.root,45,197,'Story columns are labels, not date positions. Filled points mark stated anchor years; hollow points mark approximate or retrospective anchors. Read the complete date wording.',20,color=p.muted)
    for i,(actor,color) in enumerate(palette.items()):p.text(p.root,45+i*425,244,actor,23,'700',color,True)
    segments=[dict(start=2060,end=2165,x=85,width=770,ticks=[2063,2150,2161]),dict(start=2200,end=2300,x=925,width=910,ticks=[2223,2250,2270,2293]),dict(start=2300,end=2360,x=1835,width=630,ticks=[2330,2360]),dict(start=2360,end=2378,x=2465,width=1350,ticks=[2365,2370,2375]),dict(start=2378,end=2405,x=3815,width=885,ticks=[2385,2395,2405])]
    def px(year):
        for s in segments:
            if s['start']<=year<=s['end']:return s['x']+(year-s['start'])/(s['end']-s['start'])*s['width']
        raise ValueError(year)
    art_owners={'st-001':(0,'Human'),'st-011':(1,'Vulcan'),'st-003':(2,'Klingon')}
    for actor,cell in [('Cardassian',3),('Borg',4),('Ferengi',5)]:
        ns=[n for n in source['events'] if n['actor']==actor];art_owners[ns[len(ns)//2]['id']]=(cell,actor)
    for ident,name in [('st-002','enterprise-nx.png'),('st-023','discovery.png'),('st-091','defiant.png'),('st-103','voyager.png')]:art_owners[ident]=(-1,name)
    sheet=ROOT/'artifacts/images/species-sheet.png';columns=12;cw=(W-90)/columns;records=sorted(source['events'],key=lambda n:(n['year'],n['id']));top=290;bands=[]
    for row in range(math.ceil(len(records)/columns)):
        items=records[row*columns:(row+1)*columns];year_order=sorted(set(n['year'] for n in items));body=top+55+len(year_order)*4;ends=[]
        for s in segments:
            for year in s['ticks']:p.text(p.root,px(year),top+17,year,16,'700',p.muted,**{'text-anchor':'middle'})
        p.text(p.root,890,top+17,'//',19,'700','#D8BD91',**{'text-anchor':'middle'})
        for i,n in enumerate(items):
            x=45+i*cw;color=palette.get(n['actor'],'#BFCBD4');g=ET.SubElement(p.body,tag('g'),dict(id='record-'+n['id'],**{'data-record-id':n['id']}));date_x=px(n['year']);date_y=top+29+year_order.index(n['year'])*4
            line(p.edges,[(date_x,date_y),(x+cw/2,date_y),(x+cw/2,body-4)],color,1.5,'owner-'+n['id'])
            qualified=any(token in n['date'].lower() for token in ['c.','early','recalled','earlier'])
            ET.SubElement(g,tag('circle'),dict(id='date-'+n['id'],cx=str(date_x),cy=str(date_y),r='3.3',fill='none' if qualified else color,stroke=color,**{'stroke-width':'1.4','data-year':str(n['year']),'data-date-owner':n['id'],'data-date-qualifier':'approximate-or-contextual' if qualified else 'stated-anchor'}))
            p.marks.append(dict(owner=n['id'],year=n['year'],x=date_x,band=row))
            special=art_owners.get(n['id']);tx=x+8;tw=cw-22;yy=body+20
            if special:
                cell,name=special;spec=dict(path=sheet,crop=((cell%3)*512,(cell//3)*512,512,512)) if cell>=0 else dict(path=REPO/'projects/star-trek-starships/artifacts/images/space-edition'/name)
                p.image(spec,(x+6,body+4,108,101),'art-'+n['id'],[n['id']],[n['actor']],'Illustrative '+(name if cell>=0 else 'Starfleet design family')+' context for '+n['label'])
                tx=x+121;tw=cw-135
            yy=p.paragraph(g,tx,yy,n['date'],tw,16,'700',color,field='date')
            yy=p.paragraph(g,tx,yy+16,n['label'],tw,25,'700',color,True,field='label')
            yy=p.paragraph(g,tx,yy+3,n['actor']+' · '+n['kind'],tw,15,color=p.muted)
            yy=max(yy+7,body+127 if special else yy+7)
            yy=p.paragraph(g,x+8,yy,n['detail'],cw-22,17,field='detail');yy=p.paragraph(g,x+8,yy+5,n['credit'],cw-22,15,color=p.muted,field='credit')
            line(g,[(x+1,body+5),(x+1,yy+3)],color,2.5,'story-stem-'+n['id']);b=dict(id=n['id'],x=x,y=body,w=cw-7,h=yy-body+13);p.boxes.append(b);p.units.append(b);ends.append(yy+13)
        if row==math.ceil(len(records)/columns)-1:
            # Reclaim the nine unused story slots for a source-backed political
            # comparison. This inset is schematic and outside the calendar strip.
            x0=45+3*cw+28;iy=body;group=ET.SubElement(p.body,tag('g'),dict(id='dominion-coalitions',**{'data-source-records':'st-076 st-077 st-080 st-085 st-090 st-092'}))
            p.text(group,x0,iy+25,'THE DOMINION WAR · CHANGING COALITIONS',35,'700','#D8C3ED',True)
            p.text(group,x0,iy+54,'Political relationships · schematic, not an elapsed-time axis',18,color=p.muted)
            alliance_x=x0+780;dominion_x=x0+2040
            for ident,xx,ww,col in [('alliance',alliance_x-260,520,palette['Federation']),('dominion',dominion_x-180,360,palette['Dominion'])]:
                ET.SubElement(group,tag('rect'),dict(id='political-'+ident,x=str(xx),y=str(iy+85),width=str(ww),height='56',rx='4',fill='#102B3A',stroke=col,**{'stroke-width':'1.8'}))
            p.text(group,alliance_x,iy+124,'FEDERATION ALLIANCE',32,'700',palette['Federation'],True,**{'text-anchor':'middle'})
            p.text(group,dominion_x,iy+124,'DOMINION',32,'700',palette['Dominion'],True,**{'text-anchor':'middle'})
            line(group,[(alliance_x+260,iy+112),(dominion_x-180,iy+112)],'#E8A184',3,'coalitions-war')
            p.text(group,(alliance_x+dominion_x)/2+40,iy+98,'WAR · 2373–2375',20,'700','#E8A184',True,**{'text-anchor':'middle'})
            for slug,label,xx,yy,target,col,note in [
                ('klingon','KLINGON EMPIRE',x0+120,iy+112,alliance_x,'Klingon','Alliance restored · 2373'),
                ('romulan','ROMULAN STAR EMPIRE',x0+300,iy+208,alliance_x,'Romulan','Enters the war · 2374'),
                ('cardassian','CARDASSIA',x0+2750,iy+112,dominion_x,'Cardassian','Dukat joins · 2373'),
                ('breen','BREEN CONFEDERACY',x0+2680,iy+208,dominion_x,'Other','Joins · 2375')]:
                color=palette[col]
                if slug=='klingon':points=[(xx+180,yy-7),(target-260,yy-7)]
                elif slug=='cardassian':points=[(xx-180,yy-7),(target+180,yy-7)]
                else:points=[(xx+195 if xx<target else xx-195,yy-7),(target,yy-7),(target,iy+141)]
                line(group,points,color,2,'coalition-'+slug);p.routes.append(dict(id='coalition-'+slug,source=slug,target='alliance' if target==alliance_x else 'dominion',kind='political',points=points))
                p.text(group,xx,yy,label,25,'700',color,True,**{'text-anchor':'middle'});p.text(group,xx,yy+29,note,17,color=p.muted,**{'text-anchor':'middle'})
            p.text(group,(alliance_x+dominion_x)/2,iy+193,'Damar’s rebellion breaks with the Dominion in 2375.',18,color=p.muted,**{'text-anchor':'middle'})
            ends.append(iy+257)
        bottom=max(ends);bands.append(dict(row=row,top=top,bottom=bottom,records=[n['id'] for n in items]));top=bottom+20
        line(p.root,[(45,top-16),(W-45,top-16)],'#3E5665',1)
    p.text(p.root,45,top+28,'ORIGINS · DISTANT FUTURE · ALTERNATE HISTORIES',39,'700','#C6B2DE',True)
    p.text(p.root,45,top+65,'Separate context outside the calendar strips. Dates retain the source’s approximate, unstated or conditional wording.',21,color=p.muted)
    start=top+105;cw=(W-90)/8;ends=[start]*8
    for section,items,color,startcol,count in [('ORIGINS',source['origins'],'#D8BD91',0,3),('DISTANT FUTURE',source['future'],'#9DCDBF',3,3),('ALTERNATE HISTORIES',source['branches'],'#C3AADF',6,2)]:
        for col in range(startcol,startcol+count):p.text(p.root,45+col*cw,start,section if col==startcol else 'CONTINUED',24,'700',color,True);ends[col]+=23
        for i,n in enumerate(items):
            col=startcol+min(count-1,i*count//len(items));x=45+col*cw;yy=ends[col];g=ET.SubElement(p.body,tag('g'),dict(id='record-'+n['id'],**{'data-record-id':n['id']}))
            ay=p.paragraph(g,x+9,yy+24,n['date'],cw-30,17,'700',color,field='date');ay=p.paragraph(g,x+9,ay+20,n['label'],cw-30,27,'700',color,True,field='label')
            ay=p.paragraph(g,x+9,ay+4,n['detail'],cw-30,18,field='detail');ay=p.paragraph(g,x+9,ay+6,n['credit'],cw-30,16,color=p.muted,field='credit')
            line(g,[(x,yy+5),(x,ay+4)],color,3,'context-stem-'+n['id']);b=dict(id=n['id'],x=x,y=yy,w=cw-15,h=ay-yy+16);p.boxes.append(b);p.units.append(b);ends[col]=ay+29
    end=max(ends)+20;p.paragraph(p.root,45,end,'Independent educational fan atlas. All 155 selected records and their full notes are retained. Species portraits are generic representatives; spacecraft identify design families. Every calendar strip uses the same piecewise-linear X mapping; the // break omits 2165–2200. Read qualified dates beside their entries.',W-90,19,color=p.muted)
    out=p.finish(end+83,source,(0,290,1800,1020));layout=json.loads((out/'layout.json').read_text());layout.update(segments=segments,bands=bands);(out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')


if __name__=='__main__':
    for case in sys.argv[1:] or ['starships','civilizations']:globals()[case]()

