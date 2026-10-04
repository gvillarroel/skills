#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Finish newly generated native SVG connectors; supplied artwork is unchanged."""
from __future__ import annotations
import copy
import math
import re
import xml.etree.ElementTree as ET
from palette_paints import COLORSETS, canonical, relative_luminance, rgb

NUMBER = r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?'


def property_value(node, key, fallback=''):
    matches = re.findall(r'(?:^|;)\s*'+re.escape(key)+r'\s*:\s*([^;!]+)', node.get('style', ''))
    return matches[-1].strip() if matches else node.get(key, fallback)


def set_style(node, **values):
    old = [d for d in node.get('style', '').split(';') if ':' in d and d.split(':', 1)[0].strip() not in values]
    node.set('style', ';'.join(old+[f'{k}:{v} !important' for k, v in values.items()])+';')


def native_css_property(root, node, key, fallback):
    """Resolve native class paint before choosing a nearby contrast-safe tone."""
    own = property_value(node, key)
    if own and node.get('data-arrow-id') is None and re.search(r'(?:^|;)\s*'+re.escape(key)+r'\s*:', node.get('style', '')): return own
    value = own or fallback
    for sheet in root.iter():
        if sheet.tag.rsplit('}', 1)[-1] != 'style': continue
        for selectors, declarations in re.findall(r'([^{}]+)\{([^}]+)\}', sheet.text or ''):
            matches = any(re.search(r'\.'+re.escape(c)+r'(?![\w-])', selectors) for c in node.get('class', '').split())
            if matches:
                found = re.search(r'(?:^|;)\s*'+re.escape(key)+r'\s*:\s*([^;!]+)', declarations)
                if found: value = found.group(1).strip()
    return value


def contrast(left, right):
    a, b = relative_luminance(left), relative_luminance(right)
    return (max(a, b)+.05)/(min(a, b)+.05)


def safe_paint(preferred, backgrounds, colorset):
    """Keep a valid authored hue; otherwise choose the nearest allowed 3:1 paint."""
    preferred = canonical(preferred)
    choices = [c for c in COLORSETS[colorset]['allowed'] if all(contrast(c, b) >= 3 for b in backgrounds)]
    if not choices:
        raise ValueError('Connector crosses incompatible painted surfaces; reroute it through a clear gutter.')
    origin = rgb(preferred)
    return min(choices, key=lambda c: sum((a-b)**2 for a, b in zip(rgb(c), origin)))


