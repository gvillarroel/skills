import './styles.css'
import * as THREE from 'three'

const TOKEN_HEX = {
  red: '#9e1b32',
  orange: '#e77204',
  yellow: '#f1c319',
  green: '#45842a',
  blue: '#007298',
  purple: '#652f6c',
  black: '#000000',
  white: '#ffffff',
  gray100: '#e7e7e7',
  gray200: '#cfcfcf',
  gray500: '#828282',
  gray700: '#4f4f4f',
  neutral: '#333e48',
}

const PRIMARY_TOKENS = ['red', 'orange', 'yellow', 'green', 'blue', 'purple']
const COLOR_OBJECTS = Object.fromEntries(
  Object.entries(TOKEN_HEX).map(([name, value]) => [name, new THREE.Color(value)]),
)

const examples = [
  {
    id: 'token-cube',
    kicker: 'Materials',
    title: 'Token Color Cube',
    description: 'Six known palette faces rotate as a compact material and edge-lighting sanity check.',
    setup: setupTokenCube,
  },
  {
    id: 'orbit-system',
    kicker: 'Motion',
    title: 'Orbit System',
    description: 'Colored bodies travel through visible depth rings with a fixed camera and replayable timing.',
    setup: setupOrbitSystem,
  },
  {
    id: 'data-towers',
    kicker: 'Data Space',
    title: '3D Data Towers',
    description: 'A small generated matrix becomes token-colored bars with animated vertical scale.',
    setup: setupDataTowers,
  },
  {
    id: 'particle-helix',
    kicker: 'Particles',
    title: 'Particle Helix',
    description: 'Vertex-colored points trace a rotating flow field without external assets.',
    setup: setupParticleHelix,
  },
  {
    id: 'wave-surface',
    kicker: 'Surface',
    title: 'Wave Surface',
    description: 'A buffer-geometry mesh updates height and vertex colors every frame.',
    setup: setupWaveSurface,
  },
  {
    id: 'instanced-matrix',
    kicker: 'Instances',
    title: 'Instanced Matrix',
    description: 'Repeated cubes share geometry while individual transforms and token colors animate.',
    setup: setupInstancedMatrix,
  },
  {
    id: 'path-ribbon',
    kicker: 'Path',
    title: 'Ribbon Path',
    description: 'Tube geometry and moving beads show how to choreograph motion along a 3D curve.',
    setup: setupPathRibbon,
  },
  {
    id: 'material-sampler',
    kicker: 'Lighting',
    title: 'Material Sampler',
    description: 'Primitives with varied roughness, metalness, and lights expose material differences.',
    setup: setupMaterialSampler,
  },
  {
    id: 'network-constellation',
    kicker: 'Graph',
    title: 'Network Constellation',
    description: 'Token-colored nodes and depth lines orbit as a compact 3D relationship map.',
    setup: setupNetworkConstellation,
  },
  {
    id: 'radial-rings',
    kicker: 'Composition',
    title: 'Radial Token Rings',
    description: 'Nested torus bands rotate on separate axes to reveal depth and palette order.',
    setup: setupRadialRings,
  },
  {
    id: 'vector-field',
    kicker: 'Field',
    title: 'Vector Field',
    description: 'Arrows use cones and cylinders to show directional flow over a neutral plane.',
    setup: setupVectorField,
  },
  {
    id: 'contour-layers',
    kicker: 'Contours',
    title: 'Contour Layers',
    description: 'Stacked generated loops make a small topographic model with animated lift.',
    setup: setupContourLayers,
  },
  {
    id: 'embedding-space',
    kicker: 'LLM',
    title: 'Embedding Space',
    description: 'Token vectors cluster in depth while semantic neighborhoods orbit through 3D space.',
    setup: setupEmbeddingSpace,
  },
  {
    id: 'attention-tiles',
    kicker: 'Attention',
    title: 'Attention Matrix Tiles',
    description: 'A tiled score matrix sweeps through rows like IO-aware block attention processing.',
    setup: setupAttentionTiles,
  },
  {
    id: 'qkv-projection',
    kicker: 'Transformer',
    title: 'QKV Projection Split',
    description: 'Input token columns fan into query, key, and value projection planes.',
    setup: setupQkvProjection,
  },
  {
    id: 'lora-low-rank',
    kicker: 'Adaptation',
    title: 'LoRA Low-Rank Bridge',
    description: 'Frozen weights stay neutral while two small trainable matrices inject an update.',
    setup: setupLoraLowRank,
  },
  {
    id: 'scaled-attention-3d',
    kicker: 'Attention',
    title: 'Scaled Attention Pipeline',
    description: 'Q and K planes produce a raised score matrix before softmax weights pull values forward.',
    setup: setupScaledAttention3d,
  },
  {
    id: 'multi-head-merge-3d',
    kicker: 'Transformer',
    title: 'Multi-Head Merge',
    description: 'Four attention head panels specialize in depth, then merge into a shared projection block.',
    setup: setupMultiHeadMerge3d,
  },
  {
    id: 'moe-router-3d',
    kicker: 'LLM',
    title: 'MoE Router Capacity',
    description: 'Token beads travel to expert towers while filled slots show sparse routing pressure.',
    setup: setupMoeRouter3d,
  },
  {
    id: 'speculative-decode-3d',
    kicker: 'Inference',
    title: 'Speculative Decode Tree',
    description: 'Draft tokens branch through space while accepted and rejected paths separate.',
    setup: setupSpeculativeDecode3d,
  },
  {
    id: 'rope-rotation-3d',
    kicker: 'Transformer',
    title: 'RoPE Rotation Rings',
    description: 'Query and key vectors rotate on position rings so relative phase becomes visible.',
    setup: setupRopeRotation3d,
  },
  {
    id: 'logit-lens-3d',
    kicker: 'Diagnostics',
    title: 'Logit Lens Rank Paths',
    description: 'Candidate token rank trajectories climb and fall across layer columns in depth.',
    setup: setupLogitLens3d,
  },
  {
    id: 'swiglu-ffn-3d',
    kicker: 'Transformer',
    title: 'SwiGLU Gate Volume',
    description: 'Up and gate projections expand into two rails, multiply, then contract through down projection.',
    setup: setupSwigluFfn3d,
  },
  {
    id: 'paged-kv-cache-3d',
    kicker: 'Inference',
    title: 'Paged KV Cache Blocks',
    description: 'Concurrent request streams allocate fixed memory pages and reuse freed blocks.',
    setup: setupPagedKvCache3d,
  },
]

const gallery = document.querySelector('#gallery')
const pageShell = document.querySelector('.page-shell')
const instances = []
const sharedRenderer = new THREE.WebGLRenderer({
  antialias: true,
  alpha: false,
  preserveDrawingBuffer: true,
})
sharedRenderer.outputColorSpace = THREE.SRGBColorSpace
sharedRenderer.setClearColor(COLOR_OBJECTS.white, 1)
sharedRenderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2))

document.querySelector('#example-count').textContent = String(examples.length)

for (const [index, example] of examples.entries()) {
  const card = document.createElement('article')
  card.className = 'example-card'
  card.dataset.sceneId = example.id
  card.dataset.replayCount = '0'
  card.dataset.dragCount = '0'
  card.innerHTML = `
    <div class="example-header">
      <div class="example-header-top">
        <p class="example-kicker">${example.kicker}</p>
        <button class="card-replay-button" type="button" aria-label="Replay ${example.title}">
          <span class="material-symbols-rounded" aria-hidden="true">replay</span>
          Replay
        </button>
      </div>
      <h2>${example.title}</h2>
      <p class="example-copy">${example.description}</p>
    </div>
    <div class="scene-frame">
      <canvas class="three-canvas" data-scene-id="${example.id}" aria-label="${example.title} canvas" tabindex="0"></canvas>
    </div>
  `

  gallery.append(card)

  const canvas = card.querySelector('canvas')
  const replayButton = card.querySelector('.card-replay-button')
  const instance = createSceneInstance({ canvas, card, example, index })
  replayButton.addEventListener('click', () => instance.replay())
  instances.push(instance)
}

document.querySelector('#replay-all').addEventListener('click', () => {
  pageShell.dataset.replayState = 'running'
  for (const instance of instances) instance.replay()
  window.setTimeout(() => {
    pageShell.dataset.replayState = 'idle'
  }, 900)
})

window.__threeGalleryScenes = instances
window.__threeGalleryReady = false

requestAnimationFrame((now) => {
  for (const instance of instances) instance.render(now)
  window.__threeGalleryReady = true
  requestAnimationFrame(animate)
})

window.addEventListener('beforeunload', () => {
  for (const instance of instances) instance.dispose()
  sharedRenderer.dispose()
})

function animate(now) {
  for (const instance of instances) instance.render(now)
  requestAnimationFrame(animate)
}

function createSceneInstance({ canvas, card, example, index }) {
  const context = canvas.getContext('2d', { alpha: false })
  const scene = new THREE.Scene()
  scene.background = COLOR_OBJECTS.white

  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 100)
  const root = new THREE.Group()
  scene.add(root)
  addDefaultLights(scene)

  const state = {
    startTime: performance.now() - index * 120,
    dragX: 0,
    dragY: 0,
  }

  const api = example.setup({ scene, root, camera, index })
  attachPointerDrag(canvas, root, card, state)

  function replay() {
    state.startTime = performance.now()
    state.dragX = 0
    state.dragY = 0
    root.rotation.set(0, 0, 0)
    api.reset?.()
    card.dataset.replayCount = String(Number(card.dataset.replayCount || 0) + 1)
    card.dataset.replayState = 'running'
    window.setTimeout(() => {
      card.dataset.replayState = 'idle'
    }, 900)
  }

  function render(now) {
    resizeCanvasForDisplay(canvas, camera)
    const seconds = (now - state.startTime) / 1000
    api.update(seconds, state)
    renderSceneToCanvas(scene, camera, canvas, context)
  }

  function dispose() {
    api.dispose?.()
    scene.traverse(disposeObject)
  }

  return { id: example.id, replay, render, dispose }
}

