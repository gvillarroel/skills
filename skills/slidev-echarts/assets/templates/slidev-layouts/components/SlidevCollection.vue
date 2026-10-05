<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import SlidevLayout from './SlidevLayout.vue'
import { categoryPaints, extendCategoryOrder, layoutTheme, planSlideLayout, textOnFill } from '../lib/slidev-layouts.mjs'

interface CollectionItem {
  id: string
  category?: string
  title?: string
  body?: string
  width?: number
  [key: string]: unknown
}
type Mode = 'columns' | 'grid' | 'masonry-columns' | 'masonry-rows'
interface CollectionSlot {
  item: CollectionItem
  index: number
  color: { fill: string, ink: string }
  style: Record<string, string>
  box: { id: string, width: number, height: number, contentWidth: number, contentHeight: number, [key: string]: unknown }
}
const props = withDefaults(defineProps<{
  items: CollectionItem[]
  count?: number
  mode?: Mode
  columns?: number
  rows?: number
  colorset?: 'colorset1' | 'colorset2'
  categoryOrder?: string[]
  height?: number
  gap?: number
  minItemWidth?: number
  minItemHeight?: number
  pageSize?: number
  label?: string
}>(), {
  mode: 'grid', columns: 3, rows: 3, colorset: 'colorset1', height: 330,
  gap: 12, minItemWidth: 180, minItemHeight: 72, label: 'Slide collection',
})
const emit = defineEmits<{ capacity: [report: Record<string, unknown>] }>()
const slots = defineSlots<{ item(props: CollectionSlot): unknown }>()
const root = ref<HTMLElement>()
const layout = ref<InstanceType<typeof SlidevLayout>>()
const realWidth = ref(900)
const page = ref(1)
const budget = ref(1)
const report = ref<Record<string, any> | null>(null)
const qualified = ref(false)
const partitionFits = ref(true)
const identities = ref<string[]>([])
const itemOrder = ref<string[]>([])
const probes = new Map<string, HTMLElement>()
let observer: ResizeObserver | undefined
let disposed = false
let mounted = false
let qualificationVersion = 0
let publicSignature = ''
let lastCapacity: Record<string, any> | null = null

function integer(value: number, name: string, allowZero = false) {
  if (!Number.isInteger(value) || value < (allowZero ? 0 : 1))
    throw new RangeError(`${name} must be a ${allowZero ? 'nonnegative' : 'positive'} integer.`)
  return value
}
const activeCount = computed(() => Math.min(props.items.length, integer(props.count ?? props.items.length, 'count', true)))
const effectiveColumns = computed(() => {
  const requested = integer(props.columns, 'columns')
  const capacity = Math.max(1, Math.floor((realWidth.value + props.gap) / (props.minItemWidth + props.gap)))
  return Math.min(requested, capacity)
})
const desiredBudget = computed(() => integer(props.pageSize ?? (props.mode === 'masonry-rows'
  ? integer(props.rows, 'rows') : effectiveColumns.value * integer(props.rows, 'rows')), 'pageSize'))
