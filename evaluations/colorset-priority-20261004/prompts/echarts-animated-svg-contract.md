Run the exact compact standalone command below and inspect its outputs. Treat `skills/echarts-animated-svg/` as read-only. Use only the copied skill and normal local tools; do not inspect acceptance examples, sibling skills, parent run records, repository context, or outside source files. Keep generated files in this workspace. The contract records the public allocator's returned styles on two actual canvases, including its first overflow slot, or exercises the owning native builder. Do not alter the bundled helpers.

```bash
npm install --no-audit --no-fund echarts@6.1.0
node --input-type=module - <<'JS'
import fs from 'node:fs';
import * as echarts from 'echarts';
import { solidColors, solidCategoryStyle, prepareColorsetOption, insetGraphArrowRoutes, qualifyBoxplotMedians, normalizeSvgPaints } from './skills/echarts-animated-svg/assets/templates/echarts-colorsets.mjs';
const canvases = ['#ffffff','#000000'].map(canvas => {
  const styles = solidColors('colorset1',canvas).map((_,index)=>solidCategoryStyle(index,'colorset1',canvas));
  styles.push(solidCategoryStyle(styles.length,'colorset1',canvas));
  const option={animation:false,backgroundColor:canvas,series:[{type:'graph',layout:'none',symbol:'rect',symbolSize:[72,32],label:{show:true,position:'inside'},edgeSymbol:['none','arrow'],data:styles.map((_,i)=>({id:'g'+i,name:'Group '+i,x:60+(i%6)*95,y:50+Math.floor(i/6)*65})),links:[{source:'g0',target:'g1'}]}]};
  prepareColorsetOption(option,'colorset1',option.series[0].data.map(node=>node.id));
  const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width:960,height:540});
  chart.setOption(option);
  insetGraphArrowRoutes(chart,3);
  qualifyBoxplotMedians(chart,echarts,'colorset1');
  fs.writeFileSync(canvas==='#ffffff'?'priority.white.static.svg':'priority.dark.static.svg',normalizeSvgPaints(chart.renderToSVGString(),'colorset1'));
  chart.dispose();
  const boxplot={animation:false,backgroundColor:canvas,xAxis:{type:'category',data:['Batch A','Batch B']},yAxis:{type:'value'},series:[{type:'boxplot',data:[[1,2,3,4,5],[2,3,4,5,6]]},{type:'boxplot',data:[[2,3,4,5,6],[3,4,5,6,7]]}]};
  prepareColorsetOption(boxplot,'colorset1');
  const boxChart=echarts.init(null,null,{renderer:'svg',ssr:true,width:960,height:540});
  boxChart.setOption(boxplot);
  insetGraphArrowRoutes(boxChart,3);
  const medianQualification=qualifyBoxplotMedians(boxChart,echarts,'colorset1');
  fs.writeFileSync(canvas==='#ffffff'?'boxplot.white.static.svg':'boxplot.dark.static.svg',normalizeSvgPaints(boxChart.renderToSVGString(),'colorset1'));
  boxChart.dispose();
  return {canvas,styles,preparedOption:option,boxplotPreparedOption:boxplot,medianQualification};
});
fs.writeFileSync('contract.json',JSON.stringify({colorset:'colorset1',canvases},null,2)+'\n');
JS
```
