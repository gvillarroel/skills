# Editable generated diagram families

Prepare the following explicit inputs for Lucidchart. Automatic layout is acceptable. Preserve the literal records and markup; do not infer or add people, hierarchy relationships or messages. Save the original JSON at `input/layout.json`.

```json
{
  "graph":{"title":"Generated families","infinite_canvas":true,"nodes":[{"id":"note","type":"rectangle","x":10,"y":10,"width":100,"height":50,"label":"Reference"}]},
  "collections":[{"id":"people","values":[{"id":"ada","parent":"","name":"Ada & team","role":"Director"},{"id":"lin","parent":"ada","name":"Lin <P1>","role":"Engineer"},{"id":"kai","parent":"ada","name":"Kai","role":"Analyst"}]}],
  "layouts":[
    {"id":"organization","type":"orgChart","position":{"x":150,"y":150},"collectionId":"people","idField":"id","foreignKeyField":"parent","nameField":"name","roleField":"role"},
    {"id":"topics","type":"mindMap","position":{"x":150,"y":650},"collectionId":"people","idField":"id","parentIdField":"parent","textField":"name"},
    {"id":"sequence","type":"umlSequence","position":{"x":900,"y":150},"markup":"@startuml\nUser -> API : Request\nAPI --> User : Result\n@enduml"},
    {"id":"arrange","type":"assistedLayout","shapeIds":["note"]}
  ]
}
```

Deliver `out/diagram.lucid`, `out/document.json`, `out/layout-report.json` and `out/changes.md`. Check data identity, parents, counts and the package locally. In concise English, explain which information is preserved, who computes the geometry, and what remains unverified about sequence grammar, text metrics, editing and live import. This evaluation has no authenticated Lucid connection. Keep all outputs outside the skill resource directory and do not claim that the original SVG coordinates survived these generated routes.
