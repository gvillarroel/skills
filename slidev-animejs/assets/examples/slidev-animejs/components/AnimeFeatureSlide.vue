<template>
  <section ref="root" class="anime-feature-slide" :data-feature="spec.type">
    <div class="anime-feature-header">
      <div>
        <p class="eyebrow">{{ spec.type }}</p>
        <h2>{{ spec.title }}</h2>
      </div>
      <p>{{ spec.summary }}</p>
    </div>

    <div class="anime-feature-body">
      <div class="anime-stage" :class="`stage-${spec.type}`">
        <template v-if="spec.type === 'css-transforms'">
          <div class="css-rail">
            <div class="css-card">
              <strong>Scoped card</strong>
              <span>Transform, opacity</span>
            </div>
            <span v-for="item in 5" :key="item" class="css-dot"></span>
          </div>
        </template>

        <template v-else-if="spec.type === 'css-properties-colors'">
          <div class="property-demo">
            <div class="property-panel">
              <strong>Property tween</strong>
              <span>width, radius, color, variable</span>
            </div>
          </div>
        </template>

        <template v-else-if="spec.type === 'keyframes-relative-values'">
          <div class="keyframe-track">
            <span class="track-line"></span>
            <div class="key-ball"></div>
            <div class="key-labels">
              <span>from</span>
              <span>overshoot</span>
              <span>relative</span>
            </div>
          </div>
        </template>

        <template v-else-if="spec.type === 'js-object-values'">
          <div class="value-demo">
            <div class="value-number" ref="valueNumber">0</div>
            <div class="value-meter"><span ref="valueMeter"></span></div>
          </div>
        </template>

        <template v-else-if="spec.type === 'stagger-sequences'">
          <div class="stagger-grid">
            <span v-for="item in 16" :key="item" class="stagger-cell">{{ item }}</span>
          </div>
        </template>

        <template v-else-if="spec.type === 'timeline-sequencing'">
          <div class="timeline-stack">
            <div class="timeline-mark timeline-square"></div>
            <div class="timeline-mark timeline-circle"></div>
            <div class="timeline-mark timeline-triangle"></div>
          </div>
        </template>

        <template v-else-if="spec.type === 'playback-controls'">
          <div class="playback-demo">
            <div class="playback-line"></div>
            <div class="playback-marker"></div>
            <div class="playback-status" ref="playbackStatus">paused at start</div>
          </div>
        </template>

        <template v-else-if="spec.type === 'timers'">
          <div class="timer-demo">
            <svg viewBox="0 0 180 180" class="timer-dial">
              <circle cx="90" cy="90" r="68" />
              <path ref="timerArc" d="M90 22 A68 68 0 1 1 89.9 22" />
            </svg>
            <div class="timer-readout" ref="timerReadout">0 ms</div>
          </div>
        </template>

        <template v-else-if="spec.type === 'animatable-live-input'">
          <div class="live-zone" @pointermove="handlePointerMove">
            <div class="live-target"></div>
            <div class="live-caption">move pointer or advance clicks</div>
          </div>
        </template>

        <template v-else-if="spec.type === 'easings-springs'">
          <div class="ease-demo">
            <div v-for="label in ['outExpo', 'cubicBezier', 'steps', 'spring']" :key="label" class="ease-row">
              <span>{{ label }}</span>
              <i :class="`ease-dot ease-${label}`"></i>
            </div>
          </div>
        </template>

        <template v-else-if="spec.type === 'svg-drawable'">
          <svg class="svg-demo" viewBox="0 0 520 260" role="img" aria-label="Drawable route">
            <path class="draw-line" d="M46 198 C120 60 190 60 256 150" />
            <path class="draw-line accent" d="M256 150 C310 218 390 212 474 86" />
            <path class="draw-line warm" d="M78 218 C172 184 254 224 388 168" />
          </svg>
        </template>

        <template v-else-if="spec.type === 'svg-motion-path'">
          <svg class="svg-demo" viewBox="0 0 520 260" role="img" aria-label="Motion path">
            <path class="motion-path" d="M52 202 C94 58 172 58 232 130 S354 222 464 72" />
            <g class="motion-dot">
              <circle r="14" />
              <path d="M-6 -5 L8 0 L-6 5 Z" />
            </g>
          </svg>
        </template>

        <template v-else-if="spec.type === 'svg-morph'">
          <svg class="svg-demo morph-demo" viewBox="0 0 520 260" role="img" aria-label="Morphing shape">
            <path
              class="morph-source"
              d="M106 138 C104 76 176 42 248 66 C324 92 400 54 430 116 C462 184 392 224 310 202 C238 182 114 220 106 138 Z"
            />
            <path
              class="morph-target"
              d="M92 126 C158 50 226 124 272 58 C332 108 430 74 442 164 C352 152 354 240 250 208 C176 252 150 168 92 126 Z"
            />
          </svg>
        </template>

        <template v-else-if="spec.type === 'text-split'">
          <div class="text-stage">
            <h3 class="split-heading" data-allow-overflow>Motion gives order to attention</h3>
          </div>
        </template>

        <template v-else-if="spec.type === 'text-scramble'">
          <div class="text-stage">
            <p class="scramble-label">decoded slide state</p>
            <h3 class="scramble-heading">Motion that tells the story</h3>
          </div>
        </template>

        <template v-else-if="spec.type === 'layout-transitions'">
          <div class="layout-grid" :class="{ 'is-row': activeStep > 0 }">
            <span v-for="item in layoutItems" :key="item">{{ item }}</span>
          </div>
        </template>

        <template v-else-if="spec.type === 'draggable-interactions'">
          <div class="drag-zone">
            <div class="drag-card">Drag or inspect</div>
          </div>
        </template>

        <template v-else-if="spec.type === 'scroll-observer'">
          <div class="scroll-stage">
            <div class="scroll-panel">
              <div class="scroll-filler">Scroll lane</div>
              <div class="scroll-card">Synchronized</div>
              <div class="scroll-filler tail">End state</div>
            </div>
          </div>
        </template>

        <template v-else-if="spec.type === 'scope-media-cleanup'">
          <div class="scope-demo">
            <span v-for="item in 4" :key="item" class="scope-mark">{{ item }}</span>
          </div>
        </template>

        <template v-else-if="spec.type === 'waapi-animations'">
          <div class="waapi-row">
            <span v-for="item in ['Fast', 'Small', 'Smooth']" :key="item" class="waapi-pill">{{ item }}</span>
          </div>
        </template>

        <template v-else-if="spec.type === 'engine-controls'">
          <div class="engine-demo">
            <div class="engine-track"></div>
            <div class="engine-marker"></div>
            <div class="engine-status" ref="engineStatus">engine speed: 1</div>
          </div>
        </template>
      </div>

      <aside class="anime-feature-notes">
        <div>
          <h3>APIs</h3>
          <p>{{ spec.api.join(', ') }}</p>
        </div>
        <div>
          <h3>Fixture</h3>
          <p>{{ spec.slideTest }}</p>
        </div>
        <div>
          <h3>Reference</h3>
          <p>{{ spec.reference }}</p>
        </div>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import {
  animate,
  createAnimatable,
  createDraggable,
  createLayout,
  createScope,
  createTimer,
  createTimeline,
  cubicBezier,
  engine,
  onScroll,
  scrambleText,
  splitText,
  spring,
  stagger,
  steps,
  svg,
  waapi,
} from 'animejs'
import { featureSpec } from '../lib/anime-demos.js'

