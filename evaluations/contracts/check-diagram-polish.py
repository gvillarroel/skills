#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independent semantic/output gates for the composition polish cohort."""

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path


CASES = {
    "contract": {"canvas":(1000,560,1000,14),"panels":2,"colors":{"source":"#276bc8","review":"#9e1b32"},"terms":["source","review"],"links":2},
    "naturalistic": {"canvas":(1200,800,1000,14),"panels":3,"colors":{"photos":"#276bc8","audio":"#9e1b32","video":"#24745a"},"terms":["photo","audio","video","jpeg","png","wav","mp4","date","session","project"],"links":3},
    "generalization": {"canvas":(900,1040,900,15),"panels":3,"colors":{"radio":"#276bc8","optical":"#9e1b32"},"terms":["radio","optical","archive","observatory","spectr","image","fits","tiff"],"links":2},
    "boundary": {"canvas":(1000,460,1000,14),"panels":2,"colors":{"source":"#276bc8"},"terms":["source","shared reference"],"links":1},
}


def check(run, case, audit_path):
    out=run/'workspace'/'out'
    spec=json.loads((out/'plan.json').read_text(encoding='utf-8-sig'))
    report=json.loads((out/'report.json').read_text(encoding='utf-8-sig'))
    audit=json.loads(audit_path.read_text(encoding='utf-8-sig'))
    raw=(out/'figure.svg').read_bytes();root=ET.fromstring(raw)
    expected=CASES[case];findings=[]

    def need(condition,message):
        if not condition:findings.append(message)

    need(tuple(spec['canvas'][k] for k in ('width','height','displayWidth','minTextPx'))==expected['canvas'], 'Canvas, displayed width, or typography requirement changed')
    need(len(spec['panels'])==expected['panels'],'Wrong panel count')
    need(audit.get('ok') is True,'Independent browser findings remain')
    need(audit.get('sourceSha256')==hashlib.sha256(raw).hexdigest(),'Independent audit does not match final figure')
    quality=audit.get('visualQuality',{})
    need(len(quality.get('contacts',[]))>=2*expected['links'],'Missing verified terminal contacts')
    need(all(c['error']<=1.5 and c['outward']>0 for c in quality.get('contacts',[])), 'Invalid terminal geometry')
    internal=quality.get('internalContacts',[])
    need(all(c['error']<=1.5 and c['outside'] for c in internal),'Invalid source-internal terminal geometry')
    if case=='naturalistic':need(len(internal)>=6,'Three collection-to-Archive relationships need both real terminal contacts')
    # The brief asks for two station-to-Archive connections and a separate
    # containment view; it does not require duplicating edges inside that view.
    if case=='generalization':need(len(internal)>=4,'Both station-to-Archive relationships need real terminal contacts')
    if case=='boundary':need(len(internal)>=1 and len(quality.get('openTerminals',[]))==1,'The supplied upstream wire needs one named open end and one real Source contact')
    need(all(c['ratio']+1e-9>=c['threshold'] for c in quality.get('contrasts',[])), 'Insufficient ordinary-label contrast')
    visible=' '.join(''.join(e.itertext()) for e in root.iter() if e.tag.endswith('}text')).lower()
    for term in expected['terms']:need(term in visible,f'Missing visible supplied fact: {term}')

    concept_ids={}
    for term,color in expected['colors'].items():
        concepts=[c for c in spec.get('concepts',[]) if term in (c['label']+' '+c['id']).lower()]
        need(len(concepts)==1,f'Expected one canonical concept for {term}')
        if len(concepts)==1:
            cid=concepts[0]['id'];concept_ids[cid]=term
            need(concepts[0].get('color','').lower()==color,f'Palette changed for {term}')
            need(audit.get('semanticColors',{}).get('colors',{}).get(cid)==color,f'Actual palette registry differs for {term}')

    nodes={};ellipse_concepts=set()
    for panel in spec['panels']:
        path=(out/panel['source']).resolve()
        need(path.is_relative_to((out/'panels').resolve()),'Panel source outside required folder')
        source=ET.fromstring(path.read_bytes())
        item=next((p for p in report['panels'] if p['id']==panel['id']),{})
        need(item.get('sourceSha256')==hashlib.sha256(path.read_bytes()).hexdigest(),'Source hash mismatch')
        for e in source.iter():
            if e.get('data-node-id'):
                cid=e.get('data-concept-id') or e.get('data-color-concept')
                nodes[panel['id']+'.'+e.get('data-node-id')]=cid
                if e.tag.endswith('}ellipse') and cid:ellipse_concepts.add(cid)
    satisfied=set()
    for link in report.get('links',[]):
        need(not link.get('directed',False),'Identity link invents direction')
        bindings=link.get('endpoints',[])
        need(len(bindings)==2 and all(bindings),'Unbound endpoint')
        if len(bindings)==2 and all(bindings):
            meanings=[nodes.get(b['object']) for b in bindings]
            if meanings[0] in concept_ids:
                need(meanings[0]==meanings[1],f'Identity link joins different concepts: {link["id"]}')
                if meanings[0]==meanings[1]:satisfied.add(meanings[0])
    need(set(concept_ids)<=satisfied,'A requested cross-view identity connection is missing or unverified')
    if case=='generalization':need(set(concept_ids)<=ellipse_concepts,'Both stations require actual elliptical enclosures')
    if case=='boundary':need(quality.get('connectorCount',0)>=2,'The supplied upstream connection was dropped')
    result={'runId':run.name,'case':case,'ok':not findings,'findings':findings,'sourceSha256':hashlib.sha256(raw).hexdigest(),
            'contactCount':len(quality.get('contacts',[])),'connectorCount':quality.get('connectorCount'),
            'internalContactCount':len(internal),'openTerminalCount':len(quality.get('openTerminals',[])),
            'minimumTextPx':audit.get('minimumObservedPx'),'minimumContrast':min((c['ratio'] for c in quality.get('contrasts',[])),default=None),
            'verifiedConceptLinks':sorted(satisfied),'manualVisualReviewRequired':True}
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('run',type=Path);ap.add_argument('--case',choices=CASES,required=True)
    ap.add_argument('--audit',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();result=check(args.run,args.case,args.audit)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result));return 0 if result['ok'] else 1


if __name__=='__main__':raise SystemExit(main())
