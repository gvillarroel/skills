# Permit records and vocabulary glossary

Use the supplied application ontology to extract the register's permit
records. Return `data.ttl`, `evidence.json`, and `review.md`. Also return
`glossary.md` and `glossary.csv` for all three status concepts, including
unused concepts. Use the English annotations and cite the definitions.
Keep a note about local terminology that could mislead a reviewer.

Only two kinds of assertions are in scope: each listed record's type
and its status at the register's reporting date. The register key is
unique. Use `urn:permit-record:<key>` for the record IRI. The three
named concepts are the closed list of status values. A blank entry
means no status was entered. A historical source note can explain
terminology without establishing a current status.

Use the following three inputs as the supplied files. Materialize their
contents in the workspace under the given names for evidence verification.
Create `checks.json` with the skill's RDF evidence checker.

`permit-model.ttl`

```turtle
@prefix : <urn:permit-model:> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
:Permit a owl:Class .
:status a owl:ObjectProperty ; rdfs:domain :Permit ; rdfs:range skos:Concept .
:Filed a skos:Concept, owl:NamedIndividual ;
    skos:prefLabel "Filed"@en ; skos:altLabel "Submitted"@en ;
    skos:definition "Recorded as received and awaiting a decision."@en .
:Granted a skos:Concept, owl:NamedIndividual ;
    skos:prefLabel "Granted"@en ;
    skos:definition "Approved by the issuing authority."@en .
:Archived a skos:Concept, owl:NamedIndividual ;
    skos:prefLabel "Archived"@en .
```

`permit-register.csv`

```csv
key,current_status
P17,Submitted
P18,Escalated
P19,
P20,Granted
```

`terminology.txt`

```text
Historical intake note. The intake desk used “Filed” for scanned pages even when no permit had been received.
The note records historical terminology only.
```
