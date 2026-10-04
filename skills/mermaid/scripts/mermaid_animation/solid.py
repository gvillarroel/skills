#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Native Mermaid filled-category finish; supplied SVG input retains source fidelity."""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET
import time
from pathlib import Path
from palette_paints import canonical, readable_text, rgb, solid_colors, solid_style
from arrow_contrast import finish_native_arrows

def style(element: ET.Element, declarations: str) -> None:
    keys = {part.split(':', 1)[0].strip() for part in declarations.split(';') if ':' in part}
    retained = [part for part in element.get('style', '').split(';') if ':' in part and part.split(':', 1)[0].strip() not in keys]
    element.set('style', ';'.join(retained + [declarations.rstrip(';')]) + ';')

def write_native_svg(tree: ET.ElementTree, output: Path) -> None:
    """Retry the observed transient Windows indexer file-open error, then fail."""
    payload=ET.tostring(tree.getroot(),encoding='utf-8',xml_declaration=True)
    for attempt in range(8):
        try:
            output.write_bytes(payload)
            return
        except OSError as error:
            if error.errno not in {13,22} or attempt==7:
                raise
            time.sleep(.08*(attempt+1))

def fill_shape(element: ET.Element, fill: str) -> None:
    # Keep reveal/transition opacity available; only the paint itself is opaque.
    element.set('style', re.sub(r'(?:^|;)\s*opacity:1 !important(?=;|$)', '', element.get('style', '')))
    style(element, f"fill:{fill} !important;fill-opacity:1 !important;opacity:1;stroke:none !important;stroke-width:0 !important;")

def label(element: ET.Element, fill: str) -> None:
    text = readable_text(fill)
    for child in element.iter():
        if child.tag.rsplit("}",1)[-1] in {"text", "tspan", "div", "span", "b", "p"}:
            style(child,f"fill:{text} !important;color:{text} !important;")

def category_shape(element: ET.Element, index: int, colorset: str) -> str:
    paint = solid_style(index, colorset)
    fill_shape(element, paint['fill'])
    if paint['overflow']:
        style(element, f"stroke:{paint['stroke']} !important;stroke-width:{paint['strokeWidth']} !important;stroke-dasharray:{paint['dash']} !important;")
        element.set('data-colorset-overflow', 'true')
    return paint['fill']


def element_fill(element: ET.Element, fallback: str) -> str:
    value = paint_property(element, 'fill', fallback)
    return canonical(value) if value not in {'none', 'transparent', 'inherit'} else fallback


def paint_property(element: ET.Element, key: str, fallback: str) -> str:
    match = re.search(r'(?:^|;)\s*' + re.escape(key) + r'\s*:\s*([^;!]+)', element.get('style', ''))
    return match.group(1).strip() if match else element.get(key, fallback)


def native_css_fill(root: ET.Element, selector: str, fallback: str) -> str:
    """Read a native renderer's precise class/marker selector before overriding it."""
    fill = fallback
    for sheet in root.iter():
        if sheet.tag.rsplit('}', 1)[-1] != 'style':
            continue
        for selectors, declarations in re.findall(r'([^{}]+)\{([^}]+)\}', sheet.text or ''):
            if re.search(re.escape(selector) + (r'(?![\w-])' if selector.startswith('.') else ''), selectors):
                match = re.search(r'(?:^|;)\s*fill\s*:\s*([^;!]+)', declarations)
                if match:
                    fill = canonical(match.group(1).strip())
    return fill


def effective_fill(element: ET.Element, canvas: str = '#ffffff') -> str:
    """Composite meaningful native translucent paint without changing its geometry."""
    token = paint_property(element, 'fill', canvas)
    alpha = float(paint_property(element, 'fill-opacity', '1')) * float(paint_property(element, 'opacity', '1'))
    if token.startswith('rgba'):
        values = re.findall(r'[\d.]+', token)
        alpha *= float(values[3])
    elif token.startswith('#') and len(token) in {5, 9}:
        alpha *= int(token[-2:] if len(token) == 9 else token[-1] * 2, 16) / 255
    alpha = min(1, max(0, alpha))
    return '#' + ''.join(f'{round(a*alpha+b*(1-alpha)):02x}' for a, b in zip(rgb(canonical(token)), rgb(canvas)))


