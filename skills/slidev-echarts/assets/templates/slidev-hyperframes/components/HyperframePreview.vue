<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onSlideLeave, useIsSlideActive, useSlideContext } from '@slidev/client'
import HyperframeSlide from './HyperframeSlide.vue'
import { paletteFor } from '../lib/hyperframes.js'

const props = withDefaults(defineProps<{
  src?: string; step?: number; cueTimes?: number[]; active?: boolean
  height?: number; colorset?: 'colorset1' | 'colorset2'; static?: boolean
  exportTime?: number; label?: string; poster?: string; controls?: boolean
}>(), { src: 'hyperframes/starter.html', step: 0, cueTimes: () => [0, 4, 9],
  active: undefined, height: 330, colorset: 'colorset1', static: false,
  exportTime: 9, label: 'Valve-controlled transport', controls: true })
const emit = defineEmits<{
  ready: [state: { time: number; duration: number; sourceKind: string }]
  timeupdate: [time: number]; error: [message: string]
}>()
defineSlots<{
  loading(props: { status: string }): unknown
  error(props: { message: string }): unknown
  fallback(props: { time: number; colorset: string; label: string }): unknown
}>()
const slide = ref<InstanceType<typeof HyperframeSlide>>()
const playing = ref(false), ready = ref(false), reduced = ref(false), offline = ref(false)
const slideActive = useIsSlideActive()
const { $renderContext } = useSlideContext()
const active = computed(() => props.active ?? slideActive.value)
const isStatic = computed(() => props.static || ($renderContext?.value && !['slide', 'presenter'].includes($renderContext.value)))
const showControls = computed(() => props.controls && !isStatic.value && !offline.value)
const palette = computed(() => paletteFor(props.colorset))
const style = computed(() => {
  const { roles, textOnFill } = palette.value
  return {
    gridTemplateRows: `${props.height}px${showControls.value ? ' 38px' : ''}`,
    height: `${props.height + (showControls.value ? 48 : 0)}px`,
    '--hp-surface': roles.surface, '--hp-ink': textOnFill[roles.surface],
    '--hp-primary': roles.primary, '--hp-primary-ink': textOnFill[roles.primary],
    '--hp-hover': roles.primaryDark, '--hp-hover-ink': textOnFill[roles.primaryDark],
    '--hp-quiet': roles.quiet, '--hp-quiet-ink': textOnFill[roles.quiet], '--hp-focus': roles.accent,
  }
})
function pause() { playing.value = false; slide.value?.pause() }
function play() { if (ready.value && active.value && !reduced.value && !isStatic.value && !offline.value) playing.value = true }
function toggle() { if (playing.value) pause(); else play() }
function onReady(state: { time: number; duration: number; sourceKind: string }) {
  ready.value = true; offline.value = state.sourceKind === 'fallback'; emit('ready', state)
}
function onError(message: string) { ready.value = false; pause(); emit('error', message) }
onSlideLeave(pause)
watch(() => [props.step, props.src, props.cueTimes, props.colorset, props.static, props.exportTime], () => { ready.value = false; pause() }, { deep: true })
watch(active, value => { if (!value) pause() })
let query: MediaQueryList | undefined
function updateMotion() { reduced.value = query?.matches ?? false; if (reduced.value) pause() }
onMounted(() => {
  offline.value = location.protocol === 'file:'
  query = matchMedia('(prefers-reduced-motion: reduce)'); updateMotion()
  query.addEventListener('change', updateMotion)
})
onBeforeUnmount(() => { pause(); query?.removeEventListener('change', updateMotion) })
defineExpose({ play, pause, seek: async (seconds: number) => { pause(); await slide.value?.seek(seconds) }, getPlayer: () => slide.value?.getPlayer() })
</script>

<template>
  <div class="hyperframe-preview" :style="style" :data-preview-playing="playing"
    :data-preview-ready="ready" :data-preview-controls="showControls" :data-colorset="colorset">
    <HyperframeSlide ref="slide" :src="src" :step="step" :cue-times="cueTimes" :active="active"
      :playing="playing" :height="height" :colorset="colorset" :static="static"
      :export-time="exportTime" :label="label" :poster="poster"
      @ready="onReady" @timeupdate="emit('timeupdate', $event)" @error="onError">
      <template v-if="$slots.loading" #loading="scope"><slot name="loading" v-bind="scope" /></template>
      <template v-if="$slots.error" #error="scope"><slot name="error" v-bind="scope" /></template>
      <template v-if="$slots.fallback" #fallback="scope"><slot name="fallback" v-bind="scope" /></template>
    </HyperframeSlide>
    <button v-if="showControls" class="hyperframe-preview-control" type="button"
      :disabled="!ready || !active || reduced" :aria-label="playing ? 'Pause animation' : 'Play animation'"
      :aria-pressed="playing" @click="toggle">{{ playing ? 'Pause animation' : 'Play animation' }}</button>
  </div>
</template>

<style scoped>
.hyperframe-preview { display:grid; gap:10px; width:100%; min-width:0; box-sizing:border-box;
  background:var(--hp-surface); color:var(--hp-ink); font-family:'Open Sans',sans-serif; }
.hyperframe-preview-control { box-sizing:border-box; height:38px; min-height:38px; width:max-content;
  max-width:100%; margin:0; padding:0 16px; border:0; border-radius:8px; opacity:1;
  background:var(--hp-primary); color:var(--hp-primary-ink); font:700 16px/1.2 'Open Sans',sans-serif;
  cursor:pointer; justify-self:start; }
.hyperframe-preview-control:hover:not(:disabled) { background:var(--hp-hover); color:var(--hp-hover-ink); }
.hyperframe-preview-control:focus-visible { outline:2px solid var(--hp-focus); outline-offset:2px; }
.hyperframe-preview-control:disabled { background:var(--hp-quiet); color:var(--hp-quiet-ink); opacity:1; cursor:default; }
</style>