function addDefaultLights(scene) {
  const ambient = new THREE.HemisphereLight(TOKEN_HEX.white, TOKEN_HEX.gray200, 1.65)
  scene.add(ambient)

  const key = new THREE.DirectionalLight(TOKEN_HEX.white, 2.6)
  key.position.set(5, 6, 5)
  scene.add(key)

  const fill = new THREE.DirectionalLight(TOKEN_HEX.blue, 0.65)
  fill.position.set(-4, 3, -3)
  scene.add(fill)
}

function resizeCanvasForDisplay(canvas, camera) {
  const rect = canvas.getBoundingClientRect()
  const width = Math.max(2, Math.floor(rect.width))
  const height = Math.max(2, Math.floor(rect.height))
  const pixelRatio = Math.min(window.devicePixelRatio || 1, 2)

  if (canvas.width !== Math.floor(width * pixelRatio) || canvas.height !== Math.floor(height * pixelRatio)) {
    canvas.width = Math.floor(width * pixelRatio)
    canvas.height = Math.floor(height * pixelRatio)
    camera.aspect = width / height
    camera.updateProjectionMatrix()
  }
}

function renderSceneToCanvas(scene, camera, canvas, context) {
  const rect = canvas.getBoundingClientRect()
  const width = Math.max(2, Math.floor(rect.width))
  const height = Math.max(2, Math.floor(rect.height))
  const pixelRatio = Math.min(window.devicePixelRatio || 1, 2)
  sharedRenderer.setPixelRatio(pixelRatio)
  sharedRenderer.setSize(width, height, false)
  sharedRenderer.render(scene, camera)
  context.setTransform(1, 0, 0, 1, 0, 0)
  context.drawImage(sharedRenderer.domElement, 0, 0, canvas.width, canvas.height)
}

function attachPointerDrag(canvas, root, card, state) {
  let active = false
  let lastX = 0
  let lastY = 0

  canvas.addEventListener('pointerdown', (event) => {
    active = true
    lastX = event.clientX
    lastY = event.clientY
    canvas.setPointerCapture(event.pointerId)
  })

  canvas.addEventListener('pointermove', (event) => {
    if (!active) return
    const dx = event.clientX - lastX
    const dy = event.clientY - lastY
    lastX = event.clientX
    lastY = event.clientY
    state.dragY += dx * 0.008
    state.dragX = THREE.MathUtils.clamp(state.dragX + dy * 0.006, -0.7, 0.7)
    root.rotation.y = state.dragY
    root.rotation.x = state.dragX
    card.dataset.dragCount = String(Number(card.dataset.dragCount || 0) + 1)
  })

  const endDrag = (event) => {
    if (!active) return
    active = false
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId)
  }

  canvas.addEventListener('pointerup', endDrag)
  canvas.addEventListener('pointercancel', endDrag)
}

function tokenMaterial(token, options = {}) {
  return new THREE.MeshStandardMaterial({
    color: TOKEN_HEX[token],
    roughness: 0.55,
    metalness: 0.08,
    ...options,
  })
}

function lookAtOrigin(camera) {
  camera.lookAt(0, 0, 0)
}

function setupTokenCube({ root, camera }) {
  camera.position.set(4.1, 3.2, 5.2)
  lookAtOrigin(camera)

  const cubeGroup = new THREE.Group()
  root.add(cubeGroup)

  const geometry = new THREE.BoxGeometry(2, 2, 2)
  const materials = PRIMARY_TOKENS.map((token) => tokenMaterial(token, { metalness: 0.14, roughness: 0.42 }))
  const cube = new THREE.Mesh(geometry, materials)
  cubeGroup.add(cube)

  const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(geometry),
    new THREE.LineBasicMaterial({ color: TOKEN_HEX.black, transparent: true, opacity: 0.32 }),
  )
  cubeGroup.add(edges)

  const base = new THREE.Mesh(
    new THREE.CylinderGeometry(1.75, 1.75, 0.08, 64),
    tokenMaterial('gray100', { roughness: 0.9, metalness: 0 }),
  )
  base.position.y = -1.42
  root.add(base)

  return {
    update(seconds) {
      cubeGroup.rotation.x = 0.38 + seconds * 0.46
      cubeGroup.rotation.y = 0.72 + seconds * 0.62
      cubeGroup.position.y = Math.sin(seconds * 1.7) * 0.08
    },
    reset() {
      cubeGroup.rotation.set(0.38, 0.72, 0)
      cubeGroup.position.y = 0
    },
  }
}

function setupOrbitSystem({ root, camera }) {
  camera.position.set(5.2, 3.6, 6.4)
  lookAtOrigin(camera)

  const system = new THREE.Group()
  root.add(system)

  const sun = new THREE.Mesh(
    new THREE.SphereGeometry(0.58, 48, 24),
    tokenMaterial('red', { emissive: TOKEN_HEX.red, emissiveIntensity: 0.08, roughness: 0.35 }),
  )
  system.add(sun)

  const orbiters = []
  const orbitData = [
    { radius: 1.28, size: 0.18, token: 'yellow', speed: 1.35, tilt: 0.18 },
    { radius: 1.85, size: 0.23, token: 'green', speed: 0.92, tilt: -0.28 },
    { radius: 2.48, size: 0.2, token: 'blue', speed: 0.68, tilt: 0.36 },
    { radius: 3.05, size: 0.16, token: 'purple', speed: 0.52, tilt: -0.14 },
  ]

  for (const data of orbitData) {
    const ringPoints = []
    for (let i = 0; i < 96; i += 1) {
      const angle = (i / 96) * Math.PI * 2
      ringPoints.push(new THREE.Vector3(Math.cos(angle) * data.radius, 0, Math.sin(angle) * data.radius))
    }
    const ring = new THREE.LineLoop(
      new THREE.BufferGeometry().setFromPoints(ringPoints),
      new THREE.LineBasicMaterial({ color: TOKEN_HEX.gray200, transparent: true, opacity: 0.85 }),
    )
    ring.rotation.x = data.tilt
    system.add(ring)

    const orbiter = new THREE.Mesh(
      new THREE.SphereGeometry(data.size, 32, 16),
      tokenMaterial(data.token, { roughness: 0.48, metalness: 0.05 }),
    )
    system.add(orbiter)
    orbiters.push({ mesh: orbiter, ring, ...data })
  }

  return {
    update(seconds) {
      sun.rotation.y = seconds * 0.5
      system.rotation.y = seconds * 0.08
      orbiters.forEach((orbiter, i) => {
        const angle = seconds * orbiter.speed + i * 1.4
        const x = Math.cos(angle) * orbiter.radius
        const z = Math.sin(angle) * orbiter.radius
        orbiter.mesh.position.set(x, Math.sin(angle * 0.9) * 0.1, z)
        orbiter.mesh.position.applyAxisAngle(new THREE.Vector3(1, 0, 0), orbiter.tilt)
      })
    },
    reset() {
      system.rotation.set(0, 0, 0)
    },
  }
}

function setupDataTowers({ root, camera }) {
  camera.position.set(5.8, 4.6, 6.6)
  lookAtOrigin(camera)

  const base = new THREE.Mesh(
    new THREE.BoxGeometry(5.6, 0.08, 5.6),
    tokenMaterial('gray100', { roughness: 0.85, metalness: 0 }),
  )
  base.position.y = -0.05
  root.add(base)

  const bars = []
  const values = [
    0.55, 1.25, 0.85, 1.8,
    1.45, 0.72, 1.96, 1.12,
    0.92, 1.7, 1.34, 0.64,
    1.25, 1.05, 1.62, 2.1,
  ]

  values.forEach((value, i) => {
    const x = (i % 4 - 1.5) * 1.1
    const z = (Math.floor(i / 4) - 1.5) * 1.1
    const token = PRIMARY_TOKENS[i % PRIMARY_TOKENS.length]
    const bar = new THREE.Mesh(
      new THREE.BoxGeometry(0.58, 1, 0.58),
      tokenMaterial(token, { roughness: 0.5, metalness: 0.06 }),
    )
    bar.userData.baseHeight = value
    bar.userData.phase = i * 0.42
    bar.position.set(x, value / 2, z)
    root.add(bar)

    const edge = new THREE.LineSegments(
      new THREE.EdgesGeometry(bar.geometry),
      new THREE.LineBasicMaterial({ color: TOKEN_HEX.white, transparent: true, opacity: 0.55 }),
    )
    bar.add(edge)
    bars.push(bar)
  })

  return {
    update(seconds) {
      root.rotation.y += 0
      for (const bar of bars) {
        const height = bar.userData.baseHeight * (0.78 + Math.sin(seconds * 1.4 + bar.userData.phase) * 0.18)
        bar.scale.y = height
        bar.position.y = height / 2
      }
    },
    reset() {
      bars.forEach((bar) => {
        bar.scale.y = bar.userData.baseHeight
        bar.position.y = bar.userData.baseHeight / 2
      })
    },
  }
}

