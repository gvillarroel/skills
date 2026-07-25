# User-Owned D3 Artifact Workflow

Use this reference when creating a new D3 visualization, SVG, or editable starter for a user's project. The goal is to produce code the user can keep editing without mutating this skill's validation gallery.

## Output Policy

- Write user deliverables outside the skill directory.
- Use the path requested by the user. If no path is given, create `output/d3-animated-svg/<task-slug>/` from the current workspace.
- Do not edit `skills/d3-animated-svg/assets/examples/` for ordinary user deliverables. That directory is an acceptance fixture and gallery source.
- Edit `assets/examples/` only when the user explicitly asks to improve the skill, add a gallery card, repair validation fixtures, or update published examples.
- Use gallery code as read-only reference. Copy or adapt the relevant pattern into a new artifact.

## Starter-First Workflow

1. Pick the closest pattern family: `operational-dashboard`, `inline-bar-table`, `context-window-matrix`, `animated-network`, or `blank`. Use `operational-dashboard` for KPI/table/status dashboards so the agent edits data inside a fixed layout instead of inventing panel geometry.
2. Generate a starter when shell access is available:

```powershell
uv run --script skills/d3-animated-svg/scripts/create_d3_svg_starter.py --pattern operational-dashboard --out output/d3-animated-svg/my-viz --title "My D3 visual"
```

3. Edit the generated files, not the skill gallery:
   - `index.html`: rendering code and SVG structure
   - `data.js`: editable data
   - `styles.css`: page and SVG style tokens
   - `NOTES.md`: implementation notes and validation status
   For prepared templates such as `operational-dashboard`, edit `data.js` first and preserve the seeded layout unless the user explicitly requests a structural change. If labels or notes do not fit, shorten the data strings before editing `index.html` or `styles.css`.
   Keep side-panel notes short: prefer one sentence fragment per note and no more than five rendered note lines.
4. If shell access is unavailable, manually create the same file set in the requested output directory and follow the contracts below.
5. Render or open `index.html`, then validate that the SVG is nonblank, labels fit, text stays inside the viewport, and the output can be edited without reading the skill again.

## Portable Visual Defaults

Use these defaults for ordinary user deliverables when the user or target project does not provide a palette. Do not read repository-level token files for this workflow.

- Font stack: `"Open Sans", Arial, sans-serif`
- Text: `#333e48`
- Muted text: `#696969`
- Grid/borders: `#e7e7e7` and `#cfcfcf`
- Page background: `#f7f7f7`
- Surface: `#ffffff`
- Risk/emphasis red: `#9e1b32`
- Warning orange: `#e77204`
- Caution yellow: `#f1c319`
- Success green: `#45842a`
- Information blue: `#007298`
- Soft fills: red `#ffccd5`, orange `#ffe5cc`, yellow `#fff4cc`, green `#dbffcc`, blue `#cdf3ff`

Keep output palettes compact and semantic. Use red only for risk, errors, negative deltas, or explicit emphasis. Use white label halos when labels sit on marks or dense backgrounds.

## Starter Contract

Every user-owned starter should include:

- browser-openable `index.html`
- editable data in `data.js` or inline data near the top of `index.html`
- explicit `viewBox`, `role="img"`, `title`, `desc`, and root `font-family`
- deterministic data and layout
- D3 joins for marks instead of pasted static SVG bodies
- portable SVG animation with SMIL or CSS when motion matters
- short notes that identify the pattern family, output files, and validation performed

## Adapting Gallery Patterns

When adapting a gallery example:

- Read the existing gallery only to understand geometry, data semantics, color roles, and animation timing.
- Copy only the local helper logic needed by the new artifact.
- Rename IDs and titles for the user's artifact.
- Replace gallery data with task-specific data.
- Keep the reusable visual grammar, not the fixture's labels or exact values.
- Do not import the whole gallery, page scaffold, replay system, or unrelated renderers.

## Validation

For a direct-open HTML starter:

```powershell
uv run --script skills/d3-animated-svg/scripts/render_d3_svg.py output/d3-animated-svg/my-viz/index.html --selector "svg" -o output/d3-animated-svg/my-viz.svg --screenshot output/d3-animated-svg/my-viz.png --wait-ms 1200
```

For repository validation after changing this skill:

```powershell
uv run --script scripts/validate-skills.py
```
