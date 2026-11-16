# Producer handoff

The distributable plugin contains dedicated copies: `line-world-d3`,
`line-world-mermaid`, `line-world-icons`, `line-world-hyperframes` and this
`line-world-video` orchestrator. Prefer those copies when installed; their
defaults follow the shared video contract, not the general skills' document,
logo, gallery or solid-card presentation. The originals remain available
outside the plugin. Load only the needed producer at its installed location.

The packager materializes the copies from the current general runtime bundles,
replaces their entry instructions and UI metadata, adds the same standalone
video contract to each, and records source/profile hashes. Its Mermaid copy
also replaces the generic CS1 solid finish with the bundled native video finish.
Read [plugin profiles](plugin-profiles.md) when maintaining or testing the plugin.

- **D3:** own data joins, scales, chart geometry and seeded layouts. The starter
  is a custom linked multi-view composition using genuine bundled D3 7.9.0.
  Standalone documents outside the plugin follow the general builder workflow. Pass
  row IDs, units, fixed domains and semantic group IDs into the compositor.
- **Mermaid:** own notation, graph layout and accessible diagram source. Supply
  `.mmd` plus rendered SVG, `viewBox`, node IDs and rendering receipt. Use its
  palette styler and checker before rendering; apply the video finish and preserve native geometry and
  markers. Import the resulting SVG as an asset in the project. The compositor
  owns container reveal/camera timing, not a redraw of Mermaid geometry.
  Set Mermaid's top-level `htmlLabels: false` as well as the flowchart setting
  when a portable text-only SVG is needed. Pass the config to the native renderer;
  do not flatten HTML labels by guessing text positions. Namespace compositor
  classes (`world-label`, for example) so they do not override producer `.label`
  typography. Audit label bounds after import. Explicit user line-art direction
  may use a palette-constrained native CSS override during rendering.
- **Iconify:** choose one monochrome outline family, export exact SVGs and retain
  upstream license text plus receipts. The starter includes reviewed Lucide
  glyphs for database, chart and workflow; newly requested concepts should use
  real provider exports rather than invented branded silhouettes.
- **HyperFrames Explainer:** use when the subject needs a calibrated mechanism
  and linked derived quantities. Consume its local assets and pure state
  function, retain its units, and apply the line world's camera/attention layer.

Each project asset record should carry its producer, path, hash, native bounds,
ports/state IDs, palette and license or source provenance. Optional producer
absence is not a reason to read sibling files indirectly. The starter can still
produce a complete film from its own local D3, simple original relationship
geometry and licensed icons. A Mermaid source alone is not a rendered Mermaid
asset; report an unrendered source honestly.
