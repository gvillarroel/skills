# Command contract: institutional influence composition

Read the copied skill. Write `draft.json` with exactly this authored source:

```json
{"id":"influence-contract","title":"TWO SCHOOLS OF INQUIRY","design":"editorial","mode":"lineage","width":1100,"height":1000,"font_size":18,"source_note":"Original fictional institutions and relationships.","groups":[{"id":"makers","label":"Makers","color":"#F7CD26"},{"id":"observers","label":"Observers","color":"#77BDDD"}],"nodes":[{"id":"house","label":"House of Inquiry","group":"makers","x":550,"y":250,"width":210,"detail":"Founded 1200","style":"pill"},{"id":"guild","label":"Instrument Guild","group":"makers","x":260,"y":420,"width":200,"detail":"Founded 1270"},{"id":"school","label":"School of Observers","group":"observers","x":800,"y":420,"width":200,"detail":"Founded 1280"},{"id":"academy","label":"Mechanical Academy","group":"makers","x":260,"y":640,"width":200,"detail":"Established 1480"},{"id":"observatory","label":"Public Observatory","group":"observers","x":800,"y":600,"width":200,"detail":"Established 1470"},{"id":"research","label":"Instrument Research","group":"makers","x":360,"y":830,"width":200,"detail":"Established 1600"}],"edges":[{"id":"house-guild","source":"house","target":"guild","kind":"branch"},{"id":"house-school","source":"house","target":"school","kind":"branch"},{"id":"guild-academy","source":"guild","target":"academy","kind":"branch"},{"id":"school-observatory","source":"school","target":"observatory","kind":"branch"},{"id":"academy-research","source":"academy","target":"research","kind":"branch"},{"id":"observatory-research","source":"observatory","target":"research","kind":"influence"}]}
```

Execute these commands exactly:

```sh
uv run --script skills/usefulcharts-style/scripts/route_influences.py draft.json --output result/source.json --report result/routing.json
uv run --script skills/usefulcharts-style/scripts/render_chart.py result/source.json --svg result/poster.svg --html result/poster.html --report result/layout.json
uv run --script skills/usefulcharts-style/scripts/audit_chart.py result/poster.svg --source result/source.json --report result/browser.json --png result/poster.png
```

Required outputs are `draft.json`, `result/source.json`, `result/routing.json`, `result/poster.svg`, `result/poster.html`, `result/layout.json`, `result/browser.json`, and `result/poster.png`. Preserve all source facts and coordinates. This is an exact command and artifact contract; no image-based aesthetic review is requested. Keep the copied skill read-only. Use no parent directories, sibling skills, example galleries, repository documentation, Git history or network research. Write only in this isolated workspace.
