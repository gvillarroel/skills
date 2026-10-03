#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11"]
# ///
"""Dense chronological branches, preserving dates without a false shared time axis."""
import build_poster as p

def main():
    p.rect(0,0,p.W,239,p.DARK)
    p.text("STAR TREK / CIVILIZATIONS & WARS",p.W/2,147,134,"display",p.PAPER,"middle")
    p.text("THE PRIME TIMELINE · ANCIENT ORIGINS TO THE 32ND CENTURY",p.W/2,220,36,"display",p.PAPER,"middle")
    p.text("HOW TO READ",p.M,278,27,"display")
    p.paragraph("Read downward in each historical branch. Dates establish chronology; neighboring branches use different spacing. Lines group related histories. Only labeled arrows assert a political relationship.",p.M+192,275,2100,20,fill=p.MUTED)
    p.paragraph("Color identifies the subject, not a permanent alliance. Political union, cooperation, war and temporal branches are distinct.",p.W-1070,275,1004,20,fill=p.MUTED)
    # A compact union diagram makes the defining political relationship visible.
    fy=338
    p.line(p.M,fy,p.W-p.M,fy,p.INK,1.6)
    p.text("2161",p.M,fy+49,44,"display")
    p.text("THE FOUR FOUNDERS",p.M+126,fy+48,34,"display")
    worlds=[("EARTH",670,240,"Federation"),("VULCAN",1050,240,"Vulcan"),
            ("ANDORIA",1440,250,"Andorian"),("TELLAR",1830,240,"Other")]
    for name,x,w,actor in worlds:
        p.pill(name,x,fy+12,w,p.COLORS[actor])
        p.line(x+w/2,fy+60,x+w/2,fy+99,p.COLORS[actor],3.2)
    p.line(790,fy+99,2270,fy+99,p.INK,3)
    p.arrow([(2270,fy+99),(2270,fy+36),(2470,fy+36)],"founding members",2310,fy+91,source="Earth / Vulcan / Andoria / Tellar",target="United Federation of Planets",kind="founding-member")
    p.pill("UNITED FEDERATION OF PLANETS",2485,fy+12,780,p.COLORS["Federation"])
    p.text("A common polity; the four member worlds retain distinct identities.",p.W-p.M,fy+99,19,"body",p.MUTED,"end")
    y=fy+141
    p.text('THE PRIME SEQUENCE',p.M,y+28,30,'display')
    seq=[('2063','First Contact','Federation'),('2161','Federation','Federation'),('2256-57','Klingon war','Klingon'),('2293','Khitomer','Klingon'),('2367','Wolf 359','Borg'),('2369','Bajor / DS9','Bajoran'),('2373-75','Dominion War','Dominion'),('2385','Mars attack','Federation'),('2387','Romulus lost','Romulan'),('2401','Frontier Day','Borg'),('3069','The Burn','Federation'),('3190s','Reconstruction','Federation')]
    sx=p.M+362;step=(p.W-p.M-130-sx)/(len(seq)-1)
    p.line(sx,y+75,p.W-p.M-130,y+75,p.INK,2.2)
    for i,(date,label,actor) in enumerate(seq):
        cx=sx+i*step
        p.circle(cx,y+75,7,p.COLORS[actor],p.INK,1.1)
        p.text(date,cx,y+56,22,'display',anchor='middle')
        p.text(label,cx,y+108,19,'body',anchor='middle')
    p.text('Sequence only; intervals are compressed.',p.M,y+65,18,'body',p.MUTED)
    y+=150
    data=p.DATA
    # Origins and futures stay with their subjects, reclaiming the space beside short branches.
    groups=[
        dict(title="EARTH & THE FEDERATION",actor="Federation",lanes={"earth"},origin=[10,11],future=[1,2,5,8,11],weight=1.33),
        dict(title="VULCAN, ANDORIA & ROMULUS",actor="Romulan",lanes={"founders","romulan"},origin=[4],future=[4],weight=1.00),
        dict(title="THE KLINGON EMPIRE",actor="Klingon",lanes={"klingon"},origin=[5,6],future=[3,10],weight=.88),
        dict(title="BAJOR, CARDASSIA & DOMINION",actor="Cardassian",lanes={"cardassia","dominion"},origin=[2,8],future=[6,9],weight=1.2),
        dict(title="BORG & THE DELTA QUADRANT",actor="Borg",lanes={"delta"},origin=[7],future=[],weight=1.03),
        dict(title="OTHER CIVILIZATIONS & POWERS",actor="Other",lanes={"other"},origin=[0,1,3,9],future=[0,7],weight=1.20),
    ]
    gap=29; unit=(p.W-2*p.M-gap*5)/sum(g['weight'] for g in groups)
    x=p.M; ends=[]
    for gi,g in enumerate(groups):
        w=unit*g['weight']; color=p.COLORS[g['actor']]
        p.rect(x,y,w,65,color,p.INK,1.2)
        title_lines=p.wrap(g['title'],w-25,29,'display')
        for i,v in enumerate(title_lines):p.text(v,x+12,y+26+i*29,29,'display')
        py=y+91
        origins=[dict(data['origins'][i],actor=g['actor']) for i in g['origin']]
        events=sorted([e for e in data['events'] if e['lane'] in g['lanes']],key=lambda e:e['year'])
        futures=[]
        # Context color follows its actual subject, not merely the containing column.
        for e in origins:
            if e['label']=='Xindi Civil War':e['actor']='Xindi'
            if 'Bajoran' in e['label']:e['actor']='Bajoran'
            if 'Vaadwaur' in e['label']:e['actor']='Vaadwaur'
            if 'Vulcan' in e['label']:e['actor']='Vulcan'
        for e in futures:
            if 'EMERALD CHAIN' in e['label']:e['actor']='Andorian'
            if 'Breen' in e['label']:e['actor']='Breen'
        sections=[('ANCIENT FOUNDATIONS',origins),('THE PRIME HISTORY',events),('THE DISTANT FUTURE',futures)]
        prev=None
        for subtitle,items in sections:
            if not items:continue
            if prev:
                p.line(x+3,prev,x+3,py+20,color,2,'5 5')
            p.text(subtitle,x+20,py+15,18,'display',p.MUTED)
            py+=35
            for e in items:
                if prev:
                    p.line(x+3,prev,x+3,py+5,color,2.7)
                    p.links.append(dict(type='reading-sequence',source=prev_id,target=e['id']))
                py=p.event(e,x,py,w)+8
                prev=py-21;prev_id=e['id']
        p.regions.append(dict(id=['federation','vulcan-romulan','klingon','bajor-dominion','borg-delta','other-powers'][gi],x=x,y=y,w=w,h=py-y))
        ends.append(dict(x=x,y=py,w=w,actor=g['actor']))
        x+=w+gap
    bottom=max(e['y'] for e in ends)
    # Political relationship diagrams fill only genuine open pockets, below the local history.
    # They reference existing facts without increasing the historical-entry census.
    for pocket,ids in [(ends[1],[0,1,2,7]),(ends[2],[3,4,5,6])]:
        px,py,pw=pocket['x'],pocket['y']+25,pocket['w']
        p.line(px,py,px+pw,py,p.INK,2)
        p.text('ALTERNATE HISTORIES',px+7,py+34,29,'display')
        py=p.paragraph('Separate branches, erased histories or conditional futures.',px+8,py+60,pw-16,18,fill=p.MUTED)+16
        by=py
        for i in ids:py=p.event(data['branches'][i],px,py,pw,actor='Other')+10
        p.regions.append(dict(id='branches-'+str(ids[0]),x=px,y=by,w=pw,h=py-by))
        bottom=max(bottom,py)
    # The second pocket explains the canonically separate Borg factions.
    pocket=ends[4];px,py,pw=pocket['x'],pocket['y']+31,pocket['w']
    p.line(px,py,px+pw,py,p.INK,1)
    p.text('2401: TWO DIFFERENT BORG STORIES',px+7,py+32,25,'display')
    py+=53
    p.pill('JURATI\'S COLLECTIVE',px+10,py,pw-20,p.COLORS['Borg'])
    py=p.paragraph('Cooperation and a request for provisional membership; the transwarp conduit becomes a joint concern.',px+15,py+75,pw-30,18,fill=p.MUTED)+28
    p.pill('THE JUPITER HIVE',px+10,py,pw-20,p.COLORS['Borg'])
    py=p.paragraph('The Queen behind Frontier Day attacks Starfleet. Enterprise-D destroys her cube.',px+15,py+75,pw-30,18,fill=p.MUTED)+25
    py=p.paragraph('One hive\'s destruction does not establish the extinction of every Borg faction.',px+15,py,pw-30,18,fill=p.MUTED)
    bottom=max(bottom,py)
    pocket=ends[3];px,py,pw=pocket['x'],pocket['y']+30,pocket['w']
    p.line(px,py,px+pw,py,p.INK,1)
    p.text('INSIDE THE DOMINION',px+7,py+34,29,'display')
    py+=58
    p.pill('FOUNDERS / CHANGELINGS',px+14,py,pw-28,p.COLORS['Dominion'])
    p.arrow([(px+pw/2,py+48),(px+pw/2,py+94)],'rule through',px+pw/2+92,py+81,source='Founders',target='Vorta',kind='government')
    p.pill('VORTA',px+14,py+99,pw-28,p.COLORS['Dominion'])
    p.arrow([(px+pw/2,py+147),(px+pw/2,py+194)],'command',px+pw/2+92,py+179,source='Vorta',target="Jem'Hadar",kind='command')
    p.pill("JEM'HADAR",px+14,py+199,pw-28,p.COLORS['Dominion'])
    py=p.paragraph('A ruling people, administrators and soldiers. Cardassia and the Breen join as wartime political allies; they are not these engineered servant species. [16]',px+15,py+274,pw-30,18,fill=p.MUTED)
    bottom=max(bottom,py)
    p.regions.append(dict(id='main',y=y,h=bottom-y))
    y=bottom+29
    p.regions.append(dict(id='dominion-war',y=y,h=390))
    y=p.war_network(y)
    y=p.section(y,'32','AFTER THE BURN: A GALAXY REASSEMBLED','26TH-32ND CENTURIES',
                'Temporal conflicts, political fragmentation and renewed contact. Exact dates remain approximate where the screen record is unsettled.')
    future_y=y
    y=p.compact_cards(y,data['future'],6,['Other','Federation','Federation','Klingon','Romulan','Federation','Andorian','Other','Federation','Breen','Klingon','Federation'])
    p.regions.append(dict(id='future',y=future_y,h=y-future_y))
    p.line(p.M,y,p.W-p.M,y,p.INK,2)
    p.text('SCOPE & SOURCES',p.M,y+37,29,'display')
    p.paragraph(f'{p.TOTAL} selected historical entries, including eight alternate or conditional histories. Wars, raids, political changes and disasters are identified separately. c. means approximate; revised dates remain visible. Every entry names its on-screen anchor and a numbered source. Select an entry in the viewer for its source link. This chart does not catalog every species or armed encounter.',p.M+265,y+32,2095,18,fill=p.MUTED)
    p.paragraph('Original fan reference chart · Compiled 12 September 2026. Sources: StarTrek.com and Memory Alpha\'s episode-cited screen-history sections. Design study using usefulcharts-style; independent of UsefulCharts and the Star Trek rights holders.',p.W-1035,y+32,965,18,fill=p.MUTED)
    p.export(y+137)

if __name__=='__main__':main()
