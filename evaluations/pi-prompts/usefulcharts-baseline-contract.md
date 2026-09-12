# Command-contract case: source-dated family baselines

Read the loaded skill and create `draft.json` with exactly this data:

```json
{"id":"dated-family-contract","title":"A DATED FAMILY","design":"editorial","mode":"genealogy","layout":"cohorts","source_note":"Fictional command-contract records.","groups":[{"id":"a","label":"Alder","color":"#F56550"},{"id":"b","label":"Birch","color":"#77BDDD"}],"nodes":[{"id":"a","label":"Ada","detail":"1800–1874","birth":1800,"death":1874,"group":"a","row":0},{"id":"b","label":"Ben","detail":"1802–1877","birth":1802,"death":1877,"group":"b","row":0},{"id":"c","label":"Clara","detail":"1822–1890","birth":1822,"death":1890,"group":"a","row":1},{"id":"d","label":"Daniel","detail":"1840–1912","birth":1840,"death":1912,"group":"b","row":1}],"unions":[{"id":"u","partners":["a","b"],"children":["c","d"]}],"edges":[]}
```

Execute these commands exactly as written:

```sh
uv run --script skills/usefulcharts-style/scripts/space_family_branches.py draft.json --output deliverables/brief.json --report deliverables/spacing.json
uv run --script skills/usefulcharts-style/scripts/render_chart.py deliverables/brief.json --svg deliverables/poster.svg --report deliverables/layout.json
```

Keep all supplied facts. Report the result of the placement and render commands. Required outputs are `draft.json`, `deliverables/brief.json`, `deliverables/spacing.json`, `deliverables/poster.svg` and `deliverables/layout.json`. This case checks the command interface; it does not request aesthetic acceptance or an image inspection. Keep the copied skill read-only. Use no ambient repository files, sibling skills, Git history or network research. Write only inside the isolated workspace.
