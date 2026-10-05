<template>
  <section
    ref="rootElement"
    class="hyperframes-example"
    :id="patternId"
    :data-example-id="patternSlug"
    :data-pattern-id="patternId"
    data-pattern-page="true"
    data-colorset="colorset1"
    :data-hyperframes-variant="variant"
    :data-cue-index="cueIndex"
    :data-cue-time="cueTimes[cueIndex]"
    :data-layout-choice="layoutMode"
    :data-readable-columns="readableColumns"
    :style="chromeStyle"
  >
    <div v-if="variant !== 'export'" class="hyperframes-controls">
      <div class="hyperframes-control-group" role="group" aria-label="Scene time cues">
        <span>Scene time</span>
        <button v-for="(time, index) in cueTimes" :key="time" type="button" :data-hyperframes-cue="index" :aria-pressed="cueIndex === index" @click="cueOverride = index">{{ time }} s</button>
      </div>
      <div v-if="variant === 'cells'" class="hyperframes-control-group" role="group" aria-label="Collection layout">
        <button type="button" data-hyperframes-layout="columns" :aria-pressed="layoutMode === 'columns'" @click="layoutMode = 'columns'">Columns</button>
        <button type="button" data-hyperframes-layout="masonry-columns" :aria-pressed="layoutMode === 'masonry-columns'" @click="layoutMode = 'masonry-columns'">Masonry</button>
      </div>
    </div>

    <div v-if="variant === 'live'" class="hyperframes-live-stage">
      <HyperframePreview :step="cueIndex" :cue-times="cueTimes" :height="282" label="An inlet valve controls transport into an accumulating tank" />
    </div>

    <SlidevCollection
      v-else-if="variant === 'cells'"
      :items="collectionItems"
      :mode="layoutMode"
      :columns="readableColumns"
      :rows="1"
      :page-size="readableColumns"
      :category-order="collectionItems.map(item => item.id)"
      :min-item-width="330"
      :height="330"
      :gap="12"
      label="A live mechanism and its explanatory components"
    >
      <template #item="{ item }">
        <div class="hyperframes-card-content" :data-hyperframes-card="item.id">
          <strong class="hyperframes-card-title">{{ item.title }}</strong>
          <template v-if="item.id === 'mechanism'">
            <HyperframePreview src="hyperframes/starter.html?compact=1" :step="cueIndex" :cue-times="cueTimes" :height="162" label="Compact inlet valve, connected transport and tank level" />
            <p class="hyperframes-card-caption">Incoming flow raises the stored volume.</p>
          </template>
          <template v-else-if="item.id === 'relationships'">
            <dl class="hyperframes-relations">
              <div><dt>Valve</dt><dd>Controls incoming flow</dd></div>
              <div><dt>Transport</dt><dd>Connects inlet and tank</dd></div>
              <div><dt>Tank</dt><dd>Accumulates the input</dd></div>
            </dl>
          </template>
          <p v-else class="hyperframes-card-copy">This illustrative inlet has no outflow. The valve, transport and tank share one seekable clock.</p>
        </div>
      </template>
    </SlidevCollection>

    <SlidevCollection
      v-else
      :items="exportItems"
      mode="columns"
      :columns="readableColumns"
      :rows="1"
      :page-size="readableColumns"
      :category-order="exportItems.map(item => item.id)"
      :min-item-width="330"
      :height="330"
      :gap="12"
      label="Deterministic initial and final inlet snapshots"
    >
      <template #item="{ item }">
        <div class="hyperframes-card-content" :data-hyperframes-export="item.id">
          <strong class="hyperframes-card-title">{{ item.title }}</strong>
          <HyperframeSlide src="hyperframes/starter.html?compact=1" :static="true" :export-time="item.time" :height="210" :label="item.label" />
          <p class="hyperframes-card-caption">{{ item.caption }}</p>
        </div>
      </template>
    </SlidevCollection>

    <p class="hyperframes-context">{{ context }}</p>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import HyperframeSlide from '../../../templates/slidev-hyperframes/components/HyperframeSlide.vue'
import HyperframePreview from '../../../templates/slidev-hyperframes/components/HyperframePreview.vue'
import SlidevCollection from '../../../templates/slidev-layouts/components/SlidevCollection.vue'
import { layoutTheme } from '../../../templates/slidev-layouts/lib/slidev-layouts.mjs'

