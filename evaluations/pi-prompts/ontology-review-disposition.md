# Review proposed changes to a freight intake ontology

Use the ontology-authoring skill and its guidance for reviewing disjunctions. The intake team needs a review of four packets before choosing what to materialize. Use the rules as evidence for the stated projection. Evaluate the supplied alternatives as written and leave the existing ontology intact. All terms used in the proposed restrictions are declared. The terms in each packet have local scope.

## M17 · Inbound scan

Locator `receiving-manual@r18 §4.2`

> An inbound sealed consignment must record a gate scan or a dock scan. A consignment may record both.

Project the requirement on `InboundSealedConsignment`. Treat `GateScanned` and `DockScanned` as class memberships of that same consignment.

- Option M17-A restricts an inbound sealed consignment to exactly one of the two scan classes.
- Option M17-B requires every inbound sealed consignment to be in both scan classes.

An existing OWL reasoner receipt checked a named inbound sealed consignment explicitly in both scan classes against option M17-A. It reported inconsistency. No other reasoner check has been run for this packet.

## M23 · Handoff completion

Locator `handoff-procedure@r5 §2.1`

> A cold-chain handoff is complete if it has dock clearance or a mobile terminal verification.

This paragraph defines the completion check for `ColdChainHandoff` only. The procedure does not address the case where both conditions hold. There are no other source statements on how the alternatives interact.

- Option M23-A uses a union of the two branch classes for the qualifying cases.
- Option M23-B uses their union and excludes overlap within the governed class.

## M31 · Specialist credential

Locator `site-access-rule@r9 §8.3`

> Every authorized restricted-zone escort must have an active specialist credential.

The original condition on `AuthorizedRestrictedZoneEscort` uses `hasCredential` with filler `ActiveSpecialistCredential`. The proposed replacement keeps that same owner and existential property restriction and substitutes `RegionalValidEscortCredential` as the filler. The intake team says this equivalence depends on a separate credential ontology. The requested version of `credential-crosswalk@r3` is absent, and the local ontology contains no axiom relating the two filler classes. Review the intended equivalence against the effective ontology including that versioned crosswalk.

## M42 · Display annotation

Locator `console-layout@r4 figure 6 caption`

> The legend shows gate scan as a blue square and dock scan as an orange circle. Icons are examples for the printed layout.

The freight projection covers operational membership and constraints. The diagram's labels, colors and layout are outside that projection. There are no bundles to compare for this caption.

## Deliverable

Write one `review.json` object with the single key `items`. Its value is an array of four objects, one per packet. Each object has exactly `id`, `locator`, `disposition`, `basis`, `question`, and `check`. Use the packet ID and locator as written. Write the disposition and basis in your own words. The question is a concise question for the person who can resolve a decision or `null` when no such question is needed.

When a check is relevant, set `check` to an object with `method`, `target`, `expected`, `observed`, and `blocker`. Use ordinary prose values or JSON `null`. Describe a concrete case and state what it should show. Use the supplied receipt as the only executed validation. Record what is unresolved or unavailable when that affects the check. Use `null` for `check` when the packet needs no validation.