def path_points(node, steps=40):
    """Sample native straight/quadratic/cubic connector geometry, in SVG coordinates."""
    tag = node.tag.rsplit('}', 1)[-1]
    if tag == 'line':
        start = (float(node.get('x1', 0)), float(node.get('y1', 0)))
        end = (float(node.get('x2', 0)), float(node.get('y2', 0)))
        return [(start[0]+(end[0]-start[0])*i/steps, start[1]+(end[1]-start[1])*i/steps) for i in range(steps+1)]
    if tag in {'polygon', 'polyline'}:
        values = list(map(float, re.findall(NUMBER, node.get('points', ''))))
        return list(zip(values[::2], values[1::2]))
    if tag in {'circle', 'ellipse'}:
        cx, cy = float(node.get('cx', 0)), float(node.get('cy', 0))
        rx, ry = float(node.get('rx', node.get('r', 0))), float(node.get('ry', node.get('r', 0)))
        return [(cx+rx*math.cos(i*2*math.pi/steps), cy+ry*math.sin(i*2*math.pi/steps)) for i in range(steps+1)]
    tokens = re.findall(r'[a-zA-Z]|'+NUMBER, node.get('d', ''))
    points, current, first, previous, command = [], (0., 0.), (0., 0.), None, None
    index = 0
    counts = {'M': 2, 'L': 2, 'H': 1, 'V': 1, 'C': 6, 'Q': 4, 'S': 4, 'T': 2, 'A': 7}
    while index < len(tokens):
        if tokens[index].isalpha():
            command = tokens[index]; index += 1
            if command.upper() == 'Z':
                current = first; points.append(first); continue
        kind = command.upper() if command else ''
        if kind not in counts or index+counts[kind] > len(tokens):
            break
        values = list(map(float, tokens[index:index+counts[kind]])); index += counts[kind]
        relative = command.islower()
        def xy(a, b): return (a+current[0], b+current[1]) if relative else (a, b)
        end = xy(*values[-2:]) if kind not in {'H', 'V'} else (values[0]+(current[0] if relative else 0), current[1]) if kind == 'H' else (current[0], values[0]+(current[1] if relative else 0))
        if kind == 'M':
            current = first = end; points.append(end); command = 'l' if relative else 'L'; continue
        controls = [xy(*values[i:i+2]) for i in range(0, len(values)-2, 2)] if kind in {'C', 'Q'} else []
        if kind in {'S', 'T'}:
            reflected = (2*current[0]-previous[0], 2*current[1]-previous[1]) if previous else current
            controls = [reflected, xy(*values[:2])] if kind == 'S' else [reflected]
        arc = None
        if kind == 'A' and values[0] and values[1] and current != end:
            rx, ry = abs(values[0]), abs(values[1])
            phi = math.radians(values[2]); co, si = math.cos(phi), math.sin(phi)
            dx, dy = (current[0]-end[0])/2, (current[1]-end[1])/2
            xp, yp = co*dx+si*dy, -si*dx+co*dy
            scale = math.sqrt(max(1,(xp/rx)**2+(yp/ry)**2)); rx *= scale; ry *= scale
            numerator = max(0,rx*rx*ry*ry-rx*rx*yp*yp-ry*ry*xp*xp)
            denominator = rx*rx*yp*yp+ry*ry*xp*xp
            factor = (-1 if bool(values[3]) == bool(values[4]) else 1)*math.sqrt(numerator/denominator) if denominator else 0
            cxp, cyp = factor*rx*yp/ry, -factor*ry*xp/rx
            cx, cy = co*cxp-si*cyp+(current[0]+end[0])/2, si*cxp+co*cyp+(current[1]+end[1])/2
            start_angle = math.atan2((yp-cyp)/ry,(xp-cxp)/rx)
            end_angle = math.atan2((-yp-cyp)/ry,(-xp-cxp)/rx)
            sweep = (end_angle-start_angle) % (2*math.pi)
            if not values[4] and sweep > 0: sweep -= 2*math.pi
            arc = (rx,ry,co,si,cx,cy,start_angle,sweep)
        for i in range(1, steps+1):
            t = i/steps; u = 1-t
            if arc:
                rx,ry,co,si,cx,cy,angle,sweep = arc; angle += sweep*t
                p = (cx+rx*co*math.cos(angle)-ry*si*math.sin(angle),cy+rx*si*math.cos(angle)+ry*co*math.sin(angle))
            elif len(controls) == 2:
                p = tuple(u**3*current[j]+3*u*u*t*controls[0][j]+3*u*t*t*controls[1][j]+t**3*end[j] for j in range(2))
            elif len(controls) == 1:
                p = tuple(u*u*current[j]+2*u*t*controls[0][j]+t*t*end[j] for j in range(2))
            else:
                p = tuple(u*current[j]+t*end[j] for j in range(2))
            points.append(p)
        previous = controls[-1] if controls else None
        current = end
    return points


def rect_bounds(node):
    tag = node.tag.rsplit('}', 1)[-1]
    if tag == 'rect':
        x, y = float(node.get('x', 0)), float(node.get('y', 0))
        return x, y, x+float(node.get('width', 0)), y+float(node.get('height', 0))
    if tag in {'circle', 'ellipse'}:
        x, y = float(node.get('cx', 0)), float(node.get('cy', 0))
        rx, ry = float(node.get('rx', node.get('r', 0))), float(node.get('ry', node.get('r', 0)))
        return x-rx, y-ry, x+rx, y+ry
    pts = path_points(node)
    return (min(x for x, _ in pts), min(y for _, y in pts), max(x for x, _ in pts), max(y for _, y in pts)) if pts else None


