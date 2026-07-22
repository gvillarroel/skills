---
theme: default
title: Slidev ECharts Chart-Type Lab
info: |
  A validation deck for mastering Apache ECharts chart types inside Slidev through shared synthetic data, reusable Vue components, and click-driven animation tests.
transition: slide-left
mdc: true
drawings:
  persist: false
---

# Slidev + Apache ECharts

<div class="hero-grid">
  <div class="hero-copy">
    <p class="eyebrow">Chart-type lab</p>
    <h2>One reusable Slidev pattern across every ECharts chart installer.</h2>
    <p>
      This deck uses shared synthetic data files and one animation harness to test
      render quality, update transitions, labels, legends, and responsive sizing.
    </p>
    <div class="hero-facts">
      <span>23 chart types</span>
      <span>SVG replay checks</span>
      <span>Shared JSON data</span>
      <span>Click-driven updates</span>
    </div>
  </div>
  <MarketMixChart />
</div>

---

# Shared Data Model

<div class="validation-grid">
  <div>
    <p class="eyebrow">Time</p>
    <h2>Monthly and stream data feed trends, bars, rivers, and routes.</h2>
    <p><code>data/time-series.json</code> and <code>data/river.json</code> keep temporal examples deterministic.</p>
  </div>
  <div>
    <p class="eyebrow">Structure</p>
    <h2>Hierarchies and relationships feed tree, graph, sankey, chord, and radial views.</h2>
    <p><code>data/hierarchy.json</code> and <code>data/relationships.json</code> let chart types tell the same system story.</p>
  </div>
  <div>
    <p class="eyebrow">Shape</p>
    <h2>Distribution, spatial, financial, and categorical files cover specialized charts.</h2>
    <p>The option builders reuse the same values so differences come from chart grammar, not unrelated data.</p>
  </div>
</div>

---

# Wrapper Contract

<div class="two-column">
  <div class="checklist">
    <p class="eyebrow">Reusable component</p>
    <h2>Keep lifecycle, resize, and chart registration outside Markdown.</h2>
    <ul>
      <li>Register every chart, component, feature, and renderer used by the option builders.</li>
      <li>Initialize only after the container has nonzero width and height.</li>
      <li>Resize from <code>ResizeObserver</code> so hidden Slidev slides hydrate safely.</li>
      <li>Drive updates with <code>$clicks</code>, stable series IDs, and SVG replay hooks.</li>
    </ul>
  </div>
  <pre class="code-panel"><code>&lt;ChartTypeSlide
  chart-type="line"
  :step="$clicks"
  renderer="svg"
/&gt;</code></pre>
</div>

---

# SVG Replay Contract

<div class="validation-grid">
  <div>
    <p class="eyebrow">Render first</p>
    <h2>Chart-type slides render the real ECharts SVG output.</h2>
    <p>The replay pass targets the SVG that ECharts emitted, so chart geometry, labels, gradients, and legends remain authoritative.</p>
  </div>
  <div>
    <p class="eyebrow">Replay</p>
    <h2>A wrapper class restarts motion without rebuilding the chart.</h2>
    <p>The button removes and re-adds the replay class, which lets verification prove the animation can run more than once.</p>
  </div>
  <div>
    <p class="eyebrow">Selectors</p>
    <h2>Validation rejects missing SVG replay affordances.</h2>
    <p>The script checks renderer mode, replay controls, animated marks, text, and fragile empty SVG surfaces.</p>
  </div>
</div>

---

# Generated SVG Path Draw

<GeneratedSvgMotion mode="path" :step="$clicks" />

<v-clicks class="chart-clicks">

- Generate a curve from deterministic control points.
- Reveal the path with SVG stroke dash animation.
- Keep nodes and labels inspectable after replay.

</v-clicks>

---

# Generated SVG Particle Field

<GeneratedSvgMotion mode="particles" :step="$clicks" />

<v-clicks class="chart-clicks">

- Generate particle positions from polar coordinates.
- Replay staggered dots and link arrival.
- Preserve a stable final frame for screenshots.

</v-clicks>

---

# Generated SVG Morph Bands

<GeneratedSvgMotion mode="bands" :step="$clicks" />

<v-clicks class="chart-clicks">

- Generate wave bands from baseline and amplitude values.
- Recompute path geometry as the click-state changes.
- Replay layered band entrance without replacing the SVG.

</v-clicks>

---

# Generated SVG Glyph Stack

<GeneratedSvgMotion mode="glyphs" :step="$clicks" />

<v-clicks class="chart-clicks">

