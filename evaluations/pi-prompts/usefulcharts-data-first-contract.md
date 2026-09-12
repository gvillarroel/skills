Run this exact command-contract control with the read-only usefulcharts-style bundle. Write the JSON below unchanged to draft.json, then execute these commands in order:

```sh
uv run --script skills/usefulcharts-style/scripts/compose_branching_history.py draft.json --output result/source.json --report result/composition.json
uv run --script skills/usefulcharts-style/scripts/render_chart.py result/source.json --svg result/poster.svg --html result/poster.html --report result/layout.json
uv run --script skills/usefulcharts-style/scripts/audit_chart.py result/poster.svg --source result/source.json --report result/browser.json --png result/poster.png
```

Keep all files in this workspace. Do not read acceptance examples, other skills, repository files or external task directories. Do not change the JSON or the skill. This is a command control: image inspection is not required. The final report must have no hard findings and no unrelated-shared-run warning.

```json
{
  "id": "unplaced-collections",
  "title": "THE PUBLIC COLLECTIONS",
  "design": "editorial",
  "mode": "lineage",
  "layout": "branches",
  "source_note": "Fictional test history.",
  "groups": [
    {
      "id": "g",
      "label": "Collections",
      "color": "#77BDDD"
    }
  ],
  "nodes": [
    {
      "id": "cabinet",
      "label": "Common Cabinet",
      "founded": 1700,
      "date_label": "1700",
      "group": "g",
      "detail": ""
    },
    {
      "id": "east",
      "label": "Eastern Reading Room",
      "founded": 1730,
      "date_label": "1730",
      "group": "g",
      "detail": ""
    },
    {
      "id": "west",
      "label": "Western Book Society",
      "founded": 1741,
      "date_label": "1741",
      "group": "g",
      "detail": ""
    },
    {
      "id": "library",
      "label": "United Public Library",
      "founded": 1780,
      "date_label": "1780",
      "group": "g",
      "detail": "The two bodies unite"
    }
  ],
  "edges": [
    {
      "id": "e0",
      "source": "cabinet",
      "target": "east",
      "kind": "branch"
    },
    {
      "id": "e1",
      "source": "cabinet",
      "target": "west",
      "kind": "branch"
    },
    {
      "id": "e2",
      "source": "east",
      "target": "library",
      "kind": "branch"
    },
    {
      "id": "e3",
      "source": "west",
      "target": "library",
      "kind": "branch"
    }
  ]
}
```
