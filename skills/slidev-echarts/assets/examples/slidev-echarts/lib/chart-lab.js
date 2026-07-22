import { echarts } from './echarts-setup.js'
import timeSeries from '../data/time-series.json'
import categorical from '../data/categorical.json'
import distributions from '../data/distributions.json'
import financial from '../data/financial.json'
import hierarchy from '../data/hierarchy.json'
import relationships from '../data/relationships.json'
import river from '../data/river.json'
import spatial from '../data/spatial.json'

const colors = ['#007298', '#45842a', '#e77204', '#9e1b32', '#652f6c', '#828282']
let mapsRegistered = false

function registerSyntheticMaps() {
  if (mapsRegistered)
    return
  echarts.registerMap('Synthetic Hubs', spatial.geoJson)
  mapsRegistered = true
}

function stepIndex(step, max = 2) {
  return Math.min(Math.max(Number(step) || 0, 0), max)
}

function baseOption(title) {
  return {
    aria: { show: true },
    backgroundColor: 'transparent',
    color: colors,
    animationDuration: 800,
    animationDurationUpdate: 800,
    animationEasing: 'cubicOut',
    animationEasingUpdate: 'cubicOut',
    tooltip: {},
    title: {
      text: title,
      left: 12,
      top: 6,
      textStyle: { color: '#333e48', fontSize: 14, fontWeight: 700 },
    },
  }
}

function cartesian(title) {
  return {
    ...baseOption(title),
    tooltip: { trigger: 'axis' },
    grid: { top: 58, right: 32, bottom: 42, left: 48 },
    xAxis: {
      type: 'category',
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#cfcfcf' } },
      axisLabel: { color: '#696969' },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#e7e7e7' } },
      axisLabel: { color: '#696969' },
    },
  }
}

function productValues(field) {
  return categorical.products.map((item) => item[field])
}

function channelData(field = 'value') {
  return categorical.channelMix.map((item) => ({
    name: item.name,
    value: item[field],
  }))
}

function shifted(values, step, amount) {
  return values.map((value, index) => Math.round(value + (step * amount * (index + 1)) / values.length))
}

function riverRows(step) {
  return river.streams.flatMap((name) =>
    river.dates.map((date, index) => [
      date,
      Math.round(river.values[name][index] * (1 + step * (name === 'Product' ? 0.12 : name === 'Partners' ? 0.08 : -0.03))),
      name,
    ]),
  )
}

function treeWithLift(step) {
  return {
    ...hierarchy.tree,
    children: hierarchy.tree.children.map((group, groupIndex) => ({
      ...group,
      children: group.children.map((item, itemIndex) => ({
        ...item,
        value: item.value + step * (groupIndex + itemIndex + 1) * 4,
      })),
    })),
  }
}

function treeNodeLabel(params) {
  if (!params.data?.value)
    return params.name
  return `${params.name} ${Math.round(params.data.value)}`
}

function portfolioWithLift(step) {
  return hierarchy.portfolio.map((group, groupIndex) => ({
    ...group,
    children: group.children.map((item, itemIndex) => ({
      ...item,
      value: item.value + step * (groupIndex + itemIndex + 1) * 3,
    })),
  }))
}

function graphNodes(step) {
  return relationships.nodes.map((node, index) => ({
    ...node,
    value: node.value + step * (index % 3) * 4,
    symbolSize: 18 + node.value * 0.45 + step * (index % 3) * 2,
  }))
}

function relationshipLinks(step, source = relationships.links) {
  return source.map((link, index) => ({
    ...link,
    value: link.value + step * (index % 2 === 0 ? 4 : 2),
  }))
}

function weightedRelationshipLinks(step, source = relationships.links) {
  return relationshipLinks(step, source).map((link) => ({
    ...link,
    lineStyle: { width: Math.max(1.4, link.value / 15) },
  }))
}

