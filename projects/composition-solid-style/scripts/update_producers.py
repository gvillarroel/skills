#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply owned composition producer changes; never touch palette definitions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ROOT / "skills"
OWNERS = ["compose-synchronized-svg", "diagram-composition", "usefulcharts-style", "video", "manim-svg-video"]
HELPERS = '''

def text_on_fill(fill, colorset="colorset2"):
    """Select pure black or white by the actual opaque fill's WCAG contrast."""
    return COLORSETS[colorset]["textOnFill"][require_color(fill, colorset)]

def solid_colors(colorset="colorset2", canvas="#f7f7f7"):
    """Exhaust every unique palette solid before introducing outline variants."""
    return [paint for paint in COLORSETS[colorset]["solidSequence"] if paint != canvas.lower()]

def category_style(index, colorset="colorset2", canvas="#f7f7f7"):
    """Return an inspectable solid-first fill/text/border encoding."""
    if not isinstance(index, int) or index < 0:
        raise ValueError("Category index must be a nonnegative integer")
    solids = solid_colors(colorset, canvas)
    fill = solids[index % len(solids)]
    cycle = index // len(solids)
    style = {"fill": fill, "text": text_on_fill(fill, colorset), "stroke": "none",
             "strokeWidth": 0, "dash": "", "overflow": False}
    if cycle:
        # Only after exhausting all usable solids: reuse fills with explicit,
        # finite border-color, dash and width combinations plus direct labels.
        borders = [paint for paint in solids if paint != fill and paint != canvas.lower()]
        style.update(stroke=borders[(cycle - 1) % len(borders)],
                     strokeWidth=1 + (cycle - 1) // (3 * len(borders)),
                     dash=("", "6 3", "2 3")[((cycle - 1) // len(borders)) % 3], overflow=True)
    return style
'''

def edit(owner, relative, callback):
    path = SKILLS / owner / relative
    original = path.read_text(encoding="utf-8")
    cooked = callback(original)
    if cooked != original:
        path.write_text(cooked, encoding="utf-8", newline="\n")

for owner in OWNERS:
    edit(owner, "scripts/palette_contract.py", lambda s: s if "def category_style(" in s else s + HELPERS)

def native(s):
    s = s.replace("from palette_contract import require_color", "from palette_contract import require_color, text_on_fill")
    s = s.replace('stroke="#cfcfcf", radius=5', 'stroke="none", radius=5')
    s = s.replace('def icon(self, value, x, y, size, label):', 'def icon(self, value, x, y, size, label, color=MUTED):')
    s = s.replace('"stroke": MUTED,', '"stroke": color,')
    s = s.replace("fill,stroke=node.get('fill','#f7f7f7'),accent or color or '#b5b5b5'", "fill = node.get('fill', accent or color or '#9c9c9c')\n        stroke = node.get('stroke', 'none')\n        foreground = text_on_fill(fill)")
    s = s.replace("self.bind_color(box,node,'stroke')", "self.bind_color(box,node,'fill')")
    s = s.replace('26, node["label"])', '26, node["label"], color=foreground)')
    s = s.replace('bold=True, center=not bool(icon))', 'bold=True, center=not bool(icon), color=foreground)')
    s = s.replace('center=True, color=MUTED)', 'center=True, color=foreground)')
    s = s.replace('self.w-8,self.h-8,\'#f7f7f7\',LINE', "self.w-8,self.h-8,'#f7f7f7','none'")
    s = s.replace('swatch,"#696969",1', 'swatch,"none",1')
    s = s.replace('group_box=self.rect(gx,gy,gw,gh,"#ffffff","#cfcfcf")\n            accent = self.concept_color(g)\n            if accent: self.bind_color(self.rect(gx+1,gy+1,gw-2,4,accent,"none",1),g,"fill")', 'accent = self.concept_color(g)\n            paint = accent or "#9c9c9c"\n            group_box=self.bind_color(self.rect(gx,gy,gw,gh,paint,"none"),g,"fill")\n            foreground = text_on_fill(paint)')
    s = s.replace('title_h,bold=True,color=INK)', 'title_h,bold=True,color=foreground)')
    s = s.replace('gh-title_h-22,top=True)', 'gh-title_h-22,top=True,color=foreground)')
    # Boundary enclosures contain other categories; a small opaque named header
    # carries identity without turning the whole enclosure into a tinted border.
    s = s.replace('outer=self.bind_color(self.rect(4,4,self.w-8,self.h-8,"#f7f7f7",self.concept_color(data) or LINE),data,"stroke")\n        self.label(data["label"],16,12,self.w-32,self.f*1.7,bold=True)', 'outer=self.rect(4,4,self.w-8,self.h-8,"#f7f7f7","none")\n        paint=self.concept_color(data) or "#9c9c9c"\n        self.bind_color(self.rect(8,8,self.w-16,self.f*1.7+10,paint,"none"),data,"fill")\n        self.label(data["label"],16,12,self.w-32,self.f*1.7,bold=True,color=text_on_fill(paint))')
    s = s.replace('box=self.bind_color(self.rect(x-12,gy,width+24,positions[last]+height+9-gy,"none",self.concept_color(group) or ACCENT,5),group,"stroke")\n            box.set("stroke-dasharray","6 4")\n            self.label(group["label"],x,gy+2,width,group_head-7,bold=True)', 'box=self.rect(x-12,gy,width+24,positions[last]+height+9-gy,"#ffffff","none",5)\n            paint=self.concept_color(group) or ACCENT\n            self.bind_color(self.rect(x-8,gy,width+16,group_head-4,paint,"none"),group,"fill")\n            self.label(group["label"],x,gy+2,width,group_head-7,bold=True,color=text_on_fill(paint))')
    return s