def contains(node, point):
    bounds = rect_bounds(node)
    if not bounds:
        return False
    x, y = point; left, top, right, bottom = bounds
    if node.tag.rsplit('}', 1)[-1] in {'circle', 'ellipse'}:
        rx, ry = (right-left)/2, (bottom-top)/2
        return rx > 0 and ry > 0 and ((x-(left+right)/2)/rx)**2+((y-(top+bottom)/2)/ry)**2 < .999
    if node.tag.rsplit('}', 1)[-1] in {'polygon','path'}:
        # Filled polygons use their actual contour, not their rectangular extent.
        pts = path_points(node)
        inside = False
        for a, b in zip(pts, pts[1:]+pts[:1]):
            if (a[1] > y) != (b[1] > y) and x < (b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]: inside = not inside
        return inside
    return left+.1 < x < right-.1 and top+.1 < y < bottom-.1


def event_gutter(root):
    """Approach event cards perpendicularly through the existing inter-row gutter."""
    bodies = [e for e in root.iter() if e.tag.rsplit('}',1)[-1] == 'rect' and 'stroke:none' in e.get('style','')]
    for edge in root.iter():
        if 'em-relation' not in edge.get('class','').split(): continue
        pts = path_points(edge)
        if not pts: continue
        start, end = pts[0], pts[-1]
        target = next((b for b in bodies if (bounds:=rect_bounds(b)) and bounds[0] <= end[0] <= bounds[2] and abs(end[1]-bounds[1]) < 4), None)
        if target is None: continue
        top = rect_bounds(target)[1]
        middle = (start[1]+top)/2
        route = [start,(start[0],middle),(end[0],middle),(end[0],top-3)]
        edge.set('d','M'+' L'.join(f'{x:g},{y:g}' for x,y in route))
        edge.set('data-arrow-gutter','event-row-clearance')


def c4_gutter(root):
    """Route C4 bypass relations around intervening entities without moving nodes."""
    bodies = [e for g in root.iter() if 'person-man' in g.get('class', '').split() for e in g if e.tag.rsplit('}', 1)[-1] == 'rect' or e.tag.rsplit('}', 1)[-1] == 'path' and e.get('fill', 'none') != 'none']
    bodies = [(e, rect_bounds(e)) for e in bodies if rect_bounds(e)]
    if not bodies: return
    left = min(b[0] for _, b in bodies)-32; right = max(b[2] for _, b in bodies)+32
    for edge in root.iter():
        if not edge.get('marker-end'): continue
        pts = path_points(edge)
        if not pts: continue
        def nearest(point):
            x, y = point
            return min(bodies, key=lambda item: max(item[1][0]-x, 0, x-item[1][2])**2+max(item[1][1]-y, 0, y-item[1][3])**2)
        source, target = nearest(pts[0]), nearest(pts[-1])
        # C4 may put a relation endpoint inside the database/person silhouette.
        # Clip only those contacts, retaining an ordinary native curve otherwise.
        clipped = False
        while len(pts) > 2 and contains(source[0], pts[0]):
            pts.pop(0); clipped = True
        while len(pts) > 2 and contains(target[0], pts[-1]):
            pts.pop(); clipped = True
        if clipped:
            edge.tag = edge.tag.rsplit('}', 1)[0]+'}path' if '}' in edge.tag else 'path'
            for key in ['x1', 'y1', 'x2', 'y2']: edge.attrib.pop(key, None)
            edge.set('d', 'M'+' L'.join(f'{x:g},{y:g}' for x, y in pts))
            edge.set('data-arrow-clearance', 'native-body-contact')
        crossed = [e for e, _ in bodies if e not in {source[0], target[0]} and any(contains(e, p) for p in pts[1:-1])]
        if not crossed: continue
        candidates = []
        for side, gutter in [('left', left), ('right', right)]:
            source_x = source[1][0]-3 if side == 'left' else source[1][2]+3
            target_x = target[1][0]-3 if side == 'left' else target[1][2]+3
            sy, ty = (source[1][1]+source[1][3])/2, (target[1][1]+target[1][3])/2
            route = [(source_x, sy), (gutter, sy), (gutter, ty), (target_x, ty)]
            blocked = 0
            for a, b in zip(route, route[1:]):
                for other, _ in bodies:
                    if other in {source[0], target[0]}: continue
                    if any(contains(other, (a[0]+(b[0]-a[0])*t/20, a[1]+(b[1]-a[1])*t/20)) for t in range(21)): blocked += 1
            candidates.append((blocked, route))
        blocked, route = min(candidates, key=lambda c: c[0])
        if blocked: raise ValueError('C4 relationship needs a manual clear gutter.')
        edge.tag = edge.tag.rsplit('}', 1)[0]+'}path' if '}' in edge.tag else 'path'
        for key in ['x1', 'y1', 'x2', 'y2']: edge.attrib.pop(key, None)
        edge.set('d', 'M'+' L'.join(f'{x:g},{y:g}' for x, y in route))
        edge.set('data-arrow-gutter', 'true')


