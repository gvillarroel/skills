# Inventory handoff package

Prepare a local editable Lucid Standard Import package from this explicit graph. This is a public development command-contract benchmark. Save the JSON exactly as `input/contract.json`, preserving every value. Use the stated native types; this mixed fixture does not assert a new domain notation.

```json
{
  "title":"Inventory handoff <Q4>", "page_width":1200, "page_height":600, "page_fill":"#F8FAFC", "auto_tiling":false,
  "nodes":[
    {"id":"handoff-lanes","type":"swimLanes","x":20,"y":20,"width":860,"height":260,"label":"Stock & custody","fill":"#FFFFFF","stroke":"#334155","stroke_width":2,"z_index":-1,"properties":{"vertical":true,"titleBar":{"height":28,"verticalText":false},"lanes":[{"title":"Receiving <dock>","width":360,"headerFill":"#DBEAFE","laneFill":"#EFF6FF"},{"title":"Control & archive","width":500,"headerFill":"#E2E8F0","laneFill":"#F8FAFC"}],"magnetize":false}},
    {"id":"scan","type":"predefinedProcess","x":70,"y":105,"width":180,"height":70,"label":"Scan <batch> & seal","fill":"#E0F2FE","stroke":"#075985","stroke_width":3,"stroke_style":"dashed","rounding":8,"opacity":85,"font_family":"Arial","font_size":18,"text_color":"#0C4A6E","bold":true,"italic":true,"text_align":"left","vertical_align":"center","z_index":2,"properties":{"sideWidth":0.12}},
    {"id":"register","type":"table","x":460,"y":80,"width":320,"height":160,"label":"","fill":"#FFFFFF","stroke":"#475569","stroke_width":2,"properties":{"rowCount":3,"colCount":3,"cells":[{"xPosition":0,"yPosition":0,"mergeCellsRight":2,"text":"Register <literal> & bins","style":{"fill":{"type":"color","color":"#CBD5E1"}}},{"xPosition":0,"yPosition":1,"text":"batch_id PK"},{"xPosition":1,"yPosition":1,"text":"text"},{"xPosition":2,"yPosition":1,"text":"required"},{"xPosition":0,"yPosition":2,"text":"bin <slot>"},{"xPosition":1,"yPosition":2,"text":"integer"},{"xPosition":2,"yPosition":2,"text":"0..99"}],"userSpecifiedRows":[{"index":0,"size":40},{"index":1,"size":60},{"index":2,"size":60}],"userSpecifiedCols":[{"index":0,"size":140},{"index":1,"size":100},{"index":2,"size":80}],"verticalBorder":true,"horizontalBorder":false}},
    {"id":"caption","type":"rectangle","x":950,"y":90,"width":180,"height":80,"label":"Local package only","fill":"#FEF3C7","stroke":"#92400E","stroke_width":1,"font_size":15,"underline":true,"rotation":5}
  ],
  "edges":[
    {"id":"register-link","source":"scan","target":"register","source_port":{"x":1,"y":0.5},"target_port":{"x":0,"y":0.5},"line_type":"elbow","elbow_points":[{"x":350,"y":140},{"x":350,"y":160}],"stroke":"#334155","stroke_width":2,"stroke_style":"dotted","source_marker":"exactlyOne","target_marker":"zeroOrMore","z_index":3,"labels":[{"text":"1","position":0.08,"side":"top","color":"#075985","font_size":12,"bold":true},{"text":"records & bins","position":0.52,"side":"middle","font_size":13,"italic":true},{"text":"0..*","position":0.92,"side":"bottom","font_size":12,"underline":true}]},
    {"id":"callout-link","source":{"type":"shapeEndpoint","shapeId":"caption","position":{"x":0,"y":1}},"target":{"type":"positionEndpoint","position":{"x":900,"y":360}},"line_type":"straight","joints":[{"x":920,"y":300}],"source_marker":"none","target_marker":"openArrow","stroke":"#92400E","stroke_width":1,"label":"unverified <render>","label_position":0.7,"label_side":"bottom","label_color":"#92400E","label_font_size":11}
  ],
  "groups":[{"id":"scan-register","items":["scan","register","register-link"],"z_index":4}],
  "layers":[{"id":"handoff","title":"Custody & records","items":["handoff-lanes","scan-register"],"layer_index":0},{"id":"annotation","title":"Review notes","items":["caption","callout-link"],"layer_index":1}]
}
```

After saving the input, run this exact command:

```sh
uv run --script skills/lucidchart-svg/scripts/build_native.py input/contract.json --output out/contract/diagram.lucid --document-json out/contract/document.json --report out/contract/native-report.json
```

Deliver the saved input and all four files at these exact paths:

- `input/contract.json`
- `out/contract/diagram.lucid`
- `out/contract/document.json`
- `out/contract/native-report.json`
- `out/contract/notes.md`

Check the actual package locally, including table order/merges, lane properties, literal labels, connector attachments and route, multi-label positions, styles, groups, layers, and page settings. In concise English notes, explain what was prepared, supported editability, and the limitations of local validation, rendering and live acceptance. The notes will be reviewed directly rather than scored by keywords.

Treat `skills/lucidchart-svg/` as read-only. Keep all generated files in this workspace outside that bundle. Do not discover repository examples or other skills, access the network, authenticate, upload, or create a live document. No authenticated Lucid connection is available. The deliverable is a local package; do not claim a rendered or live-verified result.