function setupParticleHelix({ root, camera }) {
  camera.position.set(4.8, 2.8, 6.4)
  lookAtOrigin(camera)

  const count = 420
  const positions = new Float32Array(count * 3)
  const colors = new Float32Array(count * 3)
  const geometry = new THREE.BufferGeometry()

  for (let i = 0; i < count; i += 1) {
    const token = PRIMARY_TOKENS[i % PRIMARY_TOKENS.length]
    COLOR_OBJECTS[token].toArray(colors, i * 3)
  }

  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

  const points = new THREE.Points(
    geometry,
    new THREE.PointsMaterial({
      size: 0.075,
      vertexColors: true,
      transparent: true,
      opacity: 0.94,
      sizeAttenuation: true,
    }),
  )
  root.add(points)

  return {
    update(seconds) {
      const position = geometry.getAttribute('position')
      for (let i = 0; i < count; i += 1) {
        const p = i / count
        const angle = p * Math.PI * 12 + seconds * 0.9
        const radius = 0.95 + Math.sin(p * Math.PI * 8 + seconds * 1.4) * 0.22
        position.setXYZ(
          i,
          Math.cos(angle) * radius,
          (p - 0.5) * 4.2,
          Math.sin(angle) * radius,
        )
      }
      position.needsUpdate = true
      points.rotation.y = seconds * 0.34
    },
    reset() {
      points.rotation.set(0, 0, 0)
    },
  }
}

function setupWaveSurface({ root, camera }) {
  camera.position.set(4.8, 3.9, 5.4)
  camera.lookAt(0, 0.15, 0)

  const geometry = new THREE.PlaneGeometry(5.4, 3.7, 54, 36)
  const colors = new Float32Array(geometry.attributes.position.count * 3)
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))

  const mesh = new THREE.Mesh(
    geometry,
    new THREE.MeshStandardMaterial({
      vertexColors: true,
      side: THREE.DoubleSide,
      roughness: 0.62,
      metalness: 0.04,
    }),
  )
  mesh.rotation.x = -Math.PI / 2
  root.add(mesh)

  const wire = new THREE.LineSegments(
    new THREE.WireframeGeometry(geometry),
    new THREE.LineBasicMaterial({ color: TOKEN_HEX.white, transparent: true, opacity: 0.16 }),
  )
  wire.rotation.x = mesh.rotation.x
  root.add(wire)

  return {
    update(seconds) {
      const position = geometry.getAttribute('position')
      const colorAttr = geometry.getAttribute('color')
      const colorA = new THREE.Color()
      const colorB = new THREE.Color()
      const mixed = new THREE.Color()

      for (let i = 0; i < position.count; i += 1) {
        const x = position.getX(i)
        const y = position.getY(i)
        const height = Math.sin(x * 1.45 + seconds * 1.3) * 0.28 + Math.cos(y * 2.1 - seconds * 1.1) * 0.2
        position.setZ(i, height)
        const normalized = THREE.MathUtils.clamp((height + 0.55) / 1.1, 0, 1)
        const lowerToken = normalized < 0.5 ? 'blue' : 'yellow'
        const upperToken = normalized < 0.5 ? 'green' : 'red'
        colorA.copy(COLOR_OBJECTS[lowerToken])
        colorB.copy(COLOR_OBJECTS[upperToken])
        mixed.lerpColors(colorA, colorB, normalized < 0.5 ? normalized * 2 : (normalized - 0.5) * 2)
        colorAttr.setXYZ(i, mixed.r, mixed.g, mixed.b)
      }

      position.needsUpdate = true
      colorAttr.needsUpdate = true
      geometry.computeVertexNormals()
      wire.geometry.dispose()
      wire.geometry = new THREE.WireframeGeometry(geometry)
      root.rotation.y = Math.sin(seconds * 0.32) * 0.12
    },
    reset() {
      root.rotation.set(0, 0, 0)
    },
  }
}

function setupPathRibbon({ root, camera }) {
  camera.position.set(4.9, 3.4, 5.8)
  lookAtOrigin(camera)

  const curve = new THREE.CatmullRomCurve3([
    new THREE.Vector3(-2.2, -0.55, 0.8),
    new THREE.Vector3(-1.15, 0.65, -1.05),
    new THREE.Vector3(0.25, 0.15, 1.05),
    new THREE.Vector3(1.25, 0.9, -0.75),
    new THREE.Vector3(2.25, -0.2, 0.65),
  ])

  const tube = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 96, 0.055, 12, false),
    tokenMaterial('blue', { roughness: 0.42, metalness: 0.18 }),
  )
  root.add(tube)

  const beads = PRIMARY_TOKENS.map((token, i) => {
    const bead = new THREE.Mesh(
      new THREE.SphereGeometry(0.14 + (i % 2) * 0.03, 24, 12),
      tokenMaterial(token, { roughness: 0.36, metalness: 0.12 }),
    )
    root.add(bead)
    return bead
  })

  const anchors = curve.getPoints(7).map((point) => {
    const anchor = new THREE.Mesh(
      new THREE.SphereGeometry(0.045, 12, 8),
      tokenMaterial('neutral', { roughness: 0.75, metalness: 0 }),
    )
    anchor.position.copy(point)
    root.add(anchor)
    return anchor
  })

  return {
    update(seconds) {
      beads.forEach((bead, i) => {
        const u = 0.02 + ((seconds * (0.08 + i * 0.006) + i / beads.length) % 0.96)
        const point = curve.getPointAt(u)
        bead.position.copy(point)
        bead.scale.setScalar(1 + Math.sin(seconds * 2.2 + i) * 0.12)
      })
      tube.rotation.y = Math.sin(seconds * 0.38) * 0.18
      for (const anchor of anchors) anchor.rotation.y = seconds
    },
    reset() {
      tube.rotation.set(0, 0, 0)
    },
  }
}

function setupInstancedMatrix({ root, camera }) {
  camera.position.set(4.8, 3.9, 5.4)
  lookAtOrigin(camera)

  const countX = 8
  const countZ = 8
  const geometry = new THREE.BoxGeometry(0.42, 0.42, 0.42)
  const groups = PRIMARY_TOKENS.map((token) => ({
    token,
    items: [],
    mesh: null,
  }))
  const matrix = new THREE.Matrix4()

  for (let z = 0; z < countZ; z += 1) {
    for (let x = 0; x < countX; x += 1) {
      const group = groups[(x + z * countX) % groups.length]
      group.items.push({ x, z })
    }
  }

  for (const group of groups) {
    group.mesh = new THREE.InstancedMesh(
      geometry,
      new THREE.MeshBasicMaterial({ color: TOKEN_HEX[group.token] }),
      group.items.length,
    )
    root.add(group.mesh)
  }

  const base = new THREE.Mesh(
    new THREE.BoxGeometry(5.2, 0.06, 5.2),
    tokenMaterial('gray100', { roughness: 0.86, metalness: 0 }),
  )
  base.position.y = -0.18
  root.add(base)

  return {
    update(seconds) {
      for (const group of groups) {
        group.items.forEach(({ x, z }, index) => {
          const px = (x - (countX - 1) / 2) * 0.56
          const pz = (z - (countZ - 1) / 2) * 0.56
          const wave = Math.sin(seconds * 1.45 + x * 0.75 + z * 0.5)
          const scale = 0.92 + (wave + 1) * 0.35
          matrix.compose(
            new THREE.Vector3(px, 0.16 + scale * 0.22, pz),
            new THREE.Quaternion().setFromEuler(new THREE.Euler(seconds * 0.22 + z * 0.08, seconds * 0.35 + x * 0.05, 0)),
            new THREE.Vector3(scale, scale, scale),
          )
          group.mesh.setMatrixAt(index, matrix)
        })
        group.mesh.instanceMatrix.needsUpdate = true
      }
    },
    reset() {
      root.rotation.set(0, 0, 0)
    },
  }
}

function setupMaterialSampler({ root, camera }) {
  camera.position.set(5.1, 3.2, 6.2)
  lookAtOrigin(camera)

  const shapes = [
    new THREE.Mesh(
      new THREE.TorusKnotGeometry(0.58, 0.18, 96, 14),
      tokenMaterial('purple', { roughness: 0.24, metalness: 0.42 }),
    ),
    new THREE.Mesh(
      new THREE.SphereGeometry(0.72, 48, 24),
      tokenMaterial('blue', { roughness: 0.18, metalness: 0.08 }),
    ),
    new THREE.Mesh(
      new THREE.ConeGeometry(0.68, 1.28, 5),
      tokenMaterial('orange', { roughness: 0.58, metalness: 0.16 }),
    ),
    new THREE.Mesh(
      new THREE.CylinderGeometry(0.46, 0.46, 1.18, 32),
      tokenMaterial('green', { roughness: 0.46, metalness: 0.08 }),
    ),
  ]

  shapes.forEach((shape, i) => {
    shape.position.x = (i - 1.5) * 1.15
    shape.position.y = i % 2 === 0 ? 0.18 : -0.06
    root.add(shape)
  })

  const spotlight = new THREE.PointLight(TOKEN_HEX.yellow, 1.5, 8)
  spotlight.position.set(-1.2, 2.2, 1.8)
  root.add(spotlight)

  const base = new THREE.Mesh(
    new THREE.BoxGeometry(5.2, 0.08, 2.1),
    tokenMaterial('gray100', { roughness: 0.86, metalness: 0 }),
  )
  base.position.set(0, -0.82, 0)
  root.add(base)

  return {
    update(seconds) {
      shapes.forEach((shape, i) => {
        shape.rotation.x = seconds * (0.38 + i * 0.08)
        shape.rotation.y = seconds * (0.62 + i * 0.04)
        shape.position.y += Math.sin(seconds * 1.4 + i) * 0.0015
      })
      spotlight.position.x = Math.sin(seconds * 0.9) * 1.8
      spotlight.position.z = Math.cos(seconds * 0.9) * 1.5
    },
    reset() {
      shapes.forEach((shape, i) => {
        shape.rotation.set(0, 0, 0)
        shape.position.y = i % 2 === 0 ? 0.18 : -0.06
      })
    },
  }
}

