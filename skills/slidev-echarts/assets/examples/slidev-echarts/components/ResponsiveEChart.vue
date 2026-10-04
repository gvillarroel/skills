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
import { colorsetTheme, enforceColorsetRenderer, insetCartesianArrowRoutes, insetGraphArrowRoutes, prepareColorsetOption, qualifyBoxplotMedians } from '../../../templates/echarts-colorsets.mjs'

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
  arrowTerminalClearance: {
    type: Number,
    default: 0,
  },
})

const chartElement = ref(null)
const chart = shallowRef(null)
const isReplaying = ref(false)
const isSvgReplayable = computed(() => props.replayable && props.renderer === 'svg')
let resizeObserver
let stopPaletteEnforcement
let qualifyingGraphArrows = false

function qualifyGraphArrows() {
  if (!chart.value || qualifyingGraphArrows)
    return

  qualifyingGraphArrows = true
  try {
    insetGraphArrowRoutes(chart.value, 3)
  }
  finally {
    qualifyingGraphArrows = false
  }
}

function applyOption() {
  if (!chart.value)
    return

  const option = prepareColorsetOption(props.option, 'colorset2')
  chart.value.setOption(option, props.updateOptions)
  if (props.arrowTerminalClearance > 0)
    chart.value.setOption(insetCartesianArrowRoutes(option, chart.value, props.arrowTerminalClearance), props.updateOptions)
  qualifyBoxplotMedians(chart.value, echarts, 'colorset2')
  if (chart.value.getZr().animation.isFinished())
    qualifyGraphArrows()
}

function resizeChart() {
  if (!chart.value)
    return

  window.requestAnimationFrame(() => {
    chart.value?.resize()
    if (props.arrowTerminalClearance > 0)
      applyOption()
    else if (chart.value)
      qualifyBoxplotMedians(chart.value, echarts, 'colorset2')
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

  chart.value = echarts.init(chartElement.value, props.theme || colorsetTheme('colorset2'), {
    renderer: props.renderer,
  })
  chart.value.on('finished', qualifyGraphArrows)
  stopPaletteEnforcement = enforceColorsetRenderer(chartElement.value, 'colorset2')
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
  stopPaletteEnforcement?.()
  stopPaletteEnforcement = undefined
  chart.value?.off('finished', qualifyGraphArrows)
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

watch(() => props.arrowTerminalClearance, () => {
  if (chart.value)
    applyOption()
})

defineExpose({ replaySvg })
</script>
