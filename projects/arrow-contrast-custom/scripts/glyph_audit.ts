/* Evaluator browser payload, loaded by the owning Playwright probe.
   Syntax: node --experimental-strip-types --check projects/arrow-contrast-custom/scripts/glyph_audit.ts.
   D3's field triangles and pump symbol are intentional direction silhouettes. */
window.auditDirectionalGlyphs = function () {
  const rgb = paint => paint.match(/[\d.]+/g).slice(0,3).map(Number);
  const lum = values => values.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
  const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
  const rows=[];
  document.querySelectorAll('.pid-pump').forEach(group=>{
    const glyph=group.querySelector('path'),back=group.querySelector('circle');
    const box=glyph.getBBox(),at=new DOMPoint(box.x+box.width*.2,box.y+box.height*.5).matrixTransform(glyph.getScreenCTM());
    const local=at.matrixTransform(back.getScreenCTM().inverse());
    rows.push({pattern:group.closest('svg').dataset.patternId,role:'pump-direction',paint:getComputedStyle(glyph).fill,backing:getComputedStyle(back).fill,contrast:ratio(rgb(getComputedStyle(glyph).fill),rgb(getComputedStyle(back).fill)),declared:glyph.dataset.directionContrast,declaredBackings:glyph.dataset.directionBackings,unresolved:glyph.dataset.arrowUnresolved,tagged:glyph.dataset.directionRole,backingHit:back.isPointInFill(local),local:[local.x,local.y],underlays:[...group.closest('svg').querySelectorAll('rect,circle,ellipse,path,polygon')].filter(s=>s!==glyph&&!s.closest('defs')&&getComputedStyle(s).fill!=='none'&&s.isPointInFill(at.matrixTransform(s.getScreenCTM().inverse()))).map(s=>({tag:s.localName,fill:getComputedStyle(s).fill,opacity:getComputedStyle(s).opacity,cls:s.getAttribute('class')}))});
  });
  document.querySelectorAll('svg').forEach(svg=>{
    if(!(svg.dataset.patternId||'').startsWith('d3-vector-field'))return;
    svg.querySelectorAll('g').forEach(group=>{
      const head=group.querySelector(':scope > path'),shaft=group.querySelector(':scope > line');
      if(!head||!shaft)return;
      rows.push({pattern:svg.dataset.patternId,role:'vector-glyph',head:getComputedStyle(head).fill,shaft:getComputedStyle(shaft).stroke,headContrast:ratio(rgb(getComputedStyle(head).fill),[255,255,255]),shaftContrast:ratio(rgb(getComputedStyle(shaft).stroke),[255,255,255])});
    });
  });
  return rows;
};
