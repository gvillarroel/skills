// Run: node projects/diagram-solid-style/scripts/test-echarts-rendered.mjs
// Uses the existing local ECharts acceptance dependency for real SVG SSR.
import assert from 'node:assert/strict'
import { createRequire } from 'node:module'
import { mkdirSync, writeFileSync } from 'node:fs'
const root = new URL('../../../',import.meta.url)
const require = createRequire(new URL('skills/echarts-animated-svg/assets/examples/echarts-animated-svg/package.json',root))
const echarts = require('echarts')
const output = new URL('projects/diagram-solid-style/artifacts/ssr/',root)
mkdirSync(output,{recursive:true})
const rows=[]
for (const skill of ['echarts-animated-svg','slidev-echarts']) {
  const h=await import(new URL(`skills/${skill}/assets/templates/echarts-colorsets.mjs`,root))
  const render = (name,option,expected) => {
    const prepared=h.prepareColorsetOption(structuredClone({animation:false,...option}),'colorset1')
    const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width:640,height:360})
    chart.setOption(prepared)
    const svg=chart.renderToSVGString()
    chart.dispose()
    writeFileSync(new URL(`${skill}-${name}.svg`,output),svg)
    const text=[...svg.matchAll(/<text\b([^>]*)>([^<]*)<\/text>/g)].filter(m=>expected[m[2]])
    assert.equal(text.length,Object.keys(expected).length,`${skill}/${name}: required actual labels`)
    for (const match of text) {
      assert.equal(/\bfill="([^"]+)"/.exec(match[1])?.[1],expected[match[2]],`${skill}/${name}/${match[2]}: actual text fill`)
      const stroke=/\bstroke="([^"]+)"/.exec(match[1])?.[1]
      const width=Number(/\bstroke-width="([^"]+)"/.exec(match[1])?.[1] ?? 0)
      assert(stroke === undefined || stroke === 'none' || width === 0,`${skill}/${name}: decorative text halo`)
    }
    rows.push({skill,case:name,passed:true,texts:text.map(m=>m[0])})
  }
  for (const type of ['pie','funnel']) render(`${type}-outer`,{series:[{type,label:{show:true},data:[{id:'A',name:'A',value:1},{id:'B',name:'B',value:2}]}]},{A:'#000000',B:'#000000'})
  render('graph-default',{series:[{type:'graph',layout:'circular',symbolSize:80,label:{show:true},data:[{id:'A',name:'A',value:1},{id:'B',name:'B',value:2}],links:[{source:'A',target:'B'}]}]},{A:'#ffffff',B:'#ffffff'})
  render('white-label-backing',{xAxis:{type:'category',data:['x']},yAxis:{},series:[{type:'bar',itemStyle:{color:'#9e1b32'},label:{show:true,position:'inside',backgroundColor:'#ffffff',formatter:'Backing'},data:[1]}]},{Backing:'#000000'})
  render('inherited-outer',{series:[{type:'pie',label:{show:true,position:'outside',backgroundColor:'#ffffff'},data:[{name:'A',value:1},{name:'B',value:2,label:{position:'inside',backgroundColor:'#ffffff'}}]}]},{A:'#000000',B:'#000000'})
  for (const canvas of ['rgba(158,27,50,1)','#9e1b32ff','rgba(255,255,255,1)','#ffffffff']) {
    const prepared=h.prepareColorsetOption({backgroundColor:canvas,series:[{type:'pie',data:[{id:'A',name:'A',value:1}]}]},'colorset1')
    const token=canvas.includes('158') || canvas.startsWith('#9e') ? '#9e1b32' : '#ffffff'
    assert(!prepared.color.includes(token),`${skill}: equivalent canvas token`)
    assert.notEqual(prepared.series[0].data[0].itemStyle.color,token)
  }
  for (const backgroundColor of ['rgba(158,27,50,0.5)','#00000080']) render(`translucent-canvas-${backgroundColor.startsWith('#')?'hex':'rgba'}`,{backgroundColor,series:[{type:'pie',label:{show:true},data:[{id:'A',name:'A',value:1}]}]},{A:'#000000'})
  assert.equal(h.readableText('rgba(158,27,50,0.5)'),'#000000')
  const graph=ids=>h.prepareColorsetOption({series:[{type:'graph',data:ids.map(id=>({id,name:id,value:1}))}]},'colorset1')
  const a=graph(['alpha','beta']),b=graph(['beta','alpha'])
  assert.deepEqual(Object.fromEntries(a.series[0].data.map(n=>[n.id,n.itemStyle.color])),Object.fromEntries(b.series[0].data.map(n=>[n.id,n.itemStyle.color])))
  const stable=h.prepareColorsetOption({series:[{type:'graph',data:[{id:'beta'}]}]},'colorset1',['alpha','beta'])
  assert.equal(stable.series[0].data[0].itemStyle.color,h.solidCategoryStyle(1,'colorset1').color)
  const caller=h.prepareColorsetOption({series:[{type:'pie',data:[{id:'beta',name:'beta',value:1,itemStyle:{color:'#333e48'}},{id:'alpha',name:'alpha',value:1,itemStyle:{color:'#9e1b32'}}]}]},'colorset1')
  assert.deepEqual(caller.series[0].data.map(n=>n.itemStyle.color),['#333e48','#9e1b32'])
  const capacity=h.solidColors('colorset1').length
  const bars=h.prepareColorsetOption({xAxis:{type:'category',data:['x']},yAxis:{},series:Array.from({length:capacity+1},(_,i)=>({id:`s${i}`,name:`s${i}`,type:'bar',label:{show:true,position:'inside'},data:[1]}))},'colorset1').series
  assert.equal(new Set(bars.slice(0,capacity).map(s=>s.itemStyle.color)).size,capacity)
  assert(bars.slice(0,capacity).every(s=>s.itemStyle.borderWidth===0));assert(bars.at(-1).itemStyle.borderWidth>0)
  const style=h.solidCategoryStyle(capacity,'colorset1')
  const preserved=h.prepareColorsetOption({series:[{type:'bar',id:'overflow',itemStyle:{...style},data:[1]}]},'colorset1').series[0].itemStyle
  assert.equal(preserved.borderWidth,style.borderWidth);assert.equal(preserved.borderColor,style.borderColor)
  for (const cs of ['colorset1','colorset2']) for (const index of [h.solidColors(cs).length,256,1296,5000]) {
    const paint=h.solidCategoryStyle(index,cs)
    assert.notEqual(paint.borderColor,paint.color);assert(paint.borderWidth>=1 && paint.borderWidth<=3)
  }
}
writeFileSync(new URL('results.json',output),JSON.stringify({passed:true,actualSvgCases:rows.length,rows},null,2)+'\n')
console.log(JSON.stringify({passed:true,actualSvgCases:rows.length,allocationAndBackingChecks:true}))
