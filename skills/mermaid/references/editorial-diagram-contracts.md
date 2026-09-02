# Editorial Diagram Contracts

Use this reference when a Mermaid diagram must explain behavior rather than merely list relationships, or when an existing diagram must be simplified or retargeted. Use `accessible-svg-metadata.md` for accessible title and description authoring and release gates.

## Separate meaning from layout

Choose in this order:

1. State the reader's one-sentence question.
2. Select one primary behavioral contract when state, enforcement, capacity, trust, or residual risk is load-bearing.
3. Choose the Mermaid family that can express that contract without discarding direction, order, quantity, boundary, or outcome.
4. Apply palette, direction, spacing, and animation only after the semantic structure is complete.

A secondary contract may contribute one cue, such as a trust-boundary label inside a queue diagram. If two contracts both need full treatment, split overview and detail. Styling and animation never compensate for a missing state, count, boundary, or outcome.

## Behavioral contract routes

Use these routes as semantic checklists, not as new Mermaid families.

| Reader question | Primary contract | Preferred family | Required visible evidence | Overview budget |
| --- | --- | --- | --- | --- |
| Why are arrivals waiting or rejected? | Finite-capacity fan-in | Flowchart; Sankey only when widths encode supplied amounts | Distinct producers, ordered queue or waiting state, numeric capacity, service point, accepted and deferred/rejected outcomes | Up to 5 producers, 5 queue slots, 1 constraint, 2 outcomes |
| Where do two evaluations first differ? | Paired policy traces | Flowchart; Sequence only when messages over time are also essential | Same ordered rules, literal `PASS`/`FAIL`/`SKIPPED`/`NOT REACHED`, first-divergence cue, final outcome for each trace | Exactly 2 traces and 3–6 rules |
| Which path may cross a boundary? | Trusted route and blocked bypass | Flowchart with labeled subgraphs, Architecture, or C4 when its abstraction is supplied | Named zones, allowed entry, blocked entry that stops at the boundary, privileged gate, approved route, audit destination | Up to 3 zones, 8 components, 10 paths |
| How does loose input become a durable record? | Unstructured-to-structured transformation | Flowchart | Representative source statements, clarification, extracted fields, named transformation, durable artifact, at least one provenance link, explicit unknowns | Up to 4 exchanges, 6 fields, 3 provenance links |
| Where is each control enforced? | Governance surface catalog | Block or Flowchart subgraphs; Requirement when verification relations are supplied | Enforcement surfaces, named controls, actor, timing, exception route, coverage gap | 3–5 surfaces and up to 24 controls; split before shrinking labels |
| How does risk survive successive defenses? | Compensating layers | Flowchart or Block | Ordered threat, mitigation and limitation per layer, residual-risk handoff, non-zero final risk or response | 3–5 layers and one primary risk thread |

Apply the tighter limit when the selected Mermaid family or the source contract imposes a smaller capacity. Keep state text, counts, units, symbols, and outcomes visible in the static source. Color and motion may reinforce them but cannot replace them.

## Budget the overview before authoring

For an ordinary overview, target no more than 9 concept nodes, 12 relations, and 2 focal elements. These are editorial limits, not parser limits. Specialized data families keep their truthful data contract instead: a Sankey retains every supplied weighted link needed for conservation, an ER diagram retains required cardinalities, and a Gantt retains required tasks and dependencies.

When an overview exceeds its budget:

1. Remove decoration and repeated legends.
2. Merge exact replicas into one labeled cohort.
3. Collapse leaf-only groups into their named parent when the user authorized simplification.
4. Move secondary instrumentation or cross-cutting detail into a detail figure.
5. Split overview and detail before reducing type below legible size.

Do not aggregate merely to hit a count. Preserve every fact unless the user requested simplification or the output contract explicitly permits it.

## Set adaptation dials independently

When transforming an existing source, freeze these decisions before rewriting:

| Dial | Options | Effect |
| --- | --- | --- |
| Destination | docs, slide, social, print, editable source | Direction, aspect pressure, label size, and whether SVG or source is primary |
| Detail | faithful, balanced, simplified | Element count and grouping |
| Audience | engineer, mixed, executive | Wording and technical sublabels, never element count |
| Motion | none, automatic semantic reveal, custom directives | Presentation only; the final static meaning remains complete |

Use these detail contracts:

- **Faithful:** retain every distinct source fact that the selected family can represent. Zone or split dense graphs instead of allowing an unreadable hairball.
- **Balanced:** keep the components and relationships that carry the main reader question; merge replicas and collapse authorized leaf groups.
- **Simplified:** retain capabilities, ordering, decisions, and outcomes; remove implementation detail only when the user authorized the reduction.

Audience changes explanatory vocabulary, not topology. Preserve fact-bearing labels, validator literals, identifiers, units, and proper nouns when they identify real systems. When an authorized adaptation changes an explanatory label, record the original and replacement wording in the fidelity ledger. Never replace a product with another product, guess a business capability, or remove a node merely because the audience is less technical.

## Emit a fidelity ledger

For every balanced or simplified adaptation, report:

```text
Detail: balanced; 14 source items -> 8 drawn
Kept: request path and terminal outcomes
Merged: worker-a, worker-b, worker-c -> Worker x3
Omitted: decorative note; duplicate legend
Moved to detail: metrics and audit branches -> operations-detail.mmd
Adapted label: "OAuth 2.0 authorization-code exchange" -> "Sign-in authorization exchange"
```

Account for every semantic source item as kept, merged, omitted, or moved to detail. Give a reason for any semantic omission. Do not report purely decorative source chrome unless its removal changes meaning.

## Audit rendered traceability

Mermaid owns final routing, so repair source structure rather than hand-editing generated paths.

Reject the render when:

- two important edges cannot be traced independently;
- an edge label collides with a node or another label;
- a connector crosses essential text or appears to terminate on the wrong node;
- a dense graph forces unreadable text or hides the primary path;
- a state, outcome, boundary, or magnitude depends only on hue;
- the accessible description contradicts the visible conclusion.

Try, in order: change `LR`/`TB`, reorder declarations without changing supplied semantic order, introduce truthful subgraphs, shorten only user-authorized explanatory text, choose a better family, or split the figure. Never patch an SVG path when the Mermaid source remains the canonical artifact.

## Sources

This guidance distills transferable design and validation ideas from [Cathryn Lavery's Diagram Design repository](https://github.com/cathrynlavery/diagram-design) at commit `f3622cf66a3c557cb2ead57b687a3c1ff63f5a2b` (MIT), adapted to this skill's Mermaid 11.16.0 and colorset contracts. Accessibility syntax and rendered ARIA behavior follow the [official Mermaid accessibility documentation](https://mermaid.js.org/config/accessibility.html).
