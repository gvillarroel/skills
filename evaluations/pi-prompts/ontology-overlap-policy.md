# Approve the complete evidence choice for three archive-release policies

Use the ontology-authoring skill and its guidance for reviewing disjunctions. The editorial board needs a decision on the complete choice rule for each of three independently governed archive release packets. Identify what the policy establishes, including the treatment of a packet that has both forms of evidence. Each policy governs only the named packet class. Review the offered class constraints as written. The board has approved neither adding a new restriction nor resolving uncertain policy by convention.

## K13 · Catalogue export

Locator `catalogue-release@v8 §6`

> An eligible catalogue export packet must include a signed catalogue receipt or a curator acceptance memo. Each document suffices on its own.

The guide contains a mock-up with both document boxes checked to illustrate the form's layout. Its caption identifies it as a form mock-up. The quoted paragraph is the only operative eligibility text for `CatalogueExportPacket`.

- K13-H requires at least one of the two document memberships for each catalogue export packet and permits overlap.
- K13-L requires exactly one of the two document memberships for each catalogue export packet.

## K24 · Research deposit

Locator `research-deposit@v4 §3`

> A research deposit packet must include an ingest receipt or an approved steward declaration. Deposits that include both also satisfy the evidence rule.

The governed subject is `ResearchDepositPacket`. Each branch is a membership of the same packet.

- K24-C requires exactly one of the two evidence memberships.
- K24-R requires at least one of the two evidence memberships and permits overlap.

## K35 · Restricted annotation release

Locator `restricted-release@v2 §9`

> A restricted annotation release packet must use either a publication warrant or a signed redaction approval. It must use just one route. A packet that carries both does not qualify under this evidence rule.

The governed subject is `RestrictedAnnotationPacket`. This is an eligibility rule for that class. It imposes no rule on other packet classes.

- K35-W requires exactly one of the two evidence memberships within the governed class.
- K35-A requires at least one and permits overlap within the governed class.

## Deliverable

Write `review.json` with exactly one key `items`. The array has one object per packet and each object has exactly `id`, `locator`, `selection`, `supported_requirement`, `disposition`, `question`, and `check`. Copy the ID and locator. Use the chosen option ID for `selection` or JSON `null` if the board cannot approve a complete option. Use concise prose for the supported requirement and disposition. Use a concrete question for an unresolved decision or JSON `null` otherwise.

In `check` give exactly `method`, `target`, `expected`, and `observed`. Each value is prose or JSON `null`. Propose an OWL check with an explicitly in-scope named packet. There is no executed reasoning result for any of these packets. State what the proposed check should show under the applicable decision.
