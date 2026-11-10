# Evidence questions for open ontology decisions

V45 tested a documentation-only change to the V44
`extract-with-ontology` bundle. The change asked the actor to keep an
underlying decision in review when the asserted graph already had a
supported uncertainty class. The review would identify the subject and
scope, cite the evidence already available, and request an observation
that distinguishes the remaining outcomes. A documented absence
remained a settled outcome in its stated scope. Selective clarification
and information sufficiency informed the design. [CLAM](https://arxiv.org/abs/2212.07769) ·
[Evaluating multi-turn information seeking](https://arxiv.org/abs/2608.14808)

## Frozen development comparison

The development cohort used four freshly authored families. They
covered preservation of an original artifact, a product component with
an unconfirmed failover mode, a route distinguished from both confirmed
and prohibited routes, and a fully resolved control. Both arms used
identical task roots, source bytes, ontologies, shapes, verifier and
materialization workflow. The same GPT-6 Luna low model ran one attempt
per cell in Harbor 0.18.0 with zero retries.

Forty-five preflight controls passed locally and in pinned Docker.
They covered alternative correct phrasing, generic questions, the
wrong subject or locator, copied keywords in a misdirected question,
unwarranted questions on resolved records, and malformed graph and
evidence outputs. Actor-container probes verified denied access to
study answers, prior artifacts and the private cohort.

| Metric | Published V44 | Review guidance |
| --- | ---: | ---: |
| Strictly admitted attempts | 2/4 | 3/4 |
| Full native passes | 1/4 | 3/4 |
| Correct evidence-backed triples in retained artifacts | 48/48 | 48/48 |
| SHACL conformance in retained artifacts | 4/4 | 4/4 |
| Complete reviews by scoped-evidence rubric in retained artifacts | 3/4 | 4/4 |
| Reviews that directly elicit the missing fact, sensitivity check | 3/4 | 3/4 |

All paired retained graphs had the same fingerprints. The masked
semantic audit agreed with the scoped-evidence verifier. In the
improved case the previous bundle omitted the question while the
candidate asked whether an authoritative record existed for the
specific missing method. A bare yes could leave the method
unidentified. A direct question would ask which method the record
specifies for the original artifact. The tighter sensitivity check
was diagnostic and did not replace the frozen rubric.

Two baseline attempts failed strict trace admission. One searched for
an absent reference file. Another submitted a shell command with a
trailing `&&`, which also occurred in the candidate attempt for that
case. The verifier scores of their retained artifacts remain diagnostic.
The custom agent expected a different skill inventory per arm. The
ordinary Harbor comparison flagged those lock differences. A separate
audit matched the normalized task, model, runtime and retry contract
after accounting for the declared treatment and serialization fields.

## Selection and independent cohort

The predeclared gate required 4/4 candidate and at least 3/4 baseline
strict admissions as well as graph, evidence and review requirements.
Both arms fell short of admission. The candidate was retained in the
study archive and the independent validation cohort remained sealed.
No validation inference ran. The three-family validation preflight
passed 30 graph and evidence controls twice, 12 semantic calibration
controls and three actor access probes. The comparison supports
further development of direct evidence questions. Private validation was unopened.

The local organizer study records the frozen protocol, task locks,
candidate and decision. Raw native jobs and blinded grades remain
in the local archive. The baseline job ID is
`36de075e-a035-464c-89ab-0eca115646ab` and the candidate job ID is
`2a2a9b35-2676-4076-a1f7-18904a485fb9`.
