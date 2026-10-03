#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=11", "playwright>=1.55,<2", "pypdf>=5,<7"]
# ///
"""Measured, editable composition primitives for this project's three posters."""
from pathlib import Path
import base64
import hashlib
import json
import math
import xml.etree.ElementTree as ET
from PIL import ImageFont, Image

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
OUT = ROOT / 'artifacts'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
PAPER = '#F7F2E8'
INK = '#20343B'
MUTED = '#59666A'
TEAL = '#226F70'
CORAL = '#A14637'
GOLD = '#87601D'
PURPLE = '#715781'
BLUE = '#375D8B'
SAGE = '#4B6A49'
COLORS = [TEAL, CORAL, GOLD, PURPLE, BLUE, SAGE]
FONT = REPO / 'skills/usefulcharts-style/assets/fonts/BarlowCondensed-Bold.ttf'
ARIAL = Path('C:/Windows/Fonts/arial.ttf')
BOLD = Path('C:/Windows/Fonts/arialbd.ttf')
ART = OUT / 'images/specimen-sheet.png'
ARCH_URL = 'https://gvillarroel.github.io/blog/posts/ai-architecture-old-ideas-new-probability/'
EVAL_URL = 'https://gvillarroel.github.io/blog/posts/from-benchmarks-to-skill-evolution/'
SPEC_URL = 'https://agentskills.io/specification'
AGENT_URL = 'https://www.anthropic.com/engineering/building-effective-agents'
TABLES = json.loads((OUT / 'data/source-tables.json').read_text(encoding='utf-8'))
SOURCES = json.loads((OUT / 'data/sources.json').read_text(encoding='utf-8'))


def tag(name):
    return '{' + NS + '}' + name


def measure(value, size=20, bold=False, display=False):
    font = ImageFont.truetype(str(FONT if display else BOLD if bold else ARIAL), round(size * 4))
    return font.getlength(str(value)) / 4


def wrap(value, width, size=20, bold=False, display=False):
    lines = []
    for paragraph in str(value).split('\n'):
        current = ''
        for word in paragraph.split():
            trial = (current + ' ' + word).strip()
            if current and measure(trial, size, bold, display) > width * .976:
                lines.append(current)
                current = word
            else:
                current = trial
        lines.append(current)
    return lines


def pale(color, amount=.91):
    a = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
    b = tuple(int(PAPER[i:i + 2], 16) for i in (1, 3, 5))
    return '#' + ''.join(f'{round(x * (1 - amount) + y * amount):02x}' for x, y in zip(a, b))


def overlap(a, b, gap=0):
    return a['x'] < b['x'] + b['w'] + gap and a['x'] + a['w'] + gap > b['x'] and a['y'] < b['y'] + b['h'] + gap and a['y'] + a['h'] + gap > b['y']


