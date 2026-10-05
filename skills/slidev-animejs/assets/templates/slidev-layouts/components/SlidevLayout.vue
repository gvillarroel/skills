<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { extendCategoryOrder, layoutTheme, planSlideLayout } from '../lib/slidev-layouts.mjs'

interface LayoutItem {
  id: string
  category?: string
  title?: string
  body?: string
  width?: number
  [key: string]: unknown
}
interface LayoutBox {
  item: LayoutItem
  index: number
  id: string
  category: string
  x: number
  y: number
  width: number
  height: number
  contentWidth: number
  contentHeight: number
  row: number
  column: number
  fill: string
  ink: string
  borderWidth: number
  borderColor: string
  borderStyle: string
}
type Mode = 'columns' | 'grid' | 'masonry-columns' | 'masonry-rows'
const props = withDefaults(defineProps<{
  items: LayoutItem[]
  mode?: Mode
  columns?: number
  rows?: number
  colorset?: 'colorset1' | 'colorset2'
  categoryOrder?: string[]
  page?: number
  pageSize?: number
  height?: number
  gap?: number
  minItemWidth?: number
  minItemHeight?: number
  label?: string
  debug?: boolean
}>(), {
  mode: 'grid', columns: 3, rows: 3, colorset: 'colorset1', page: 1,
  height: 390, gap: 16, minItemWidth: 140, minItemHeight: 96,
  label: 'Slide components', debug: false,
})
const emit = defineEmits<{ capacity: [report: Record<string, unknown>] }>()
defineSlots<{
  item(props: { item: LayoutItem, index: number, color: { fill: string, ink: string }, style: Record<string, string>, box: LayoutBox }): unknown
}>()
const frame = ref<HTMLElement>()
const width = ref(900)
const measurements = ref<Record<string, { height: number, width: number }>>({})
const registry = ref<string[]>([])
const bodies = new Map<string, HTMLElement>()
let observer: ResizeObserver | undefined
let disposed = false
let queued = false
let emittedReport = ''

watch(() => [props.items, props.categoryOrder] as const, () => {
  // Explicit categoryOrder owns cross-slide identity. The local registry retains
  // all first-seen identities when the visible dataset changes or is reordered.
  const previous = props.categoryOrder
    ? extendCategoryOrder(props.categoryOrder, registry.value.map(id => ({ id })))
    : registry.value
  registry.value = extendCategoryOrder(previous, props.items)
}, { immediate: true, deep: true })
const theme = computed(() => layoutTheme(props.colorset))
const plan = computed(() => planSlideLayout({
  items: props.items, mode: props.mode, columns: props.columns, rows: props.rows,
  width: width.value, height: props.height, gap: props.gap,
  minItemWidth: props.minItemWidth, minItemHeight: props.minItemHeight,
  page: props.page, pageSize: props.pageSize, colorset: props.colorset,
  categoryOrder: registry.value, measurements: measurements.value,
}))
const rootStyle = computed(() => ({
  height: `${props.height}px`, '--layout-canvas': theme.value.canvas,
  '--layout-ink': theme.value.ink, '--layout-primary': theme.value.primary,
  '--layout-line': theme.value.line, '--layout-quiet': theme.value.quiet,
  fontFamily: theme.value.font,
}))
function itemStyle(box: LayoutBox) {
  return {
    left: `${box.x}px`, top: `${box.y}px`, width: `${box.width}px`,
    minHeight: `${box.height}px`, backgroundColor: box.fill, color: box.ink,
    borderWidth: `${box.borderWidth}px`, borderColor: box.borderColor,
    borderStyle: box.borderStyle, '--layout-fill': box.fill, '--layout-text': box.ink,
  }
}
function slotStyle(box: LayoutBox) {
  return { color: box.ink, backgroundColor: box.fill, '--layout-fill': box.fill, '--layout-text': box.ink }
}
function measure() {
  if (disposed || !frame.value) return
  const nextWidth = frame.value.clientWidth
  if (nextWidth > 0 && Math.abs(nextWidth - width.value) > 0.25) width.value = nextWidth
  const next = { ...measurements.value }
  let changed = false
  for (const box of plan.value.items as LayoutBox[]) {
    const body = bodies.get(box.id)
    if (!body) continue
    // offset/scroll dimensions are native CSS pixels even when Slidev scales
    // its fixed frame with a CSS transform. Never shrink or clamp text.
    const height = Math.max(body.offsetHeight, body.scrollHeight) + 28 + 2 * box.borderWidth
    const width = body.scrollWidth > body.clientWidth + 1
      ? body.scrollWidth + 28 + 2 * box.borderWidth
      : box.width
    const old = next[box.id]
    if (!old || Math.abs(old.height - height) > 0.5 || Math.abs(old.width - width) > 0.5) {
      next[box.id] = { height: Math.max(1, height), width: Math.max(1, width) }
      changed = true
    }
  }
  if (changed) measurements.value = next
}
function schedule() {
  if (disposed || queued) return
  queued = true
  nextTick(() => { queued = false; measure() })
}
function bodyRef(id: string, value: unknown) {
  const old = bodies.get(id)
  if (old && old !== value) observer?.unobserve(old)
  if (value && typeof value === 'object' && 'nodeType' in value) {
    const element = value as HTMLElement
    bodies.set(id, element)
    observer?.observe(element)
  } else bodies.delete(id)
}
watch(plan, () => {
  schedule()
  const report = { ...plan.value, items: undefined }
  const signature = JSON.stringify(report)
  // A parent can derive responsive item props from capacity. Emit only changed
  // public capacity values so equivalent rebuilt arrays cannot form a loop.
  if (signature !== emittedReport) { emittedReport = signature; emit('capacity', report) }
}, { deep: true, immediate: true })
onMounted(() => {
  if (typeof ResizeObserver !== 'undefined') {
    observer = new ResizeObserver(schedule)
    if (frame.value) observer.observe(frame.value)
    bodies.forEach(body => observer?.observe(body))
  }
  schedule()
  // Font readiness can change every native content height. Guard resolution
  // after unmount and keep ResizeObserver as the ongoing content-size owner.
  if (typeof document !== 'undefined' && document.fonts) {
    document.fonts.load('18px "Open Sans"').then(() => document.fonts.ready).then(schedule).catch(schedule)
  }
})
onBeforeUnmount(() => { disposed = true; observer?.disconnect(); bodies.clear() })
defineExpose({ report: plan, remeasure: schedule })
</script>

