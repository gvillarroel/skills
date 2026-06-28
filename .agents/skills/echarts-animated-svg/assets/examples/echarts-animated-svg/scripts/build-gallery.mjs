import { writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import * as echarts from 'echarts'

const __dirname = dirname(fileURLToPath(import.meta.url))
const exampleRoot = resolve(__dirname, '..')
const width = 520
const height = 330
const fontPrimary = '"Open Sans", Arial, sans-serif'
const iconFont = '"Material Symbols Rounded"'
const brand = {
  primary: '#9e1b32',
  neutral: '#333e48',
  red: '#9e1b32',
  orange: '#e77204',
  yellow: '#f1c319',
  green: '#45842a',
  blue: '#007298',
  purple: '#652f6c',
  black: '#000000',
  white: '#ffffff',
  gray10: '#e7e7e7',
  gray20: '#cfcfcf',
  gray30: '#b7b7b7',
  gray40: '#9f9f9f',
  gray50: '#878787',
  gray60: '#696969',
  gray70: '#4f4f4f',
  gray80: '#333e48',
  gray90: '#1c1c1c',
  background: '#f7f7f7',
  link: '#007298',
  linkHover: '#004d66',
  highlightRed: '#ffccd5',
  highlightOrange: '#ffe5cc',
  highlightYellow: '#fff4cc',
  highlightGreen: '#dbffcc',
  highlightBlue: '#cdf3ff',
  highlightPurple: '#f9ccff',
  success: '#36b300',
  warning: '#ff9633',
  caution: '#ffd332',
  info: '#00ace6',
}
const colors = [brand.red, brand.orange, brand.yellow, brand.green, brand.blue, brand.purple]
const highlights = [brand.highlightRed, brand.highlightOrange, brand.highlightYellow, brand.highlightGreen, brand.highlightBlue, brand.highlightPurple]
const axisLabelStyle = { color: brand.gray70, fontSize: 10 }
const axisNameStyle = { color: brand.neutral, fontSize: 11, fontWeight: 600 }
const legendTextStyle = { color: brand.neutral, fontSize: 10, fontWeight: 600 }
const darkCellText = brand.gray90
const lightCellText = brand.gray10
const lineSeriesPalette = [brand.red, brand.blue, brand.green, brand.purple, brand.orange, brand.yellow]
const phasePalette = [brand.purple, brand.blue, brand.orange, brand.green]

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
const products = [
  { name: 'Core', previous: 32, value: 48 },
  { name: 'Growth', previous: 26, value: 38 },
  { name: 'Platform', previous: 22, value: 34 },
  { name: 'Services', previous: 18, value: 25 },
]
const channelMix = [
  { name: 'Product', value: 34 },
  { name: 'Partners', value: 24 },
  { name: 'Search', value: 22 },
  { name: 'Events', value: 12 },
  { name: 'Outbound', value: 8 },
]
const opportunities = [
  ['Self Serve', 78, 88, 18],
  ['Expansion', 84, 72, 26],
  ['Marketplace', 68, 82, 14],
  ['Enterprise', 58, 64, 32],
  ['Automation', 92, 76, 20],
  ['Enablement', 73, 58, 12],
]
const capabilityLabels = ['Coverage', 'Quality', 'Speed', 'Margin', 'Retention']
const hierarchy = {
  name: 'Growth',
  children: [
    { name: 'Acquire', value: 36, children: [{ name: 'Search', value: 18 }, { name: 'Partner', value: 18 }] },
    { name: 'Convert', value: 42, children: [{ name: 'Trial', value: 22 }, { name: 'Sales', value: 20 }] },
    { name: 'Retain', value: 30, children: [{ name: 'Success', value: 18 }, { name: 'Education', value: 12 }] },
  ],
}
const portfolio = hierarchy.children
const nodes = [
  { name: 'Product', value: 42 },
  { name: 'Sales', value: 36 },
  { name: 'Success', value: 30 },
  { name: 'Partners', value: 26 },
  { name: 'Support', value: 22 },
  { name: 'Data', value: 18 },
]
const links = [
  { source: 'Product', target: 'Sales', value: 18 },
  { source: 'Product', target: 'Success', value: 13 },
  { source: 'Sales', target: 'Partners', value: 12 },
  { source: 'Success', target: 'Support', value: 10 },
  { source: 'Data', target: 'Product', value: 9 },
  { source: 'Partners', target: 'Success', value: 8 },
]
const nodeColors = {
  Product: brand.blue,
  Sales: brand.orange,
  Success: brand.green,
  Partners: brand.yellow,
  Support: brand.red,
  Data: brand.purple,
  Core: brand.red,
}
const stageColors = {
  Plan: brand.purple,
  Discovery: brand.purple,
  Build: brand.blue,
  Launch: brand.orange,
  Learn: brand.green,
}
const treemapColors = {
  Acquire: brand.orange,
  Search: brand.yellow,
  Partner: brand.blue,
  Events: brand.purple,
  Convert: brand.red,
  Trial: brand.red,
  Sales: brand.orange,
  Lifecycle: brand.purple,
  Retain: brand.green,
  Success: brand.green,
  Education: brand.blue,
  Support: brand.purple,
}
const geoJson = {
  type: 'FeatureCollection',
  features: [
    polygon('North Hub', [[[0, 3], [2, 3], [2, 5], [0, 5], [0, 3]]]),
    polygon('West Hub', [[[0, 0], [2, 0], [2, 3], [0, 3], [0, 0]]]),
    polygon('Central Hub', [[[2, 1], [4, 1], [4, 4], [2, 4], [2, 1]]]),
    polygon('East Hub', [[[4, 0], [6, 0], [6, 4], [4, 4], [4, 0]]]),
  ],
}
echarts.registerMap('Synthetic Hubs', geoJson)

const chartDefinitions = [
  {
    type: 'line',
    title: 'Line',
    summary: 'Trend continuity through stroke drawing.',
    option: () => ({
      ...cartesian('ARR index trend'),
      legend: { right: 8, top: 8, textStyle: legendTextStyle },
      xAxis: { ...categoryAxis(), data: months },
      series: [
        { name: 'Baseline', type: 'line', smooth: true, data: [44, 47, 50, 54, 58, 61], lineStyle: { width: 2, type: 'dashed' } },
        { name: 'Scenario', type: 'line', smooth: true, data: [42, 50, 56, 63, 71, 82], areaStyle: { opacity: 0.12 }, symbolSize: 8, lineStyle: { width: 4 } },
      ],
    }),
  },
  {
    type: 'bar',
    title: 'Bar',
    summary: 'Category growth from a shared baseline.',
    option: () => ({
      ...cartesian('Product contribution'),
      xAxis: { ...categoryAxis(), data: products.map((item) => item.name) },
      series: [{ type: 'bar', barWidth: 34, itemStyle: { borderRadius: [6, 6, 0, 0] }, label: { show: true, position: 'top' }, data: products.map((item) => item.value) }],
    }),
  },
  {
    type: 'pie',
    title: 'Pie',
    summary: 'Part-to-whole slices revealed around the center.',
    option: () => ({
      ...baseOption('Channel mix'),
      legend: { bottom: 0, left: 'center', textStyle: legendTextStyle },
      series: [{ type: 'pie', radius: ['42%', '70%'], center: ['50%', '48%'], label: { formatter: '{b}\n{d}%' }, data: channelMix }],
    }),
  },
  {
    type: 'scatter',
    title: 'Scatter',
    summary: 'Opportunity points fade in without moving axes.',
    option: () => ({
      ...baseOption('Opportunity portfolio'),
      grid: { top: 56, right: 30, bottom: 42, left: 48 },
      xAxis: { min: 50, max: 100, name: 'Confidence', axisLabel: { formatter: '{value}%' }, splitLine: splitLine() },
      yAxis: { min: 40, max: 100, name: 'Impact', splitLine: splitLine() },
      visualMap: { show: false, dimension: 3, min: 10, max: 34, inRange: { symbolSize: [10, 32], color: ['#45842a', '#e77204', '#9e1b32'] } },
      series: [{ type: 'scatter', data: opportunities, encode: { x: 1, y: 2, tooltip: [0, 1, 2, 3] } }],
    }),
  },
  {
    type: 'radar',
    title: 'Radar',
    summary: 'Grid, benchmark, then current profile.',
    option: () => ({
      ...baseOption('Capability shape'),
      legend: { bottom: 0, left: 'center', textStyle: legendTextStyle },
      radar: {
        center: ['50%', '48%'],
        radius: '58%',
        indicator: capabilityLabels.map((name) => ({ name, max: 100 })),
        axisName: axisNameStyle,
        splitLine: { lineStyle: { color: '#cfcfcf' } },
        splitArea: { areaStyle: { color: [brand.background, brand.gray10] } },
      },
      series: [{ type: 'radar', areaStyle: { opacity: 0.16 }, data: [{ name: 'Current', value: [72, 65, 78, 62, 70] }, { name: 'Target', value: [88, 82, 84, 80, 86] }] }],
    }),
  },
  {
    type: 'map',
    title: 'Map',
    summary: 'Regions fade in with boundaries kept readable.',
    option: () => ({
      ...baseOption('Synthetic regional map'),
      visualMap: { min: 50, max: 90, left: 12, bottom: 16, text: ['High', 'Low'], inRange: { color: [brand.highlightBlue, brand.blue, brand.purple] }, textStyle: legendTextStyle },
      series: [{ type: 'map', map: 'Synthetic Hubs', top: 44, bottom: 18, label: { show: true, color: '#333e48' }, data: [
        { name: 'North Hub', value: 84 },
        { name: 'West Hub', value: 63 },
        { name: 'Central Hub', value: 78 },
        { name: 'East Hub', value: 71 },
      ] }],
    }),
  },
  {
    type: 'tree',
    title: 'Tree',
    summary: 'Root, branches, then leaves and labels.',
    option: () => ({
      ...baseOption('Growth system tree'),
      series: [{ type: 'tree', data: [hierarchy], top: 42, left: 58, bottom: 18, right: 90, orient: 'LR', expandAndCollapse: false, symbolSize: 10, label: { color: '#333e48', position: 'left', align: 'right' }, leaves: { label: { position: 'right', align: 'left' } }, lineStyle: { color: brand.gray40 } }],
    }),
  },
  {
    type: 'treemap',
    title: 'Treemap',
    summary: 'Parent areas settle before labels.',
    option: () => ({
      ...baseOption('Portfolio allocation treemap'),
      series: [{ type: 'treemap', roam: false, top: 48, left: 12, right: 12, bottom: 12, breadcrumb: { show: false }, label: { show: true }, upperLabel: { show: true, height: 22 }, levels: [{ itemStyle: { borderColor: '#fff', borderWidth: 3, gapWidth: 3 } }], data: portfolio }],
    }),
  },
  {
    type: 'graph',
    title: 'Graph',
    summary: 'Nodes appear before topology links.',
    option: () => ({
      ...baseOption('Relationship graph'),
      series: [{ type: 'graph', layout: 'circular', top: 46, bottom: 20, roam: false, data: nodes.map((node) => ({ ...node, symbolSize: 20 + node.value * 0.45 })), links, label: { show: true, color: '#333e48' }, lineStyle: { color: 'source', curveness: 0.24, opacity: 0.5 } }],
    }),
  },
  {
    type: 'chord',
    title: 'Chord',
    summary: 'Outer arcs orient before ribbons fade in.',
    option: () => ({
      ...baseOption('Channel overlap chord'),
      series: [{ type: 'chord', radius: ['62%', '74%'], center: ['50%', '52%'], data: nodes.slice(0, 6).map((node) => ({ name: node.name, value: node.value })), links, label: { color: '#333e48' }, lineStyle: { opacity: 0.28, color: 'source' } }],
    }),
  },
  {
    type: 'gauge',
    title: 'Gauge',
    summary: 'Arc and value settle into one ratio.',
    option: () => ({
      ...baseOption('Operating readiness'),
      series: [{ type: 'gauge', startAngle: 210, endAngle: -30, min: 0, max: 1, progress: { show: true, width: 18 }, axisLine: { lineStyle: { width: 18 } }, axisLabel: { formatter: (value) => `${Math.round(value * 100)}%` }, anchor: { show: true, showAbove: true, size: 14 }, detail: { valueAnimation: false, formatter: (value) => `${Math.round(value * 100)}%`, fontSize: 30, color: '#333e48' }, data: [{ value: 0.78, name: 'Readiness' }] }],
    }),
  },
  {
    type: 'funnel',
    title: 'Funnel',
    summary: 'Stages reveal from top to bottom.',
    option: () => ({
      ...baseOption('Conversion funnel'),
      series: [{ type: 'funnel', left: '12%', top: 52, bottom: 12, width: '76%', minSize: '18%', maxSize: '92%', gap: 4, sort: 'descending', label: { show: true, position: 'inside', formatter: '{b}: {c}' }, data: [
        { name: 'Visitors', value: 100 },
        { name: 'Trials', value: 62 },
        { name: 'Qualified', value: 38 },
        { name: 'Won', value: 21 },
      ] }],
    }),
  },
  {
    type: 'parallel',
    title: 'Parallel',
    summary: 'Axes first, then multidimensional polylines.',
    option: () => ({
      ...baseOption('Segment profile parallel coordinates'),
      parallelAxis: capabilityLabels.map((name, dim) => ({ dim, name })),
      parallel: { left: 56, right: 40, top: 72, bottom: 42, parallelAxisDefault: parallelAxisDefault(50, 100) },
      series: [{ type: 'parallel', lineStyle: { width: 3, opacity: 0.45 }, data: [[72, 65, 78, 62, 70], [84, 72, 76, 80, 74], [66, 88, 70, 76, 82], [78, 75, 84, 68, 88]] }],
    }),
  },
  {
    type: 'sankey',
    title: 'Sankey',
    summary: 'Columns establish endpoints before links.',
    option: () => ({
      ...baseOption('Lead flow sankey'),
      series: [{ type: 'sankey', top: 50, bottom: 16, left: 18, right: 70, nodeAlign: 'justify', data: nodes, links, label: { color: '#333e48' }, lineStyle: { color: 'gradient', curveness: 0.48, opacity: 0.35 } }],
    }),
  },
  {
    type: 'boxplot',
    title: 'Boxplot',
    summary: 'Distribution summaries build by cohort.',
    option: () => ({
      ...cartesian('Cycle-time distribution'),
      xAxis: { ...categoryAxis(), data: ['Starter', 'Growth', 'Scale', 'Enterprise'] },
      yAxis: { ...valueAxis(), name: 'Days' },
      series: [{ type: 'boxplot', itemStyle: { color: '#cdf3ff', borderColor: '#007298' }, data: [[12, 18, 24, 30, 38], [10, 16, 22, 28, 34], [14, 20, 26, 36, 48], [16, 24, 32, 46, 60]] }],
    }),
  },
  {
    type: 'candlestick',
    title: 'Candlestick',
    summary: 'OHLC movement reads left to right.',
    option: () => ({
      ...cartesian('Synthetic index candlestick'),
      xAxis: { ...categoryAxis(), data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'] },
      yAxis: { ...valueAxis(), scale: true },
      series: [{ type: 'candlestick', itemStyle: { color: '#9e1b32', color0: '#45842a', borderColor: '#9e1b32', borderColor0: '#45842a' }, data: [[42, 48, 40, 51], [48, 46, 44, 52], [46, 54, 45, 57], [54, 50, 49, 58], [50, 61, 48, 64], [61, 58, 55, 66]] }],
    }),
  },
  {
    type: 'effectScatter',
    title: 'Effect Scatter',
    summary: 'Priority points appear before pulse rings.',
    option: () => ({
      ...baseOption('Priority pulses'),
      grid: { top: 56, right: 30, bottom: 42, left: 48 },
      xAxis: { min: 50, max: 100, name: 'Confidence', axisLabel: { formatter: '{value}%' }, splitLine: splitLine() },
      yAxis: { min: 40, max: 100, name: 'Impact', splitLine: splitLine() },
      series: [{ type: 'effectScatter', symbolSize: (value) => value[3] * 0.8, rippleEffect: { brushType: 'stroke', scale: 3.6 }, data: opportunities.slice(0, 5), encode: { x: 1, y: 2, tooltip: [0, 1, 2, 3] } }],
    }),
  },
  {
    type: 'lines',
    title: 'Lines',
    summary: 'Routes draw before endpoints.',
    option: () => ({
      ...baseOption('Route lines on a planning grid'),
      grid: { top: 56, right: 28, bottom: 38, left: 44 },
      xAxis: { min: 0, max: 70, splitLine: splitLine() },
      yAxis: { min: 0, max: 90, splitLine: splitLine() },
      series: [
        { type: 'lines', coordinateSystem: 'cartesian2d', lineStyle: { color: '#007298', curveness: 0.18, opacity: 0.65 }, data: [
          { coords: [[0, 22], [28, 44]], lineStyle: { width: 4 } },
          { coords: [[28, 44], [62, 58]], lineStyle: { width: 6 } },
          { coords: [[8, 15], [18, 78]], lineStyle: { width: 3 } },
        ] },
        { type: 'scatter', symbolSize: 8, itemStyle: { color: '#9e1b32' }, data: [[0, 22], [28, 44], [62, 58], [18, 78], [8, 15]] },
      ],
    }),
  },
  {
    type: 'heatmap',
    title: 'Heatmap',
    summary: 'Cells reveal as a readable grid.',
    option: () => ({
      ...baseOption('Engagement heatmap'),
      grid: { top: 58, right: 28, bottom: 64, left: 52 },
      xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], splitArea: { show: true } },
      yAxis: { type: 'category', data: ['AM', 'Mid', 'PM', 'Late'], splitArea: { show: true } },
      visualMap: { min: 10, max: 70, calculable: true, orient: 'horizontal', left: 'center', bottom: 6, inRange: { color: ['#cdf3ff', '#007298', '#9e1b32'] } },
      series: [{ type: 'heatmap', label: { show: true }, data: heatmapData() }],
    }),
  },
  {
    type: 'pictorialBar',
    title: 'Pictorial Bar',
    summary: 'Repeated symbols accumulate upward.',
    option: () => ({
      ...cartesian('Capacity pictorial bars'),
      xAxis: { ...categoryAxis(), data: products.map((item) => item.name) },
      yAxis: { ...valueAxis(), max: 90 },
      series: [{ type: 'pictorialBar', symbol: 'roundRect', symbolRepeat: true, symbolSize: [18, 8], symbolMargin: 2, itemStyle: { color: '#45842a' }, label: { show: true, position: 'top' }, data: products.map((item) => item.value) }],
    }),
  },
  {
    type: 'themeRiver',
    title: 'Theme River',
    summary: 'Streams settle layer by layer.',
    option: () => ({
      ...baseOption('Demand stream theme river'),
      legend: { top: 28, right: 8, textStyle: legendTextStyle },
      singleAxis: { top: 84, bottom: 36, left: 52, right: 24, type: 'time', axisLabel: axisLabelStyle, axisLine: { lineStyle: { color: brand.gray30 } } },
      series: [{ type: 'themeRiver', label: { show: false }, data: riverData() }],
    }),
  },
  {
    type: 'sunburst',
    title: 'Sunburst',
    summary: 'Hierarchy expands from inner to outer rings.',
    option: () => ({
      ...baseOption('Portfolio sunburst'),
      series: [{ type: 'sunburst', data: portfolio, radius: [0, '78%'], center: ['50%', '54%'], sort: null, label: { rotate: 'radial', color: '#333e48' }, levels: [{}, { r0: '18%', r: '42%' }, { r0: '42%', r: '78%' }] }],
    }),
  },
  {
    type: 'custom',
    title: 'Custom',
    summary: 'RenderItem ranges extend from their start.',
    option: () => ({
      ...baseOption('Custom timeline ranges'),
      grid: { top: 58, right: 28, bottom: 42, left: 78 },
      xAxis: { min: 0, max: 110, axisLabel: { formatter: '{value}%' }, splitLine: splitLine() },
      yAxis: { type: 'category', data: ['Plan', 'Build', 'Launch', 'Learn'] },
      series: [{ type: 'custom', data: [[0, 8, 38], [1, 22, 72], [2, 48, 92], [3, 64, 102]], renderItem: renderRangeItem }],
    }),
  },
]