def marker_copy(root, edge, key, paint, index, parents):
    ref = re.search(r'#([^\)]+)', edge.get(key, ''))
    if not ref or 'sequencenumber' in ref.group(1): return
    marker = next((e for e in root.iter() if e.get('id') == ref.group(1)), None)
    if marker is None: return
    if marker.get('data-arrow-owner') == str(index)+key:
        clone = marker
    else:
        clone = copy.deepcopy(marker)
        clone.set('id', ref.group(1)+'-contrast-'+str(index)+'-'+key)
        clone.set('data-arrow-owner', str(index)+key)
        parents[marker].append(clone)
    bounds = [rect_bounds(e) for e in clone.iter() if e is not clone and rect_bounds(e)]
    if bounds:
        vb = list(map(float, clone.get('viewBox', '').split()))
        scale = min(float(clone.get('markerWidth', 3))/vb[2], float(clone.get('markerHeight', 3))/vb[3]) if len(vb) == 4 else 1
        units = 1 if clone.get('markerUnits') == 'userSpaceOnUse' else float(property_value(edge, 'stroke-width', '1'))
        padding = 3/max(.01, scale*units)
        value = float(clone.get('refX', 0))
        clone.set('refX', str(max(value, max(b[2] for b in bounds)+padding) if key == 'marker-end' else min(value, min(b[0] for b in bounds)-padding)))
    for child in clone.iter():
        tag = child.tag.rsplit('}', 1)[-1]
        if tag not in {'path', 'polygon', 'polyline', 'line', 'circle', 'rect'}: continue
        closed = tag in {'polygon', 'circle', 'rect'} or re.search(r'[zZ]', child.get('d', ''))
        hollow = tag in {'circle', 'rect'} and property_value(child, 'fill', '').lower() in {'white', '#ffffff'}
        set_style(child, fill='#ffffff' if hollow else paint if closed else 'none', stroke=paint if hollow or not closed else 'none')
    edge.set(key, 'url(#'+clone.get('id')+')')
    # Animated SVG keeps marker identity in a CSS custom property so reveal can
    # hide the head until its shaft arrives. Update that identity, not its timing.
    animation_key = '--am-'+key
    if re.search(re.escape(animation_key)+r'\s*:',edge.get('style','')):
        set_style(edge, **{animation_key:'url(#'+clone.get('id')+')'})


