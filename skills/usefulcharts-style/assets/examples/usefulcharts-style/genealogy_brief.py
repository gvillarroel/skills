#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["osqp>=1,<2", "numpy>=2,<3", "scipy>=1.14,<2"]
# ///
"""Synthetic kinship records with expanding, ending, and intermarrying houses."""

from collections import Counter


def build_genealogy(base):
    from render_chart import text_width
    from space_family_branches import space_branches
    houses=['Alder','Bayeux','Corven','Daleshire','Everen','Falken','Rosene']
    realms=['the Alder March','Bayeux','the Corven Coast','Daleshire','the Everen Isles','Falken','Rosene']
    d=base('aurelian-families','DYNASTIES OF THE AURELIAN COAST','genealogy',[f'House {h}' for h in houses])
    d.update(pattern_id='usefulcharts-dynastic-genealogy',layout='cohorts',cohort_top=208,cohort_bottom=2545,cohort_gap=18,partner_gap=20,cohort_weights={str(r):1.65 for r in range(1,6)},font_size=10.6,
        subtitle='A founding family, seven houses, and the marriages that joined their branches',
        reading_note='Double lines: partners. Descent starts at the union; dotted descent is uncertain. r. marks a reign; other intervals are lifespans. Vertical spacing is schematic.',
        source_note='Original synthetic genealogy · All names, dates, titles, and relationships are invented. Public-domain portraits are decorative art samples, not likenesses.')
    male=['Adrian','Edmund','Hugh','Robert','Philip','Louis','Henri','Conrad','Otto','Frederick','Alaric','Baldwin','Roland','Victor','Charles','Leo','Martin','Richard','Stephen','William','Edward','Francis','George','Albert','Julian','Henry','Arthur','Felix']
    female=['Adele','Beatrice','Eleanor','Matilda','Isabel','Margaret','Alice','Joanna','Agnes','Emma','Sofia','Cecilia','Anne','Helena','Louise','Mary','Clara','Elise','Irene','Diana','Vera','Rose','Ada','Eve']
    male_art=[862,15708,24684,864,111317,95998,89043,16367]
    female_art=[87760,78591,11390,866,105945,75374,105600,31233]
    counts=[1,2,4,6,7,8,7,8,6,4,5,7,8,9,7,5,4,6,8,9,7,6,8,6,4,5,8,9,7,8,6,7,9,7,5,4,7,8,6,7,6]
    previous=[];house_counter=0;numbering=Counter();art_counter=0
    for row,count in enumerate(counts):
        # These declared synthetic birth counts are the topology. Layout never
        # invents or removes relatives to satisfy a desired silhouette.
        births=[1]*len(previous)
        if previous:
            distribution=Counter(p['house'] for p in previous)
            if row>5 and len(previous)==count and max(distribution.values())>1:
                ending=next(i for i,p in enumerate(previous) if distribution[p['house']]>1)
                births[ending]=0
            while sum(births)<count:
                candidates=[i for i,n in enumerate(births) if n<2]
                represented=Counter(previous[i]['house'] if k==0 else previous[i]['spouse_house'] for i,n in enumerate(births) for k in range(n))
                chosen=min(candidates,key=lambda i:(represented[previous[i]['house'] if births[i]==0 else previous[i]['spouse_house']],(i+row)%len(previous)))
                births[chosen]+=1
            while sum(births)>count:
                candidates=[i for i,n in enumerate(births) if n]
                represented=Counter(previous[i]['house'] if k==0 else previous[i]['spouse_house'] for i,n in enumerate(births) for k in range(n))
                chosen=max(candidates,key=lambda i:(represented[previous[i]['house'] if births[i]==1 else previous[i]['spouse_house']],(i+row)%len(previous)))
                births[chosen]-=1
        ancestry=[(i,child) for i,n in enumerate(births) for child in range(n)] if previous else [(None,0)]
        current=[]
        for column,(parent,child_order) in enumerate(ancestry):
            group=previous[parent]['house'] if parent is not None else 0
            founded=child_order>0 and house_counter<6
            if founded:house_counter+=1;group=house_counter
            elif child_order>0:group=previous[parent]['spouse_house']
            partner_parent=None
            if parent is not None and row>4 and row%3==1 and column in (1,count-2):
                anticipated_birth=previous[parent]['married']+2+child_order*4
                choices=[i for i in range(len(previous)) if i!=parent and abs(previous[i]['married']+4-anticipated_birth)<=12]
                if choices:partner_parent=max(choices,key=lambda i:abs(i-parent)) if row in (10,19,28,37) and column==1 else min(choices,key=lambda i:abs(i-parent))
            # Records are generated before placement. Births follow a declared
            # parental marriage; accession follows adulthood and succession.
            # Different reign lengths are consequences of those life records.
            birth=824 if parent is None else previous[parent]['married']+2+child_order*4
            spouse_birth=previous[partner_parent]['married']+4 if partner_parent is not None else birth+[3,-2,1,-4,4,0,-1][(row+column)%7]
            married=max(birth,spouse_birth)+[21,24,20,23,22,25][(row+column)%6]
            accession=858 if parent is None else max(birth+19,previous[parent]['died'] if child_order==0 else birth+28)
            died=max(accession+5,married+12,birth+[65,51,74,46,62,57,69,43,71,54,66][(row*3+column)%11])
            spouse_died=max(married+12,spouse_birth+[61,73,52,68,47,64,76,56][(row+column*3)%8])
            woman=(row*3+column)%9 in (2,5)
            name=(female if woman else male)[(row+column*5)%len(female if woman else male)]
            if row==0:name='Aurelian'
            numbering[(group,name)]+=1
            roman=['','I','II','III','IV','V','VI','VII','VIII','IX','X'][numbering[(group,name)]]
            person=f'person-{row}-{column}';spouse=f'consort-{row}-{column}';uid=f'marriage-{row}-{column}'
            # Portraits identify selected reigns and branch founders. Connecting
            # ancestors and consorts use deliberately subordinate typography.
            connecting=(row+column*2)%7==4 and not founded and row>2
            landmark=row==0 or founded or (row in (11,18,26,33,39) and column in (1,count-2))
            style='plain' if connecting else 'card'
            title='Lady' if woman else 'Lord'
            details=f'r. {accession}–{died}' if not connecting else f'{birth}–{died}'
            n=dict(id=person,label=f'{name} {roman}',detail=details,birth=birth,death=died,reign_start=None if connecting else accession,group=f'g{group}',house=houses[group],realm=realms[group],role='connecting ancestor' if connecting else 'ruler',row=row,width=75 if connecting else 80,style=style,size=10.6)
            if landmark:
                n.update(icon=f'museum-{(female_art if woman else male_art)[art_counter%8]}',icon_width=27,width=107,style='emblem',role='house founder' if founded else 'landmark ruler')
                art_counter+=1
            if row==0:n.update(label='Aurelian I',detail=f'Founder · r. 858–{died}',width=133,size=13.5,icon_width=36,style='hero')
            partner_name=(male if woman else female)[(row*7+column*3+2)%len(male if woman else female)]
            # Selected spouses have explicitly recorded ancestry in another
            # branch; their birth-house color therefore differs from the ruler.
            spouse_group=previous[partner_parent]['house'] if partner_parent is not None else (group+1)%7 if row>4 else group
            partner=dict(id=spouse,label=partner_name,detail=f'{spouse_birth}–{spouse_died}',birth=spouse_birth,death=spouse_died,group=f'g{spouse_group}',row=row,width=max(57,len(partner_name)*5.9+11),style='plain',size=9.6,role='consort')
            d['nodes'].extend([n,partner]);union=dict(id=uid,partners=[person,spouse],children=[]);d['unions'].append(union)
            if parent is not None:
                if row==29 and column==3:d['edges'].append(dict(id='disputed-ancestry',source=previous[parent]['id'],target=person,kind='uncertain'))
                else:previous[parent]['union']['children'].append(person)
            if partner_parent is not None:previous[partner_parent]['union']['children'].append(spouse)
            if founded:
                d['annotations'].append(dict(node=person,dx=0,dy=-35,width=108,label=f'HOUSE OF {houses[group].upper()}',kind='pill',group=f'g{group}',size=9.2))
            current.append(dict(id=uid,house=group,spouse_house=spouse_group,union=union,married=married,died=died))
        # Named relatives whose lines end have their own places in the cohort.
        # They occupy the space released by terminated branches, not extra lanes.
        if row>5 and count<=7:
            for k in range(1 if count==7 else 2):
                parent=(row+k*3)%len(previous);h=previous[parent]['house'];nid=f'collateral-{row}-{k}'
                d['nodes'].append(dict(id=nid,label=(female if k else male)[(row*2+k)%len(female if k else male)],detail=['abbess','d. young','count of Lorn','the chronicler'][row%4],group=f'g{h}',row=row,width=65,style='plain',size=9.3,role='collateral relative'))
                previous[parent]['union']['children'].append(nid)
        previous=current
    for row,column,offset,seat in [(9,0,350,'Lorn'),(16,2,330,'Whitehaven'),(24,3,340,'Westmere'),(35,0,-185,'Dunport')]:
        node=f'person-{row}-{column}'
        person=next(n for n in d['nodes'] if n['id']==node);person['court']=seat
        d['annotations'].append(dict(node=node,dx=offset,dy=0,width=148,label=f'{person["house"].upper()} OF {seat.upper()}',kind='pill',group=person['group'],size=9.5))
    d['annotations'].extend([
        dict(node='person-0-0',dx=-270,dy=3,width=158,label='The coastal\nfounding family',kind='heading',icon='shield',group='g0',size=18),
        dict(node='person-0-0',dx=270,dy=3,width=195,label='A thousand years\nof recorded descent',kind='heading',icon='crown',group='g2',size=18)])
    # The source records above determine hierarchy. Compact nameplates and
    # complete date envelopes are composed before local baseline fitting.
    d.update(width=1890,height=2835,cohort_top=204.75,cohort_bottom=2719.5,
        cohort_weights={str(row):1.1 for row in range(1,6)},
        cohort_spread={str(row):1+.35*(7-row)/6 for row in range(1,7)})
    for node in d['nodes']:
        if node.get('style')=='plain':continue
        node.update(detail_position='outside',size=13.5 if node['row']==0 else 11.8,detail_size=9.1)
        if node.get('icon'):node['icon_width']=36 if node['row']==0 else 33
        if node.get('icon'):
            node['size']=15.5 if node['row']==0 else 13.3
            node['icon_width']=52 if node['row']==0 else 46
        node['width']=max(58,text_width(node['label'],node['size'],True)+(16 if node.get('icon') else 14)+node.get('icon_width',0),
            text_width(node.get('detail',''),node['detail_size'])+16)
    for annotation in d['annotations']:
        if annotation.get('kind')=='heading':annotation['dy']=35
    resolved,_=space_branches(d,date_scale=3,local_labels=True)
    # Source-bound territorial orientation points, chosen after whole-page and
    # detail review. They are not additional events or invented relationships.
    landmarks=[('person-6-0',-44,-160),('person-11-1',120,-108),('person-19-3',-128,132),
        ('person-28-2',-228,52),('person-33-1',-212,100),('person-35-1',-208,116),('person-27-7',-32,-132)]
    for variant,(node,dx,dy) in enumerate(landmarks):
        resolved['annotations'].append(dict(kind='landmark',node=node,field='realm',width=112 if variant in (0,5) else 146,size=17,
            icon='heraldry',art_size=32,art_position='above' if variant==0 else 'beside',variant=variant,dx=dx,dy=dy,vertical_radius=170))
    resolved['source_note']+=' Heraldic devices are fictional.'
    return resolved