const props = defineProps({
  feature: {
    type: String,
    required: true,
  },
  step: {
    type: Number,
    default: 0,
  },
})

const root = ref(null)
const valueNumber = ref(null)
const valueMeter = ref(null)
const timerArc = ref(null)
const timerReadout = ref(null)
const playbackStatus = ref(null)
const engineStatus = ref(null)
const layoutItems = ref(['Plan', 'Build', 'Test', 'Ship'])

const spec = computed(() => featureSpec(props.feature))
const activeStep = computed(() => Math.min(Math.max(Number(props.step) || 0, 0), 2))

let scope = null
let cleanupHandlers = []
let liveAnimatable = null
let previousEngineSpeed = 1

function addCleanup(handler) {
  cleanupHandlers.push(handler)
}

function cleanup() {
  cleanupHandlers.forEach((handler) => handler())
  cleanupHandlers = []
  if (scope) {
    scope.revert()
    scope = null
  }
  liveAnimatable = null
}

function query(selector) {
  return root.value.querySelector(selector)
}

function queryAll(selector) {
  return Array.from(root.value.querySelectorAll(selector))
}

function handlePointerMove(event) {
  if (!liveAnimatable || spec.value.type !== 'animatable-live-input') return
  const bounds = query('.live-zone').getBoundingClientRect()
  liveAnimatable.x(event.clientX - bounds.left - bounds.width / 2)
  liveAnimatable.y(event.clientY - bounds.top - bounds.height / 2)
}