function lineOption(step) {
  const stage = stepIndex(step)
  const scenario = shifted(timeSeries.revenue.scenario, stage, 10)
  return {
    ...cartesian('ARR index trend'),
    legend: { right: 8, top: 8, textStyle: { color: '#696969' } },
    xAxis: { ...cartesian().xAxis, data: timeSeries.months },
    series: [
      {
        id: 'baseline',
        name: 'Baseline',
        type: 'line',
        smooth: true,
        data: timeSeries.revenue.baseline,
        lineStyle: { width: 2, type: 'dashed' },
      },
      {
        id: 'scenario',
        name: stage < 2 ? 'Scenario' : 'Scenario with update',
        type: 'line',
        smooth: true,
        data: scenario,
        areaStyle: { opacity: 0.12 },
        symbolSize: 8,
        lineStyle: { width: 4 },
        universalTransition: true,
      },
    ],
  }
}

function barOption(step) {
  const stage = stepIndex(step)
  return {
    ...cartesian('Product contribution'),
    xAxis: { ...cartesian().xAxis, data: categorical.products.map((item) => item.name) },
    series: [
      {
        id: 'product-bars',
        type: 'bar',
        data: stage === 0 ? productValues('previous') : shifted(productValues('value'), stage - 1, 8),
        barWidth: 34,
        itemStyle: { borderRadius: [6, 6, 0, 0] },
        label: { show: stage > 1, position: 'top', color: '#4f4f4f' },
        universalTransition: true,
      },
    ],
  }
}

function pieOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Channel mix'),
    legend: { bottom: 0, left: 'center', textStyle: { color: '#696969' } },
    tooltip: { trigger: 'item' },
    series: [
      {
        id: 'channel-mix',
        type: 'pie',
        radius: stage > 0 ? ['42%', '70%'] : ['0%', '68%'],
        center: ['50%', '48%'],
        data: channelData(stage > 1 ? 'next' : 'value'),
        label: { formatter: '{b}\n{d}%', color: '#4f4f4f' },
        universalTransition: true,
      },
    ],
  }
}

function scatterOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Opportunity portfolio'),
    tooltip: {
      formatter: (params) => {
        const [name, confidence, impact, effort] = params.data
        return `${name}<br/>Confidence: ${confidence}%<br/>Impact: ${impact}<br/>Effort: ${effort}`
      },
    },
    grid: { top: 56, right: 30, bottom: 42, left: 48 },
    xAxis: { min: 50, max: 100, name: 'Confidence', axisLabel: { formatter: '{value}%', color: '#696969' }, splitLine: { lineStyle: { color: '#e7e7e7' } } },
    yAxis: { min: 40, max: 100, name: 'Impact', axisLabel: { color: '#696969' }, splitLine: { lineStyle: { color: '#e7e7e7' } } },
    visualMap: { show: false, dimension: 3, min: 10, max: 34, inRange: { symbolSize: [10, 32], color: ['#45842a', '#e77204', '#9e1b32'] } },
    series: [
      {
        id: 'opportunities',
        type: 'scatter',
        data: distributions.opportunities.map(([name, confidence, impact, effort], index) => [
          name,
          Math.min(99, confidence + stage * (index % 2 ? 2 : 4)),
          Math.min(98, impact + stage * (index % 3 ? 3 : 5)),
          effort,
        ]),
        encode: { x: 1, y: 2, tooltip: [0, 1, 2, 3] },
        universalTransition: true,
      },
    ],
  }
}

function radarOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Capability shape'),
    legend: { bottom: 0, left: 'center', textStyle: { color: '#696969' } },
    tooltip: {},
    radar: {
      center: ['50%', '48%'],
      radius: '58%',
      indicator: distributions.capabilities.labels.map((name) => ({ name, max: 100 })),
      axisName: { color: '#696969' },
      splitLine: { lineStyle: { color: '#cfcfcf' } },
      splitArea: { areaStyle: { color: ['#f7f7f7', '#eef2f7'] } },
    },
    series: [
      {
        id: 'capability',
        type: 'radar',
        areaStyle: { opacity: 0.16 },
        data: [
          { name: 'Current', value: shifted(distributions.capabilities.current, stage, 8) },
          { name: 'Target', value: distributions.capabilities.target },
        ],
      },
    ],
  }
}