function setupNetworkConstellation({ root, camera }) {
  camera.position.set(5.4, 3.8, 6.2)
  lookAtOrigin(camera)

  const nodes = []
  const nodePositions = [
    [-1.8, 0.65, -0.7],
    [-0.9, -0.35, 1.2],
    [-0.2, 0.95, 0.15],
    [0.72, -0.55, -1.05],
    [1.62, 0.45, 0.82],
    [2.12, -0.05, -0.45],
    [-1.35, 1.32, 0.72],
    [0.34, 1.48, -1.18],
  ].map(([x, y, z]) => new THREE.Vector3(x, y, z))

  nodePositions.forEach((position, i) => {
    const node = new THREE.Mesh(
      new THREE.SphereGeometry(0.18 + (i % 3) * 0.035, 24, 12),
      tokenMaterial(PRIMARY_TOKENS[i % PRIMARY_TOKENS.length], { roughness: 0.36, metalness: 0.1 }),
    )
    node.position.copy(position)
    root.add(node)
    nodes.push(node)
  })

  const links = [
    [0, 1], [0, 2], [1, 2], [1, 4], [2, 3], [2, 6],
    [3, 4], [3, 7], [4, 5], [5, 7], [6, 7], [0, 6],
  ].map(([a, b], i) => {
    const geometry = new THREE.BufferGeometry().setFromPoints([nodePositions[a], nodePositions[b]])
    const line = new THREE.Line(
      geometry,
      new THREE.LineBasicMaterial({
        color: TOKEN_HEX[PRIMARY_TOKENS[i % PRIMARY_TOKENS.length]],
        transparent: true,
        opacity: 0.58,
      }),
    )
    root.add(line)
    return line
  })

  return {
    update(seconds) {
      root.rotation.y = seconds * 0.26
      root.rotation.x = Math.sin(seconds * 0.42) * 0.16
      nodes.forEach((node, i) => {
        node.scale.setScalar(1 + Math.sin(seconds * 2 + i * 0.7) * 0.16)
      })
      links.forEach((link, i) => {
        link.material.opacity = 0.42 + Math.sin(seconds * 1.7 + i) * 0.16
      })
    },
    reset() {
      root.rotation.set(0, 0, 0)
    },
  }
}

function setupRadialRings({ root, camera }) {
  camera.position.set(4.9, 3.4, 5.8)
  lookAtOrigin(camera)

  const rings = PRIMARY_TOKENS.map((token, i) => {
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(0.68 + i * 0.22, 0.035 + i * 0.004, 16, 96),
      tokenMaterial(token, { roughness: 0.44, metalness: 0.18 }),
    )
    ring.rotation.x = Math.PI / 2 + i * 0.12
    ring.rotation.y = i * 0.28
    root.add(ring)
    return ring
  })

  const center = new THREE.Mesh(
    new THREE.OctahedronGeometry(0.48, 1),
    tokenMaterial('neutral', { roughness: 0.38, metalness: 0.2 }),
  )
  root.add(center)

  return {
    update(seconds) {
      rings.forEach((ring, i) => {
        ring.rotation.z = seconds * (0.34 + i * 0.07)
        ring.rotation.y = i * 0.28 + Math.sin(seconds * 0.62 + i) * 0.28
      })
      center.rotation.x = seconds * 0.55
      center.rotation.y = seconds * 0.74
    },
    reset() {
      rings.forEach((ring, i) => {
        ring.rotation.set(Math.PI / 2 + i * 0.12, i * 0.28, 0)
      })
      center.rotation.set(0, 0, 0)
    },
  }
}

function setupVectorField({ root, camera }) {
  camera.position.set(5.3, 4.2, 6)
  lookAtOrigin(camera)

  const base = new THREE.Mesh(
    new THREE.BoxGeometry(5.4, 0.06, 4.2),
    tokenMaterial('gray100', { roughness: 0.88, metalness: 0 }),
  )
  base.position.y = -0.25
  root.add(base)

  const arrows = []
  for (let z = 0; z < 4; z += 1) {
    for (let x = 0; x < 5; x += 1) {
      const token = PRIMARY_TOKENS[(x + z) % PRIMARY_TOKENS.length]
      const arrow = new THREE.Group()
      const shaft = new THREE.Mesh(
        new THREE.CylinderGeometry(0.045, 0.045, 0.58, 12),
        tokenMaterial(token, { roughness: 0.5, metalness: 0.05 }),
      )
      shaft.rotation.z = Math.PI / 2
      const head = new THREE.Mesh(
        new THREE.ConeGeometry(0.12, 0.28, 16),
        tokenMaterial(token, { roughness: 0.42, metalness: 0.08 }),
      )
      head.rotation.z = -Math.PI / 2
      head.position.x = 0.42
      arrow.add(shaft, head)
      arrow.position.set((x - 2) * 1.02, 0.2, (z - 1.5) * 0.82)
      arrow.userData.phase = x * 0.65 + z * 0.92
      root.add(arrow)
      arrows.push(arrow)
    }
  }

  return {
    update(seconds) {
      arrows.forEach((arrow) => {
        const phase = arrow.userData.phase
        arrow.rotation.y = Math.sin(seconds * 1.25 + phase) * 0.9
        arrow.rotation.z = Math.cos(seconds * 1.1 + phase) * 0.18
        arrow.position.y = 0.2 + Math.sin(seconds * 1.6 + phase) * 0.12
      })
    },
    reset() {
      arrows.forEach((arrow) => {
        arrow.rotation.set(0, 0, 0)
        arrow.position.y = 0.2
      })
    },
  }
}

function setupContourLayers({ root, camera }) {
  camera.position.set(5.2, 4.6, 5.8)
  lookAtOrigin(camera)

  const layers = []
  const radii = [1.65, 1.38, 1.12, 0.88, 0.64, 0.42]
  radii.forEach((radius, i) => {
    const shape = new THREE.Shape()
    for (let p = 0; p <= 96; p += 1) {
      const angle = (p / 96) * Math.PI * 2
      const wobble = 1 + Math.sin(angle * 3 + i * 0.7) * 0.12 + Math.cos(angle * 5 - i * 0.4) * 0.06
      const x = Math.cos(angle) * radius * wobble
      const y = Math.sin(angle) * radius * wobble
      if (p === 0) shape.moveTo(x, y)
      else shape.lineTo(x, y)
    }

    const mesh = new THREE.Mesh(
      new THREE.ExtrudeGeometry(shape, { depth: 0.07, bevelEnabled: false }),
      tokenMaterial(PRIMARY_TOKENS[i % PRIMARY_TOKENS.length], { roughness: 0.58, metalness: 0.04 }),
    )
    mesh.rotation.x = -Math.PI / 2
    mesh.position.y = i * 0.18
    mesh.userData.baseY = mesh.position.y
    root.add(mesh)
    layers.push(mesh)
  })

  const base = new THREE.Mesh(
    new THREE.CylinderGeometry(2.15, 2.15, 0.06, 96),
    tokenMaterial('gray100', { roughness: 0.9, metalness: 0 }),
  )
  base.position.y = -0.08
  root.add(base)

  return {
    update(seconds) {
      layers.forEach((layer, i) => {
        layer.position.y = layer.userData.baseY + Math.sin(seconds * 1.2 + i * 0.55) * 0.035
        layer.rotation.z = seconds * (0.08 + i * 0.01)
      })
      root.rotation.y = Math.sin(seconds * 0.38) * 0.18
    },
    reset() {
      layers.forEach((layer) => {
        layer.position.y = layer.userData.baseY
        layer.rotation.z = 0
      })
      root.rotation.set(0, 0, 0)
    },
  }
}

function setupEmbeddingSpace({ root, camera }) {
  camera.position.set(5.5, 3.6, 6.4)
  lookAtOrigin(camera)

  const axisMaterial = new THREE.LineBasicMaterial({ color: TOKEN_HEX.gray200, transparent: true, opacity: 0.9 })
  const axes = [
    [new THREE.Vector3(-2.5, 0, 0), new THREE.Vector3(2.5, 0, 0)],
    [new THREE.Vector3(0, -1.7, 0), new THREE.Vector3(0, 1.7, 0)],
    [new THREE.Vector3(0, 0, -2.2), new THREE.Vector3(0, 0, 2.2)],
  ]
  axes.forEach((points) => {
    root.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), axisMaterial))
  })

  const tokens = []
  const centers = [
    new THREE.Vector3(-1.25, 0.2, -0.85),
    new THREE.Vector3(0.25, 0.72, 0.35),
    new THREE.Vector3(1.25, -0.18, -0.25),
    new THREE.Vector3(-0.35, -0.75, 1.1),
  ]
  for (let i = 0; i < 48; i += 1) {
    const center = centers[i % centers.length]
    const angle = i * 1.618
    const radius = 0.18 + (i % 5) * 0.08
    const token = PRIMARY_TOKENS[i % PRIMARY_TOKENS.length]
    const point = new THREE.Mesh(
      new THREE.SphereGeometry(0.075 + (i % 3) * 0.01, 16, 8),
      tokenMaterial(token, { roughness: 0.4, metalness: 0.08 }),
    )
    point.userData.base = new THREE.Vector3(
      center.x + Math.cos(angle) * radius,
      center.y + Math.sin(angle * 0.7) * radius * 0.8,
      center.z + Math.sin(angle) * radius,
    )
    point.userData.phase = i * 0.27
    root.add(point)
    tokens.push(point)
  }

  const centroid = new THREE.Mesh(
    new THREE.OctahedronGeometry(0.26, 1),
    tokenMaterial('neutral', { roughness: 0.36, metalness: 0.18 }),
  )
  root.add(centroid)

  return {
    update(seconds) {
      tokens.forEach((token) => {
        token.position.copy(token.userData.base)
        token.position.y += Math.sin(seconds * 1.2 + token.userData.phase) * 0.08
      })
      centroid.rotation.x = seconds * 0.65
      centroid.rotation.y = seconds * 0.82
      root.rotation.y = Math.sin(seconds * 0.36) * 0.24
    },
    reset() {
      root.rotation.set(0, 0, 0)
      centroid.rotation.set(0, 0, 0)
    },
  }
}

