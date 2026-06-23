<template>
  <section ref="root" class="svg-asset-slide" :data-asset="spec.slug">
    <div class="svg-asset-header">
      <div>
        <p class="eyebrow">generated svg asset</p>
        <h2>{{ spec.title }}</h2>
      </div>
      <p>{{ spec.summary }}</p>
    </div>

    <div class="svg-asset-body">
      <div class="svg-asset-stage" :class="`stage-${spec.slug}`" v-html="svgMarkup"></div>
      <aside class="svg-asset-notes">
        <div>
          <h3>Source File</h3>
          <p>{{ spec.file }}</p>
        </div>
        <div>
          <h3>Anime.js APIs</h3>
          <p>{{ spec.api.join(', ') }}</p>
        </div>
        <div>
          <h3>Animation Hooks</h3>
          <p>{{ spec.selectors.join(', ') }}</p>
        </div>
        <div>
          <h3>Click Story</h3>
          <p>{{ spec.clickStory }}</p>
        </div>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { animate, createScope, createTimeline, stagger, svg } from 'animejs'
import { svgAssetSpec, svgAssetSvgs } from '../lib/svg-assets.js'

const props = defineProps({
  asset: {
    type: String,
    required: true,
  },
  step: {
    type: Number,
    default: 0,
  },
})

const root = ref(null)
const spec = computed(() => svgAssetSpec(props.asset))
const svgMarkup = computed(() => svgAssetSvgs[props.asset] || '')
const activeStep = computed(() => Math.min(Math.max(Number(props.step) || 0, 0), 2))

let scope = null

function cleanup() {
  if (scope) {
    scope.revert()
    scope = null
  }
}

function query(selector) {
  return root.value.querySelector(selector)
}

function queryAll(selector) {
  return Array.from(root.value.querySelectorAll(selector))
}

function drawables(selector) {
  return queryAll(selector).flatMap((line) => svg.createDrawable(line))
}

function runDrawableCircuit() {
  animate(drawables('.svg-drawable'), {
    draw: ['0 0', '0 1'],
    delay: stagger(120, {
      from: activeStep.value === 0 ? 'first' : activeStep.value === 1 ? 'center' : 'last',
    }),
    duration: 1800,
    ease: 'inOutQuad',
    loop: true,
    loopDelay: 280,
  })
  animate('.svg-node', {
    scale: [0.82, 1.18],
    opacity: [0.62, 1],
    transformOrigin: 'center',
    delay: stagger(80, { from: activeStep.value === 2 ? 'last' : 'first' }),
    duration: 760,
    ease: 'outBack(2)',
    loop: true,
    alternate: true,
  })
}

function runMotionOrbit() {
  const route = query('#orbit-path')
  const traveler = query('#orbit-traveler')
  animate(traveler, {
    ...svg.createMotionPath(route),
    duration: activeStep.value > 1 ? 2200 : 3000,
    ease: 'linear',
    loop: true,
  })
  animate(svg.createDrawable(route), {
    draw: ['0 0', '0 1'],
    duration: activeStep.value > 0 ? 2200 : 3000,
    ease: 'linear',
    loop: true,
  })
  animate('.orbit-ring', {
    rotate: activeStep.value === 1 ? '-1turn' : '1turn',
    transformOrigin: 'center',
    delay: stagger(90),
    duration: 3600,
    ease: 'linear',
    loop: true,
  })
  animate('.orbit-pulse', {
    scale: [0.7, 1.22],
    opacity: [0.42, 0.9],
    transformOrigin: 'center',
    delay: stagger(140),
    duration: 860,
    ease: 'inOutSine',
    loop: true,
    alternate: true,
  })
}

function runMorphingBadge() {
  const targets = ['#badge-target-diamond', '#badge-target-star', '#badge-target-wave']
  const fills = ['#45842a', '#007298', '#9e1b32']
  animate('#badge-source', {
    d: svg.morphTo(targets[activeStep.value], 0.65),
    fill: fills[activeStep.value],
    duration: 1500,
    ease: 'inOutExpo',
    loop: true,
    alternate: true,
  })
  animate('.badge-spark', {
    scale: [0.82, 1.22],
    opacity: [0.56, 1],
    transformOrigin: 'center',
    delay: stagger(70, { from: 'center' }),
    duration: 680,
    ease: 'outBack(2)',
    loop: true,
    alternate: true,
  })
}

function runStaggerDashboard() {
  animate('.dashboard-card', {
    y: [12, 0],
    opacity: [0.58, 1],
    delay: stagger(120, {
      from: activeStep.value === 0 ? 'first' : activeStep.value === 1 ? 'center' : 'last',
    }),
    duration: 900,
    ease: 'outExpo',
    loop: true,
    alternate: true,
  })
  animate('.dashboard-bar', {
    scaleX: [0.18, activeStep.value > 1 ? 1.08 : 0.92],
    transformOrigin: 'left center',
    delay: stagger(70),
    duration: 980,
    ease: 'inOutQuad',
    loop: true,
    alternate: true,
  })
  animate('.dashboard-dot', {
    scale: [0.78, 1.18],
    transformOrigin: 'center',
    delay: stagger(90),
    duration: 680,
    ease: 'outBack(2)',
    loop: true,
    alternate: true,
  })
}

function runTimelineMachine() {
  animate(drawables('.machine-cable'), {
    draw: ['0 0', '0 1'],
    delay: stagger(160),
    duration: 1700,
    ease: 'inOutQuad',
    loop: true,
  })
  createTimeline({
    defaults: { duration: 900, ease: 'outExpo' },
    loop: true,
    alternate: true,
  })
    .label('start')
    .add('.machine-gear', { rotate: '1turn', transformOrigin: 'center', duration: 1900, ease: 'linear' }, 'start')
    .add('.machine-block', { x: activeStep.value > 1 ? 286 : 214 }, 'start+=120')
    .add('.machine-signal', {
      scale: [0.72, 1.2],
      opacity: [0.4, 1],
      transformOrigin: 'center',
      delay: stagger(110),
    }, 'start+=240')
}

function runInteractiveHotspots() {
  const route = query('.map-route')
  animate(svg.createDrawable(route), {
    draw: ['0 0', '0 1'],
    duration: 1800,
    ease: 'inOutQuad',
    loop: true,
  })
  animate('.map-hotspot', {
    scale: [0.82, 1.22],
    opacity: [0.72, 1],
    transformOrigin: 'center',
    delay: stagger(120, {
      from: activeStep.value === 0 ? 'first' : activeStep.value === 1 ? 'center' : 'last',
    }),
    duration: 760,
    ease: 'outBack(2)',
    loop: true,
    alternate: true,
  })
  animate('.map-callout', {
    y: [10, 0],
    opacity: [0.58, 1],
    delay: stagger(130),
    duration: 860,
    ease: 'outExpo',
    loop: true,
    alternate: true,
  })
}

const runners = {
  'drawable-circuit': runDrawableCircuit,
  'motion-orbit': runMotionOrbit,
  'morphing-badge': runMorphingBadge,
  'stagger-dashboard': runStaggerDashboard,
  'timeline-machine': runTimelineMachine,
  'interactive-hotspots': runInteractiveHotspots,
}

async function start() {
  if (!root.value) return
  cleanup()
  await nextTick()
  scope = createScope({
    root: root.value,
    defaults: { duration: 900, ease: 'outExpo' },
  })
  scope.add(() => {
    runners[spec.value.slug]()
  })
}

onMounted(start)
onBeforeUnmount(cleanup)
watch(() => [props.asset, activeStep.value], start, { flush: 'post' })
</script>