function runCssTransforms() {
  animate('.css-card', {
    x: [0, 148],
    rotate: '1turn',
    scale: [0.94, 1.06],
    opacity: [0.75, 1],
    duration: 1800,
    ease: 'inOutSine',
    loop: true,
    alternate: true,
  })
  animate('.css-dot', {
    y: [18, -18],
    opacity: [0.35, 1],
    scale: [0.65, 1.2],
    delay: stagger(90),
    duration: 900,
    ease: 'outBack(2)',
    loop: true,
    alternate: true,
  })
}

function runCssPropertiesColors() {
  animate('.property-panel', {
    width: ['160px', `${250 + activeStep.value * 30}px`],
    borderRadius: ['8px', '34px'],
    backgroundColor: ['#cdf3ff', activeStep.value > 1 ? '#ffccd5' : '#dbffcc'],
    '--accent-size': ['16px', `${42 + activeStep.value * 8}px`],
    duration: 1400,
    ease: 'inOutQuad',
    loop: true,
    alternate: true,
  })
}

function runKeyframesRelativeValues() {
  animate('.key-ball', {
    x: [
      { from: 0, to: 114 + activeStep.value * 12, duration: 420, ease: 'outQuad' },
      { to: 72, duration: 280, ease: 'inOutQuad' },
      { to: '+=140', duration: 620, ease: 'outElastic(1, .7)' },
    ],
    y: [
      { to: -54, duration: 420, ease: 'outQuad' },
      { to: 18, duration: 280, ease: 'inQuad' },
      { to: 0, duration: 620, ease: 'outBounce' },
    ],
    backgroundColor: ['#45842a', '#007298', '#9e1b32'],
    loop: true,
    alternate: true,
  })
}

function runObjectValues() {
  const state = {
    score: 18,
    width: 22,
  }
  const targetScore = 72 + activeStep.value * 8
  const targetWidth = 62 + activeStep.value * 11

  animate(state, {
    score: targetScore,
    width: targetWidth,
    duration: 1500,
    ease: 'outCubic',
    loop: true,
    alternate: true,
    onUpdate: () => {
      if (valueNumber.value) valueNumber.value.textContent = Math.round(state.score).toString()
      if (valueMeter.value) valueMeter.value.style.width = `${Math.round(state.width)}%`
    },
  })
}

function runStaggerSequences() {
  animate('.stagger-cell', {
    y: [-14, 18],
    scale: [0.82, 1.12],
    backgroundColor: ['#cdf3ff', '#dbffcc'],
    delay: stagger(65, {
      grid: [4, 4],
      from: activeStep.value === 0 ? 'first' : activeStep.value === 1 ? 'center' : 'last',
    }),
    duration: 820,
    ease: 'inOutQuad',
    loop: true,
    alternate: true,
  })
}

function runTimelineSequencing() {
  createTimeline({
    defaults: { duration: 760, ease: 'outExpo' },
    loop: true,
    alternate: true,
  })
    .label('start')
    .add('.timeline-square', { x: 156, rotate: 90 }, 'start')
    .add('.timeline-circle', { x: 156, scale: 1.35 }, '<+=120')
    .add('.timeline-triangle', { x: 156, rotate: '1turn' }, '<+=120')
    .call(() => {}, '<+=120')
}

function runPlaybackControls() {
  const animation = animate('.playback-marker', {
    x: 270,
    rotate: '1turn',
    duration: 2200,
    ease: 'inOutSine',
    autoplay: false,
  })
  if (activeStep.value === 0) {
    animation.seek(0)
    animation.pause()
    playbackStatus.value.textContent = 'pause() at start'
  } else if (activeStep.value === 1) {
    animation.seek(1100)
    animation.pause()
    playbackStatus.value.textContent = 'seek() to midpoint'
  } else {
    animation.reverse()
    animation.restart()
    playbackStatus.value.textContent = 'reverse() then restart()'
  }
  addCleanup(() => animation.revert())
}

