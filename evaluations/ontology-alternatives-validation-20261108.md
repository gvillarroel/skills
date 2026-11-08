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
decisions each. In a separate generation diagnostic on two
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
