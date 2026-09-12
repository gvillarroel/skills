#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Check visible branch captions against their independent editable source."""

import re

BROWSER_AUDIT = r"""
  const branch_captions=[...svg.querySelectorAll('[data-annotation-id]')]
    .filter(el=>['pill','heading'].includes(el.dataset.annotationKind)).map(el=>{
      const body=el.querySelector(':scope > rect'),box=bounds(body||el);
      const kind=el.dataset.annotationKind;
      const texts=[...el.querySelectorAll(':scope > text')].map(t=>{
        const origin=textOrigin(t),matrix=svg.getScreenCTM().inverse().multiply(t.getScreenCTM());
        return {text:t.textContent,origin:{x:origin.x,y:origin.y},
          font:parseFloat(getComputedStyle(t).fontSize)*Math.hypot(matrix.a,matrix.b),...painted(t)};
      });
      const hits=[];
      for(const path of svg.querySelectorAll('[data-edge-id]')){
        const length=path.getTotalLength(),matrix=svg.getScreenCTM().inverse().multiply(path.getScreenCTM());
        for(let at=0;at<=length;at+=2){
          const p=path.getPointAtLength(at),v=new DOMPoint(p.x,p.y).matrixTransform(matrix);
          if(v.x>box.x+.5&&v.x<box.x+box.w-.5&&v.y>box.y+.5&&v.y<box.y+box.h-.5){hits.push({id:path.dataset.edgeId,target:path.dataset.target});break;}
        }
      }
      return {id:el.dataset.annotationId,kind,box,texts,hits,
        outline:body?{stroke:getComputedStyle(body).stroke,...painted(body)}:null,
        artwork:[...el.querySelectorAll(':scope > [data-artwork]')].map(a=>({kind:a.dataset.artwork,...painted(a)}))};
    });
"""


def check_captions(report, source):
    if not source.get('_branch_annotation_envelopes'):
        return
    findings = report['findings']
    expected = {f'annotation-{i}': a for i, a in enumerate(source.get('annotations', [])) if a.get('kind') in ('pill', 'heading')}
    actual = {a['id']: a for a in report.get('branch_captions', [])}
    if sorted(expected) != sorted(actual):
        findings.append(dict(type='source-branch-caption-inventory'))
    boxes = {n['id']: n['box'] for n in report['nodes']}
    colors = {g['id']: g['color'] for g in source['groups']}
    for aid, annotation in expected.items():
        drawn = actual.get(aid)
        if not drawn:
            continue
        def fail(kind):
            findings.append(dict(type='source-branch-caption-' + kind, id=aid))
        texts = drawn['texts']
        if drawn['kind'] != annotation['kind'] or ' '.join(' '.join(t['text'] for t in texts).split()) != ' '.join(annotation['label'].split()):
            fail('label')
        size = annotation.get('size', 13)
        if not texts or any(abs(t['font'] - size) > .05 or not t['visible'] or t['opacity'] < .99 for t in texts):
            fail('type-or-visibility')
        box = boxes.get(annotation['node'])
        if box:
            x = box['x'] + box['w'] / 2 + annotation.get('dx', 0)
            y = box['y'] + box['h'] / 2 + annotation.get('dy', 0)
            height = len(texts) * size * 1.12 + 7
            if any(abs(t['origin']['x'] - x) > .1 or abs(t['origin']['y'] - (y - height / 2 + size + i * size * 1.12)) > .1 for i, t in enumerate(texts)):
                fail('anchor')
        if annotation['kind'] == 'pill':
            outline = drawn['outline']
            if not outline or not outline['visible'] or outline['opacity'] < .99 or abs(outline['box']['w'] - annotation.get('width', 130)) > .1:
                fail('panel')
            if outline and annotation.get('group'):
                color = colors[annotation['group']]
                rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                if tuple(int(v) for v in re.findall(r'\d+', outline['stroke'])) != rgb:
                    fail('color')
        if annotation.get('icon'):
            if not drawn['artwork'] or any(not art['visible'] or art['opacity'] < .99 for art in drawn['artwork']):
                fail('artwork')
        for hit in drawn['hits']:
            if annotation['kind'] != 'pill' or hit['target'] != annotation['node']:
                findings.append(dict(type='branch-caption-unrelated-path', id=aid, edge=hit['id']))


if __name__ == '__main__':
    print('Use audit_chart.py with --source to verify resolved branch captions.')
