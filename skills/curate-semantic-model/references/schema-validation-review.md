# Review versioned JSON Schema validation

Pin both source snapshots and their declared dialects. Keep schema
pointers, reference sites, and the instance path separate. The same
definition can govern more than one object, item, or conditional branch.

For two Draft 7 schemas, use the bundled graph check when a pull request
moves definitions, introduces local references, or rearranges a choice.

~~~text
uv run --script <skill-dir>/scripts/compare_schema_graphs.py before.json after.json --output schema-graph-review.json
~~~

Use `--assume-draft7` only when an input omits its dialect and the task
establishes Draft 7. The check uses standard validation with `format`
and content metadata treated as annotations. It resolves indexed local
JSON Pointer references offline and permits cycles guarded by descent
into instance children. External references, nested resource identifiers,
unsupported keywords and unguarded cycles leave the proof unresolved.

`equivalent` certifies identical validation graphs after the supported
rewrites. The report binds both raw SHA-256 hashes and both graph hashes.
The checker retains the multiplicity of `oneOf` branches and keeps
`additionalProperties` within its source object. `unknown` leaves
equivalence unresolved. Review dialect and format behavior independently
when the deployed validator enables another policy.

For an acceptance change, construct a complete JSON instance under the
governing path, including any required parent, trigger or companion field.
Replay the same instance against each original schema under its own
declared dialect, with only the pinned resources available. Record the
schema and instance pointers for a rejection. Test a nearby accepted
case, the old and new boundary, and an out-of-scope instance when the
location matters.

- Accepted after and rejected before establishes a newly accepted instance.
- Accepted before and rejected after establishes a newly rejected instance.
- Examples in both directions establish incomparability. A one-sided
  example establishes that direction. Certifying an overall relaxation
  or tightening also requires a proof of inclusion in the other direction.
- Report an unresolved direction when search runs out or validation cannot
  resolve a reference. Keep a loader error distinct from a rejection.

A schema view records validation semantics within its declared profile.
Retain the original files as the source for descriptions, defaults, examples
and other metadata that can matter to a different review.
[Draft 7 core](https://json-schema.org/draft-07/json-schema-core) · [Draft 7 validation](https://json-schema.org/draft-07/json-schema-validation) · [Directional witness generation](https://arxiv.org/abs/2202.12849)
