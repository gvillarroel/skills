<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useId, watch } from 'vue'
import { useIsSlideActive, useSlideContext } from '@slidev/client'
import type { HyperframesPlayer } from '@hyperframes/player'
import fontUrl from '../public/hyperframes/fonts/open-sans-latin-wght-normal.woff2?inline'
import { assetUrl, compositionDocument, cueTime, paletteFor, sceneMarkup, SCENE_DURATION, starterUrl } from '../lib/hyperframes.js'

const props = withDefaults(defineProps<{
  src?: string; step?: number; cueTimes?: number[]; active?: boolean; playing?: boolean
  height?: number; colorset?: 'colorset1' | 'colorset2'; static?: boolean
  exportTime?: number; label?: string; poster?: string
}>(), { src: 'hyperframes/starter.html', step: 0, cueTimes: () => [0, 3, 6, 9],
  active: undefined, playing: false, height: 330, colorset: 'colorset1', static: false, exportTime: 9,
  label: 'Valve-controlled transport' })
const emit = defineEmits<{
  ready: [state: { time: number; duration: number; sourceKind: string }]
  timeupdate: [time: number]; error: [message: string]
}>()
defineSlots<{
  loading(props: { status: string }): unknown
  error(props: { message: string }): unknown
  fallback(props: { time: number; colorset: string; label: string }): unknown
}>()
const slideActive = useIsSlideActive()
const { $renderContext } = useSlideContext()
const host = ref<HTMLElement>()
const status = ref('loading'), ready = ref(false), paused = ref(true), time = ref(0), duration = ref(0)
const sourceKind = ref('composition'), message = ref('')
const palette = computed(() => paletteFor(props.colorset))
const isStatic = computed(() => props.static || ($renderContext?.value && !['slide', 'presenter'].includes($renderContext.value)))
const active = computed(() => (props.active ?? slideActive.value) && !documentHidden.value)
const documentHidden = ref(false)
const manualTime = ref<number>()
const targetTime = computed(() => manualTime.value ?? (isStatic.value ? validTime(props.exportTime) : cueTime(props.step, props.cueTimes, duration.value || Infinity)))
const validHeight = computed(() => { if (!Number.isFinite(props.height) || props.height <= 0) throw new TypeError('height must be positive and finite'); return props.height })
const style = computed(() => ({ height: `${validHeight.value}px`, '--hf-surface': palette.value.roles.surface, '--hf-ink': '#000000' }))
const fallbackId = `${useId()}-`
const fontCss = `@font-face{font-family:'Open Sans';font-style:normal;font-weight:300 800;src:url('${fontUrl}') format('woff2')}`
const fallback = computed(() => sceneMarkup(targetTime.value, palette.value, props.src.includes('compact=1'), fallbackId))
let player: HyperframesPlayer | undefined, generation = 0, applyGeneration = 0, assetsReady = false, disposed = false
let cleanup: Array<() => void> = []
const paintRequests = new Set<number>(), paintWaiters = new Set<() => void>()
function validTime(value: number) {
  if (!Number.isFinite(value) || value < 0) throw new TypeError('exportTime must be finite and nonnegative')
  return Math.min(value, duration.value || Infinity)
}
function fail(error: unknown) {
  message.value = error instanceof Error ? error.message : String(error)
  ready.value = false; status.value = 'error'; player?.pause(); paused.value = true
  emit('error', message.value)
}
function stop() { player?.pause(); paused.value = true }
function play() {
  if (ready.value && active.value && !isStatic.value && !motionQuery?.matches) { player?.play(); paused.value = false }
}
let motionQuery: MediaQueryList | undefined, request: AbortController | undefined
function reportReady() {
  ready.value = true; status.value = 'ready'
  emit('ready', { time: time.value, duration: duration.value, sourceKind: sourceKind.value })
}
function paintedFrame() {
  return new Promise<void>(resolve => {
    const finish = () => { paintWaiters.delete(finish); resolve() }
    paintWaiters.add(finish)
    const first = requestAnimationFrame(() => {
      paintRequests.delete(first)
      const second = requestAnimationFrame(() => { paintRequests.delete(second); finish() })
      paintRequests.add(second)
    })
    paintRequests.add(first)
  })
}
async function applyCue(seconds = targetTime.value, resume = props.playing && manualTime.value === undefined) {
  if (sourceKind.value === 'fallback') {
    const epoch = ++applyGeneration
    ready.value = false; stop(); time.value = validTime(seconds)
    await nextTick(); await document.fonts.ready
    if (epoch !== applyGeneration || disposed) return
    await paintedFrame()
    if (epoch === applyGeneration && !disposed) reportReady()
    return
  }
  if (!player?.ready || !assetsReady || disposed) return
  const epoch = ++applyGeneration, current = player
  ready.value = false
  current.pause(); current.seek(validTime(seconds)); paused.value = true
  // The same-origin runtime seek is synchronous; two native paints also cover its bridge message.
  const doc = current.iframeElement.contentDocument
  if (doc) await doc.fonts.ready
  if (epoch !== applyGeneration || current !== player || disposed) return
  await paintedFrame()
  if (epoch !== applyGeneration || current !== player || disposed) return
  time.value = current.currentTime
  reportReady()
  if (resume) play()
}
function destroyPlayer() {
  ++applyGeneration; stop()
  for (const remove of cleanup) remove()
  cleanup = []; player?.remove(); player = undefined; assetsReady = false
  request?.abort(); request = undefined
  for (const frame of paintRequests) cancelAnimationFrame(frame)
  paintRequests.clear()
  for (const finish of [...paintWaiters]) finish()
}
async function mountPlayer() {
  const epoch = ++generation
  destroyPlayer(); ready.value = false; status.value = 'loading'; message.value = ''; duration.value = 0
  if (location.protocol === 'file:') {
    sourceKind.value = 'fallback'; duration.value = props.src.split('?')[0].endsWith('hyperframes/starter.html') ? SCENE_DURATION : 0
    time.value = targetTime.value; paused.value = true
    await nextTick(); await document.fonts.load('600 24px "Open Sans"'); await document.fonts.ready
    if (epoch === generation && !disposed) await applyCue()
    return
  }
  sourceKind.value = 'composition'
  try {
    await import('@hyperframes/player')
    if (epoch !== generation || disposed || !host.value) return
    const current = document.createElement('hyperframes-player') as HyperframesPlayer
    player = current
    current.style.cssText = `display:block;width:100%;height:100%;min-width:0;min-height:0;background:${palette.value.roles.surface}`
    current.setAttribute('muted', ''); current.setAttribute('audio-locked', '')
    current.setAttribute('assets-loading-ui', 'none'); current.setAttribute('shader-loading', 'none')
    current.setAttribute('runtime-src', assetUrl('hyperframes/vendor/hyperframe.runtime.iife.js', import.meta.env.BASE_URL, document.baseURI))
    current.iframeElement.title = props.label
    const listen = (name: string, fn: EventListener) => { current.addEventListener(name, fn); cleanup.push(() => current.removeEventListener(name, fn)) }
    listen('ready', event => { duration.value = (event as CustomEvent).detail.duration; if (assetsReady) void applyCue() })
    listen('assetsready', () => { assetsReady = true; void applyCue() })
    listen('timeupdate', () => { time.value = current.currentTime; paused.value = current.paused; emit('timeupdate', time.value) })
    listen('pause', () => { paused.value = true })
    listen('play', () => { if (!active.value || isStatic.value || motionQuery?.matches) stop(); else paused.value = false })
    listen('error', event => fail((event as CustomEvent).detail?.message || 'Composition could not load'))
    const url = starterUrl(props.src, props.colorset, import.meta.env.BASE_URL, document.baseURI)
    if (new URL(url).origin !== location.origin) throw new TypeError('Composition src must be same-origin; copy its complete local folder into public/')
    request = new AbortController()
    const response = await fetch(url, { signal: request.signal })
    if (!response.ok) throw new Error(`Composition request failed (${response.status})`)
    const html = await response.text()
    if (epoch !== generation || disposed) return
    const documentRoot = new DOMParser().parseFromString(html, 'text/html').querySelector('[data-composition-id][data-width][data-height]')
    if (!documentRoot || !['width', 'height'].every(key => { const value = Number(documentRoot.getAttribute(`data-${key}`)); return Number.isFinite(value) && value > 0 })) throw new TypeError('Composition HTML needs a root with positive data-width/data-height and data-composition-id')
    current.setAttribute('srcdoc', compositionDocument(html, url))
    host.value.appendChild(current)
  } catch (error) { if (epoch === generation && !disposed) fail(error) }
}
function visibility() { documentHidden.value = document.hidden }
onMounted(() => {
  // Retain one font definition per document: remounting cells must not restart font loading/pagination.
  if (!document.querySelector('style[data-slidev-hyperframes-font]')) {
    const style = document.createElement('style'); style.dataset.slidevHyperframesFont = ''; style.textContent = fontCss
    document.head.appendChild(style)
  }
  visibility(); document.addEventListener('visibilitychange', visibility)
  motionQuery = matchMedia('(prefers-reduced-motion: reduce)')
  const motion = () => { if (motionQuery!.matches) stop(); else if (props.playing) play() }
  motionQuery.addEventListener('change', motion); cleanupMotion = () => motionQuery?.removeEventListener('change', motion)
  void mountPlayer()
})
let cleanupMotion = () => {}
watch(() => [props.src, props.colorset], () => { manualTime.value = undefined; if (host.value) void mountPlayer() })
watch(targetTime, () => {
  void applyCue()
})
watch(() => [props.step, props.cueTimes, props.static, props.exportTime], () => { manualTime.value = undefined }, { deep: true })
watch([active, isStatic], () => {
  manualTime.value = undefined
  if (!active.value || isStatic.value || !props.playing) stop()
  if (active.value) void applyCue()
})
watch(() => props.playing, () => { if (props.playing) play(); else stop() })
watch(() => props.label, () => { if (player) player.iframeElement.title = props.label })
onBeforeUnmount(() => { disposed = true; ++generation; document.removeEventListener('visibilitychange', visibility); cleanupMotion(); destroyPlayer() })
defineExpose({ seek: (seconds: number) => { if (!Number.isFinite(seconds) || seconds < 0) throw new TypeError('seek requires finite nonnegative seconds'); manualTime.value = validTime(seconds); return applyCue(manualTime.value, false) }, play, pause: stop, getPlayer: () => player })
</script>

