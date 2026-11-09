# Witnesses for ontology review decisions

## Development design

Two independently authored prompts exercise source authority and
validation in separate isolated skill workspaces. The authoring
packets cover class scope, qualified counts, permission versus
substitution, logical entailment and submitted-graph validation.
The fixed-model packets cover an unresolved fact, an established
fact without a mapping, an inclusive policy, an observed violation
and a missing verification input. The guides and prompts use
different domain terms. The prompts and findings are public
development evidence. [Authoring prompt](pi-prompts/ontology-contrastive-review.md) ·
[Fixed-model prompt](pi-prompts/ontology-guided-decision-types.md)

Reviewers checked each decision, source locator, question and proposed
test independently. The same case must give the stated result for
each option. An OWL consistency witness for absence needs explicit
negative information. A proposed entailment check must query a
consistent ontology with the relevant background axioms. SHACL
checks focus selection and conformance on the stated submitted
graph. Preserve the expected results separately from any executed
observations. HermiT and pySHACL checked the formal authoring oracle
before the actor outputs were reviewed.

For the fixed-model runs, RDFLib checked the seven expected triples
after mapping plain RDF 1.1 string syntax to `xsd:string`. It also
checked for extra assertions. Exact evidence quotes were checked
against the embedded files. The review criteria required preserving
the rail claim as a mapping gap, keeping both confirmed seal codes
despite the validation failure, and keeping receipt filing distinct
from signature verification.

## Isolated forward qualification

The comparison used Pi 1.4.0 in strict JSON mode and
`github-copilot/gpt-6-luna` with low thinking. The published baseline
was `0949281428967dc4ef6ccf9b6d79199fcb501e86`. Each arm read the
same frozen prompt for that skill. The candidate retained the
standard runtime payload and write surface.

| Authoring wording | Strict runs | Correct dispositions | Usable distinguishing checks |
| --- | ---: | ---: | ---: |
| Published baseline | 2/2 | 10/10 | 8/10 |
| Differences and scope checks | 2/2 | 10/10 | 8/10 |
| Explicit negative facts | 2/2 | 10/10 | 9/10 |
| Consistency with witness before entailment | 2/2 | 10/10 | 10/10 |

Both baseline reviews selected the right rule for the laboratory
case. One treated a missing assertion as an OWL negative fact.
The other proposed a witness satisfying both options. The next
wording required explicit absence or a query for the stronger
axiom. One run then proposed interpreting entailment from a
witness that made both options inconsistent. Checking consistency
with the witness corrected that regression. The final candidate
also passed the earlier three-packet overlap qualification, with
all three dispositions and expected outcomes correct.
[Overlap regression prompt](pi-prompts/ontology-overlap-policy.md)

A further strict run passed the tracked authoring prompt after
removing its extra trailing blank line.

| Fixed-model wording | Strict runs | Exact seven-triple graphs |
| --- | ---: | ---: |
| Published baseline | 1/2 | 1/2 |
| Separate fact, mapping and policy decisions | 2/2 | 1/2 |
| Resolve confirmed constraint violations with evidence | 2/3 | 1/3 |
| Keep other supported facts for a pending record | 2/3 | 3/3 |
| Separate settled policies from representation gaps | 2/2 | 2/2 |

Graph scores include inspection of artifacts from runs that failed
the strict event gate. The baseline and fourth candidate each had a
run that called RDFLib from an interpreter that did not provide it.
Another run wrote an incomplete evidence ledger and dropped
source-backed type assertions while trying to pass the checker.
The fourth candidate kept the complete graph in every run. One
review introduced an unsupported representation gap while answering
a settled policy question. The final two runs had all five review
items correct, with exact quotes and the same canonical graph.
The graph fingerprint was
`f638acc506d8763969121ca8c463c911df8a145a54dd89b7241acbd1678bc1fb`.
The two review files used different prose.
The earlier permit extraction and glossary case also passed strict
execution with six evidence-covered assertions and three glossary
entries. [Permit regression](ontology-guided-cross-file-20261108.md#glossary-and-extraction-routing)

~~~powershell
uv run --script scripts/run-pi-skill-eval.py extract-ontologies --prompt-file evaluations/pi-prompts/ontology-contrastive-review.md --model github-copilot/gpt-6-luna --thinking low --mode json --strict --run-id ontology-contrastive-review-replay --expect-output review.json
uv run --script scripts/run-pi-skill-eval.py extract-with-ontology --prompt-file evaluations/pi-prompts/ontology-guided-decision-types.md --model github-copilot/gpt-6-luna --thinking low --mode json --strict --run-id ontology-guided-decision-replay --expect-output review.json --expect-output data.ttl
python -B -m unittest discover -s evaluations/contracts -p 'test_ontology*.py'
~~~

The repository suite passed 38 ontology tests and 17 Pi harness
tests. The pattern, skill, independence, and payload validators
passed. The forward runs qualify the review guidance on public
development cases.

## Deterministic checks

On four synthetic families, the full expected matrix contained 34
case and observation combinations. An exhaustive selector chose 17
of them, including an out-of-scope check for each family. These
separated all 50 distinct pairs of supplied options. Two generic
branch examples per family separated 20 pairs. HermiT matched all
92 OWL case and option bundles. pySHACL matched 89 shape and graph
cases and verified focus selection independently. The observed report
repeated byte for byte after replacing generated blank-node labels
in SHACL result paths with canonical fingerprints.

| Family | Generic cases | Selected distinguishing cases with boundary checks |
| --- | ---: | ---: |
| OWL class scope and overlap | 11/15 | 15/15 |
| OWL value scope and cardinality | 0/10 | 10/10 |
| SHACL fields and shared values | 4/10 | 10/10 |
| SHACL value scope and cardinality | 5/15 | 15/15 |

This is coverage of the proposed comparisons. An independently
tested SHACL mutant kept the expected result for the separating
case while selecting the wrong targets. Shared requirements, an
intended positive case, and focus boundaries therefore remain
separate validation items. If two candidates have the same expected
result for every available witness, further evidence is required
to distinguish them.

## Vocabulary evolution experiment

The current published planner invalidates every prior premise when
the registry text changes. Ten archived PR pairs had an unchanged
typed registry and 14 eligible premises among 37. For a separate
diagnostic, an unused declaration and a registry reordering were
introduced independently into each head packet. A prototype with
reviewed term dependencies made all 74 correct decisions. The
published global guard made 46 correct decisions and discarded 28
eligible reuses. Across 27 synthetic controls, the prototype made
27 correct decisions, the global guard made 21 and missed six
eligible reuses, and comparing only emitted symbols made 13 and
allowed 14 unsafe reuses.

That experiment assumes a fully reviewed vocabulary closure and an
order-independent typed registry. It remains a development prototype.
Reuse of an interpretation and reuse of a reasoner result need separate
proofs. An added role, nominal, or imported axiom can change a query over
existing terms. An independent in-memory test on ten synthetic OWL 2 DL
pairs matched full HermiT with BOT, TOP and STAR in 1,158 entailment
checks whose query symbols were in scope and 180 consistency checks.
The three extraction modes also detected a change confined to an
import when both import closures were included. [Locality-based modules](https://arxiv.org/pdf/1207.1641)