function setupAttentionTiles({ root, camera }) {
  camera.position.set(5.3, 4.8, 5.6)
  lookAtOrigin(camera)

  const size = 8
  const tiles = []
  const activeMaterial = new THREE.MeshBasicMaterial({ color: TOKEN_HEX.yellow })
  const base = new THREE.Mesh(
    new THREE.BoxGeometry(5.2, 0.05, 5.2),
    tokenMaterial('gray100', { roughness: 0.88, metalness: 0 }),
  )
  base.position.y = -0.08
  root.add(base)

  for (let row = 0; row < size; row += 1) {
    for (let col = 0; col < size; col += 1) {
      const distance = Math.abs(row - col)
      const token = distance < 2 ? 'red' : PRIMARY_TOKENS[(row + col) % PRIMARY_TOKENS.length]
      const material = new THREE.MeshBasicMaterial({ color: TOKEN_HEX[token] })
      const tile = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.08, 0.42), material)
      tile.position.set((col - 3.5) * 0.55, 0.02, (row - 3.5) * 0.55)
      tile.userData = { row, col, baseToken: token, material, distance }
      root.add(tile)
      tiles.push(tile)
    }
  }

  const cursor = new THREE.Mesh(
    new THREE.BoxGeometry(4.72, 0.035, 0.08),
    activeMaterial,
  )
  cursor.position.y = 0.22
  root.add(cursor)

  return {
    update(seconds) {
      const sweep = (seconds * 1.2) % size
      tiles.forEach((tile) => {
        const rowPulse = Math.max(0, 1 - Math.abs(tile.userData.row - sweep) / 1.4)
        const diagPulse = tile.userData.distance === 0 ? 0.42 : 0
        const height = 0.08 + (rowPulse + diagPulse) * 0.42
        tile.scale.y = height / 0.08
        tile.position.y = height / 2
      })
      cursor.position.z = (Math.floor(sweep) - 3.5) * 0.55
      root.rotation.y = Math.sin(seconds * 0.28) * 0.16
    },
    reset() {
      tiles.forEach((tile) => {
        tile.scale.y = 1
        tile.position.y = 0.04
      })
      root.rotation.set(0, 0, 0)
    },
  }
}

function setupQkvProjection({ root, camera }) {
  camera.position.set(5.7, 3.8, 6.2)
  lookAtOrigin(camera)

  const inputs = []
  const planes = []
  for (let i = 0; i < 6; i += 1) {
    const input = new THREE.Mesh(
      new THREE.BoxGeometry(0.32, 0.5, 0.32),
      tokenMaterial(PRIMARY_TOKENS[i % PRIMARY_TOKENS.length], { roughness: 0.48, metalness: 0.06 }),
    )
    input.position.set(-1.9, (i - 2.5) * 0.42, 0)
    input.userData.phase = i * 0.4
    root.add(input)
    inputs.push(input)
  }

  const projectionData = [
    { label: 'Q', token: 'red', z: -1.2 },
    { label: 'K', token: 'blue', z: 0 },
    { label: 'V', token: 'green', z: 1.2 },
  ]

  projectionData.forEach((data, planeIndex) => {
    const plane = new THREE.Group()
    const slab = new THREE.Mesh(
      new THREE.BoxGeometry(0.14, 2.8, 0.84),
      tokenMaterial(data.token, { roughness: 0.42, metalness: 0.1, transparent: true, opacity: 0.9 }),
    )
    plane.add(slab)
    plane.position.set(0.15 + planeIndex * 0.68, 0, data.z)
    root.add(plane)
    planes.push(plane)

    inputs.forEach((input, i) => {
      const points = [input.position.clone(), new THREE.Vector3(plane.position.x, (i - 2.5) * 0.3, data.z)]
      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(points),
        new THREE.LineBasicMaterial({ color: TOKEN_HEX[data.token], transparent: true, opacity: 0.45 }),
      )
      root.add(line)
    })
  })

  const output = new THREE.Mesh(
    new THREE.BoxGeometry(0.48, 1.9, 1.9),
    tokenMaterial('yellow', { roughness: 0.5, metalness: 0.08 }),
  )
  output.position.set(2.7, 0, 0)
  root.add(output)

  return {
    update(seconds) {
      inputs.forEach((input) => {
        input.position.x = -1.9 + Math.sin(seconds * 1.5 + input.userData.phase) * 0.08
      })
      planes.forEach((plane, i) => {
        plane.rotation.y = Math.sin(seconds * 1.1 + i) * 0.22
      })
      output.scale.y = 0.86 + Math.sin(seconds * 1.4) * 0.12
      output.rotation.y = seconds * 0.22
    },
    reset() {
      inputs.forEach((input) => {
        input.position.x = -1.9
      })
      planes.forEach((plane) => plane.rotation.set(0, 0, 0))
      output.scale.set(1, 1, 1)
      output.rotation.set(0, 0, 0)
    },
  }
}

function setupLoraLowRank({ root, camera }) {
  camera.position.set(5.5, 3.9, 6)
  lookAtOrigin(camera)

  const baseTiles = []
  for (let row = 0; row < 5; row += 1) {
    for (let col = 0; col < 5; col += 1) {
      const tile = new THREE.Mesh(
        new THREE.BoxGeometry(0.36, 0.07, 0.36),
        tokenMaterial((row + col) % 2 === 0 ? 'gray200' : 'gray100', { roughness: 0.9, metalness: 0 }),
      )
      tile.position.set((col - 2) * 0.44, -0.06, (row - 2) * 0.44)
      root.add(tile)
      baseTiles.push(tile)
    }
  }

  const leftRank = []
  const rightRank = []
  for (let i = 0; i < 5; i += 1) {
    const a = new THREE.Mesh(
      new THREE.BoxGeometry(0.22, 1.05, 0.18),
      tokenMaterial(PRIMARY_TOKENS[i % PRIMARY_TOKENS.length], { roughness: 0.45, metalness: 0.08 }),
    )
    a.position.set(-1.8, 0.36, (i - 2) * 0.28)
    root.add(a)
    leftRank.push(a)

    const b = new THREE.Mesh(
      new THREE.BoxGeometry(0.18, 0.88, 0.22),
      tokenMaterial(PRIMARY_TOKENS[(i + 2) % PRIMARY_TOKENS.length], { roughness: 0.45, metalness: 0.08 }),
    )
    b.position.set(1.8, 0.36, (i - 2) * 0.28)
    root.add(b)
    rightRank.push(b)
  }

  const bridge = new THREE.Mesh(
    new THREE.TorusGeometry(1.08, 0.045, 12, 72),
    tokenMaterial('yellow', { roughness: 0.34, metalness: 0.2 }),
  )
  bridge.rotation.x = Math.PI / 2
  bridge.position.y = 0.42
  root.add(bridge)

  const updatePatch = new THREE.Mesh(
    new THREE.BoxGeometry(1.22, 0.1, 1.22),
    tokenMaterial('blue', { roughness: 0.52, metalness: 0.06, transparent: true, opacity: 0.82 }),
  )
  updatePatch.position.y = 0.08
  root.add(updatePatch)

  return {
    update(seconds) {
      leftRank.forEach((bar, i) => {
        bar.scale.y = 0.74 + Math.sin(seconds * 1.7 + i) * 0.22
      })
      rightRank.forEach((bar, i) => {
        bar.scale.y = 0.74 + Math.cos(seconds * 1.5 + i) * 0.2
      })
      bridge.rotation.z = seconds * 0.72
      updatePatch.scale.setScalar(0.88 + Math.sin(seconds * 1.4) * 0.08)
      root.rotation.y = Math.sin(seconds * 0.32) * 0.16
    },
    reset() {
      leftRank.forEach((bar) => bar.scale.set(1, 1, 1))
      rightRank.forEach((bar) => bar.scale.set(1, 1, 1))
      bridge.rotation.set(Math.PI / 2, 0, 0)
      updatePatch.scale.set(1, 1, 1)
      root.rotation.set(0, 0, 0)
    },
  }
}