def plantuml_head_clearance(edges, backgrounds):
    """Move a native filled tip into its existing gutter, retaining the route."""
    shafts = [edge for edge in edges if edge.tag.rsplit('}', 1)[-1] in {'line', 'path', 'polyline'} and property_value(edge, 'fill', 'none') == 'none']
    for head in edges:
        tag = head.tag.rsplit('}', 1)[-1]
        if tag not in {'polygon', 'path'} or property_value(head, 'fill', 'none') in {'none', '#ffffff', '#FFFFFF', 'white'}:
            continue
        points = path_points(head)
        if not points:
            continue
        center = tuple(sum(point[i] for point in points)/len(points) for i in (0, 1))
        candidates = []
        for shaft in shafts:
            track = path_points(shaft)
            if len(track) < 2:
                continue
            for at_end, endpoint in ((True, track[-1]), (False, track[0])):
                candidates.append((math.dist(center, endpoint), shaft, track, at_end))
        if not candidates:
            continue
        distance, shaft, track, at_end = min(candidates, key=lambda item: item[0])
        if distance > 16:
            continue
        a, b = (track[-2], track[-1]) if at_end else (track[1], track[0])
        length = math.dist(a, b)
        if not length:
            continue
        direction = ((b[0]-a[0])/length, (b[1]-a[1])/length)
        tip = max(points, key=lambda point: point[0]*direction[0]+point[1]*direction[1])
        margin = 3 + float(property_value(head, 'stroke-width', '1')) / 2
        shift = 0
        for shape in backgrounds:
            shape_margin = margin + (float(property_value(shape, 'stroke-width', '1')) / 2 if property_value(shape, 'stroke', 'none') != 'none' else 0)
            # Ignore an enclosing region whose boundary is nowhere near this
            # contact. Measure the complete head stroke, not just its tip point.
            if contains(shape, tip):
                for step in range(1, 81):
                    distance = step / 10
                    if not contains(shape, (tip[0]-direction[0]*distance, tip[1]-direction[1]*distance)):
                        shift = max(shift, shape_margin+distance)
                        break
            else:
                for step in range(1, 46):
                    distance = step / 10
                    if contains(shape, (tip[0]+direction[0]*distance, tip[1]+direction[1]*distance)):
                        shift = max(shift, shape_margin-distance+.2)
                        break
        if shift <= 0:
            continue
        dx, dy = -shift*direction[0], -shift*direction[1]
        if tag == 'polygon':
            head.set('points', ' '.join(f'{x+dx:g},{y+dy:g}' for x,y in points))
        else:
            # Explicit native head paths use absolute M/L pairs; retain their
            # contour rather than flattening a shaft or adding a halo.
            if re.search(r'[a-zA-KN-Y]', head.get('d', '')):
                continue
            head.set('d', re.sub(r'([ML])\s*('+NUMBER+r')[ ,]+('+NUMBER+r')', lambda match: f'{match[1]}{float(match[2])+dx:g},{float(match[3])+dy:g}', head.get('d', '')))
        head.set('data-arrow-clearance', 'native-tip-gutter-3px')
        # Activity shafts terminate at the tip. Other native shafts already end
        # behind the head and keep their complete curve unchanged.
        if math.dist(b, tip) < 1 and shaft.tag.rsplit('}', 1)[-1] == 'line':
            shaft.set('x2' if at_end else 'x1', str(b[0]+dx))
            shaft.set('y2' if at_end else 'y1', str(b[1]+dy))


