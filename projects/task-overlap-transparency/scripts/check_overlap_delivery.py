#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0", "Pillow>=11"]
# ///
"""Check portable SVG delivery, original data, and scoped alpha negative controls."""

import argparse
import importlib.util
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('overlap_verifier',Path(__file__).with_name('verify_overlap.py'))
verifier=importlib.util.module_from_spec(spec);spec.loader.exec_module(verifier)


def measure_pixels(state,png):
    image=Image.open(png).convert('RGB')
    for sample in state['samples']:
        x=round(sample['screenPoint']['x']);y=round(sample['screenPoint']['y'])
        pixel=list(image.getpixel((min(max(x,0),image.width-1),min(max(y,0),image.height-1))))
        sample['observedRgb']=pixel
        sample['maximumChannelError']=max(abs(a-b) for a,b in zip(pixel,sample['expectedRgb']))
        if sample['maximumChannelError']>5:state['findings'].append(f"Export pixel mismatch: {sample['memberships']} ({sample['maximumChannelError']:.3f} channel units).")
    state['clean']=not state['findings']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--baseline',type=Path,required=True)
    parser.add_argument('--output-directory',type=Path,required=True)
    parser.add_argument('--export-directory',type=Path,help="Directory of namespace-correct exported SVGs when distinct from native report captures.")
    parser.add_argument('--svg',type=Path,help="Inspect one standalone production SVG in all four viewport/motion states.")
    args=parser.parse_args();output=args.output_directory.resolve();output.mkdir(parents=True,exist_ok=True)
    native=json.loads(args.reference.read_text(encoding='utf-8'));baseline=json.loads(args.baseline.read_text(encoding='utf-8'))
    before=baseline['states'][0]
    palette=json.loads((ROOT/'skills/d3/assets/palettes/colorsets.json').read_text(encoding='utf-8'))['colorsets']['colorset1']
    reference={'regions':before['regions'],'tasks':before['tasks'],'dotRadius':2.25,'allowed':palette['allowed'],**before['invariants']}
    findings=[];comparisons=0
    for state in native['states']:
        if state['tasks']!=before['tasks']:findings.append(f"Native task/dot/leader/membership data changed: {state['width']}/{state['reducedMotion']}/{state['replay']}.")
        if state['invariants']!=before['invariants']:findings.append('Native membership/collision/crossing invariants changed.')
        for region,old in zip(state['regions'],before['regions']):
            if any(region[key]!=old[key] for key in ('id','cx','cy','r')):findings.append('Native scope region geometry changed.')
            comparisons+=1
        comparisons+=len(state['tasks'])
    result={'clean':False,'source':str(args.source),'nativeGeometryComparisons':comparisons,'nativeComparisonFindings':findings,'exports':[],'negativeControls':[],'errors':[]}
    with sync_playwright() as playwright:
        browser=verifier.launch(playwright)
        page=browser.new_page(viewport={'width':1440,'height':1100})
        page.on('pageerror',lambda error:result['errors'].append(str(error)))
        page.goto(args.source.resolve().as_uri(),wait_until='load',timeout=120000)
        page.locator('[data-example="task-overlap-dense"]').scroll_into_view_if_needed();page.wait_for_timeout(1600)
        page.evaluate("const svg=document.querySelector('[data-example=task-overlap-dense] svg');svg.pauseAnimations();svg.setCurrentTime(5)")
        controls={
          'opaque-set-regions':"svg.querySelectorAll('.overlap-circle').forEach(circle=>{remember(circle);circle.style.fillOpacity='1';circle.setAttribute('fill-opacity','1');});",
          'missing-semantic-declaration':"const circle=svg.querySelector('.overlap-circle');remember(circle);circle.removeAttribute('data-opacity-role');window.D3SolidStyle.normalize(svg);",
          'translucent-task-dot':"const dot=svg.querySelector('.task-dot');remember(dot);dot.style.fillOpacity='.28';dot.setAttribute('fill-opacity','.28');",
          'wrong-label-contrast':"const label=svg.querySelector('.task-label');remember(label);label.style.fill='#ffffff';label.setAttribute('fill','#ffffff');",
          'off-palette-region-fill':"const circle=svg.querySelector('.overlap-circle');remember(circle);circle.style.fill='#123456';circle.setAttribute('fill','#123456');"
        }
        for name,mutation in controls.items():
            code="""() => {const svg=document.querySelector('[data-example="task-overlap-dense"] svg'),saved=[];
              const remember=element=>saved.push({element,attributes:[...element.attributes].map(attribute=>[attribute.name,attribute.value])});
            """+mutation+'\nconst result=('+verifier.INSPECT+")(null);\n"+"""
              saved.forEach(({element,attributes})=>{[...element.attributes].forEach(attribute=>element.removeAttribute(attribute.name));attributes.forEach(([name,value])=>element.setAttribute(name,value));});return result;
            }"""
            checked=page.evaluate(code)
            result['negativeControls'].append({'name':name,'rejected':not checked['clean'],'findings':checked['findings']})
        result['ordinaryOpaqueControl']=page.evaluate("""() => {
          const svg=document.querySelector('[data-example="task-overlap-dense"] svg'),probe=document.createElementNS(svg.namespaceURI,'rect');
          probe.setAttribute('x','-50');probe.setAttribute('y','-50');probe.setAttribute('width','8');probe.setAttribute('height','8');probe.setAttribute('fill','#9e1b32');probe.setAttribute('fill-opacity','.28');svg.append(probe);
          window.D3SolidStyle.normalize(svg);
          const result={ordinaryAlpha:Number(getComputedStyle(probe).fillOpacity),semanticAlphas:[...svg.querySelectorAll('.overlap-circle')].map(circle=>Number(getComputedStyle(circle).fillOpacity))};probe.remove();return result;
        }""")
        page.close()
        for width in [1440,390]:
            for reduced in [False,True]:
                source=args.svg or (args.export_directory or args.reference.parent)/f"overlap-{width}-{'reduced' if reduced else 'normal'}-0.svg"
                page=browser.new_page(viewport={'width':width,'height':1100},reduced_motion='reduce' if reduced else 'no-preference')
                page.on('pageerror',lambda error:result['errors'].append(str(error)))
                page.goto(source.resolve().as_uri(),wait_until='load',timeout=120000);page.wait_for_timeout(4000)
                page.evaluate('const svg=document.querySelector("svg");svg.pauseAnimations();svg.setCurrentTime(5)')
                state=page.evaluate(verifier.INSPECT,{'reference':reference});state.update({'width':width,'reducedMotion':reduced,'source':str(source)})
                png=output/f"export-{width}-{'reduced' if reduced else 'normal'}.png";page.locator('svg').screenshot(path=str(png));measure_pixels(state,png)
                if state['tasks']!=before['tasks']:state['findings'].append('Portable SVG task/leader/membership data differs from native baseline.')
                state['clean']=not state['findings'];result['exports'].append(state);page.close()
        browser.close()
    opaque=result['ordinaryOpaqueControl']
    result['clean']=not findings and not result['errors'] and all(state['clean'] for state in result['exports']) and all(control['rejected'] for control in result['negativeControls']) and opaque['ordinaryAlpha']==1 and all(abs(alpha-.28)<.00001 for alpha in opaque['semanticAlphas'])
    (output/'delivery.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'clean':result['clean'],'nativeGeometryComparisons':comparisons,'exports':len(result['exports']),'negativeControls':len(result['negativeControls']),'findings':findings,'errors':result['errors'],'report':str(output/'delivery.json')},indent=2))
    return 0 if result['clean'] else 1


if __name__=='__main__':raise SystemExit(main())
