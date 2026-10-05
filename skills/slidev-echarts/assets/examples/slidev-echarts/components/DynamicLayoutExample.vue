<template>
  <section
    class="dynamic-layout-example"
    :id="patternId"
    :data-example-id="patternSlug"
    :data-pattern-id="patternId"
    data-pattern-page="true"
    :data-colorset="colorset"
    :data-count="itemCount"
    :data-columns="columns"
    :data-page="page"
    :data-pages="pages"
    :data-order="reversed ? 'reversed' : 'source'"
    :style="chromeStyle"
  >
    <div class="layout-demo-controls" aria-label="Dynamic layout settings">
      <div class="layout-demo-control-group" role="group" aria-label="Number of components">
        <span>Components</span>
        <button v-for="count in [3, 7, 11]" :key="count" type="button" :data-layout-control="'items-' + count" :aria-pressed="itemCount === count" @click="setCount(count)">{{ count }}</button>
      </div>
      <div v-if="mode !== 'masonry-rows'" class="layout-demo-control-group" role="group" aria-label="Number of columns">
        <span>Columns</span>
        <button v-for="count in [2, 3, 4]" :key="count" type="button" :data-layout-control="'columns-' + count" :aria-pressed="columns === count" @click="setColumns(count)">{{ count }}</button>
      </div>
      <span v-else class="layout-demo-fixed-rows">3 rows · variable widths</span>
      <button type="button" data-layout-control="reverse" :aria-pressed="reversed" @click="reversed = !reversed">Reverse order</button>
    </div>

    <SlidevLayout
      :items="items"
      :mode="mode"
      :columns="columns"
      :rows="mode === 'grid' ? 2 : 3"
      :colorset="colorset"
      :category-order="categoryOrder"
      :page="page"
      :page-size="pageSize"
      :height="330"
      :gap="12"
      :min-item-width="140"
      :min-item-height="mode === 'masonry-columns' ? 72 : 96"
      :label="layoutLabel"
      @capacity="capacity = $event"
    >
      <template #item="{ item }">
        <div class="layout-demo-card-content">
          <strong class="layout-demo-card-title">{{ item.title }}</strong>
          <p class="layout-demo-card-body">{{ item.body }}</p>
          <svg v-if="mode === 'grid'" class="layout-demo-metric" viewBox="0 0 180 14" role="img" :aria-label="item.metric + ' percent complete'">
            <path d="M 0 7 H 180" fill="none" stroke="currentColor" stroke-width="2" />
            <path :d="'M 0 7 H ' + item.metric * 1.8" fill="none" stroke="currentColor" stroke-width="6" />
          </svg>
        </div>
      </template>
    </SlidevLayout>

    <div class="layout-demo-pagination">
      <span aria-live="polite">{{ itemCount }} components · {{ mode === 'masonry-rows' ? '3 rows' : columns + ' columns' }} · {{ colorset }}</span>
      <div class="layout-demo-page-controls" role="group" aria-label="Layout pages">
        <button type="button" data-layout-control="page-previous" :disabled="page === 1" @click="page--">Previous</button>
        <span>Page {{ page }} of {{ pages }}</span>
        <button type="button" data-layout-control="page-next" :disabled="page === pages" @click="page++">Next</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import SlidevLayout from '../../../templates/slidev-layouts/components/SlidevLayout.vue'
import { layoutTheme } from '../../../templates/slidev-layouts/lib/slidev-layouts.mjs'

const props = defineProps({
  mode: { type: String, required: true },
  namespace: { type: String, required: true },
  colorset: { type: String, default: 'colorset1' },
})