function arcPath(progress) {
  const angle = -90 + progress * 359.99
  const radians = (angle * Math.PI) / 180
  const x = 90 + 68 * Math.cos(radians)
  const y = 90 + 68 * Math.sin(radians)
  const largeArc = progress > 0.5 ? 1 : 0
  return `M90 22 A68 68 0 ${largeArc} 1 ${x.toFixed(2)} ${y.toFixed(2)}`
}

function runTimers() {
  const timer = createTimer({
    duration: 1800 + activeStep.value * 400,
    loop: true,
    frameRate: 30,
    onUpdate: (self) => {
      const progress = self.progress / 100
      timerReadout.value.textContent = `${Math.round(self.currentTime)} ms`
      timerArc.value.setAttribute('d', arcPath(progress))
    },
  })
  addCleanup(() => timer.revert())
}

function runAnimatableLiveInput() {
  liveAnimatable = createAnimatable('.live-target', {
    x: 500,
    y: 500,
    ease: 'out(3)',
  })
  const positions = [
    [-120, -40],
    [96, 28],
    [140, -66],
  ]
  const [x, y] = positions[activeStep.value]
  liveAnimatable.x(x)
  liveAnimatable.y(y)
}

function runEasingsSprings() {
  const rows = [
    ['.ease-outExpo', 'outExpo'],
    ['.ease-cubicBezier', cubicBezier(0.45, 0, 0.15, 1)],
    ['.ease-steps', steps(5)],
    ['.ease-spring', spring(1, 80, 10, 0)],
  ]
  rows.forEach(([selector, ease], index) => {
    animate(selector, {
      x: 250,
      duration: 1500,
      ease,
      delay: index * 80,
      loop: true,
      alternate: true,
    })
  })
}

function runSvgDrawable() {
  const drawables = queryAll('.draw-line').flatMap((line) => svg.createDrawable(line))
  animate(drawables, {
    draw: ['0 0', '0 1', '1 1'],
    delay: stagger(160),
    duration: 2100,
    ease: 'inOutQuad',
    loop: true,
  })
}

function runSvgMotionPath() {
  const path = query('.motion-path')
  const marker = query('.motion-dot')
  animate(marker, {
    ...svg.createMotionPath(path),
    duration: 2600,
    ease: 'linear',
    loop: true,
  })
  animate(svg.createDrawable(path), {
    draw: '0 1',
    duration: 2600,
    ease: 'linear',
    loop: true,
  })
}

function runSvgMorph() {
  animate('.morph-source', {
    d: svg.morphTo('.morph-target', 0.5),
    duration: 1600,
    ease: 'inOutExpo',
    loop: true,
    alternate: true,
  })
}

function runTextSplit() {
  const splitter = splitText(query('.split-heading'), {
    words: false,
    chars: true,
    accessible: true,
  })
  addCleanup(() => splitter.revert())
  animate(splitter.chars, {
    y: [24, 0],
    opacity: [0, 1],
    rotate: [-8, 0],
    delay: stagger(28),
    duration: 860,
    ease: 'outExpo',
    loop: true,
    alternate: true,
    loopDelay: 700,
  })
}

function runTextScramble() {
  const target = query('.scramble-heading')
  target.textContent = 'Motion that tells the story'
  animate(target, {
    innerHTML: scrambleText({
      text: activeStep.value > 1 ? 'State changes drive the slide' : 'Motion that tells the story',
      chars: '01XO',
      revealDelay: 65,
      seed: 12,
    }),
    duration: 1500,
    ease: 'linear',
    loop: true,
    loopDelay: 900,
  })
}

async function runLayoutTransitions() {
  const layoutRoot = query('.layout-grid')
  const layout = createLayout(layoutRoot)
  addCleanup(() => layout.revert())
  layout.record()
  if (activeStep.value > 1) {
    layoutItems.value = ['Ship', 'Plan', 'Test', 'Build']
  } else {
    layoutItems.value = ['Plan', 'Build', 'Test', 'Ship']
  }
  await nextTick()
  layout.animate()
}

