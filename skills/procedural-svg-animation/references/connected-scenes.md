# Compact ordered concept scenes

Use this route for caller-supplied stage labels, a message route or a simple
loop of concepts. It builds self-contained SVG with consecutive forward edges
and an optional final-to-first return. It is a narrow semantic-scene helper,
not a numerical solver or a catalog-pattern renderer.

```text
uv run --script <skill-root>/scripts/build_connected_scene.py build --label Source --label Check --label Destination --seed 73021 --output artifacts/message.svg
uv run --script <skill-root>/scripts/build_connected_scene.py validate artifacts/message.svg
uv run --script <skill-root>/scripts/render_procedural_svg.py artifacts/message.svg --screenshot artifacts/preview.png --report artifacts/browser.json
```

Repeat `--label` for 2–12 unique stage names in source order. Quote complete
labels containing spaces. Use `--return-route` for a final-to-first return,
`--palette colorset2` when requested and `--duration-ms` for a different shared
clock. Seed is retained as audit metadata; placement depends on the exact text
and topology and needs no random perturbation. Write exact outputs outside the
read-only bundle. Use `--force` only for an intentional rebuild of that output.

Omitted dimensions fit conservative final-font label bounds, 10-unit horizontal
and 6-unit vertical insets, a visible shaft, a complete 10-unit arrowhead, and
the token's swept bounds. Cards keep 18 px text and a 36-unit height; neither
boxes nor routes stretch to fill an explicit canvas. `--width` and `--height`
preserve a larger requested canvas and reject one smaller than the readable
geometry. For difficult labels, inspect actual browser bounds and rebuild with
appropriate dimensions rather than reducing the font.

Base routes and their directional heads remain visible. Accent paths reveal
during the first 22% of the shared clock; sequential tokens follow afterward.
Tokens stop before the arrowhead envelope and stay outside nodes and labels.
Reduced motion hides the accent/token layer and retains the complete stationary
explanation. Inspect early, middle, loop-boundary and reduced-motion states at
native size. A hash/nonblank render is insufficient to establish readability.

The dedicated validator reconstructs the semantic scene from its embedded
construction contract and rejects missing heads, altered endpoints or labels,
overlapping changed geometry, paint changes and modified motion. Correct flags
and rebuild supported scenes rather than editing the generated SVG. Do not run
`validate_procedural_svg.py` on this route or copy a catalog pattern's metadata
onto custom geometry: that validator deliberately checks the catalog contract.
For branching or other unsupported relationships, author a separate SVG and
audit text, endpoint ownership, route separation, motion bounds and reduced
motion directly; do not claim the ordered-scene validator covers that layout.
