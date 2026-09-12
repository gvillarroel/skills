# Chronology note hierarchy and image ownership

Use this treatment within `usefulcharts-parallel-history` when repeated heading/body stacks flatten the page, or an illustration appears to explain a neighboring event. Retain the [narrative chronology workflow](narrative-chronology.md), exact numeric dates and complete source text.

## Distinguish ordinary explanation from landmarks

Set `text_layout: paragraph` on ordinary events. The renderer flows the bold `label` into regular `detail`, retaining `size` and `detail_size` in editable SVG runs. A terminal period is added for display unless the label already ends in `.?!:`; the JSON words and punctuation are unchanged. Each line uses its largest run's measured height. Its first line remains anchored to `year`.

Keep `text_layout: stacked` (the default) for selected landmarks whose names need a separate, stronger heading. An illustration does not automatically make its event a landmark. Base emphasis on the supplied history, not an alternating pattern or a fixed quota.

```json
{
  "id": "survey", "lane": "coast", "year": 1840,
  "label": "1840 · The harbor survey",
  "detail": "Pilots record safe channels and seasonal currents.",
  "text_layout": "paragraph", "size": 18, "detail_size": 15,
  "icon": "illustration-square-rigged-ship",
  "art_position": "auto", "art_width": 100, "art_height": 97.65
}
```

On a compact poster, keep approximately 18/15-unit ordinary type; the 12/11-unit dense mural treatment needs substantial data. Compare the whole page after changing paragraph shape. Recovered space can permit a shorter page without reducing font units, but reduce height only if all exact dates, long notes and art remain readable. Do not enlarge the page to conceal one awkward paragraph.

## Keep the image with its explanation

For a new note, `art_position: auto` lets `pack_timeline_events.py` try above, below and both sides. It ranks clear candidates by fewer lines, shorter total height, wider prose and proximity to the preferred horizontal position. It preserves the image dimensions and the text's exact year. The output replaces `auto` with one explicit position; render that output directly. Explicit positions remain authoritative.

Honor a requested image relationship with an explicit position: a picture requested beside its prose needs `left` or `right` in the draft. After changing an image position, its dimensions, the text treatment or neighboring periods during visual repair, run the packing helper again before rendering. Hand-adjusting a formerly clear offset can put the new text footprint over a duration stem. Keep the revised facts and treatment in the draft; let the helper measure the new complete group.

The helper excludes automatic arrangements whose image shares a vertical band with another event date in the same region, considering both earlier and later events. Explicit placements receive a `composition_warnings` entry instead of being silently changed. The browser independently repeats that check against the actual SVG image viewport, and prints the warning alongside its geometry result.

Treat `illustration-competing-date` as a review prompt, not proof of an incorrect historical link. Two notes can be separated horizontally, and an image outside another date band can still look detached. Inspect the actual crop: identify the caption that an unfamiliar reader would pair with the picture. Move the picture beside or below its own prose, choose `auto`, or recompose neighboring periods when ownership remains ambiguous. Preserve the date and every source word. Do not accept an image merely because it clears bounding boxes.

Do not force positional variety. A wide low bridge can belong above its explanation, while a ship fits below; equal intervals or a repeated four-position cycle are not compositional goals. Keep enough text width beside an image; omit an unnecessary `--max-width` cap so the helper can allocate its image-plus-prose allowance.

## Verify visible type and association

Run the normal pack → render → source-backed audit commands from [narrative chronology](narrative-chronology.md). Inspect `composition_warnings` even when `status` is `pass`. The audit checks source wording, heading/detail order, font size, weight, visibility, contrast, actual run positions and image identity independently of the packing logic.

Open the final PNG. Compare the full composition and a dense group at an equal scale. Check the strongest landmark, the narrowest mixed paragraph, and each image next to its preceding and following notes. A clear local improvement does not establish visual parity with a professionally composed reference.
