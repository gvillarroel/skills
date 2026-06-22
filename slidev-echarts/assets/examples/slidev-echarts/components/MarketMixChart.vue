<template>
  <section class="chart-example market-mix">
    <div class="chart-copy">
      <p class="eyebrow">Acquisition mix</p>
      <h3>Stacked volume with a quality signal</h3>
      <p>Blend bars and a line series to keep demand volume and pipeline quality in the same story.</p>
    </div>
    <ResponsiveEChart :option="option" height="270px" aria-label="Acquisition mix chart" />
  </section>
</template>

<script setup>
import { computed } from 'vue'
import ResponsiveEChart from './ResponsiveEChart.vue'

const source = [
  ['month', 'Paid Search', 'Partners', 'Product Led', 'Pipeline Quality'],
  ['Jan', 42, 18, 28, 62],
  ['Feb', 48, 22, 34, 66],
  ['Mar', 51, 25, 43, 71],
  ['Apr', 46, 30, 49, 74],
  ['May', 39, 36, 58, 78],
  ['Jun', 35, 43, 64, 83],
]

const option = computed(() => ({
  aria: { show: true },
  backgroundColor: 'transparent',
  color: ['#007298', '#45842a', '#e77204', '#9e1b32'],
  tooltip: { trigger: 'axis' },
  legend: {
    top: 0,
    right: 0,
    textStyle: { color: '#696969' },
  },
  grid: {
    top: 56,
    right: 48,
    bottom: 42,
    left: 48,
  },
  dataset: { source },
  xAxis: {
    type: 'category',
    axisTick: { show: false },
    axisLine: { lineStyle: { color: '#cfcfcf' } },
    axisLabel: { color: '#696969' },
  },
  yAxis: [
    {
      type: 'value',
      name: 'Leads',
      splitLine: { lineStyle: { color: '#e7e7e7' } },
      axisLabel: { color: '#696969' },
      nameTextStyle: { color: '#828282' },
    },
    {
      type: 'value',
      name: 'Quality',
      min: 50,
      max: 90,
      splitLine: { show: false },
      axisLabel: { formatter: '{value}%', color: '#696969' },
      nameTextStyle: { color: '#828282' },
    },
  ],
  series: [
    { id: 'paid-search', type: 'bar', stack: 'leads', name: 'Paid Search', emphasis: { focus: 'series' } },
    { id: 'partners', type: 'bar', stack: 'leads', name: 'Partners', emphasis: { focus: 'series' } },
    { id: 'product-led', type: 'bar', stack: 'leads', name: 'Product Led', emphasis: { focus: 'series' } },
    {
      id: 'pipeline-quality',
      type: 'line',
      name: 'Pipeline Quality',
      yAxisIndex: 1,
      smooth: true,
      symbolSize: 8,
      lineStyle: { width: 3 },
      encode: { x: 'month', y: 'Pipeline Quality' },
    },
  ],
}))
</script>