function setupScaledAttention3d({ root, camera }) {
  camera.position.set(6.4, 4.4, 6.6)
  lookAtOrigin(camera)

  const tiles = []
  const panels = [
    { name: 'q', x: -2.45, z: -1.15, rows: 5, cols: 2, token: 'red', delay: 0 },
    { name: 'k', x: -1.42, z: -1.15, rows: 2, cols: 5, token: 'blue', delay: 0.5 },
    { name: 'scores', x: -0.28, z: 0.05, rows: 5, cols: 5, token: 'orange', delay: 1 },
    { name: 'softmax', x: 1.28, z: 0.05, rows: 5, cols: 5, token: 'green', delay: 1.5 },
    { name: 'v', x: 2.62, z: -1.15, rows: 5, cols: 2, token: 'purple', delay: 2 },
  ]

  panels.forEach((panel, panelIndex) => {
    const frame = new THREE.Mesh(
      new THREE.BoxGeometry(panel.cols * 0.28 + 0.34, 0.045, panel.rows * 0.28 + 0.34),
      tokenMaterial('gray100', { roughness: 0.9, metalness: 0 }),
    )
    frame.position.set(panel.x + (panel.cols - 1) * 0.14, -0.08, panel.z + (panel.rows - 1) * 0.14)
    root.add(frame)

    for (let row = 0; row < panel.rows; row += 1) {
      for (let col = 0; col < panel.cols; col += 1) {
        const future = panel.name === 'scores' && col > row
        const token = future ? 'gray200' : panel.token
        const cube = new THREE.Mesh(
          new THREE.BoxGeometry(0.21, 0.12, 0.21),
          tokenMaterial(token, { roughness: 0.5, metalness: 0.04 }),
        )
        cube.position.set(panel.x + col * 0.28, 0.03, panel.z + row * 0.28)
        cube.userData = { row, col, panelIndex, panelName: panel.name, delay: panel.delay, baseY: cube.position.y }
        root.add(cube)
        tiles.push(cube)
      }
    }
  })

  const outputBars = []
  for (let i = 0; i < 4; i += 1) {
    const bar = new THREE.Mesh(
      new THREE.BoxGeometry(0.18, 0.72, 0.18),
      tokenMaterial(PRIMARY_TOKENS[(i + 1) % PRIMARY_TOKENS.length], { roughness: 0.42, metalness: 0.1 }),
    )
    bar.position.set(2.25 + i * 0.26, 0.34, 1.5)
    bar.userData.phase = i * 0.6
    root.add(bar)
    outputBars.push(bar)
  }

  const cursor = new THREE.Mesh(
    new THREE.BoxGeometry(1.55, 0.055, 0.08),
    tokenMaterial('yellow', { roughness: 0.42, metalness: 0.12 }),
  )
  cursor.position.set(1.84, 0.42, 0.05)
  root.add(cursor)

  addTube(root, [new THREE.Vector3(-1.95, 0.24, -0.75), new THREE.Vector3(-0.28, 0.38, 0.55)], 'orange', 0.025)
  addTube(root, [new THREE.Vector3(0.55, 0.3, 0.7), new THREE.Vector3(1.25, 0.36, 0.65)], 'green', 0.025)
  addTube(root, [new THREE.Vector3(1.95, 0.32, 0.65), new THREE.Vector3(2.55, 0.42, 1.45)], 'purple', 0.025)

  return {
    update(seconds) {
      const activeRow = (seconds * 1.25) % 5
      tiles.forEach((tile) => {
        const rowPulse = Math.max(0, 1 - Math.abs(tile.userData.row - activeRow) / 1.2)
        const panelPulse = 0.5 + Math.sin(seconds * 1.3 + tile.userData.panelIndex * 0.8 + tile.userData.row * 0.3) * 0.2
        const height = 0.12 + rowPulse * 0.36 + panelPulse * 0.05
        tile.scale.y = height / 0.12
        tile.position.y = height / 2
      })
      cursor.position.z = 0.05 + Math.floor(activeRow) * 0.28
      outputBars.forEach((bar, i) => {
        const height = 0.5 + Math.sin(seconds * 1.7 + bar.userData.phase) * 0.16 + i * 0.05
        bar.scale.y = height
        bar.position.y = height * 0.36
      })
      root.rotation.y = Math.sin(seconds * 0.28) * 0.16
    },
    reset() {
      root.rotation.set(0, 0, 0)
      tiles.forEach((tile) => {
        tile.scale.y = 1
        tile.position.y = tile.userData.baseY
      })
    },
  }
}

function setupMultiHeadMerge3d({ root, camera }) {
  camera.position.set(6.2, 4.2, 6.4)
  lookAtOrigin(camera)

  const heads = [
    { x: -1.95, z: -1.15, token: 'blue' },
    { x: -0.55, z: -1.15, token: 'green' },
    { x: -1.95, z: 0.45, token: 'orange' },
    { x: -0.55, z: 0.45, token: 'purple' },
  ]
  const cells = []
  heads.forEach((head, headIndex) => {
    const base = new THREE.Mesh(
      new THREE.BoxGeometry(1.02, 0.05, 1.02),
      tokenMaterial('gray100', { roughness: 0.9, metalness: 0 }),
    )
    base.position.set(head.x + 0.36, -0.08, head.z + 0.36)
    root.add(base)
    for (let row = 0; row < 4; row += 1) {
      for (let col = 0; col < 4; col += 1) {
        const hot = (row + headIndex) % 4 === col
        const cube = new THREE.Mesh(
          new THREE.BoxGeometry(0.18, hot ? 0.34 : 0.16, 0.18),
          tokenMaterial(hot ? 'red' : head.token, { roughness: 0.48, metalness: 0.06 }),
        )
        cube.position.set(head.x + col * 0.24, cube.geometry.parameters.height / 2, head.z + row * 0.24)
        cube.userData = { headIndex, row, col, baseHeight: cube.geometry.parameters.height }
        root.add(cube)
        cells.push(cube)
      }
    }
  })

  const strips = []
  heads.forEach((head, i) => {
    const strip = new THREE.Mesh(
      new THREE.BoxGeometry(0.84, 0.14, 0.18),
      tokenMaterial(head.token, { roughness: 0.44, metalness: 0.08 }),
    )
    strip.position.set(1.05, 0.22 + i * 0.18, -0.7 + i * 0.46)
    root.add(strip)
    strips.push(strip)
    addTube(root, [
      new THREE.Vector3(head.x + 0.7, 0.28, head.z + 0.35),
      new THREE.Vector3(0.4, 0.38 + i * 0.08, strip.position.z),
      strip.position.clone(),
    ], head.token, 0.02)
  })

  const projection = new THREE.Mesh(
    new THREE.BoxGeometry(0.62, 1.1, 1.7),
    tokenMaterial('yellow', { roughness: 0.42, metalness: 0.18 }),
  )
  projection.position.set(2.25, 0.62, 0)
  root.add(projection)
  addTube(root, [new THREE.Vector3(1.48, 0.62, 0), new THREE.Vector3(1.96, 0.62, 0)], 'yellow', 0.04)

  return {
    update(seconds) {
      cells.forEach((cell) => {
        const pulse = 0.85 + Math.sin(seconds * 2 + cell.userData.headIndex + cell.userData.row * 0.4) * 0.2
        cell.scale.y = pulse
        cell.position.y = (cell.userData.baseHeight * pulse) / 2
      })
      strips.forEach((strip, i) => {
        strip.scale.x = 0.82 + Math.sin(seconds * 1.6 + i) * 0.12
      })
      projection.rotation.y = Math.sin(seconds * 0.8) * 0.28
      root.rotation.y = Math.sin(seconds * 0.25) * 0.15
    },
    reset() {
      root.rotation.set(0, 0, 0)
      projection.rotation.set(0, 0, 0)
    },
  }
}

function setupMoeRouter3d({ root, camera }) {
  camera.position.set(6.4, 3.8, 6.6)
  lookAtOrigin(camera)

  const routes = [
    { token: 'blue', start: new THREE.Vector3(-2.4, 0.75, -1.2), end: new THREE.Vector3(1.9, 0.72, -1.25), delay: 0 },
    { token: 'orange', start: new THREE.Vector3(-2.4, 0.45, -0.7), end: new THREE.Vector3(1.9, 0.7, -0.35), delay: 0.18 },
    { token: 'green', start: new THREE.Vector3(-2.4, 0.15, -0.2), end: new THREE.Vector3(1.9, 0.68, 0.55), delay: 0.36 },
    { token: 'purple', start: new THREE.Vector3(-2.4, -0.15, 0.3), end: new THREE.Vector3(1.9, 0.66, 1.35), delay: 0.54 },
    { token: 'red', start: new THREE.Vector3(-2.4, -0.45, 0.8), end: new THREE.Vector3(1.9, 1.05, -0.35), delay: 0.72 },
    { token: 'yellow', start: new THREE.Vector3(-2.4, -0.75, 1.3), end: new THREE.Vector3(1.9, 0.98, 1.35), delay: 0.9 },
  ]

  const beads = []
  routes.forEach((route, i) => {
    const curve = new THREE.CatmullRomCurve3([
      route.start,
      new THREE.Vector3(-0.7, 0.9 + i * 0.03, route.start.z * 0.3),
      new THREE.Vector3(0.75, 0.7, route.end.z),
      route.end,
    ])
    route.curve = curve
    addTube(root, curve.getPoints(32), route.token, i === 4 ? 0.035 : 0.022, i === 4 ? 0.82 : 0.42)
    const bead = new THREE.Mesh(
      new THREE.SphereGeometry(0.13, 24, 12),
      tokenMaterial(route.token, { roughness: 0.36, metalness: 0.12 }),
    )
    bead.position.copy(route.start)
    root.add(bead)
    beads.push({ bead, route })
  })

  const experts = []
  ;['blue', 'orange', 'green', 'purple'].forEach((token, i) => {
    const tower = new THREE.Mesh(
      new THREE.BoxGeometry(0.62, 0.62, 0.55),
      tokenMaterial(token, { roughness: 0.45, metalness: 0.08 }),
    )
    tower.position.set(2.15, 0.3, -1.25 + i * 0.85)
    root.add(tower)
    experts.push(tower)
    for (let slot = 0; slot < 2; slot += 1) {
      const cube = new THREE.Mesh(
        new THREE.BoxGeometry(0.22, 0.22, 0.22),
        tokenMaterial(slot === 1 && i === 1 ? 'red' : token, { roughness: 0.38, metalness: 0.08 }),
      )
      cube.position.set(2.15 + (slot - 0.5) * 0.26, 0.78, -1.25 + i * 0.85)
      root.add(cube)
    }
  })

  const scoreWall = new THREE.Mesh(
    new THREE.BoxGeometry(0.08, 2.25, 2.8),
    tokenMaterial('gray100', { roughness: 0.92, metalness: 0 }),
  )
  scoreWall.position.set(-0.25, 0.15, 0)
  root.add(scoreWall)

  return {
    update(seconds) {
      beads.forEach(({ bead, route }) => {
        const t = (seconds * 0.22 + route.delay) % 1
        bead.position.copy(safeCurvePoint(route.curve, t))
        bead.scale.setScalar(0.88 + Math.sin(seconds * 5 + route.delay * 4) * 0.12)
      })
      experts.forEach((expert, i) => {
        expert.scale.y = 0.82 + Math.sin(seconds * 1.5 + i) * 0.18
        expert.position.y = 0.31 * expert.scale.y
      })
      root.rotation.y = Math.sin(seconds * 0.26) * 0.16
    },
    reset() {
      beads.forEach(({ bead, route }) => bead.position.copy(route.start))
      root.rotation.set(0, 0, 0)
    },
  }
}