const columns = ref(3)
const itemCount = ref(7)
const page = ref(1)
const reversed = ref(false)
const capacity = ref(null)
const catalog = [
  { id: 'plan', title: 'Plan', body: 'Set the next outcome.', detail: 'Set the next outcome and agree on clear evidence of progress.', width: 180, metric: 74 },
  { id: 'research', title: 'Research', body: 'Collect useful evidence.', detail: 'Collect useful evidence from interviews, source documents, and observed behavior.', width: 225, metric: 58 },
  { id: 'design', title: 'Design', body: 'Make the idea concrete.', detail: 'Build a small prototype.', width: 160, metric: 82 },
  { id: 'build', title: 'Build', body: 'Ship a working increment.', detail: 'Ship a working increment, keep the scope focused, and record the decisions behind the implementation.', width: 220, metric: 63 },
  { id: 'measure', title: 'Measure', body: 'Track the same metric.', detail: 'Track the same metric before and after the change.', width: 185, metric: 91 },
  { id: 'review', title: 'Review', body: 'Check facts and usability.', detail: 'Review facts and usability, then resolve the remaining questions.', width: 205, metric: 67 },
  { id: 'release', title: 'Release', body: 'Publish the approved work.', detail: 'Publish the approved work and document the next step.', width: 230, metric: 88 },
  { id: 'support', title: 'Support', body: 'Answer the next question.', detail: 'Answer the next question with a reusable explanation.', width: 165, metric: 79 },
  { id: 'learn', title: 'Learn', body: 'Promote what worked.', detail: 'Promote what worked into a repeatable practice and retain the evidence.', width: 190, metric: 55 },
  { id: 'improve', title: 'Improve', body: 'Refine the next iteration.', detail: 'Refine the next iteration using observations from the last release.', width: 210, metric: 72 },
  { id: 'share', title: 'Share', body: 'Make the result discoverable.', detail: 'Make the result discoverable for the next person who needs it.', width: 180, metric: 84 },
]
const categoryOrder = catalog.map(item => item.id)
const items = computed(() => {
  const selected = catalog.slice(0, itemCount.value).map(item => ({ ...item, category: item.id, body: props.mode === 'masonry-columns' ? item.detail : item.body }))
  return reversed.value ? selected.reverse() : selected
})
const pageSize = computed(() => props.mode === 'masonry-rows' ? 9 : props.mode === 'grid' ? columns.value * 2 : props.mode === 'masonry-columns' ? Math.min(6, columns.value * 2) : columns.value * 3)
const pages = computed(() => Math.max(1, Math.ceil(itemCount.value / pageSize.value)))
const patternSlug = computed(() => ({ columns: 'dynamic-columns', grid: 'dynamic-grid' }[props.mode] || props.mode))
const patternId = computed(() => props.namespace + '-' + patternSlug.value)
const layoutLabel = computed(() => ({ columns: 'Dynamic column composition', grid: 'Dynamic component grid', 'masonry-rows': 'Components packed into three horizontal rows', 'masonry-columns': 'Variable-height components packed into columns' }[props.mode]))
const chromeStyle = computed(() => {
  const theme = layoutTheme(props.colorset)
  return { '--demo-canvas': theme.canvas, '--demo-ink': theme.ink, '--demo-primary': theme.primary, '--demo-quiet': theme.quiet, fontFamily: theme.font }
})
watch(pages, value => { page.value = Math.min(page.value, value) })
function setCount(value) { itemCount.value = value; page.value = 1 }
function setColumns(value) { columns.value = value; page.value = 1 }
</script>

<style scoped>
.dynamic-layout-example {
  color: var(--demo-ink);
  width: 100%;
  min-width: 0;
}
.layout-demo-controls, .layout-demo-control-group, .layout-demo-pagination, .layout-demo-page-controls {
  align-items: center;
  display: flex;
  gap: 7px;
}
.layout-demo-controls {
  flex-wrap: wrap;
  justify-content: space-between;
  margin: 0 0 12px;
}
.layout-demo-control-group, .layout-demo-fixed-rows { font-size: 13px; }
.layout-demo-control-group > span { margin-right: 3px; }
.dynamic-layout-example button {
  background: var(--demo-quiet);
  border: 0;
  border-radius: 0;
  color: var(--demo-ink);
  font-family: inherit;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.2;
  padding: 7px 10px;
}
.dynamic-layout-example button[aria-pressed="true"] {
  background: var(--demo-primary);
  color: var(--demo-canvas);
}
.dynamic-layout-example button:focus-visible { outline: 2px solid var(--demo-primary); outline-offset: 2px; }
.dynamic-layout-example button:disabled { opacity: 0.45; }
.layout-demo-card-content { color: inherit; display: grid; gap: 5px; }
.layout-demo-card-title { color: inherit; display: block; font-size: 16px; line-height: 1.2; }
.layout-demo-card-body { color: inherit !important; font-size: 14px; line-height: 1.4; margin: 0; }
.layout-demo-metric { color: inherit; display: block; height: 14px; margin-top: 3px; width: 100%; }
.layout-demo-pagination { font-size: 12px; justify-content: space-between; margin-top: 12px; }
.layout-demo-page-controls > span { min-width: 78px; text-align: center; }
</style>
