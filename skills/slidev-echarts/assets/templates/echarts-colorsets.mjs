// Copy this self-contained file into the chart project. Import with Node or Vite.
// Authored categorical colors are discrete; values, labels, sizes, and geometry stay unchanged.
export const colorsets = {
  colorset1: ['#000000','#1c1c1c','#333e48','#363636','#4f4f4f','#696969','#6d1222','#828282','#9c9c9c','#9e1b32','#b5b5b5','#cfcfcf','#e7e7e7','#e8002a','#f7f7f7','#ffccd5','#ffffff'],
  colorset2: ['#000000','#004d66','#007298','#00ace6','#1c1c1c','#294d19','#333e48','#363636','#36b300','#431f47','#45842a','#4f4f4f','#652f6c','#696969','#6d1222','#828282','#98700c','#994a00','#9c9c9c','#9e00b3','#9e1b32','#b5b5b5','#cdf3ff','#cfcfcf','#dbffcc','#e77204','#e7e7e7','#e8002a','#f1c319','#f7f7f7','#f9ccff','#ff9633','#ffccd5','#ffd332','#ffe5cc','#fff4cc','#ffffff'],
}
const sequences = {"colorset1": ["#9e1b32", "#333e48", "#6d1222", "#828282", "#e8002a", "#4f4f4f", "#696969", "#9c9c9c", "#b5b5b5", "#1c1c1c", "#363636", "#000000", "#cfcfcf", "#e7e7e7", "#ffccd5", "#ffffff", "#f7f7f7"], "colorset2": ["#9e1b32", "#007298", "#e77204", "#45842a", "#652f6c", "#f1c319", "#6d1222", "#004d66", "#994a00", "#294d19", "#431f47", "#98700c", "#e8002a", "#00ace6", "#ff9633", "#36b300", "#9e00b3", "#ffd332", "#333e48", "#4f4f4f", "#696969", "#828282", "#9c9c9c", "#b5b5b5", "#1c1c1c", "#363636", "#000000", "#cfcfcf", "#e7e7e7", "#ffccd5", "#cdf3ff", "#dbffcc", "#f9ccff", "#ffe5cc", "#fff4cc", "#ffffff", "#f7f7f7"]}
const rgb = (hex) => [1,3,5].map((index) => Number.parseInt(hex.slice(index,index+2),16))

function paintChannels(value) {
  if (typeof value !== 'string') return null
  const v = value.trim().toLowerCase()
  const h = /^#([\da-f]{3,4}|[\da-f]{6}|[\da-f]{8})$/.exec(v)
  if (h) {
    const hex = h[1].length < 5 ? [...h[1]].map(c => c+c).join('') : h[1]
    return [...rgb('#'+hex.slice(0,6)),hex.length === 8 ? parseInt(hex.slice(6),16)/255 : 1]
  }
  const m = /^rgba?\(\s*([\d.]+)[, ]+([\d.]+)[, ]+([\d.]+)(?:\s*[,/]\s*([\d.]+)(%)?)?\s*\)$/.exec(v)
  if (!m) return null
  const channels = [Number(m[1]),Number(m[2]),Number(m[3]),m[4] === undefined ? 1 : Math.max(0,Math.min(1,Number(m[4])/(m[5] ? 100 : 1)))]
  return channels.every(Number.isFinite) ? channels : null
}
function paintHex(channels) {
  return '#'+channels.slice(0,3).map(c => Math.round(c).toString(16).padStart(2,'0')).join('')
}
function canonicalOpaque(value) {
  const channels = paintChannels(value)
  return channels && channels[3] === 1 ? paintHex(channels) : String(value).trim().toLowerCase()
}
function compositePaint(value, under, colorset) {
  const channels = paintChannels(typeof value === 'string' ? normalizePaint(value,colorset) : '')
  if (!channels) return under
  const base = paintChannels(under) ?? [255,255,255,1]
  return paintHex(channels.slice(0,3).map((c,i) => c*channels[3]+base[i]*(1-channels[3])))
}

