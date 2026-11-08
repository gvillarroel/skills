# Preserve RDF literal identity before SHACL validation

SHACL Core counts RDF terms on a path. OWL datatype semantics can
identify equal values represented by distinct RDF literals. For
example, an explicitly typed integer with a leading zero and the
same integer without it are different terms in the input graph.
In contrast, a plain string and the same lexical form explicitly
typed as `xsd:string` denote the same RDF term. [RDF 1.1 literal
identity](https://www.w3.org/TR/rdf11-concepts/#dfn-literal-term-equality)
and [SHACL maximum count](https://www.w3.org/TR/shacl/#MaxCountConstraintComponent).

## CLI reproduction

The same data and shapes were submitted to the original and revised
validators with inference disabled.

| Case | Original report | Revised report |
| --- | --- | --- |
| Integer literals with different lexical forms and the same numeric value | Missed maximum count violation | Reports maximum count violation |
| Boolean literals with different lexical forms and the same value | Missed maximum count violation | Reports maximum count violation |
| Plain string and its explicit `xsd:string` spelling | Reported a false maximum count violation | Conforms |
| A shape requires the other lexical form of an integer | Missed required value violation | Reports required value violation |

The revised loader scopes RDFLib's literal normalization flag to
parsing. It restores that flag when parsing completes or raises an
error. It canonicalizes the RDF-equivalent string spellings and
language tag case for all input graph roles. The regression checks
passed for Turtle, N-Triples, N3, RDF/XML and JSON-LD. They cover
maximum counts, exact values, duplicate strings across files, and
parser error recovery.

In a strict isolated Luna run `semantic-literal-identity-20261108-a`,
the skill ran its bundled validator, retained the original inputs,
and produced the two expected findings on the intended nodes. The
plain and explicit string forms produced no violation.

```powershell
uv run --script evaluations/contracts/test_rdf_literal_validation.py
uv run --script scripts/run-pi-skill-eval.py extract-ontologies --prompt-file evaluations/pi-prompts/ontology-literal-identity.md --run-id semantic-literal-identity-replay --model github-copilot/gpt-6-luna --thinking low --mode json --strict --expect-output data.ttl --expect-output shapes.ttl --expect-output validation.json --expect-output review.md --expect-output-json-field validation.json::summary.violations=2 --expect-output-json-field validation.json::summary.data_triples=6
```

## Parser boundary

The pinned parser still rewrites some unquoted numeric forms before
creating Turtle or N3 literals. Its constructor also normalizes
whitespace for `xsd:token` and `xsd:normalizedString` independently
of the global flag. The fix covers the tested explicit lexical
forms and graph-based SHACL Core comparisons. Opt-in SHACL-SPARQL
uses a separate query parser. [RDFLib literal constructor](https://github.com/RDFLib/rdflib/blob/7.6.0/rdflib/term.py).
