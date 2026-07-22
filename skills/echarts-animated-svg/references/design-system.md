# Design System For ECharts Animated SVG Outputs

Use these tokens when generating or restyling ECharts animated SVG examples, gallery HTML, replay controls, and chart palettes.

## Typography And Icons

- Use `'Open Sans', Arial, sans-serif` as the primary font family for HTML and ECharts text.
- Use `'Material Symbols Rounded'` for icon glyphs in replay, restore, navigation, or toolbar controls.
- Keep letter spacing at `0`. Avoid viewport-scaled font sizes.

## Core Colors

- Primary brand: `#9e1b32`
- Neutral brand and interface text: `#333e48`
- Chart palette: `#9e1b32`, `#e77204`, `#f1c319`, `#45842a`, `#007298`, `#652f6c`
- Page background: `#f7f7f7`
- Card and chart surface: `#ffffff`
- Borders and focus: `#cfcfcf`
- Subtle grid lines: `#e7e7e7`
- Secondary text: `#696969`
- Link/default interactive blue: `#007298`
- Hover interactive blue: `#004d66`

## Highlights And Status

- Highlights: red `#ffccd5`, orange `#ffe5cc`, yellow `#fff4cc`, green `#dbffcc`, blue `#cdf3ff`, purple `#f9ccff`
- Status: error `#e8002a`, warning `#ff9633`, caution `#ffd332`, success `#36b300`, information `#00ace6`, special `#9e00b3`

## Implementation Notes

- Put tokens in one shared constant or CSS variable block per generated artifact, then reuse them in chart options and controls.
- Avoid reintroducing older sample palettes such as slate, Tailwind blue, Tailwind teal, or purple-only gradients.
- Prefer icon-plus-text buttons for replay controls so the Material Symbols glyph remains clear even when the web font is still loading.