function luminance(fill) {
  const paint = paintChannels(fill) ?? [255,255,255,1]
  const channels = paint.slice(0,3).map(c => c*paint[3]+255*(1-paint[3])).map((c) => c / 255).map((c) => c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4)
  return channels.reduce((sum,c,i) => sum+c*[.2126,.7152,.0722][i],0)
}
function contrast(a,b) {
  const left=luminance(a),right=luminance(b)
  return (Math.max(left,right)+.05)/(Math.min(left,right)+.05)
}
export function readableText(fill) {
  return contrast(fill,'#000000') >= contrast(fill,'#ffffff') ? '#000000' : '#ffffff'
}
export function contrastSafeArrowStyle(style = {}, colorset = 'colorset1', background = '#ffffff') {
  // Inspect the visible composite, including both color alpha and line opacity.
  const normalizedSurface = normalizePaint(background,colorset)
  const surface = normalizedSurface === 'transparent' ? [255,255,255,0] : paintChannels(normalizedSurface)
  if (!surface) throw new Error('Arrow backing requires a known solid color; inspect gradients or unresolved paint explicitly')
  const backing = surface.slice(0,3).map(c => c*surface[3]+255*(1-surface[3]))
  const raw = normalizePaint(style.color ?? '#696969',colorset)
  const channels = raw === 'transparent' ? [0,0,0,0] : paintChannels(raw)
  if (!channels) throw new Error('Arrow paint requires a known solid color; resolve gradients or CSS paint before qualification')
  const opacity = Math.max(0,Math.min(1,Number(style.opacity ?? 1)))
  const width = Math.max(1.5,Number(style.width ?? 2))
  if (!Number.isFinite(opacity) || !Number.isFinite(width)) throw new Error('Arrow opacity and width must be finite numbers')
  const luminanceChannels = c => c.map(v => v/255).map(v => v <= .04045 ? v/12.92 : ((v+.055)/1.055)**2.4).reduce((sum,v,i) => sum+v*[.2126,.7152,.0722][i],0)
  const level = color => {
    const a=luminanceChannels(color),b=luminanceChannels(backing)
    return (Math.max(a,b)+.05)/(Math.min(a,b)+.05)
  }
  const alpha = channels[3]*opacity
  const visible = channels.slice(0,3).map((c,i) => c*alpha+backing[i]*(1-alpha))
  if (level(visible) >= 3) return {...style,color:raw,opacity,width}
  const choices = colorsets[colorset].filter(color => level(rgb(color)) >= 3)
  if (!choices.length) throw new Error('No allowed arrow paint contrasts with this backing; use a clear route gutter')
  const origin = channels.slice(0,3)
  const color = choices.reduce((best,value) => {
    const distance = c => rgb(c).reduce((sum,v,i) => sum+(v-origin[i])**2,0)
    return distance(value) < distance(best) ? value : best
  })
  return {...style,color,opacity:1,width}
}
export function insetCartesianArrowRoutes(option, chart, clearancePx = 7) {
  // Call after the original option is laid out; always pass original route data
  // again after resizing so clearance is in pixels rather than data units.
  if (!Number.isFinite(clearancePx) || clearancePx < 0) throw new Error('Arrow clearance must be a finite nonnegative pixel distance')
  if (!clearancePx) return option
  const seriesList=Array.isArray(option.series)?option.series:[option.series]
  const series=seriesList.map((series,index)=>{
    if (series?.type!=='lines' || series.coordinateSystem!=='cartesian2d') return series
    const layout=chart.getOption()
    if (layout.xAxis?.[series.xAxisIndex??0]?.type==='category' || layout.yAxis?.[series.yAxisIndex??0]?.type==='category') throw new Error('Arrow inset requires continuous Cartesian axes; qualify categorical routes explicitly')
    return {...series,data:(series.data??[]).map(edge=>{
      const symbols=edge.symbol??series.symbol
      const ends=Array.isArray(symbols)?symbols:[symbols,symbols]
      if (!ends.includes('arrow')) return edge
      if (series.polyline || !Array.isArray(edge.coords) || edge.coords.length!==2) throw new Error('Arrow inset supports two-point Cartesian routes; qualify other geometry explicitly')
      const finder={seriesIndex:index},points=edge.coords.map(point=>chart.convertToPixel(finder,point))
      if (points.some(p=>!Array.isArray(p)||p.some(v=>!Number.isFinite(v)))) throw new Error('Initialize the Cartesian chart before applying arrow clearance')
      const [a,b]=points,dx=b[0]-a[0],dy=b[1]-a[1]
      if (Math.hypot(dx,dy)<clearancePx*3) throw new Error('Route is too short for the requested arrow clearance')
      const curve=Number(edge.lineStyle?.curveness??series.lineStyle?.curveness??0)
      if (!Number.isFinite(curve)) throw new Error('Arrow route curveness must be a finite number')
      const control=[(a[0]+b[0])/2+dy*curve,(a[1]+b[1])/2-dx*curve]
      const coords=edge.coords.map((point,end)=>{
        if (ends[end]!=='arrow') return [...point]
        const anchor=points[end],direction=[control[0]-anchor[0],control[1]-anchor[1]],length=Math.hypot(...direction)
        return chart.convertFromPixel(finder,anchor.map((v,i)=>v+direction[i]*clearancePx/length))
      })
      return {...edge,coords}
    })}
  })
  return {...option,series:Array.isArray(option.series)?series:series[0]}
}
function arrowPresentation(seriesList, colorset, canvas) {
  const hasArrow = symbols => (Array.isArray(symbols) ? symbols : [symbols]).some(symbol => symbol === 'arrow')
  const states = ['emphasis','select','blur']
  for (const series of seriesList) {
    const nodes = new Map()
    for (const [index,node] of (series.data ?? []).entries()) {
      if (node && typeof node === 'object') for (const key of [index,node.id,node.name]) if (key !== undefined) nodes.set(String(key),node)
    }
    const resolve = (style,edge) => {
      const color = style.color
      const node = color === 'source' ? nodes.get(String(edge?.source)) : color === 'target' ? nodes.get(String(edge?.target)) : null
      return {...style,color:node?.itemStyle?.color ?? (['source','target','auto'].includes(color) ? '#696969' : color ?? '#696969')}
    }
    const finish = (owner,base,edge) => {
      owner.lineStyle = contrastSafeArrowStyle(resolve({...base,...owner.lineStyle},edge),colorset,canvas)
      for (const state of states) {
        owner[state] ??= {}
        owner[state].lineStyle = contrastSafeArrowStyle(resolve({...owner.lineStyle,...owner[state].lineStyle},edge),colorset,canvas)
      }
    }
    if (series.type === 'graph') {
      const directed = hasArrow(series.edgeSymbol)
      if (directed) finish(series,series.lineStyle ?? {})
      for (const edge of series.links ?? series.edges ?? []) if (directed || hasArrow(edge.symbol)) finish(edge,series.lineStyle ?? {},edge)
    } else if (series.type === 'lines') {
      // Native EffectLine is chosen at series level. An edge's show:false
      // does not disable its glyph once that renderer has been selected.
      const moving = effect => series.effect?.show && hasArrow(effect?.symbol)
      const finishEffect = (owner, inherited, lineStyle) => {
        const effect = {...inherited,...owner}
        const style = contrastSafeArrowStyle({color:effect.color ?? lineStyle.color,opacity:effect.opacity ?? 1},colorset,canvas)
        owner.color = style.color
        owner.opacity = style.opacity
      }
      const directed = hasArrow(series.symbol)
      if (directed || moving(series.effect)) finish(series,series.lineStyle ?? {})
      if (moving(series.effect)) finishEffect(series.effect,{},series.lineStyle)
      for (const edge of series.data ?? []) if (edge && typeof edge === 'object') {
        const effect = {...series.effect,...edge.effect}
        if (hasArrow(edge.symbol ?? series.symbol) || moving(effect)) finish(edge,series.lineStyle ?? {},edge)
        if (moving(effect) && edge.effect) finishEffect(edge.effect,series.effect,edge.lineStyle)
      }
    }
    const terminalArrow = series.markLine?.data?.some(entry => (Array.isArray(entry)?entry:[entry]).some(terminal => hasArrow(terminal?.symbol)))
    if (series.markLine && (series.markLine.symbol === undefined || hasArrow(series.markLine.symbol) || terminalArrow)) {
      const mark = series.markLine
      finish(mark,mark.lineStyle ?? {})
      for (const entry of mark.data ?? []) for (const edge of Array.isArray(entry) ? entry : [entry]) if (edge && typeof edge === 'object') finish(edge,mark.lineStyle,edge)
    }
  }
}
export function solidColors(colorset = 'colorset1', canvas = '#ffffff') {
  return sequences[colorset].filter((color) => color !== canonicalOpaque(canvas))
}
export function solidCategoryStyle(index, colorset = 'colorset1', canvas = '#ffffff') {
  if (!Number.isInteger(index) || index < 0) throw new Error('Category index must be a nonnegative integer')
  const colors = solidColors(colorset,canvas),cycle = Math.floor(index/colors.length),slot = index%colors.length,fill = colors[slot]
  const borders = colorsets[colorset].filter(color => color !== fill && contrast(fill,color) >= 3)
  const phase = Math.max(0,cycle-1)
  return {color:fill,borderColor:cycle ? borders[phase%borders.length] : 'none',borderWidth:cycle ? 1+Math.floor(phase/(borders.length*3))%3 : 0,borderType:cycle ? ['solid','dashed','dotted'][Math.floor(phase/borders.length)%3] : 'solid',textColor:readableText(fill),overflow:cycle>0}
}
function solidPresentation(option, colorset, canvas, categoryOrder = []) {
  if (option.colorsetPresentation === 'source') { delete option.colorsetPresentation; return }
  delete option.colorsetPresentation
  const textCanvas = compositePaint(canvas,'#ffffff',colorset)
  const soft = {'#ffccd5':'#9e1b32','#cdf3ff':'#007298','#dbffcc':'#45842a','#ffe5cc':'#e77204','#fff4cc':'#f1c319','#f9ccff':'#652f6c'}
  const shapeTypes = new Set(['bar','pie','funnel','graph','tree','treemap','sunburst','sankey','scatter','effectScatter','pictorialBar','heatmap'])
  const nodeTypes = new Set(['pie','funnel','graph','tree','treemap','sunburst','sankey'])
  const positions = {pie:'outer',funnel:'outer',graph:'inside',tree:'left',treemap:'inside',sunburst:'inside',sankey:'right',bar:'inside',scatter:'inside',effectScatter:'inside',pictorialBar:'inside',heatmap:'inside'}
  const seriesList = Array.isArray(option.series) ? option.series : option.series ? [option.series] : []
  const keys = new Set(), identities = new WeakMap()
  const collect = (node, scope, path) => {
    if (!node || typeof node !== 'object' || Array.isArray(node)) return
    const key = String(node.id ?? node.name ?? `${scope}/${path}`)
    identities.set(node,key);keys.add(key)
    ;(node.children ?? []).forEach((child,index) => collect(child,scope,`${path}.${index}`))
  }
  seriesList.forEach((series,index) => {
    if (!shapeTypes.has(series.type)) return
    const scope = String(series.id ?? series.name ?? `series-${index}`)
    if (nodeTypes.has(series.type) || series.colorBy === 'data') (series.data ?? []).forEach((node,i) => collect(node,scope,String(i)))
    else { identities.set(series,scope);keys.add(scope) }
  })
  const order = [...new Set(categoryOrder.map(String))]
  const compare = new Intl.Collator('en',{numeric:true}).compare
  order.push(...[...keys].filter(key => !order.includes(key)).sort(compare))
  const categoryIndices = new Map(order.map((key,index) => [key,index]))
  const paintFor = (node, fallback) => identities.has(node) ? solidCategoryStyle(categoryIndices.get(identities.get(node)),colorset,canvas) : fallback
  const labelStyle = (value, fill, defaultPosition) => {
    const position = value.position ?? defaultPosition
    const inside = typeof position === 'string' && /^(?:inside|middle|center)/.test(position)
    const under = inside ? compositePaint(fill,textCanvas,colorset) : textCanvas
    const backing = value.backgroundColor === 'inherit' ? fill : compositePaint(value.backgroundColor, under, colorset)
    const result = {...value,position,color:readableText(backing),textBorderColor:'none',textBorderWidth:0,textShadowBlur:0,borderWidth:0}
    if (value.rich) result.rich = Object.fromEntries(Object.entries(value.rich).map(([key,token]) => [key,{...token,color:readableText(token.backgroundColor === 'inherit' ? fill : compositePaint(token.backgroundColor,backing,colorset)),textBorderColor:'none',textBorderWidth:0,textShadowBlur:0,borderWidth:0}]))
    return result
  }
  const visit = (node, inheritedPaint, inheritedLabel, defaultPosition, filled) => {
    if (!node || typeof node !== 'object' || Array.isArray(node)) return
    const own = node.itemStyle ?? {}, declared = typeof own.overflow === 'boolean'
    const paint = declared ? own : paintFor(node,inheritedPaint)
    let fill = typeof own.color === 'string' ? normalizePaint(own.color,colorset) : paint.color
    if (!declared && typeof own.color === 'string' && soft[fill]) fill = normalizePaint(soft[fill],colorset)
    const labels = {...inheritedLabel,...node.label}
    if (filled) {
      const width = declared ? (own.overflow ? own.borderWidth : 0) : paint.borderWidth
      node.itemStyle = {...own,color:fill,opacity:1,borderWidth:width ?? 0,borderColor:width ? paint.borderColor : 'none',borderType:paint.borderType ?? 'solid'}
      delete node.itemStyle.textColor;delete node.itemStyle.overflow
      node.label = labelStyle(labels,fill,defaultPosition)
      for (const state of ['emphasis','select','blur']) if (node[state]) {
        const stateFill = typeof node[state].itemStyle?.color === 'string' ? normalizePaint(node[state].itemStyle.color,colorset) : fill
        if (node[state].itemStyle) node[state].itemStyle = {...node[state].itemStyle,borderWidth:width ?? 0,borderColor:width ? paint.borderColor : 'none'}
        node[state].label = labelStyle({...labels,...node[state].label},stateFill,defaultPosition)
      }
    }
    for (const child of node.children ?? []) visit(child,{...paint,color:fill},labels,defaultPosition,filled)
    for (const child of node.data ?? []) visit(child,{...paint,color:fill},labels,defaultPosition,filled)
    for (const child of node.levels ?? []) visit(child,{...paint,color:fill},labels,defaultPosition,filled)
  }
  seriesList.forEach((series,index) => {
    if (series.type === 'tree' && (!series.symbol || series.symbol === 'emptyCircle')) series.symbol = 'circle'
    if (series.type === 'boxplot') {
      series.itemStyle = {...series.itemStyle,color:normalizePaint(soft[series.itemStyle?.color] ?? series.itemStyle?.color ?? '#007298',colorset)}
      series.itemStyle.borderColor = series.itemStyle.color
    }
    visit(series,solidCategoryStyle(index,colorset,canvas),{},positions[series.type] ?? 'outside',shapeTypes.has(series.type))
  })
  arrowPresentation(seriesList,colorset,option.backgroundColor ?? '#ffffff')
  if (option.tooltip) option.tooltip.borderWidth = 0
}

