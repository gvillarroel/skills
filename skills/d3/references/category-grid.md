# Responsive Category Grid

- **SVG metadata:** Use `--pattern-id` for a caller-supplied stable ID; the default is `d3-category-grid`.
- **Use when:** A catalogue, legend or set of named groups needs equal-size directly labeled tiles whose color expresses identity.
- **Builder:** `scripts/build_category_grid.py`

## Input and Output Contract

Supply a non-empty ordered JSON array of labels or category objects with a
`label` string and optional unique `id`. Extra caller data remains in the
embedded data records. Preserve every supplied label and reading-order position.

```json
[
  {"id": "west", "label": "Western service group", "region": "west"},
  {"id": "east", "label": "Eastern service group", "region": "east"}
]
```

Run the builder outside the read-only skill directory:

```text
uv run --script <d3-skill>/scripts/build_category_grid.py --data categories.json --output catalogue.html --svg-output catalogue.svg --allocation-output allocation.json --title "Service groups" --description "Ordered service groups as equal-size labeled tiles." --colorset colorset1 --canvas "#ffffff"
```

Map exact requested paths to these flags. `--svg-output` exports the actual
rendered SVG, including final paint, geometry, accessibility and overflow
metadata. `--allocation-output` records actual computed tile styles with
`canvas`, ordered `labels`, and `styles` containing fill, text, stroke,
strokeWidth, strokeDasharray, opacity and tier. Omit optional outputs when not
requested. Use `--screenshot` for a desktop inspection PNG; use `--force` to
replace owned outputs after correcting data or flags.

## Rendering Contract

- Use the genuine unchanged bundled D3 7.9.0 runtime and D3 joins. The builder embeds runtime, palette, data and solid finalizer for offline editing.
- Pass each original zero-based index to `D3SolidStyle.categoryStyle(index, colorset, actualCanvas)`. Bind every returned style and the ancestor overflow tier; no early modulo or hardcoded white outlined fallback.
- Exclude only the actual canvas token. First use every solid category color in the complete ordered sequence, then preserve the allocator's contrasting overflow borders.
- Expose `data-category-index` once on each filled tile. Keep the category group and its direct label associated without repeating the body index.
- Keep all bodies equal in size. Recompute column count and a native-width viewBox when the HTML gets narrower; `--columns` limits the maximum and `--width` limits the page width.
- Keep the resting label font readable at mobile size. Measure and wrap real glyphs without dropping characters, increasing every tile's common height when needed.
- Create each SVG's title and desc before validation. Finalize solid paint before recording allocation or exporting.

## Validation

```text
python <d3-skill>/scripts/check_self_contained_html.py catalogue.html
python <d3-skill>/scripts/check_palette_contract.py catalogue.html --colorset colorset1
python <d3-skill>/scripts/check_palette_contract.py catalogue.svg --colorset colorset1
uv run --script <d3-skill>/scripts/render_d3_svg.py catalogue.html --output scratch/mobile.svg --screenshot scratch/mobile.png --viewport 390x900 --wait-ms 200
```

Use the selected colorset in the palette check. Inspect desktop and 390-pixel
mobile output. Check complete tile and outline bounds, label bounds, reading
order, actual font size and the standalone export; absence of document scroll
overflow alone cannot prove that SVG marks fit. Correct input or builder flags
and rerun. For custom geometry outside this supported route, read
`references/palette-contract.md` and use the genuine bundled runtime and full
allocator instead of recreating partial implementations.

When checking requested label order with `check_visual_contract.py`, repeat
`--require-ordered-text "Western service group" --require-ordered-text "Eastern service group"`
or quote the explicit sequence
`--require-ordered-text "Western service group|Eastern service group"`.
Both apply the same order check. Use legacy `--ordered-text` for a label whose
literal text contains `|`; that flag never splits its argument.
