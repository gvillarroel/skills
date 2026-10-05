Render this deliberately small synthetic lineage using the supplied skill. Save this JSON exactly as `brief.json`:

```json
{"id":"synthetic-archive","title":"ARCHIVE ORIGINS","design":"editorial","mode":"lineage","layout":"auto","groups":[{"id":"archive","label":"Archive network","color":"#9e1b32"}],"nodes":[{"id":"origin","label":"Record Cabinet","date_label":"1720","group":"archive","detail_position":"outside"},{"id":"north","label":"Northern Archive","date_label":"1760","group":"archive","detail_position":"outside"},{"id":"south","label":"Southern Archive","date_label":"1770","group":"archive","detail_position":"outside"},{"id":"joint","label":"Joint Repository","date_label":"1840","group":"archive","detail_position":"outside"}],"edges":[{"id":"north-origin","source":"origin","target":"north","kind":"branch"},{"id":"south-origin","source":"origin","target":"south","kind":"branch"},{"id":"north-merger","source":"north","target":"joint","kind":"branch"},{"id":"south-merger","source":"south","target":"joint","kind":"branch"}],"source_note":"All names and dates are synthetic.","reading_note":"Solid links show branches and merger inputs. Positions are causal stages, not proportional elapsed time."}
```

Read the skill's connected-layout guidance. Run these commands exactly in separate shell calls:

```sh
uv run --script skills/usefulcharts-style/scripts/render_chart.py brief.json --svg archive.svg --html archive.html --report layout.json
```

```sh
uv run --script skills/usefulcharts-style/scripts/audit_chart.py archive.svg --source brief.json --report browser.json --png archive.png
```

Open the actual PNG and create `review.md` describing label/route readability and remaining unnecessary space. This limited scope does not require a reference-density claim. Exact required outputs are `brief.json`, `archive.svg`, `archive.html`, `layout.json`, `browser.json`, `archive.png`, `review.md`. Keep `skills/usefulcharts-style/` read-only and generated files in the workspace. Do not read galleries or other skills.
