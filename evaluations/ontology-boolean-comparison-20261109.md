# Reviewed Boolean rule comparison

The document comparison command now compares reviewed Boolean rules.
The draft binds both source revisions by SHA-256 and pins every rule
to an exact line citation. It supplies the stable atom identities.

The comparator checks the whole rule in both directions. The result
includes a witness for each populated truth-table region and a semantic
fingerprint for each side. Equivalent syntax gives the same fingerprint
over the same atom identities, including when an expression mentions a
variable that cannot change its truth value. An inconsistent or
tautological side yields a hold.

## Release checks

The full skill suite passed 200 tests, including 13 CLI cases for the
new mode. The cases cover necessary and sufficient conditions,
biconditionals, negation scope, split requirements, counterexamples,
vacuity, evidence and source bindings, and immutable output. An
independent Z3 check agreed on all 160 seeded formula pairs, including
the directional witnesses, joint satisfiability and essential atoms.

Three strict isolated GPT-6 Luna low runs invoked the bundled command
with the reviewed inputs. Both runs on the same inclusive-versus-
exclusive rule pair produced byte-identical results. The inconsistent
rule set produced the expected hold.

## Development evidence

With four authored pairs derived from SHACL and JSON Schema and the
same reviewed atom inventory, the formula-and-solver path produced the
correct classifications in two runs. Direct classification scored
three out of four. The open-vocabulary translation variants were less
reliable because they changed or synthesized quote spans. Automatic
translation remains under development. [SHACL logical constraints](https://www.w3.org/TR/shacl/#core-components-logical) · [JSON Schema conditional validation](https://json-schema.org/understanding-json-schema/reference/conditionals)

~~~text
uv run --no-project --python 3.14 python -B -m unittest discover -s skills/curate-semantic-model/scripts -p "test_*.py"
uv run --script scripts/validate-skills.py
uv run --script scripts/check-repo-payload.py
~~~

[Document comparison options](../skills/curate-semantic-model/references/document-versions.md#compare-reviewed-boolean-rules)
