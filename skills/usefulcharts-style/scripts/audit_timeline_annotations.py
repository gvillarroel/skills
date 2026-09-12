#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Compare browser-observed event art and text against the supplied source."""


def check_annotations(report,data,lane_origins,time_y):
    """Independently verify source identity, placement, dimensions and date anchors."""
    normalize=lambda value:' '.join(str(value).split())
    def finding(kind,eid):report['findings'].append(dict(type=kind,id=eid))
    start,end=data['time']['start'],data['time']['end'];y0,y1=time_y
    for index,event in enumerate(data.get('events',[])):
        eid=event.get('id',f'event-{index}')
        texts=[t for t in report['texts'] if t.get('event')==eid]
        arts=[a for a in report.get('illustrations',[]) if a['event']==eid]
        expected_count=1 if event.get('icon') else 0
        if len(arts)!=expected_count:finding('source-event-art-inventory',eid)
        if not texts:continue
        position=event.get('art_position','below');side=position in ('left','right')
        weights={lane['id']:lane.get('weight',1) for lane in data['lanes']}
        width=event.get('width',(report['canvas'][0]-175)*weights[event['lane']]/sum(weights.values())-78)
        aw=event.get('art_width',event.get('art_size',56));ah=event.get('art_height',event.get('art_size',56))
        x=lane_origins[event['lane']]+event.get('offset',64)
        year_y=y0+(event['year']-start)/(end-start)*(y1-y0)
        tx=x+aw+8 if event.get('icon') and position=='left' else x
        heading=event.get('size',10.5);detail=event.get('detail_size',heading*.88)
        has_roles=all(t.get('role') in ('heading','detail') for t in texts)
        if any(t.get('role') for t in texts) and not has_roles:finding('source-event-text-role',eid)
        if has_roles:
            for role,field in (('heading','label'),('detail','detail')):
                actual=normalize(' '.join(t['text'] for t in texts if t['role']==role))
                if actual!=normalize(event.get(field,'')):finding('source-event-text-content',eid)
        elif normalize(' '.join(t['text'] for t in texts))!=normalize(event['label']+' '+event.get('detail','')):
            finding('source-event-text-content',eid)
        y=year_y
        for text in texts:
            font=heading if text.get('role')=='heading' else detail if text.get('role')=='detail' else text['font']
            if abs(text['font']-font)>.02:finding('source-event-text-size',eid)
            origin=text.get('origin',{})
            if abs(origin.get('x',tx)-tx)>.12 or abs(origin.get('y',y+font)-y-font)>.12:
                finding('source-event-text-position',eid)
            y+=font*1.18
        if not arts or not event.get('icon'):continue
        art=arts[0]
        if event['icon'].startswith('illustration-'):
            if art.get('illustration_id')!=event['icon'][13:] or art.get('use_href')!='#asset-'+event['icon']:
                finding('source-event-art-identity',eid)
            if not art.get('visible') or art.get('opacity',0)<.99:finding('source-event-art-visibility',eid)
            ax=x if position=='left' else x+width-aw if position=='right' else x+(width-aw)/2
            ay=year_y if side else year_y-ah-5 if position=='above' else y+5
            expected=dict(x=ax,y=ay,w=aw,h=ah);actual=art.get('viewport')
            if not actual or any(abs(actual[key]-value)>.12 for key,value in expected.items()):
                finding('source-event-art-geometry',eid)
