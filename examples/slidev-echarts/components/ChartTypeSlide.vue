<template>
  <section class="chart-type-slide">
    <div class="chart-type-header">
      <div>
        <p class="eyebrow">{{ spec.type }}</p>
        <h2>{{ spec.title }}</h2>
      </div>
      <div class="chart-type-summary">
        <p>{{ spec.summary }}</p>
        <div class="chart-type-controls">
          <span class="renderer-badge">{{ renderer.toUpperCase() }} renderer</span>
          <button v-if="renderer === 'svg'" type="button" data-svg-replay-button @click="replaySvg">
            Replay SVG
          </button>
        </div>
      </div>
    </div>

    <div class="chart-type-body">
      <ResponsiveEChart
        ref="chartRef"
        :option="option"
        height="280px"
        :renderer="renderer"
        :replayable="renderer === 'svg'"
        :aria-label="`${spec.title} animation demo`"
        class-name="chart-lab-frame"
      />

      <aside class="chart-type-notes">
        <div>
          <h3>Data shape</h3>
          <p>{{ spec.dataShape }}</p>
        </div>
        <div>
          <h3>Animation test</h3>
          <p>{{ spec.animation }}</p>
        </div>
        <div>
          <h3>Modules</h3>
          <p>{{ spec.modules.join(', ') }}</p>
        </div>
        <div>
          <h3>SVG replay</h3>
          <p>Animate rendered marks from a wrapper class and keep ECharts geometry intact.</p>
        </div>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import ResponsiveEChart from './ResponsiveEChart.vue'
import { chartSpec } from '../lib/chart-lab.js'

const props = defineProps({
  chartType: {
    type: String,
    required: true,
  },
  step: {
    type: Number,
    default: 0,
  },
  renderer: {
    type: String,
    default: 'svg',
    validator: (value) => ['canvas', 'svg'].includes(value),
  },
})

const chartRef = ref(null)
const spec = computed(() => chartSpec(props.chartType))
const option = computed(() => spec.value.option(props.step))

function replaySvg() {
  chartRef.value?.replaySvg()
}
</script>