function runDraggableInteractions() {
  const zone = query('.drag-zone')
  const card = query('.drag-card')
  const draggable = createDraggable(card, {
    container: zone,
    containerPadding: 10,
  })
  addCleanup(() => draggable.revert())
  animate(card, {
    x: [0, 126],
    y: [0, activeStep.value * 16],
    rotate: [0, 5],
    duration: 1300,
    ease: 'inOutSine',
    loop: true,
    alternate: true,
  })
}

function runScrollObserver() {
  const container = query('.scroll-panel')
  const target = query('.scroll-card')
  const observer = onScroll({ container, target, sync: 0.8 })
  addCleanup(() => observer.revert())
  animate(target, {
    x: 210,
    rotate: '1turn',
    autoplay: observer,
    duration: 1200,
    ease: 'outExpo',
  })
  requestAnimationFrame(() => {
    container.scrollTo({ top: activeStep.value > 0 ? container.scrollHeight : 120, behavior: 'smooth' })
  })
}

function runScopeMediaCleanup() {
  animate('.scope-mark', {
    y: [-10, 18],
    scale: [0.85, 1.12],
    delay: stagger(100),
    duration: 900,
    ease: 'outExpo',
    loop: true,
    alternate: true,
  })
}

function runWaapiAnimations() {
  const animation = waapi.animate('.waapi-pill', {
    x: activeStep.value > 0 ? 118 : 82,
    opacity: [0.5, 1],
    scale: [0.94, 1.08],
    rotate: ['-3deg', '3deg'],
    delay: stagger(90),
    duration: 1100,
    ease: 'outExpo',
    loop: true,
    alternate: true,
  })
  addCleanup(() => animation.cancel())
}

function runEngineControls() {
  previousEngineSpeed = engine.speed
  engine.speed = activeStep.value === 0 ? 1 : activeStep.value === 1 ? 0.55 : 1.45
  engineStatus.value.textContent = `engine speed: ${engine.speed}`
  const animation = animate('.engine-marker', {
    x: 270,
    duration: 1600,
    ease: 'inOutSine',
    loop: true,
    alternate: true,
  })
  if (activeStep.value === 1) {
    setTimeout(() => {
      engine.pause()
      engineStatus.value.textContent = 'engine.pause()'
      setTimeout(() => {
        engine.resume()
        engineStatus.value.textContent = `engine.resume(), speed: ${engine.speed}`
      }, 450)
    }, 450)
  }
  addCleanup(() => {
    animation.revert()
    engine.speed = previousEngineSpeed
    engine.resume()
  })
}

const runners = {
  'css-transforms': runCssTransforms,
  'css-properties-colors': runCssPropertiesColors,
  'keyframes-relative-values': runKeyframesRelativeValues,
  'js-object-values': runObjectValues,
  'stagger-sequences': runStaggerSequences,
  'timeline-sequencing': runTimelineSequencing,
  'playback-controls': runPlaybackControls,
  timers: runTimers,
  'animatable-live-input': runAnimatableLiveInput,
  'easings-springs': runEasingsSprings,
  'svg-drawable': runSvgDrawable,
  'svg-motion-path': runSvgMotionPath,
  'svg-morph': runSvgMorph,
  'text-split': runTextSplit,
  'text-scramble': runTextScramble,
  'layout-transitions': runLayoutTransitions,
  'draggable-interactions': runDraggableInteractions,
  'scroll-observer': runScrollObserver,
  'scope-media-cleanup': runScopeMediaCleanup,
  'waapi-animations': runWaapiAnimations,
  'engine-controls': runEngineControls,
}

async function start() {
  if (!root.value) return
  cleanup()
  await nextTick()
  scope = createScope({
    root: root.value,
    defaults: { duration: 900, ease: 'outExpo' },
    mediaQueries: {
      reduceMotion: '(prefers-reduced-motion)',
    },
  })
  scope.add((self) => {
    if (spec.value.type === 'scope-media-cleanup' && self.matches.reduceMotion) {
      queryAll('.scope-mark').forEach((mark) => {
        mark.style.transform = 'translateY(0)'
      })
      return
    }
    runners[spec.value.type]()
  })
}

onMounted(start)
onBeforeUnmount(cleanup)
watch(() => [props.feature, activeStep.value], start, { flush: 'post' })
</script>
