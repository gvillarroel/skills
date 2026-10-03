/* Evaluator-side marker geometry and local-backing checks, independent of skills.
   Loaded by Playwright with page.add_script_tag.
   Syntax: node --experimental-strip-types --check projects/arrow-contrast-custom/scripts/arrow_audit.ts. */
window.auditRenderedArrows = function () {
  const channels = paint => { const match=(paint||'').match(/^rgba?\(([^)]+)\)/); return match ? match[1].split(/[, ]+/).map(Number) : null; };
  const lum = rgb => rgb.slice(0,3).map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
  const contrast = (a,b) => (Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
  const composite = (paint,bg,alpha) => paint.slice(0,3).map((value,index)=>value*alpha+bg[index]*(1-alpha));
  const opacity = (element,property='opacity') => {let alpha=property==='opacity'?1:+getComputedStyle(element)[property];for(let node=element;node;node=node.parentElement)alpha*=+getComputedStyle(node).opacity;return alpha;};
  const rows=[];
  document.querySelectorAll('svg').forEach(svg=>{
    const all=[...svg.querySelectorAll('*')];
    const shapes=all.filter(node=>node.matches('rect,circle,ellipse,polygon,path')&&!node.closest('defs,mask,clipPath,pattern'));
    const backing=(point,owner)=>{
      let bg=[255,255,255],cover=[];
      for(const shape of shapes){
        if(shape===owner)continue;
        const style=getComputedStyle(shape),paint=channels(style.fill);
        if(!paint||style.display==='none'||style.visibility==='hidden'||opacity(shape)===0)continue;
        let hit=false;try{hit=shape.isPointInFill(point.matrixTransform(shape.getScreenCTM().inverse()));}catch{}
        for(let ancestor=shape.parentElement;hit&&ancestor&&ancestor!==svg;ancestor=ancestor.parentElement){
          const reference=getComputedStyle(ancestor).clipPath.match(/#([^"')]+)/)?.[1],clip=reference&&svg.querySelector('#'+CSS.escape(reference)+' path');
          if(clip)try{hit=clip.isPointInFill(point.matrixTransform(clip.getScreenCTM().inverse()));}catch{}
        }
        if(hit){bg=composite(paint,bg,opacity(shape,'fillOpacity')*(paint[3]??1));if(all.indexOf(shape)>all.indexOf(owner))cover.push(shape.id||shape.getAttribute('class')||shape.localName);}
      }
      return {bg,cover};
    };
    all.filter(node=>node.matches('path,line,polyline')&&getComputedStyle(node).markerEnd!=='none').forEach(owner=>{
      const style=getComputedStyle(owner),identifier=style.markerEnd.match(/#([^"')]+)/)?.[1];
      const marker=identifier&&svg.querySelector('#'+CSS.escape(identifier));
      const mark=marker?.querySelector('path,polygon,circle');
      if(!mark||!owner.getTotalLength)return;
      const length=owner.getTotalLength(),end=owner.getPointAtLength(length),previous=owner.getPointAtLength(Math.max(0,length-.5));
      const angle=Math.atan2(end.y-previous.y,end.x-previous.x),box=mark.getBBox(),view=marker.viewBox.baseVal;
      const unit=marker.getAttribute('markerUnits')==='userSpaceOnUse'?1:parseFloat(style.strokeWidth);
      const scale=marker.markerWidth.baseVal.value/(view.width||box.width)*unit;
      const x=(box.x+box.width*.55-marker.refX.baseVal.value)*scale;
      const y=(box.y+box.height*.5-marker.refY.baseVal.value)*scale;
      const headLocal=new DOMPoint(end.x+Math.cos(angle)*x-Math.sin(angle)*y,end.y+Math.sin(angle)*x+Math.cos(angle)*y);
      const headPoint=headLocal.matrixTransform(owner.getScreenCTM()),headBacking=backing(headPoint,owner);
      const headStyle=getComputedStyle(mark),headRaw=headStyle.fill==='none'?headStyle.stroke:headStyle.fill==='context-stroke'?style.stroke:headStyle.fill;
      const headPaint=channels(headRaw),shaftPaint=channels(style.stroke);
      const headAlpha=opacity(owner)*+headStyle.fillOpacity*(headPaint?.[3]??1),shaftAlpha=opacity(owner,'strokeOpacity')*(shaftPaint?.[3]??1);
      const samples=Array.from({length:127},(_,i)=>(i+1)/128).map(fraction=>{const local=owner.getPointAtLength(length*fraction),point=new DOMPoint(local.x,local.y).matrixTransform(owner.getScreenCTM()),under=backing(point,owner);return {fraction,backing:under.bg,cover:under.cover,contrast:shaftPaint?contrast(composite(shaftPaint,under.bg,shaftAlpha),under.bg):null};});
      // Actual triangles are sampled near both wings, the tip and the interior,
      // independently of the helper's four silhouette probes and shaft finalizer.
      const headSamples=[[.05,.08],[.05,.92],[.95,.5],[.55,.5],[.2,.4],[.2,.6]].map(([fx,fy])=>{
        const lx=(box.x+box.width*fx-marker.refX.baseVal.value)*scale;
        const ly=(box.y+box.height*fy-marker.refY.baseVal.value)*scale;
        const point=new DOMPoint(end.x+Math.cos(angle)*lx-Math.sin(angle)*ly,end.y+Math.sin(angle)*lx+Math.cos(angle)*ly).matrixTransform(owner.getScreenCTM());
        const under=backing(point,owner);
        return {fraction:[fx,fy],backing:under.bg,cover:under.cover,contrast:headPaint?contrast(composite(headPaint,under.bg,headAlpha),under.bg):null};
      });
      const headRatio=Math.min(...headSamples.map(sample=>sample.contrast??0));
      const targetId=owner.dataset.target||owner.__data__?.target?.id||owner.__data__?.target;
      const targetCircle=typeof targetId==='string'&&svg.querySelector('[data-instrument-id="'+CSS.escape(targetId)+'"] circle');
      let targetPortAudit=null;
      if(targetCircle){
        const matrix=targetCircle.getScreenCTM(),center=new DOMPoint(+targetCircle.getAttribute('cx'),+targetCircle.getAttribute('cy')).matrixTransform(matrix);
        const tx=(box.x+box.width-marker.refX.baseVal.value)*scale,ty=(box.y+box.height*.5-marker.refY.baseVal.value)*scale;
        const tip=new DOMPoint(end.x+Math.cos(angle)*tx-Math.sin(angle)*ty,end.y+Math.sin(angle)*tx+Math.cos(angle)*ty).matrixTransform(owner.getScreenCTM());
        const tangent=new DOMPoint(end.x-previous.x,end.y-previous.y).matrixTransform(new DOMMatrix([owner.getScreenCTM().a,owner.getScreenCTM().b,owner.getScreenCTM().c,owner.getScreenCTM().d,0,0]));
        const delta=[center.x-tip.x,center.y-tip.y],distance=Math.hypot(...delta),screenScale=Math.hypot(matrix.a,matrix.b);
        const alignment=(delta[0]*tangent.x+delta[1]*tangent.y)/(distance*Math.hypot(tangent.x,tangent.y));
        const clearance=distance/screenScale-(+targetCircle.getAttribute('r'));
        targetPortAudit={targetId,alignment,clearance,passed:alignment>=.99&&clearance>=3.99};
      }
      const callout=owner.closest('[data-gap-id]'),barrierId=callout?.dataset.barrierId;
      const targetRect=barrierId&&svg.querySelector('[data-barrier-id="'+CSS.escape(barrierId)+'"] rect');
      if(targetRect){
        const matrix=targetRect.getScreenCTM(),bounds=targetRect.getBBox();
        const center=new DOMPoint(bounds.x+bounds.width/2,bounds.y+bounds.height/2).matrixTransform(matrix);
        const tx=(box.x+box.width-marker.refX.baseVal.value)*scale,ty=(box.y+box.height*.5-marker.refY.baseVal.value)*scale;
        const tip=new DOMPoint(end.x+Math.cos(angle)*tx-Math.sin(angle)*ty,end.y+Math.sin(angle)*tx+Math.cos(angle)*ty).matrixTransform(owner.getScreenCTM());
        const localTip=tip.matrixTransform(matrix.inverse());
        const tangent=new DOMPoint(end.x-previous.x,end.y-previous.y).matrixTransform(new DOMMatrix([owner.getScreenCTM().a,owner.getScreenCTM().b,owner.getScreenCTM().c,owner.getScreenCTM().d,0,0]));
        const delta=[center.x-tip.x,center.y-tip.y],alignment=(delta[0]*tangent.x+delta[1]*tangent.y)/(Math.hypot(...delta)*Math.hypot(tangent.x,tangent.y));
        const clearance=bounds.y-localTip.y;
        targetPortAudit={targetId:barrierId,port:'top',alignment,clearance,passed:alignment>=.99&&clearance>=3.99&&localTip.x>=bounds.x&&localTip.x<=bounds.x+bounds.width};
      }
      rows.push({pattern:svg.dataset.patternId||svg.id,owner:owner.id||owner.getAttribute('class')||owner.localName,marker:identifier,source:owner.__data__?.source?.id||owner.__data__?.source||null,target:owner.__data__?.target?.id||owner.__data__?.target||null,
        headPaint:headRaw,shaftPaint:style.stroke,headAlpha,shaftAlpha,headContrast:headRatio,headBacking:headBacking.bg,headCover:[...new Set(headSamples.flatMap(sample=>sample.cover))],headSamples,shaftMinimumContrast:Math.min(...samples.filter(sample=>!sample.cover.length).map(sample=>sample.contrast??0)),shaftSamples:samples,
        declaredContrast:owner.dataset.arrowContrast,unresolved:owner.dataset.arrowUnresolved,retreat:owner.dataset.arrowClearance,terminalScope:owner.dataset.arrowTerminalPaint,
        targetPortAudit,
        headHidden:headSamples.some(sample=>sample.cover.length>0),markerMismatch:headRaw!==style.stroke,visible:opacity(owner)>0});
    });
  });
  return rows;
};