function mapOption(step) {
  const stage = stepIndex(step)
  registerSyntheticMaps()
  return {
    ...baseOption('Synthetic regional map'),
    tooltip: { trigger: 'item' },
    visualMap: { min: 50, max: 90, left: 12, bottom: 16, text: ['High', 'Low'], inRange: { color: ['#cdf3ff', '#007298'] }, textStyle: { color: '#696969' } },
    series: [
      {
        id: 'hub-map',
        type: 'map',
        map: 'Synthetic Hubs',
        roam: false,
        top: 44,
        bottom: 18,
        label: { show: true, color: '#333e48' },
        emphasis: { label: { color: '#333e48' } },
        data: spatial.mapValues.map((item) => ({ name: item.name, value: stage > 0 ? item.next : item.value })),
        universalTransition: true,
      },
    ],
  }
}

function treeOption(step) {
  return {
    ...baseOption('Growth system tree'),
    tooltip: { trigger: 'item', triggerOn: 'mousemove' },
    series: [
      {
        id: 'tree',
        type: 'tree',
        data: [treeWithLift(stepIndex(step))],
        top: 42,
        left: 128,
        bottom: 18,
        right: 126,
        symbolSize: 10,
        orient: 'LR',
        expandAndCollapse: false,
        label: {
          color: '#4f4f4f',
          position: 'left',
          verticalAlign: 'middle',
          align: 'right',
          backgroundColor: 'rgba(255, 255, 255, 0.86)',
          padding: [1, 3],
          formatter: treeNodeLabel,
        },
        leaves: {
          label: {
            position: 'right',
            align: 'left',
            backgroundColor: 'rgba(255, 255, 255, 0.86)',
            padding: [1, 3],
            formatter: treeNodeLabel,
          },
        },
        lineStyle: { color: '#9c9c9c' },
        animationDurationUpdate: 700,
      },
    ],
  }
}

function treemapOption(step) {
  return {
    ...baseOption('Portfolio allocation treemap'),
    tooltip: { trigger: 'item' },
    series: [
      {
        id: 'treemap',
        type: 'treemap',
        roam: false,
        top: 48,
        left: 12,
        right: 12,
        bottom: 12,
        breadcrumb: { show: false },
        label: { show: true, formatter: '{b}' },
        upperLabel: { show: true, height: 22 },
        levels: [{ itemStyle: { borderColor: '#fff', borderWidth: 3, gapWidth: 3 } }],
        data: portfolioWithLift(stepIndex(step)),
        universalTransition: true,
      },
    ],
  }
}

function graphOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Relationship graph'),
    tooltip: {},
    legend: { show: false },
    series: [
      {
        id: 'graph',
        type: 'graph',
        layout: 'circular',
        circular: { rotateLabel: false },
        roam: false,
        top: 46,
        bottom: 20,
        data: graphNodes(stage).map((node) => ({
          ...node,
          itemStyle: { borderColor: '#ffffff', borderWidth: 2 },
        })),
        links: weightedRelationshipLinks(stage),
        label: {
          show: true,
          color: '#1e293b',
          position: 'right',
          distance: 6,
          backgroundColor: 'rgba(255, 255, 255, 0.82)',
          padding: [1, 3],
        },
        lineStyle: { color: 'source', curveness: 0.24, opacity: 0.62 },
        emphasis: { focus: 'adjacency' },
        universalTransition: true,
      },
    ],
  }
}

function chordOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Channel overlap chord'),
    tooltip: {},
    series: [
      {
        id: 'chord',
        type: 'chord',
        radius: ['60%', '75%'],
        center: ['50%', '52%'],
        data: relationships.nodes.slice(0, 6).map((node) => ({ name: node.name, value: node.value })),
        links: relationshipLinks(stage, relationships.chordLinks),
        label: {
          color: '#1e293b',
          backgroundColor: 'rgba(255, 255, 255, 0.82)',
          padding: [1, 3],
        },
        lineStyle: { opacity: 0.36, color: 'source' },
        universalTransition: true,
      },
    ],
  }
}

function gaugeOption(step) {
  const value = stepIndex(step) > 0 ? categorical.gauge.next : categorical.gauge.value
  return {
    ...baseOption('Operating readiness'),
    series: [
      {
        id: 'readiness',
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: 1,
        progress: { show: true, width: 18 },
        axisLine: { lineStyle: { width: 18 } },
        axisLabel: { formatter: (v) => `${Math.round(v * 100)}%`, color: '#696969' },
        anchor: { show: true, showAbove: true, size: 14 },
        detail: { valueAnimation: true, formatter: (v) => `${Math.round(v * 100)}%`, fontSize: 30, color: '#333e48' },
        data: [{ value, name: categorical.gauge.label }],
      },
    ],
  }
}

function funnelOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Conversion funnel'),
    tooltip: { trigger: 'item' },
    legend: { show: false },
    series: [
      {
        id: 'funnel',
        type: 'funnel',
        left: '12%',
        top: 52,
        bottom: 12,
        width: '76%',
        minSize: '18%',
        maxSize: '92%',
        gap: 4,
        sort: 'descending',
        label: { show: true, position: 'inside', formatter: '{b}: {c}' },
        data: categorical.funnel.map((item) => ({ name: item.name, value: stage > 0 ? item.next : item.value })),
        universalTransition: true,
      },
    ],
  }
}

function parallelOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Segment profile parallel coordinates'),
    tooltip: {},
    parallelAxis: [
      { dim: 0, name: 'Coverage' },
      { dim: 1, name: 'Quality' },
      { dim: 2, name: 'Speed' },
      { dim: 3, name: 'Margin' },
      { dim: 4, name: 'Retention' },
    ],
    parallel: { left: 56, right: 40, top: 66, bottom: 36, parallelAxisDefault: { type: 'value', min: 50, max: 100, nameTextStyle: { color: '#696969' }, axisLabel: { color: '#828282' } } },
    series: [
      {
        id: 'parallel',
        type: 'parallel',
        lineStyle: { width: 3, opacity: 0.45 },
        data: distributions.parallel.map((row, index) => row.slice(1).map((value) => value + stage * (index % 2 ? 2 : 4))),
      },
    ],
  }
}

function sankeyOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Lead flow sankey'),
    tooltip: { trigger: 'item' },
    series: [
      {
        id: 'sankey',
        type: 'sankey',
        top: 42,
        bottom: 12,
        left: 18,
        right: 88,
        nodeWidth: 20,
        nodeGap: 10,
        nodeAlign: 'justify',
        data: relationships.nodes,
        links: relationshipLinks(stage),
        label: {
          color: '#1e293b',
          backgroundColor: 'rgba(255, 255, 255, 0.76)',
          padding: [1, 3],
        },
        lineStyle: { color: 'gradient', curveness: 0.48, opacity: 0.46 },
        emphasis: { focus: 'adjacency' },
        universalTransition: true,
      },
    ],
  }
}

function boxplotOption(step) {
  const stage = stepIndex(step)
  return {
    ...cartesian('Cycle-time distribution'),
    xAxis: { ...cartesian().xAxis, data: distributions.cohorts },
    yAxis: { ...cartesian().yAxis, name: 'Days' },
    series: [
      {
        id: 'boxplot',
        type: 'boxplot',
        data: distributions.boxplot.map((box, index) => box.map((value) => value + stage * (index + 1))),
        itemStyle: { color: '#cdf3ff', borderColor: '#007298' },
        universalTransition: true,
      },
    ],
  }
}

