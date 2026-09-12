# Exact command control: independent institutional paths

Write the following JSON exactly to `draft.json`. Keep the copied skill read-only. This is a command control; image inspection is not required.

```json
{
  "id": "independent-branches",
  "title": "INDEPENDENT INSTITUTIONAL HISTORIES",
  "design": "editorial",
  "mode": "lineage",
  "width": 1400,
  "height": 1000,
  "source_note": "Original synthetic test records.",
  "groups": [
    {
      "id": "g",
      "label": "Institutions",
      "color": "#F56550"
    }
  ],
  "nodes": [
    {
      "id": "a",
      "label": "Western Workshop",
      "group": "g",
      "width": 150,
      "x": 200,
      "y": 250,
      "date_label": "1710",
      "detail_position": "outside"
    },
    {
      "id": "b",
      "label": "Institute of Weights",
      "group": "g",
      "width": 150,
      "x": 850,
      "y": 600,
      "date_label": "1850",
      "detail_position": "outside"
    },
    {
      "id": "c",
      "label": "Eastern Workshop",
      "group": "g",
      "width": 150,
      "x": 500,
      "y": 250,
      "date_label": "1730",
      "detail_position": "outside"
    },
    {
      "id": "d",
      "label": "Institute of Measures",
      "group": "g",
      "width": 150,
      "x": 1100,
      "y": 600,
      "date_label": "1860",
      "detail_position": "outside"
    }
  ],
  "edges": [
    {
      "id": "first",
      "source": "a",
      "target": "b",
      "kind": "branch"
    },
    {
      "id": "second",
      "source": "c",
      "target": "d",
      "kind": "branch"
    }
  ]
}
```

Run these exact commands in order:

```sh
uv run --script skills/usefulcharts-style/scripts/render_chart.py draft.json --svg result/poster.svg --html result/poster.html --report result/layout.json
```

```sh
uv run --script skills/usefulcharts-style/scripts/audit_chart.py result/poster.svg --source draft.json --report result/browser.json --png result/poster.png
```

Required artifacts: `draft.json`, `result/poster.svg`, `result/poster.html`, `result/layout.json`, `result/browser.json`, `result/poster.png`. Preserve all supplied fields, dates and relationships. Verify that the browser audit has no hard findings and no `unrelated-shared-run` warning. Report the result without changing the source or the skill.
