// Copy this self-contained file into the chart project. Import with Node or Vite.
// Authored categorical colors are discrete; values, labels, sizes, and geometry stay unchanged.
export const colorsets = {
  colorset1: ['#000000','#1c1c1c','#333e48','#363636','#4f4f4f','#696969','#6d1222','#828282','#9c9c9c','#9e1b32','#b5b5b5','#cfcfcf','#e7e7e7','#e8002a','#f7f7f7','#ffccd5','#ffffff'],
  colorset2: ['#000000','#004d66','#007298','#00ace6','#1c1c1c','#294d19','#333e48','#363636','#36b300','#431f47','#45842a','#4f4f4f','#652f6c','#696969','#6d1222','#828282','#98700c','#994a00','#9c9c9c','#9e00b3','#9e1b32','#b5b5b5','#cdf3ff','#cfcfcf','#dbffcc','#e77204','#e7e7e7','#e8002a','#f1c319','#f7f7f7','#f9ccff','#ff9633','#ffccd5','#ffd332','#ffe5cc','#fff4cc','#ffffff'],
}
const sequences = { colorset1: ['#9e1b32','#333e48','#6d1222','#828282','#e8002a','#cfcfcf'], colorset2: ['#9e1b32','#007298','#e77204','#45842a','#652f6c','#f1c319'] }
const rgb = (hex) => [1,3,5].map((index) => Number.parseInt(hex.slice(index,index+2),16))
export function nearestColor(value, colorset = 'colorset1') {
  const hex = value.toLowerCase().replace(/^#([\da-f])([\da-f])([\da-f])$/, '#$1$1$2$2$3$3')
  if (colorsets[colorset].includes(hex)) return hex
  const origin = rgb(hex)
  return colorsets[colorset].reduce((best, color) => {
    const distance = (candidate) => rgb(candidate).reduce((sum, channel, index) => sum + (channel-origin[index])**2,0)
    return distance(color) < distance(best) ? color : best
  })
}
export function prepareColorsetOption(option, colorset = 'colorset1') {
  const walk = (value) => {
    if (!value || typeof value !== 'object') return
    if (!Array.isArray(value)) {
      delete value.colorSaturation
      delete value.colorLightness
    }
    for (const [key, child] of Object.entries(value)) {
      if (/^(?:color|fill|stroke|backgroundColor|borderColor|shadowColor)$/.test(key)) {
        if (typeof child === 'string') value[key] = normalizePaint(child, colorset)
        else if (Array.isArray(child)) value[key] = child.map((paint) => typeof paint === 'string' ? normalizePaint(paint, colorset) : paint)
      }
      walk(value[key])
    }
  }
  walk(option)
  option.color ||= sequences[colorset]
  option.textStyle = { color: '#333e48', ...option.textStyle }
  const maps = option.visualMap ? (Array.isArray(option.visualMap) ? option.visualMap : [option.visualMap]) : []
  for (const map of maps) {
    const colors = map.inRange?.color
    if (!Array.isArray(colors) || colors.length < 2) continue
    const min = Number(map.min ?? 0), max = Number(map.max ?? 100)
    map.type = 'piecewise'
    map.pieces = colors.map((color, index) => ({
      ...(index ? { gte: min+(max-min)*index/colors.length } : { min: -Infinity }),
      ...(index < colors.length-1 ? { lt: min+(max-min)*(index+1)/colors.length } : { max: Infinity }),
      color,
    }))
    delete map.calculable
    delete map.inRange.color
    map.textStyle = { color: '#696969', ...map.textStyle }
  }
  return option
}
export function normalizeSvgPaints(svg, colorset = 'colorset1') {
  const color = '(#[\\da-fA-F]{3,8}\\b|(?:rgba?|hsla?)\\([^)]*\\)|[a-zA-Z]+)'
  return svg.replace(new RegExp('\\b(fill|stroke|stop-color|color)="'+color+'"','g'),
    (_match, key, value) => `${key}="${renderedPaint(value, colorset)}"`)
    .replace(new RegExp('\\b(fill|stroke|stop-color|color)\\s*:\\s*'+color,'g'),
      (_match, key, value) => `${key}:${renderedPaint(value, colorset)}`)
}
function renderedPaint(value, colorset) {
  // API semantic markers must resolve to a real paint before SVG serialization.
  return ['source','target','auto'].includes(value) ? '#828282' : normalizePaint(value, colorset)
}
export function normalizePaint(value, colorset = 'colorset1') {
  if (typeof value !== 'string') return value
  value = value.trim()
  if (['none','transparent','inherit','currentcolor'].includes(value.toLowerCase())) return value
  if (value === 'black') return '#000000'
  if (value === 'white') return '#ffffff'
  const named={"aliceblue":"#f0f8ff","antiquewhite":"#faebd7","aqua":"#00ffff","aquamarine":"#7fffd4","azure":"#f0ffff","beige":"#f5f5dc","bisque":"#ffe4c4","black":"#000000","blanchedalmond":"#ffebcd","blue":"#0000ff","blueviolet":"#8a2be2","brown":"#a52a2a","burlywood":"#deb887","cadetblue":"#5f9ea0","chartreuse":"#7fff00","chocolate":"#d2691e","coral":"#ff7f50","cornflowerblue":"#6495ed","cornsilk":"#fff8dc","crimson":"#dc143c","cyan":"#00ffff","darkblue":"#00008b","darkcyan":"#008b8b","darkgoldenrod":"#b8860b","darkgray":"#a9a9a9","darkgreen":"#006400","darkgrey":"#a9a9a9","darkkhaki":"#bdb76b","darkmagenta":"#8b008b","darkolivegreen":"#556b2f","darkorange":"#ff8c00","darkorchid":"#9932cc","darkred":"#8b0000","darksalmon":"#e9967a","darkseagreen":"#8fbc8f","darkslateblue":"#483d8b","darkslategray":"#2f4f4f","darkslategrey":"#2f4f4f","darkturquoise":"#00ced1","darkviolet":"#9400d3","deeppink":"#ff1493","deepskyblue":"#00bfff","dimgray":"#696969","dimgrey":"#696969","dodgerblue":"#1e90ff","firebrick":"#b22222","floralwhite":"#fffaf0","forestgreen":"#228b22","fuchsia":"#ff00ff","gainsboro":"#dcdcdc","ghostwhite":"#f8f8ff","gold":"#ffd700","goldenrod":"#daa520","gray":"#808080","green":"#008000","greenyellow":"#adff2f","grey":"#808080","honeydew":"#f0fff0","hotpink":"#ff69b4","indianred":"#cd5c5c","indigo":"#4b0082","ivory":"#fffff0","khaki":"#f0e68c","lavender":"#e6e6fa","lavenderblush":"#fff0f5","lawngreen":"#7cfc00","lemonchiffon":"#fffacd","lightblue":"#add8e6","lightcoral":"#f08080","lightcyan":"#e0ffff","lightgoldenrodyellow":"#fafad2","lightgray":"#d3d3d3","lightgreen":"#90ee90","lightgrey":"#d3d3d3","lightpink":"#ffb6c1","lightsalmon":"#ffa07a","lightseagreen":"#20b2aa","lightskyblue":"#87cefa","lightslategray":"#778899","lightslategrey":"#778899","lightsteelblue":"#b0c4de","lightyellow":"#ffffe0","lime":"#00ff00","limegreen":"#32cd32","linen":"#faf0e6","magenta":"#ff00ff","maroon":"#800000","mediumaquamarine":"#66cdaa","mediumblue":"#0000cd","mediumorchid":"#ba55d3","mediumpurple":"#9370db","mediumseagreen":"#3cb371","mediumslateblue":"#7b68ee","mediumspringgreen":"#00fa9a","mediumturquoise":"#48d1cc","mediumvioletred":"#c71585","midnightblue":"#191970","mintcream":"#f5fffa","mistyrose":"#ffe4e1","moccasin":"#ffe4b5","navajowhite":"#ffdead","navy":"#000080","oldlace":"#fdf5e6","olive":"#808000","olivedrab":"#6b8e23","orange":"#ffa500","orangered":"#ff4500","orchid":"#da70d6","palegoldenrod":"#eee8aa","palegreen":"#98fb98","paleturquoise":"#afeeee","palevioletred":"#db7093","papayawhip":"#ffefd5","peachpuff":"#ffdab9","peru":"#cd853f","pink":"#ffc0cb","plum":"#dda0dd","powderblue":"#b0e0e6","purple":"#800080","rebeccapurple":"#663399","red":"#ff0000","rosybrown":"#bc8f8f","royalblue":"#4169e1","saddlebrown":"#8b4513","salmon":"#fa8072","sandybrown":"#f4a460","seagreen":"#2e8b57","seashell":"#fff5ee","sienna":"#a0522d","silver":"#c0c0c0","skyblue":"#87ceeb","slateblue":"#6a5acd","slategray":"#708090","slategrey":"#708090","snow":"#fffafa","springgreen":"#00ff7f","steelblue":"#4682b4","tan":"#d2b48c","teal":"#008080","thistle":"#d8bfd8","tomato":"#ff6347","turquoise":"#40e0d0","violet":"#ee82ee","wheat":"#f5deb3","white":"#ffffff","whitesmoke":"#f5f5f5","yellow":"#ffff00","yellowgreen":"#9acd32"}
  if (named[value.toLowerCase()]) return nearestColor(named[value.toLowerCase()],colorset)
  const hsl=value.match(/^hsla?\(\s*([.\d]+)(?:deg)?\s*[, ]\s*([.\d]+)%\s*[, ]\s*([.\d]+)%(?:\s*[,/]\s*([.\d]+))?\s*\)$/)
  if (hsl) {
    const h=Number(hsl[1])/360%1,s=Number(hsl[2])/100,l=Number(hsl[3])/100
    const hue=(p,q,t)=>{t=(t+1)%1;return t<1/6?p+(q-p)*6*t:t<1/2?q:t<2/3?p+(q-p)*(2/3-t)*6:p}
    const q=l<.5?l*(1+s):l+s-l*s,p=2*l-q
    const channels=s?[hue(p,q,h+1/3),hue(p,q,h),hue(p,q,h-1/3)]:[l,l,l]
    const mapped=nearestColor('#'+channels.map((c)=>Math.round(c*255).toString(16).padStart(2,'0')).join(''),colorset)
    return hsl[4]===undefined?mapped:`rgba(${rgb(mapped).join(',')},${hsl[4]})`
  }
  if (/^#[\da-f]{3,8}$/i.test(value)) {
    let raw = value.slice(1)
    if ([3,4].includes(raw.length)) raw = [...raw].map((character) => character+character).join('')
    return nearestColor('#'+raw.slice(0,6), colorset)+(raw.length===8?raw.slice(6):'')
  }
  const match = value.match(/^rgba?\(\s*(\d+(?:\.\d+)?%?)\s*[, ]\s*(\d+(?:\.\d+)?%?)\s*[, ]\s*(\d+(?:\.\d+)?%?)(?:\s*[,/]\s*([.\d]+%?))?\s*\)$/i)
  if (!match) return value
  const hex = '#'+match.slice(1,4).map((channel)=>Math.round(Number.parseFloat(channel)*(channel.endsWith('%')?2.55:1)).toString(16).padStart(2,'0')).join('')
  const mapped = nearestColor(hex, colorset)
  return match[4] === undefined ? mapped : `rgba(${rgb(mapped).join(',')},${match[4]})`
}
export function enforceColorsetRenderer(container, colorset = 'colorset1') {
  // Keep native defaults, emphasis states, and animation tweens on exact authored base paints.
  const attached = new WeakSet()
  const apply = () => {
    container.querySelectorAll('canvas').forEach((canvas) => {
      const context = canvas.getContext('2d')
      if (!context || attached.has(context)) return
      attached.add(context)
      for (const key of ['fillStyle','strokeStyle','shadowColor']) {
        const descriptor = Object.getOwnPropertyDescriptor(CanvasRenderingContext2D.prototype,key)
        Object.defineProperty(context,key,{configurable:true,get(){return descriptor.get.call(this)},set(value){descriptor.set.call(this,normalizePaint(value,colorset))}})
      }
    })
    container.querySelectorAll('svg').forEach((svg) => {
      for (const element of [svg,...svg.querySelectorAll('*')]) {
        for (const key of ['fill','stroke','stop-color','color','style']) {
          const source=element.getAttribute(key)
          if (source===null) continue
          const target=key==='style'?normalizeSvgPaints(source,colorset):renderedPaint(source,colorset)
          if (source!==target) element.setAttribute(key,target)
        }
        if (element.tagName.toLowerCase()==='style') {
          const source=element.textContent, target=normalizeSvgPaints(source,colorset)
          if (source!==target) element.textContent=target
        }
      }
    })
  }
  apply()
  const observer=new MutationObserver(apply)
  observer.observe(container,{subtree:true,childList:true,attributes:true,characterData:true})
  return () => observer.disconnect()
}
export function colorsetTheme(colorset = 'colorset1') {
  const axis = { axisLine:{lineStyle:{color:'#cfcfcf'}},axisTick:{lineStyle:{color:'#cfcfcf'}},axisLabel:{color:'#696969'},splitLine:{lineStyle:{color:'#e7e7e7'}},splitArea:{areaStyle:{color:['#ffffff','#f7f7f7']}} }
  return { color: sequences[colorset], backgroundColor:'#ffffff', textStyle:{color:'#333e48'}, title:{textStyle:{color:'#333e48'},subtextStyle:{color:'#696969'}},legend:{textStyle:{color:'#333e48'}},categoryAxis:axis,valueAxis:axis,timeAxis:axis,logAxis:axis,radar:axis,tooltip:{backgroundColor:'#ffffff',borderColor:'#cfcfcf',textStyle:{color:'#333e48'}},candlestick:{itemStyle:{color:'#9e1b32',color0:colorset==='colorset2'?'#45842a':'#333e48',borderColor:'#6d1222',borderColor0:'#696969'}},tree:{lineStyle:{color:'#cfcfcf'}},graph:{lineStyle:{color:'#cfcfcf'}},sankey:{lineStyle:{color:'#828282'}},gauge:{axisLine:{lineStyle:{color:[[1,'#cfcfcf']]}},axisTick:{lineStyle:{color:'#828282'}},splitLine:{lineStyle:{color:'#696969'}},axisLabel:{color:'#696969'},detail:{color:'#333e48'}},calendar:{itemStyle:{color:'#ffffff',borderColor:'#cfcfcf'},dayLabel:{color:'#696969'},monthLabel:{color:'#696969'},yearLabel:{color:'#333e48'}} }
}
