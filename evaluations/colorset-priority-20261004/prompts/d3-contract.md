Run the exact compact standalone command below and inspect its outputs. Treat `skills/d3/` as read-only. Use only the copied skill and normal local tools; do not inspect acceptance examples, sibling skills, parent run records, repository context, or outside source files. Keep generated files in this workspace. The contract records the public allocator's returned styles on two actual canvases, including its first overflow slot, or exercises the owning native builder. Do not alter the bundled helpers.

```bash
node --input-type=commonjs - <<'JS'
const fs = require('node:fs'), vm = require('node:vm');
const palettes = JSON.parse(fs.readFileSync('skills/d3/assets/palettes/colorsets.json','utf8')).colorsets;
const context = { window: { D3_SOLID_PALETTES: palettes }, document: { readyState: 'loading', addEventListener(){} }, MutationObserver: class { observe(){} }, requestAnimationFrame(){} };
vm.createContext(context);
vm.runInContext(fs.readFileSync('skills/d3/assets/templates/solid-style.js','utf8'), context);
const canvases = ['#ffffff','#000000'].map(canvas => {
  const count = palettes.colorset1.solidSequence.filter(paint => paint !== canvas).length;
  return {canvas, styles:Array.from({length:count+1},(_,index)=>context.window.D3SolidStyle.categoryStyle(index,'colorset1',canvas))};
});
fs.writeFileSync('contract.json', JSON.stringify({colorset:'colorset1',canvases},null,2)+'\n');
const vendor=fs.readFileSync('skills/d3/assets/vendor/d3.v7.9.0.min.js','utf8');
const code=`const canvases=${JSON.stringify(canvases)}; canvases.forEach(entry=>{const svg=d3.select('main').append('svg').attr('viewBox','0 0 504 390').attr('data-canvas',entry.canvas).style('background',entry.canvas);const rows=svg.selectAll('g').data(entry.styles).join('g').attr('data-category-index',(_,i)=>i).attr('transform',(_,i)=>'translate('+(12+i%4*123)+','+(12+Math.floor(i/4)*74)+')');rows.append('rect').attr('width',110).attr('height',58).attr('fill',d=>d.fill).attr('stroke',d=>d.stroke).attr('stroke-width',d=>d.strokeWidth).attr('stroke-dasharray',d=>d.strokeDasharray);rows.append('text').attr('x',55).attr('y',34).attr('text-anchor','middle').attr('font-size',14).attr('font-family','Arial').attr('fill',d=>d.text).text((_,i)=>'Group '+i);});`;
fs.writeFileSync('contract.html','<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Category canvases</title><style>body{margin:0;padding:12px;background:#ffffff}main{max-width:1040px;display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:12px}svg{width:100%;height:auto;display:block}</style><main></main><script>'+vendor+'</script><script>'+code+'</script></html>');
JS
```
