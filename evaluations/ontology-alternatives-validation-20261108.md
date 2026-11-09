# Ontology alternatives and validation

The authoring skill distinguishes an unresolved interpretation from a
domain disjunction. For two branches, it separates inclusive choice,
exactly one, and at most one. It also separates constraints on each
value from constraints on the entire set or record. [OWL 2 class
expressions](https://www.w3.org/TR/owl2-direct-semantics/#Class_Expressions)
and [SHACL Core logical constraints](https://www.w3.org/TR/shacl/#core-components-logical).

The fixed-ontology skill preserves source-backed assertions and runs
the supplied validation separately. An unresolved alternative stays
together in review when the supplied model cannot express it faithfully.
The review records the applicable target, constraint, and observed
outcome.

## Results

| Check | Result |
| --- | --- |
| Local acceptance matrix | Seven methods passed, including 54 value and record conformance cases. Additional controls covered target selection, identical values on different paths, OWL-RL materialization, and separate assertion-evidence and validation results. |
| Authoring with Luna | One forward inclusive OWL class axiom matched the reference. The emitted SHACL contract passed nine independent conformance cases, including both packets, neither, incomplete mixed packets, wrong datatypes and a record outside the target. |
| Fixed-ontology extraction with Luna | All 12 reference assertions and row or cell evidence passed. Exactly three expected `sh:xone` violations were reported. The evidence-backed overlap remained in the graph, and neither uncertain candidate ID became an asserted fact. |

The separate OWL-RL controls check materialization behavior. The
forward authoring grader checks the stipulated OWL structure and
executes the SHACL conformance cases with inference disabled.
Both accepted forward runs used `github-copilot/gpt-6-luna` in strict
isolated Pi mode. Run IDs were `semantic-authoring-alternatives-20261108-d`
and `semantic-guided-alternatives-20261108-c`. The independent graders
also rejected a nonexclusive SHACL replacement, an OWL converse added
by equivalence, and a source cell locator moved to the wrong row.

Earlier strict runs exposed missing environment dependencies and a
bundled shell call that the exact-command gate did not recognize as a
standalone invocation. One earlier guided ledger also used an incorrect
full IRI for `rdf:type` and failed independent evidence checking.
The accepted run used pinned tools and generated a successful bundled
evidence check. The independent grader accepts either a complete
source row or an exact cell quotation with its row and column locator.

## Reproduce

Run from the repository root.

```powershell
uv run --script evaluations/contracts/test_ontology_alternatives.py
uv run --script evaluations/contracts/test_ontology_guided_extraction.py
uv run --script scripts/run-pi-skill-eval.py extract-ontologies --prompt-file evaluations/pi-prompts/ontology-authoring-alternatives.md --model github-copilot/gpt-6-luna --thinking low --mode json --strict --run-id semantic-authoring-alternatives-replay --expect-output ontology.ttl --expect-output shapes.ttl --expect-output review.md
uv run --script evaluations/contracts/grade_ontology_alternatives.py authoring evaluations/runs/semantic-authoring-alternatives-replay/workspace
uv run --script scripts/run-pi-skill-eval.py extract-with-ontology --prompt-file evaluations/pi-prompts/ontology-guided-alternatives.md --model github-copilot/gpt-6-luna --thinking low --mode json --strict --run-id semantic-guided-alternatives-replay --expect-output data.ttl --expect-output evidence.json --expect-output checks.json --expect-output validation.ttl --expect-output review.md --expect-output-json-field checks.json::status=passed --expect-output-json-field checks.json::evidence_covered_triples=12
uv run --script evaluations/contracts/grade_ontology_alternatives.py guided evaluations/runs/semantic-guided-alternatives-replay/workspace
```

The raw run directories are local artifacts. The prompts, source fixtures,
graders and local acceptance matrix are versioned. The separate
[glossary and routing report](ontology-guided-cross-file-20261108.md#glossary-and-extraction-routing)
covers glossary-only and extraction-plus-glossary behavior.

## Branch selection and value counts

The count guidance distinguishes existence, exactly one qualifying
value, and exactly one value in total with an allowed type. A value
belonging to both classes in the allowed union counts once. A
qualified count alone allows values outside the qualifying class. A total
typed count also checks those values. Separately, `sh:targetClass`
follows subclass declarations in the submitted data graph even when
optional inference is disabled. [OWL 2 cardinality semantics](https://www.w3.org/TR/owl2-direct-semantics/#Class_Expressions)
and [SHACL class targets](https://www.w3.org/TR/shacl/#targetClass).

The local suite now has nine methods. The added count matrix passed
all 21 cases, including two different qualifying values, one value in
both classes, and one qualifying value with an unqualified value.
A separate target control found the subclass instance and left the
unrelated instance outside the check.

An offline HermiT probe passed 27/27 consistency checks and 9/9
entailment checks under OWL 2 DL. It distinguished an explicit zero
count from missing assertions, and two names from two explicitly
different individuals. With two qualifying named fillers, exact-one
entails equality unless difference is established. With a qualifying
filler and an explicitly disjoint other filler, only the total typed
count rejects the extra value. The local result SHA-256 is
`fc4f26ca218490557a1fc921095b88dac72d189709416599469638951b4e6de3`.

The count-only authoring fixture supplies three consumer contracts.
Its independent grader executes the resulting shapes against a
separate 22-check matrix, including the subclass focus node. The
strict Luna run `semantic-count-scope-20261108-c` loaded the revised
reference and passed 22/22. The grader rejected mutations that used
exclusive branch membership, replaced a qualified bound with a total
bound, or substituted a fixed node for the class target. An earlier
self-check failed because it expected a named node shape in the
human-readable result. The final evaluator checks the actual RDF
focus nodes with optional inference disabled. The final guided run
`semantic-guided-alternatives-20261108-d` retained all 12 supported
facts and reported exactly the same three expected violations.

```powershell
uv run --script scripts/run-pi-skill-eval.py extract-ontologies --prompt-file evaluations/pi-prompts/ontology-count-scope.md --run-id semantic-count-scope-replay --model github-copilot/gpt-6-luna --thinking low --mode json --strict --expect-output shapes.ttl --expect-output review.md
uv run --script evaluations/contracts/grade_ontology_count_scope.py evaluations/runs/semantic-count-scope-replay/workspace/shapes.ttl
```

The research that exposed the ambiguity between existence and
exact-one in an RDF triple projection is recorded separately.
[Evidence attribution study](ontology-attribution-20261108.md#matched-comparison)

## Premise-local cardinality rewrites

The review fixture covers a safe exact-count rewrite, an equivalent
whole ontology with changed premise attribution, mismatched qualifiers
and guards, a count on a named individual, an impossible class in a
consistent ontology, and required versus optional exclusive branches.
The eight expected decisions were checked with 16/16 HermiT probes
under OWL 2 DL. The local reasoner receipt SHA-256 is
`f328eca8117807fdfafe0c834e18c55ea0b64555cd3e384c6399f838a8220d28`.
[OWL 2 Direct Semantics](https://www.w3.org/TR/owl2-direct-semantics/#Inference_Problems)

The original shorthand output schema passed 8/8 in one strict Luna
run. The other run interpreted the range of IDs as one key and
passed 3/8. The revised schema enumerates each required key. Two
fresh strict runs of the released skill, `semantic-count-guidance-20261108-c`
and `semantic-count-guidance-20261108-d`, both read the disjunction
reference and passed 8/8. The grader requires the exact case and
field sets and JSON boolean values.

```powershell
uv run --script scripts/run-pi-skill-eval.py extract-ontologies --prompt-file evaluations/pi-prompts/ontology-cardinality-rewrite.md --run-id semantic-count-guidance-replay --model github-copilot/gpt-6-luna --thinking low --mode json --strict --expect-output reviews.json
uv run --script evaluations/contracts/grade_ontology_cardinality_rewrite.py evaluations/runs/semantic-count-guidance-replay/workspace/reviews.json
```

## Syntax-bearing evidence spans

The OWL Primer's minimum cardinality example supplies the named
individual in the enclosing `ClassAssertion`. In a public development
packet, the source fragment ended before the individual. Both count
policies failed both runs on the clipped packet. Restoring the exact
enclosing assertion at the same coordinate gave 4/4 correct Luna
runs and one exact pair per policy under the unchanged HermiT reference.
Restoring only the prose cue gave 1/4 whole-and-premise passes. All
four restored the individual minimum at its code coordinate, while
three also asserted logical claims at coordinates the frozen rubric
treated as contextual. These are sensitivity results on a consumed
source. [OWL Primer cardinality examples](https://www.w3.org/TR/2012/REC-owl2-primer-20121211/#Property_Cardinality_Restrictions)

The isolated review fixture covers a complete named assertion, a
code block with syntax-sensitive comment boundaries, and a guarded
rule offered as evidence for a global claim. Two strict Luna runs,
`semantic-evidence-boundary-20261108-a` and
`semantic-evidence-boundary-20261108-b`, read the revised workflow
and passed 3/3 each. A Rust compiler confirmed the three discriminants
in the complete example and rejected the flattened example.

```powershell
uv run --script scripts/run-pi-skill-eval.py extract-ontologies --prompt-file evaluations/pi-prompts/ontology-evidence-boundary.md --run-id semantic-evidence-boundary-replay --model github-copilot/gpt-6-luna --thinking low --mode json --strict --expect-output evidence.json
uv run --script evaluations/contracts/grade_ontology_evidence_boundary.py evaluations/runs/semantic-evidence-boundary-replay/workspace/evidence.json
```

## Types supplied by another premise

The borrowed-scope fixture tests a type added to the values of
a qualified maximum and a type added to the condition of a
required field. A separate premise makes those rewrites equivalent
in the complete ontology. The isolated premise accepts additional
models after the rewrite. The positive control states the
all-values type in the same premise, so the rewrite preserves both
scopes. HermiT passed six bidirectional entailment contrasts and
four consistency probes. The reasoner receipt SHA-256 is
`e6b74749bbdfb091a18e45ae16a7e6983ba8b8a180955415c09e94c359cd5705`.
[OWL 2 class expression semantics](https://www.w3.org/TR/owl2-direct-semantics/#Class_Expressions)

Two strict Luna review runs of the released skill passed 3/3
decisions each. The refined fixture makes the open-world name
semantics, the typed literals, and the shared witness in the
guard explicit. Two further strict Luna runs,
`semantic-borrowed-scope-explicit-a` and
`semantic-borrowed-scope-explicit-b`, each passed 3/3 with
byte-identical decision files. The independent formal report
also reproduced byte for byte.

In a separate generation diagnostic on two
already used WoT and ACME cases, the baseline and three wording
variants each passed 0/4 strict runs under the original rubric.
The variants tested a compact rule, a worked example, and a
premise-first workflow instruction. The scope decision test
measures review of supplied alternatives. The generation
diagnostic shows the remaining authoring gap.

```powershell
uv run --script scripts/run-pi-skill-eval.py extract-ontologies --prompt-file evaluations/pi-prompts/ontology-borrowed-scope.md --run-id semantic-borrowed-scope-replay --model github-copilot/gpt-6-luna --thinking low --mode json --strict --expect-output scope-review.json
uv run --script evaluations/contracts/grade_ontology_borrowed_scope.py evaluations/runs/semantic-borrowed-scope-replay/workspace/scope-review.json
```

## Stable choice among admitted representations

Reissuing opaque IDs changed the lexicographic ID winner between
two equivalent bundles in a synthetic control. The resulting OWL
and ledger bytes changed even though both outputs passed reasoning.
The bundled chooser sorts canonical axiom lists by UTF-8 bytes
after semantic admission. It separates an empty admitted bundle
from an unresolved group with no admitted candidates.

An independent HermiT check confirmed all 11 expected option
dispositions in the fixture, including permitted overlap outside
an exclusive guard, typed literal mismatches, and explicit context.
Four unit tests exercise invariant content order, strict input,
empty versus unresolved, and deterministic UTF-8 output. The
formal receipt SHA-256 is
`4fa75bece1070a233503b59148fdb45f41ff7bca95dedf368394a27d6c2a5021`.

Two strict baseline Luna runs each passed 1/6 exact decisions.
Prose guidance alone reached 4/6 and 6/6. The lower result chose
an equivalent bundle outside the expected content ordering.
The first helper variant produced two correct artifacts, with
one strict failure from an ambiguous partial file edit. The
final guide asks the agent to write the complete admitted JSON
once. Two strict final Luna runs invoked the helper, retained all
nine admitted bundles, passed 6/6 each, and emitted identical
decision bytes. This fixture measures review and representation
selection for fixed alternatives.

```powershell
uv run --script evaluations/contracts/test_ontology_comparison_bundle.py
uv run --script scripts/run-pi-skill-eval.py extract-ontologies --prompt-file evaluations/pi-prompts/ontology-stable-option-selection.md --run-id semantic-option-stable-replay --model github-copilot/gpt-6-luna --thinking low --mode json --strict --expect-output selected-options.json
uv run --script evaluations/contracts/grade_ontology_stable_option_selection.py evaluations/runs/semantic-option-stable-replay/workspace/selected-options.json
```

## Premise-local Boolean comparison views

The standalone utility builds a bounded reduced decision form
from class implications, equivalences and exclusions within each
premise. It treats OWL restrictions as Boolean atoms and keeps
unresolved rows and unsupported axioms in the source order.
Use the output as a proposed comparison ledger. Verify the
whole ontology and each premise against the original with an
independent OWL 2 DL reasoner. [Bryant's reduced decision graphs](https://doi.org/10.1184/r1/6622400.v1)

Nine executable controls passed, including all 256 three-variable
truth tables. In a separate artifact fixture, seven HermiT checks
confirmed valid equivalence and caught a source attribution shift
that preserved whole-ontology meaning. The independent proof
receipt SHA-256 is
`01dee88d2a67ccd24558ffd790983fcfab37af154f5f93924204b8bbb95097d2`.

On ten distinct public development sources, HermiT accepted
30/30 changed comparison views of correct outputs. The raw exact
pair counts were 2/10 for the separate-records arm and 4/10 for
both grouped selectors. The independently verified comparison
counts were 4/10 and 6/10. The released script matched the
prototype's ledger content for all 60 scored artifacts.
This measures representation stability on already correct graphs.

Two final strict Luna runs of the standalone skill passed all six
artifact checks. Each invoked the bundled script for all three
ledgers. The equivalent pair produced identical comparison
files, and the attribution-shifted input retained a different
file. Both runs preserved the three raw input ledgers.

```powershell
uv run --script evaluations/contracts/test_ontology_boolean_comparison.py
uv run --script scripts/run-pi-skill-eval.py extract-ontologies --prompt-file evaluations/pi-prompts/ontology-boolean-comparison-view.md --run-id semantic-boolean-replay --model github-copilot/gpt-6-luna --thinking low --mode json --strict --expect-output left-source.json --expect-output right-source.json --expect-output shifted-source.json --expect-output left-view.json --expect-output right-view.json --expect-output shifted-view.json
uv run --script evaluations/contracts/grade_ontology_boolean_comparison_view.py evaluations/runs/semantic-boolean-replay/workspace
```

## Actionable extraction review

The guided-extraction reference distinguishes an unresolved source
interpretation, a supported claim that the model cannot express,
an observed constraint finding, a blocked check, and contextual
text. An open alternative retains its source and the question that
would resolve it. A check records its scope, expected observation,
and observed result or blocker.

A new isolated review case covers five independently scored source
rows. It includes a known disjunction with a missing mapping, an
overlap ambiguity, a supported measurement that violates SHACL, a
timestamp check without its required input, and context. Local
pySHACL verified the measurement and boundary controls. The guided
candidate passed the strict Pi event and output gates and scored
20/20 on the blinded rubric. The baseline artifact scored 18/20
and failed the strict tool gate. Its report treated a completed
finding as blocked and conflated the measured fact with the finding.
The candidate read the revised reference. The baseline did not
read its counterpart. There was one strict isolated Luna slot per
arm, so this contrast does not isolate the effect of wording.

The separate ontology-authoring wording candidate tied its baseline
at 13/16. Both selected an inclusive interpretation where the
source left overlap unresolved. That candidate remained in
development. All four runtime invocations used
`github-copilot/gpt-6-luna`. The frozen blinded qualification
receipt SHA-256 is
`8d89e92e0fbede58a84e89f2be123708c2580bbd1f3625928ae6d505bd270b7b`.

## Integer interval comparison

The comparison utility recognizes a direct intersection of two
restrictions on `xsd:integer` with one lower and one upper bound.
It keeps the original inclusive or exclusive facets and explicitly
typed literal spellings. The narrow rule applies to a nonempty
interval and keeps it in its source-owned premise.

In two independently correct outputs from a prospective Java SE 21
case, one output joined the bounds in a single datatype restriction
and the other intersected two restrictions. The previous views
differed. The new views matched in canonical RDF, OWL Functional
Syntax and premise-ledger bytes. Among four prospective public
sources the frame arm gained one verified exact comparison pair
from 2/4 to 3/4. The raw extraction counts were 7/8 correct runs
and 2/4 exact pairs.

Eleven repository tests passed. A pinned HermiT verifier matched
34 expected results for the Java pair, positive rewrites and
counterexamples. The controls distinguish disjunction, mismatched
datatypes, a wrong endpoint or governing class, and shifted premise
ownership. Both strict isolated Luna runs on the final bundle
executed the utility for all three input ledgers. The combined
and split ranges produced identical views. The shifted premise
kept a distinct view. The output hashes repeated across the two
runs, and the original three ledgers passed the artifact check.

The HermiT receipt SHA-256 is
`e3a2e145465f24c15ca3118036e1e43c61dafa0cc9d94d43417e874faf535810`.
The isolated check receipt SHA-256 is
`60e73e71ade9342e14f5f43ab8c5f423d69f245897cb75c5a4c1fb65d23cb60e`.
[Java SE 21 primitive ranges](https://docs.oracle.com/javase/specs/jls/se21/html/jls-4.html#jls-4.2.1) · [Isolated evaluation prompt](pi-prompts/ontology-integer-interval-view.md)
