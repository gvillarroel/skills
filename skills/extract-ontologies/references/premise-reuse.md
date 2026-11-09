# Plan premise reuse across reviewed source versions

Use this workflow when a prior numbered OWL premise ledger is approved
and both revisions have reviewed authority dependencies. Give each
source a stable lineage ID. Use the same premise ID only for the same
unit of authority. A matching label or repeated sentence alone leaves
identity unresolved.

The source packets have the keys `id`, `namespace`, `ontology_iri`,
`scope`, and `segments`. The first segment has ID `term-registry`.
The other segments contain a stable p-number ID and exact `text`.
The approved ledger uses `premises` with `id`, `axioms` in OWL
Functional Syntax, and a nullable `gap`.

Record both exact source file hashes and the approved ledger file hash.
Pin the authoring profile for each side, including the typed compiler,
grammar and projection policy when they are part of the workflow.
An example review envelope uses this shape.

~~~json
{
  "before_source_sha256": "<file digest>",
  "after_source_sha256": "<file digest>",
  "approved_ledger_sha256": "<file digest>",
  "before_profile_sha256": "<profile digest>",
  "after_profile_sha256": "<profile digest>",
  "dependencies": {
    "before": {
      "rows": {"p01": {"complete": true, "reads": [], "watches": ["applicable-exceptions"]}},
      "selectors": {"applicable-exceptions": {"complete": true, "members": []}}
    },
    "after": {
      "rows": {
        "p01": {"complete": true, "reads": [], "watches": ["applicable-exceptions"]},
        "p02": {"complete": true, "reads": [], "watches": []}
      },
      "selectors": {"applicable-exceptions": {"complete": true, "members": ["p02"]}}
    }
  }
}
~~~

A row's own text is implicit. List other source units in `reads` when
they supply meaning or scope. Use `watches` for relevant groups whose
membership can change, including currently empty exception or override
groups. List every current member under its stable selector. Mark a
review incomplete if its authority coverage is uncertain. Require
review of the current membership even when its previous list was empty.
The digests bind bytes and do not establish the completeness of a
review or authenticate its reviewer.

~~~text
uv run --script <skill-dir>/scripts/plan_owl_premise_reuse.py --before before.json --after after.json --approved-ledger approved.json --review dependency-review.json --output reuse-plan.json
~~~

The plan marks reuse only for a resolved prior row with identical own
text, projection and vocabulary, and a complete unchanged dependency
closure, including relative source order and watched memberships. It
lists removed premises separately. Re-author or review rows marked
`recompute` using the current context. Keep the plan separate from
the materialized graph. Check the whole candidate and the source
attribution of each retained or regenerated premise before approval.
Use a source-dependent reviewer or reasoner for those checks.
