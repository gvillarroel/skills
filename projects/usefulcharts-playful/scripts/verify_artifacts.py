#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2", "pypdf>=5,<7"]
# ///
"""Independently compare source records, printed fields, calendar marks and exports."""
from pathlib import Path
import hashlib
import io
import json
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pypdf import PdfReader, PdfWriter
from pypdf.generic import ArrayObject, FloatObject, NameObject, NullObject, RectangleObject
from artwork import ROOT,REPO,tag,render
sys.path.insert(0,str(REPO/'skills/usefulcharts-style/scripts'))
from audit_panel_poster import audit

BASE={
 'instruments':REPO/'projects/usefulcharts-cross-domain/artifacts/revision-2/instruments/poster.svg',
 'bsd':REPO/'projects/usefulcharts-cross-domain/artifacts/revision-2/bsd/poster.svg',
 'mars':REPO/'projects/usefulcharts-cross-domain/artifacts/revision-2/mars/poster.svg',
 'civilizations':REPO/'projects/star-trek-canonical-timeline/artifacts/svgs/star-trek-timeline.svg',
 'starships':REPO/'projects/star-trek-starships/artifacts/flow-edition/svgs/star-trek-starships.svg',
}
DETAIL={'instruments':(32,215,1510,1100),'bsd':(32,890,1510,1120),'mars':(1560,270,1600,820),'civilizations':(55,740,1430,1050),'starships':(70,3140,1090,1900)}

def source_records(source):return source.get('nodes') or source.get('ships') or [n for k in ('events','origins','future','branches') for n in source[k]]
def record_texts(root,case):
    result={}
    for e in root.iter(tag('g')):
        identifier=e.get('data-record-id')
        if case=='civilizations' and 'record' in e.get('class','').split():identifier=e.get('id')
        if case=='starships' and e.get('data-fragment'):identifier=e.get('data-fragment')
        if identifier:result[identifier]=[' '.join(''.join(t.itertext()).split()) for t in e.iter(tag('text'))]
    return result
def date_marks(root,case):
    if case=='mars':return [dict(e.attrib) for e in root.iter() if e.get('data-date-owner') or e.get('data-span-owner')]
    return [dict(e.attrib) for e in root.iter() if e.get('data-year') or e.get('data-start') or e.get('data-end') or e.get('data-kind')]