- Generate repeated glyph rows from a small model.
- Animate compact marks without layout shift.
- Validate that generated SVG surfaces replay like charts.

</v-clicks>

---

# Narrative Chart Build

<RevenueStory :step="$clicks" />

<v-clicks class="chart-clicks">

- Move from baseline to a product-qualified scenario.
- Add partner lift while keeping the baseline visible.
- End on a clean evidence frame for the recorder.

</v-clicks>

---

# Multi-Chart Dashboard

<ExecutiveDashboard :step="$clicks" />

<v-clicks class="chart-clicks">

- Reweight the channel mix without changing layout.
- Update all chart instances from one scenario state.
- Stabilize labels and KPIs before the video advances.

</v-clicks>

---

# Spotlight Composition

<CompositionScene scene="spotlight" :step="$clicks" />

<v-clicks class="chart-clicks">

- Give the chart most of the frame.
- Let callouts reinforce the changing stream.
- Hold the final visual as a usable still frame.

</v-clicks>

---

# Comparison Composition

<CompositionScene scene="comparison" :step="$clicks" />

<v-clicks class="chart-clicks">

- Separate magnitude and portfolio quality.
- Synchronize both charts from the same click state.
- Finish with aligned axes, legends, and captions.

</v-clicks>

---

# Line Chart

<ChartTypeSlide chart-type="line" :step="$clicks" />

<v-clicks class="chart-clicks">

- Update the scenario values while the baseline remains anchored.
- Preserve continuity with stable series IDs and smooth line interpolation.
- Confirm the final state keeps readable axes and legend.

</v-clicks>

---

# Bar Chart

<ChartTypeSlide chart-type="bar" :step="$clicks" />

<v-clicks class="chart-clicks">

- Grow bars from previous to current product contribution.
- Keep category order stable while values change.
- Reveal labels only when the final state has enough space.

</v-clicks>

---

# Pie Chart

<ChartTypeSlide chart-type="pie" :step="$clicks" />

<v-clicks class="chart-clicks">

- Render the initial part-to-whole view.
- Morph the same named slices into a donut.
- Update the mix without changing the category identity.

</v-clicks>

---

# Scatter Chart

<ChartTypeSlide chart-type="scatter" :step="$clicks" />

<v-clicks class="chart-clicks">

- Plot opportunity confidence against impact.
- Move points while visualMap keeps effort encoded as size and color.
- Check that tooltips retain tuple context.

</v-clicks>

---

# Radar Chart

<ChartTypeSlide chart-type="radar" :step="$clicks" />

<v-clicks class="chart-clicks">

- Compare current and target capability profiles.
- Expand the current polygon toward the target.
- Keep axis labels outside the shape and visible.

</v-clicks>

---

# Map Chart

<ChartTypeSlide chart-type="map" :step="$clicks" />

<v-clicks class="chart-clicks">

- Register the synthetic GeoJSON map before setting options.
- Update regional values through the visual scale.
- Verify region labels remain readable after the choropleth morph.

</v-clicks>

---

# Tree Chart

<ChartTypeSlide chart-type="tree" :step="$clicks" />

<v-clicks class="chart-clicks">

- Show the growth-system parent-child structure.
- Update leaf values without collapsing branches.
- Keep left-to-right labels clear inside the slide frame.

</v-clicks>

---

# Treemap Chart

<ChartTypeSlide chart-type="treemap" :step="$clicks" />

<v-clicks class="chart-clicks">

- Reuse portfolio hierarchy as nested rectangles.
- Reflow area as allocations change.
- Keep group labels visible without breadcrumb noise.

</v-clicks>

---

# Graph Chart

<ChartTypeSlide chart-type="graph" :step="$clicks" />

<v-clicks class="chart-clicks">

- Render node-link topology in a deterministic circular layout.
- Update node size and link weight.
- Use adjacency emphasis without relying on force randomness.

</v-clicks>

---

# Chord Chart

<ChartTypeSlide chart-type="chord" :step="$clicks" />

<v-clicks class="chart-clicks">

- Show category arcs and overlap ribbons.
- Animate link value changes while keeping node names stable.
- Keep chord labels short because radial space is limited.

</v-clicks>

---

# Gauge Chart

<ChartTypeSlide chart-type="gauge" :step="$clicks" />

<v-clicks class="chart-clicks">

- Present one headline readiness ratio.
- Use ECharts value animation for the needle and detail text.
- Avoid extra series that would dilute the single KPI.

</v-clicks>

---

# Funnel Chart

<ChartTypeSlide chart-type="funnel" :step="$clicks" />