def native_family_details(root: ET.Element, colorset: str) -> None:
    """Finish actual native category bodies without flattening native line art."""
    family = root.get('aria-roledescription', '').lower()
    colors = solid_colors(colorset)
    parents = {child: parent for parent in root.iter() for child in parent}
    tag = lambda element: element.tag.rsplit('}', 1)[-1]
    groups = [element for element in root.iter() if tag(element) == 'g']
    roles = ['csPrimary', 'csAccent', 'csMuted', 'csCritical', 'csWarning', 'csSuccess', 'csInfo', 'csSpecial', 'csNeutral']
    # Class-authored node labels can contain a separate native SVG text backing.
    # Keep that backing with its actual node paint, including Block SVG text.
    for group in groups:
        classes = group.get('class', '').split()
        role = next((name for name in roles if name in classes), None)
        if role and 'node' in classes:
            index = roles.index(role)
            fill = solid_style(index, colorset)['fill']
            for child in group.iter():
                if tag(child) in {'rect', 'circle', 'ellipse', 'polygon'}:
                    category_shape(child, index, colorset)
            label(group, fill)
    if family == 'kanban':
        for index, group in enumerate(g for g in groups if 'node' in g.get('class', '').split()):
            fill = solid_style(index, colorset)['fill']
            for child in group.iter():
                if tag(child) == 'rect':
                    category_shape(child, index, colorset)
            label(group, fill)
    if family == 'c4':
        types: dict[str, int] = {}
        entity_boxes = []
        for group in groups:
            if 'person-man' not in group.get('class', '').split():
                continue
            stereotype = next((''.join(child.itertext()).strip() for child in group if tag(child) == 'text'), group.get('id', 'entity'))
            index = types.setdefault(stereotype, len(types))
            fill = solid_style(index, colorset)['fill']
            for child in group:
                if tag(child) in {'rect', 'circle', 'ellipse', 'polygon'} or (tag(child) == 'path' and child.get('fill', 'none') != 'none'):
                    category_shape(child, index, colorset)
                    if tag(child) == 'rect':
                        entity_boxes.append((child, fill))
                elif tag(child) == 'path':
                    # The open cylinder seam conveys database geometry.
                    style(child, f'stroke:{readable_text(fill)} !important;stroke-width:1;')
            label(group, fill)
        for group in groups:
            if 'person-man' in group.get('class', '').split():
                continue
            for text in group:
                if tag(text) != 'text' or 'x' not in text.attrib or 'y' not in text.attrib:
                    continue
                x, y = float(text.get('x', 0)), float(text.get('y', 0))
                fill = next((paint for box, paint in entity_boxes if float(box.get('x', 0)) <= x <= float(box.get('x', 0))+float(box.get('width', 0)) and float(box.get('y', 0)) <= y <= float(box.get('y', 0))+float(box.get('height', 0))), '#ffffff')
                # Native relationship captions can cross an entity rectangle.
                label(text, fill)
    if family == 'swimlane':
        lanes = sorted((g for g in groups if 'swimlane' in g.get('class', '').split()), key=lambda g: g.get('id', ''))
        for index, group in enumerate(lanes):
            fill = solid_style(index, colorset)['fill']
            for child in group:
                classes = child.get('class', '').split()
                if 'swimlane-title' in classes:
                    category_shape(child, index, colorset)
                elif 'swimlane-body' in classes:
                    # A lane's body is canvas; its opaque header carries identity.
                    style(child, 'fill:none !important;stroke:none !important;stroke-width:0 !important;')
                elif 'swimlane-label' in classes:
                    label(child, fill)
    if family == 'journey':
        headers = [e for e in root.iter() if 'journey-section' in e.get('class', '').split()]
        ranges = [(float(e.get('x', 0)), float(e.get('width', 0)), index) for index, e in enumerate(headers)]
        for element in root.iter():
            classes = element.get('class', '').split()
            if tag(element) == 'rect' and ('journey-section' in classes or 'task' in classes):
                x = float(element.get('x', 0))
                index = next((i for left, width, i in ranges if left <= x < left + width), 0)
                fill = category_shape(element, index, colorset)
                parent = parents.get(element)
                if parent is not None:
                    for child in parent:
                        if tag(child) == 'switch':
                            label(child, fill)
            actor = next((re.fullmatch(r'actor-(\d+)', c) for c in classes if re.fullmatch(r'actor-(\d+)', c)), None)
            if actor and tag(element) == 'circle':
                category_shape(element, int(actor.group(1)), colorset)
    if family == 'gantt':
        task_fills: dict[str, str] = {}
        for element in root.iter():
            classes = element.get('class', '').split()
            if tag(element) == 'rect' and 'task' in classes:
                status = ' '.join(classes).lower()
                index = 3 if 'done' in status else 2 if 'active' in status else 0
                if colorset == 'colorset1' and index:
                    index -= 1
                fill = colors[index]
                if 'crit' in status:
                    # Critical is a semantic status boundary, not a category rim.
                    style(element, f'fill:{fill} !important;fill-opacity:1 !important;opacity:1;')
                else:
                    fill_shape(element, fill)
                task_fills[element.get('id', '')] = fill
        for element in root.iter():
            if tag(element) == 'text' and 'taskText' in element.get('class', '').split():
                fill = task_fills.get(element.get('id', '').removesuffix('-text'), '#ffffff')
                label(element, '#ffffff' if 'Outside' in element.get('class', '') else fill)
    if family == 'treemap':
        index = 0
        for group in groups:
            classes = group.get('class', '').split()
            if not ('treemapSection' in classes or 'treemapLeafGroup' in classes):
                continue
            bodies = [e for e in group if tag(e) == 'rect' and ('treemapLeaf' in e.get('class', '').split() or 'treemapSection' in e.get('class', '').split()) and e.get('fill') not in {'none', 'transparent'}]
            if not bodies:
                continue
            fill = solid_style(index, colorset)['fill']
            for body in bodies:
                category_shape(body, index, colorset)
            for child in group:
                if tag(child) == 'text':
                    label(child, fill)
            index += 1
    if family == 'zenuml':
        columns = []
        for index, group in enumerate(g for g in groups if 'participant' in g.get('class', '').split()):
            box = next((e for e in group if 'participant-box' in e.get('class', '').split()), None)
            if box is None:
                continue
            fill = category_shape(box, index, colorset)
            columns.append((float(box.get('x', 0)) + float(box.get('width', 0))/2, fill))
            label(group, fill)
            for icon in group:
                if 'participant-icon' in icon.get('class', '').split():
                    style(icon, f'color:{readable_text(fill)} !important;')
        for element in root.iter():
            classes = element.get('class', '').split()
            if 'occurrence' in classes and columns:
                x = float(element.get('x', 0)) + float(element.get('width', 0))/2
                fill_shape(element, min(columns, key=lambda col: abs(col[0]-x))[1])
            if tag(element) == 'text' and any(c in classes for c in ['message-label', 'seq-number', 'frame-label']):
                label(element, '#ffffff')
    if family == 'railroadebnf':
        for group in groups:
            classes = group.get('class', '').split()
            if 'railroad-terminal' in classes or 'railroad-nonterminal' in classes:
                index = 0 if 'railroad-terminal' in classes else 1
                fill = solid_style(index, colorset)['fill']
                for child in group:
                    if tag(child) == 'rect':
                        category_shape(child, index, colorset)
                label(group, fill)
    if family == 'wardley':
        for index, group in enumerate(g for g in groups if 'wardley-node--component' in g.get('class', '').split()):
            for child in group:
                if tag(child) == 'circle' and not child.get('class'):
                    # Procurement overlays remain meaningful native glyphs.
                    category_shape(child, index, colorset)
    if family == 'cynefin':
        for index, element in enumerate(e for e in root.iter() if 'cynefinItem' in e.get('class', '').split()):
            fill = category_shape(element, 5 + index, colorset)
            parent = parents.get(element)
            if parent is not None:
                label(parent, fill)
        domains = [e for e in root.iter() if 'cynefinDomain' in e.get('class', '').split()]
        center = next((e for e in root.iter() if 'cynefinConfusion' in e.get('class', '').split()), None)
        center_geometry = re.match(r'M\s*([\d.]+)[, ]+([\d.]+)\s+A\s*([\d.]+)[, ]+([\d.]+)', center.get('d', '')) if center is not None else None
        for element in root.iter():
            if not any(c in element.get('class', '').split() for c in ['cynefinSubtitle', 'cynefinArrowLabel']):
                continue
            x, y = float(element.get('x', 0)), float(element.get('y', 0))
            if center_geometry:
                left, cy, rx, ry = map(float, center_geometry.groups())
                if ((x-left-rx)/rx)**2 + ((y-cy)/ry)**2 <= 1:
                    label(element, element_fill(center, colors[4]))
                    continue
            domain = next((e for e in domains if float(e.get('x', 0)) <= x <= float(e.get('x', 0))+float(e.get('width', 0)) and float(e.get('y', 0)) <= y <= float(e.get('y', 0))+float(e.get('height', 0))), None)
            if domain is not None:
                label(element, element_fill(domain, colors[0]))
    if family == 'quadrantchart':
        boxes = [e for g in groups if 'quadrant' in g.get('class', '').split() for e in g if tag(e) == 'rect']
        for group in groups:
            if 'data-point' not in group.get('class', '').split():
                continue
            circle = next((e for e in group if tag(e) == 'circle'), None)
            if circle is None:
                continue
            x, y = float(circle.get('cx', 0)), float(circle.get('cy', 0))
            box = next((e for e in boxes if float(e.get('x', 0)) <= x <= float(e.get('x', 0))+float(e.get('width', 0)) and float(e.get('y', 0)) <= y <= float(e.get('y', 0))+float(e.get('height', 0))), None)
            if box is not None:
                label(group, element_fill(box, colors[0]))
    if family == 'gitgraph':
        for element in root.iter():
            if 'commit-label' in element.get('class', '').split():
                label(element, '#ffffff')
    if family == 'eventmodeling':
        for group in groups:
            if 'em-swimlane' in group.get('class', '').split():
                for text in group:
                    if tag(text) == 'text':
                        label(text, '#f7f7f7')
    if family in {'sequence', 'sequencediagram'}:
        marker_fill = native_css_fill(root, '[id$="-sequencenumber"]', '#696969')
        for element in root.iter():
            classes = element.get('class', '').split()
            if any(c in classes for c in ['loopText', 'sectionTitle', 'messageText']) or tag(element) == 'text' and 'actor-man' in classes:
                # Conditions sit in meaningful translucent control regions.
                label(element, '#ffffff')
            if 'sequenceNumber' in classes:
                # Marker instances have zero DOM bounds; read their native paint.
                label(element, marker_fill)
    if family == 'venn':
        for group in groups:
            region = next((e for e in group if tag(e) == 'path'), None)
            if region is not None:
                for caption in group:
                    if tag(caption) == 'text' and 'label' in caption.get('class', '').split():
                        label(caption, effective_fill(region))
    if family == 'radar':
        for element in root.iter():
            swatch = next((c for c in element.get('class', '').split() if re.fullmatch(r'radarLegendBox-\d+', c)), None)
            if swatch:
                # Preserve the matching curve identity; only swatches are opaque.
                fill_shape(element, native_css_fill(root, '.' + swatch, colors[0]))