def plantuml_shaft_clearance(edges, backgrounds, minimum_length=20):
    """Trim native grouped body contacts through their existing short gutter."""
    for shaft in edges:
        tag = shaft.tag.rsplit('}', 1)[-1]
        if tag not in {'line', 'path'} or property_value(shaft, 'fill', 'none') != 'none':
            continue
        points = path_points(shaft)
        if len(points) < 2 or sum(math.dist(a,b) for a,b in zip(points,points[1:])) < minimum_length:
            continue
        for at_end in (False, True):
            tip, other = (points[-1], points[-2]) if at_end else (points[0], points[1])
            length = math.dist(tip, other)
            if not length:
                continue
            direction = ((other[0]-tip[0])/length, (other[1]-tip[1])/length)
            shift = 0
            for shape in backgrounds:
                # Native endpoints can sit less than the containment tolerance
                # inside a body. Probe toward that body before clipping into the
                # gutter, so the complete stroke clears even a shallow contact.
                backed = (tip[0]-direction[0]*.2, tip[1]-direction[1]*.2)
                if not contains(shape, tip) and not contains(shape, backed):
                    continue
                for step in range(1, 121):
                    distance = step / 10
                    point = (tip[0]+direction[0]*distance, tip[1]+direction[1]*distance)
                    if not contains(shape, point):
                        target_width = float(property_value(shape,'stroke-width','1')) if property_value(shape,'stroke','none') != 'none' else 0
                        shift = max(shift, distance+3+(float(property_value(shaft,'stroke-width','1'))+target_width)/2)
                        break
            if not shift:
                continue
            x, y = tip[0]+direction[0]*shift, tip[1]+direction[1]*shift
            if tag == 'line':
                shaft.set('x2' if at_end else 'x1', str(x))
                shaft.set('y2' if at_end else 'y1', str(y))
            elif at_end:
                shaft.set('d', re.sub(r'('+NUMBER+r')[ ,]+('+NUMBER+r')\s*$', f'{x:g},{y:g}', shaft.get('d','')))
            else:
                shaft.set('d', re.sub(r'^\s*M\s*('+NUMBER+r')[ ,]+('+NUMBER+r')', f'M{x:g},{y:g}', shaft.get('d','')))
            shaft.set('data-arrow-clearance', 'native-body-gutter-3px')


def plantuml_source_port_clearance(edges, backgrounds, root, colorset):
    """Keep native JSON/YAML relation ports beside their source in its gutter.

    Native port dots occupy a value cell inside the source body. Move that dot
    and only the straight initial shaft prefix when its fill and the canvas
    cannot share a 3:1 connector paint. Preserve every curve, target, and head.
    """
    canvas = canonical(property_value(root, 'background', '#ffffff'))
    shafts = [edge for edge in edges if edge.tag.rsplit('}', 1)[-1] == 'path'
              and property_value(edge, 'fill', 'none') == 'none']
    for port in edges:
        if port.tag.rsplit('}', 1)[-1] not in {'circle', 'ellipse'}:
            continue
        center = (float(port.get('cx', 0)), float(port.get('cy', 0)))
        body = next((shape for shape in reversed(backgrounds) if contains(shape, center)), None)
        if body is None:
            continue
        backing = canonical(property_value(body, 'fill'))
        if any(contrast(paint, canvas) >= 3 and contrast(paint, backing) >= 3
               for paint in COLORSETS[colorset]['allowed']):
            continue
        matches = [shaft for shaft in shafts if (points := path_points(shaft))
                   and math.dist(points[0], center) < .5]
        if len(matches) != 1:
            raise ValueError('Native source port requires one matching outgoing shaft before gutter repair.')
        shaft = matches[0]
        prefix = re.match(r'^\s*M\s*('+NUMBER+r')[ ,]+('+NUMBER+r')\s*L\s*('+NUMBER+r')[ ,]+('+NUMBER+r')', shaft.get('d', ''))
        if not prefix:
            raise ValueError('Native source port requires an absolute straight initial shaft prefix for gutter repair.')
        first = (float(prefix[3]), float(prefix[4]))
        length = math.dist(center, first)
        if not length:
            raise ValueError('Native source port has no outgoing direction for gutter repair.')
        direction = ((first[0]-center[0])/length, (first[1]-center[1])/length)
        bounds = rect_bounds(body)
        limit = math.ceil(max(bounds[2]-bounds[0], bounds[3]-bounds[1])*10)+10
        distance = next((step/10 for step in range(1, limit)
                         if not contains(body, (center[0]+direction[0]*step/10,
                                                center[1]+direction[1]*step/10))), None)
        if distance is None:
            raise ValueError('Native source port cannot reach a clear source-body gutter.')
        rx = float(port.get('rx', port.get('r', 0)))
        ry = float(port.get('ry', port.get('r', 0)))
        radius = math.hypot(rx*direction[0], ry*direction[1])
        body_width = float(property_value(body, 'stroke-width', '1')) if property_value(body, 'stroke', 'none') != 'none' else 0
        # Account for containment's 0.1 px interior tolerance and ray sampling;
        # the complete painted port envelope still needs a full 3 px gutter.
        shift = distance+.2+3+radius+(float(property_value(port, 'stroke-width', '1'))+body_width)/2
        relocated = (center[0]+direction[0]*shift, center[1]+direction[1]*shift)
        port.set('cx', f'{relocated[0]:g}')
        port.set('cy', f'{relocated[1]:g}')
        if length < shift:
            first = relocated
        suffix = shaft.get('d', '')[prefix.end():]
        shaft.set('d', f'M{relocated[0]:g},{relocated[1]:g} L{first[0]:g},{first[1]:g}'+suffix)
        for node in (port, shaft):
            node.set('data-arrow-clearance', 'native-source-port-gutter-3px')


