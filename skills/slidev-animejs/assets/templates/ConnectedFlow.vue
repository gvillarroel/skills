<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useId, watch } from 'vue'
import { animate, createScope, createTimeline } from 'animejs'

// Replaced by scaffold_connected_flow.py; keep the measured geometry/motion code.
const config = __FLOW_CONFIG__
const props = defineProps({ step: { type: [Number, String], default: 0 } })
const root = ref(null)
const nodes = ref([])
const routes = ref([])
const size = ref({ width: 600, height: 240 })
const ready = ref(false)
const status = ref('Complete handoff map')
const activeStep = computed(() => Math.min(2, Math.max(0, Number(props.step) || 0)))
const markerId = `flow-head-${config.id}-${useId()}`
let scope, media

async function measure() {
  await document.fonts.ready
  const probe = root.value.querySelector('.flow-probe')
  const widths = config.labels.map(label => {
    probe.textContent = label
    return Math.ceil(probe.getBBox().width + 20)
  })
  const h = Math.max(36, Math.ceil(probe.getBBox().height + 12))
  let x = 18
  const main = widths.map((w, i) => {
    const n = { id: `main-${i}`, label: config.labels[i], x, y: config.branch ? 118 : 18, w: Math.max(50, w), h }
    x += n.w + 48
    return n
  })
  const all = [...main], edges = []
  const add = (id, source, target, d, label = '', lx = 0, ly = 0, anchor = 'middle') => edges.push({ id, source, target, d, label, lx, ly, anchor })
  main.slice(0, -1).forEach((n, i) => {
    const t = main[i + 1]
    add(`main-${i}`, n.id, t.id, `M${n.x + n.w + 4},${n.y + h / 2} H${t.x - 7}`)
  })
  if (config.branch) {
    const n = main[config.branch.at], c = n.x + n.w / 2
    probe.textContent = config.branch.label
    const w = Math.max(50, Math.ceil(probe.getBBox().width + 20))
    const b = { id: 'branch', label: config.branch.label, x: c - w / 2, y: 18, w, h }
    all.push(b)
    add('branch-out', n.id, b.id, `M${c - 14},${n.y - 4} V${b.y + h + 7}`, config.branch.outLabel, c - 23, 91, 'end')
    add('branch-back', b.id, n.id, `M${c + 14},${b.y + h + 4} V${n.y - 7}`, config.branch.backLabel, c + 23, 91, 'start')
  }
  if (config.return) {
    const s = main[config.return.source], t = main[config.return.target]
    const sx = s.x + s.w / 2 - 14, tx = t.x + t.w / 2 + 14, lane = s.y + h + 40
    add('return', s.id, t.id, `M${sx},${s.y + h + 4} V${lane} H${tx} V${t.y + h + 7}`, config.return.label, (sx + tx) / 2, lane + 25)
  }
  nodes.value = all
  routes.value = edges
  await nextTick()
  const bbox = root.value.querySelector('.flow-content').getBBox()
  const shift = 18 - bbox.x
  root.value.querySelector('.flow-content').setAttribute('transform', `translate(${shift} 0)`)
  size.value = { width: Math.ceil(bbox.width + 36), height: Math.ceil(bbox.y + bbox.height + 18) }
  if (size.value.width > 850) throw new Error('Labels exceed the native readable slide width; use a separate subdiagram instead of shrinking text.')
  ready.value = true
  root.value.querySelector('.parcel').style.display = ''
  await nextTick()
  play()
}