def native_solid_presentation(root: ET.Element, colorset: str) -> None:
    colors = solid_colors(colorset)
    quadrant_index = 0
    section_indices: dict[int, int] = {}
    card_index = 0
    kanban = root.get('aria-roledescription', '').lower() == 'kanban'
    # Scoped native category groups cover section-driven families. Header sections
    # are containers; each group's native numbered mapping retains its identity.
    for group in root.iter():
        classes = group.get("class", "").split()
        section = next((re.fullmatch(r"section-(-?\d+)",c) for c in classes if re.fullmatch(r"section-(-?\d+)",c)), None)
        if section and group.tag.rsplit("}",1)[-1] == "g" and any(c in classes for c in ("node","timeline-node","cluster")):
            section_id = int(section.group(1))
            index = section_indices.setdefault(section_id, len(section_indices))
            fill = solid_style(index, colorset)['fill']
            for shape in group:
                if shape.tag.rsplit("}",1)[-1] in {"rect","circle","ellipse","polygon","path"}:
                    category_shape(shape,index,colorset)
            label(group,fill)
        if kanban and 'node' in classes and group.tag.rsplit('}',1)[-1] == 'g':
            # Native Kanban cards are sibling groups without a numbered section.
            # Give each stable DOM card ID the next solid slot, with no white rim.
            fill = solid_style(card_index, colorset)['fill']
            for shape in group:
                if shape.tag.rsplit('}',1)[-1] in {'rect','circle','ellipse','polygon','path'}:
                    category_shape(shape,card_index,colorset)
            label(group,fill)
            card_index += 1
        if "em-box" in classes:
            shape = next((child for child in group if child.tag.rsplit("}",1)[-1] == "rect"),None)
            if shape is not None:
                fill=canonical(shape.get("fill",colors[0]));fill_shape(shape,fill);label(group,fill)
        if "quadrant" in classes:
            # Each domain has one native box and its own text descendants.
            boxes=[child for child in group if child.tag.rsplit("}",1)[-1]=='rect']
            for box in boxes:
                fill=colors[quadrant_index%len(colors)]
                fill_shape(box,fill);label(group,fill)
            quadrant_index += 1
    # Pie puts all arcs and all inside labels in separate consecutive groups.
    arcs=[element for element in root.iter() if "pieCircle" in element.get("class", "").split()]
    labels=[element for element in root.iter() if "slice" in element.get("class", "").split()]
    for index,arc in enumerate(arcs):
        fill=category_shape(arc,index,colorset)
        if index<len(labels):label(labels[index],fill)
    domains=[element for element in root.iter() if 'cynefinDomain' in element.get('class','').split()]
    domain_labels=[element for element in root.iter() if 'cynefinDomainLabel' in element.get('class','').split()]
    for index,domain in enumerate(domains):
        fill_shape(domain,colors[index])
        if index<len(domain_labels):label(domain_labels[index],colors[index])
    for element in root.iter():
        if 'cynefinConfusion' in element.get('class','').split():
            fill_shape(element,colors[4])
            if len(domain_labels)>4:label(domain_labels[4],colors[4])
        if 'cynefinSubtitle' in element.get('class','').split():
            try:
                x,y=float(element.get('x','0')),float(element.get('y','0'))
                slot=0 if x<400 and y<300 else 1 if y<300 else 2 if x<400 else 3
                label(element,colors[slot])
            except ValueError:
                pass
    for element in root.iter():
        classes=element.get('class','').split()
        if 'pieOuterCircle' in classes:
            style(element,'stroke:none !important;stroke-width:0 !important;')
        if 'packetBlock' in classes:
            fill_shape(element,colors[0])
        if 'packetLabel' in classes:
            label(element,colors[0])
        if 'ishikawa-label-group' in classes or 'ishikawa-head-group' in classes:
            for child in element:
                if child.tag.rsplit('}',1)[-1] in {'rect','path'}:fill_shape(child,colors[0])
            label(element,colors[0])
    native_family_details(root, colorset)
    finish_native_arrows(root, colorset)
    root.set('data-category-presentation','solid-first')