def finish_native_arrows(root, colorset, renderer='mermaid'):
    """Preserve direction; repair resting paints and native marker clearance."""
    family = root.get('aria-roledescription', '').lower()
    if family == 'c4': c4_gutter(root)
    if family == 'eventmodeling': event_gutter(root)
    parents = {c: p for p in root.iter() for c in p}
    def in_group(node, name):
        while node in parents:
            node = parents[node]
            if name in node.get('class', '').split(): return True
        return False
    def in_definition(node):
        while node in parents:
            node = parents[node]
            if node.tag.rsplit('}', 1)[-1] in {'defs', 'marker', 'clipPath'}: return True
        return False
    edges = []
    for node in root.iter():
        if node.get('data-style-role') == 'semantic-detail': continue
        tag = node.tag.rsplit('}', 1)[-1]
        classes = ' '.join(c for c in node.get('class', '').split() if not c.startswith('am-'))
        marker = any(node.get(k) for k in ['marker-start', 'marker-end']) and 'sequencenumber' not in ''.join(node.get(k, '') for k in ['marker-start', 'marker-end'])
        diagram = root.get('data-diagram-type', '')
        native = renderer == 'plantuml' and (in_group(node, 'link') or in_group(node, 'message'))
        fill = property_value(node, 'fill', 'none')
        if renderer == 'plantuml' and diagram in {'ACTIVITY', 'EBNF', 'REGEX'}:
            bounds = rect_bounds(node)
            small_head = bounds and bounds[2]-bounds[0] <= 12 and bounds[3]-bounds[1] <= 12
            native = native or tag == 'line' or tag == 'path' and (fill == 'none' or small_head) or tag == 'polygon' and small_head
        if renderer == 'plantuml' and diagram in {'JSON', 'YAML', 'MINDMAP', 'WBS'}:
            bounds = rect_bounds(node)
            small_head = bounds and bounds[2]-bounds[0] <= 12 and bounds[3]-bounds[1] <= 12
            native = native or tag == 'path' and (fill == 'none' or small_head) or tag in {'polygon', 'ellipse', 'circle'} and small_head
            if diagram == 'WBS' and tag == 'line' and property_value(node, 'stroke-width', '') == '1.5': native = True
        if renderer == 'plantuml' and diagram == 'GANTT':
            native = native or tag == 'path' and fill == 'none' or tag == 'polygon'
        if fill != 'none' and not marker and not native and 'arrow' not in classes.lower(): continue
        if tag in {'line', 'path', 'polyline', 'polygon', 'ellipse', 'circle'} and not in_definition(node) and (marker or native or re.search(r'arrow|relation|edge|link|message-line|messageLine', classes)):
            if in_group(node, 'node'): continue
            edges.append(node)
    backgrounds = [e for e in root.iter() if e.tag.rsplit('}', 1)[-1] in {'rect', 'circle', 'ellipse','polygon', 'path'} and not in_definition(e) and property_value(e, 'fill', 'none') not in {'none', 'transparent'} and float(property_value(e, 'fill-opacity', '1')) > .999 and e not in edges]
    if renderer == 'plantuml':
        native_family = root.get('data-diagram-type')
        # Hollow final-state rings are painted targets even though their center
        # is transparent. Their outer contour also needs complete-head clearance.
        rings = [node for node in root.iter() if native_family in {'ACTIVITY', 'STATE'}
                 and node.tag.rsplit('}', 1)[-1] in {'circle', 'ellipse'}
                 and property_value(node, 'fill', 'none') == 'none'
                 and property_value(node, 'stroke', 'none') != 'none'
                 and (bounds := rect_bounds(node)) and max(bounds[2]-bounds[0], bounds[3]-bounds[1]) <= 30]
        clearances = backgrounds+rings
        if native_family in {'JSON', 'YAML'}:
            plantuml_source_port_clearance(edges, backgrounds, root, colorset)
        plantuml_shaft_clearance([edge for edge in edges if in_group(edge, 'link')], clearances)
        if native_family in {'MINDMAP', 'WBS', 'ACTIVITY', 'STATE'}:
            plantuml_shaft_clearance([edge for edge in edges if not in_group(edge, 'link')], clearances, minimum_length=1)
        plantuml_head_clearance(edges, clearances)
    order = {e: i for i, e in enumerate(root.iter())}
    for index, edge in enumerate(edges):
        points = path_points(edge)
        if not points: continue
        if family == 'er':
            length = sum(math.dist(a,b) for a,b in zip(points,points[1:]))
            needed = 6
            for key in ['marker-start','marker-end']:
                ref = re.search(r'#([^\)]+)',edge.get(key,''))
                marker = next((e for e in root.iter() if ref and e.get('id') == ref.group(1)),None)
                if marker is None: continue
                bounds = [rect_bounds(e) for e in marker if rect_bounds(e)]
                if bounds:
                    low,high = min(b[0] for b in bounds),max(b[2] for b in bounds)
                    existing = float(marker.get('refX',0))
                    needed += high-min(existing,low-3) if key == 'marker-start' else max(existing,high+3)-low
            if length < needed:
                raise ValueError('ER gutter cannot fit both cardinality glyphs. Increase config.er.rankSpacing to at least 80 and rerender; preserve glyph semantics.')
        paints = ['#ffffff']
        if family == 'cynefin': paints = [COLORSETS[colorset]['solidSequence'][0], COLORSETS[colorset]['solidSequence'][1]]
        elif renderer == 'plantuml':
            paints = []
            samples = points + [((a[0]+b[0])/2, (a[1]+b[1])/2) for a, b in zip(points, points[1:]+points[:1])] if edge.tag.rsplit('}', 1)[-1] == 'polygon' else points
            for point in samples:
                backing = canonical(property_value(root, 'background', '#ffffff'))
                for shape in backgrounds:
                    if order[shape] < order[edge] and contains(shape, point): backing = canonical(property_value(shape, 'fill'))
                paints.append(backing)
            paints = list(set(paints)) or ['#ffffff']
        preferred = native_css_property(root, edge, 'stroke', '#696969')
        if preferred in {'none', 'inherit', 'currentColor'}: preferred = '#696969'
        paint = safe_paint(preferred, paints, colorset)
        filled_head = 'arrow' in edge.get('class', '').lower() and property_value(edge, 'fill', 'none') != 'none' and not any(edge.get(k) for k in ['marker-start','marker-end'])
        set_style(edge, stroke='none' if filled_head else paint, **{'stroke-opacity': '1'})
        if filled_head: set_style(edge, fill=paint)
        if renderer == 'plantuml' and edge.tag.rsplit('}', 1)[-1] in {'polygon', 'path', 'ellipse', 'circle'} and property_value(edge, 'fill', 'none') not in {'none', '#FFFFFF', '#ffffff', 'white'}:
            set_style(edge, fill=paint)
        edge.set('data-arrow-id', edge.get('id', family+'-arrow-'+str(index)))
        for key in ['marker-start', 'marker-end']: marker_copy(root, edge, key, paint, index, parents)
    if edges: root.set('data-arrow-contrast', 'native-resting-3to1')
    else: root.attrib.pop('data-arrow-contrast',None)
