Run this exact command-contract control with the read-only usefulcharts-style bundle. Write the following JSON unchanged to draft.json, then execute the three commands in order.

```sh
uv run --script skills/usefulcharts-style/scripts/compose_context_insets.py draft.json --output result/source.json --report result/context.json
uv run --script skills/usefulcharts-style/scripts/render_chart.py result/source.json --svg result/poster.svg --html result/poster.html --report result/layout.json
uv run --script skills/usefulcharts-style/scripts/audit_chart.py result/poster.svg --source result/source.json --report result/browser.json --png result/poster.png
```

Keep all generated files in this workspace. Do not change the source JSON or the copied skill. Do not read acceptance examples, other skills, repository documents or external task directories. Image inspection is not required in this command control. The final audit must contain no hard findings.

```json
{
  "id": "distinct-study-collections",
  "title": "MEASURING THE WORLD",
  "design": "editorial",
  "mode": "lineage",
  "layout": "authored",
  "width": 1400,
  "height": 1570,
  "font_size": 17,
  "source_note": "Fictional independent teaching collections. Original symbols are illustrative, not institutional logos.",
  "reading_note": "The independent collections imply no descent. Counts refer only to records shown.",
  "groups": [
    {
      "id": "sky",
      "label": "Sky and space",
      "color": "#F56550"
    },
    {
      "id": "instruments",
      "label": "Instruments",
      "color": "#F7CD26"
    },
    {
      "id": "light",
      "label": "Optical studies",
      "color": "#98BD92"
    },
    {
      "id": "places",
      "label": "Maritime and civic",
      "color": "#77BDDD"
    }
  ],
  "nodes": [
    {
      "id": "star",
      "label": "Star Catalogue House",
      "group": "sky",
      "icon": "star",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 215,
      "y": 590,
      "size": 18
    },
    {
      "id": "sun",
      "label": "Solar Calendar Office",
      "group": "sky",
      "icon": "sun",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 538,
      "y": 590,
      "size": 18
    },
    {
      "id": "compass",
      "label": "Compass Collection",
      "group": "instruments",
      "icon": "compass",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 861,
      "y": 590,
      "size": 18
    },
    {
      "id": "astrolabe",
      "label": "Astrolabe Cabinet",
      "group": "instruments",
      "icon": "astrolabe",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 1184,
      "y": 590,
      "size": 18
    },
    {
      "id": "orbit",
      "label": "Orbital Studies Institute",
      "group": "sky",
      "icon": "orbit",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 215,
      "y": 825,
      "size": 18
    },
    {
      "id": "globe",
      "label": "Globe Collection",
      "group": "instruments",
      "icon": "globe",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 538,
      "y": 825,
      "size": 18
    },
    {
      "id": "wheel",
      "label": "Wheelwrights Archive",
      "group": "instruments",
      "icon": "wheel",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 861,
      "y": 825,
      "size": 18
    },
    {
      "id": "gear",
      "label": "Mechanical Transmission Room",
      "group": "instruments",
      "icon": "gear",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 1184,
      "y": 825,
      "size": 18
    },
    {
      "id": "lens",
      "label": "Optical Lens Collection",
      "group": "light",
      "icon": "lens",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 215,
      "y": 1060,
      "size": 18
    },
    {
      "id": "prism",
      "label": "Spectrum Laboratory",
      "group": "light",
      "icon": "prism",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 538,
      "y": 1060,
      "size": 18
    },
    {
      "id": "anchor",
      "label": "Harbour Records Office",
      "group": "places",
      "icon": "anchor",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 861,
      "y": 1060,
      "size": 18
    },
    {
      "id": "ship",
      "label": "Voyage Collection",
      "group": "places",
      "icon": "ship",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 1184,
      "y": 1060,
      "size": 18
    },
    {
      "id": "tower",
      "label": "Tower Records Room",
      "group": "places",
      "icon": "tower",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 215,
      "y": 1295,
      "size": 18
    },
    {
      "id": "observatory",
      "label": "Observatory Papers",
      "group": "sky",
      "icon": "observatory",
      "icon_width": 65,
      "width": 260,
      "style": "emblem",
      "x": 538,
      "y": 1295,
      "size": 18
    }
  ],
  "edges": [],
  "insets": [
    {
      "id": "instrument-story",
      "kind": "story",
      "box": [
        80,
        180,
        470,
        240
      ],
      "title": "Different ways of measuring",
      "text": "These independent collections distinguish navigation, celestial observation and optical work.",
      "source_nodes": [
        "compass",
        "astrolabe",
        "lens"
      ],
      "icon": "astrolabe",
      "art_width": 110,
      "art_height": 110
    },
    {
      "id": "collection-counts",
      "kind": "counts",
      "box": [
        780,
        180,
        540,
        240
      ],
      "title": "Collections represented here",
      "columns": 2
    }
  ]
}
```
