#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inspect actual contextual inset text, counted marks, artwork and placement."""

import re
import base64
from pathlib import Path

BROWSER_AUDIT = r'''
  const context_insets=[...svg.querySelectorAll('[data-inset-id]')].map(el=>{
    const box=bounds(el.querySelector('[data-inset-box]'));
    const words=role=>[...el.querySelectorAll(`[data-inset-role="${role}"]`)].map(t=>({text:t.textContent,font:parseFloat(getComputedStyle(t).fontSize),...painted(t)}));
    const art=el.querySelector('[data-inset-art] [data-artwork]');
    const result={id:el.dataset.insetId,kind:el.dataset.insetKind,box,title:words('title'),story:words('story'),
      art:art?{kind:art.dataset.artwork,illustration_id:art.dataset.illustrationId||null,use_href:art.querySelector('use')?.getAttribute('href')||null,image_href:art.dataset.artwork==='public-domain-museum-image'?art.querySelector('image')?.getAttribute('href'):null,viewport:viewport(art),...painted(art)}:null,
      groups:[...el.querySelectorAll('[data-count-group]')].map(group=>({id:group.dataset.countGroup,
        label:[...group.querySelectorAll('[data-inset-role="group-label"]')].map(t=>t.textContent).join(' '),
        label_fonts:[...group.querySelectorAll('[data-inset-role="group-label"],[data-inset-role="count"]')].map(t=>parseFloat(getComputedStyle(t).fontSize)),
        total:group.querySelector('[data-inset-role="count"]')?.textContent,
        marks:[...group.querySelectorAll('[data-count-mark]')].map(p=>painted(p))}))};
    if(!contained(box,{x:48,y:130,w:view.width-96,h:view.height-215},.5))findings.push({type:'inset-outside-paper',id:result.id});
    for(const node of nodes)if(intersect(box,node.box,.5))findings.push({type:'inset-node-collision',id:result.id,node:node.id});
    for(const child of el.querySelectorAll('text,[data-artwork],[data-count-mark]')){
      const state=painted(child),b=viewport(child)||state.box;
      if(!contained(b,box,.5))findings.push({type:'inset-content-overflow',id:result.id});
      if(!state.visible||state.opacity<.98||state.box.w<.1||state.box.h<.1)findings.push({type:'inset-hidden-content',id:result.id});
    }
    for(const label of el.querySelectorAll('text'))if(art&&intersect(bounds(label),viewport(art)||bounds(art),.5))findings.push({type:'inset-art-text-collision',id:result.id});
    const marks=result.groups.flatMap(group=>group.marks);
    for(let i=0;i<marks.length;i++)for(let j=i+1;j<marks.length;j++)if(intersect(marks[i].box,marks[j].box,.3))findings.push({type:'inset-mark-overlap',id:result.id});
    for(const other of svg.querySelectorAll('[data-inset-id],[data-annotation-id]'))if(other!==el&&intersect(box,bounds(other),.5))findings.push({type:'inset-context-collision',id:result.id});
    for(const path of svg.querySelectorAll('[data-edge-id],[data-union-id]')){
      const length=path.getTotalLength(),matrix=svg.getScreenCTM().inverse().multiply(path.getScreenCTM());
      for(let at=0;at<=length;at+=2){
        const point=path.getPointAtLength(at),p=new DOMPoint(point.x,point.y).matrixTransform(matrix);
        if(p.x>box.x&&p.x<box.x+box.w&&p.y>box.y&&p.y<box.y+box.h){findings.push({type:'inset-path-collision',id:result.id,path:path.dataset.edgeId||path.dataset.unionId});break;}
      }
    }
    return result;
  });
'''


def check_insets(report, data):
    expected = {item.get('id', f'inset-{index}'): item for index,item in enumerate(data.get('insets', [])) if item.get('kind') in ('story', 'counts')}
    actual = {item['id']: item for item in report.get('context_insets', [])}
    findings = report['findings']
    if sorted(expected) != sorted(actual):findings.append(dict(type='source-inset-inventory'))
    normalize = lambda text: ' '.join(text.split())
    for iid,item in expected.items():
        if iid not in actual:continue
        drawn = actual[iid]
        if drawn['kind'] != item['kind']:findings.append(dict(type='source-inset-kind', id=iid))
        if any(abs(drawn['box'][key]-value) > .1 for key,value in zip(('x','y','w','h'),item['box'])):
            findings.append(dict(type='source-inset-position', id=iid))
        if normalize(' '.join(t['text'] for t in drawn['title'])) != normalize(item['title']):
            findings.append(dict(type='source-inset-title', id=iid))
        if any(abs(t['font']-item.get('title_size',17)) > .1 for t in drawn['title']):findings.append(dict(type='source-inset-type',id=iid))
        if item['kind'] == 'story':
            if normalize(' '.join(t['text'] for t in drawn['story'])) != normalize(item['text']):findings.append(dict(type='source-inset-prose',id=iid))
            if any(abs(t['font']-item.get('size',14)) > .1 for t in drawn['story']):findings.append(dict(type='source-inset-type',id=iid))
            art = drawn['art'];icon = item.get('icon')
            if bool(art) != bool(icon):findings.append(dict(type='source-inset-art',id=iid))
            elif art:
                kind = 'illustration-'+art['illustration_id'] if art['illustration_id'] else art['kind']
                if icon.startswith(('museum-','object-')):
                    identifier=icon.split('-',1)[1]
                    folder='portraits' if icon.startswith('museum-') else 'objects'
                    file=Path(__file__).resolve().parent.parent/'assets'/folder/(identifier+'.jpg')
                    if identifier.isdigit() and file.is_file():
                        expected_image='data:image/jpeg;base64,'+base64.b64encode(file.read_bytes()).decode('ascii')
                        if art['image_href']!=expected_image:findings.append(dict(type='source-inset-art',id=iid))
                    else:findings.append(dict(type='source-inset-art',id=iid))
                elif kind != icon or (icon.startswith('illustration-') and art['use_href'] != '#asset-'+icon):findings.append(dict(type='source-inset-art',id=iid))
        else:
            groups = {group['id']: group for group in data['groups']}
            selected = item.get('groups', list(groups))
            if [group['id'] for group in drawn['groups']] != selected:findings.append(dict(type='source-inset-groups',id=iid))
            for group in drawn['groups']:
                gid = group['id']
                if gid not in groups:continue
                total = sum(node['group'] == gid for node in data['nodes'])
                if group['total'] != str(total) or len(group['marks']) != total:findings.append(dict(type='source-inset-count',id=iid,group=gid))
                if normalize(group['label']) != normalize(groups[gid]['label']):findings.append(dict(type='source-inset-group-label',id=iid,group=gid))
                if any(abs(size-item.get('label_size',12))>.1 for size in group['label_fonts']):findings.append(dict(type='source-inset-type',id=iid))
                rgb = tuple(int(groups[gid]['color'][i:i+2],16) for i in (1,3,5))
                for mark in group['marks']:
                    values = tuple(int(v) for v in re.findall(r'\d+', mark['fill']))
                    if values != rgb:findings.append(dict(type='source-inset-group-color',id=iid,group=gid));break


if __name__ == '__main__':
    print('Run audit_chart.py with an independent source JSON to inspect contextual insets.')