<template>
  <div class="hyperframe-slide" :style="style" :aria-label="label" role="group"
    :data-ready="ready" :data-status="status" :data-time="time" :data-paused="paused"
    :data-source-kind="sourceKind" :data-colorset="colorset" :data-static="isStatic">
    <div v-show="sourceKind === 'composition'" ref="host" class="hyperframe-host" />
    <div v-if="sourceKind === 'fallback'" class="hyperframe-fallback">
      <slot name="fallback" :time="targetTime" :colorset="colorset" :label="label">
        <img v-if="poster" :src="poster" :alt="label" />
        <div v-else-if="src.split('?')[0].endsWith('hyperframes/starter.html')" v-html="fallback" />
        <p v-else>Interactive composition: {{ label }}. Serve this deck over HTTP to play it.</p>
      </slot>
    </div>
    <div v-if="status === 'loading'" class="hyperframe-message" role="status"><slot name="loading" :status="status">Loading composition…</slot></div>
    <div v-if="status === 'error'" class="hyperframe-message" role="alert"><slot name="error" :message="message">{{ message }}</slot></div>
  </div>
</template>

<style scoped>
.hyperframe-slide { position:relative; width:100%; min-width:0; box-sizing:border-box; overflow:hidden; background:var(--hf-surface); color:var(--hf-ink); font-family:'Open Sans',sans-serif; }
.hyperframe-host,.hyperframe-fallback { width:100%;height:100%;min-width:0;min-height:0; }
.hyperframe-fallback :deep(svg),.hyperframe-fallback img,.hyperframe-fallback :deep(div) { display:block;width:100%;height:100%;object-fit:contain; }
.hyperframe-message { position:absolute;inset:0;display:grid;place-items:center;padding:16px;box-sizing:border-box;background:var(--hf-surface);color:var(--hf-ink);font-size:16px;opacity:1; }
.hyperframe-fallback p { margin:0;padding:16px;font-size:16px;opacity:1; }
</style>
