# Native Mermaid video operations

The copied producer retains its native rendering, styling, palette and grammar
resources. Its `animate_mermaid_svg.py` calls this plugin's video finish.

## Author and style

Keep Mermaid source in a project-owned directory with only relevant diagrams.
Use `references/diagram-types.json` to inspect the bundled family's supported
declarations when needed. Author a useful `accTitle` and `accDescr`; omit visible
`title` statements. Prefer one small actual mechanism over an oversized graph.

```text
uv run --script <skill-root>/scripts/style_mermaid_directory.py diagrams --write --report style.json
uv run --script <skill-root>/scripts/style_mermaid_directory.py diagrams --check --report style-check.json
uv run --script <skill-root>/scripts/animate_mermaid_svg.py diagrams/route.mmd -o route.svg --animation none --require-accessibility --config-file mermaid-config.json
```

Pass `--mmdc-arg=--puppeteerConfigFile --mmdc-arg=browser.json` when using an
existing local Chrome/Chromium executable. Keep renderer caches and outputs
inside the project. No source diagram is considered rendered until SVG exists.

## Native configuration

Set top-level `htmlLabels:false`, `flowchart.htmlLabels:false`, and
`journey.textPlacement:"old"` for portable text. Start with a readable native
font size, then fit and measure the result in its final section. Adjust diagram
direction, native spacing or layout before squeezing labels. An axis unit is
essential data context, even when all automatic headings are absent.

For pinned grammars which reject accessibility directives, render a temporary
source with those directives removed, retain their intended content in the
authored source comments, add invisible SVG title/desc with unique referenced
IDs, and verify final metadata and geometry. Do not add a visible title.

## Handoff

Deliver `.mmd`, actual SVG, source/render hashes, viewBox, entity IDs and focus
ports. Keep native arrowheads and data geometry. Namespace imported IDs, CSS,
markers and metadata. Use `--animation none` for assets driven by the parent
video clock. If a supplied SVG has independent CSS/SMIL animation, freeze or
map it to that clock before composing.

Verify labels and legends pairwise, semantic shapes, exact palette, local fonts,
zero foreignObject, no scripts/external assets, and repeated seeking.
The video finish removes automatic diagram title marks, neutralizes CS1 surfaces
and shadows, and retains quantitative widths. Colorset2 preserves the producer's
contrast-aware category finish when explicitly needed.
