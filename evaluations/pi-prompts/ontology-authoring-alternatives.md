# Model identity documents and validate evidence packets

Read the two approved passages below. Deliver `ontology.ttl`,
`shapes.ttl` and `review.md`. Use `urn:intake:` as the namespace and
the identifiers given here. The only logical class definition in scope
is the stated direction of the IdentityDocument rule. Declare the
classes and four string-valued properties named in the passages.
Keep the record check in SHACL Core and use the submitted type to
select its records. Extra metadata on an incomplete branch is allowed.
In the review explain what a missing branch in an OWL graph establishes,
and list test cases that distinguish the two requirements.
For local RDF and shape checks, use the pinned environment with
`uv run --with rdflib==7.6.0 --with pyshacl==0.40.0 python`.

## Domain policy ID-DOMAIN, §2

Every `IdentityDocument` is a `DigitalCredential` or a
`PaperCredential`. It may be both. A document's classification as a
digital or paper credential is insufficient to classify it as an
identity document.

## Consumer contract ID-INGEST, §5

Every record explicitly typed as `Submission` must contain exactly
one complete evidence packet. A digital packet requires at least one
`digitalCode` and at least one `signature`. A paper packet requires
at least one `paperCode` and at least one `seal`. The properties
are strings. A packet missing any required field is incomplete.
Incomplete packet metadata can be carried alongside a complete
packet. Other records are outside this check. Apply the consumer
contract directly to the submitted graph with inference disabled.
