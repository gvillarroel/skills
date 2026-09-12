Run this exact command control with the read-only usefulcharts-style skill. Write the JSON below unchanged to draft.json. Execute these commands in order:

```sh
uv run --script skills/usefulcharts-style/scripts/create_branch_poster.py draft.json --output-dir result
```

Keep generated files inside this workspace. Do not read acceptance examples, sibling skills, repository files or external task directories. Do not modify the JSON or the skill. Image inspection is not required for this command control. Report any findings honestly.

```json
{
  "id": "captioned-collections",
  "title": "THE PUBLIC COLLECTIONS",
  "design": "editorial",
  "mode": "lineage",
  "layout": "branches",
  "source_note": "Fictional command control.",
  "groups": [
    {
      "id": "civic",
      "label": "Civic collections",
      "color": "#77BDDD"
    }
  ],
  "nodes": [
    {
      "id": "cabinet",
      "label": "Common Cabinet",
      "founded": 1700,
      "date_label": "1700",
      "group": "civic",
      "detail": ""
    },
    {
      "id": "east",
      "label": "Eastern Reading Room",
      "founded": 1730,
      "date_label": "1730",
      "group": "civic",
      "detail": ""
    },
    {
      "id": "west",
      "label": "Western Book Society",
      "founded": 1741,
      "date_label": "1741",
      "group": "civic",
      "detail": ""
    },
    {
      "id": "library",
      "label": "United Public Library",
      "founded": 1780,
      "date_label": "1780",
      "group": "civic",
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
  ],
  "annotations": [
    {
      "node": "east",
      "kind": "pill",
      "label": "EASTERN READING TRADITIONS",
      "group": "civic",
      "width": 320,
      "size": 18
    }
  ]
}
```
