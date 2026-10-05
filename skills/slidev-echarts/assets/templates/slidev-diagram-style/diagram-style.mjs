// Browser-safe runtime template. Copy beside setup/mermaid.ts into a Slidev deck.
// No runtime dependency on another skill or repository fixture.

const sequences = {
  colorset1: ['#9e1b32', '#000000', '#828282', '#1c1c1c', '#9c9c9c', '#363636', '#b5b5b5', '#333e48', '#cfcfcf', '#4f4f4f', '#e7e7e7', '#696969', '#f7f7f7', '#6d1222', '#e8002a', '#ffccd5'],
  colorset2: ['#9e1b32', '#007298', '#e77204', '#45842a', '#652f6c', '#f1c319', '#6d1222', '#004d66', '#994a00', '#294d19', '#431f47', '#98700c', '#e8002a', '#00ace6', '#ff9633', '#36b300', '#9e00b3', '#ffd332', '#333e48', '#4f4f4f', '#696969', '#828282', '#9c9c9c', '#b5b5b5', '#1c1c1c', '#363636', '#000000', '#cfcfcf', '#e7e7e7', '#ffccd5', '#cdf3ff', '#dbffcc', '#f9ccff', '#ffe5cc', '#fff4cc', '#f7f7f7'],
}

const renderQueues = new WeakMap()

function textOn(fill) {
  const rgb = [1, 3, 5].map(i => parseInt(fill.slice(i, i + 2), 16) / 255)
  const linear = rgb.map(c => c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)
  const luminance = linear[0] * 0.2126 + linear[1] * 0.7152 + linear[2] * 0.0722
  return (luminance + 0.05) / 0.05 >= 1.05 / (luminance + 0.05) ? '#000000' : '#ffffff'
}

/** Inject native Mermaid from the deck so the template has no package imports. */
export function createColorsetRenderer(mermaid, setup) {
  // Slidev can call its setup hook separately for each request. Share the queue
  // per native Mermaid instance, rather than per returned renderer function.
  let queue = renderQueues.get(mermaid)
  if (!queue) {
    queue = { pending: Promise.resolve(), serial: 0 }
    renderQueues.set(mermaid, queue)
  }
  return async (code, options) => {
    // Mermaid keeps shared initialization state. Serialize across slides.
    const render = queue.pending.then(async () => {
      const config = await setup() || {}
      const {
        theme: automaticSlidevTheme,
        colorsetPresentation,
        'colorset-presentation': colorsetPresentationAttribute,
        ...functionalOptions
      } = options || {}
      const preserveSource = colorsetPresentation === 'source' || colorsetPresentationAttribute === 'source'
      // Slidev injects theme:dark from its UI; source frontmatter still wins.
      mermaid.initialize(preserveSource
        ? { startOnLoad: false, ...functionalOptions, ...(automaticSlidevTheme ? { theme: automaticSlidevTheme } : {}) }
        : { startOnLoad: false, ...config, ...functionalOptions })
      // Mermaid measures text once. Wait for the deck font before layout so
      // async webfont loading cannot crop final glyphs in the generated SVG.
      if (!preserveSource && globalThis.document?.fonts) {
        await globalThis.document.fonts.load('16px "Open Sans"')
        await globalThis.document.fonts.ready
      }
      const { svg } = await mermaid.render(`slidev-colorset-${++queue.serial}`, code)
      if (preserveSource)
        return svg
      const document = new DOMParser().parseFromString(svg, 'image/svg+xml')
      const root = document.documentElement
      const active = mermaid.mermaidAPI?.getConfig?.() || config
      // Native SVGs are often transparent. Give black captions their actual
      // declared backing, including when the surrounding Slidev UI is dark.
      const canvas = active.themeVariables?.background || '#ffffff'
      if (!root.style.backgroundColor)
        root.style.setProperty('background-color', canvas)
      finishNativeLabels(root, active)
      return new XMLSerializer().serializeToString(root)
    })
    queue.pending = render.then(() => undefined, () => undefined)
    return render
  }
}