function setupSpeculativeDecode3d({ root, camera }) {
  camera.position.set(5.8, 3.6, 6.2)
  lookAtOrigin(camera)

  const accepted = [
    new THREE.Vector3(-2.2, 0.15, 0),
    new THREE.Vector3(-1.3, 0.22, -0.15),
    new THREE.Vector3(-0.4, 0.25, 0.06),
    new THREE.Vector3(0.5, 0.2, -0.08),
  ]
  const rejected = [
    accepted[3],
    new THREE.Vector3(1.1, 0.58, -0.85),
    new THREE.Vector3(1.82, 0.8, -1.3),
  ]
  const target = [
    accepted[3],
    new THREE.Vector3(1.12, 0.12, 0.45),
    new THREE.Vector3(1.9, 0.12, 0.92),
  ]

  const acceptedCurve = new THREE.CatmullRomCurve3(accepted)
  const rejectedCurve = new THREE.CatmullRomCurve3(rejected)
  const targetCurve = new THREE.CatmullRomCurve3(target)
  addTube(root, acceptedCurve.getPoints(40), 'green', 0.035, 0.78)
  addTube(root, rejectedCurve.getPoints(32), 'red', 0.03, 0.72)
  addTube(root, targetCurve.getPoints(32), 'purple', 0.03, 0.72)

  const nodes = [
    ...accepted.map((position, i) => ({ position, token: i === 0 ? 'neutral' : 'green', scale: i === 0 ? 0.18 : 0.14 })),
    { position: rejected[1], token: 'red', scale: 0.13 },
    { position: rejected[2], token: 'red', scale: 0.13 },
    { position: target[1], token: 'purple', scale: 0.13 },
    { position: target[2], token: 'purple', scale: 0.13 },
  ].map((item) => {
    const mesh = new THREE.Mesh(
      new THREE.SphereGeometry(item.scale, 24, 12),
      tokenMaterial(item.token, { roughness: 0.36, metalness: 0.12 }),
    )
    mesh.position.copy(item.position)
    root.add(mesh)
    return mesh
  })

  const verifier = new THREE.Mesh(
    new THREE.TorusGeometry(1.28, 0.035, 12, 96),
    tokenMaterial('yellow', { roughness: 0.34, metalness: 0.18 }),
  )
  verifier.position.set(-0.2, 0.25, 0)
  verifier.rotation.x = Math.PI / 2
  root.add(verifier)

  const draftBead = new THREE.Mesh(
    new THREE.SphereGeometry(0.1, 20, 10),
    tokenMaterial('orange', { roughness: 0.35, metalness: 0.1 }),
  )
  root.add(draftBead)

  return {
    update(seconds) {
      const t = (seconds * 0.28) % 1
      draftBead.position.copy(safeCurvePoint(acceptedCurve, t))
      if (t > 0.72) draftBead.position.copy(safeCurvePoint(targetCurve, (t - 0.72) / 0.28))
      verifier.rotation.z = seconds * 0.9
      nodes.forEach((node, i) => {
        node.scale.setScalar(1 + Math.sin(seconds * 2.2 + i) * 0.12)
      })
      root.rotation.y = Math.sin(seconds * 0.28) * 0.18
    },
    reset() {
      draftBead.position.copy(accepted[0])
      root.rotation.set(0, 0, 0)
    },
  }
}

function setupRopeRotation3d({ root, camera }) {
  camera.position.set(5.4, 3.5, 6.4)
  lookAtOrigin(camera)

  const base = new THREE.Mesh(
    new THREE.BoxGeometry(5.2, 0.05, 2.2),
    tokenMaterial('gray100', { roughness: 0.9, metalness: 0 }),
  )
  base.position.set(0, -0.12, 0.22)
  root.add(base)

  const vectorGroups = []
  for (let i = 0; i < 5; i += 1) {
    const group = new THREE.Group()
    group.position.set((i - 2) * 0.9, 0.1, 0)
    root.add(group)
    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(0.38, 0.028, 12, 64),
      tokenMaterial(PRIMARY_TOKENS[i % PRIMARY_TOKENS.length], { roughness: 0.38, metalness: 0.12 }),
    )
    ring.rotation.x = Math.PI / 2
    group.add(ring)
    const q = makeVectorRod('red', 0.4)
    const k = makeVectorRod('blue', 0.33)
    q.userData.baseAngle = i * 0.52
    k.userData.baseAngle = i * 0.52 - 0.25
    group.add(q, k)
    vectorGroups.push({ group, q, k, phase: i * 0.5 })
  }

  const phaseLine = new THREE.Line(
    new THREE.BufferGeometry().setFromPoints(
      Array.from({ length: 26 }, (_, i) => {
        const x = (i / 25 - 0.5) * 4
        return new THREE.Vector3(x, -0.85 + Math.sin(i * 0.28) * 0.16, 1.2)
      }),
    ),
    new THREE.LineBasicMaterial({ color: TOKEN_HEX.purple, transparent: true, opacity: 0.82 }),
  )
  root.add(phaseLine)

  return {
    update(seconds) {
      vectorGroups.forEach(({ group, q, k, phase }, i) => {
        group.rotation.y = Math.sin(seconds * 0.6 + phase) * 0.22
        q.rotation.z = q.userData.baseAngle + seconds * (0.72 + i * 0.05)
        k.rotation.z = k.userData.baseAngle + seconds * (0.72 + i * 0.05) - 0.34
      })
      phaseLine.rotation.y = Math.sin(seconds * 0.32) * 0.2
      root.rotation.y = Math.sin(seconds * 0.22) * 0.12
    },
    reset() {
      vectorGroups.forEach(({ group, q, k }) => {
        group.rotation.set(0, 0, 0)
        q.rotation.z = q.userData.baseAngle
        k.rotation.z = k.userData.baseAngle
      })
      root.rotation.set(0, 0, 0)
    },
  }
}

function setupLogitLens3d({ root, camera }) {
  camera.position.set(6.2, 3.9, 6.8)
  lookAtOrigin(camera)

  const layers = [-2, -1, 0, 1, 2]
  const series = [
    { token: 'blue', ranks: [4, 3, 2, 1, 1] },
    { token: 'green', ranks: [2, 2, 3, 3, 4] },
    { token: 'orange', ranks: [5, 4, 4, 4, 3] },
    { token: 'purple', ranks: [1, 1, 1, 2, 2] },
    { token: 'red', ranks: [3, 5, 5, 5, 5] },
  ]

  layers.forEach((x, i) => {
    const column = new THREE.Mesh(
      new THREE.BoxGeometry(0.05, 2.25, 0.05),
      tokenMaterial('gray200', { roughness: 0.9, metalness: 0 }),
    )
    column.position.set(x, 0.05, 0)
    root.add(column)
    const cap = new THREE.Mesh(
      new THREE.BoxGeometry(0.24, 0.08, 0.24),
      tokenMaterial(PRIMARY_TOKENS[i % PRIMARY_TOKENS.length], { roughness: 0.5, metalness: 0.06 }),
    )
    cap.position.set(x, 1.25, 0)
    root.add(cap)
  })

  const beads = []
  series.forEach((item, seriesIndex) => {
    const points = item.ranks.map((rank, i) => new THREE.Vector3(layers[i], 1.18 - rank * 0.42, (seriesIndex - 2) * 0.22))
    const curve = new THREE.CatmullRomCurve3(points)
    addTube(root, curve.getPoints(64), item.token, item.token === 'blue' ? 0.04 : 0.024, item.token === 'blue' ? 0.9 : 0.58)
    const bead = new THREE.Mesh(
      new THREE.SphereGeometry(item.token === 'blue' ? 0.13 : 0.095, 20, 10),
      tokenMaterial(item.token, { roughness: 0.34, metalness: 0.12 }),
    )
    root.add(bead)
    beads.push({ bead, curve, delay: seriesIndex * 0.1 })
  })

  return {
    update(seconds) {
      beads.forEach(({ bead, curve, delay }) => {
        bead.position.copy(safeCurvePoint(curve, (seconds * 0.18 + delay) % 1))
      })
      root.rotation.y = Math.sin(seconds * 0.25) * 0.2
    },
    reset() {
      beads.forEach(({ bead, curve }) => bead.position.copy(safeCurvePoint(curve, 0)))
      root.rotation.set(0, 0, 0)
    },
  }
}