edit("diagram-composition", "scripts/build_panels.py", native)

def poster(s):
    s = s.replace('preferred = max((INK, "#FFFFFF"), key=lambda c: contrast(c, background))\n    return preferred if contrast(preferred, background) >= 4.5 else "#000000"', 'return max(("#000000", "#ffffff"), key=lambda c: contrast(c, background))')
    s = s.replace('self.paper, "#FFFFFF", 2, 12', 'self.paper, "none", 0, 12')
    s = s.replace('group["color"], self.muted, .7, 2', 'group["color"], "none", 0, 2')
    s = s.replace('paint,self.paper,2,3', 'paint,"none",0,3')
    s = s.replace('self.rect(box, paint, ink if node.get("emphasis") else paint, 2.8 if node.get("emphasis") else 1,', 'self.rect(box, paint, "none", 0,')
    s = s.replace('29), self.paper, paint, 2, 14', '29), paint, "none", 0, 14')
    s = s.replace('lane["label"].upper(), 15, bold=True)', 'lane["label"].upper(), 15, text_color(paint), bold=True, background=paint)')
    return s
edit("usefulcharts-style", "scripts/render_chart.py", poster)
edit("usefulcharts-style", "scripts/editorial_poster.py", lambda s: s.replace("self.paper,'#FFFFFF',3,13", "self.paper,'none',0,13").replace("self.rect((x,y,w,h),'#ffffff',paint,2,12)", "self.rect((x,y,w,h),paint,'none',0,12)").replace("line,13,bold=True,background='#ffffff'", "line,13,text_color(paint),bold=True,background=paint"))
edit("usefulcharts-style", "scripts/create_panel_poster.py", lambda s: s.replace('fill="#f7f7f7" stroke="#cfcfcf"', 'fill="#f7f7f7" stroke="none"').replace('fill="{PAPER}" stroke="{color}" stroke-width="1.6"', 'fill="{color}" stroke="none"').replace('fill="{PAPER}" stroke="#cfcfcf"', 'fill="{PAPER}" stroke="none"'))