watch(() => [props.items, props.categoryOrder] as const, () => {
  const previous = props.categoryOrder
    ? extendCategoryOrder(props.categoryOrder, identities.value.map(id => ({ id })))
    : identities.value
  identities.value = extendCategoryOrder(previous, props.items)
  const seen = new Set(itemOrder.value)
  for (const item of props.items) if (!seen.has(item.id)) { seen.add(item.id); itemOrder.value.push(item.id) }
  queueQualification()
}, { immediate: true, deep: true })
const activeItems = computed(() => props.items.slice(0, activeCount.value).map(item => {
  if (props.mode !== 'masonry-rows') return item
  const globalIndex = itemOrder.value.indexOf(item.id)
  const preferred = item.width ?? realWidth.value * [0.70, 0.82, 0.95][globalIndex % 3]
  if (!Number.isFinite(preferred) || preferred <= 0) throw new RangeError(`Item ${item.id} width must be positive.`)
  return { ...item, width: Math.min(realWidth.value, Math.max(props.minItemWidth, preferred)) }
}))
const pages = computed(() => Math.max(1, Math.ceil(activeCount.value / budget.value)))
const paints = computed(() => categoryPaints(props.items, { colorset: props.colorset, categoryOrder: identities.value }))
function probeWidth(item: CollectionItem) {
  const width = props.mode === 'masonry-rows' ? item.width as number
    : Math.max(props.minItemWidth, (realWidth.value - props.gap * (effectiveColumns.value - 1)) / effectiveColumns.value)
  const paint = paints.value.get(String(item.category ?? item.id))
  return Math.max(1, width - 28 - 2 * paint.borderWidth)
}
function probeRef(id: string, element: unknown) {
  if (element && typeof element === 'object' && 'nodeType' in element) probes.set(id, element as HTMLElement)
  else probes.delete(id)
}
async function qualify(version: number) {
  await nextTick()
  if (typeof document !== 'undefined' && document.fonts) {
    try { await document.fonts.load('14px "Open Sans"'); await document.fonts.ready } catch { /* The browser fallback still receives native measurement. */ }
  }
  await nextTick()
  if (disposed || version !== qualificationVersion) return
  if (!slots.item) {
    const measurements = Object.fromEntries(activeItems.value.map(item => {
      const element = probes.get(item.id)
      const paint = paints.value.get(String(item.category ?? item.id))
      return [item.id, { height: Math.max(1, element?.offsetHeight ?? 1) + 28 + 2 * paint.borderWidth }]
    }))
    const trackCapacity = props.mode === 'masonry-rows'
      ? props.rows * Math.max(1, Math.floor((realWidth.value + props.gap) / (props.minItemWidth + props.gap)))
      : effectiveColumns.value * Math.max(1, Math.floor((props.height + props.gap) / (props.minItemHeight + props.gap)))
    let candidate = Math.max(1, Math.min(budget.value, trackCapacity))
    let fits = false
    // Qualify one complete, stable partition before a user traverses it. Only
    // plaintext is duplicated here; arbitrary slot component lifecycles stay singular.
    while (candidate >= 1) {
      fits = true
      for (let current = 1; current <= Math.max(1, Math.ceil(activeCount.value / candidate)); current++) {
        const planned = planSlideLayout({ items: activeItems.value, mode: props.mode,
          columns: effectiveColumns.value, rows: props.rows, width: realWidth.value,
          height: props.height, gap: props.gap, minItemWidth: props.minItemWidth,
          minItemHeight: props.minItemHeight, colorset: props.colorset,
          categoryOrder: identities.value, measurements, page: current, pageSize: candidate })
        if (!planned.fits) { fits = false; break }
      }
      if (fits || candidate === 1) break
      candidate--
    }
    budget.value = candidate
    partitionFits.value = fits
  } else partitionFits.value = true
  page.value = 1
  qualified.value = true
  await nextTick()
  if (!disposed && version === qualificationVersion) {
    layout.value?.remeasure()
    await nextTick()
    await nextTick()
    if (!disposed && version === qualificationVersion && lastCapacity) receiveCapacity(lastCapacity)
  }
}
function queueQualification() {
  if (!mounted || disposed) return
  qualified.value = false
  void qualify(++qualificationVersion)
}
watch(() => [activeCount.value, props.mode, props.columns, props.rows, props.height, props.colorset,
  props.gap, props.minItemWidth, props.minItemHeight, props.pageSize, realWidth.value] as const, () => {
  budget.value = Math.max(1, Math.min(desiredBudget.value, activeCount.value || 1))
  page.value = 1
  queueQualification()
}, { immediate: true })
watch(pages, value => { page.value = Math.min(page.value, value) })
const theme = computed(() => layoutTheme(props.colorset))
const rootStyle = computed(() => ({
  '--collection-canvas': theme.value.canvas, '--collection-ink': theme.value.ink,
  '--collection-primary': theme.value.primary, '--collection-quiet': theme.value.quiet,
  '--collection-on-primary': textOnFill(theme.value.primary), fontFamily: theme.value.font,
}))
function receiveCapacity(value: Record<string, any>) {
  // Child cached widths/heights can be transient during a page or width change.
  // They report capacity, but never change an already qualified partition.
  lastCapacity = value
  report.value = { ...value, fits: value.fits && partitionFits.value }
  const publicReport = { ...report.value, partitionFits: partitionFits.value, qualified: qualified.value,
    collectionCount: activeCount.value,
    requestedColumns: props.columns, effectiveColumns: effectiveColumns.value,
    collectionPage: page.value, collectionPages: pages.value, collectionPageSize: budget.value }
  const signature = JSON.stringify(publicReport)
  if (signature !== publicSignature) { publicSignature = signature; emit('capacity', publicReport) }
}
function measureWidth() {
  if (disposed || !root.value) return
  const measured = root.value.clientWidth
  if (measured > 0 && Math.abs(measured - realWidth.value) > .5) realWidth.value = measured
}
function previousPage() { page.value = Math.max(1, page.value - 1) }
function nextPage() { page.value = Math.min(pages.value, page.value + 1) }
onMounted(() => {
  mounted = true
  measureWidth()
  if (typeof ResizeObserver !== 'undefined') { observer = new ResizeObserver(measureWidth); if (root.value) observer.observe(root.value) }
  if (typeof document !== 'undefined') document.fonts?.addEventListener('loadingdone', queueQualification)
  queueQualification()
})
onBeforeUnmount(() => {
  disposed = true; qualificationVersion++; observer?.disconnect(); probes.clear()
  if (typeof document !== 'undefined') document.fonts?.removeEventListener('loadingdone', queueQualification)
})
defineExpose({ page, pages, report, qualified, effectiveColumns, budget, previousPage, nextPage })
</script>