function play() {
  if (!ready.value) return
  scope?.revert()
  scope = createScope({ root: root.value })
  const token = root.value.querySelector('.parcel')
  token.setAttribute('opacity', '0')
  token.removeAttribute('data-motion-route')
  const secondary = ['return', 'branch-out', 'branch-back'].filter(id => routes.value.some(r => r.id === id))
  status.value = activeStep.value === 0 ? 'Complete handoff map' : activeStep.value === 1 || !secondary.length ? 'Standard handoff' : 'Return and check'
  if (media.matches || activeStep.value === 0) return
  const ids = activeStep.value === 1
    ? routes.value.filter(r => r.id.startsWith('main-')).map(r => r.id)
    : secondary.length ? secondary : routes.value.filter(r => r.id.startsWith('main-')).map(r => r.id)
  scope.add(() => {
    const timeline = createTimeline({ defaults: { ease: 'linear' } })
    for (const id of ids) {
      const path = root.value.querySelector(`[data-route="${id}"]`)
      const length = path.getTotalLength(), progress = { distance: 8 }
      if (length < 30) throw new Error('Route is too short for a visible head and parcel clearance.')
      const update = () => {
        const p = path.getPointAtLength(progress.distance)
        token.setAttribute('transform', `translate(${p.x} ${p.y})`)
      }
      timeline.add(progress, {
        distance: [8, length - 18], duration: Math.max(600, length * 5),
        onBegin: () => { token.setAttribute('data-motion-route', id); token.setAttribute('opacity', '1'); update() },
        onUpdate: update,
        onComplete: () => token.setAttribute('opacity', '0'),
      })
    }
  })
}
onMounted(() => {
  media = matchMedia('(prefers-reduced-motion: reduce)')
  media.addEventListener('change', play)
  measure()
})
watch(activeStep, play, { flush: 'post' })
onBeforeUnmount(() => { scope?.revert(); media?.removeEventListener('change', play) })
</script>

<template>
  <section ref="root" class="connected-flow" :data-ready="ready" :data-click-state="activeStep" :data-palette="config.palette">
    <svg :viewBox="`0 0 ${size.width} ${size.height}`" :width="size.width" :height="size.height" role="img" :aria-label="config.title">
      <defs><marker :id="markerId" markerUnits="userSpaceOnUse" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="10" markerHeight="10" orient="auto"><path d="M0 0L10 5L0 10Z" :fill="config.ink" /></marker></defs>
      <text class="flow-probe" x="0" y="0" visibility="hidden">Measure</text>
      <g class="flow-content">
        <g fill="none" :stroke="config.ink" stroke-width="2.5" stroke-linejoin="round">
          <path v-for="r in routes" :key="r.id" :d="r.d" :data-route="r.id" :data-source="r.source" :data-target="r.target" :marker-end="`url(#${markerId})`" />
        </g>
        <g class="route-labels" :fill="config.ink"><g v-for="r in routes.filter(r => r.label)" :key="r.id" :transform="`translate(${r.lx} ${r.ly})`"><text x="0" y="0" :text-anchor="r.anchor">{{ r.label }}</text></g></g>
        <g v-for="n in nodes" :key="n.id" :data-node="n.id" class="flow-node" :transform="`translate(${n.x} ${n.y})`">
          <rect :width="n.w" :height="n.h" rx="4" :fill="config.fill" />
          <text :x="n.w / 2" :y="n.h / 2" text-anchor="middle" dominant-baseline="middle" :fill="config.text">{{ n.label }}</text>
        </g>
        <g class="parcel" style="display:none" opacity="0" :fill="config.accent" pointer-events="none"><rect x="-4" y="-3" width="8" height="6" rx="1" /></g>
      </g>
    </svg>
    <div class="flow-controls"><span aria-live="polite">{{ status }}</span><button type="button" @click="play">Replay</button></div>
  </section>
</template>

<style scoped>
.connected-flow { display: grid; justify-items: center; gap: 10px; width: fit-content; max-width: 100%; margin: 12px auto; font-family: 'Open Sans', Arial, sans-serif; }
.connected-flow svg { display: block; flex: none; overflow: visible; }
.flow-node text, .flow-probe { font-size: 18px; font-weight: 500; }
.route-labels text { font-size: 16px; }
.flow-controls { width: 100%; display: flex; justify-content: space-between; align-items: center; gap: 24px; font-size: 16px; }
.flow-controls button { padding: 3px 10px; border: 1px solid currentColor; border-radius: 4px; color: inherit; background: white; font: inherit; cursor: pointer; }
</style>
