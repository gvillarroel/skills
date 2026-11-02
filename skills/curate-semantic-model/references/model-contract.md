# Executable model contract and typed errors

## Contents

- [Representation](#canonical-representation)
- [Independent input pair](#minimal-independent-input-pair)
- [Contract language](#supported-contract-language)
- [Competency questions](#executable-competency-questions)
- [Incremental validation](#incremental-validation-and-persistence)
- [Diagnostics](#actionable-diagnostics)

`semantic_model.py` implements a bounded JSON contract, version 1, not full JSON
Schema, SHACL, OWL reasoning, or semantic identity detection. Additional formal
checks may use an available processor or the optional `extract-ontologies` skill.

## Canonical representation

The model root contains `schema_version: "1"`, `contract_id`,
`contract_version`, `sources`, `nodes`, `relations`, and `bindings`. Optional
`metadata` is an object; optional `history` is a list. Field names and codes
are stable English identifiers; content can follow the requested output language.

| Record | Required content and meaning |
|---|---|
| `sources[]` | Nonempty `id`, `locator`, `text`. Preserve extra fields, including approvals, weights, required flags, and provenance. An inventoried evidence unit is not itself an extracted concept. |
| `nodes[]` | `id`, `type`, `label`, `definition`, `source_ids`; optional `attributes`, `aliases`. Define distinguishing scope. An alias does not create another node. |
| `relations[]` | `id`, `type`, `from`, `to`, `source_ids`; optional `review` containing `decision: "accepted"`, `reviewer`, `rationale` when required. A declared reviewer is not independent certification. |
| `bindings` | Source ID to a nonempty list of existing node IDs. This checks explicit representation and references, not semantic fidelity of the mapping. |
| `metadata` | Original values preserved when validating against a baseline; not interpreted as axioms. |
| `history` | Complete removed assertions and path proofs from reduction, retained outside the active graph for audit. |

IDs must be unique within each collection. Resolve references by exact ID, never
labels, prefixes, or substrings. Nodes and relations require at least one source
by default; a type profile can adjust its node minimum. Helpers read local files
without URL dereferencing or model calls.

## Minimal independent input pair

Save the first block as `contract.json` and the second as `model.json` in the
task workspace. These complete inputs need no external fixtures.

```json
{
  "schema_version": "1", "id": "minimal-items", "version": "1.0",
  "require_source_bindings": true,
  "types": {"Item": {"attributes": {}, "closed_attributes": true}},
  "relations": {},
  "checks": [{"id": "preserve-item", "query": {
    "op": "bindings", "source_id": "source:A"
  }, "expect": ["item:A"]}]
}
```

```json
{
  "schema_version": "1", "contract_id": "minimal-items",
  "contract_version": "1.0",
  "sources": [{"id": "source:A", "locator": "input#A",
    "text": "Retrieve existing reusable skills.", "selected": true}],
  "nodes": [{"id": "item:A", "type": "Item", "label": "Skill retrieval",
    "definition": "Find existing reusable skills for a task.",
    "source_ids": ["source:A"]}],
  "relations": [], "bindings": {"source:A": ["item:A"]}
}
```

```text
uv run --script <skill-dir>/scripts/semantic_model.py validate --model model.json --contract contract.json --report validation.json
```

Adapt this syntax with domain constraints and meaningful competency questions.

## Supported contract language

The contract declares `schema_version: "1"`, `id`, `version`, `types`,
`relations`, `require_source_bindings`, and `checks`. Choose domain-specific
type and predicate names.

A `types.<Type>` profile supports:

- `attributes`: attribute name to a specification; `required_attributes`: a list
  of previously declared attributes.
- `closed_attributes`: reject undeclared attributes if true; default false means
  tolerating them is the explicit policy, not an implemented check of their values.
- `min_sources`: a nonnegative integer, default 1.
- `outgoing`: predicate to `min`/`max` counts of distinct target IDs. These are
  record cardinalities, not OWL cardinalities or a claim that different IRIs
  necessarily denote different real-world entities.

Attribute specifications support `type` (`string`, `integer`, `number`,
`boolean`, `array`, `object`), `enum`, string/array `min_length` and `max_length`,
numeric `minimum` and `maximum`, and array `items_type`. They do not support
recursive shapes, regex, formats, nested object schemas, or arbitrary rules.
An unknown constraint is an engine error, not a partially passed check.

A `relations.<Predicate>` profile supports:

- `from_types`, `to_types`: endpoint application constraints, not `rdfs:domain`
  or `rdfs:range` inference axioms.
- `acyclic`: forbid cycles of this predicate only; do not combine hierarchies
  with different meanings.
- `symmetric`: normalize endpoint pairs for redundancy/exclusion checks; it does
  not materialize inverse edges or change directed queries.
- `review_required`: require the review declaration described above.
- `exclusive_with`: predicates incompatible on the same pair.
- `transitive`: a contract declaration, not OWL inference.
- `reduce_closure`: explicit permission to remove redundant materialized edges.
  It requires `transitive: true`, `acyclic: true`, `symmetric: false`. Enable it
  only when the questions and semantics allow preserving closure instead of
  every direct edge.

Version changed obligations; do not weaken them to pass an addition. Multiple
parents can be legitimate. Choosing a DAG does not make `broader` transitive.

## Executable competency questions

Each `checks[]` entry has `id`, `query`, and `expect`, an exact ID list. Operators:

```json
{"op":"nodes_of_type","type":"Requirement"}
{"op":"nodes_where","type":"Requirement","equals":{"domain":"context"}}
{"op":"bindings","source_id":"source:retrieve"}
{"op":"neighbors","from":"cap:skills","relation":"has_component"}
{"op":"reachable","from":"class:specific","relation":"is_a"}
```

Each query has exactly the fields for its operator:

| Operator | Required fields |
|---|---|
| `nodes_of_type` | `op`, `type` |
| `nodes_where` | `op`, `type`, nonempty `equals` object |
| `bindings` | `op`, `source_id` |
| `neighbors`, `reachable` | `op`, `from`, `relation` |

`nodes_where.type` is mandatory even when `equals` appears to identify a unique
role. Name one declared type; use separate complete checks for different types
rather than omitting the field. An incomplete query is an engine/input error,
so repair the owned contract before interpreting model conformity.

Results are compared as sorted ID sets. `nodes_where` uses conjunction over
declared attributes and exact scalar values with matching JSON/Python types:
no `true` to `1` coercion, and integer `1` differs from floating `1.0`. There
are no regex, range, or arbitrary-expression filters. `neighbors` returns direct
outgoing edges; `reachable` traverses directed paths of length at least one.
Reachability is declared topology, not proof of natural-language entailment.
An exact `nodes_of_type` expectation closes that type's snapshot and prevents
new instances until the contract is reviewed. Use narrower questions for open
addition workflows unless a closed set is the actual obligation.

The reducer needs at least one meaningful check. It retains every source and
node, combines only assertions equal in all fields except ID and `source_ids`,
and checks every transitive removal against questions and rules. It does not
simplify definitions. Weak questions cannot establish semantic preservation.

## Incremental validation and persistence

An addition contains only `sources`, `nodes`, `relations`, and/or `bindings`.
Records are appended and existing bindings unioned. Reusing an existing ID is
invalid. Editing or deleting needs an explicit model change, impact review, and
baseline validation.

`stage` validates the baseline, then the complete candidate. `reduce` records
removed assertions in `history`. Both create a new candidate only when conformant.
`validate --baseline base.json` preserves all earlier sources, their fields and
exact nested JSON types, plus existing metadata keys and values, including nulls.
Enums also compare exact nested types. This detects changed marks, not whether
a changed binding is semantically faithful.

Inputs and existing candidates are never overwritten. A report can be refreshed
at a separate path. Exit codes: **0**, conformant; **1**, data violations; **2**,
unsupported contract, malformed input, processor failure, or I/O error. Keep
`contract_status`, `semantic_status`, and `engine_status` separate.
`semantic_status` remains `not_run` even for a conformant JSON model. An unavailable
formal check must be reported as not checked.

## Actionable diagnostics

Data errors include `code`, `path`, `entity`, `type`, `expected`, `actual`,
`severity`, `message`, `contract`, and `rule_version`.

| Code | Meaning or repair |
|---|---|
| `UNDECLARED_TYPE` | Reuse a suitable profile or propose a versioned extension. |
| `MISSING_REQUIRED_FIELD` | Supply the missing field, such as a scope-preserving definition. |
| `MISSING_ATTRIBUTE`, `ATTRIBUTE_TYPE`, `ATTRIBUTE_ENUM`, `ATTRIBUTE_RANGE` | Repair a value that violates its declared profile. |
| `UNKNOWN_ATTRIBUTE` | Fix a typo or explicitly review an extension to a closed profile. |
| `DANGLING_REFERENCE`, `INVALID_BINDING` | An endpoint/represented node is absent, or a binding is not a nonempty list of existing node IDs. |
| `RELATION_TYPE_MISMATCH` | Use the correct relation, such as instance-of instead of subclass. |
| `CARDINALITY_VIOLATION` | A composite lacks enough distinct components. |
| `CYCLE_FORBIDDEN` | The addition creates a cycle of a predicate declared acyclic. |
| `INCOMPATIBLE_RELATION` | Incompatible predicates were asserted for the same pair. |
| `REVIEW_REQUIRED` | Supply an evidence-backed review declaration for the strong assertion. |
| `SOURCE_UNREPRESENTED`, `SOURCE_LOSS`, `SOURCE_MUTATION` | Representation is missing, or original evidence/marks changed. |
| `COMPETENCY_CHECK_FAILED` | A query no longer returns its agreed answer. |
| `REDUNDANT_RELATION` | Warning: inspect the entire assertion before deduplicating a repeated pair. |
| `UNSUPPORTED_CONSTRAINT` | Contract error: the requested rule was not checked. |

Structural checks precede competency queries. An empty or dangling binding
fails structural validation; competency checks are then not run. To test a
query-answer mismatch, keep references and all other structure valid while
changing the answer. Inspect the report before choosing an expected diagnostic;
a later query failure cannot replace an earlier structural finding.

For skills requirements, test retrieval, storage, and learning separately.
An ALL capability can group retrieval and storage without asserting identity
or propagating their selections to learning.