<template>
  <section
    ref="root" class="slidev-collection" :style="rootStyle" :aria-label="label"
    :data-collection-mode="mode" :data-colorset="colorset" :data-collection-count="activeCount"
    :data-collection-page="page" :data-collection-pages="pages" :data-collection-budget="budget"
    :data-collection-columns="effectiveColumns" :data-collection-width="realWidth"
    :data-collection-qualified="String(qualified)" :aria-busy="!qualified"
    :data-collection-fits="report ? String(report.fits) : 'pending'"
  >
    <SlidevLayout
      ref="layout" :items="activeItems" :mode="mode" :columns="effectiveColumns" :rows="rows"
      :colorset="colorset" :category-order="identities" :page="page" :page-size="budget"
      :height="height" :gap="gap" :min-item-width="minItemWidth" :min-item-height="minItemHeight"
      :label="label" @capacity="receiveCapacity"
      :style="{ visibility: qualified ? 'visible' : 'hidden' }"
    >
      <template #item="slotProps">
        <slot v-if="slots.item" name="item" v-bind="slotProps" />
        <div v-else class="collection-card" :style="{ color: slotProps.color.ink }">
          <h3 v-if="slotProps.item.title" class="collection-title">{{ slotProps.item.title }}</h3>
          <p v-if="slotProps.item.body" class="collection-body">{{ slotProps.item.body }}</p>
          <span v-if="!slotProps.item.title && !slotProps.item.body">{{ slotProps.item.id }}</span>
        </div>
      </template>
    </SlidevLayout>
    <nav class="collection-pager" aria-label="Collection pages" :style="{ visibility: qualified ? 'visible' : 'hidden' }">
      <button type="button" data-page-action="previous" aria-label="Previous page" :disabled="!qualified || page === 1" @click="previousPage">Previous page</button>
      <span aria-live="polite">Page {{ page }} of {{ pages }}</span>
      <button type="button" data-page-action="next" aria-label="Next page" :disabled="!qualified || page === pages" @click="nextPage">Next page</button>
    </nav>
    <div v-if="!slots.item" class="collection-probes" aria-hidden="true">
      <div v-for="item in activeItems" :key="item.id" :ref="element => probeRef(item.id, element)"
        class="collection-card" :style="{ width: `${probeWidth(item)}px` }" :data-measure-item-id="item.id">
        <h3 v-if="item.title" class="collection-title">{{ item.title }}</h3>
        <p v-if="item.body" class="collection-body">{{ item.body }}</p>
        <span v-if="!item.title && !item.body">{{ item.id }}</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.slidev-collection { width: 100%; color: var(--collection-ink); background: var(--collection-canvas); }
.collection-card { font-family: inherit; font-size: 14px; line-height: 1.4; opacity: 1; overflow-wrap: anywhere; white-space: normal; }
.collection-title { margin: 0 0 6px; color: inherit; font-family: inherit; font-size: 16px; line-height: 1.2; font-weight: 700; opacity: 1; }
.collection-body { margin: 0; color: inherit; font-family: inherit; font-size: 14px; line-height: 1.4; opacity: 1; }
.collection-pager { display: flex; align-items: center; justify-content: space-between; gap: 12px; height: 32px; margin-top: 4px; color: var(--collection-ink); font-size: 14px; line-height: 1.2; }
.collection-pager button { margin: 0; padding: 6px 12px; border: 0; border-radius: 0; font: inherit; color: var(--collection-on-primary); background: var(--collection-primary); cursor: pointer; opacity: 1; }
.collection-pager button:disabled { color: var(--collection-ink); background: var(--collection-quiet); cursor: default; opacity: 1; }
.collection-pager button:focus-visible { outline: 2px solid var(--collection-ink); outline-offset: 2px; }
.collection-probes { position: absolute; left: -100000px; top: 0; visibility: hidden; pointer-events: none; }
</style>
