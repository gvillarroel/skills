# Review five changes before the ontology handoff

The registry team is deciding which changes to merge. Review the two proposals in each packet against the material supplied for that packet. The five packets are independent. Treat the proposed axioms and shapes as alternatives for review, and leave the existing files as they are. Terms named in each packet are declared in its own model.

## T08 · Tide gauge intake

Locator: `gauge-intake@r12 §4.1`

> A temporary gauge must have a bench calibration or a field calibration before intake. A gauge with both calibrations also meets this requirement.

The asset register uses `TemporaryGauge` for a kind of `Gauge`. `BenchCalibrated` and `FieldCalibrated` classify the gauge itself. The team has supplied no calibration rule for its permanent gauges.

- T08-M requires each `TemporaryGauge` to belong to at least one calibration class.
- T08-R requires each `Gauge` to belong to at least one calibration class.

## C19 · Overnight survey crew

Locator: `survey-staffing@r6 §7.2`

> Each overnight survey crew must contain exactly two certified inspectors. The lead may also assign observers who are not certified inspectors.

The relationship `hasCrewMember` points from the crew to people. The source counts people, including when the staffing sheet mentions a person more than once.

- C19-V requires exactly two crew members in total and requires those two to be certified inspectors.
- C19-H requires exactly two certified inspectors among the crew members and leaves the total crew size open.

## A27 · Outage authorization

Locator: `access-handbook@r9 §3.4`

> For ordinary intake, an access request is accompanied by written unit approval. During a declared outage, a regional authorization may be attached to the request.

The change ticket asks what should happen to a request that has regional authorization during an outage. This is the entire approved passage for that decision. The owners of the handbook are available to answer a question.

- A27-K lets a regional authorization satisfy the approval requirement on its own during an outage.
- A27-D lets a regional authorization accompany the request during an outage and still requires written unit approval.

## L34 · Laboratory sample release

Locator: `sample-release@r15 §8`

> A released sample must have an instrument check that was calibrated for that sample.

The current rule is `ReleasedSample ⊑ ∃hasInstrumentCheck.CalibratedCheck`. The shared ontology declares `hasInstrumentCheck` a subproperty of `hasCheck` and `CalibratedCheck` a subclass of `CompletedCheck`. There are no other background axioms about these terms or imported ontologies. The change ticket asks for a representation that preserves the current release requirement.

- L34-T replaces the current rule with `ReleasedSample ⊑ ∃hasCheck.CompletedCheck`.
- L34-N keeps the current rule and also records `ReleasedSample ⊑ ∃hasCheck.CompletedCheck`.

## B46 · Loan submission records

Locator: `lending-feed@r4 §5.3`

> The intake service must reject a submitted loan record that has no approval code in the submitted data.

Intake runs directly on the submitted RDF graph with inference disabled. A record explicitly typed `LoanSubmission` is in scope. The sample graph contains `loan22 rdf:type LoanSubmission` and no `approvalCode` statement about `loan22`. Approval codes are strings.

- B46-P uses an OWL existential data property restriction that gives each `LoanSubmission` an `approvalCode` of type `xsd:string`.
- B46-J uses a SHACL property shape on `LoanSubmission` with path `approvalCode`, minimum count one and datatype `xsd:string`.

## Handoff file

Write `review.json` in the workspace root. Use a JSON object with the single key `items` and one item per packet in the order above. Each item has exactly these keys.

- `id` and `locator` copy the packet ID and locator.
- `status` is `select` when one offered option can be approved, `clarify` when the source owner needs to resolve a decision, or `reject` when the source settles the decision and neither offered option fits.
- `selection` is the approved option ID or JSON `null`.
- `basis` is a concise explanation of the decision using the packet.
- `question` is the question for the source owner or JSON `null` when no question is needed.
- `method` and `case` describe a check and the concrete input to use for it.
- `expectations` is an object keyed by the two option IDs. Give the expected result under each option for the same check and input.
- `observation` is JSON `null` when the check was proposed only. If you execute it, report the actual result and how it was obtained.

The handoff contains source excerpts and proposed options. No executed checks are supplied.
