# Command-contract case: source-bound editorial context

Read the loaded skill and write `draft.json` with exactly this source:

```json
{"id":"context-contract","title":"ARCHIVES OF THE VALE","design":"editorial","mode":"lineage","layout":"authored","width":1200,"height":1000,"source_note":"Fictional demonstration. Heraldic devices are fictional.","groups":[{"id":"red","label":"Alder","color":"#F56550"}],"nodes":[{"id":"a","label":"First archive","realm":"The Alder March","group":"red","x":450,"y":250,"width":140},{"id":"b","label":"Later archive","realm":"Bayeux & Coast","group":"red","x":700,"y":500,"width":140}],"edges":[{"id":"e","source":"a","target":"b","kind":"branch"}],"annotations":[{"kind":"landmark","node":"b","field":"realm","width":160,"size":18,"dx":-160,"dy":0,"icon":"heraldry","art_size":36,"art_position":"beside"}]}
```

Execute these commands exactly:

```sh
uv run --script skills/usefulcharts-style/scripts/place_context_landmarks.py draft.json --output result/source.json --report result/placement.json
uv run --script skills/usefulcharts-style/scripts/render_chart.py result/source.json --svg result/poster.svg --report result/layout.json
uv run --script skills/usefulcharts-style/scripts/audit_chart.py result/poster.svg --source result/source.json --report result/browser.json --png result/poster.png
```

Keep all data unchanged except resolved annotation offsets. Required outputs are `draft.json`, `result/source.json`, `result/placement.json`, `result/poster.svg`, `result/layout.json`, `result/browser.json`, and `result/poster.png`. This case checks the command interface and browser geometry, not aesthetic acceptance; no image inspection is requested. Keep the copied skill read-only. Use no repository files, sibling skills, Git history or network research. Write only inside the isolated workspace.
