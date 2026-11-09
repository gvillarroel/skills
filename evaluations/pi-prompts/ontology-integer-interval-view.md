# Prepare comparable integer-range views

Use the ontology-authoring skill to compare the representations of two
pinned snapshots. Each row belongs to its numbered premise. Create the
three source files with the following exact strings. Keep them as raw
source ledgers.

Write left-source.json.

    {"premises":[{"id":"p01","gap":null,"axioms":["SubClassOf(:CodeValue DataAllValuesFrom(:number DatatypeRestriction(xsd:integer xsd:minInclusive \"-2\"^^xsd:integer xsd:maxInclusive \"7\"^^xsd:integer)))"]},{"id":"p02","gap":null,"axioms":["SubClassOf(:CodeValue :MeasuredValue)"]}]}

Write right-source.json.

    {"premises":[{"id":"p01","gap":null,"axioms":["SubClassOf(:CodeValue DataAllValuesFrom(:number DataIntersectionOf(DatatypeRestriction(xsd:integer xsd:maxInclusive \"7\"^^xsd:integer) DatatypeRestriction(xsd:integer xsd:minInclusive \"-2\"^^xsd:integer))))"]},{"id":"p02","gap":null,"axioms":["SubClassOf(:CodeValue :MeasuredValue)"]}]}

Write shifted-source.json.

    {"premises":[{"id":"p01","gap":null,"axioms":[]},{"id":"p02","gap":null,"axioms":["SubClassOf(:CodeValue :MeasuredValue)","SubClassOf(:CodeValue DataAllValuesFrom(:number DataIntersectionOf(DatatypeRestriction(xsd:integer xsd:maxInclusive \"7\"^^xsd:integer) DatatypeRestriction(xsd:integer xsd:minInclusive \"-2\"^^xsd:integer))))"]}]}

Use the bundled normalizer on each and write left-view.json,
right-view.json and shifted-view.json. Treat these as proposed
comparison artifacts. This task provides no OWL reasoner. Report only
the file-level observations in this execution. The six files are the
deliverables.
