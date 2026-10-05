<script setup lang="ts">
import { computed, h, onBeforeUnmount, onMounted, ref } from 'vue'
import HyperframePreview from './HyperframePreview.vue'
import SlidevCollection from './SlidevCollection.vue'
import { paletteFor } from '../lib/hyperframes.js'
import story from '../data/hyperframes-story.json'

const props = withDefaults(defineProps<{ variant?: 'hero' | 'cell' | 'export'; clicks?: number; columns?: number }>(),
  { variant: 'hero', clicks: 0, columns: undefined })
const root = ref<HTMLElement>()
const logicalWidth = ref(900)
const isCell = computed(() => props.variant === 'cell')
const colors = computed(() => paletteFor(story.colorset))
const style = computed(() => ({ color: colors.value.textOnFill[colors.value.roles.surface], background: colors.value.roles.surface }))
const items = [
  { id: 'mechanism', category: 'mechanism', title: 'Live mechanism' },
  { id: 'explanation', category: 'explanation', title: story.explanation.title, body: story.explanation.body },
]
const requestedColumns = computed(() => props.columns ?? story.compactLayout.columns)
const pageSize = computed(() => Math.min(2, requestedColumns.value,
  Math.max(1, Math.floor((logicalWidth.value + story.compactLayout.gap) / (story.compactLayout.minItemWidth + story.compactLayout.gap)))))
// One preview definition serves hero, cell and export; edit choreography in JSON.
const Scene = ({ height }: { height: number }) => h(HyperframePreview, {
  src: isCell.value ? story.compactComposition : story.composition,
  step: props.clicks, cueTimes: story.cueTimes, exportTime: story.exportTime,
  colorset: story.colorset, static: props.variant === 'export', height,
})
function cellHeight(box: { contentHeight: number }) {
  return Math.min(story.compactLayout.playerHeight, box.contentHeight - 48)
}
let observer: ResizeObserver | undefined
onMounted(() => {
  observer = new ResizeObserver(([entry]) => { logicalWidth.value = entry.contentRect.width })
  if (root.value) observer.observe(root.value)
})
onBeforeUnmount(() => observer?.disconnect())
</script>

<template>
  <section ref="root" class="hyperframe-story" :style="style" :data-story-variant="variant">
    <h1 class="story-heading">{{ story.titles[variant] }}</h1>
    <SlidevCollection v-if="isCell" :items="items" :category-order="items.map(item => item.category)"
      :colorset="story.colorset" :mode="story.compactLayout.mode" :columns="requestedColumns"
      :rows="1" :height="story.compactLayout.height" :gap="story.compactLayout.gap"
      :min-item-width="story.compactLayout.minItemWidth" :min-item-height="story.compactLayout.minItemHeight"
      :page-size="pageSize" label="Live composition and explanation">
      <template #item="{ item, box, color }">
        <Scene v-if="item.id === 'mechanism'" :height="cellHeight(box)" />
        <article v-else class="story-explanation" :style="{ color: color.ink }">
          <h2>{{ item.title }}</h2><p>{{ item.body }}</p>
        </article>
      </template>
    </SlidevCollection>
    <template v-else>
      <Scene :height="story.heroHeight" />
      <p v-if="variant === 'export'" class="story-export-note">Deterministic frame at {{ story.exportTime }} seconds</p>
    </template>
  </section>
</template>

<style scoped>
.hyperframe-story { width:100%; min-width:0; font-family:'Open Sans',sans-serif; }
.story-heading { margin:0 0 12px; color:inherit; font:700 28px/1.2 'Open Sans',sans-serif; opacity:1; }
.story-explanation h2 { margin:0 0 10px; color:inherit; font:700 16px/1.25 'Open Sans',sans-serif; opacity:1; }
.story-explanation p { margin:0; color:inherit; font:400 14px/1.4 'Open Sans',sans-serif; opacity:1; }
.story-export-note { margin:12px 0 0; color:inherit; font:400 14px/1.4 'Open Sans',sans-serif; opacity:1; }
</style>
