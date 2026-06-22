<template>
  <section class="composition-scene" :class="scene">
    <template v-if="scene === 'spotlight'">
      <div class="composition-copy">
        <p class="eyebrow">Spotlight composition</p>
        <h2>{{ activeCopy.title }}</h2>
        <p>{{ activeCopy.summary }}</p>
        <div class="composition-steps">
          <span
            v-for="(item, index) in spotlightCopy"
            :key="item.label"
            :class="{ active: index === activeIndex }"
          >
            {{ item.label }}
          </span>
        </div>
      </div>

      <div class="spotlight-stage">
        <ResponsiveEChart
          :option="primaryOption"
          height="330px"
          aria-label="Theme river spotlight chart"
          class-name="spotlight-chart"
        />
        <div class="spotlight-callouts">
          <div v-for="metric in activeCopy.metrics" :key="metric.label">
            <span>{{ metric.label }}</span>
            <strong>{{ metric.value }}</strong>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <div class="comparison-header">
        <div>
          <p class="eyebrow">Comparison composition</p>
          <h2>{{ activeCopy.title }}</h2>
        </div>
        <p>{{ activeCopy.summary }}</p>
      </div>

      <div class="comparison-grid">
        <div class="comparison-panel">
          <div>
            <p class="eyebrow">Magnitude</p>
            <h3>Product contribution</h3>
          </div>
          <ResponsiveEChart :option="primaryOption" height="170px" aria-label="Bar comparison chart" />
        </div>

        <div class="comparison-panel">
          <div>
            <p class="eyebrow">Portfolio</p>
            <h3>Confidence and impact</h3>
          </div>
          <ResponsiveEChart :option="secondaryOption" height="170px" aria-label="Scatter comparison chart" />
        </div>
      </div>

    </template>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import ResponsiveEChart from './ResponsiveEChart.vue'
import { chartSpec } from '../lib/chart-lab.js'

const props = defineProps({
  scene: {
    type: String,
    default: 'spotlight',
    validator: (value) => ['spotlight', 'comparison'].includes(value),
  },
  step: {
    type: Number,
    default: 0,
  },
})

const spotlightCopy = [
  {
    label: 'Baseline stream',
    title: 'Let one large chart carry the scene.',
    summary: 'A spotlight composition gives the chart most of the slide while copy and metrics frame the interpretation.',
    metrics: [
      { label: 'Product stream', value: '31%' },
      { label: 'Partner lift', value: '18%' },
    ],
  },
  {
    label: 'Focus shift',
    title: 'Use click state to rebalance attention.',
    summary: 'The chart changes first, then the surrounding callouts reinforce what the audience should compare.',
    metrics: [
      { label: 'Product stream', value: '36%' },
      { label: 'Partner lift', value: '24%' },
    ],
  },
  {
    label: 'Motion proof',
    title: 'Keep the final frame useful as a still.',
    summary: 'Video export should end each scene on a stable, readable composition after the motion resolves.',
    metrics: [
      { label: 'Product stream', value: '42%' },
      { label: 'Partner lift', value: '29%' },
    ],
  },
]

const comparisonCopy = [
  {
    label: 'Separate measures',
    title: 'Place charts side by side only when the comparison is explicit.',
    summary: 'The first state separates magnitude and portfolio quality without asking one chart to do both jobs.',
  },
  {
    label: 'Synchronized update',
    title: 'Advance both charts from the same click state.',
    summary: 'The viewer sees product contribution and opportunity quality move together, so the video reads as one decision.',
  },
  {
    label: 'Final alignment',
    title: 'Use the last state as the export-safe evidence frame.',
    summary: 'Stable axes, legends, and labels make the recorded composition useful even after the animation finishes.',
  },
]

const activeIndex = computed(() => Math.min(Math.max(Number(props.step) || 0, 0), 2))
const activeCopy = computed(() => (props.scene === 'spotlight' ? spotlightCopy : comparisonCopy)[activeIndex.value])
const primaryType = computed(() => (props.scene === 'spotlight' ? 'themeRiver' : 'bar'))
const secondaryType = computed(() => (props.scene === 'comparison' ? 'scatter' : 'pie'))
const primaryOption = computed(() => chartSpec(primaryType.value).option(activeIndex.value))
const secondaryOption = computed(() => chartSpec(secondaryType.value).option(activeIndex.value))
</script>