def main():
    output=ROOT/'artifacts/reviews';output.mkdir(parents=True,exist_ok=True)
    selected=set(sys.argv[1:]) or set(BASE)
    results=[r for r in json.loads((output/'independent-checks.json').read_text()) if r['case'] not in selected] if (output/'independent-checks.json').exists() else []
    for case,base_path in BASE.items():
        if case not in selected:continue
        out=ROOT/'artifacts/revision-2'/case;before=ET.parse(base_path).getroot();after=ET.parse(out/'poster.svg').getroot();source=json.loads((out/'source.json').read_text(encoding='utf-8'))
        issues=[];records=source_records(source)
        if record_texts(before,case)!=record_texts(after,case):issues.append('Printed record fields changed')
        if case in ['bsd','instruments','mars']:
            expected=json.loads((base_path.parent/'source.json').read_text(encoding='utf-8'))
            report=audit(out/'poster.svg',out/'source.json')
            (out/'browser.json').write_text(json.dumps(report,indent=2)+'\n')
            if report['status']!='pass':issues.extend(report['findings'])
        else:
            original_source=REPO/('projects/star-trek-starships/data/ships.json' if case=='starships' else 'projects/star-trek-canonical-timeline/data/timeline.json')
            expected=json.loads(original_source.read_text(encoding='utf-8'))
        if source!=expected:issues.append('Source inventory changed')
        if case in ['mars','starships'] and date_marks(before,case)!=date_marks(after,case):issues.append('Calendar marker geometry changed')
        render(out,DETAIL[case]);render_info=json.loads((out/'render.json').read_text())
        issues.extend(render_info['image_text_overlaps']);issues.extend(render_info['errors'])
        w,h=render_info['canvas']
        for t in render_info['texts']:
            if t['x']<-.6 or t['y']<-.6 or t['x']+t['w']>w+.6 or t['y']+t['h']>h+.6:issues.append(dict(type='outside-canvas',text=t['text']))
        # Browser SVG-to-PDF exports lose script-only source links. Restore one
        # explicit source link per selected record and real in-page references.
        if case in ['bsd','instruments','mars']:record_boxes={b['id']:b['box'] for b in report['records']}
        else:record_boxes={b['id']:b for b in json.loads((out/'layout.json').read_text())['boxes']}
        writer=PdfWriter();writer.append(PdfReader(out/'poster.pdf'))
        for annotation in writer.pages[0].get('/Annots',[]):
            action=annotation.get_object().get('/A');uri=str(action.get('/URI','')) if action else ''
            if 'about:blank#record-' in uri:
                target=uri.split('#record-',1)[1]
                if target in record_boxes:
                    b=record_boxes[target];action.clear();action[NameObject('/S')]=NameObject('/GoTo')
                    action[NameObject('/D')]=ArrayObject([writer.pages[0].indirect_reference,NameObject('/XYZ'),FloatObject(b['x']*.75),FloatObject((h-b['y'])*.75),NullObject()])
        source_links=[]
        for n in records:
            ref=source.get('sources',{}).get(n.get('source'),{})
            url=n.get('source_url') or ref.get('url');b=record_boxes.get(n['id'])
            if not url or b is None:issues.append(dict(type='missing-pdf-source-link',record=n['id']));continue
            writer.add_uri(0,url,RectangleObject([b['x']*.75,(h-b['y']-b['h'])*.75,(b['x']+b['w'])*.75,(h-b['y'])*.75]),border=[0,0,0]);source_links.append(n['id'])
        buffer=io.BytesIO();writer.write(buffer);(out/'poster.pdf').write_bytes(buffer.getvalue())
        pdf=PdfReader(out/'poster.pdf');page=pdf.pages[0]
        if len(pdf.pages)!=1:issues.append('PDF page count')
        if abs(float(page.mediabox.width)-w*.75)>1 or abs(float(page.mediabox.height)-h*.75)>1:issues.append('PDF page size')
        text=' '.join(unicodedata.normalize('NFKC',page.extract_text()).split())
        labels=[n.get('label',n.get('name','')) for n in records]
        missing=[label for label in labels if ' '.join(label.split()) not in text]
        if missing:issues.append(dict(type='pdf-label-extraction',labels=missing))
        subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','1900','-png',str(out/'poster.pdf'),str(out/'pdf-preview')],check=True,capture_output=True)
        previous_area=float(before.get('width'))*float(before.get('height'))
        info=dict(case=case,status='pass' if not issues else 'fail',records=len(records),printed_fragments=len(record_texts(after,case)),canvas=[w,h],original_canvas=[float(before.get('width')),float(before.get('height'))],area_change_percent=round((w*h/previous_area-1)*100,2),source_preserved=source==expected,printed_record_fields_preserved=record_texts(before,case)==record_texts(after,case),calendar_marks_preserved=case not in ['mars','starships'] or date_marks(before,case)==date_marks(after,case),illustration_placements=len(json.loads((out/'art-map.json').read_text())),pdf_pages=len(pdf.pages),pdf_source_links=len(source_links),findings=issues,reference_density_status='pending',sha256={name:hashlib.sha256((out/name).read_bytes()).hexdigest() for name in ['poster.svg','poster.png','detail.png','poster.pdf','source.json']})
        results.append(info);print(json.dumps({k:info[k] for k in ['case','status','records','area_change_percent','findings']}))
    (output/'independent-checks.json').write_text(json.dumps(results,indent=2)+'\n')
    return any(r['status']!='pass' for r in results)
if __name__=='__main__':raise SystemExit(main())
