# Dispatch desk closeout

I'm covering the dispatch desk today. Please turn the register below into `data.ttl` using our current vocabulary and leave a `review.json` I can use to close the five tickets. Keep the dispatch IRIs in the form `urn:dispatch-record:<key>`. Our importer accepts record types and direct property values in `data.ttl`. The files below are the complete handoff packet. Use them as the sources for this review.

Make `review.json` an object with an `items` array. Give each ticket one item with `ticket`, `assessment`, `evidence`, and `next_step`. Write the assessment and next step in plain English. Use `null` if nothing further is needed. Each entry in `evidence` has `source` and `quote` and quotes the supplied file directly.

## Tickets

| Ticket | What the desk wants to know |
| --- | --- |
| D17 | Which transport mode can we put on the dispatch? |
| D23 | What can we record about its transport mode? |
| H6 | What evidence does the handbook require before handoff? |
| D41 | Can this dispatch clear the seal-code check? |
| D57 | Can we confirm the signature on its fallback receipt? |

`dispatch-vocabulary.ttl`

```turtle
@prefix d: <urn:dispatch-model:> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

d:Dispatch a owl:Class .
d:Mode a owl:Class ; owl:equivalentClass [ a owl:Class ; owl:oneOf ( d:Road d:Air ) ] .
d:Road a owl:NamedIndividual, d:Mode .
d:Air a owl:NamedIndividual, d:Mode .
d:Road owl:differentFrom d:Air .
d:transportMode a owl:ObjectProperty ; rdfs:domain d:Dispatch ; rdfs:range d:Mode .
d:sealCode a owl:DatatypeProperty ; rdfs:domain d:Dispatch ; rdfs:range xsd:string .
d:sealScanId a owl:DatatypeProperty ; rdfs:domain d:Dispatch ; rdfs:range xsd:string .
d:fallbackReceiptId a owl:DatatypeProperty ; rdfs:domain d:Dispatch ; rdfs:range xsd:string .
```

`dispatch-register.txt`

```text
D17 | The carrier confirmed this dispatch went by road or by air. Its mode field is still blank and the carrier could not tell us which.
D23 | The carrier confirmed this dispatch went by rail.
D41 | Two seal codes were recorded on the dispatch at closeout. Both were read directly from the dispatch and confirmed: S-041A and S-041B.
D57 | Fallback receipt RC-570 was filed for this dispatch. The signature-ledger export is still with Records and was not included in this packet.
```

`desk-handbook.txt`

```text
H6 Before handoff, attach a seal scan or a fallback receipt. Attaching both is acceptable.
H8 For the seal-code check, a dispatch may have at most one distinct seal code in its closeout record.
H9 Verify a fallback receipt signature by matching its receipt ID to a signed entry in signature-ledger.csv. The dispatch register records filing only.
```