<template>
  <section
    ref="frame" class="slidev-dynamic-layout" role="region" :aria-label="label"
    tabindex="0" :style="rootStyle" :data-layout-mode="mode" :data-colorset="colorset"
    :data-page="plan.page" :data-pages="plan.pages" :data-layout-fits="String(plan.fits)"
    :data-required-width="plan.requiredWidth" :data-required-height="plan.requiredHeight"
    :data-configured-rows="plan.configuredRows" :data-configured-columns="plan.configuredColumns"
    :data-occupied-rows="plan.occupiedRows" :data-occupied-columns="plan.occupiedColumns"
  >
    <div class="layout-canvas" role="list" :style="{ width: `${Math.max(width, plan.requiredWidth)}px`, minHeight: `${Math.max(height, plan.requiredHeight)}px` }">
      <article
        v-for="box in plan.items" :key="box.id" class="layout-item" role="listitem"
        :style="itemStyle(box)" :data-item-id="box.id" :data-category-id="box.category"
        :data-row="box.row" :data-column="box.column" :data-fill="box.fill" :data-ink="box.ink"
        :aria-label="box.item.title || box.id"
      >
        <div :ref="value => bodyRef(box.id, value)" class="layout-item-content">
          <slot name="item" :item="box.item" :index="box.index" :color="{ fill: box.fill, ink: box.ink }" :style="slotStyle(box)" :box="box">
            <h3 v-if="box.item.title" class="layout-card-title">{{ box.item.title }}</h3>
            <p v-if="box.item.body" class="layout-card-body">{{ box.item.body }}</p>
            <span v-if="!box.item.title && !box.item.body">{{ box.id }}</span>
          </slot>
        </div>
      </article>
    </div>
    <div v-if="debug && !plan.fits" class="layout-capacity" role="status">
      Capacity exceeded: {{ plan.reasons.join(', ') }}. Increase pages or split the slide.
    </div>
  </section>
</template>

<style scoped>
.slidev-dynamic-layout {
  position: relative; width: 100%; box-sizing: border-box; overflow: auto;
  background: var(--layout-canvas); color: var(--layout-ink);
  font-size: 18px; line-height: 1.35;
}
.slidev-dynamic-layout:focus-visible { outline: 2px solid var(--layout-primary); outline-offset: 3px; }
.layout-canvas { position: relative; }
.layout-item {
  position: absolute; box-sizing: border-box; padding: 14px;
  overflow-wrap: anywhere; border-radius: 0; font: inherit;
}
.layout-item-content { font: inherit; color: inherit; }
.layout-card-title { margin: 0 0 8px; color: inherit; font-family: inherit; font-size: 20px; line-height: 1.2; font-weight: 700; }
.layout-card-body { margin: 0; color: inherit; opacity: 1; font-family: inherit; font-size: 18px; line-height: 1.35; }
.layout-capacity {
  position: sticky; left: 0; bottom: 0; padding: 8px 12px;
  background: var(--layout-quiet); color: var(--layout-ink); font-size: 16px;
}
</style>