function finishNativeLabels(root, config) {
  // Native pie labels share one fill even when the slices have different fills.
  const slices = root.querySelectorAll('.pieCircle')
  const sliceLabels = root.querySelectorAll('.slice')
  slices.forEach((slice, i) => {
    const fill = slice.getAttribute('fill')
    if (sliceLabels[i] && /^#[0-9a-f]{6}$/i.test(fill || ''))
      sliceLabels[i].style.setProperty('fill', textOn(fill), 'important')
  })
  // Class compartments are meaningful lines. Native base styling reuses the
  // red body border paint for their separators, making those lines invisible.
  // Scope the repair to class nodes; ER row dividers have different backings.
  if (root.getAttribute('aria-roledescription') !== 'class' && !root.classList.contains('classDiagram'))
    return
  root.querySelectorAll('.node').forEach((node) => {
    const body = node.querySelector('.label-container > path[fill]:not([fill="none"]), .label-container > rect, rect.label-container')
    const nativeFill = body?.style.getPropertyValue('fill') || body?.getAttribute('fill')
    const fill = /^#[0-9a-f]{6}$/i.test(nativeFill || '')
      ? nativeFill
      : config.themeVariables?.mainBkg || config.themeVariables?.primaryColor
    if (!/^#[0-9a-f]{6}$/i.test(fill || ''))
      return
    node.querySelectorAll('.divider path, .divider line').forEach((divider) => {
      divider.style.setProperty('stroke', textOn(fill), 'important')
      divider.style.setProperty('fill', 'none', 'important')
    })
  })
}

/** Deck-wide Mermaid defaults: ordinary fences inherit paint and compact layout. */
export function mermaidColorsetConfig(selected = 'colorset1') {
  const scale = sequences[selected]
  if (!scale)
    throw new Error(`Unknown diagram colorset: ${selected}`)
  const extended = selected === 'colorset2'
  const primary = scale[0]
  const secondary = scale[1]
  const tertiary = scale[2]
  const note = extended ? scale[3] : secondary
  const state = extended ? secondary : primary
  const task = extended ? secondary : primary
  const activeTask = extended ? tertiary : secondary
  const doneTask = extended ? scale[3] : tertiary
  const ink = '#000000'
  const surface = '#ffffff'
  const muted = '#696969'
  const quiet = '#e7e7e7'
  const variables = {
    darkMode: false,
    fontFamily: '"Open Sans", Arial, sans-serif',
    fontSize: '16px',
    background: surface,
    primaryColor: primary,
    primaryBorderColor: primary,
    primaryTextColor: textOn(primary),
    secondaryColor: secondary,
    secondaryBorderColor: secondary,
    secondaryTextColor: textOn(secondary),
    tertiaryColor: tertiary,
    tertiaryBorderColor: tertiary,
    tertiaryTextColor: textOn(tertiary),
    lineColor: muted,
    textColor: ink,
    mainBkg: primary,
    nodeBkg: primary,
    nodeBorder: primary,
    nodeTextColor: textOn(primary),
    clusterBkg: quiet,
    clusterBorder: '#9c9c9c',
    defaultLinkColor: muted,
    edgeLabelBackground: surface,
    labelColor: textOn(secondary),
    titleColor: ink,
    noteBkgColor: note,
    noteBorderColor: note,
    noteTextColor: textOn(note),
    actorBkg: primary,
    actorBorder: primary,
    actorTextColor: textOn(primary),
    actorLineColor: muted,
    signalColor: muted,
    signalTextColor: ink,
    labelBoxBkgColor: quiet,
    labelBoxBorderColor: '#9c9c9c',
    labelTextColor: ink,
    loopTextColor: ink,
    activationBkgColor: tertiary,
    activationBorderColor: tertiary,
    sequenceNumberColor: textOn(muted),
    classText: textOn(primary),
    transitionColor: muted,
    stateLabelColor: textOn(state),
    stateBkg: state,
    labelBackgroundColor: secondary,
    compositeBackground: quiet,
    altBackground: '#cfcfcf',
    compositeTitleBackground: quiet,
    compositeBorder: state,
    commitLabelColor: ink,
    commitLabelBackground: surface,
    tagLabelColor: ink,
    tagLabelBackground: quiet,
    sectionBkgColor: quiet,
    altSectionBkgColor: '#cfcfcf',
    sectionBkgColor2: quiet,
    taskBkgColor: task,
    taskBorderColor: task,
    taskTextColor: textOn(task),
    taskTextDarkColor: ink,
    taskTextLightColor: surface,
    taskTextOutsideColor: ink,
    activeTaskBkgColor: activeTask,
    activeTaskBorderColor: activeTask,
    doneTaskBkgColor: doneTask,
    doneTaskBorderColor: doneTask,
    critBkgColor: primary,
    critBorderColor: primary,
    excludeBkgColor: quiet,
    gridColor: '#9c9c9c',
    todayLineColor: '#e8002a',
    pieTitleTextColor: ink,
    pieLegendTextColor: ink,
    pieSectionTextColor: surface,
    pieStrokeColor: surface,
    pieStrokeWidth: '0px',
    pieOuterStrokeWidth: '0px',
    pieOuterStrokeColor: surface,
    pieOpacity: 1,
    quadrant1Fill: extended ? '#dbffcc' : surface,
    quadrant2Fill: extended ? '#cdf3ff' : quiet,
    quadrant3Fill: extended ? '#f9ccff' : '#cfcfcf',
    quadrant4Fill: extended ? '#ffe5cc' : quiet,
    quadrant1TextFill: ink,
    quadrant2TextFill: ink,
    quadrant3TextFill: ink,
    quadrant4TextFill: ink,
    quadrantPointFill: extended ? secondary : primary,
    quadrantPointTextFill: ink,
    quadrantXAxisTextFill: ink,
    quadrantYAxisTextFill: ink,
    quadrantInternalBorderStrokeFill: muted,
    quadrantExternalBorderStrokeFill: muted,
    quadrantTitleFill: ink,
    archEdgeColor: muted,
    archEdgeArrowColor: muted,
    archEdgeWidth: '3',
    archGroupBorderColor: '#9c9c9c',
    archGroupBorderWidth: '1px',
    errorBkgColor: quiet,
    errorTextColor: ink,
    THEME_COLOR_LIMIT: 12,
    xyChart: {
      backgroundColor: surface,
      titleColor: ink,
      xAxisLabelColor: ink,
      xAxisTitleColor: ink,
      xAxisTickColor: muted,
      xAxisLineColor: muted,
      yAxisLabelColor: ink,
      yAxisTitleColor: ink,
      yAxisTickColor: muted,
      yAxisLineColor: muted,
      plotColorPalette: scale.slice(0, extended ? 6 : 5).join(', '),
    },
    radar: {
      axisColor: ink,
      axisLabelColor: ink,
      graticuleColor: '#828282',
      legendBoxBorderColor: '#9c9c9c',
      legendBoxBackgroundColor: surface,
    },
  }
  // Explicit finite colors prevent Mermaid's generated hue/lightness variants.
  scale.slice(0, 12).forEach((fill, i) => {
    variables[`cScale${i}`] = fill
    variables[`cScalePeer${i}`] = fill
    variables[`cScaleLabel${i}`] = textOn(fill)
    variables[`cScaleInv${i}`] = textOn(fill)
    variables[`pie${i + 1}`] = fill
    if (i < 8) {
      variables[`fillType${i}`] = fill
      variables[`git${i}`] = fill
      variables[`gitInv${i}`] = textOn(fill)
      variables[`gitBranchLabel${i}`] = textOn(fill)
      variables[`venn${i + 1}`] = fill
    }
  })

  return {
    theme: 'base',
    darkMode: false,
    fontFamily: variables.fontFamily,
    themeVariables: variables,
    // Mermaid places these rules inside its SVG, including Slidev shadow roots.
    themeCSS: `
      .node > rect, .node > circle, .node > ellipse, .node > polygon,
      .node > path, rect.actor, .note, .task, .task0, .task1, .task2, .task3 {
        stroke-width: 0 !important;
      }
      .edgeLabel, .edgeLabel text, .edgeLabel span, .edgeLabel p,
      .edgeLabel .label, .edgeLabel .nodeLabel, .edgeLabel .label text {
        color: ${ink} !important; fill: ${ink} !important;
      }
      .edgeLabel .labelBkg, .edgeLabel rect {
        fill: ${surface} !important; background-color: ${surface} !important;
      }
      .edgeLabel span, .edgeLabel p { background-color: ${surface} !important; }
      .cluster-label, .cluster-label text, .cluster-label span,
      .statediagram-cluster .cluster-label, .statediagram-cluster .cluster-label text {
        color: ${ink} !important; fill: ${ink} !important;
      }
      .row-rect-odd > path:not([fill="none"]) { fill: ${surface} !important; }
      .row-rect-even > path:not([fill="none"]) { fill: ${quiet} !important; }
      .attribute-type, .attribute-name, .attribute-keys, .attribute-comment,
      .attribute-type span, .attribute-name span, .attribute-keys span,
      .attribute-comment span, .attribute-type p, .attribute-name p,
      .attribute-keys p, .attribute-comment p {
        color: ${ink} !important; fill: ${ink} !important;
      }
    `,
    flowchart: { padding: 6, nodeSpacing: 24, rankSpacing: 32, subGraphTitleMargin: { top: 4, bottom: 12 } },
    state: { padding: 6, nodeSpacing: 28, rankSpacing: 32 },
    class: { padding: 6, nodeSpacing: 28, rankSpacing: 36 },
    er: { entityPadding: 6, diagramPadding: 6, nodeSpacing: 60, rankSpacing: 80 },
    sequence: { height: 36, boxMargin: 6, noteMargin: 8, messageMargin: 28 },
    mindmap: { padding: 6 },
    block: { padding: 6 },
    requirement: { rect_padding: 6 },
  }
}