const props = defineProps({
  variant: { type: String, default: 'live' },
  namespace: { type: String, required: true },
  step: { type: Number, default: 0 },
})
const cueTimes = [0, 3, 6, 9]
const cueOverride = ref(null)
const cueIndex = computed(() => Math.max(0, Math.min(cueTimes.length - 1, Math.floor(cueOverride.value ?? props.step))))
const layoutMode = ref('columns')
const rootElement = ref(null)
const actualWidth = ref(885)
const readableColumns = computed(() => Math.max(1, Math.min(2, Math.floor((actualWidth.value + 12) / 342))))
let resizeObserver
onMounted(() => {
  const measure = () => { actualWidth.value = rootElement.value?.clientWidth || 885 }
  measure()
  resizeObserver = new ResizeObserver(measure)
  resizeObserver.observe(rootElement.value)
})
onBeforeUnmount(() => resizeObserver?.disconnect())
watch(() => props.step, () => { cueOverride.value = null })
const patternSlug = computed(() => props.variant === 'live' ? 'hyperframes' : 'hyperframes-' + props.variant)
const patternId = computed(() => props.namespace + '-' + patternSlug.value)
const theme = layoutTheme()
const chromeStyle = {
  '--hf-example-canvas': theme.canvas,
  '--hf-example-ink': theme.ink,
  '--hf-example-primary': theme.primary,
  '--hf-example-quiet': theme.quiet,
  '--hf-example-line': theme.line,
  fontFamily: theme.font,
}
const collectionItems = [
  { id: 'mechanism', title: 'Valve, transport and tank' },
  { id: 'relationships', title: 'Read the mechanism' },
  { id: 'assumptions', title: 'Illustrative model' },
]
const exportItems = [
  { id: 'closed', title: '0 s · Valve closed', time: 0, label: 'Initial inlet state with the valve closed and no accumulated volume', caption: 'No incoming transport; empty tank.' },
  { id: 'open', title: '9 s · Valve open', time: 9, label: 'Later inlet state with open valve, incoming transport and accumulated tank volume', caption: 'Incoming transport; accumulated volume.' },
]
const context = computed(() => props.variant === 'export'
  ? 'Static snapshots preserve the requested time, palette and mechanism.'
  : props.variant === 'cells'
    ? 'Two readable columns become one at narrow widths; every component remains reachable.'
    : 'Opening the valve starts transport; incoming flow accumulates in the tank.')
</script>

<style scoped>
.hyperframes-example { width: 100%; color: var(--hf-example-ink); font-family: "Open Sans", Arial, sans-serif; }
.hyperframes-controls { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 0 0 12px; min-height: 28px; }
.hyperframes-control-group { display: flex; align-items: center; gap: 6px; }
.hyperframes-control-group > span { margin-right: 4px; font-size: 12px; }
.hyperframes-controls button { display: inline-flex; align-items: center; justify-content: center; min-height: 28px; padding: 4px 10px; border: 0; background: var(--hf-example-quiet); color: var(--hf-example-ink); font: 600 12px/20px "Open Sans", Arial, sans-serif; cursor: pointer; }
.hyperframes-controls button[aria-pressed="true"] { background: var(--hf-example-primary); color: #ffffff; }
.hyperframes-controls button:focus-visible { outline: 2px solid var(--hf-example-line); outline-offset: 3px; }
.hyperframes-live-stage { background: var(--hf-example-canvas); }
.hyperframes-card-content { color: inherit; font-family: "Open Sans", Arial, sans-serif; }
.hyperframes-card-title { display: block; margin: 0 0 8px; font: 600 16px/22px "Open Sans", Arial, sans-serif; color: inherit; }
.hyperframes-card-caption { margin: 8px 0 0; font: 400 14px/20px "Open Sans", Arial, sans-serif; color: inherit; }
.hyperframes-card-copy { margin: 0; font: 400 14px/22px "Open Sans", Arial, sans-serif; color: inherit; }
.hyperframes-relations { margin: 4px 0 0; font: 400 14px/22px "Open Sans", Arial, sans-serif; }
.hyperframes-relations > div { margin-bottom: 10px; }
.hyperframes-relations dt { font-weight: 600; }
.hyperframes-relations dd { margin: 0; }
.hyperframes-context { margin: 10px 0 0; font: 400 12px/18px "Open Sans", Arial, sans-serif; color: var(--hf-example-ink); }
</style>
