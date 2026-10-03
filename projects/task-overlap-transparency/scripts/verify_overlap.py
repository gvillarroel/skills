#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright>=1.52.0", "Pillow>=11"]
# ///
"""Independently verify semantic overlap alpha, data, labels and rendered pixels."""

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image
from playwright.sync_api import Error, sync_playwright


INSPECT=r"""options => {
  const reference=options?.reference;
  const svg=document.querySelector('[data-example="task-overlap-dense"] svg') || document.querySelector('svg');
  const findings=[];
  const regions=[...svg.querySelectorAll('circle.overlap-circle')];
  const layout=window.D3_TASK_OVERLAP_LAYOUTS?.saturated || reference;
  const colorset=svg.dataset.colorset || svg.dataset.colorSet || document.body?.dataset.colorset || document.body?.dataset.colorSet || reference?.colorset;
  const allowed=new Set(window.D3_SOLID_PALETTES?.[colorset]?.allowed || reference.allowed);
  const parse=value=>{
    if (/^#[0-9a-f]{6}$/i.test(value)) return [1,3,5].map(i=>parseInt(value.slice(i,i+2),16));
    const channels=value.match(/^rgba?\(([^)]+)\)$/)?.[1].split(/[ ,/]+/).map(Number);
    return channels?.slice(0,3);
  };
  const hex=values=>'#'+values.map(v=>Math.round(v).toString(16).padStart(2,'0')).join('');
  const alpha=element=>{
    let value=Number(getComputedStyle(element).fillOpacity);
    for(let node=element;node&&node!==svg.parentElement;node=node.parentElement)value*=Number(getComputedStyle(node).opacity);
    return value;
  };
  const luminance=color=>parse(color).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
  const contrast=(a,b)=>(Math.max(luminance(a),luminance(b))+.05)/(Math.min(luminance(a),luminance(b))+.05);
  const inside=(element,point)=>{try{return element.isPointInFill(point.matrixTransform(element.getScreenCTM().inverse()));}catch{return false;}};
  const paints=[...svg.querySelectorAll('rect,circle,path,polygon')].filter(element=>!element.closest('defs,mask,clipPath'));
  const compositeAt=(point,objects=paints)=>{
    let color=[255,255,255];
    for(const element of objects){const style=getComputedStyle(element),fill=parse(style.fill);if(!fill||style.display==='none'||style.visibility==='hidden'||!inside(element,point))continue;
      const amount=alpha(element);color=fill.map((v,i)=>v*amount+color[i]*(1-amount));
    }
    return {rgb:color,hex:hex(color)};
  };
  const regionResults=regions.map(region=>{
    const style=getComputedStyle(region),data=region.__data__ || reference.regions.find(item=>item.id===region.dataset.setId),fill=hex(parse(style.fill));
    if(region.dataset.opacityRole!=='semantic')findings.push(`${data.id}: semantic opacity is undeclared.`);
    if(Math.abs(Number(style.fillOpacity)-.28)>.00001 || Math.abs(alpha(region)-.28)>.00001)findings.push(`${data.id}: expected readable semantic alpha .28, found ${alpha(region)}.`);
    if(style.stroke!=='none'&&Number(style.strokeOpacity)>0)findings.push(`${data.id}: region has a decorative border.`);
    if(!allowed.has(fill))findings.push(`${data.id}: authored region fill is outside ${colorset}.`);
    if(region.cx.baseVal.value!==data.cx||region.cy.baseVal.value!==data.cy||region.r.baseVal.value!==data.r)findings.push(`${data.id}: set geometry changed.`);
    return {id:data.id,cx:region.cx.baseVal.value,cy:region.cy.baseVal.value,r:region.r.baseVal.value,fill,alpha:alpha(region),semantic:region.dataset.opacityRole==='semantic',stroke:style.stroke};
  });
  const dots=[...svg.querySelectorAll('circle.task-dot')];
  const leaders=[...svg.querySelectorAll('line.task-leader')];
  const groups=[...svg.querySelectorAll('g.task-label-group')];
  if(regions.length!==9||dots.length!==100||leaders.length!==100||groups.length!==100)findings.push('Expected 9 regions, 100 task dots, 100 leaders and 100 label groups.');
  const taskResults=dots.map(dot=>{
    const data=dot.__data__ || reference.tasks.find(item=>item.id===dot.dataset.taskId), label=groups.find(group=>group.dataset.taskId===data.id),leader=leaders.find(line=>line.dataset.taskId===data.id);
    if(Math.abs(dot.cx.baseVal.value-data.x)>.001||Math.abs(dot.cy.baseVal.value-data.y)>.001||Math.abs(dot.r.baseVal.value-layout.dotRadius)>.00001)findings.push(`${data.id}: task geometry changed.`);
    if(dot.dataset.memberships!==data.memberships.join(' ')||Number(dot.dataset.membershipCount)!==(data.membershipCount ?? data.memberships.length)||label?.querySelector('text')?.textContent!==data.label)findings.push(`${data.id}: task data/membership/label changed.`);
    if(alpha(dot)<.999||alpha(label.querySelector('rect'))<.999)findings.push(`${data.id}: a task dot or label face became translucent.`);
    return {id:data.id,x:data.x,y:data.y,memberships:data.memberships,label:data.label,
      leader:{x1:leader.x1.baseVal.value,y1:leader.y1.baseVal.value,x2:leader.x2.baseVal.value,y2:leader.y2.baseVal.value}};
  });
  const labelResults=[...svg.querySelectorAll('text')].map(text=>{
    const box=text.getBoundingClientRect(),point=new DOMPoint(box.x+box.width/2,box.y+box.height/2), backing=compositeAt(point).hex,paint=hex(parse(getComputedStyle(text).fill));
    const black=contrast('#000000',backing),white=contrast('#ffffff',backing),expected=black>=white?'#000000':'#ffffff';
    if(paint!==expected)findings.push(`${text.textContent}: label is not maximum-contrast black/white over ${backing}.`);
    if(contrast(paint,backing)<4.5)findings.push(`${text.textContent}: label contrast is below 4.5:1.`);
    return {text:text.textContent,fill:paint,backing,contrast:contrast(paint,backing)};
  });
  const lines=[...svg.querySelectorAll('line')];
  const unobstructed=point=>{
    if(dots.some(dot=>{const p=point.matrixTransform(dot.getScreenCTM().inverse());return Math.hypot(p.x-dot.cx.baseVal.value,p.y-dot.cy.baseVal.value)<dot.r.baseVal.value+4;}))return false;
    if(lines.some(line=>{const p=point.matrixTransform(line.getScreenCTM().inverse()),x1=line.x1.baseVal.value,y1=line.y1.baseVal.value,x2=line.x2.baseVal.value,y2=line.y2.baseVal.value,t=Math.max(0,Math.min(1,((p.x-x1)*(x2-x1)+(p.y-y1)*(y2-y1))/((x2-x1)**2+(y2-y1)**2)));return Math.hypot(p.x-(x1+t*(x2-x1)),p.y-(y1+t*(y2-y1)))<4;}))return false;
    return ![...svg.querySelectorAll('text')].some(text=>{const b=text.getBoundingClientRect();return point.x>b.x-3&&point.x<b.right+3&&point.y>b.y-3&&point.y<b.bottom+3;});
  };
  const samples=[],seen=new Set();
  for(let y=35;y<410;y+=5)for(let x=195;x<700;x+=5){
    const point=new DOMPoint(x,y).matrixTransform(svg.getScreenCTM());
    const matching=regions.filter(region=>inside(region,point));
    if(!matching.length||matching.length>4||seen.has(matching.length)||!unobstructed(point))continue;
    if(matching.some(region=>{const p=point.matrixTransform(region.getScreenCTM().inverse());return Math.abs(Math.hypot(p.x-region.cx.baseVal.value,p.y-region.cy.baseVal.value)-region.r.baseVal.value)<5;}))continue;
    const result=compositeAt(point,regions), box=(svg.closest('[data-example]') || svg).getBoundingClientRect();
    samples.push({multiplicity:matching.length,memberships:matching.map(region=>region.dataset.setId),svgPoint:{x,y},screenPoint:{x:point.x-box.x,y:point.y-box.y},expectedRgb:result.rgb,expectedHex:result.hex});seen.add(matching.length);
  }
  if(![1,2,3].every(value=>seen.has(value)))findings.push('Missing clear single/double/triple overlap samples.');
  return {clean:findings.length===0,findings,patternId:svg.dataset.patternId,colorset,regions:regionResults,tasks:taskResults,labels:labelResults,samples,
    invariants:{membershipBuckets:layout.membershipBuckets,labelOverlapCount:layout.labelOverlapCount,labelCircleOverlapCount:layout.labelCircleOverlapCount,labelDotOverlapCount:layout.labelDotOverlapCount,labelLeaderOverlapCount:layout.labelLeaderOverlapCount,leaderCrossingCount:layout.leaderCrossingCount,sameColorLeaderCrossingCount:layout.sameColorLeaderCrossingCount}};
}"""