const extraChartDefinitions = [
  {
    type: 'stacked-area-line',
    profile: 'line',
    title: 'Stacked Area Line',
    summary: 'Multiple area layers draw while axes stay fixed.',
    option: () => ({
      ...cartesian('Stacked pipeline trend'),
      legend: { right: 8, top: 8, textStyle: legendTextStyle },
      xAxis: { ...categoryAxis(), data: months },
      series: [
        { name: 'Product', type: 'line', stack: 'total', smooth: true, areaStyle: { opacity: 0.18 }, data: [18, 22, 24, 29, 34, 38] },
        { name: 'Partners', type: 'line', stack: 'total', smooth: true, areaStyle: { opacity: 0.16 }, data: [12, 15, 18, 20, 24, 27] },
        { name: 'Events', type: 'line', stack: 'total', smooth: true, areaStyle: { opacity: 0.14 }, data: [8, 10, 13, 12, 15, 18] },
      ],
    }),
  },
  {
    type: 'waterfall-bar',
    profile: 'bar',
    title: 'Waterfall Bar',
    summary: 'Transparent offsets preserve the rendered delta geometry.',
    option: () => ({
      ...cartesian('Net revenue bridge'),
      xAxis: { ...categoryAxis(), data: ['Start', 'Product', 'Partners', 'Churn', 'Expansion', 'Net'] },
      yAxis: { ...valueAxis(), max: 110 },
      series: [
        {
          name: 'Offset',
          type: 'bar',
          stack: 'bridge',
          itemStyle: { color: 'transparent' },
          emphasis: { disabled: true },
          data: [0, 36, 62, 78, 66, 0],
        },
        {
          name: 'Delta',
          type: 'bar',
          stack: 'bridge',
          label: { show: true, position: 'top' },
          data: [36, 26, 16, -12, 14, 80],
          itemStyle: { color: (params) => params.value < 0 ? '#9e1b32' : '#45842a', borderRadius: [6, 6, 0, 0] },
        },
      ],
    }),
  },
  {
    type: 'diverging-bar',
    profile: 'bar',
    title: 'Diverging Bar',
    summary: 'Positive and negative bars grow from the same zero line.',
    option: () => ({
      ...baseOption('Segment contribution delta'),
      grid: { top: 58, right: 36, bottom: 42, left: 86 },
      xAxis: { type: 'value', min: -40, max: 60, splitLine: splitLine(), axisLabel: axisLabelStyle },
      yAxis: { type: 'category', data: ['Support', 'Churn', 'Expansion', 'Partner', 'Product'], axisLabel: axisLabelStyle },
      series: [{ type: 'bar', label: { show: true, position: 'right' }, data: [-16, -28, 34, 22, 48], itemStyle: { color: (params) => params.value < 0 ? '#9e1b32' : '#007298', borderRadius: 6 } }],
    }),
  },
  {
    type: 'nested-donut',
    profile: 'pie',
    title: 'Nested Donut',
    summary: 'Inner and outer rings reveal related part-to-whole views.',
    option: () => ({
      ...baseOption('Channel mix by stage'),
      legend: { bottom: 0, left: 'center', textStyle: legendTextStyle },
      series: [
        { type: 'pie', radius: ['26%', '42%'], center: ['50%', '48%'], label: { show: false }, data: channelMix.slice(0, 3) },
        { type: 'pie', radius: ['52%', '72%'], center: ['50%', '48%'], label: { formatter: '{b}' }, data: channelMix },
      ],
    }),
  },
  {
    type: 'bubble-quadrant',
    profile: 'scatter',
    title: 'Bubble Quadrant',
    summary: 'Bubble symbols pop over stable quadrant guides.',
    option: () => ({
      ...baseOption('Opportunity quadrant'),
      grid: { top: 56, right: 30, bottom: 42, left: 48 },
      xAxis: { min: 50, max: 100, name: 'Confidence', axisLabel: { formatter: '{value}%' }, splitLine: splitLine() },
      yAxis: { min: 40, max: 100, name: 'Impact', splitLine: splitLine() },
      visualMap: { show: false, dimension: 3, min: 10, max: 34, inRange: { symbolSize: [12, 40], color: ['#45842a', '#e77204', '#9e1b32'] } },
      series: [
        { type: 'scatter', data: opportunities, encode: { x: 1, y: 2, tooltip: [0, 1, 2, 3] }, markLine: { symbol: 'none', silent: true, lineStyle: { color: brand.gray30, type: 'dashed' }, data: [{ xAxis: 75 }, { yAxis: 70 }] } },
      ],
    }),
  },
  {
    type: 'segmented-gauge',
    profile: 'gauge',
    title: 'Segmented Gauge',
    summary: 'Threshold arcs settle before the center KPI.',
    option: () => ({
      ...baseOption('Reliability threshold'),
      series: [{
        type: 'gauge',
        startAngle: 210,
        endAngle: -30,
        min: 0,
        max: 100,
        progress: { show: true, width: 16 },
        axisLine: { lineStyle: { width: 16, color: [[0.55, '#ffccd5'], [0.8, '#ffe5cc'], [1, '#dbffcc']] } },
        pointer: { width: 5 },
        anchor: { show: true, size: 12 },
        detail: { formatter: '{value}%', fontSize: 30, color: '#333e48' },
        data: [{ value: 86, name: 'Reliability' }],
      }],
    }),
  },
  {
    type: 'hub-graph',
    profile: 'graph',
    title: 'Hub Graph',
    summary: 'Fixed node coordinates keep topology replay deterministic.',
    option: () => ({
      ...baseOption('Hub-and-spoke influence graph'),
      series: [{
        type: 'graph',
        layout: 'none',
        roam: false,
        label: { show: true, color: '#333e48' },
        lineStyle: { color: 'source', curveness: 0.18, opacity: 0.58 },
        data: [
          { name: 'Core', x: 260, y: 145, symbolSize: 58, value: 58 },
          { name: 'Data', x: 120, y: 82, symbolSize: 32, value: 28 },
          { name: 'Sales', x: 400, y: 74, symbolSize: 38, value: 34 },
          { name: 'Success', x: 420, y: 226, symbolSize: 36, value: 32 },
          { name: 'Partners', x: 126, y: 222, symbolSize: 34, value: 30 },
        ],
        links: [
          { source: 'Core', target: 'Data', value: 16 },
          { source: 'Core', target: 'Sales', value: 22 },
          { source: 'Core', target: 'Success', value: 18 },
          { source: 'Core', target: 'Partners', value: 14 },
          { source: 'Sales', target: 'Success', value: 10 },
        ],
      }],
    }),
  },
  {
    type: 'conversion-sankey',
    profile: 'sankey',
    title: 'Conversion Sankey',
    summary: 'More columns test link fading while preserving gradients.',
    option: () => ({
      ...baseOption('Trial conversion flow'),
      series: [{
        type: 'sankey',
        top: 48,
        bottom: 18,
        left: 12,
        right: 52,
        nodeWidth: 18,
        nodeGap: 10,
        data: [
          { name: 'Organic' }, { name: 'Paid' }, { name: 'Partner' },
          { name: 'Trial' }, { name: 'Qualified' }, { name: 'Won' }, { name: 'Nurture' },
        ],
        links: [
          { source: 'Organic', target: 'Trial', value: 36 },
          { source: 'Paid', target: 'Trial', value: 28 },
          { source: 'Partner', target: 'Trial', value: 20 },
          { source: 'Trial', target: 'Qualified', value: 46 },
          { source: 'Trial', target: 'Nurture', value: 24 },
          { source: 'Qualified', target: 'Won', value: 31 },
          { source: 'Qualified', target: 'Nurture', value: 12 },
        ],
        label: { color: '#333e48' },
        lineStyle: { color: 'gradient', curveness: 0.5, opacity: 0.42 },
      }],
    }),
  },
  {
    type: 'calendar-heatmap',
    profile: 'heatmap',
    title: 'Calendar Heatmap',
    summary: 'Date cells fade in while calendar labels stay readable.',
    option: () => ({
      ...baseOption('January activity calendar'),
      visualMap: { min: 12, max: 72, orient: 'horizontal', left: 'center', bottom: 8, inRange: { color: ['#cdf3ff', '#007298', '#9e1b32'] } },
      calendar: { top: 74, left: 44, right: 24, cellSize: ['auto', 24], range: '2026-01', itemStyle: { borderColor: '#ffffff', borderWidth: 2 }, dayLabel: { color: '#696969' }, monthLabel: { color: '#696969' }, yearLabel: { show: false } },
      series: [{ type: 'heatmap', coordinateSystem: 'calendar', data: calendarData() }],
    }),
  },
  {
    type: 'polar-bar',
    profile: 'bar',
    title: 'Polar Bar',
    summary: 'Radial columns grow from the polar baseline.',
    option: () => ({
      ...baseOption('Seasonal polar capacity'),
      polar: { radius: ['18%', '72%'], center: ['50%', '55%'] },
      angleAxis: { type: 'category', data: ['North', 'East', 'South', 'West', 'Central', 'Online'], axisLabel: { ...axisLabelStyle, color: brand.neutral } },
      radiusAxis: { axisLabel: axisLabelStyle, splitLine: splitLine() },
      series: [{ type: 'bar', coordinateSystem: 'polar', roundCap: true, data: [32, 48, 42, 36, 54, 61], itemStyle: { color: '#45842a' }, label: { show: true, position: 'middle', formatter: '{c}' } }],
    }),
  },
  {
    type: 'radar-delta',
    profile: 'radar',
    title: 'Radar Delta',
    summary: 'Three profiles reveal over the same capability frame.',
    option: () => ({
      ...baseOption('Capability delta radar'),
      legend: { bottom: 0, left: 'center', textStyle: legendTextStyle },
      radar: {
        center: ['50%', '48%'],
        radius: '58%',
        indicator: capabilityLabels.map((name) => ({ name, max: 100 })),
        axisName: axisNameStyle,
        splitLine: { lineStyle: { color: '#cfcfcf' } },
        splitArea: { areaStyle: { color: [brand.background, brand.gray10] } },
      },
      series: [{ type: 'radar', areaStyle: { opacity: 0.12 }, data: [
        { name: 'Now', value: [72, 65, 78, 62, 70] },
        { name: 'Next', value: [80, 76, 82, 72, 79] },
        { name: 'Target', value: [88, 82, 84, 80, 86] },
      ] }],
    }),
  },
  {
    type: 'timeline-ranges',
    profile: 'custom',
    title: 'Timeline Ranges',
    summary: 'Custom rendered ranges animate from start to finish.',
    option: () => ({
      ...baseOption('Delivery timeline ranges'),
      grid: { top: 58, right: 28, bottom: 42, left: 82 },
      xAxis: { min: 0, max: 120, axisLabel: { formatter: '{value}%' }, splitLine: splitLine() },
      yAxis: { type: 'category', inverse: true, data: ['Discovery', 'Build', 'Launch', 'Learn'], axisLabel: axisLabelStyle },
      series: [{ type: 'custom', data: [[0, 6, 32], [1, 26, 76], [2, 58, 98], [3, 72, 112]], renderItem: renderRangeItem }],
    }),
  },
  {
    type: 'step-threshold-line',
    profile: 'line',
    title: 'Step Threshold Line',
    summary: 'Step changes and a target line test mixed stroke timing.',
    option: () => ({
      ...cartesian('Threshold attainment steps'),
      legend: { right: 8, top: 8, textStyle: legendTextStyle },
      xAxis: { ...categoryAxis(), data: months },
      yAxis: { ...valueAxis(), max: 100 },
      series: [
        {
          name: 'Committed',
          type: 'line',
          step: 'middle',
          symbolSize: 8,
          data: [28, 40, 52, 64, 72, 86],
          lineStyle: { width: 4, color: brand.blue },
          areaStyle: { color: brand.highlightBlue, opacity: 0.45 },
          markLine: { symbol: 'none', lineStyle: { color: brand.red, type: 'dashed' }, label: { color: brand.red }, data: [{ yAxis: 70, name: 'Target' }] },
        },
        { name: 'Actual', type: 'line', smooth: true, symbolSize: 7, data: [24, 34, 58, 61, 76, 82], lineStyle: { width: 3, color: brand.green } },
      ],
    }),
  },
  {
    type: 'horizontal-stacked-bar',
    profile: 'horizontal-bar',
    title: 'Horizontal Stacked Bar',
    summary: 'Horizontal bars grow from the left while segment labels follow.',
    option: () => ({
      ...baseOption('Segment capacity stack'),
      legend: { right: 8, top: 8, textStyle: legendTextStyle },
      grid: { top: 58, right: 32, bottom: 34, left: 92 },
      xAxis: { type: 'value', max: 100, axisLabel: { formatter: '{value}%' }, splitLine: splitLine() },
      yAxis: { type: 'category', data: ['Starter', 'Growth', 'Scale', 'Enterprise'], axisLabel: axisLabelStyle },
      series: [
        { name: 'Core', type: 'bar', stack: 'total', barWidth: 22, label: { show: true, formatter: '{c}%' }, data: [34, 42, 46, 52] },
        { name: 'Automation', type: 'bar', stack: 'total', barWidth: 22, label: { show: true, formatter: '{c}%' }, data: [22, 26, 28, 24] },
        { name: 'Services', type: 'bar', stack: 'total', barWidth: 22, label: { show: true, formatter: '{c}%' }, data: [18, 16, 14, 12] },
      ],
    }),
  },
  {
    type: 'rose-area-donut',
    profile: 'pie',
    title: 'Rose Area Donut',
    summary: 'Rose segments test radial scaling with uneven arc areas.',
    option: () => ({
      ...baseOption('Campaign response rose'),
      legend: { bottom: 0, left: 'center', textStyle: legendTextStyle },
      series: [{
        type: 'pie',
        roseType: 'area',
        radius: ['18%', '72%'],
        center: ['50%', '48%'],
        label: { formatter: '{b}' },
        data: [
          { name: 'Search', value: 36 },
          { name: 'Partner', value: 24 },
          { name: 'Event', value: 18 },
          { name: 'Outbound', value: 14 },
          { name: 'Referral', value: 10 },
        ],
      }],
    }),
  },
  {
    type: 'matrix-heatmap',
    profile: 'heatmap',
    title: 'Matrix Heatmap',
    summary: 'Dense matrix cells reveal row by row with values intact.',
    option: () => ({
      ...baseOption('Workflow handoff matrix'),
      grid: { top: 58, right: 30, bottom: 48, left: 78 },
      xAxis: { type: 'category', data: ['Plan', 'Design', 'Build', 'QA', 'Ship', 'Learn'], axisLabel: axisLabelStyle, splitArea: { show: true } },
      yAxis: { type: 'category', data: ['Core', 'Data', 'Sales', 'Success', 'Ops'], axisLabel: axisLabelStyle, splitArea: { show: true } },
      visualMap: { min: 8, max: 76, orient: 'horizontal', left: 'center', bottom: 6, inRange: { color: [brand.highlightYellow, brand.orange, brand.red] } },
      series: [{ type: 'heatmap', label: { show: true, color: brand.neutral }, data: matrixHeatmapData() }],
    }),
  },
  {
    type: 'scatter-regression',
    profile: 'scatter',
    title: 'Scatter Regression',
    summary: 'Points fade in first, then the fitted guide line draws across.',
    option: () => ({
      ...baseOption('Confidence to impact regression'),
      grid: { top: 56, right: 30, bottom: 42, left: 48 },
      xAxis: { min: 50, max: 100, name: 'Confidence', axisLabel: { formatter: '{value}%' }, splitLine: splitLine() },
      yAxis: { min: 40, max: 100, name: 'Impact', splitLine: splitLine() },
      series: [
        { type: 'scatter', symbolSize: (value) => value[3] * 0.85, data: opportunities, encode: { x: 1, y: 2, tooltip: [0, 1, 2, 3] } },
        { type: 'line', symbol: 'none', lineStyle: { width: 4, color: brand.purple }, data: [[55, 58], [95, 86]] },
      ],
    }),
  },
  {
    type: 'dual-ring-gauge',
    profile: 'gauge',
    title: 'Dual Ring Gauge',
    summary: 'Concentric KPI rings verify separate arc and value reveals.',
    option: () => ({
      ...baseOption('Operating health rings'),
      series: [
        {
          type: 'gauge',
          radius: '74%',
          startAngle: 210,
          endAngle: -30,
          min: 0,
          max: 100,
          progress: { show: true, width: 14, itemStyle: { color: brand.blue } },
          axisLine: { lineStyle: { width: 14, color: [[1, brand.gray10]] } },
          pointer: { show: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          detail: { formatter: '{value}%', offsetCenter: [0, '-8%'], fontSize: 24, color: brand.neutral },
          data: [{ value: 78, name: 'Health' }],
        },
        {
          type: 'gauge',
          radius: '50%',
          startAngle: 210,
          endAngle: -30,
          min: 0,
          max: 100,
          progress: { show: true, width: 12, itemStyle: { color: brand.green } },
          axisLine: { lineStyle: { width: 12, color: [[1, brand.gray10]] } },
          pointer: { show: false },
          axisTick: { show: false },
          splitLine: { show: false },
          axisLabel: { show: false },
          detail: { formatter: '{value}%', offsetCenter: [0, '34%'], fontSize: 18, color: brand.gray70 },
          data: [{ value: 64, name: 'Coverage' }],
        },
      ],
    }),
  },
  {
    type: 'parallel-scenarios',
    profile: 'parallel',
    title: 'Parallel Scenarios',
    summary: 'More polylines stress parallel-axis draw order and opacity.',
    option: () => ({
      ...baseOption('Scenario profile comparison'),
      parallelAxis: capabilityLabels.map((name, dim) => ({ dim, name })),
      parallel: { left: 56, right: 40, top: 72, bottom: 42, parallelAxisDefault: parallelAxisDefault(45, 100) },
      series: [{ type: 'parallel', lineStyle: { width: 2.5, opacity: 0.36 }, data: [
        [72, 65, 78, 62, 70],
        [84, 72, 76, 80, 74],
        [66, 88, 70, 76, 82],
        [78, 75, 84, 68, 88],
        [91, 80, 82, 74, 79],
        [58, 69, 64, 92, 71],
      ] }],
    }),
  },
  {
    type: 'nested-treemap-drilldown',
    profile: 'treemap',
    title: 'Nested Treemap Drilldown',
    summary: 'Three hierarchy depths exercise parent, leaf, and label timing.',
    option: () => ({
      ...baseOption('Operating model treemap'),
      series: [{
        type: 'treemap',
        roam: false,
        top: 48,
        left: 12,
        right: 12,
        bottom: 12,
        breadcrumb: { show: false },
        label: { show: true },
        upperLabel: { show: true, height: 22, color: brand.neutral },
        levels: [
          { itemStyle: { borderColor: brand.white, borderWidth: 3, gapWidth: 3 } },
          { colorSaturation: [0.35, 0.65] },
          { colorSaturation: [0.45, 0.75] },
        ],
        data: [
          { name: 'Acquire', value: 42, children: [{ name: 'Search', value: 18 }, { name: 'Partner', value: 14 }, { name: 'Events', value: 10 }] },
          { name: 'Convert', value: 48, children: [{ name: 'Trial', value: 18 }, { name: 'Sales', value: 20 }, { name: 'Lifecycle', value: 10 }] },
          { name: 'Retain', value: 36, children: [{ name: 'Success', value: 16 }, { name: 'Education', value: 9 }, { name: 'Support', value: 11 }] },
        ],
      }],
    }),
  },
]

function polygon(name, coordinates) {
  return { type: 'Feature', properties: { name }, geometry: { type: 'Polygon', coordinates } }
}

function baseOption(title) {
  return {
    backgroundColor: 'transparent',
    color: colors,
    animation: false,
    textStyle: { fontFamily: fontPrimary, color: brand.neutral },
    tooltip: {},
    title: { text: title, left: 12, top: 6, textStyle: { color: brand.neutral, fontSize: 14, fontWeight: 700 } },
  }
}

function categoryAxis() {
  return { type: 'category', axisTick: { show: false }, axisLine: { lineStyle: { color: brand.gray30 } }, axisLabel: axisLabelStyle, nameTextStyle: axisNameStyle }
}

function valueAxis() {
  return { type: 'value', splitLine: splitLine(), axisLine: { lineStyle: { color: brand.gray30 } }, axisLabel: axisLabelStyle, nameTextStyle: axisNameStyle }
}

function splitLine() {
  return { lineStyle: { color: brand.gray10 } }
}

function cartesian(title) {
  return {
    ...baseOption(title),
    tooltip: { trigger: 'axis' },
    grid: { top: 58, right: 32, bottom: 42, left: 48 },
    xAxis: categoryAxis(),
    yAxis: valueAxis(),
  }
}

function readableTextForColor(color) {
  return [brand.yellow, brand.highlightRed, brand.highlightOrange, brand.highlightYellow, brand.highlightGreen, brand.highlightBlue, brand.highlightPurple, brand.gray10, brand.gray20].includes(color)
    ? darkCellText
    : lightCellText
}

function heatmapLabelColor(value, threshold = 46) {
  const score = Array.isArray(value) ? value[2] : value
  return score >= threshold ? lightCellText : darkCellText
}

function heatmapLabel() {
  return {
    show: true,
    fontSize: 9,
    fontWeight: 800,
  }
}

function heatmapCells(values, threshold = 46) {
  return values.map(([x, y, value]) => ({
    value: [x, y, value],
    label: {
      ...heatmapLabel(),
      formatter: String(value),
      color: heatmapLabelColor(value, threshold),
    },
  }))
}

function labelBackplate(overrides = {}) {
  return {
    color: brand.neutral,
    backgroundColor: 'rgba(255,255,255,0.9)',
    borderColor: brand.gray20,
    borderWidth: 1,
    borderRadius: 3,
    padding: [2, 4],
    fontSize: 10,
    fontWeight: 700,
    textBorderColor: brand.white,
    textBorderWidth: 2,
    ...overrides,
  }
}

function pieLabel() {
  return {
    color: brand.neutral,
    fontSize: 10,
    lineHeight: 12,
  }
}

function pieLabelLine() {
  return {
    lineStyle: { color: brand.gray60, width: 1.4 },
  }
}

function colorNodes(items, labelStyle) {
  return items.map((node) => ({
    ...node,
    itemStyle: { color: nodeColors[node.name] || brand.blue },
    label: labelStyle || { color: readableTextForColor(nodeColors[node.name] || brand.blue), fontWeight: 700 },
  }))
}

function colorLinks(items) {
  return items.map((link) => ({
    ...link,
    lineStyle: { color: brand.gray30, opacity: 0.72, width: Math.max(1.4, link.value / 7) },
  }))
}

function parallelAxisDefault(min = 50, max = 100) {
  return {
    type: 'value',
    min,
    max,
    nameTextStyle: axisNameStyle,
    axisLabel: { ...axisLabelStyle, color: brand.gray70 },
    axisLine: { lineStyle: { color: brand.gray50 } },
    splitLine: { lineStyle: { color: brand.gray10 } },
  }
}

function parallelRows(rows, palette = lineSeriesPalette) {
  return rows.map((value, index) => ({
    value,
    lineStyle: { color: palette[index % palette.length], width: 2.7, opacity: 0.74 },
  }))
}

function treemapLeaf(name, value) {
  const color = treemapColors[name] || brand.blue
  return {
    name,
    value,
    itemStyle: { color, borderColor: brand.gray10, borderWidth: 2 },
    label: { color: readableTextForColor(color), fontWeight: 700 },
  }
}

function treemapGroup(name, children) {
  const color = treemapColors[name] || brand.blue
  return {
    name,
    value: children.reduce((sum, child) => sum + child.value, 0),
    itemStyle: { color, borderColor: brand.gray20, borderWidth: 2 },
    label: { color: readableTextForColor(color), fontWeight: 800 },
    children,
  }
}

function heatmapData() {
  const values = []
  for (let x = 0; x < 5; x += 1) {
    for (let y = 0; y < 4; y += 1)
      values.push([x, y, 12 + x * 8 + y * 6 + ((x + y) % 2) * 8])
  }
  return values
}

function matrixHeatmapData() {
  const values = []
  for (let x = 0; x < 6; x += 1) {
    for (let y = 0; y < 5; y += 1)
      values.push([x, y, 8 + x * 7 + y * 5 + ((x * y) % 3) * 6])
  }
  return values
}

function sunburstData() {
  return [
    treemapGroup('Acquire', [treemapLeaf('Search', 18), treemapLeaf('Partner', 18)]),
    treemapGroup('Convert', [treemapLeaf('Trial', 22), treemapLeaf('Sales', 20)]),
    treemapGroup('Retain', [treemapLeaf('Success', 18), treemapLeaf('Education', 12)]),
  ]
}

function nestedTreemapData() {
  return [
    {
      ...treemapGroup('Acquire', [
        { name: 'Search', value: 18, itemStyle: { color: brand.highlightOrange }, label: { color: darkCellText, fontWeight: 700 } },
        { name: 'Partner', value: 14, itemStyle: { color: brand.highlightYellow }, label: { color: darkCellText, fontWeight: 700 } },
        { name: 'Events', value: 10, itemStyle: { color: brand.highlightPurple }, label: { color: darkCellText, fontWeight: 700 } },
      ]),
      itemStyle: { color: brand.orange, borderColor: brand.gray20, borderWidth: 2 },
    },
    {
      ...treemapGroup('Convert', [
        { name: 'Trial', value: 18, itemStyle: { color: brand.highlightRed }, label: { color: darkCellText, fontWeight: 700 } },
        { name: 'Sales', value: 20, itemStyle: { color: brand.highlightOrange }, label: { color: darkCellText, fontWeight: 700 } },
        { name: 'Lifecycle', value: 10, itemStyle: { color: brand.highlightBlue }, label: { color: darkCellText, fontWeight: 700 } },
      ]),
      itemStyle: { color: brand.red, borderColor: brand.gray20, borderWidth: 2 },
    },
    {
      ...treemapGroup('Retain', [
        { name: 'Success', value: 16, itemStyle: { color: brand.highlightGreen }, label: { color: darkCellText, fontWeight: 700 } },
        { name: 'Education', value: 9, itemStyle: { color: brand.highlightBlue }, label: { color: darkCellText, fontWeight: 700 } },
        { name: 'Support', value: 11, itemStyle: { color: brand.highlightPurple }, label: { color: darkCellText, fontWeight: 700 } },
      ]),
      itemStyle: { color: brand.yellow, borderColor: brand.gray20, borderWidth: 2 },
      label: { color: darkCellText, fontWeight: 800 },
    },
  ]
}

function flowNodes(names) {
  const palette = [brand.orange, brand.purple, brand.blue, brand.yellow, brand.green, brand.red, brand.orange]
  return names.map((name, index) => ({
    name,
    itemStyle: { color: palette[index % palette.length] },
    label: labelBackplate(),
  }))
}

function highlightedLinks(items) {
  return items.map((link, index) => ({
    ...link,
    lineStyle: { color: highlights[index % highlights.length], opacity: 0.62 },
  }))
}

function riverData() {
  const names = ['Product', 'Partners', 'Search']
  const dates = ['2026/01/01', '2026/02/01', '2026/03/01', '2026/04/01', '2026/05/01', '2026/06/01']
  return names.flatMap((name, nameIndex) => dates.map((date, dateIndex) => [date, 18 + nameIndex * 8 + dateIndex * (nameIndex + 2), name]))
}

function calendarData() {
  const values = []
  for (let day = 1; day <= 31; day += 1) {
    const date = `2026-01-${String(day).padStart(2, '0')}`
    values.push([date, 14 + (day % 7) * 7 + Math.floor(day / 5) * 4])
  }
  return values
}

function renderRangeItem(params, api) {
  const categoryIndex = api.value(0)
  const start = api.coord([api.value(1), categoryIndex])
  const end = api.coord([api.value(2), categoryIndex])
  const size = api.size([0, 1])
  const barHeight = size[1] * 0.56
  return {
    type: 'rect',
    shape: { x: start[0], y: start[1] - barHeight / 2, width: Math.max(2, end[0] - start[0]), height: barHeight, r: 6 },
    style: { fill: phasePalette[categoryIndex % phasePalette.length] },
  }
}

function asArray(value) {
  if (!value)
    return []
  return Array.isArray(value) ? value : [value]
}

function polishAxis(axis) {
  axis.axisLabel = { ...axisLabelStyle, ...(axis.axisLabel || {}) }
  axis.nameTextStyle = { ...axisNameStyle, ...(axis.nameTextStyle || {}) }
  axis.axisLine = { ...(axis.axisLine || {}), lineStyle: { color: brand.gray30, ...((axis.axisLine || {}).lineStyle || {}) } }
  axis.splitLine = { ...(axis.splitLine || {}), lineStyle: { color: brand.gray10, ...((axis.splitLine || {}).lineStyle || {}) } }
  if (axis.name) {
    axis.nameLocation = axis.nameLocation || 'middle'
    axis.nameGap = axis.nameGap || 26
  }
}

function polishOption(definition, option) {
  option.color = colors
  option.textStyle = { fontFamily: fontPrimary, color: brand.neutral, ...(option.textStyle || {}) }
  asArray(option.legend).forEach((legend) => {
    legend.textStyle = { ...legendTextStyle, ...(legend.textStyle || {}) }
  })
  asArray(option.xAxis).forEach(polishAxis)
  asArray(option.yAxis).forEach(polishAxis)
  asArray(option.parallelAxis).forEach(polishAxis)
  asArray(option.visualMap).forEach((visualMap) => {
    visualMap.textStyle = { ...legendTextStyle, ...(visualMap.textStyle || {}) }
  })

  const series = asArray(option.series)
  series.forEach((item) => {
    if (item.label?.show)
      item.label = { color: brand.neutral, fontWeight: 700, fontSize: 10, ...item.label }
    if (item.type === 'pie') {
      item.label = { ...pieLabel(), ...(item.label || {}) }
      item.labelLine = { ...pieLabelLine(), ...(item.labelLine || {}) }
      item.itemStyle = { borderColor: brand.gray10, borderWidth: 2, ...(item.itemStyle || {}) }
    }
  })

  switch (definition.type) {
    case 'line':
      series[0].lineStyle = { ...(series[0].lineStyle || {}), color: brand.blue, width: 2.6 }
      series[0].itemStyle = { color: brand.blue }
      series[1].lineStyle = { ...(series[1].lineStyle || {}), color: brand.red, width: 4 }
      series[1].itemStyle = { color: brand.red, borderColor: brand.gray10, borderWidth: 2 }
      series[1].areaStyle = { color: brand.highlightRed, opacity: 0.36 }
      break
    case 'bar':
      series[0].itemStyle = { color: brand.blue, borderRadius: [6, 6, 0, 0], ...(series[0].itemStyle || {}) }
      series[0].label = { show: true, position: 'top', color: darkCellText, fontWeight: 800 }
      break
    case 'scatter':
      series[0].itemStyle = { opacity: 0.92, borderColor: brand.gray10, borderWidth: 1.5 }
      option.xAxis.nameTextStyle = axisNameStyle
      option.yAxis.nameTextStyle = axisNameStyle
      break
    case 'radar':
      option.legend.textStyle = legendTextStyle
      option.radar.axisName = axisNameStyle
      option.radar.splitLine = { lineStyle: { color: brand.gray30 } }
      series[0].data = [
        { name: 'Current', value: [72, 65, 78, 62, 70], lineStyle: { color: brand.red, width: 3 }, itemStyle: { color: brand.red }, areaStyle: { color: brand.highlightRed, opacity: 0.44 } },
        { name: 'Target', value: [88, 82, 84, 80, 86], lineStyle: { color: brand.blue, width: 3 }, itemStyle: { color: brand.blue }, areaStyle: { color: brand.highlightBlue, opacity: 0.3 } },
      ]
      break
    case 'map':
      series[0].top = 50
      series[0].bottom = 28
      option.visualMap.show = false
      option.visualMap.orient = 'horizontal'
      option.visualMap.left = 30
      option.visualMap.bottom = 12
      option.visualMap.itemWidth = 88
      option.visualMap.itemHeight = 10
      option.visualMap.textGap = 8
      option.visualMap.inRange = { color: [brand.highlightBlue, brand.blue, brand.purple] }
      option.visualMap.textStyle = labelBackplate({ backgroundColor: 'rgba(255,255,255,0.82)', borderWidth: 0, padding: [1, 3] })
      series[0].label = { show: true, color: brand.white, fontWeight: 800, fontSize: 10, textBorderColor: brand.gray90, textBorderWidth: 2.4 }
      series[0].emphasis = { label: { show: true, color: brand.white, fontWeight: 800, textBorderColor: brand.gray90, textBorderWidth: 2.4 }, itemStyle: { areaColor: brand.red } }
      series[0].itemStyle = { borderColor: brand.gray20, borderWidth: 2 }
      break
    case 'tree':
      series[0].itemStyle = { color: brand.green, borderColor: brand.highlightGreen, borderWidth: 2 }
      series[0].lineStyle = { color: brand.gray50, width: 2 }
      series[0].label = { color: brand.neutral, fontWeight: 700, position: 'left', align: 'right' }
      series[0].leaves = { label: { color: brand.neutral, fontWeight: 700, position: 'right', align: 'left' } }
      break
    case 'treemap':
      series[0].data = sunburstData()
      series[0].label = { show: true, color: brand.neutral, fontWeight: 700 }
      series[0].upperLabel = { show: true, height: 24, color: brand.neutral, fontWeight: 800 }
      series[0].levels = [{ itemStyle: { borderColor: brand.gray10, borderWidth: 2, gapWidth: 3 } }]
      break
    case 'graph':
      series[0].data = colorNodes(nodes.map((node) => ({ ...node, symbolSize: 22 + node.value * 0.45 })), labelBackplate())
      series[0].links = colorLinks(links)
      series[0].label = { show: true, ...labelBackplate(), position: 'right', distance: 6 }
      series[0].lineStyle = { color: brand.gray30, curveness: 0.22, opacity: 0.5, width: 1.4 }
      break
    case 'chord':
      series[0].label = { color: brand.neutral, fontWeight: 700, fontSize: 10 }
      series[0].lineStyle = { opacity: 0.42, color: 'source' }
      break
    case 'gauge':
      series[0].progress = { show: true, width: 18, itemStyle: { color: brand.green } }
      series[0].axisLine = { lineStyle: { width: 18, color: [[0.55, brand.red], [0.72, brand.orange], [0.86, brand.yellow], [1, brand.green]] } }
      series[0].pointer = { width: 4, length: '54%', itemStyle: { color: brand.red } }
      series[0].splitLine = { length: 10, lineStyle: { color: brand.gray60, width: 2 } }
      series[0].axisTick = { distance: -18, length: 5, lineStyle: { color: brand.gray50, width: 1.2 } }
      series[0].detail = { ...series[0].detail, offsetCenter: [0, '28%'], color: brand.gray90, fontWeight: 800 }
      series[0].title = { offsetCenter: [0, '47%'], color: brand.gray70, fontSize: 12, fontWeight: 700 }
      series[0].axisLabel = { ...series[0].axisLabel, color: brand.gray70, distance: 18, fontSize: 10 }
      break
    case 'funnel': {
      const stage = [brand.red, brand.orange, brand.yellow, brand.green]
      series[0].gap = 6
      series[0].label = { show: true, position: 'inside', formatter: '{b}: {c}', fontWeight: 800, fontSize: 11 }
      series[0].data = series[0].data.map((item, index) => ({
        ...item,
        itemStyle: { color: stage[index] },
        label: { color: readableTextForColor(stage[index]) },
      }))
      break
    }
    case 'parallel':
      series[0].data = parallelRows(series[0].data)
      series[0].lineStyle = { width: 2.7, opacity: 0.74 }
      break
    case 'sankey':
      series[0].data = colorNodes(nodes, labelBackplate())
      series[0].links = highlightedLinks(links)
      series[0].label = { ...labelBackplate(), position: 'right' }
      series[0].lineStyle = { color: 'gradient', curveness: 0.48, opacity: 0.42 }
      break
    case 'boxplot':
      series[0].itemStyle = { color: brand.highlightBlue, borderColor: brand.blue, borderWidth: 2.2 }
      option.series.push({ type: 'scatter', symbolSize: 7, itemStyle: { color: brand.orange }, data: [[0, 38], [3, 60]] })
      option.yAxis.name = 'Cycle time, days'
      break
    case 'candlestick':
      series[0].itemStyle = { color: brand.green, color0: brand.red, borderColor: brand.green, borderColor0: brand.red }
      option.yAxis.name = 'Index value'
      break
    case 'effectScatter':
      series[0].symbolSize = (value) => 10 + value[3] * 0.62
      series[0].itemStyle = { color: brand.red, borderColor: brand.highlightRed, borderWidth: 3 }
      series[0].rippleEffect = { brushType: 'stroke', scale: 3.5, color: brand.highlightRed }
      break
    case 'lines':
      series[0].lineStyle = { color: brand.blue, curveness: 0.18, opacity: 0.76 }
      series[1].symbolSize = 10
      series[1].itemStyle = { color: brand.red, borderColor: brand.highlightRed, borderWidth: 3 }
      break
    case 'heatmap':
      option.grid.bottom = 72
      option.visualMap.show = false
      option.visualMap.dimension = 2
      option.visualMap.inRange = { color: [brand.highlightBlue, brand.blue, brand.red] }
      series[0].label = heatmapLabel()
      series[0].data = heatmapCells(heatmapData(), 42)
      series[0].itemStyle = { borderColor: brand.gray20, borderWidth: 1 }
      break
    case 'pictorialBar':
      series[0].itemStyle = { color: brand.green, borderColor: brand.gray10, borderWidth: 0.6 }
      series[0].label = { show: true, position: 'top', color: brand.neutral, fontWeight: 800 }
      break
    case 'themeRiver':
      option.color = [brand.red, brand.orange, brand.yellow]
      series[0].itemStyle = { borderColor: brand.gray10, borderWidth: 1 }
      break
    case 'sunburst':
      series[0].data = sunburstData()
      series[0].label = { rotate: 'radial', fontSize: 10, color: brand.neutral }
      series[0].itemStyle = { borderColor: brand.gray10, borderWidth: 2 }
      break
    case 'custom':
      option.yAxis.inverse = true
      option.yAxis.axisLabel = axisLabelStyle
      break
    case 'stacked-area-line':
      series.forEach((item, index) => {
        const lineColors = [brand.red, brand.orange, brand.blue]
        const fillColors = [brand.highlightRed, brand.highlightOrange, brand.highlightBlue]
        item.lineStyle = { color: lineColors[index], width: 2.8 }
        item.itemStyle = { color: lineColors[index], borderColor: brand.gray10, borderWidth: 1.5 }
        item.areaStyle = { color: fillColors[index], opacity: 0.44 - index * 0.06 }
      })
      break
    case 'waterfall-bar':
      series[1].label = { show: true, position: 'top', color: brand.gray90, fontWeight: 800, distance: 8 }
      break
    case 'diverging-bar':
      series[0].label = { show: true, position: 'right', color: brand.gray90, fontWeight: 800, distance: 8 }
      series[0].markLine = { symbol: 'none', silent: true, lineStyle: { color: brand.gray70, width: 2 }, data: [{ xAxis: 0 }] }
      break
    case 'nested-donut':
      series.forEach((item) => {
        item.itemStyle = { borderColor: brand.gray10, borderWidth: 2 }
        item.label = item.label?.show === false ? item.label : { ...pieLabel(), ...(item.label || {}) }
        item.labelLine = pieLabelLine()
      })
      break
    case 'bubble-quadrant':
      option.visualMap.inRange = { symbolSize: [14, 40], color: [brand.blue, brand.green, brand.yellow, brand.orange, brand.red] }
      series[0].markLine.lineStyle = { color: brand.gray50, type: 'dashed', width: 1.4 }
      break
    case 'segmented-gauge':
      series[0].progress = { show: true, width: 16, itemStyle: { color: brand.green } }
      series[0].axisLine = { lineStyle: { width: 16, color: [[0.55, brand.red], [0.8, brand.orange], [0.92, brand.yellow], [1, brand.green]] } }
      series[0].pointer = { width: 4, length: '54%', itemStyle: { color: brand.red } }
      series[0].splitLine = { length: 9, lineStyle: { color: brand.gray60, width: 2 } }
      series[0].axisTick = { distance: -16, length: 5, lineStyle: { color: brand.gray50, width: 1.1 } }
      series[0].axisLabel = { color: brand.gray70, distance: 16, fontSize: 10 }
      series[0].detail = { formatter: '{value}%', offsetCenter: [0, '30%'], fontSize: 30, color: brand.gray90, fontWeight: 800 }
      series[0].title = { offsetCenter: [0, '50%'], color: brand.gray70, fontSize: 12, fontWeight: 700 }
      break
    case 'hub-graph': {
      option.title.show = false
      const hubNodes = [
        { name: 'Core', x: 260, y: 156, symbolSize: 58, value: 58 },
        { name: 'Data', x: 52, y: 72, symbolSize: 34, value: 28 },
        { name: 'Sales', x: 468, y: 72, symbolSize: 38, value: 34 },
        { name: 'Success', x: 461, y: 258, symbolSize: 38, value: 32 },
        { name: 'Partners', x: 59, y: 258, symbolSize: 36, value: 30 },
      ]
      delete series[0].top
      delete series[0].bottom
      series[0].data = hubNodes.map((node) => ({
        ...node,
        itemStyle: { color: nodeColors[node.name] || brand.blue },
        label: labelBackplate(),
      }))
      series[0].links = colorLinks(series[0].links)
      series[0].label = { show: true, ...labelBackplate(), position: 'right', distance: 6 }
      series[0].lineStyle = { color: brand.gray30, curveness: 0, opacity: 0.52, width: 1.5 }
      break
    }
    case 'conversion-sankey':
      series[0].nodeGap = 14
      series[0].data = flowNodes(['Organic', 'Paid', 'Partner', 'Trial', 'Qualified', 'Won', 'Nurture'])
      series[0].links = highlightedLinks(series[0].links)
      series[0].label = { ...labelBackplate(), position: 'right' }
      series[0].lineStyle = { color: 'gradient', curveness: 0.5, opacity: 0.38 }
      break
    case 'calendar-heatmap':
      option.visualMap.inRange = { color: [brand.gray10, brand.highlightBlue, brand.blue, brand.purple, brand.red] }
      option.calendar.itemStyle = { borderColor: brand.gray10, borderWidth: 1 }
      option.calendar.dayLabel = { color: brand.neutral, fontWeight: 700 }
      option.calendar.monthLabel = { color: brand.neutral, fontWeight: 700 }
      break
    case 'polar-bar':
      option.polar.center = ['50%', '56%']
      series[0].itemStyle = { color: (params) => colors[params.dataIndex % colors.length] }
      series[0].label = { show: false }
      option.angleAxis.axisLabel = { ...axisLabelStyle, color: brand.neutral, fontSize: 9, margin: 10 }
      option.radiusAxis.axisLabel = { show: false }
      option.radiusAxis.splitLine = { lineStyle: { color: brand.gray10 } }
      break
    case 'radar-delta':
      option.legend.textStyle = legendTextStyle
      option.radar.axisName = axisNameStyle
      option.radar.splitLine = { lineStyle: { color: brand.gray30 } }
      series[0].data = [
        { name: 'Now', value: [72, 65, 78, 62, 70], lineStyle: { color: brand.red, width: 2.6 }, itemStyle: { color: brand.red }, areaStyle: { color: brand.highlightRed, opacity: 0.36 } },
        { name: 'Next', value: [80, 76, 82, 72, 79], lineStyle: { color: brand.orange, width: 2.6 }, itemStyle: { color: brand.orange }, areaStyle: { color: brand.highlightOrange, opacity: 0.28 } },
        { name: 'Target', value: [88, 82, 84, 80, 86], lineStyle: { color: brand.yellow, width: 3 }, itemStyle: { color: brand.yellow }, areaStyle: { opacity: 0.08 } },
      ]
      break
    case 'timeline-ranges':
      option.yAxis.inverse = true
      option.yAxis.axisLabel = axisLabelStyle
      break
    case 'step-threshold-line':
      series[0].lineStyle = { width: 4, color: brand.blue }
      series[0].itemStyle = { color: brand.blue, borderColor: brand.gray10, borderWidth: 1.5 }
      series[0].areaStyle = { color: brand.highlightBlue, opacity: 0.32 }
      series[0].markLine.lineStyle = { color: brand.red, type: 'dashed', width: 2 }
      series[1].lineStyle = { width: 3.2, color: brand.orange }
      series[1].itemStyle = { color: brand.orange, borderColor: brand.gray10, borderWidth: 1.5 }
      break
    case 'horizontal-stacked-bar': {
      const stackColors = [brand.red, brand.orange, brand.yellow]
      series.forEach((item, index) => {
        item.itemStyle = { color: stackColors[index], borderColor: brand.gray10, borderWidth: 1 }
        item.label = { show: true, formatter: '{c}%', color: readableTextForColor(stackColors[index]), fontWeight: 800, fontSize: 10 }
      })
      break
    }
    case 'rose-area-donut':
      series[0].itemStyle = { borderColor: brand.gray10, borderWidth: 2 }
      series[0].label = pieLabel()
      series[0].labelLine = pieLabelLine()
      break
    case 'matrix-heatmap':
      option.grid.bottom = 60
      option.visualMap.show = false
      option.visualMap.dimension = 2
      option.visualMap.inRange = { color: [brand.highlightYellow, brand.yellow, brand.orange, brand.red, brand.purple] }
      series[0].label = heatmapLabel()
      series[0].data = heatmapCells(matrixHeatmapData(), 50)
      series[0].itemStyle = { borderColor: brand.gray20, borderWidth: 1 }
      break
    case 'scatter-regression':
      series[0].itemStyle = { color: brand.red, borderColor: brand.gray10, borderWidth: 1.8, opacity: 0.88 }
      series[1].lineStyle = { width: 4, color: brand.purple }
      option.grid.right = 42
      break
    case 'dual-ring-gauge':
      series[0].progress.itemStyle = { color: brand.green }
      series[0].axisLine.lineStyle.color = [[1, brand.gray20]]
      series[0].detail = { ...series[0].detail, offsetCenter: [0, '-13%'], fontSize: 24, color: brand.gray90, fontWeight: 800 }
      series[0].title = { show: true, offsetCenter: [0, '9%'], color: brand.gray70, fontSize: 12, fontWeight: 700 }
      series[1].progress.itemStyle = { color: brand.orange }
      series[1].axisLine.lineStyle.color = [[1, brand.gray20]]
      series[1].detail = { ...series[1].detail, offsetCenter: [0, '36%'], fontSize: 18, color: brand.neutral, fontWeight: 800 }
      series[1].title = { show: true, offsetCenter: [0, '53%'], color: brand.gray70, fontSize: 11, fontWeight: 700 }
      break
    case 'parallel-scenarios':
      series[0].data = parallelRows(series[0].data)
      series[0].lineStyle = { width: 2.5, opacity: 0.7 }
      break
    case 'nested-treemap-drilldown':
      series[0].data = nestedTreemapData()
      series[0].label = { show: true, color: darkCellText, fontWeight: 700 }
      series[0].upperLabel = { show: true, height: 24, color: brand.neutral, fontWeight: 800 }
      series[0].levels = [
        { itemStyle: { borderColor: brand.gray20, borderWidth: 2, gapWidth: 3 } },
        { itemStyle: { borderColor: brand.gray10, borderWidth: 2, gapWidth: 2 } },
        { itemStyle: { borderColor: brand.gray10, borderWidth: 1, gapWidth: 1 } },
      ]
      break
  }

  return option
}

function renderSvg(definition) {
  const chart = echarts.init(null, null, { renderer: 'svg', ssr: true, width, height })
  chart.setOption(polishOption(definition, definition.option()))
  const svg = chart.renderToSVGString()
  chart.dispose()
  return decorateSvg(svg, definition.profile || definition.type)
}

function decorateSvg(svg, chartType) {
  const chartSlug = slug(chartType)
  let order = 0
  let decorated = svg.replace(
    /<(path|rect|circle|ellipse|line|polyline|polygon|text)\b([^>]*)>/g,
    (match, tag, attrs) => {
      const role = roleFor(chartType, tag, attrs)
      const delay = Math.min(order * 34, 1150)
      let nextAttrs = appendAttr(attrs, 'class', `easv-mark easv-${role}`)
      nextAttrs = appendStyle(nextAttrs, `--easv-delay:${delay}ms`)
      nextAttrs = appendAttr(nextAttrs, 'data-easv-order', String(order))
      if (role === 'draw' && ['path', 'line', 'polyline', 'polygon'].includes(tag) && !/\spathLength=/.test(nextAttrs))
        nextAttrs += ' pathLength="1"'
      order += 1
      return `<${tag}${nextAttrs}>`
    },
  )

  decorated = decorated.replace('<svg ', `<svg class="easv-svg easv-profile-${chartSlug}" data-echarts-chart-type="${escapeHtml(chartType)}" `)
  return decorated
}

function roleFor(chartType, tag, attrs) {
  if (tag === 'text')
    return 'label'
  const hasTransform = /\stransform=/.test(attrs)
  const hasStroke = /\sstroke="(?!none)/.test(attrs)
  const pathlike = ['path', 'line', 'polyline', 'polygon'].includes(tag)
  if (chartType === 'horizontal-bar')
    return pathlike || tag === 'rect' ? 'scale-x' : 'fade'
  if (hasTransform)
    return 'fade'
  if (['line', 'lines', 'parallel', 'tree'].includes(chartType) && pathlike && hasStroke)
    return 'draw'
  if (chartType === 'radar' && pathlike && hasStroke)
    return 'draw'
  if (['scatter', 'effectScatter', 'graph'].includes(chartType))
    return pathlike && hasStroke ? 'draw' : 'fade'
  if (['bar', 'boxplot', 'candlestick', 'custom', 'funnel', 'heatmap', 'pictorialBar', 'treemap'].includes(chartType))
    return 'scale-y'
  return 'fade'
}

function appendAttr(attrs, name, value) {
  const pattern = new RegExp(`\\s${name}="([^"]*)"`)
  const match = attrs.match(pattern)
  if (!match)
    return `${attrs} ${name}="${escapeHtml(value)}"`
  if (name === 'class') {
    const classes = new Set(match[1].split(/\s+/).filter(Boolean))
    value.split(/\s+/).filter(Boolean).forEach((className) => classes.add(className))
    return attrs.replace(pattern, ` ${name}="${[...classes].join(' ')}"`)
  }
  return attrs
}

function appendStyle(attrs, declaration) {
  const match = attrs.match(/\sstyle="([^"]*)"/)
  if (!match)
    return `${attrs} style="${declaration}"`
  const separator = match[1].trim().endsWith(';') ? '' : ';'
  return attrs.replace(/\sstyle="([^"]*)"/, ` style="${match[1]}${separator}${declaration}"`)
}

