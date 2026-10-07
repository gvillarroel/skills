# Rich native compilation contract

Save the following JSON as `input/graph.json`. Compile it using the supplied skill, without changing its explicit notation, types or fields. Deliver `out/diagram.lucid`, `out/document.json`, `out/native-report.json` and `out/status.md`. The status must be factual English and explain local validation versus live acceptance. No authenticated Lucid connection is available.

```json
{
  "title":"Rich native contract", "page_width":1000, "page_height":400, "page_fill":"#FFFFFF", "auto_tiling":false,
  "nodes":[
    {"id":"work","type":"bpmnActivity","x":20,"y":20,"width":150,"height":80,"label":"Review <P1> & accept","fill":"#EEEEEE","stroke":"#333333","stroke_width":2,"stroke_style":"dashed","opacity":80,"font_family":"Arial","font_size":16,"bold":true,"text_align":"left","properties":{"activityType":"task","taskType":"user"}},
    {"id":"entity","type":"table","x":350,"y":20,"width":220,"height":120,"label":"","properties":{"rowCount":2,"colCount":2,"cells":[{"xPosition":0,"yPosition":0,"mergeCellsRight":1,"text":"Invoice <literal>"},{"xPosition":0,"yPosition":1,"text":"id PK"},{"xPosition":1,"yPosition":1,"text":"integer"}]}},
    {"id":"compute","type":"namedShape","x":700,"y":20,"width":80,"height":80,"label":"Compute","properties":{"className":"ArchAmazonEC2AWS2024"}}
  ],
  "edges":[{"id":"rel","source":"work","target":"entity","source_port":{"x":1,"y":0.5},"target_port":{"x":0,"y":0.5},"line_type":"elbow","elbow_points":[{"x":260,"y":60},{"x":260,"y":80}],"stroke":"#111111","stroke_width":2,"source_marker":"one","target_marker":"zeroOrMore","labels":[{"text":"1","position":0.1,"side":"top","color":"#111111","font_size":12},{"text":"0..*","position":0.9,"side":"bottom","color":"#111111","font_size":12}]}],
  "groups":[{"id":"pair","items":["work","entity","rel"],"z_index":2}],
  "layers":[{"id":"semantic","title":"Diagram","items":["pair","compute"],"layer_index":0}]
}
```

Run this exact compilation command after saving the input:

```bash
uv run --script skills/lucidchart-svg/scripts/build_native.py input/graph.json --output out/diagram.lucid --document-json out/document.json --report out/native-report.json
```

Verify literal labels, type-specific fields, table merges, explicit route and multiplicities, group/layer membership and library defaults. Do not infer a new BPMN or ER meaning from this explicit mixed contract fixture. Do not modify the read-only skill bundle.
