# Exact command contract: visible duration stems and weighted lanes

Write the exact JSON below to `draft.json`. Keep the loaded skill read-only. This is a command control, so image inspection is not required.

```json
{"id":"stem-contract","title":"TWO REGIONAL HISTORIES","design":"editorial","mode":"timeline","width":1200,"height":1600,"source_note":"All records are fictional.","reading_note":"Stems and full bands show exact durations. Wider capsules name periods. Width is compositional.","groups":[{"id":"g","label":"Coast","color":"#77BDDD"},{"id":"h","label":"Hills","color":"#98BD92"}],"time":{"start":1800,"end":2000,"step":25},"lanes":[{"id":"coast","label":"Coast","weight":1.4},{"id":"hills","label":"Hills","weight":1}],"periods":[{"id":"early","label":"Early council","lane":"coast","group":"g","start":1800,"end":1870,"offset":25,"bar_width":40,"treatment":"stem","stem_width":5,"label_position":0.65,"size":16},{"id":"later","label":"Later assembly","lane":"coast","group":"g","start":1890,"end":2000,"offset":85,"bar_width":40,"size":16},{"id":"ridge","label":"Ridge communities","lane":"hills","group":"h","start":1800,"end":2000,"offset":20,"bar_width":40,"treatment":"stem","stem_width":4,"size":16}],"transitions":[{"id":"reform","source":"early","target":"later","kind":"succession","style":"ribbon","ribbon_width":10}],"events":[{"id":"school","lane":"coast","year":1835,"label":"A public school","detail":"Teachers establish classes.","size":18,"detail_size":15},{"id":"roads","lane":"hills","year":1920,"label":"Common roads","detail":"Councils share maintenance.","size":18,"detail_size":15}]}
```

Run each exact command in order:

```sh
uv run --script skills/usefulcharts-style/scripts/pack_timeline_events.py draft.json --output deliverables/brief.json --report deliverables/placements.json --max-width 220
```

```sh
uv run --script skills/usefulcharts-style/scripts/render_chart.py deliverables/brief.json --svg deliverables/poster.svg --report deliverables/layout.json
```

```sh
uv run --script skills/usefulcharts-style/scripts/audit_chart.py deliverables/poster.svg --source deliverables/brief.json --report deliverables/browser.json --png deliverables/poster.png
```

Required outputs: `draft.json`, `deliverables/brief.json`, `deliverables/placements.json`, `deliverables/poster.svg`, `deliverables/layout.json`, `deliverables/browser.json`, `deliverables/poster.png`. Preserve every field except the event offsets and widths assigned by the placement helper. Report completion.