function candlestickOption(step) {
  const stage = stepIndex(step)
  return {
    ...cartesian('Synthetic index candlestick'),
    xAxis: { ...cartesian().xAxis, data: financial.days },
    yAxis: { ...cartesian().yAxis, scale: true },
    series: [
      {
        id: 'candlestick',
        type: 'candlestick',
        data: financial.ohlc.map((row, index) => row.map((value) => value + (stage > 0 && index > 3 ? 3 : 0))),
        itemStyle: { color: '#9e1b32', color0: '#45842a', borderColor: '#9e1b32', borderColor0: '#45842a' },
      },
    ],
  }
}

function effectScatterOption(step) {
  const stage = stepIndex(step)
  return {
    ...scatterOption(stage),
    title: { ...baseOption('Priority pulses').title },
    series: [
      {
        id: 'priority-pulses',
        type: 'effectScatter',
        data: distributions.opportunities.slice(0, 5).map(([name, confidence, impact, effort], index) => [name, confidence + stage * 3, impact + stage * (index + 1), effort]),
        encode: { x: 1, y: 2, tooltip: [0, 1, 2, 3] },
        symbolSize: (value) => value[3] * 0.8,
        showEffectOn: stage > 0 ? 'render' : 'emphasis',
        rippleEffect: { brushType: 'stroke', scale: 3.8 },
      },
    ],
  }
}

function linesOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Route lines on a planning grid'),
    tooltip: {},
    grid: { top: 56, right: 28, bottom: 38, left: 44 },
    xAxis: { min: 0, max: 70, axisLabel: { color: '#696969' }, splitLine: { lineStyle: { color: '#e7e7e7' } } },
    yAxis: { min: 0, max: 90, axisLabel: { color: '#696969' }, splitLine: { lineStyle: { color: '#e7e7e7' } } },
    series: [
      {
        id: 'route-lines',
        type: 'lines',
        coordinateSystem: 'cartesian2d',
        data: spatial.routes.map((route) => ({
          name: route.name,
          coords: route.coords,
          lineStyle: { width: Math.max(2, route.value / 8 + stage) },
        })),
        symbol: ['circle', 'arrow'],
        symbolSize: [5, 11],
        lineStyle: { color: '#007298', curveness: 0.18, opacity: 0.72 },
      },
      {
        id: 'route-points',
        type: 'scatter',
        data: [[0, 22], [28, 44], [62, 58], [18, 78], [8, 15]],
        symbolSize: 8,
        itemStyle: { color: '#9e1b32' },
      },
    ],
  }
}

function heatmapOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Engagement heatmap'),
    tooltip: { position: 'top' },
    grid: { top: 58, right: 28, bottom: 64, left: 52 },
    xAxis: { type: 'category', data: distributions.heatmap.days, splitArea: { show: true }, axisLabel: { color: '#696969' } },
    yAxis: { type: 'category', data: distributions.heatmap.hours, splitArea: { show: true }, axisLabel: { color: '#696969' } },
    visualMap: { min: 10, max: 70, calculable: true, orient: 'horizontal', left: 'center', bottom: 6, inRange: { color: ['#cdf3ff', '#007298', '#9e1b32'] } },
    series: [
      {
        id: 'heatmap',
        type: 'heatmap',
        data: distributions.heatmap.values.map(([x, y, value]) => [x, y, value + stage * (x + y)]),
        label: { show: stage > 1 },
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(15,23,42,0.25)' } },
      },
    ],
  }
}

function pictorialBarOption(step) {
  const stage = stepIndex(step)
  return {
    ...cartesian('Capacity pictorial bars'),
    xAxis: { ...cartesian().xAxis, data: categorical.products.map((item) => item.name) },
    yAxis: { ...cartesian().yAxis, max: 90 },
    series: [
      {
        id: 'pictorial',
        type: 'pictorialBar',
        symbol: 'roundRect',
        symbolRepeat: true,
        symbolSize: [18, 8],
        symbolMargin: 2,
        data: shifted(productValues('value'), stage, 8),
        label: { show: true, position: 'top', color: '#4f4f4f' },
        itemStyle: { color: '#45842a' },
        universalTransition: true,
      },
    ],
  }
}