<v-clicks class="chart-clicks">

- Show ordered conversion attrition.
- Morph segment widths as improved conversion data appears.
- Keep labels inside the funnel for scan speed.

</v-clicks>

---

# Parallel Chart

<ChartTypeSlide chart-type="parallel" :step="$clicks" />

<v-clicks class="chart-clicks">

- Compare segment profiles across five normalized dimensions.
- Animate polyline changes without changing axis order.
- Keep all dimensions on the same 50-100 scale.

</v-clicks>

---

# Sankey Chart

<ChartTypeSlide chart-type="sankey" :step="$clicks" />

<v-clicks class="chart-clicks">

- Show directed lead flow across stages.
- Update link widths while preserving path semantics.
- Use gradient links to reinforce source-to-target movement.

</v-clicks>

---

# Boxplot Chart

<ChartTypeSlide chart-type="boxplot" :step="$clicks" />

<v-clicks class="chart-clicks">

- Compare cohort distributions with five-number summaries.
- Animate range and median changes.
- Keep all boxes on one scale for fair comparison.

</v-clicks>

---

# Candlestick Chart

<ChartTypeSlide chart-type="candlestick" :step="$clicks" />

<v-clicks class="chart-clicks">

- Show open-high-low-close interval movement.
- Shift later-period candles to test update transitions.
- Preserve conventional up/down colors.

</v-clicks>

---

# Effect Scatter Chart

<ChartTypeSlide chart-type="effectScatter" :step="$clicks" />

<v-clicks class="chart-clicks">

- Reuse opportunity points from the scatter slide.
- Enable ripple effects for priority emphasis.
- Confirm animated effects do not obscure the axis reading.

</v-clicks>

---

# Lines Chart

<ChartTypeSlide chart-type="lines" :step="$clicks" />

<v-clicks class="chart-clicks">

- Draw synthetic origin-destination routes on a planning grid.
- Preserve direction with SVG-safe arrow endpoints.
- Vary route width to show volume without a map dependency.

</v-clicks>

---

# Heatmap Chart

<ChartTypeSlide chart-type="heatmap" :step="$clicks" />

<v-clicks class="chart-clicks">

- Show day-hour engagement intensity.
- Animate cell value changes through a fixed visualMap.
- Reveal labels only in the final state.

</v-clicks>

---

# Pictorial Bar Chart

<ChartTypeSlide chart-type="pictorialBar" :step="$clicks" />

<v-clicks class="chart-clicks">

- Encode magnitude with repeated symbols.
- Animate symbol repetition as capacity grows.
- Use pictorial bars only when symbols help recall.

</v-clicks>

---

# Theme River Chart

<ChartTypeSlide chart-type="themeRiver" :step="$clicks" />

<v-clicks class="chart-clicks">

- Show channel volume as flowing layers over time.
- Rebalance stream thickness with deterministic rows.
- Keep stream names stable for legend-driven reading.

</v-clicks>

---

# Sunburst Chart

<ChartTypeSlide chart-type="sunburst" :step="$clicks" />

<v-clicks class="chart-clicks">

- Reuse the portfolio hierarchy as radial rings.
- Morph leaf weights while preserving hierarchy.
- Keep labels short enough for curved radial space.

</v-clicks>

---

# Custom Chart

<ChartTypeSlide chart-type="custom" :step="$clicks" />

<v-clicks class="chart-clicks">

- Render domain-specific timeline ranges with <code>renderItem</code>.
- Animate range endpoints through encoded x dimensions.
- Use custom series only when built-in marks are not expressive enough.

</v-clicks>

---

# Validation Targets

<div class="validation-grid four-up">
  <div>
    <p class="eyebrow">Build</p>
    <h2>The production deck must compile all chart modules.</h2>
    <p><code>npm run build</code> catches missing ECharts installers and invalid option shapes.</p>
  </div>
  <div>
    <p class="eyebrow">Browser</p>
    <h2>Every chart and generated SVG slide must render a replayable surface.</h2>
    <p>Playwright checks SVG renderer mode, visible marks, labels, replay controls, and click-driven updates.</p>
  </div>
  <div>
    <p class="eyebrow">Video</p>
    <h2>The recorder must traverse every slide and click state.</h2>
    <p><code>npm run video</code> writes MP4/WebM, screenshots, and a verification manifest.</p>
  </div>
  <div>
    <p class="eyebrow">Reference</p>
    <h2>Every chart type has a dedicated skill reference.</h2>
    <p>Reference files document data shape, animation pattern, display guidance, and common pitfalls.</p>
  </div>
</div>
