# Pattern Opportunities From Data Visualization Books

This note summarizes reusable opportunities for the current skill pattern libraries after reviewing the downloaded data visualization books. It is intentionally written as original pattern guidance, not as copied book content.

## Source Processing

All eight downloaded or mirrored sources from the initial book list are marked `processed` in `source-processing-status.md`. Each source has a concise note under `source-notes/` with local evidence paths, assimilated guidance, target pattern areas, and a copyright/use boundary.

## Current Pattern Coverage

The current D3 and video pattern surface already covers many chart families that appear across the reviewed books:

- Distributions: histogram, boxplot, violin, ridgeline, ECDF, beeswarm, mirrored beeswarm, density contours, hexbin, rectangular binning, dot plot, point-range, and forecast fan.
- Interaction: brush handles, lasso selection, ordinal brushing, focus and context, zoom to bounds, cursor lines, zoomable bars, and "you draw it" interactions.
- Layouts: facets, scatterplot matrix, tables with inline bars or sparklines, pivot heat tables, parallel coordinates, treemaps, alluvial diagrams, and small multiples.
- Maps: choropleths, bivariate choropleths, cartograms, bubble maps, spike maps, projection comparisons, and tile-based maps.
- Animation/video: progressive reveal, guided comparison, density management, metro-style routing, repair contracts, and visual hierarchy checks.

The main gap is not missing basic chart types. The best opportunities are composite patterns, interaction state contracts, and validation rules that make existing chart patterns more defensible and easier to choose.

## Recommended Promotions

### 1. Distribution Alternatives Composite

Create a reusable D3 pattern that compares multiple distribution encodings from the same dataset: raw points, jittered points, beeswarm, boxplot, violin, ridgeline, half-eye or interval summary, and compact dot plot. This should be a decision pattern, not just a gallery.

Recommended owner: `skills/d3-animated-svg/`

Why it matters:

- Current coverage has many individual distribution patterns, but not a single route that teaches when each representation is preferable.
- The Cedric Scherer workshop materials and the Wilke/R Graphics sources repeatedly point toward richer alternatives to default bar or box views.
- This would directly improve explanatory charts, quality audits, and video scenes where the system needs to show why a distribution summary is credible.

Pattern contract:

- Inputs: numeric value, grouping variable, optional weight, optional uncertainty interval.
- States: raw sample, overplotting-managed sample, summary overlay, uncertainty overlay, final annotated comparison.
- Validation: sample points must remain visible or intentionally aggregated; group comparisons must share a scale; legends or labels must explain interval semantics.

### 2. Visual Grammar Contract

Add a compact metadata contract for generated patterns: data variables, aesthetic mappings, statistical transform, scale, coordinate system, facet/grouping rule, annotation layer, and interaction state.

Recommended owner: `skills/d3-animated-svg/` or shared video pattern references.

Why it matters:

- The ggplot2 and Wilke sources reinforce that visualizations are mappings from data into visual aesthetics, mediated by scales and transformations.
- Current animated patterns can be visually polished while still underspecifying what data variable controls each visual channel.
- A metadata contract would make audits more precise and reduce generic decorative output.

Pattern contract:

- Every reusable pattern should state `data_fields`, `visual_channels`, `stat_transforms`, `scale_contract`, `coordinate_contract`, `interaction_contract`, and `accessibility_contract`.
- Validation should fail when a visual channel cannot be traced back to data, state, or intentional decoration.

### 3. Linked Brushing Dashboard

Create a linked-view pattern where a selection in one view drives highlight, filter, or detail states in other views. Candidate combinations: scatterplot plus table, map plus histogram, density plus raw points, scatterplot matrix plus detail panel.

Recommended owner: `skills/d3-animated-svg/`

Why it matters:

- The Plotly book emphasizes graphical queries, linked views, hover, filtering, brushing, and persistent selections.
- Current coverage has brushes, lasso, and focus/context, but a reusable multi-view query contract would make interaction behavior easier to apply consistently.

Pattern contract:

- Inputs: shared stable row key, query field, view-specific encodings.
- Events: hover, click, brush, lasso, clear, optional persistent selection.
- Modes: highlight preserves context; filter removes marks and may rescale; compare keeps previous and current selections visible.
- Validation: selection keys must be stable; all linked views must update from the same source of truth; clear-state behavior must be visible and testable.

### 4. Layered Refinement Animation

Promote a reusable animation sequence that moves from raw data to analytical summary to uncertainty to annotation. This can be used in standalone SVG, HTML/D3/Anime.js, and Slidev scenes.

