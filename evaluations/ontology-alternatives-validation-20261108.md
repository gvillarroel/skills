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
