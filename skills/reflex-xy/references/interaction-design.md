# Progressive chart controls

Use this recipe when embedding an XY chart in a chat component, small panel or
application. Keep the first view focused on the user's chart. Do not turn a
chart into an API catalogue or export dashboard.

## First view

- Show the chart with a meaningful title and keep Colorset 1 as the default.
- Choose one primary action for the host: save an image for an interactive chat
  component, or open the interactive HTML when the host only paints an image.
- Provide one clearly labelled disclosure such as `More options`. Keep optional
  fullscreen available only when the host supports it.
- Hide palette/view selectors, alternate formats, sample generators, rerender
  actions, paths, engine versions and developer metadata initially. A successful
  render does not need a permanent ready banner or a tutorial paragraph.

## Reveal capabilities by purpose

Keep one secondary level, grouping controls by purpose rather than exposing
every capability as a separate button. Use labelled selectors for display and
export choices. Preserve interactive HTML, SVG/PNG, editable Python and JSON;
make the additional formats available after opening options. Keep Colorset 2
available only by explicit request or selection.

Preserve the current data and chart identity when changing palette or preview
mode. Label sample generators as replacing the current data. Retain controls
and values when the user closes/reopens options. Do not automatically expand
advanced settings based on guesses about user proficiency.

If native browser toolbar controls overwhelm a compact embedded chart, keep
hover/navigation available and move the toolbar behind an explicit chart-tools
control. A preview-only style or wrapper must leave the downloaded native HTML
and source unchanged. Do not claim SVG or PNG supports live hover/pan/zoom.

Show loading only during work and actionable errors only after a failure. Keep
the previous valid chart and its exports available during failed regeneration.
Show link expiry or static/live limitations where they affect a user's action,
not as always-visible implementation prose.

## Verify the actual interaction

Prefer native disclosure controls, or a button with `aria-expanded` and a linked
hidden region. Support Tab, Enter and Space; keep hidden controls out of the tab
order. If Escape closes the region, return focus to its trigger. In a native
host, use supported elements and distinguish host-provided behavior from tested
DOM behavior. Do not invent unsupported accessibility or layout properties.

Check initial versus expanded controls at desktop and narrow mobile widths.
Use at least 44 by 44 CSS pixels for authored touch targets. Verify keyboard
disclosure, focus visibility, preserved input, all formats, explicit Colorset 2,
new-chart Colorset 1, loading/error recovery and actual native chart interaction.
Count visible actions inside the chart as well as around it. Inspect screenshots;
an overflow-free outer wrapper can still hide a cropped native canvas.

This is a design recipe, not a claim of usability-study or complete WCAG
conformance. Primary guidance: [NN/G progressive disclosure](https://www.nngroup.com/articles/progressive-disclosure/),
[W3C disclosure pattern](https://www.w3.org/WAI/ARIA/apg/patterns/disclosure/),
and [W3C enhanced target size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-enhanced.html).
