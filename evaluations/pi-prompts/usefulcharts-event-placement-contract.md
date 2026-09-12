# Exact command contract: place dated notes

Write the exact following JSON to `draft.json`. Keep the loaded skill read-only.

```json
{"id":"note-contract","title":"A REGIONAL HISTORY","design":"editorial","mode":"timeline","width":1100,"height":1500,"source_note":"Fictional source data.","groups":[{"id":"g","label":"Coast","color":"#77BDDD"}],"time":{"start":1800,"end":2000,"step":25},"lanes":[{"id":"coast","label":"Coast"}],"periods":[{"id":"early","label":"Early council","lane":"coast","group":"g","start":1800,"end":1870,"offset":30,"bar_width":32},{"id":"later","label":"Later assembly","lane":"coast","group":"g","start":1890,"end":2000,"offset":180,"bar_width":32}],"transitions":[{"id":"reform","source":"early","target":"later","kind":"succession","style":"ribbon"}],"events":[{"id":"school","lane":"coast","year":1835,"label":"A public school","detail":"Teachers establish classes.","size":13,"detail_size":11},{"id":"roads","lane":"coast","year":1920,"label":"Common roads","detail":"Councils share maintenance.","size":13,"detail_size":11}]}
```

Run this exact command:

```sh
uv run --script skills/usefulcharts-style/scripts/pack_timeline_events.py draft.json --output deliverables/brief.json --report deliverables/placements.json
```

Then run this exact command:

```sh
uv run --script skills/usefulcharts-style/scripts/render_chart.py deliverables/brief.json --svg deliverables/poster.svg --report deliverables/layout.json
```

Required outputs: `draft.json`, `deliverables/brief.json`, `deliverables/placements.json`, `deliverables/poster.svg`, and `deliverables/layout.json`. Preserve the two event years and all source words. Report completion; image inspection is not part of this command-only control.
