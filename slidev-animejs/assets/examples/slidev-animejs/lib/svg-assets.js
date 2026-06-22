import drawableCircuitSvg from '../assets/animated-svg/drawable-circuit.svg?raw'
import interactiveHotspotsSvg from '../assets/animated-svg/interactive-hotspots.svg?raw'
import morphingBadgeSvg from '../assets/animated-svg/morphing-badge.svg?raw'
import motionOrbitSvg from '../assets/animated-svg/motion-orbit.svg?raw'
import staggerDashboardSvg from '../assets/animated-svg/stagger-dashboard.svg?raw'
import timelineMachineSvg from '../assets/animated-svg/timeline-machine.svg?raw'

export const svgAssetOrder = [
  'drawable-circuit',
  'motion-orbit',
  'morphing-badge',
  'stagger-dashboard',
  'timeline-machine',
  'interactive-hotspots',
]

export const svgAssetSvgs = {
  'drawable-circuit': drawableCircuitSvg,
  'motion-orbit': motionOrbitSvg,
  'morphing-badge': morphingBadgeSvg,
  'stagger-dashboard': staggerDashboardSvg,
  'timeline-machine': timelineMachineSvg,
  'interactive-hotspots': interactiveHotspotsSvg,
}

export const svgAssetSpecs = {
  'drawable-circuit': {
    title: 'Drawable Circuit',
    summary: 'Independent circuit paths and nodes for path draw-on, node pulse, and staggered signal sequencing.',
    file: 'assets/animated-svg/drawable-circuit.svg',
    api: ['svg.createDrawable', 'animate', 'stagger'],
    selectors: ['.svg-drawable', '.svg-node', '[data-anime-group="drawables"]'],
    clickStory: 'Click steps change the draw origin and node emphasis while the SVG structure stays stable.',
  },
  'motion-orbit': {
    title: 'Motion Orbit',
    summary: 'A routed orbit path with a traveler group, pulses, and rings for path-following motion.',
    file: 'assets/animated-svg/motion-orbit.svg',
    api: ['svg.createMotionPath', 'svg.createDrawable', 'animate'],
    selectors: ['#orbit-path', '#orbit-traveler', '.orbit-ring', '.orbit-pulse'],
    clickStory: 'Click steps change ring direction and route timing without touching path geometry.',
  },
  'morphing-badge': {
    title: 'Morphing Badge',
    summary: 'One visible source path plus hidden compatible target paths for controlled shape morphing.',
    file: 'assets/animated-svg/morphing-badge.svg',
    api: ['svg.morphTo', 'animate', 'stagger'],
    selectors: ['#badge-source', '#badge-target-star', '#badge-target-wave', '#badge-target-diamond', '.badge-spark'],
    clickStory: 'Click steps pick diamond, star, or wave targets through the same source path.',
  },
  'stagger-dashboard': {
    title: 'Stagger Dashboard',
    summary: 'Repeated cards, bars, and status dots sized for staggered entrance and metric animation.',
    file: 'assets/animated-svg/stagger-dashboard.svg',
    api: ['animate', 'stagger'],
    selectors: ['.dashboard-card', '.dashboard-bar', '.dashboard-dot'],
    clickStory: 'Click steps change stagger origin and bar reach while preserving dashboard layout.',
  },
  'timeline-machine': {
    title: 'Timeline Machine',
    summary: 'Cable paths, gear, conveyor block, and signal lamps for label-based timeline choreography.',
    file: 'assets/animated-svg/timeline-machine.svg',
    api: ['createTimeline', 'svg.createDrawable', 'animate'],
    selectors: ['.machine-cable', '.machine-gear', '.machine-block', '.machine-signal'],
    clickStory: 'Click steps vary conveyor distance and signal overlap inside one repeatable timeline.',
  },
  'interactive-hotspots': {
    title: 'Interactive Hotspots',
    summary: 'Map regions, a route, hotspots, and callouts for pointer or click-driven state animation.',
    file: 'assets/animated-svg/interactive-hotspots.svg',
    api: ['svg.createDrawable', 'animate', 'stagger'],
    selectors: ['.map-route', '.map-hotspot', '.map-callout', '[data-region]'],
    clickStory: 'Click steps rotate the active hotspot emphasis from west to center to east.',
  },
}

export function svgAssetSpec(type) {
  return {
    slug: type,
    ...svgAssetSpecs[type],
  }
}
