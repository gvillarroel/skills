# Validate an exact RDF literal count

The data and shapes below are the supplied input files. Save them as
`data.ttl` and `shapes.ttl` with their explicit datatype spellings.
Run the bundled semantic validator in the skill to produce
`validation.json`. Use its JSON output and no optional inference.
A graph nonconformance is an expected result, so handle validator
exit code 1 as a completed check and retain the report. Add a short
`review.md` that identifies the focus nodes and explains their
outcomes. Do not repair or change the submitted graph or shapes.

```bash
uv run --script skills/extract-ontologies/scripts/validate_semantic_artifacts.py --data data.ttl --shapes shapes.ttl --inference none --output-format json > validation.json; code=$?; test "$code" -eq 1
```

`data.ttl`

```turtle
@prefix : <urn:review-literals:> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
:Number a :Counted ; :value "01"^^xsd:integer, "1"^^xsd:integer .
:String a :Counted ; :value "alpha", "alpha"^^xsd:string .
:Required :value "1"^^xsd:integer .
```

`shapes.ttl`

```turtle
@prefix : <urn:review-literals:> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
:Count a sh:NodeShape ; sh:targetClass :Counted ;
    sh:property [ sh:path :value ; sh:maxCount 1 ] .
:RequiredLexical a sh:NodeShape ; sh:targetNode :Required ;
    sh:property [ sh:path :value ; sh:hasValue "01"^^xsd:integer ] .
```