def launch(playwright):
    try:
        return playwright.chromium.launch()
    except Error as error:
        for channel,path in [("msedge",Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")),("chrome",Path("C:/Program Files/Google/Chrome/Application/chrome.exe"))]:
            if path.exists():return playwright.chromium.launch(channel=channel)
        raise error


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("--output-directory",type=Path,required=True)
    parser.add_argument("--baseline",action="store_true")
    parser.add_argument("--quick",action="store_true")
    parser.add_argument("--replays",type=int,choices=(1,2,3),default=3,help="Number of settled initial/replay states per viewport/motion mode.")
    args=parser.parse_args()
    output=args.output_directory.resolve();output.mkdir(parents=True,exist_ok=True)
    source=args.source if args.source.startswith(('http://','https://')) else Path(args.source).resolve().as_uri()
    result={"source":args.source,"baseline":args.baseline,"states":[],"errors":[],"clean":False}
    with sync_playwright() as playwright:
        browser=launch(playwright)
        for width in ((1440,) if args.quick else (1440,390)):
            for reduced in ((False,) if args.quick else (False,True)):
                context=browser.new_context(viewport={"width":width,"height":1100},reduced_motion="reduce" if reduced else "no-preference")
                page=context.new_page();page.on('pageerror',lambda error:result['errors'].append(str(error)))
                page.goto(source,wait_until='load',timeout=120000)
                card=page.locator('[data-example="task-overlap-dense"]');card.scroll_into_view_if_needed()
                if width==390:card.evaluate('element=>element.scrollLeft=(element.scrollWidth-element.clientWidth)/2')
                for replay in range(1 if args.quick else args.replays):
                    if replay:card.locator('[data-replay]').click()
                    if width==390:card.evaluate('element=>element.scrollLeft=(element.scrollWidth-element.clientWidth)/2')
                    page.wait_for_timeout(1600)
                    page.evaluate("const svg=document.querySelector('[data-example=task-overlap-dense] svg');svg.pauseAnimations();svg.setCurrentTime(5)")
                    page.wait_for_timeout(100)
                    state=page.evaluate(INSPECT);state.update({"width":width,"reducedMotion":reduced,"replay":replay})
                    stem=f"overlap-{width}-{'reduced' if reduced else 'normal'}-{replay}"
                    svg=card.locator('svg');png=output/f"{stem}.png";card.screenshot(path=str(png),animations='allow')
                    image=Image.open(png).convert('RGB')
                    for sample in state['samples']:
                        x=round(sample['screenPoint']['x']);y=round(sample['screenPoint']['y'])
                        pixel=list(image.getpixel((min(max(x,0),image.width-1),min(max(y,0),image.height-1))));sample['observedRgb']=pixel
                        sample['maximumChannelError']=max(abs(a-b) for a,b in zip(pixel,sample['expectedRgb']))
                        if sample['maximumChannelError']>5:state['findings'].append(f"Pixel sample {sample['memberships']} differs from actual alpha composite by {sample['maximumChannelError']:.3f} channel units.")
                    state['clean']=not state['findings'];result['states'].append(state)
                    if replay==0:
                        card.screenshot(path=str(output/f"{stem}-card.png"))
                        serialized=svg.evaluate("""node=>{
                          const clone=node.cloneNode(true),originals=[...node.querySelectorAll('text')],copies=[...clone.querySelectorAll('text')];
                          originals.forEach((text,index)=>{const style=getComputedStyle(text);for(const property of ['font-family','font-size','font-weight'])copies[index].style.setProperty(property,style.getPropertyValue(property));});
                          return new XMLSerializer().serializeToString(clone);
                        }""")
                        (output/f"{stem}.svg").write_text(serialized,encoding='utf-8')
                context.close()
        browser.close()
    result['clean']=not result['errors'] and all(state['clean'] for state in result['states'])
    path=output/'verification.json';path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({"clean":result['clean'],"states":len(result['states']),"findings":sum(len(state['findings']) for state in result['states']),"errors":result['errors'],"report":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()},indent=2))
    return 0 if result['clean'] or (args.baseline and not result['errors']) else 1


if __name__=='__main__':raise SystemExit(main())