def mechanism(s):
    s = s.replace('fill="none", stroke="ink", sw=3', 'fill="none", stroke=None, sw=3')
    s = s.replace('cooked = {"id": identity,', 'if stroke is None:\n            stroke = "none" if fill != "none" else "ink"\n        cooked = {"id": identity,')
    s = s.replace('"tank-shell", d="M640 312 V780 C640 832 940 832 940 780 V312", fill="surface"', '"tank-shell", d="M640 312 V780 C640 832 940 832 940 780 V312 Z", fill="muted"')
    s = s.replace('"tank-cap", cx=790, cy=312, rx=150, ry=38, fill="surface"', '"tank-cap", cx=790, cy=312, rx=150, ry=38, fill="muted"')
    s = s.replace('"pipe-shell", x=100, y=305, width=555, height=50, rx=25, fill="quiet"', '"pipe-shell", x=100, y=305, width=555, height=50, rx=25, fill="muted"')
    s = s.replace('"valve-body", d="M305 283 H405 L430 305 V355 L405 377 H305 L280 355 V305 Z", fill="surface"', '"valve-body", d="M305 283 H405 L430 305 V355 L405 377 H305 L280 355 V305 Z", fill="muted"')
    s = s.replace('"car-body", d="M95 405 L110 365 L172 355 L202 310 H281 L319 355 L366 365 L385 406 V431 H95 Z", fill="surface"', '"car-body", d="M95 405 L110 365 L172 355 L202 310 H281 L319 355 L366 365 L385 406 V431 H95 Z", fill="muted"')
    s = s.replace('fill="quiet", sw=5', 'fill="ink", sw=5')
    return s
edit("hyperframes-explainer", "scripts/compose_mechanism.py", mechanism)
edit("hyperframes-explainer", "assets/templates/brief.json", lambda s: s.replace('"fill": "surface", "stroke": "ink", "strokeWidth": 5', '"fill": "muted", "stroke": "none", "strokeWidth": 0'))

def manim(s):
    s = s.replace('"label_color": "#333e48"', '"label_color": "#000000"').replace('"placeholder_fill": "#f7f7f7"', '"placeholder_fill": "#9e1b32"').replace('"placeholder_text": "#9e1b32"', '"placeholder_text": "#ffffff"')
    s = s.replace('stroke_width=0.45,', 'stroke_width=0,').replace('fill_opacity=0.82,', 'fill_opacity=1,').replace('fill_opacity=0.8,', 'fill_opacity=1,\n        stroke_width=0,')
    return s
edit("manim-svg-video", "scripts/compose_svg_video.py", manim)

def hierarchy(s):
    s = s.replace(">.179?'#1c1c1c':'#ffffff'", ">Math.sqrt(.05*1.05)-.05?'#000000':'#ffffff'")
    s = s.replace("return '#333e48';const rgb", "return '#000000';const rgb")
    s = s.replace("stroke:'#fff','stroke-width':3", "stroke:'none','stroke-width':0")
    s = s.replace("m.setAttribute('stroke','#f7f7f7');m.setAttribute('stroke-width','.7')", "m.setAttribute('stroke','none');m.setAttribute('stroke-width','0')")
    s = s.replace('stroke:#f7f7f7;stroke-width:.7;', 'stroke:none;stroke-width:0;')
    s = s.replace('border:1px solid var(--line)', 'border:0').replace('border:1px solid var(--edge)', 'border:0').replace('border:1px solid #0002', 'border:0')
    s = s.replace('button[aria-pressed=true]{border-color:var(--accent);background:var(--wash);color:#333e48}', 'button[aria-pressed=true]{border:0;background:var(--accent);color:#ffffff}')
    return s
edit("hierarchy-lens", "assets/templates/explorer.html", hierarchy)
edit("hierarchy-lens", "assets/templates/pixels.html", hierarchy)

def video(s):
    helper = '''function textOnFill(fill) {
  const channels = [1, 3, 5].map(i => parseInt(fill.slice(i, i + 2), 16) / 255);
  const linear = channels.map(v => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
  const L = linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722;
  return (L + 0.05) / 0.05 >= 1.05 / (L + 0.05) ? "#000000" : "#ffffff";
}

'''
    s = s.replace('function chip(g, x, y, text, options = {}) {', helper+'function chip(g, x, y, text, options = {}) {\n  const fill = options.fill ?? palette.blue;')
    s = s.replace('.attr("fill", options.fill ?? palette.blueHighlight)\n    .attr("stroke", options.stroke ?? palette.blue)', '.attr("fill", fill)\n    .attr("stroke", options.stroke ?? "none")')
    s = s.replace('.attr("fill", options.textColor ?? palette.brandNeutral)', '.attr("fill", options.textColor ?? textOnFill(fill))')
    s = s.replace('stroke = "#ffffff")', 'stroke = "none")')
    return s
edit("video", "assets/examples/ai-concept-videos/renderer.js", video)

print("Updated owned composition producers.")
