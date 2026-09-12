# Command-contract case: portrait emphasis and an authored opening

Read the loaded skill and write `draft.json` with exactly this source:

```json
{"id":"reserved-family-contract","title":"A FAMILY AND ITS SCHOOL","design":"editorial","mode":"genealogy","layout":"cohorts","cohort_spread":{"1":1.35},"source_note":"Fictional demonstration. Heraldic devices are fictional. The portrait is decorative, not a likeness.","groups":[{"id":"a","label":"Alder","color":"#F56550"},{"id":"b","label":"Birch","color":"#77BDDD"}],"nodes":[{"id":"p1","label":"Anna","icon":"museum-862","icon_width":50,"emphasis":true,"detail":"1800–1874","birth":1800,"death":1874,"group":"a","row":0},{"id":"p2","label":"Ben","detail":"1802–1877","birth":1802,"death":1877,"group":"b","row":0},{"id":"c1","label":"Clara","detail":"1822–1890","birth":1822,"death":1890,"group":"a","row":1,"place":"Alder school"},{"id":"c2","label":"Daniel","detail":"1840–1912","birth":1840,"death":1912,"group":"b","row":1}],"unions":[{"id":"u1","partners":["p1","p2"],"children":["c1","c2"]}],"edges":[],"annotations":[{"kind":"landmark","node":"c1","field":"place","width":160,"size":20,"icon":"heraldry","art_size":32,"art_position":"beside"}]}
```

Execute these commands exactly:

```sh
uv run --script skills/usefulcharts-style/scripts/space_family_branches.py draft.json --output result/source.json --report result/placement.json --reserve-context
uv run --script skills/usefulcharts-style/scripts/render_chart.py result/source.json --svg result/poster.svg --report result/layout.json
uv run --script skills/usefulcharts-style/scripts/audit_chart.py result/poster.svg --source result/source.json --report result/browser.json --png result/poster.png
```

Preserve every supplied record, date, category, partnership and child. Required outputs are `draft.json`, `result/source.json`, `result/placement.json`, `result/poster.svg`, `result/layout.json`, `result/browser.json`, and `result/poster.png`. This checks the exact command interface and source-backed browser geometry; no aesthetic acceptance or image inspection is requested. Keep the copied skill read-only. Use no repository files, sibling skills, Git history or network research. Write only inside the isolated workspace.
