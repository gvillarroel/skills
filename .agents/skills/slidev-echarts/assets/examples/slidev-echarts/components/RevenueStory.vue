<template>
  <section class="revenue-story">
    <div class="story-header">
      <div>
        <p class="eyebrow">Click story</p>
        <h2>{{ activeStage.label }}</h2>
      </div>
      <p>{{ activeStage.summary }}</p>
    </div>
    <ResponsiveEChart
      :option="option"
      :update-options="{ lazyUpdate: false, notMerge: false }"
      height="220px"
      aria-label="Revenue scenario chart"
    />
    <div class="step-pills">
      <span
        v-for="(stage, index) in stages"
        :key="stage.label"
        :class="{ active: index === activeIndex }"
      >
        {{ stage.label }}
      </span>
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

const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
const baseline = [44, 47, 50, 54, 58, 61]

const stages = [
  {
    label: 'Baseline',
    summary: 'The original plan leans on broad acquisition and produces steady but shallow growth.',
    values: [44, 47, 50, 54, 58, 61],
    color: '#007298',
  },
  {
    label: 'Product-qualified demand',
    summary: 'Traffic shifts toward product signals, lifting mid-quarter conversion without adding noise.',
    values: [44, 50, 57, 63, 68, 72],
    color: '#45842a',
  },
  {
    label: 'Partner lift',
    summary: 'Partner coverage compounds the qualified path and moves the second half above target.',
    values: [44, 50, 60, 70, 78, 86],
    color: '#e77204',
  },
  {
    label: 'New operating path',
    summary: 'The final view keeps the baseline visible while the improved path carries the story.',
    values: [44, 52, 63, 75, 86, 96],
    color: '#9e1b32',
  },
]

const activeIndex = computed(() => Math.min(Math.max(Number(props.step) || 0, 0), stages.length - 1))
const activeStage = computed(() => stages[activeIndex.value])
const source = computed(() => months.map((month, index) => ({
  month,
  Baseline: baseline[index],
  Scenario: activeStage.value.values[index],
})))

const option = computed(() => ({
  aria: { show: true },
  backgroundColor: 'transparent',
  color: ['#9c9c9c', activeStage.value.color],
  animationDuration: 700,
  animationDurationUpdate: 700,
  animationEasingUpdate: 'cubicOut',
  tooltip: { trigger: 'axis' },
  legend: {
    top: 2,
    right: 8,
    textStyle: { color: '#696969' },
  },
  grid: {
    top: 58,
    right: 28,
    bottom: 42,
    left: 48,
  },
  dataset: { source: source.value },
  xAxis: {
    type: 'category',
    axisTick: { show: false },
    axisLine: { lineStyle: { color: '#cfcfcf' } },
    axisLabel: { color: '#696969' },
  },
  yAxis: {
    type: 'value',
    name: 'ARR index',
    min: 35,
    max: 105,
    splitLine: { lineStyle: { color: '#e7e7e7' } },
    axisLabel: { color: '#696969' },
    nameTextStyle: { color: '#828282' },
  },
  series: [
    {
      id: 'baseline',
      name: 'Baseline',
      type: 'line',
      smooth: true,
      symbolSize: 7,
      lineStyle: { width: 2, type: 'dashed' },
      encode: { x: 'month', y: 'Baseline' },
    },
    {
      id: 'scenario',
      name: activeStage.value.label,
      type: 'bar',
      barWidth: 28,
      itemStyle: { borderRadius: [6, 6, 0, 0] },
      encode: { x: 'month', y: 'Scenario' },
      universalTransition: true,
    },
  ],
}))
</script>
