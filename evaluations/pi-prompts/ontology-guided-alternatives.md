# Extract manifests and validate their transport references

Apply the supplied ontology and SHACL contract to the register. Produce
`data.ttl`, `evidence.json`, `checks.json`, `validation.ttl`, and `review.md`.
Put the evidence-backed facts in `data.ttl`. Use the SHACL report to show
which records meet the consumer's contract. Run pySHACL with inference
disabled on the extracted graph and supplied shapes and preserve its
standard Turtle report. A validation violation is an expected check
result, so retain the report and continue the review. Use this command
to invoke the pinned validator without relying on an installed Python
package.

```bash
uvx --from pyshacl==0.40.0 pyshacl -s manifest-shapes.ttl -i none -f turtle data.ttl > validation.ttl; code=$?; test "$code" -eq 0 || test "$code" -eq 1
```

Run the bundled evidence checker to produce `checks.json` using the
supplied ontology, the asserted graph and your evidence ledger. Match
the full predicate IRI in each evidence row to its asserted triple.

Use the three supplied files below. Materialize them under the given
names. The register keys are unique, and the instance IRI pattern is
`urn:manifest-record:<key>`. The two reference columns name the matching
properties. A cell can contain a confirmed ID, be blank, or be an
operator's note. A blank is an unestablished value. The type column gives
the RDF class. Review any row where you cannot establish the referenced
ID or where the extracted facts violate the supplied record contract.

`manifest-model.ttl`

```turtle
@prefix : <urn:manifest-model:> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
:Manifest a owl:Class .
:Supplement a owl:Class .
:truckID a owl:DatatypeProperty .
:flightID a owl:DatatypeProperty .
```

`manifest-shapes.ttl`

```turtle
@prefix : <urn:manifest-model:> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
:TransportChoice a sh:NodeShape ;
    sh:targetClass :Manifest ;
    sh:xone (
        [ sh:property [ sh:path :truckID ; sh:minCount 1 ] ]
        [ sh:property [ sh:path :flightID ; sh:minCount 1 ] ]
    ) .
```

`manifest-register.csv`

```csv
key,type,truckID,flightID
M1,Manifest,TR-1,
M2,Manifest,,FL-2
M3,Manifest,TR-3,FL-3
M4,Manifest,,
M5,Manifest,TR-5 or TR-6 (operator unsure),
S1,Supplement,TR-9,FL-9
```
