# Exact command contract: dated illustration arrangements

Write the JSON below exactly to `draft.json`. Keep `skills/usefulcharts-style/` read-only. Write generated files only inside this workspace. This is a command control; image inspection is not required.

```json
{"id":"art-contract","title":"A REGIONAL HISTORY","design":"editorial","mode":"timeline","width":1000,"height":2000,"source_note":"All events and institutions are fictional. The identified drawings illustrate subjects, not these invented events.","reading_note":"One year scale. The first heading line marks each event date. Stems show exact durations; capsules name periods.","groups":[{"id":"g","label":"Region","color":"#77BDDD"}],"time":{"start":1800,"end":2000,"step":25},"lanes":[{"id":"region","label":"Region"}],"periods":[{"id":"council","label":"Regional council","lane":"region","group":"g","start":1800,"end":2000,"offset":20,"bar_width":40,"treatment":"stem","stem_width":5,"size":16}],"transitions":[],"events":[{"id":"clock","lane":"region","year":1830,"label":"Clockmaking schools","detail":"Workshops explain the anchor escapement.","size":18,"detail_size":15,"icon":"illustration-clock-escapement","art_position":"above","art_width":75,"art_height":97.13},{"id":"ship","lane":"region","year":1880,"label":"Seasonal convoys","detail":"Merchants coordinate regular voyages.","size":18,"detail_size":15,"icon":"illustration-square-rigged-ship","art_position":"left","art_width":100,"art_height":97.65},{"id":"bridge","lane":"region","year":1930,"label":"Bridge surveys","detail":"Engineers record spans and distances.","size":18,"detail_size":15,"icon":"illustration-suspension-bridge","art_position":"right","art_width":125,"art_height":76.92},{"id":"post","lane":"region","year":1980,"label":"The postal archive","detail":"A collection records earlier coach routes.","size":18,"detail_size":15,"icon":"illustration-stagecoach","art_position":"below","art_width":125,"art_height":51.88}]}
```

Run each exact command in order:

```sh
uv run --script skills/usefulcharts-style/scripts/pack_timeline_events.py draft.json --output deliverables/brief.json --report deliverables/placements.json --max-width 360
```

```sh
uv run --script skills/usefulcharts-style/scripts/render_chart.py deliverables/brief.json --svg deliverables/poster.svg --report deliverables/layout.json
```

```sh
uv run --script skills/usefulcharts-style/scripts/audit_chart.py deliverables/poster.svg --source deliverables/brief.json --report deliverables/browser.json --png deliverables/poster.png
```

Required outputs: `draft.json`, `deliverables/brief.json`, `deliverables/placements.json`, `deliverables/poster.svg`, `deliverables/layout.json`, `deliverables/browser.json`, `deliverables/poster.png`. Preserve all fields except the event offsets and widths assigned by the helper. Report completion.
