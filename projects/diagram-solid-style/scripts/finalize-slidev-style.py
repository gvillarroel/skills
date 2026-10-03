#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[3]
soft={'#cdf3ff':'#007298','#dbffcc':'#45842a','#fff4cc':'#f1c319','#ffe5cc':'#e77204','#ffccd5':'#9e1b32','#f9ccff':'#652f6c'}
black={'#45842a','#e77204','#f1c319','#828282','#00ace6','#ff9633','#ffd332'}
pack=ROOT/'skills/slidev-animejs/assets/templates/slidev-svg-asset-pack'
for path in (pack/'assets/animated-svg').glob('*.svg'):
    text=path.read_text(encoding='utf-8')
    def filled(match):
        tag=match.group()
        paint=re.search(r'fill="(#[\da-f]{6})"',tag)
        if not paint or paint.group(1) not in soft:return tag
        tag=tag.replace(paint.group(1),soft[paint.group(1)],1)
        tag=re.sub(r'stroke="[^"]*"','stroke="none"',tag)
        tag=re.sub(r'stroke-width="[^"]*"','stroke-width="0"',tag)
        return tag
    text=re.sub(r'<path\b[^>]*>',filled,text)
    text=text.replace('fill="#ffffff" stroke="#cfcfcf" stroke-width="4" data-anime-group="callouts"','fill="#333e48" stroke="none" stroke-width="0" data-anime-group="callouts"')
    if path.name=='interactive-hotspots.svg':
        text=text.replace('class="map-labels" fill="#4f4f4f"','class="map-labels" fill="#ffffff"')
        text=text.replace('class="map-route"','class="map-route" data-meaningful-line="true"')
        text=text.replace('stroke="#4f4f4f" stroke-width="12"','stroke="#000000" stroke-width="12"')
    if path.name=='timeline-machine.svg':
        # Preserve a readable gear hub after changing its surrounding silhouette.
        text=text.replace('r="22" fill="#007298"','r="22" fill="#ffffff"')
    path.write_text(text,encoding='utf-8')

for skill in ['slidev-animejs','slidev-echarts']:
    css=ROOT/'skills'/skill/'assets/examples'/skill/'styles/index.css'
    text=css.read_text(encoding='utf-8')
    def rule(match):
        body=match.group()
        fill=re.search(r'background:\s*(#[\da-f]{6});',body)
        if fill and fill.group(1) in set(soft.values()):
            color='#000000' if fill.group(1) in black else '#ffffff'
            body=re.sub(r'(?<![\w-])color:\s*#[\da-f]{6}', 'color: '+color,body)
        return body
    text=re.sub(r'[^{}]+\{[^{}]*\}',rule,text)
    css.write_text(text,encoding='utf-8')

p=pack/'components/SvgAssetSlide.vue'
t=p.read_text(encoding='utf-8')
t=re.sub(r'border:\s*[\d.]+px solid #[\da-f]{6};','border: 0;',t)
p.write_text(t,encoding='utf-8')

p=ROOT/'skills/slidev-animejs/assets/examples/slidev-animejs/components/AnimeFeatureSlide.vue'
t=p.read_text(encoding='utf-8')
t=t.replace("backgroundColor: { from: '#cdf3ff', to: activeStep.value > 1 ? '#ffccd5' : '#dbffcc', ease: steps(1) },", "backgroundColor: { from: '#007298', to: activeStep.value > 1 ? '#9e1b32' : '#45842a', ease: steps(1) },\n    color: { from: '#ffffff', to: activeStep.value > 1 ? '#ffffff' : '#000000', ease: steps(1) },")
t=t.replace("backgroundColor: { from: '#cdf3ff', to: '#dbffcc', ease: steps(1) },", "backgroundColor: { from: '#007298', to: '#45842a', ease: steps(1) },\n    color: { from: '#ffffff', to: '#000000', ease: steps(1) },")
p.write_text(t,encoding='utf-8')

p=ROOT/'skills/slidev-echarts/assets/examples/slidev-echarts/components/GeneratedSvgMotion.vue'
t=p.read_text(encoding='utf-8').replace("const fills = ['#cdf3ff', '#cdf3ff', '#cdf3ff', '#ffe5cc', '#ffccd5']", "const fills = ['#007298', '#45842a', '#652f6c', '#e77204', '#9e1b32']").replace('opacity: 0.72,','opacity: 1,')
p.write_text(t,encoding='utf-8')

for mode in [1,2]:
    p=ROOT/f'skills/plantuml-colorset-renderer/assets/themes/cs{mode}.puml'
    t=p.read_text(encoding='utf-8').replace('arrow {\n  LineColor #696969','arrow {\n  LineThickness 1.5\n  LineColor #696969')
    t=t.replace('<style>\nroot', '<style>\ntitle {\n  LineThickness 0\n  BackgroundColor transparent\n}\nroot')
    # New activity renderer nests arrows under activityDiagram styles.
    t=t.replace('</style>', 'activityDiagram {\n  arrow {\n    LineColor #696969\n    LineThickness 1.5\n  }\n}\n</style>')
    p.write_text(t,encoding='utf-8')
print('Final portable surfaces and native meaningful arrow thickness repaired.')
