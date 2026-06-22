<template>
  <figure
    class="echart-frame"
    :class="[className, { 'svg-replayable-frame': isSvgReplayable, 'is-replaying': isReplaying }]"
    :style="{ height }"
    :aria-label="ariaLabel"
    :data-renderer="renderer"
    :data-svg-replayable="isSvgReplayable ? 'true' : undefined"
  >
    <div ref="chartElement" class="echart-canvas"></div>
  </figure>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import { echarts } from '../lib/echarts-setup.js'

const props = defineProps({
  option: {
    type: Object,
    required: true,
  },
  height: {
    type: String,
    default: '360px',
  },
  renderer: {
    type: String,
    default: 'canvas',
    validator: (value) => ['canvas', 'svg'].includes(value),
  },
  theme: {
    type: [String, Object],
    default: null,
  },
  updateOptions: {
    type: Object,
    default: () => ({
      lazyUpdate: false,
      notMerge: false,
    }),
  },
  className: {
    type: String,
    default: '',
  },
  ariaLabel: {
    type: String,
    default: 'ECharts visualization',
  },
  replayable: {
    type: Boolean,
    default: false,
  },
})

const chartElement = ref(null)
const chart = shallowRef(null)
const isReplaying = ref(false)
const isSvgReplayable = computed(() => props.replayable && props.renderer === 'svg')
let resizeObserver

function applyOption() {
  if (!chart.value)
    return

  chart.value.setOption(props.option, props.updateOptions)
}

function resizeChart() {
  if (!chart.value)
    return

  window.requestAnimationFrame(() => {
    chart.value?.resize()
  })
}

function handleContainerResize() {
  if (chart.value) {
    resizeChart()
    return
  }

  void initChart()
}

async function initChart() {
  await nextTick()

  if (!chartElement.value || chart.value)
    return

  if (chartElement.value.clientWidth === 0 || chartElement.value.clientHeight === 0)
    return

  chart.value = echarts.init(chartElement.value, props.theme, {
    renderer: props.renderer,
  })
  applyOption()
  resizeChart()
}

function startResizeObserver() {
  if ('ResizeObserver' in window) {
    resizeObserver = new ResizeObserver(handleContainerResize)
    resizeObserver.observe(chartElement.value)
  }
}

function handleWindowResize() {
  handleContainerResize()
}

function disposeChartInstance() {
  chart.value?.dispose()
  chart.value = null
}

function replaySvg() {
  if (!isSvgReplayable.value || !chartElement.value)
    return false

  isReplaying.value = false
  void chartElement.value.offsetWidth
  isReplaying.value = true
  return true
}

function disposeChart() {
  resizeObserver?.disconnect()
  resizeObserver = undefined
  window.removeEventListener('resize', handleWindowResize)
  disposeChartInstance()
}

onMounted(() => {
  startResizeObserver()
  window.addEventListener('resize', handleWindowResize, { passive: true })
  void initChart()
})
onBeforeUnmount(disposeChart)

watch(
  () => props.option,
  () => {
    if (chart.value)
      applyOption()
    else
      void initChart()
  },
  { deep: true },
)

watch(
  () => [props.renderer, props.theme],
  async () => {
    disposeChartInstance()
    await initChart()
  },
)

defineExpose({ replaySvg })
</script>
