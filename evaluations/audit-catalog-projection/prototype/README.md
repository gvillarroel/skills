# Experimental projection-audit bundle

Status: **not promoted**. This exact candidate passes public development and a
fresh replay but fails the one-way private gate. The private phase also has a
required-reward interface defect. See the [full disposition](../evolution-20261112.md)
and [approved aggregate receipts](../validation-aggregate-20261112.json).

The complete candidate stays in the local study archive, with native bundle digest:

`sha256:a959fccd3eedeeaad160dafcdd006cd00432bb7ad3b37082c396753b934ed9b4`

Public code consists of the deterministic helper and its 49 tests under the
[semantic evaluation project](../../../projects/semantic-skill-evaluation/README.md),
plus its API contract. The helper bytes are the evaluated component; no complete
candidate bundle, runtime skill promotion or independent ontology-correctness
claim is published. No post-private fix or alternate candidate is selected.

## Inspect the deterministic component

The helper compares user-declared JSON fields and reviewed identities. It can be
used directly when source, projection and contract are already supplied:

```sh
uv run --script projects/semantic-skill-evaluation/scripts/audit_catalog_projection.py \
  --source approved.json --projected export.json \
  --contract projection-contract.json --report new-projection-report.json
```

Read the [field/identity contract](../../../projects/semantic-skill-evaluation/catalog-projection-contract.md)
before constructing inputs. Create the report's parent directory first. Exit0
means declared fields are preserved, exit1 reports differences and exit2 means
the check could not run. Every report retains `semantic_status: not_checked`.
Field equality does not prove a source ontology correct or resolve definition
equivalence.

Run the 49 deterministic regressions without a model:

```sh
uv run --script projects/semantic-skill-evaluation/scripts/test_audit_catalog_projection.py
```

Private execution errors and incomplete repetition prevent qualifying the agent
workflow. Future qualification needs a corrected preflighted instrument and
untouched independent cases; this consumed cohort cannot be a fresh gate.