function themeRiverOption(step) {
  return {
    ...baseOption('Demand stream theme river'),
    tooltip: { trigger: 'axis' },
    legend: { top: 28, right: 8, textStyle: { color: '#696969' } },
    singleAxis: {
      top: 78,
      bottom: 36,
      left: 52,
      right: 24,
      type: 'time',
      axisLabel: { color: '#696969' },
      axisLine: { lineStyle: { color: '#cfcfcf' } },
    },
    series: [
      {
        id: 'theme-river',
        type: 'themeRiver',
        data: riverRows(stepIndex(step)),
        label: { show: false },
        emphasis: { focus: 'series' },
      },
    ],
  }
}

function sunburstOption(step) {
  return {
    ...baseOption('Portfolio sunburst'),
    tooltip: { trigger: 'item' },
    series: [
      {
        id: 'sunburst',
        type: 'sunburst',
        data: portfolioWithLift(stepIndex(step)),
        radius: [0, '78%'],
        center: ['50%', '54%'],
        sort: null,
        label: { rotate: 'radial', color: '#4f4f4f' },
        levels: [{}, { r0: '18%', r: '42%' }, { r0: '42%', r: '78%' }],
        universalTransition: true,
      },
    ],
  }
}

function customOption(step) {
  const stage = stepIndex(step)
  return {
    ...baseOption('Custom timeline ranges'),
    tooltip: {},
    grid: { top: 58, right: 28, bottom: 42, left: 78 },
    xAxis: { min: 0, max: 110, axisLabel: { formatter: '{value}%', color: '#696969' }, splitLine: { lineStyle: { color: '#e7e7e7' } } },
    yAxis: { type: 'category', data: distributions.ranges.map((row) => row[0]), axisLabel: { color: '#696969' } },
    series: [
      {
        id: 'custom-ranges',
        type: 'custom',
        data: distributions.ranges.map(([name, start, end, value], index) => [index, start, end + stage * 4, value]),
        encode: { x: [1, 2], y: 0 },
        renderItem(params, api) {
          const categoryIndex = api.value(0)
          const start = api.coord([api.value(1), categoryIndex])
          const end = api.coord([api.value(2), categoryIndex])
          const height = api.size([0, 1])[1] * 0.56
          return {
            type: 'rect',
            shape: {
              x: start[0],
              y: start[1] - height / 2,
              width: Math.max(2, end[0] - start[0]),
              height,
              r: 6,
            },
            style: {
              fill: colors[categoryIndex % colors.length],
            },
          }
        },
      },
    ],
  }
}