function slug(value) {
  return value.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`).replace(/^-/, '').replace(/[^a-z0-9-]+/g, '-')
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('"', '&quot;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
}

function pageCss() {
  return `
:root {
  color-scheme: light;
  --font-primary: ${fontPrimary};
  --font-icons: ${iconFont};
  --brand-primary: ${brand.primary};
  --brand-neutral: ${brand.neutral};
  --brand-red: ${brand.red};
  --brand-orange: ${brand.orange};
  --brand-yellow: ${brand.yellow};
  --brand-green: ${brand.green};
  --brand-blue: ${brand.blue};
  --brand-purple: ${brand.purple};
  --brand-gray-10: ${brand.gray10};
  --brand-gray-20: ${brand.gray20};
  --brand-gray-30: ${brand.gray30};
  --brand-gray-40: ${brand.gray40};
  --brand-gray-50: ${brand.gray50};
  --brand-gray-60: ${brand.gray60};
  --brand-gray-70: ${brand.gray70};
  --brand-gray-80: ${brand.gray80};
  --brand-gray-90: ${brand.gray90};
  --brand-background: ${brand.background};
  --brand-link: ${brand.link};
  --brand-link-hover: ${brand.linkHover};
  --brand-focus: ${brand.gray20};
  --brand-highlight-blue: ${brand.highlightBlue};
  font-family: var(--font-primary);
  background: var(--brand-background);
  color: var(--brand-neutral);
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--brand-background); }
.page-shell { max-width: 1480px; margin: 0 auto; padding: 28px; }
.topbar {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 22px;
}
h1 { margin: 0 0 6px; font-size: 32px; line-height: 1.1; letter-spacing: 0; }
.lede { margin: 0; color: var(--brand-gray-70); max-width: 760px; line-height: 1.45; }
.actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
button {
  border: 1px solid var(--brand-gray-20);
  background: #fff;
  color: var(--brand-neutral);
  border-radius: 8px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 9px 12px;
  font: inherit;
  font-weight: 650;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(51, 62, 72, .08);
}
button:hover { border-color: var(--brand-link); background: var(--brand-highlight-blue); color: var(--brand-link-hover); }
button:focus-visible { outline: 3px solid var(--brand-focus); outline-offset: 2px; }
.material-symbols-rounded {
  font-family: var(--font-icons);
  font-size: 18px;
  font-variation-settings: "FILL" 0, "wght" 700, "GRAD" 0, "opsz" 20;
  line-height: 1;
}
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 16px;
}
.chart-card {
  background: #fff;
  border: 1px solid var(--brand-gray-20);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 26px rgba(51, 62, 72, .07);
}
.card-header {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  align-items: start;
  padding: 14px 14px 10px;
  border-bottom: 1px solid var(--brand-gray-10);
}
.card-header h2 { margin: 0 0 4px; font-size: 17px; line-height: 1.2; letter-spacing: 0; }
.card-header p { margin: 0; color: var(--brand-gray-60); line-height: 1.35; font-size: 13px; }
.chart-stage { padding: 8px 10px 12px; background: #ffffff; }
.chart-stage svg { display: block; width: 100%; height: auto; overflow: visible; }
.easv-svg .easv-mark {
  transform-box: fill-box;
  transform-origin: center;
}
.chart-card.is-playing .easv-fade,
.chart-card.is-playing .easv-label {
  opacity: 0;
  animation: easv-fade 760ms cubic-bezier(.22, 1, .36, 1) forwards;
  animation-delay: var(--easv-delay, 0ms);
}
.chart-card.is-playing .easv-scale-y {
  opacity: 0;
  transform: scaleY(.04);
  transform-origin: center bottom;
  animation: easv-scale-y 820ms cubic-bezier(.22, 1, .36, 1) forwards;
  animation-delay: var(--easv-delay, 0ms);
}
.chart-card.is-playing .easv-scale-x {
  opacity: 0;
  transform: scaleX(.04);
  transform-origin: left center;
  animation: easv-scale-x 820ms cubic-bezier(.22, 1, .36, 1) forwards;
  animation-delay: var(--easv-delay, 0ms);
}
.chart-card.is-playing .easv-draw {
  opacity: 1;
  stroke-dasharray: 1;
  stroke-dashoffset: 1;
  animation: easv-draw 860ms cubic-bezier(.22, 1, .36, 1) forwards;
  animation-delay: var(--easv-delay, 0ms);
}
@keyframes easv-fade { to { opacity: 1; } }
@keyframes easv-scale-y { to { opacity: 1; transform: scaleY(1); } }
@keyframes easv-scale-x { to { opacity: 1; transform: scaleX(1); } }
@keyframes easv-draw { to { stroke-dashoffset: 0; } }
@media (max-width: 760px) {
  .page-shell { padding: 18px; }
  .topbar { display: block; }
  .actions { justify-content: flex-start; margin-top: 14px; }
  .gallery { grid-template-columns: 1fr; }
}
@media (prefers-reduced-motion: reduce) {
  .chart-card.is-playing .easv-mark {
    animation: none !important;
    opacity: 1 !important;
    transform: none !important;
    stroke-dashoffset: 0 !important;
  }
}
`.trim()
}

function pageJs() {
  return `
function replayCard(card) {
  card.classList.remove('is-playing')
  void card.offsetWidth
  card.dataset.replayCount = String(Number(card.dataset.replayCount || 0) + 1)
  card.classList.add('is-playing')
}

document.querySelectorAll('[data-replay-card]').forEach((button) => {
  button.addEventListener('click', () => replayCard(button.closest('.chart-card')))
})

document.querySelector('#replay-all').addEventListener('click', () => {
  document.querySelectorAll('.chart-card').forEach(replayCard)
})
`.trim()
}

const galleryDefinitions = [...chartDefinitions, ...extraChartDefinitions]

const cards = galleryDefinitions.map((definition) => {
  const svg = renderSvg(definition)
  const exampleId = slug(definition.type)
  return `
    <article class="chart-card is-playing" id="example-${escapeHtml(exampleId)}" data-example-id="${escapeHtml(exampleId)}" data-chart-type="${escapeHtml(definition.type)}" data-replay-count="0">
      <header class="card-header">
        <div>
          <h2>${escapeHtml(definition.title)}</h2>
          <p>${escapeHtml(definition.summary)}</p>
        </div>
        <button type="button" data-replay-card aria-label="Replay ${escapeHtml(definition.title)} animation"><span class="material-symbols-rounded" aria-hidden="true">replay</span><span>Replay</span></button>
      </header>
      <div class="chart-stage">${svg}</div>
    </article>
  `.trim()
})

const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>ECharts Animated SVG Gallery</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400..700,0..1,0&family=Open+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>${pageCss()}</style>
</head>
<body>
  <main class="page-shell" data-expected-cards="${galleryDefinitions.length}" data-core-chart-count="${chartDefinitions.length}" data-extra-example-count="${extraChartDefinitions.length}">
    <header class="topbar">
      <div>
        <h1>ECharts Animated SVG Gallery</h1>
        <p class="lede">${chartDefinitions.length} ECharts chart types plus ${extraChartDefinitions.length} extra motion recipes are rendered as inline SVG and replayable after the first animation finishes.</p>
      </div>
      <div class="actions">
        <button id="replay-all" type="button"><span class="material-symbols-rounded" aria-hidden="true">replay</span><span>Replay all</span></button>
      </div>
    </header>
    <section class="gallery" aria-label="Animated ECharts SVG examples">
      ${cards.join('\n      ')}
    </section>
  </main>
  <script>${pageJs()}</script>
</body>
</html>
`

await writeFile(resolve(exampleRoot, 'index.html'), html, 'utf8')
console.log(`Wrote ${resolve(exampleRoot, 'index.html')} with ${galleryDefinitions.length} animated SVG examples.`)
