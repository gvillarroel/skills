#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Measure source-backed prose and compact institution-count insets."""

import math
from render_chart import attr, fmt, ident, number, require, wrap

CONTEXT_KINDS = {'story', 'counts'}


def inset_content(item, data, *, measure_only=False):
    require(data.get('mode') == 'lineage', 'Story and institution-count insets are for institutional lineages.')
    require(item.get('kind') in CONTEXT_KINDS, 'Unknown contextual inset kind.')
    require(isinstance(item.get('box'), list) and len(item['box']) == 4, 'An inset requires an authored x, y, width and height box.')
    x,y,w,h = [number(value, 'inset box') for value in item['box']]
    require(w >= 150 and h > 0, 'A contextual inset needs a readable positive footprint.')
    title_size = number(item.get('title_size', 17), 'inset title size')
    require(title_size >= 10 and isinstance(item.get('title'), str) and item['title'].strip(), 'A contextual inset requires a readable title.')
    title = wrap(item['title'], w-10, title_size, True)
    title_height = len(title)*title_size*1.18
    content = dict(box=(x,y,w,h), title=title, title_size=title_size, title_height=title_height)
    if item['kind'] == 'story':
        known = {n['id'] for n in data['nodes']}
        references = item.get('source_nodes', [])
        require(isinstance(references,list) and references and all(isinstance(n,str) for n in references) and len(references) == len(set(references)) and all(n in known for n in references),
                'A story inset requires unique known source_nodes.')
        require(isinstance(item.get('text'), str) and item['text'].strip(), 'A story inset requires source-backed prose.')
        size = number(item.get('size', 14), 'story text size')
        require(size >= 10, 'Story text must remain readable.')
        aw = number(item.get('art_width', 90), 'story art width') if item.get('icon') else 0
        ah = number(item.get('art_height', aw), 'story art height') if item.get('icon') else 0
        require(not item.get('icon') or (aw > 0 and ah > 0), 'Story artwork dimensions must be positive.')
        text_x = aw+22 if aw else 5
        require(w-text_x-5 >= 80, 'The story inset has too little width for its prose.')
        lines = wrap(item['text'], w-text_x-5, size)
        body_top = title_height+22
        required = body_top+max(ah, len(lines)*size*1.22)+6
        require(measure_only or required <= h, 'The story inset is too short for complete prose and artwork.')
        content.update(size=size, lines=lines, art_width=aw, art_height=ah, text_x=text_x, body_top=body_top)
    else:
        groups = {g['id']: g for g in data['groups']}
        selected = item.get('groups', list(groups))
        require(isinstance(selected,list) and selected and all(isinstance(g,str) for g in selected) and len(selected) == len(set(selected)) and all(g in groups for g in selected), 'Count inset groups must be unique and known.')
        columns = item.get('columns', 2)
        require(type(columns) is int and 1 <= columns <= 3, 'Count inset columns must be 1, 2 or 3.')
        columns = min(columns, len(selected))
        cell_width = w/columns
        require(cell_width >= 150, 'Count inset columns need at least 150 units each.')
        size = number(item.get('label_size', 12), 'count label size')
        require(size >= 10, 'Count labels must remain readable.')
        per_line = math.floor((cell_width-45)/10)
        cells = []
        for gid in selected:
            count = sum(n['group'] == gid for n in data['nodes'])
            labels = wrap(groups[gid]['label'], cell_width-12, size, True)
            marker_rows = math.ceil(count/per_line)
            height = len(labels)*size*1.18+8+max(12, marker_rows*14)+9
            cells.append(dict(group=gid, count=count, labels=labels, height=height, marker_rows=marker_rows))
        rows = [max(cell['height'] for cell in cells[i:i+columns]) for i in range(0, len(cells), columns)]
        body_top = title_height+14
        required = body_top+sum(rows)+16
        require(measure_only or required <= h, f'The count inset needs at least {required:.1f} units of height; keep all symbols and enlarge the box.')
        extra = max(0,h-required)/len(rows)
        tops = [body_top]
        for height in rows[:-1]:tops.append(tops[-1]+height+extra)
        content.update(cells=cells, columns=columns, cell_width=cell_width, size=size, per_line=per_line, tops=tops)
    content['required_height'] = required
    return content


def draw_context_inset(poster, item, index):
    content = inset_content(item, poster.data)
    x,y,w,h = content['box']
    iid = ident(item.get('id', f'inset-{index}'))
    poster.add(f'<g data-inset-id="{iid}" data-inset-kind="{item["kind"]}">')
    poster.rect(content['box'], 'none', extra='data-inset-box="true"')
    for i,line in enumerate(content['title']):
        poster.text(x+w/2, y+content['title_size']+i*content['title_size']*1.18, line, content['title_size'], bold=True, css='data-inset-role="title"')
    if item['kind'] == 'story':
        if item.get('icon'):
            poster.add('<g data-inset-art="true">')
            poster.rect((x+5,y+content['body_top'],content['art_width'],content['art_height']), 'none', extra='data-inset-art-box="true"')
            poster.artwork(item['icon'], x+5, y+content['body_top'], content['art_width'], content['art_height'], poster.ink, item.get('variant',0))
            poster.add('</g>')
        for i,line in enumerate(content['lines']):
            poster.text(x+content['text_x'], y+content['body_top']+content['size']+i*content['size']*1.22, line,
                        content['size'], anchor='start', css='data-inset-role="story"')
    else:
        for i,cell in enumerate(content['cells']):
            xx = x+(i%content['columns'])*content['cell_width']
            yy = y+content['tops'][i//content['columns']]
            paint = poster.groups[cell['group']]['color']
            poster.add(f'<g data-count-group="{attr(cell["group"])}">')
            for j,line in enumerate(cell['labels']):
                poster.text(xx+4, yy+content['size']+j*content['size']*1.18, line, content['size'], bold=True, anchor='start', css='data-inset-role="group-label"')
            top = yy+len(cell['labels'])*content['size']*1.18+8
            for j in range(cell['count']):
                px = xx+5+(j%content['per_line'])*10
                py = top+(j//content['per_line'])*14
                poster.add(f'<path data-count-mark="true" d="M{fmt(px)} {fmt(py+4)}l3.5 -4l3.5 4v7h-7Z" fill="{paint}"/>')
            poster.text(xx+content['cell_width']-18, top+11, str(cell['count']), content['size'], anchor='end', css='data-inset-role="count"')
            poster.add('</g>')
        poster.text(x+w/2, y+h-2, 'One symbol = one institution shown', 10, poster.muted, css='data-inset-role="key"')
    poster.add('</g>')


if __name__ == '__main__':
    print('Use authored story or counts insets with the editorial lineage renderer.')
