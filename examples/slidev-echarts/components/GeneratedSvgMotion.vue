<template>
  <section class="generated-svg-slide">
    <div class="generated-svg-header">
      <div>
        <p class="eyebrow">{{ spec.type }}</p>
        <h2>{{ spec.title }}</h2>
      </div>
      <div class="generated-svg-summary">
        <p>{{ spec.summary }}</p>
        <div class="generated-svg-controls">
          <span class="renderer-badge">Vue SVG renderer</span>
          <button type="button" data-svg-replay-button @click="replaySvg">
            Replay SVG
          </button>
        </div>
      </div>
    </div>

    <div class="generated-svg-body">
      <div
        ref="frameElement"
        class="generated-svg-frame"
        :class="{ 'is-replaying': isReplaying }"
        data-generated-svg-demo="true"
        data-renderer="vue-svg"
        data-svg-replayable="true"
      >
        <svg viewBox="0 0 720 300" role="img" :aria-label="spec.title">
          <defs>
            <linearGradient id="svg-motion-blue" x1="0" x2="1" y1="0" y2="1">
              <stop offset="0%" stop-color="#007298" />
              <stop offset="100%" stop-color="#45842a" />
            </linearGradient>
            <linearGradient id="svg-motion-warm" x1="0" x2="1" y1="0" y2="0">
              <stop offset="0%" stop-color="#e77204" />
              <stop offset="100%" stop-color="#9e1b32" />
            </linearGradient>
            <marker id="svg-motion-arrow" markerHeight="9" markerWidth="9" orient="auto" refX="7" refY="4.5">
              <path d="M0,0 L8,4.5 L0,9 Z" fill="#007298" />
            </marker>
          </defs>

          <template v-if="mode === 'path'">
            <path class="svg-gridline" d="M60 242 H660" />
            <line v-for="x in [180, 360, 540]" :key="`path-grid-${x}`" :x1="x" y1="58" :x2="x" y2="242" class="svg-gridline muted" />
            <path class="svg-motion-guide" :d="pathShape" />
            <path class="svg-motion-path" :d="pathShape" data-draw pathLength="1" />
            <g v-for="node in pathNodes" :key="node.label" data-node>
              <circle :cx="node.x" :cy="node.y" :r="node.r" fill="#ffffff" stroke="#007298" stroke-width="3" />
              <circle :cx="node.x" :cy="node.y" r="5" fill="#45842a" />
              <text :x="node.x" :y="node.y + 30" text-anchor="middle" data-label>{{ node.label }}</text>
            </g>
          </template>

          <template v-else-if="mode === 'particles'">
            <circle cx="360" cy="150" :r="particleRadius + 20" class="svg-orbit-ring" />
            <circle cx="360" cy="150" :r="particleRadius - 18" class="svg-orbit-ring muted" />
            <line
              v-for="particle in particles"
              :key="`line-${particle.id}`"
              :x1="360"
              :y1="150"
              :x2="particle.x"
              :y2="particle.y"
              class="svg-particle-link"
            />
            <g v-for="particle in particles" :key="particle.id" data-particle>
              <circle :cx="particle.x" :cy="particle.y" :r="particle.r + 8" :fill="particle.glow" opacity="0.16" />
              <circle :cx="particle.x" :cy="particle.y" :r="particle.r" :fill="particle.fill" />
            </g>
            <text x="360" y="145" text-anchor="middle" class="svg-center-label" data-label>{{ stageLabel }}</text>
            <text x="360" y="166" text-anchor="middle" data-label>deterministic particle field</text>
          </template>

          <template v-else-if="mode === 'bands'">
            <line v-for="x in [150, 250, 350, 450, 550]" :key="`band-grid-${x}`" :x1="x" y1="56" :x2="x" y2="242" class="svg-gridline muted" />
            <path
              v-for="band in bands"
              :key="band.id"
              :d="band.d"
              :fill="band.fill"
              :opacity="band.opacity"
              data-band
            />
            <circle
              v-for="band in bands"
              :key="`band-dot-${band.id}`"
              :cx="626 - band.id * 18"
              :cy="88 + band.id * 30"
              r="5"
              :fill="band.fill"
              stroke="#ffffff"
              stroke-width="2"
              data-band
            />
            <path class="svg-motion-axis" d="M64 242 H660" />
            <text x="64" y="270" data-label>origin</text>
            <text x="660" y="270" text-anchor="end" data-label>settled output</text>
          </template>

          <template v-else>
            <g v-for="glyph in glyphs" :key="glyph.id" data-glyph>
              <rect
                :x="glyph.x"
                :y="glyph.y"
                :width="glyph.width"
                :height="glyph.height"
                rx="8"
                :fill="glyph.fill"
              />
              <circle :cx="glyph.x + glyph.width - 14" :cy="glyph.y + 14" r="5" fill="#ffffff" opacity="0.86" />
            </g>
            <path class="svg-motion-axis" d="M68 250 H652" />
            <text x="72" y="278" data-label>generated glyph rows</text>
            <text x="652" y="278" text-anchor="end" data-label>{{ stageLabel }}</text>
          </template>
        </svg>
      </div>

      <aside class="generated-svg-notes">
        <div v-for="note in spec.notes" :key="note.title">
          <h3>{{ note.title }}</h3>
          <p>{{ note.body }}</p>
        </div>
      </aside>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  mode: {
    type: String,
    required: true,
    validator: (value) => ['path', 'particles', 'bands', 'glyphs'].includes(value),
  },
  step: {
    type: Number,
    default: 0,
  },
})

