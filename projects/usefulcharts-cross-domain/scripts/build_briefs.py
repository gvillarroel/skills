#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Author selected factual inventories before any poster layout decisions."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
BSD_URL = 'https://cgit.freebsd.org/src/tree/share/misc/bsd-family-tree'
MIMO_URL = 'https://biblio.ugent.be/publication/01HN30DTX2BZYYEVXRG7Q7M06Q'

def write(name, data):
    target = ROOT / 'data' / (name + '.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(case=name, nodes=len(data['nodes']), edges=len(data['edges']))))

def bsd():
    rows = [
        ('v1','UNIX V1','1971','research','First Edition'),
        ('v2','UNIX V2','1972','research','Second Edition'),
        ('v3','UNIX V3','1973','research','Pipes enter Research UNIX'),
        ('v4','UNIX V4','1973','research','Rewritten in C'),
        ('v5','UNIX V5','1974','research','Fifth Edition'),
        ('v6','UNIX V6','1975','research','Basis of the first BSD'),
        ('v7','UNIX V7','1979','research','Seventh Edition'),
        ('b1','1BSD','1977–78','berkeley','Tools for PDP-11 UNIX'),
        ('b2','2BSD','1978–79','berkeley','Second Berkeley distribution'),
        ('32v','UNIX/32V','1978–79','research','Research UNIX for the VAX'),
        ('b3','3BSD','1979–80','berkeley','Virtual memory on the VAX'),
        ('b40','4.0BSD','1980','berkeley','VAX distribution'),
        ('b41','4.1BSD','1981','berkeley','VAX distribution'),
        ('b41a','4.1aBSD','1982','berkeley','Networking alpha'),
        ('b41b','4.1bBSD','Undated','berkeley','Internal filesystem version'),
        ('b41c','4.1cBSD','1982','berkeley','IPC beta'),
        ('b42','4.2BSD','1983','berkeley','Berkeley release'),
        ('b43','4.3BSD','1986','berkeley','Berkeley release'),
        ('tahoe','4.3BSD Tahoe','1988','berkeley','Tahoe release'),
        ('net1','NET/1','1988–89','berkeley','Networking distribution'),
        ('reno','4.3BSD Reno','1990','berkeley','Reno release'),
        ('net2','NET/2','1991','berkeley','Networking distribution'),
        ('b44a','4.4BSD Alpha','1992','berkeley','Development release'),
        ('b44','4.4BSD','1993','berkeley','Berkeley release'),
        ('lite','4.4BSD Lite','1994','berkeley','Source for several BSD systems'),
        ('lite2','4.4BSD Lite2','1995','berkeley','Final CSRG distribution'),
        ('386a','386BSD 0.0','1992','386bsd','Early PC release'),
        ('386b','386BSD 0.1','1992','386bsd','PC release'),
        ('386c','386BSD 1.0','1994','386bsd','Later release'),
        ('f1','FreeBSD 1.0','1993','freebsd','First release'),
        ('f11','FreeBSD 1.1','1994','freebsd','Release series'),
        ('f115','FreeBSD 1.1.5','1994','freebsd','Release series'),
        ('f1151','FreeBSD 1.1.5.1','1994','freebsd','Final 1.x release shown'),
        ('f2','FreeBSD 2.0','1994','freebsd','4.4BSD Lite base'),
        ('f205','FreeBSD 2.0.5','1995','freebsd','Release series'),
        ('f21','FreeBSD 2.1','1995','freebsd','Last FreeBSD release shown'),
        ('n08','NetBSD 0.8','1993','netbsd','First release'),
        ('n09','NetBSD 0.9','1993','netbsd','Release series'),
        ('n1','NetBSD 1.0','1994','netbsd','4.4BSD Lite contribution'),
        ('n11','NetBSD 1.1','1995','netbsd','Last NetBSD release shown'),
        ('osalpha','BSD/386 Alpha','1991','bsdi','Commercial BSD branch'),
        ('os033','BSD/386 0.3.3','1992','bsdi','Selected alpha release'),
        ('os094','BSD/386 0.9.4','1992','bsdi','Selected prerelease'),
        ('os1','BSD/386 1.0','1993','bsdi','Commercial release'),
        ('os11','BSD/386 1.1','1994','bsdi','Commercial release'),
        ('os2','BSD/OS 2.0','1995','bsdi','4.4BSD Lite contribution'),
        ('os201','BSD/OS 2.0.1','1995','bsdi','Last BSD/OS release shown'),
    ]
    groups = [('research','Research UNIX','#385E75'),('berkeley','Berkeley / CSRG','#8A4935'),
              ('386bsd','386BSD','#735C85'),('freebsd','FreeBSD','#994851'),
              ('netbsd','NetBSD','#776329'),('bsdi','BSDI','#397465')]
    nodes = [dict(id=i,label=label,date_label=date,group=group,detail=detail,
                  detail_position='outside',source_url=BSD_URL) for i,label,date,group,detail in rows]
    edges=[]
    def chain(ids,kind='branch'):
        for a,b in zip(ids,ids[1:]):edges.append(dict(id=a+'-'+b,source=a,target=b,kind=kind))
    chain(['v1','v2','v3','v4','v5','v6','v7','32v','b3','b40','b41','b41a','b41b','b41c','b42','b43','tahoe','net1','reno','net2','b44a','b44','lite','lite2'])
    chain(['v6','b1','b2','b3'])
    chain(['net2','386a','386b','386c'])
    chain(['386b','f1','f11','f115','f1151'])
    chain(['lite','f2','f205','f21'])
    chain(['net2','n08','n09'])
    chain(['n08','n1','n11'])
    chain(['net2','osalpha','os033','os094','os1','os11','os2','os201'])
    for a,b in [('386b','n08'),('n08','f1'),('lite','n1'),('lite','os2')]:
        edges.append(dict(id=a+'-'+b,source=a,target=b,kind='influence'))
    for n in nodes:
        if n['id'] in ['v6','b3','net2','lite']:n['emphasis']=True
    write('bsd',dict(id='unix-bsd-1971-1995',title='UNIX AND THE BSD FAMILY',design='editorial',mode='lineage',layout='branches',branch_order='causal',
          groups=[dict(id=i,label=l,color=c) for i,l,c in groups],nodes=nodes,edges=edges,
          source_note='Source: FreeBSD, The UNIX system family tree. Selected Research UNIX and BSD releases through 1995; later histories omitted.',
          reading_note='Schematic descent, not elapsed time. Solid: source lineage; dotted: code contribution. Year ranges retain disputed dates. No date is inferred for 4.1bBSD.'))

def instruments():
    # Classification identifiers and selected labels are facts from MIMO 2011.
    families = [
      ('1','Idiophones','The body vibrates','#8C5533',[
       ('11','Struck bodies'),('111','Direct blows'),('112','Indirect blows'),('12','Plucked tongues'),('121','In a frame'),('122','On a board or comb'),('13','Friction bodies'),('131','Friction sticks'),('132','Friction plaques'),('133','Friction vessels'),('14','Blown bodies'),('141','Blown sticks'),('142','Blown plaques'),('15','Metal sheets'),('16','Flexed diaphragms')]),
      ('2','Membranophones','A stretched skin vibrates','#9A4A52',[
       ('21','Struck drums'),('211','Directly struck'),('212','Rattle drums'),('23','Friction drums'),('231','With a stick'),('232','With a cord'),('233','By hand'),('24','Singing membranes'),('241','Free kazoos'),('242','Tube or vessel kazoos')]),
      ('3','Chordophones','Tensioned strings vibrate','#426C56',[
       ('31','Simple / zithers'),('311','Bar zithers'),('312','Tube zithers'),('313','Raft zithers'),('314','Board zithers'),('315','Trough zithers'),('316','Frame zithers'),('32','Composite'),('321','Lutes'),('322','Harps'),('323','Spike harps'),('324','Tanged harps'),('33','Variable tension'),('331','Loose string to drumhead'),('332','String from neck to head')]),
      ('4','Aerophones','Air produces the sound','#386E86',[
       ('41','Free air'),('411','Displacement'),('412','Interrupted flow'),('413','Plosive'),('42','Wind instruments'),('420','Non-flute edge tones'),('421','Flutes'),('422','Reed pipes'),('423','Lip reeds'),('424','Membranopipes')]),
      ('5','Electrophones','Signals feed a loudspeaker','#715487',[
       ('51','Electro-acoustic'),('511','Vibrating bodies'),('512','Membranes'),('513','Strings'),('514','Air mechanisms'),('515','Transducers'),('52','Electromechanical'),('521','Tone wheels'),('522','Photoelectric'),('523','Record / playback'),('524','Mechanical samplers'),('525','Sound processing'),('53','Analogue electronics'),('54','Digital electronics'),('55','Analogue / digital hybrids'),('56','Software')]),
    ]
    groups=[];nodes=[];edges=[]
    for code,name,detail,color,children in families:
        groups.append(dict(id=code,label=name,color=color))
        for sub,label in [(code,name)]+children:
            nodes.append(dict(id=sub,label=label,date_label=sub,group=code,detail=detail if sub==code else '',
                              detail_position='outside',source_url=MIMO_URL,emphasis=sub==code))
            if sub!=code:edges.append(dict(id=sub[:-1]+'-'+sub,source=sub[:-1],target=sub,kind='branch'))
    write('instruments',dict(id='instruments-by-sound',title='HOW INSTRUMENTS MAKE SOUND',design='editorial',mode='lineage',layout='branches',branch_order='causal',
        groups=groups,nodes=nodes,edges=edges,
        source_note='Source: MIMO Consortium, revised Hornbostel–Sachs classification (2011). Selected categories; deeper subdivisions omitted. Labels abbreviated.',
        reading_note='Codes identify classes, not dates or rank. Links mean contains. Unmodified acoustic instruments with added microphones or pickups remain in families 1–4.'))

if __name__=='__main__':
    bsd();instruments()
