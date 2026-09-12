Use the copied usefulcharts-style skill for this deterministic command-contract case. Treat `skills/usefulcharts-style/` as read-only. Work only in the isolated workspace, do not inspect parent directories or other skills, and do not run Git commands.

Write the following JSON unchanged to `deliverables/source.json`:

```json
{
  "id": "separate-content-contract",
  "title": "A SMALL INSTITUTIONAL HISTORY",
  "design": "editorial",
  "mode": "lineage",
  "layout": "auto",
  "groups": [{"id":"civic","label":"Civic collections","color":"#F4C948"}],
  "nodes": [
    {"id":"room","label":"The Common Reading Room","group":"civic","detail_position":"outside","date_label":"c. 1710–1715","detail":"A shared collection opens"},
    {"id":"library","label":"The Public Library","group":"civic","detail_position":"outside","date_label":"1764","detail":"The collection becomes a public institution","emphasis":true}
  ],
  "edges": [{"id":"public-foundation","source":"room","target":"library","kind":"branch"}],
  "source_note": "Original synthetic history; names and dates are invented.",
  "reading_note": "Solid path: institutional descent. Positions are schematic. Dates mean establishment or reorganisation."
}
```

Run this command exactly:

```sh
uv run --script skills/usefulcharts-style/scripts/render_chart.py deliverables/source.json --svg deliverables/chart.svg --html deliverables/chart.html --report deliverables/layout.json
```

Verify these four exact nonempty outputs and the passing layout report. Do not install a browser or claim visual inspection in this contract case; the evaluator will inspect the rendered result independently. A concise final report is sufficient.