export function nearestColor(value, colorset = 'colorset1') {
  const hex = value.toLowerCase().replace(/^#([\da-f])([\da-f])([\da-f])$/, '#$1$1$2$2$3$3')
  if (colorsets[colorset].includes(hex)) return hex
  const origin = rgb(hex)
  return colorsets[colorset].reduce((best, color) => {
    const distance = (candidate) => rgb(candidate).reduce((sum, channel, index) => sum + (channel-origin[index])**2,0)
    return distance(color) < distance(best) ? color : best
  })
}
export function prepareColorsetOption(option, colorset = 'colorset1', categoryOrder = []) {
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
  const canvas = typeof option.backgroundColor === 'string' && option.backgroundColor !== 'transparent' ? canonicalOpaque(normalizePaint(option.backgroundColor, colorset)) : '#ffffff'
  if (option.colorsetPresentation !== 'source') option.color = solidColors(colorset, canvas)
  option.color ||= solidColors(colorset, canvas)
  solidPresentation(option, colorset, canvas, categoryOrder)
  walk(option)
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
  return { color: sequences[colorset], backgroundColor:'#ffffff', textStyle:{color:'#333e48'}, title:{textStyle:{color:'#333e48'},subtextStyle:{color:'#696969'}},legend:{textStyle:{color:'#333e48'}},categoryAxis:axis,valueAxis:axis,timeAxis:axis,logAxis:axis,radar:axis,tooltip:{backgroundColor:'#ffffff',borderWidth:0,borderColor:'#cfcfcf',textStyle:{color:'#333e48'}},candlestick:{itemStyle:{color:'#9e1b32',color0:colorset==='colorset2'?'#45842a':'#333e48',borderColor:'#6d1222',borderColor0:'#696969'}},tree:{lineStyle:{color:'#696969',opacity:1,width:2}},graph:{lineStyle:{color:'#696969',opacity:1,width:2}},lines:{lineStyle:{color:'#696969',opacity:1,width:2}},sankey:{lineStyle:{color:'#828282'}},gauge:{axisLine:{lineStyle:{color:[[1,'#cfcfcf']]}},axisTick:{lineStyle:{color:'#828282'}},splitLine:{lineStyle:{color:'#696969'}},axisLabel:{color:'#696969'},detail:{color:'#333e48'}},calendar:{itemStyle:{color:'#ffffff',borderColor:'#cfcfcf'},dayLabel:{color:'#696969'},monthLabel:{color:'#696969'},yearLabel:{color:'#333e48'}} }
}
