# Narrative chronology composition

Use this route for a numeric timeline with dated explanatory notes, branching periods, or contextual images. Read the timeline fields in [the editorial contract](editorial-contract.md). For a small comparison without branches or events, retain [compact chronology](compact-chronology.md).

## Match the page to the amount of history

For about 20 periods and 24 notes or fewer, start from [the compact annotated template](../assets/templates/narrative-timeline.json): approximately 1300 × 1700 for three lanes, 16-unit period names, 18-unit note headings, 20-unit landmarks, and 15-unit body text. Use fewer lanes on a narrower page. Increase the width only when the actual simultaneous periods and wrapped words require it. A small branching history is still a small history.

Do not use the dense 1800 × 2700 defaults for a dozen periods, or lengthen the page to 3600 just to fit one image. Such a page can pass geometry while its words become tiny among empty corridors. First adjust local period offsets, narrow excess ribbon width, and choose a readable image footprint. For ordinary compact notes, `--max-width 220` opens a wider quiet area. When placing side images, omit that cap for the helper's automatic image-plus-prose allowance, or choose a larger complete-group limit such as 320. A 110-unit image plus an eight-unit gap needs 288 units to retain 170 units for prose; capping the whole group at 170 or 220 can leave word-by-word text. Render the helper's output directly.

## Compose the colored history first

Keep exact start/end years and typed transitions. Choose each period's horizontal position and width by its local relationships. A ribbon's width is compositional unless the input explicitly assigns it a quantity. Preserve the center when narrowing a ribbon so a cosmetic change does not scramble its connections.

Use the least colored area that accommodates the label and its attachment ports. On a substantial 1800-unit-wide poster, start around 20–30 units for quieter periods and 40–60 for major institutions. These are starting points, not fixed values: a long wrapped label or four branches can require more width. Keep every transition port at least five units inside its period and keep filled bridges inside their own dated gaps. Preserve actual gaps; do not stretch periods to conceal discontinuities.

Give pivotal events a stronger heading. For a substantial poster, a useful first treatment is 12–13-unit ordinary headings, 14–15-unit landmarks, and 10–11-unit contextual text. Judge those sizes in the rendered page. Do not reduce all notes to fit a small opening beside a wide band; recompose the band first.

### Mix duration stems and full bands

When long, quiet intervals create broad strips of empty color, give selected periods `treatment: stem`, `stem_width: 5`, and a normal `bar_width` large enough for the name. The fine stem spans the exact start/end dates. A wider capsule contains the rotated name and does not assert a shorter duration. Retain full `ribbon` treatment for consequential periods and where the continuous colored area helps a reader follow a dense branch. Explain the distinction in the reading note, for example: “Stems and full bands show exact durations; wider stem labels name periods.”

Keep treatment selection deliberate. Applying stems to every ordinary period can leave a skeletal page, while treating only long quiet continuities retains a useful contrast with important phases. Do not alternate styles or label positions mechanically. Optional `label_position` runs from 0 to 1 through the capsule's available vertical travel, default 0.5; use it to move a name closer to its local narrative while preserving the stem's dates.

Stem ports must be centered (`source_port` or `target_port: 0.5`). Bridges taper to the actual visible stem width, including when the other endpoint is a full band. An explicit `ribbon_width` sets the bridge's maximum width; a thinner stem narrows that end. Recompute ports after changing treatment. The renderer rejects an attachment aimed at empty space beside a stem.

### Allocate regional width by content

Set optional positive `weight` on each lane to distribute available horizontal space proportionally. All unspecified weights are 1; equal weights preserve the original equal-width layout. For example, weights 1.2, 1, 0.8 give the region with more simultaneous histories extra room without changing any year position. `offset` remains measured from that lane's left edge in SVG units, so recompose offsets after changing weights or page width; they are not scaled automatically. Keep complete names and image dimensions readable in narrower lanes.

