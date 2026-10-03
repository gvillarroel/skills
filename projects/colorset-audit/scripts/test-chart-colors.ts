// Run: node --experimental-strip-types projects/colorset-audit/scripts/test-chart-colors.ts
// Node.js 22.6+ native TypeScript runner; no external dependencies.
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { colorsets, normalizePaint, prepareColorsetOption } from '../../../skills/echarts-animated-svg/assets/templates/echarts-colorsets.mjs'
for (const selected of Object.keys(colorsets)) {
  for (const input of ['lightgray','LightSteelBlue','#123','#1234','#12345688','rgb(10%,20%,30%)','rgba(15,23,42,.3)','hsl(210,50%,40%)']) {
    const output = normalizePaint(input, selected)
    const base = output.startsWith('rgba') ? '#'+output.match(/[\d.]+/g).slice(0,3).map((part)=>Number(part).toString(16).padStart(2,'0')).join('') : output.slice(0,7)
    assert.ok(colorsets[selected].includes(base), `${input} => ${output} outside ${selected}`)
  }
  const option = prepareColorsetOption({ series:[{type:'bar',data:[12,9,7],name:'Original #123456',itemStyle:{color:{type:'linear',colorStops:[{offset:0,color:'#123456'},{offset:1,color:'navy'}]}}}], visualMap:{min:0,max:12,inRange:{color:['#007298','#9e1b32']}} },selected)
  assert.deepEqual(option.series[0].data,[12,9,7])
  assert.equal(option.series[0].name,'Original #123456')
  assert.equal(option.visualMap.type,'piecewise')
  for (const stop of option.series[0].itemStyle.color.colorStops) assert.ok(colorsets[selected].includes(stop.color))
}
assert.equal(await readFile(new URL('../../../skills/echarts-animated-svg/assets/templates/echarts-colorsets.mjs',import.meta.url),'utf8'),await readFile(new URL('../../../skills/slidev-echarts/assets/templates/echarts-colorsets.mjs',import.meta.url),'utf8'))
console.log('Both independent chart templates pass named/RGB/HSL/alpha normalization, discrete scales, gradient endpoints, and data/label preservation.')