export const chartSpecs = {
  line: {
    title: 'Line Chart',
    type: 'line',
    summary: 'Use line charts for ordered trends where update animation should preserve continuity.',
    dataShape: 'Shared monthly revenue arrays with stable series IDs.',
    animation: 'Morphs the scenario line and area while keeping the baseline anchored.',
    modules: ['LineChart', 'GridComponent', 'TooltipComponent', 'LegendComponent'],
    option: lineOption,
  },
  bar: {
    title: 'Bar Chart',
    type: 'bar',
    summary: 'Use bars for ranked categorical magnitude and clear before-after comparisons.',
    dataShape: 'Product category objects with previous and current values.',
    animation: 'Updates bar heights and reveals value labels on the final click.',
    modules: ['BarChart', 'GridComponent'],
    option: barOption,
  },
  pie: {
    title: 'Pie Chart',
    type: 'pie',
    summary: 'Use pie or donut charts for a small number of parts of one whole.',
    dataShape: 'Channel mix objects with stable names for slice diffing.',
    animation: 'Transitions from full pie to donut and then morphs the mix.',
    modules: ['PieChart', 'LegendComponent'],
    option: pieOption,
  },
  scatter: {
    title: 'Scatter Chart',
    type: 'scatter',
    summary: 'Use scatter plots to expose relationships between two quantitative measures.',
    dataShape: 'Opportunity tuples: name, confidence, impact, effort.',
    animation: 'Moves points by confidence and impact while visualMap scales effort.',
    modules: ['ScatterChart', 'GridComponent', 'VisualMapComponent'],
    option: scatterOption,
  },
  radar: {
    title: 'Radar Chart',
    type: 'radar',
    summary: 'Use radar charts for compact multidimensional profile comparisons.',
    dataShape: 'Capability labels plus current and target score vectors.',
    animation: 'Expands the current polygon toward the target profile.',
    modules: ['RadarChart', 'RadarComponent', 'LegendComponent'],
    option: radarOption,
  },
  map: {
    title: 'Map Chart',
    type: 'map',
    summary: 'Use maps when spatial adjacency or region ownership carries meaning.',
    dataShape: 'Synthetic GeoJSON features plus per-region values.',
    animation: 'Morphs choropleth values after registering the synthetic map.',
    modules: ['MapChart', 'GeoComponent', 'VisualMapComponent'],
    option: mapOption,
  },
  tree: {
    title: 'Tree Chart',
    type: 'tree',
    summary: 'Use trees for explicit parent-child structures and dependency paths.',
    dataShape: 'Nested growth-system hierarchy with leaf values.',
    animation: 'Updates leaf values while keeping branch geometry stable.',
    modules: ['TreeChart'],
    option: treeOption,
  },
  treemap: {
    title: 'Treemap Chart',
    type: 'treemap',
    summary: 'Use treemaps for hierarchical part-to-whole allocation.',
    dataShape: 'Portfolio hierarchy reused with values on leaf nodes.',
    animation: 'Reflows rectangles as allocation weights change.',
    modules: ['TreemapChart'],
    option: treemapOption,
  },
  graph: {
    title: 'Graph Chart',
    type: 'graph',
    summary: 'Use graph charts for node-link relationships where topology matters.',
    dataShape: 'Shared relationship nodes and weighted links.',
    animation: 'Changes node size and link weights in a circular layout.',
    modules: ['GraphChart'],
    option: graphOption,
  },
  chord: {
    title: 'Chord Chart',
    type: 'chord',
    summary: 'Use chord charts for symmetric or overlapping flows among a small set of categories.',
    dataShape: 'Relationship nodes plus chord-specific weighted links.',
    animation: 'Updates ribbon widths while keeping category arcs stable.',
    modules: ['ChordChart'],
    option: chordOption,
  },
  gauge: {
    title: 'Gauge Chart',
    type: 'gauge',
    summary: 'Use gauges for one headline ratio when the threshold context is obvious.',
    dataShape: 'Single readiness ratio with current and next values.',
    animation: 'Uses valueAnimation to move the needle and numeric detail.',
    modules: ['GaugeChart'],
    option: gaugeOption,
  },
  funnel: {
    title: 'Funnel Chart',
    type: 'funnel',
    summary: 'Use funnels for ordered attrition across process stages.',
    dataShape: 'Stage objects with current and improved counts.',
    animation: 'Morphs segment widths as conversion improves.',
    modules: ['FunnelChart'],
    option: funnelOption,
  },
  parallel: {
    title: 'Parallel Chart',
    type: 'parallel',
    summary: 'Use parallel coordinates to compare many measures across several entities.',
    dataShape: 'Segment rows with five normalized capability dimensions.',
    animation: 'Slides polylines as segment scores improve.',
    modules: ['ParallelChart', 'ParallelComponent'],
    option: parallelOption,
  },
  sankey: {
    title: 'Sankey Chart',
    type: 'sankey',
    summary: 'Use sankey charts for directed volume transfer across stages.',
    dataShape: 'Shared relationship nodes and directed links.',
    animation: 'Changes link widths while preserving the flow path.',
    modules: ['SankeyChart'],
    option: sankeyOption,
  },
  boxplot: {
    title: 'Boxplot Chart',
    type: 'boxplot',
    summary: 'Use boxplots to compare distributions without showing every point.',
    dataShape: 'Precomputed five-number summaries by cohort.',
    animation: 'Updates distribution ranges and median positions.',
    modules: ['BoxplotChart', 'GridComponent'],
    option: boxplotOption,
  },
  candlestick: {
    title: 'Candlestick Chart',
    type: 'candlestick',
    summary: 'Use candlesticks for open-high-low-close interval movement.',
    dataShape: 'Synthetic OHLC arrays keyed by trading day.',
    animation: 'Updates later-period candles to simulate a shifted index.',
    modules: ['CandlestickChart', 'GridComponent'],
    option: candlestickOption,
  },
  effectScatter: {
    title: 'Effect Scatter Chart',
    type: 'effectScatter',
    summary: 'Use effect scatter when priority points need pulsing attention.',
    dataShape: 'Opportunity tuples reused from the scatter chart.',
    animation: 'Switches ripple effects on and moves high-priority points.',
    modules: ['EffectScatterChart', 'GridComponent'],
    option: effectScatterOption,
  },
  lines: {
    title: 'Lines Chart',
    type: 'lines',
    summary: 'Use lines charts for directional origin-destination routes.',
    dataShape: 'Synthetic route coordinate pairs on a planning grid.',
    animation: 'Thickens high-volume routes and preserves arrowed origin-destination direction in SVG.',
    modules: ['LinesChart', 'ScatterChart', 'GridComponent'],
    option: linesOption,
  },
  heatmap: {
    title: 'Heatmap Chart',
    type: 'heatmap',
    summary: 'Use heatmaps for dense two-dimensional intensity patterns.',
    dataShape: 'Day-hour-value cells with a shared visual scale.',
    animation: 'Raises cell intensity and reveals labels on the final click.',
    modules: ['HeatmapChart', 'VisualMapComponent', 'GridComponent'],
    option: heatmapOption,
  },
  pictorialBar: {
    title: 'Pictorial Bar Chart',
    type: 'pictorialBar',
    summary: 'Use pictorial bars when repeated symbols make magnitude more memorable.',
    dataShape: 'Product contribution values reused from categorical data.',
    animation: 'Repeats rounded symbols as category values grow.',
    modules: ['PictorialBarChart', 'GridComponent'],
    option: pictorialBarOption,
  },
  themeRiver: {
    title: 'Theme River Chart',
    type: 'themeRiver',
    summary: 'Use theme river charts for stacked topic volume over time.',
    dataShape: 'Date, value, stream-name rows generated from shared channel data.',
    animation: 'Rebalances stream thickness over time.',
    modules: ['ThemeRiverChart', 'SingleAxisComponent', 'LegendComponent'],
    option: themeRiverOption,
  },
  sunburst: {
    title: 'Sunburst Chart',
    type: 'sunburst',
    summary: 'Use sunburst charts for radial hierarchical part-to-whole stories.',
    dataShape: 'Portfolio hierarchy reused from tree and treemap.',
    animation: 'Morphs ring segment sizes as leaf values change.',
    modules: ['SunburstChart'],
    option: sunburstOption,
  },
  custom: {
    title: 'Custom Chart',
    type: 'custom',
    summary: 'Use custom series when the mark geometry is domain-specific.',
    dataShape: 'Timeline range tuples rendered as rounded bars.',
    animation: 'Extends range bars through renderItem-driven geometry.',
    modules: ['CustomChart', 'GridComponent'],
    option: customOption,
  },
}

export const chartOrder = Object.keys(chartSpecs)

export function chartSpec(type) {
  return chartSpecs[type]
}
