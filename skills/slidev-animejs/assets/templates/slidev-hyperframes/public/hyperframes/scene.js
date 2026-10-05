import { SCENE_DURATION, sceneState, sceneMarkup } from './scene-model.js'
import palettes from './colorsets.json' with { type: 'json' }

const params = new URL(document.baseURI).searchParams
const selected = params.get('colorset') === 'colorset2' ? 'colorset2' : 'colorset1'
const compact = params.get('compact') === '1'
const root = document.querySelector('[data-composition-id]')
if (compact) { root.dataset.width = '420'; root.dataset.height = '260' }
const palette = palettes.colorsets[selected]
root.dataset.colorset = selected

function renderAt(seconds) {
  const state = sceneState(seconds)
  root.dataset.sceneTime = String(state.time)
  root.dataset.valveOpen = String(state.valveOpen)
  root.dataset.level = String(state.level)
  root.dataset.parcelProgress = String(state.parcelProgress)
  root.innerHTML = sceneMarkup(state.time, palette, compact)
  return state
}
const clock = { seconds: 0 }
const timeline = gsap.timeline({ paused: true }).to(clock, {
  seconds: SCENE_DURATION, duration: SCENE_DURATION, ease: 'none',
  onUpdate: () => renderAt(clock.seconds),
}, 0)
window.__timelines = window.__timelines || {}
window.__timelines[root.dataset.compositionId] = timeline
window.explainer = { renderAt, stateAt: sceneState, seek: seconds => { timeline.totalTime(sceneState(seconds).time, false); return renderAt(clock.seconds) } }
renderAt(0)
await document.fonts.load('600 24px "Open Sans"')
await document.fonts.ready
window.__renderReady = true