Inspect the whole page and the busiest lower branch before reducing the canvas. Unchanged type units become larger at an equal displayed poster width, but longer wrapped paragraphs can erase that benefit. A successful packing pass does not decide this tradeoff.

## Place notes against the complete geometry

Write an authored draft with `design: editorial`, `mode: timeline`, the numeric `time` scale, named `lanes`, and positioned `periods`. Each event needs a distinct `id`, exact `year`, `lane`, `label`, and optional `detail`. Specify its type sizes and any `icon`, `art_width`, and `art_height` deliberately. Events retain their source-array order. Existing event `offset` and `width` are placement preferences for the helper, not protected coordinates.

```sh
uv run --script <skill-dir>/scripts/pack_timeline_events.py draft.json --output brief.json --report placements.json
uv run --script <skill-dir>/scripts/render_chart.py brief.json --svg poster.svg --html poster.html --report layout.json
uv run --script <skill-dir>/scripts/audit_chart.py poster.svg --source brief.json --report browser.json --png poster.png
```

The helper changes only each event's horizontal `offset` and wrapping `width`. It preserves all words, dates, type sizes, image dimensions, intervals and relationships. It measures wrapped lines and the entire illustration viewport, reserves filled bridges and uncertain orthogonal connections, and places earlier events before later ones. For stems it reserves both the thin duration rectangle and the complete name capsule, allowing notes beside the genuinely unpainted part of the label envelope. The source-backed audit checks the visible stem's exact duration, width, center, color and visibility independently of that invisible envelope. It has no repository or acceptance-fixture dependency. `uv` provisions its declared Shapely dependency.

Inspect the resulting PNG. A placement pass is not an aesthetic verdict. Check the busiest division, a note exactly at a period endpoint, the narrowest paragraph and the footer. A complete note may occupy different widths on different lines; a connection can pass beside the short last line only when the browser confirms that it does not touch the text or image.

If the helper reports `needs-layout`, it writes no replacement brief. Enlarge the page or recompose the adjacent periods and their ports before retrying. Revise an illustration's placed size only after checking it remains legible. Never delete a note or move its year to obtain a pass. The helper does not solve fixed-coordinate user layouts, cross-lane callouts, custom annotations, or global backtracking: compose those directly and audit them.

## Integrate images into the paper

Use identified, inspected art for its subject. Bundled transparent choices include `illustration-clock-escapement`, `illustration-square-rigged-ship`, `illustration-suspension-bridge`, and `illustration-stagecoach`. The three transport drawings have width:height ratios 213:208, 273:168, and 359:149. Their unchanged source bytes and provenance are bundled. Keep source identities and depicted technologies distinct from invented events; these explanatory drawings do not document the fictional year beside them.

Choose `art_position: above`, `below` (default), `left`, or `right` for the relationship between a note and its image. `width` encloses the complete group. Side images reserve their width plus an eight-unit gap, and the prose wraps in the remainder. Above/below images are centered with a five-unit gap. The first heading line stays anchored at the numeric year in every arrangement; an above image occupies earlier space without changing the event date. The helper reserves that earlier geometry too. Keep enough distance from the preceding note and any preceding period that has already ended.

Use a wide low silhouette, such as a vehicle or bridge, where it supports horizontal explanation; a tall instrument can sit beside a short paragraph. Do not alternate positions mechanically. Inspect text and illustration as one local group and compare the silhouette at its actual size. If side placement leaves a sliver of text, use above/below or recompose adjacent intervals. The source-backed audit checks the actual image reference, viewport, visibility, text roles and date anchors independently of the packing helper.

Choose transparency for free-standing illustrations on the map field. A white source panel can work inside a colored institutional nameplate but look pasted onto an open chronology. Reject it there rather than calling it transparent. Inspect line weight at the actual placed size: a technically valid vector or a pale museum print can become an unreadable thumbnail. Do not add images at regular intervals merely to fill blank space.