function setupSwigluFfn3d({ root, camera }) {
  camera.position.set(6.2, 3.6, 6.6)
  lookAtOrigin(camera)

  const input = makeBarStack(root, new THREE.Vector3(-2.4, 0, 0), 'blue', [0.55, 0.82, 0.48, 0.72])
  const up = makeBarStack(root, new THREE.Vector3(-0.95, 0.45, -0.85), 'orange', [0.45, 0.68, 0.9, 0.62, 0.8, 0.52])
  const gate = makeBarStack(root, new THREE.Vector3(-0.95, 0.05, 0.85), 'purple', [0.82, 0.42, 0.68, 0.96, 0.5, 0.74])
  const product = makeBarStack(root, new THREE.Vector3(0.75, 0.25, 0), 'red', [0.48, 0.35, 0.78, 0.84, 0.5, 0.62])
  const down = makeBarStack(root, new THREE.Vector3(2.35, 0, 0), 'green', [0.66, 0.52, 0.78, 0.58])

  const multiply = new THREE.Mesh(
    new THREE.TorusGeometry(0.38, 0.035, 12, 60),
    tokenMaterial('red', { roughness: 0.32, metalness: 0.18 }),
  )
  multiply.position.set(0.32, 0.62, 0)
  multiply.rotation.x = Math.PI / 2
  root.add(multiply)

  const routes = [
    addTube(root, [new THREE.Vector3(-1.9, 0.48, 0), new THREE.Vector3(-1.35, 0.95, -0.65), new THREE.Vector3(-0.95, 0.95, -0.85)], 'orange', 0.025),
    addTube(root, [new THREE.Vector3(-1.9, 0.42, 0), new THREE.Vector3(-1.35, 0.25, 0.65), new THREE.Vector3(-0.95, 0.55, 0.85)], 'purple', 0.025),
    addTube(root, [new THREE.Vector3(-0.25, 0.85, -0.7), new THREE.Vector3(0.25, 0.75, 0), new THREE.Vector3(0.75, 0.82, 0)], 'red', 0.028),
    addTube(root, [new THREE.Vector3(1.35, 0.75, 0), new THREE.Vector3(1.8, 0.58, 0), new THREE.Vector3(2.35, 0.48, 0)], 'green', 0.028),
  ]

  return {
    update(seconds) {
      ;[input, up, gate, product, down].forEach((stack, stackIndex) => {
        stack.forEach((bar, i) => {
          const height = bar.userData.baseHeight * (0.86 + Math.sin(seconds * 1.6 + stackIndex + i * 0.5) * 0.18)
          bar.scale.y = height / bar.userData.baseHeight
          bar.position.y = bar.userData.originY + (height - bar.userData.baseHeight) / 2
        })
      })
      multiply.rotation.z = seconds * 0.9
      routes.forEach((route, i) => {
        route.material.opacity = 0.44 + Math.sin(seconds * 1.8 + i) * 0.16
      })
      root.rotation.y = Math.sin(seconds * 0.26) * 0.16
    },
    reset() {
      root.rotation.set(0, 0, 0)
      multiply.rotation.set(Math.PI / 2, 0, 0)
    },
  }
}

function setupPagedKvCache3d({ root, camera }) {
  camera.position.set(6.2, 4.2, 6.6)
  lookAtOrigin(camera)

  const pages = []
  const pageTokens = ['blue', 'orange', 'green', 'purple', 'blue', 'green', 'orange', 'green', 'purple', 'gray100', 'gray100', 'gray100']
  for (let row = 0; row < 3; row += 1) {
    for (let col = 0; col < 4; col += 1) {
      const index = row * 4 + col
      const page = new THREE.Mesh(
        new THREE.BoxGeometry(0.38, 0.18, 0.38),
        tokenMaterial(pageTokens[index], { roughness: 0.48, metalness: 0.06 }),
      )
      page.position.set(0.85 + col * 0.52, 0.05, -0.82 + row * 0.52)
      page.userData = { row, col, index, baseY: page.position.y }
      root.add(page)
      pages.push(page)
    }
  }

  const requests = [
    { token: 'blue', y: 0.72, z: -1.1, targets: [0, 1, 2] },
    { token: 'orange', y: 0.42, z: -0.35, targets: [3, 4] },
    { token: 'green', y: 0.12, z: 0.4, targets: [5, 6, 7] },
    { token: 'purple', y: -0.18, z: 1.15, targets: [1, 8] },
  ]
  const beads = []
  requests.forEach((request, requestIndex) => {
    const requestBlock = new THREE.Mesh(
      new THREE.BoxGeometry(0.72, 0.22, 0.26),
      tokenMaterial(request.token, { roughness: 0.45, metalness: 0.08 }),
    )
    requestBlock.position.set(-2.2, request.y, request.z)
    root.add(requestBlock)

    request.targets.forEach((targetIndex, targetOffset) => {
      const target = pages[targetIndex].position
      const curve = new THREE.CatmullRomCurve3([
        requestBlock.position.clone(),
        new THREE.Vector3(-1.0, request.y + 0.35, (request.z + target.z) * 0.45),
        new THREE.Vector3(0.2, 0.38, target.z),
        target.clone().add(new THREE.Vector3(0, 0.18, 0)),
      ])
      addTube(root, curve.getPoints(32), request.token, requestIndex === 3 && targetIndex === 1 ? 0.034 : 0.02, 0.48)
      const bead = new THREE.Mesh(
        new THREE.SphereGeometry(0.075, 16, 8),
        tokenMaterial(request.token, { roughness: 0.36, metalness: 0.12 }),
      )
      root.add(bead)
      beads.push({ bead, curve, delay: requestIndex * 0.17 + targetOffset * 0.06 })
    })
  })

  const reused = new THREE.Mesh(
    new THREE.TorusGeometry(0.34, 0.025, 10, 48),
    tokenMaterial('green', { roughness: 0.36, metalness: 0.12 }),
  )
  reused.position.copy(pages[1].position).add(new THREE.Vector3(0, 0.32, 0))
  reused.rotation.x = Math.PI / 2
  root.add(reused)

  return {
    update(seconds) {
      pages.forEach((page) => {
        const pulse = Math.sin(seconds * 1.5 + page.userData.index * 0.35) * 0.08
        page.position.y = page.userData.baseY + Math.max(0, pulse)
      })
      beads.forEach(({ bead, curve, delay }) => {
        bead.position.copy(safeCurvePoint(curve, (seconds * 0.22 + delay) % 1))
      })
      reused.rotation.z = seconds * 1.2
      root.rotation.y = Math.sin(seconds * 0.24) * 0.16
    },
    reset() {
      pages.forEach((page) => {
        page.position.y = page.userData.baseY
      })
      root.rotation.set(0, 0, 0)
    },
  }
}

function addTube(root, points, token, radius = 0.026, opacity = 0.7) {
  const curve = new THREE.CatmullRomCurve3(points)
  const tube = new THREE.Mesh(
    new THREE.TubeGeometry(curve, 36, radius, 8, false),
    tokenMaterial(token, { roughness: 0.48, metalness: 0.08, transparent: opacity < 1, opacity }),
  )
  root.add(tube)
  return tube
}

function safeCurvePoint(curve, t) {
  return curve.getPointAt(THREE.MathUtils.clamp(Number.isFinite(t) ? t : 0, 0, 0.999))
}

function makeVectorRod(token, length) {
  const group = new THREE.Group()
  const shaft = new THREE.Mesh(
    new THREE.CylinderGeometry(0.025, 0.025, length, 12),
    tokenMaterial(token, { roughness: 0.38, metalness: 0.12 }),
  )
  shaft.rotation.z = Math.PI / 2
  shaft.position.x = length / 2
  const tip = new THREE.Mesh(
    new THREE.SphereGeometry(0.06, 16, 8),
    tokenMaterial(token, { roughness: 0.32, metalness: 0.12 }),
  )
  tip.position.x = length
  group.add(shaft, tip)
  return group
}

function makeBarStack(root, origin, token, values) {
  const bars = []
  values.forEach((value, i) => {
    const bar = new THREE.Mesh(
      new THREE.BoxGeometry(0.12, value, 0.12),
      tokenMaterial(token, { roughness: 0.42, metalness: 0.08 }),
    )
    bar.position.set(origin.x + i * 0.16, origin.y + value / 2, origin.z)
    bar.userData.baseHeight = value
    bar.userData.originY = origin.y + value / 2
    root.add(bar)
    bars.push(bar)
  })
  return bars
}

function disposeObject(object) {
  if (object.geometry) object.geometry.dispose()
  if (object.material) {
    const materials = Array.isArray(object.material) ? object.material : [object.material]
    for (const material of materials) {
      for (const value of Object.values(material)) {
        if (value && typeof value === 'object' && 'isTexture' in value) value.dispose()
      }
      material.dispose()
    }
  }
}