const frameElement = ref(null)
const isReplaying = ref(false)
const stage = computed(() => Math.min(Math.max(Number(props.step) || 0, 0), 3))
const mode = computed(() => props.mode)

const specs = {
  path: {
    type: 'generated path',
    title: 'Generated SVG Path Draw',
    summary: 'Build a deterministic path and animate stroke reveal, node arrival, and final labels.',
    notes: [
      { title: 'Geometry', body: 'The curve is generated from click-state control points.' },
      { title: 'Replay', body: 'Stroke dash animation runs from a wrapper class.' },
      { title: 'Validation', body: 'The recorder checks marks, text, replay, and click-state changes.' },
    ],
  },
  particles: {
    type: 'generated particles',
    title: 'Generated SVG Particle Field',
    summary: 'Place particles from computed polar coordinates and replay staggered orbit entry.',
    notes: [
      { title: 'Geometry', body: 'Positions are deterministic, not random, so screenshots are stable.' },
      { title: 'Replay', body: 'Particles and links animate without replacing the SVG.' },
      { title: 'Validation', body: 'The final frame keeps all dots and labels available to inspect.' },
    ],
  },
  bands: {
    type: 'generated bands',
    title: 'Generated SVG Morph Bands',
    summary: 'Generate layered wave bands whose paths change with each click-state.',
    notes: [
      { title: 'Geometry', body: 'Each band path is computed from the same baseline and amplitude.' },
      { title: 'Replay', body: 'Bands rise in sequence while the final SVG remains static.' },
      { title: 'Validation', body: 'Path counts and text labels keep the example auditable.' },
    ],
  },
  glyphs: {
    type: 'generated glyphs',
    title: 'Generated SVG Glyph Stack',
    summary: 'Generate compact glyph rows that change height, order, and emphasis over clicks.',
    notes: [
      { title: 'Geometry', body: 'Every rectangle is generated from a small row model.' },
      { title: 'Replay', body: 'Glyphs pop in with staggered CSS custom properties.' },
      { title: 'Validation', body: 'The recorder rejects blank or non-replayable generated SVG frames.' },
    ],
  },
}

const spec = computed(() => specs[props.mode])
const stageLabel = computed(() => `state ${stage.value + 1}`)

const pathNodes = computed(() => {
  const lift = stage.value * 8
  return [
    { label: 'input', x: 86, y: 226, r: 13 },
    { label: 'shape', x: 230, y: 126 - lift, r: 16 },
    { label: 'motion', x: 408, y: 158 + lift * 0.4, r: 18 },
    { label: 'replay', x: 616, y: 84 + lift * 0.6, r: 15 },
  ]
})

const pathShape = computed(() => {
  const nodes = pathNodes.value
  return `M${nodes[0].x} ${nodes[0].y} C160 ${190 - stage.value * 12}, 166 ${76 - stage.value * 6}, ${nodes[1].x} ${nodes[1].y} S330 ${218 + stage.value * 10}, ${nodes[2].x} ${nodes[2].y} S526 ${54 + stage.value * 8}, ${nodes[3].x} ${nodes[3].y}`
})

const particleRadius = computed(() => 82 + stage.value * 11)
const particles = computed(() => {
  const fills = ['#007298', '#45842a', '#e77204', '#9e1b32', '#652f6c', '#828282']
  return Array.from({ length: 14 }, (_, index) => {
    const angle = (Math.PI * 2 * index) / 14 + stage.value * 0.18
    const radius = particleRadius.value + (index % 3) * 12
    return {
      id: index,
      x: Math.round(360 + Math.cos(angle) * radius),
      y: Math.round(150 + Math.sin(angle) * radius * 0.72),
      r: 5 + ((index + stage.value) % 4),
      fill: fills[index % fills.length],
      glow: fills[(index + 2) % fills.length],
    }
  })
})

const bands = computed(() => {
  const fills = ['#cdf3ff', '#cdf3ff', '#99f6e4', '#fed7aa', '#fecdd3']
  return fills.map((fill, index) => {
    const top = 222 - index * 36
    const lower = top + 24
    const amp = 18 + stage.value * 7 + index * 3
    const d = [
      `M64 ${top}`,
      `C164 ${top - amp}, 226 ${top + amp}, 324 ${top - amp * 0.4}`,
      `S510 ${top - amp * 1.2}, 660 ${top - amp * 0.2}`,
      `L660 ${lower}`,
      `C510 ${lower - amp * 0.35}, 324 ${lower + amp * 0.25}, 64 ${lower}`,
      'Z',
    ].join(' ')
    return {
      id: index,
      d,
      fill,
      opacity: 0.72,
    }
  })
})

const glyphs = computed(() => {
  const fills = ['#007298', '#45842a', '#e77204', '#9e1b32', '#652f6c']
  return Array.from({ length: 20 }, (_, index) => {
    const col = index % 5
    const row = Math.floor(index / 5)
    const width = 48 + ((index + stage.value * 2) % 5) * 10 + stage.value * 4
    return {
      id: index,
      x: 94 + col * 116,
      y: 72 + row * 45,
      width,
      height: 30,
      fill: fills[(index + stage.value) % fills.length],
    }
  })
})

function replaySvg() {
  if (!frameElement.value)
    return false

  isReplaying.value = false
  frameElement.value.offsetWidth
  isReplaying.value = true
  window.setTimeout(() => {
    isReplaying.value = false
  }, 1150)

  return true
}
</script>
