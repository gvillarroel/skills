# Audit catalog field preservation

## Contents

- [Choose the scope](#choose-the-scope)
- [Bind inputs and identities](#bind-inputs-and-identities)
- [Declare compared fields](#declare-compared-fields)
- [Run and inspect the report](#run-and-inspect-the-report)
- [Review the meaning separately](#review-the-meaning-separately)

## Choose the scope

Use `scripts/audit_catalog_projection.py` to compare an authoritative JSON
registry with a proposed JSON projection or export. It reports changed,
lost and introduced records/fields. It does not extract an ontology,
interpret definition equivalence, or certify logical consistency.

Keep the full approved vocabulary and reviewed overrides before converting.
A reduced export may omit aliases or review flags. If the source is absent,
state that the conversion cannot be audited; do not recover missing values
from a shared display name or a generated description.

## Bind inputs and identities

Pin both exact UTF-8 files with raw-byte SHA-256 hashes. Choose each record
collection by an RFC 6901 JSON pointer. Collections may be arrays of objects
with an `id` field, or objects whose keys are record identities.
For arrays, set `source_id_path` and `projected_id_path` when the two formats
store local IDs at different pointers. Each defaults to shared `id_path`
(itself `/id` by default). Dictionary collections use their keys.

Use the source's stable keys. When local IDs differ, supply a reviewed,
version-bound bridge under `bindings.source` or `bindings.projected`.
Each supplied side must map every local collection ID exactly once to a
distinct stable ID. The helper rejects incomplete or merging bridges.
It never infers identity from labels. Keep homonyms as separate records.

The helper's identifiers use the local bounded nonblank-string
contract. A selected record collection cannot establish identities in another
collection or rewrite reference values automatically.

## Declare compared fields

Create a contract with `schema_version: 1`, `source_records`,
`projected_records`, optional `id_path`, `source_id_path`,
`projected_id_path`, `source_sha256`,
optional `bindings`, and a nonempty `fields` array.

~~~json
{
  "schema_version": 1,
  "source_records": "/terms",
  "projected_records": "/terms",
  "source_sha256": {
    "source": "<raw source SHA-256>",
    "projected": "<raw projected SHA-256>"
  },
  "fields": [
    {"name": "definition", "source": "/description", "projected": "/description"},
    {"name": "aliases", "source": "/synonyms", "projected": "/synonyms", "mode": "unordered"},
    {"name": "review", "source": "/description_certified", "projected": "/description_certified", "category": "review"},
    {"name": "key-order", "source": "/pk", "projected": "/pk"}
  ]
}
~~~

Field pointers are relative to a record. Categories are `semantic` (default),
`review`, or `provenance`. Object key order is immaterial. Arrays remain
ordered unless that field explicitly uses `mode: "unordered"`; duplicate
items still count. Preserve composite-key order and typed values. Missing,
null, false, empty text and empty arrays are distinct.

Select every field needed by the task. Fields outside this contract are
outside the claim. Fields absent from both sides appear as unchecked.
An empty authoritative collection or no selected authoritative fields is
not preservation evidence. Use `allow_empty_source: true` only when an empty
source is the declared input. Invalid numbers, decimal precision loss,
duplicate keys/IDs, unknown contract fields and unsupported pointers fail
closed. JSON pointers are bounded to 50 components.

## Run and inspect the report

Write a new report path outside the resource bundle. Capture the helper exit
rather than allowing an expected data difference to become a shell error.

~~~python
import subprocess
result = subprocess.run([
    "uv", "run", "--script", "PROJECT/scripts/audit_catalog_projection.py",
    "--source", "approved.json", "--projected", "export.json",
    "--contract", "projection-contract.json", "--report", "projection-report.json"
], check=False, capture_output=True, text=True)
~~~

Replace PROJECT with projects/semantic-skill-evaluation or its absolute path. Exit 0 means the selected
fields are preserved; exit 1 means the report contains differences; exit 2
means the comparison could not run or the output path already exists.
For exit 0/1, inspect the actual report. For exit 2, diagnose owned inputs
or an authorized helper defect before treating the check as complete.

The report separates record changes, field changes and categories, unchecked
fields and coverage counts. It binds source/contract hashes and gives
fingerprints of the declared field views under the reviewed identity bridge.
These fingerprints cover this field scope, not the entire ontology.
`category_fingerprints` additionally separates the declared semantic, review
and provenance field views. A changed review flag or locator can leave the
semantic field view unchanged. An unselected category is `not_selected`, and
an equal view without authoritative field values stays `not_checked`.
These are user-declared data categories; their hashes do not establish
logical or natural-language semantic equivalence.
Keep the report verbatim and put interpretation elsewhere.

## Review the meaning separately

`semantic_status` stays `not_checked` for every structural outcome.
A data change may be intentional, a paraphrase, a review-state change, or
conversion loss. Compare it with the governing sources and competency duties.
Do not use certification, recency or a successful parser as domain truth.

Retain source IDs and locators and preserve reviewed terms unless their
authority actually changes. A missing alias in a projection is not evidence
that the source withdrew it. For a review, show the exact term, property,
source version, both values, applicable rule and affected query. Offer the
concrete alternatives supported by that evidence; keep unresolved source or
identity questions pending.
