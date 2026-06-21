<template>
  <section class="dashboard-demo">
    <div class="dashboard-heading">
      <div>
        <p class="eyebrow">Dashboard slide</p>
        <h2>{{ activeStage.title }}</h2>
      </div>
      <p>{{ activeStage.summary }}</p>
    </div>

    <div class="dashboard-metrics">
      <div v-for="metric in activeStage.metrics" :key="metric.label">
        <span>{{ metric.label }}</span>
        <strong>{{ metric.value }}</strong>
      </div>
    </div>

    <div class="dashboard-grid">
      <ResponsiveEChart :option="mixOption" height="205px" aria-label="Channel mix donut chart" />
      <ResponsiveEChart :option="radarOption" height="205px" aria-label="Capability radar chart" />
      <ResponsiveEChart :option="portfolioOption" height="205px" aria-label="Portfolio scatter chart" />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import ResponsiveEChart from './ResponsiveEChart.vue'

const props = defineProps({
  step: {
    type: Number,
    default: 0,
  },
})

const stages = [
  {
    title: 'Use multiple ECharts instances when comparison matters.',
    summary: 'Each chart has its own option but shares the same lifecycle wrapper and design system.',
    mix: [32, 24, 21, 23],
    current: [74, 82, 68, 71, 77],
    scatterLift: [0, 0, 0, 0, 0],
    metrics: [
      { label: 'Qualified mix', value: '56%' },
      { label: 'Coverage', value: '74' },
      { label: 'Priority plays', value: '5' },
    ],
  },
  {
    title: 'Let the deck focus attention before the data changes.',
    summary: 'The first click reweights channel mix and raises the operating profile without moving slide layout.',
    mix: [28, 29, 18, 25],
    current: [78, 84, 72, 74, 79],
    scatterLift: [3, 4, 2, 5, 3],
    metrics: [
      { label: 'Qualified mix', value: '63%' },
      { label: 'Coverage', value: '78' },
      { label: 'Priority plays', value: '5' },
    ],
  },
  {
    title: 'Use synchronized chart motion to make the argument legible.',
    summary: 'The second click updates every chart from the same business stage so the dashboard reads as one story.',
    mix: [24, 34, 16, 26],
    current: [82, 87, 77, 77, 82],
    scatterLift: [6, 7, 4, 8, 6],
    metrics: [
      { label: 'Qualified mix', value: '70%' },
      { label: 'Coverage', value: '82' },
      { label: 'Priority plays', value: '5' },
    ],
  },
  {
    title: 'Finish on a stable dashboard state for video export.',
    summary: 'The final state keeps all labels readable and avoids late layout shifts before the recorder advances.',
    mix: [22, 37, 14, 27],
    current: [86, 90, 82, 80, 86],
    scatterLift: [9, 10, 6, 10, 8],
    metrics: [
      { label: 'Qualified mix', value: '74%' },
      { label: 'Coverage', value: '86' },
      { label: 'Priority plays', value: '5' },
    ],
  },
]

const activeIndex = computed(() => Math.min(Math.max(Number(props.step) || 0, 0), stages.length - 1))
const activeStage = computed(() => stages[activeIndex.value])
const channels = ['Product', 'Partners', 'Events', 'Outbound']

const mixOption = computed(() => ({
  aria: { show: true },
  color: ['#007298', '#45842a', '#e77204', '#9e1b32'],
  animationDurationUpdate: 700,
  animationEasingUpdate: 'cubicOut',
  tooltip: { trigger: 'item' },
  legend: {
    bottom: 0,
    left: 'center',
    textStyle: { color: '#696969' },
  },
  series: [
    {
      id: 'channel-mix',
      name: 'Channel Mix',
      type: 'pie',
      radius: ['46%', '72%'],
      center: ['50%', '44%'],
      avoidLabelOverlap: true,
      label: { show: false },
      labelLine: { show: false },
      data: channels.map((name, index) => ({
        name,
        value: activeStage.value.mix[index],
      })),
      universalTransition: true,
    },
  ],
}))

const radarOption = computed(() => ({
  aria: { show: true },
  color: ['#45842a', '#9e1b32'],
  animationDurationUpdate: 700,
  animationEasingUpdate: 'cubicOut',
  tooltip: {},
  legend: {
    bottom: 0,
    left: 'center',
    textStyle: { color: '#696969' },
  },
  radar: {
    center: ['50%', '46%'],
    radius: '50%',
    indicator: [
      { name: 'Coverage', max: 100 },
      { name: 'Quality', max: 100 },
      { name: 'Speed', max: 100 },
      { name: 'Margin', max: 100 },
      { name: 'Retain', max: 100 },
    ],
    axisName: { color: '#696969', fontSize: 11 },
    splitLine: { lineStyle: { color: '#cfcfcf' } },
    splitArea: { areaStyle: { color: ['#f7f7f7', '#eef2f7'] } },
  },
  series: [
    {
      id: 'capability',
      type: 'radar',
      areaStyle: { opacity: 0.14 },
      data: [
        { name: 'Current', value: activeStage.value.current },
        { name: 'Target', value: [88, 90, 82, 79, 86] },
      ],
    },
  ],
}))

const portfolioOption = computed(() => ({
  aria: { show: true },
  color: ['#007298'],
  animationDurationUpdate: 700,
  animationEasingUpdate: 'cubicOut',
  tooltip: {
    formatter: (params) => {
      const [confidence, impact, effort, initiative] = params.data
      return `${initiative}<br/>Confidence: ${confidence}%<br/>Impact: ${impact}<br/>Effort: ${effort}`
    },
  },
  grid: {
    top: 28,
    right: 24,
    bottom: 42,
    left: 48,
  },
  xAxis: {
    name: 'Confidence',
    min: 50,
    max: 100,
    axisLabel: { formatter: '{value}%', color: '#696969' },
    nameTextStyle: { color: '#828282' },
    splitLine: { lineStyle: { color: '#e7e7e7' } },
  },
  yAxis: {
    name: 'Impact',
    min: 20,
    max: 100,
    axisLabel: { color: '#696969' },
    nameTextStyle: { color: '#828282' },
    splitLine: { lineStyle: { color: '#e7e7e7' } },
  },
  visualMap: {
    show: false,
    dimension: 2,
    min: 8,
    max: 34,
    inRange: {
      symbolSize: [10, 32],
      color: ['#45842a', '#e77204', '#9e1b32'],
    },
  },
  series: [
    {
      id: 'portfolio',
      type: 'scatter',
      data: [
        [72, 86, 22, 'Usage alerts'],
        [88, 78, 16, 'Partner scoring'],
        [64, 58, 30, 'Events refresh'],
        [92, 91, 12, 'In-app expansion'],
        [76, 69, 26, 'Lifecycle offers'],
      ].map(([confidence, impact, effort, initiative], index) => [
        Math.min(99, confidence + activeStage.value.scatterLift[index]),
        Math.min(98, impact + activeStage.value.scatterLift[index]),
        effort,
        initiative,
      ]),
      universalTransition: true,
    },
  ],
}))
</script>