Recommended owner: `skills/html-d3-anime-video-workflow/` with a D3 reference link when needed.

Why it matters:

- Several reviewed sources support the same explanatory sequence: show observations, reveal a summary, clarify uncertainty, then annotate the takeaway.
- This pattern maps well to existing video repair contracts because it gives each scene a data-first structure before adding motion.

Pattern contract:

- Stages: raw marks, grouped/faceted context, statistical summary, uncertainty display, direct labels, final callout.
- Validation: the animation must not hide the denominator, must preserve scale continuity across stages, and must keep the takeaway visible after motion ends.

### 5. Overplotting Resolution Ladder

Create a decision ladder for dense point data: transparency, hollow or smaller marks, jitter, faceting, bin2d, hexbin, density contours, and summarization.

Recommended owner: `skills/d3-animated-svg/`

Why it matters:

- R Graphics Cookbook and Wilke both provide practical overplotting guidance.
- Current pattern inventory includes the component encodings, but a reusable ladder would let agents choose a method based on density, task, and screen size.

Pattern contract:

- Inputs: x, y, optional group, estimated point density, viewport size.
- Selection logic: preserve individual points when identification matters; bin when aggregate shape matters; facet when group comparison matters; contour when density topology matters.
- Validation: dense regions must remain legible; jitter must not imply false precision; bins must expose count or density semantics.

### 6. Map Story Fit Check

Add a geospatial decision checklist before creating a map pattern: whether geography is truly the story, what geographic level is defensible, how classification breaks affect interpretation, and what non-map comparison should accompany the view.

Recommended owner: `skills/d3-animated-svg/` geospatial references.

Why it matters:

- Hands-On Data Visualization highlights practical map interaction needs, geographic level choices, class breaks, and source/credit context.
- The current pattern inventory has many map forms; the missing piece is a stronger map-selection gate.

Pattern contract:

- Inputs: geometry level, measure, denominator, classification method, projection, source attribution.
- Validation: map must include source/credit metadata, class breaks must be declared, tooltip or small-screen fallback must be available, and a non-map comparison should be considered for ranked or temporal tasks.

### 7. Annotation And Direct Label Polish

Promote a focused annotation pattern for direct labels, leader lines, label lanes, clipping/margin control, and compact legend alternatives.

Recommended owner: `skills/d3-animated-svg/` and video quality audit references.

Why it matters:

- The ggplot Wizardry source repeatedly points to margin, clipping, legend positioning, text boxes, and mark annotations as practical finish-quality work.
- Current D3 guidance includes label overlap checks; this promotion would make high-quality annotation a first-class pattern rather than a late repair.

Pattern contract:

- Inputs: labeled marks, priority score, collision boxes, leader-line anchors, optional label lanes.
- Validation: labels must not overlap marks or each other; off-plot labels need explicit margin space; clipped annotations are failures unless intentionally masked.

### 8. Publishable Accessibility Contract

Standardize a minimum contract for title, subtitle, source, credit, accessible text, keyboard or non-hover fallback, and export/download affordances when appropriate.

Recommended owner: shared D3 and HTML/D3/Anime.js references.

Why it matters:

- Hands-On Data Visualization emphasizes web publication context, while Wilke and Plotly materials reinforce clear decoding of scales, hover text, and interaction.
- Current generated SVGs can include `title` and `desc`; a richer contract would make examples more publishable and easier to audit.

Pattern contract:

- Required: chart title, data source, `title`/`desc` in SVG when applicable, visible legend or direct labels, and declared unit/scale semantics.
- Interactive views: hover must not be the only way to read essential values; provide selected-state text, table fallback, or labels for small screens.
- Validation: exported artifact should expose meaningful accessible text and should remain interpretable without pointer hover.

## Do Not Promote Yet

- Do not import book figures, screenshots, datasets, or slide layouts into skills.
- Do not add broad "data visualization theory" prose to `SKILL.md`; keep runtime guidance procedural and compact.
- Do not mark a pattern as accepted until it has an isolated fixture or runtime validation path.

## Suggested Next Skill Work

The highest-leverage reference step has been promoted to `skills/d3-animated-svg/references/pattern-selection-contracts.md`. The promoted reference covers the visual grammar contract, distribution selection, overplotting ladder, linked brushing, map fit, annotation finish, and publishable accessibility checks.

The next substantive pattern promotion should be a small distribution composite acceptance fixture with stable item IDs and a validator that checks scale sharing, label visibility, raw/summary state transitions, and interval semantics.
