# Narrative chronology composition

Use this route for a numeric timeline with dated explanatory notes, branching periods, or contextual images. Read the timeline fields in [the editorial contract](editorial-contract.md). For a small comparison without branches or events, retain [compact chronology](compact-chronology.md).

## Match the page to the amount of history

For about 20 periods and 24 notes or fewer, start from [the compact annotated template](../assets/templates/narrative-timeline.json): approximately 1300 × 1700 for three lanes, 16-unit period names, 18-unit note headings, 20-unit landmarks, and 15-unit body text. Use fewer lanes on a narrower page. Increase the width only when the actual simultaneous periods and wrapped words require it. A small branching history is still a small history.

Do not use the dense 1800 × 2700 defaults for a dozen periods, or lengthen the page to 3600 just to fit one image. Such a page can pass geometry while its words become tiny among empty corridors. First adjust the local period offsets, narrow excess ribbon width, and choose a readable image footprint. For this compact profile, call the note helper with `--max-width 220` so an event can use the wider quiet area instead of becoming a narrow paragraph. Its output is the brief to render.

## Compose the colored history first

Keep exact start/end years and typed transitions. Choose each period's horizontal position and width by its local relationships. A ribbon's width is compositional unless the input explicitly assigns it a quantity. Preserve the center when narrowing a ribbon so a cosmetic change does not scramble its connections.

Use the least colored area that accommodates the label and its attachment ports. On a substantial 1800-unit-wide poster, start around 20–30 units for quieter periods and 40–60 for major institutions. These are starting points, not fixed values: a long wrapped label or four branches can require more width. Keep every transition port at least five units inside its period and keep filled bridges inside their own dated gaps. Preserve actual gaps; do not stretch periods to conceal discontinuities.

Give pivotal events a stronger heading. For a substantial poster, a useful first treatment is 12–13-unit ordinary headings, 14–15-unit landmarks, and 10–11-unit contextual text. Judge those sizes in the rendered page. Do not reduce all notes to fit a small opening beside a wide band; recompose the band first.

## Place notes against the complete geometry

Write an authored draft with `design: editorial`, `mode: timeline`, the numeric `time` scale, named `lanes`, and positioned `periods`. Each event needs a distinct `id`, exact `year`, `lane`, `label`, and optional `detail`. Specify its type sizes and any `icon`, `art_width`, and `art_height` deliberately. Events retain their source-array order. Existing event `offset` and `width` are placement preferences for the helper, not protected coordinates.

```sh
uv run --script <skill-dir>/scripts/pack_timeline_events.py draft.json --output brief.json --report placements.json
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

The helper changes only each event's horizontal `offset` and wrapping `width`. It preserves all words, dates, type sizes, image dimensions, intervals and relationships. It measures wrapped lines and the entire illustration viewport, reserves filled bridges and uncertain orthogonal connections, and places earlier events before later ones. It has no repository or acceptance-fixture dependency. `uv` provisions its declared Shapely dependency.

Inspect the resulting PNG. A placement pass is not an aesthetic verdict. Check the busiest division, a note exactly at a period endpoint, the narrowest paragraph and the footer. A complete note may occupy different widths on different lines; a connection can pass beside the short last line only when the browser confirms that it does not touch the text or image.

If the helper reports `needs-layout`, it writes no replacement brief. Enlarge the page or recompose the adjacent periods and their ports before retrying. Revise an illustration's placed size only after checking it remains legible. Never delete a note or move its year to obtain a pass. The helper does not solve fixed-coordinate user layouts, cross-lane callouts, custom annotations, or global backtracking: compose those directly and audit them.

## Integrate images into the paper

Use identified, inspected art for its subject. `illustration-clock-escapement` provides a transparent historical clock-mechanism drawing; its source bytes and provenance are bundled. Keep source identities distinct from invented events.

Choose transparency for free-standing illustrations on the map field. A white source panel can work inside a colored institutional nameplate but look pasted onto an open chronology. Reject it there rather than calling it transparent. Inspect line weight at the actual placed size: a technically valid vector or a pale museum print can become an unreadable thumbnail. Do not add images at regular intervals merely to fill blank space.