class Poster:
    def __init__(self, case, title, subtitle, number, width=3000):
        self.case, self.width = case, width
        self.root = ET.Element(tag('svg'), dict(width=str(width), height='2500', viewBox=f'0 0 {width} 2500', role='img', **{'aria-labelledby': 'poster-title poster-desc'}))
        ET.SubElement(self.root, tag('title'), id='poster-title').text = title
        ET.SubElement(self.root, tag('desc'), id='poster-desc').text = subtitle
        self.defs = ET.SubElement(self.root, tag('defs'))
        ET.SubElement(self.defs, tag('style')).text = '@font-face{font-family:AtlasTitle;src:url(data:font/ttf;base64,' + base64.b64encode(FONT.read_bytes()).decode() + ');font-weight:700}text{font-family:Arial,sans-serif}g[data-record-id]{cursor:pointer}'
        self.bg = self.rect(self.root, 0, 0, width, 2500, PAPER)
        self.edges = ET.SubElement(self.root, tag('g'), id='relationships')
        self.body = ET.SubElement(self.root, tag('g'), id='knowledge-records')
        self.records, self.routes, self.images, self.marks = [], [], [], []
        self.text(self.body, 65, 30, 'THE BLOG KNOWLEDGE ATLAS  /  ' + number, 17, True, MUTED)
        self.text(self.body, 63, 133, title, 82, True, INK, True)
        self.para(self.body, 67, 174, subtitle, width - 130, 22, color=MUTED)
        self.line([(65, 212), (width - 65, 212)], INK, 2, track=False)
        self.title, self.subtitle = title, subtitle

    def rect(self, parent, x, y, w, h, fill, stroke=None, rx=0):
        attrs = dict(x=str(x), y=str(y), width=str(w), height=str(h), fill=fill, rx=str(rx))
        if stroke:
            attrs.update(stroke=stroke, **{'stroke-width': '1.1'})
        return ET.SubElement(parent, tag('rect'), attrs)

    def text(self, parent, x, y, value, size=20, bold=False, color=INK, display=False, **attrs):
        attrib = dict(x=str(x), y=str(y), fill=color, **{'font-size': str(size), 'font-weight': '700' if bold else '400'})
        if display:
            attrib['style'] = 'font-family:AtlasTitle'
        attrib.update(attrs)
        el = ET.SubElement(parent, tag('text'), attrib)
        el.text = str(value)
        return el

    def para(self, parent, x, y, value, width, size=20, bold=False, color=INK, display=False, leading=1.28):
        for line in wrap(value, width, size, bold, display):
            self.text(parent, x, y, line, size, bold, color, display)
            y += size * leading
        return y

    def heading(self, x, y, title, note='', width=900, color=INK):
        self.text(self.body, x, y, title, 37, True, color, True)
        if note:
            return self.para(self.body, x + 1, y + 32, note, width, 19, color=MUTED)
        return y + 20

    def line(self, points, color=INK, width=2, ident=None, source=None, target=None, kind=None, dash=None, arrow=False, track=True):
        ident = ident or f'route-{len(self.routes) + 1:03d}'
        attrs = dict(id=ident, d='M' + 'L'.join(f'{x:.2f} {y:.2f}' for x, y in points), fill='none', stroke=color, **{'stroke-width': str(width), 'stroke-linejoin': 'round', 'stroke-linecap': 'round'})
        if dash:
            attrs['stroke-dasharray'] = dash
        if source:
            attrs.update({'data-source': source, 'data-target': target, 'data-kind': kind or 'related'})
        if arrow:
            mid = 'arrow-' + color.strip('#')
            if self.defs.find(f".//*[@id='{mid}']") is None:
                m = ET.SubElement(self.defs, tag('marker'), dict(id=mid, viewBox='0 0 10 10', refX='9', refY='5', markerWidth='7', markerHeight='7', orient='auto-start-reverse', markerUnits='userSpaceOnUse'))
                ET.SubElement(m, tag('path'), d='M0 0L10 5L0 10Z', fill=color)
            attrs['marker-end'] = f'url(#{mid})'
        ET.SubElement(self.edges, tag('path'), attrs)
        if track:
            self.routes.append(dict(id=ident, points=points, source=source, target=target, kind=kind))
        return ident

    def record(self, ident, x, y, w, title, detail, color=TEAL, kicker=None, size=20, title_size=29, url=ARCH_URL, source='architecture', source_line=None, fill=False, image=None):
        g = ET.SubElement(self.body, tag('g'), id='record-' + ident, **{'data-record-id': ident})
        ET.SubElement(g, tag('title')).text = title + '\n' + detail
        left = x + 14
        yy = y + 6
        if kicker:
            yy = self.para(g, left, yy + 18, kicker, w - 28, 17, True, color) + 4
        if image is not None:
            self.art(image, x + 36, yy + 1, w - 72, 185, ident, title)
            yy += 198
        yy = self.para(g, left, yy + title_size, title, w - 28, title_size, True, color, True) + 4
        yy = self.para(g, left, yy, detail, w - 28, size)
        h = yy - y + 5
        if fill:
            bg = ET.Element(tag('rect'), dict(x=str(x), y=str(y), width=str(w), height=str(h), fill=pale(color), rx='5'))
            g.insert(1, bg)
        self.rect(g, x, y + 8, 3, max(28, h - 17), color)
        self.records.append(dict(id=ident, x=x, y=y, w=w, h=h, title=title, detail=detail, kicker=kicker, color=color, url=url, source=source, source_line=source_line, image=image))
        return self.records[-1]

    def art(self, index, x, y, w, h, owner, caption):
        iw, ih = Image.open(ART).size
        # Intact source sheet; SVG viewport crops preserve original bitmap pixels.
        # Cell boundaries were inspected in the generated sheet before use.
        col, row = index % 4, index // 4
        sx, sy, cw, ch = col * iw / 4, row * ih / 3, iw / 4, ih / 3
        factor = min(w / cw, h / ch)
        aw, ah = cw * factor, ch * factor
        x, y = x + (w - aw) / 2, y + (h - ah) / 2
        aid = 'specimen-sheet'
        if self.defs.find(f".//*[@id='{aid}']") is None:
            ET.SubElement(self.defs, tag('image'), id=aid, width=str(iw), height=str(ih), href='data:image/png;base64,' + base64.b64encode(ART.read_bytes()).decode())
        ident = f'art-{owner}-{len(self.images) + 1:02d}'
        s = ET.SubElement(self.body, tag('svg'), dict(id=ident, x=str(x), y=str(y), width=str(aw), height=str(ah), viewBox=f'{sx} {sy} {cw} {ch}', overflow='hidden', **{'data-art-id': ident, 'data-art-anchor': owner, 'aria-label': 'Conceptual specimen: ' + caption}))
        ET.SubElement(s, tag('use'), href='#' + aid)
        self.images.append(dict(id=ident, owner=owner, specimen=index, x=x, y=y, w=aw, h=ah, caption=caption))
        return self.images[-1]

    def finish(self, height, footnote, detail):
        self.root.set('height', str(height))
        self.root.set('viewBox', f'0 0 {self.width} {height}')
        self.bg.set('height', str(height))
        self.line([(65, height - 105), (self.width - 65, height - 105)], INK, 1.5, track=False)
        self.para(self.body, 67, height - 74, footnote, self.width - 350, 17, color=MUTED)
        self.text(self.body, self.width - 270, height - 35, f'{len(self.records):02d} RECORDS  /  {len(self.images):02d} SPECIMENS', 16, True, MUTED)
        out = OUT / self.case
        out.mkdir(parents=True, exist_ok=True)
        svg = ET.tostring(self.root, encoding='unicode')
        (out / 'poster.svg').write_text(svg, encoding='utf-8')
        payload = dict(case=self.case, title=self.title, subtitle=self.subtitle, canvas=[self.width, height], records=self.records, images=self.images, routes=self.routes, marks=self.marks, detail=detail, sources=SOURCES, svg_sha256=hashlib.sha256((out/'poster.svg').read_bytes()).hexdigest())
        (out / 'manifest.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(dict(case=self.case, canvas=payload['canvas'], records=len(self.records), images=len(self.images))))
        return out
