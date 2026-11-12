# NVIDIA Auto Ontology feasibility audit

Date: 2026-11-12. Owner: `curate-semantic-model`; related workflows:
`extract-ontologies` and `extract-with-ontology`.

## Decision and scope

Retain NVIDIA Auto Ontology as a candidate for relational semantic catalogs,
model interchange, reviewed vocabulary workflows, and relationship contracts.
Use an adapter with explicit identity and evidence policies before treating its
exports as reproducible document-ontology snapshots. This audit does not
promote a skill candidate or change the default extraction backend.

Inspected the Apache-2.0 repository at
[`fc43a82600e18b19d159c52023f54f5572f537ac`](https://github.com/NVIDIA/auto-ontology/tree/fc43a82600e18b19d159c52023f54f5572f537ac).
The application primarily derives a business ontology from relational schemas
and supports natural-language querying through SQL. A product/features dataset
loaded into a relational store is a plausible integration input. Crawling
arbitrary product pages and classifying AI versus non-AI claims still require
the document extraction and evidence workflow.

Read the repository instructions, contribution policy, model interchange
implementation, node identity implementation, semantic pipeline, management
skill, and relevant issue/PR conversations. No upstream files were modified.
The contribution policy currently declines external PRs.

## Components worth reusing

| Component | Application to the skills | Required adaptation |
| --- | --- | --- |
| Terms, descriptions, synonyms, certification, and column mappings | Vocabulary review and source-to-ontology mappings | Preserve these fields explicitly across every export/import boundary. |
| Native model interchange with explicit IDs and import reconciliation | Before/after snapshots and scoped updates | Supply stable IDs, canonicalize declared unordered collections, and validate readback. |
| Management skill relationship contracts | Review direction, multiplicity, null keys, units, grain, and authoritative sources | Bind each decision to document evidence and ontology constraints. |
| Staged edit, inspect, apply, and readback workflow | Review concrete changes before publishing | Keep reviewed overrides separate from regenerated proposals. |
| Read-only MCP catalog and query tools | Consume a deployed structured semantic catalog | Evaluate answerability and evidence fidelity on the actual catalog. |

Primary source references:
[modeling workflow](https://github.com/NVIDIA/auto-ontology/blob/fc43a82600e18b19d159c52023f54f5572f537ac/skills/nvidia-ontology-management/references/modeling.md),
[publication workflow](https://github.com/NVIDIA/auto-ontology/blob/fc43a82600e18b19d159c52023f54f5572f537ac/skills/nvidia-ontology-management/references/publication.md),
[model assembly and import](https://github.com/NVIDIA/auto-ontology/blob/fc43a82600e18b19d159c52023f54f5572f537ac/auto_ontology/dal/model_interchange.py),
and [MCP tools](https://github.com/NVIDIA/auto-ontology/blob/fc43a82600e18b19d159c52023f54f5572f537ac/mcp/auto_ontology_mcp/tools.py).

## Executed probe

[probe_interchange.py](probe_interchange.py) imports the unchanged upstream
Pydantic model classes and directly loads the upstream catalog node module.
It requires Python 3.12 or 3.13 and pins Pydantic 2.13.5. The executed command
selected Python 3.12. It verifies the checkout HEAD before importing.

The experiment contains 14 authored pairs from one synthetic two-table
product/features fixture. Five pairs permute foreign keys, joins, terms,
semantic foreign keys, or tables while retaining the payload. Nine pairs change
a definition, relationship direction, relationship enablement, relationship
presence, composite-key order, column type, term ID, display-name collision,
or duplicate-record multiplicity.

These controls compare serialized structural information after native schema
validation. The expected results are author-defined development controls;
they are neither independent ontology cases nor a sealed benchmark.
In particular, preserving composite-key order is a conservative interchange
contract, and duplicate records remain visible for validation rather than
being silently removed.

| Comparison strategy | Controls matched | Observed failure |
| --- | ---: | --- |
| Object keys sorted, arrays retained | 9/14 | All five harmless ordering controls differ. |
| Recursively sort every list | 13/14 | Hides a composite-key ordering change. |
| Sort only declared unordered collections | 14/14 | No failure in these controls. |

The third strategy is the local prototype in this probe. Its path whitelist
must be reviewed against each format revision. A 14/14 result does not
establish upstream export determinism, correct ontology extraction, or a
measured improvement in any skill's model accuracy.

Additional observations from the actual model classes:

- `ModelTerm` roundtrip drops supplied `synonyms`, `name_certified`, and
  `description_certified` fields because they are absent from the interchange
  schema. The exported DAL term projection also omits them.
- Two newly created `CatalogNode` objects receive different generated UUIDs.
  Supplying the same `existing_id` preserves the ID in both objects.
- Original and replay reports are byte-identical, SHA-256
  `d00e4bef55473c7c68946e6cff3fdedef9e2a8b8f3533301460293a34dcfbd81`.
  This proves reproducibility of these observations, not of independent LLM
  ontology generations.

Source evidence:
[interchange term schema](https://github.com/NVIDIA/auto-ontology/blob/fc43a82600e18b19d159c52023f54f5572f537ac/auto_ontology/server/model_interchange/schemas.py#L107),
[term export projection](https://github.com/NVIDIA/auto-ontology/blob/fc43a82600e18b19d159c52023f54f5572f537ac/auto_ontology/dal/model_interchange.py#L255),
and [node identity](https://github.com/NVIDIA/auto-ontology/blob/fc43a82600e18b19d159c52023f54f5572f537ac/auto_ontology/catalog/model/node.py#L18).

## Reproduction

Clone the upstream repository separately, check out the pinned revision, and
verify a clean worktree. From this skills repository, run:

```powershell
uv run --python 3.12 --script evaluations/curate-semantic-model/auto-ontology-20261112/probe_interchange.py <upstream-checkout> <new-report.json>
```

The report destination must not already exist. The script writes all case
outcomes, observed field preservation, identity observations, source revision,
and the SHA-256 hashes of both imported source modules. Its summary should
report 9/14, 13/14, and 14/14 respectively; synonym/certification preservation
should be false, fresh IDs equal should be false, and supplied IDs equal
should be true. Repeat with another report destination and compare hashes.

Imported source digests at the audited revision:

| Module | SHA-256 |
| --- | --- |
| `auto_ontology/server/model_interchange/schemas.py` | `54e3d56e3ffb1178d5b4bfc2872fce761ede8461c3d8ea0a753f7a0fa7ecfc39` |
| `auto_ontology/catalog/model/node.py` | `7ad91c1b809caceb34be1b5a23c0b1f9b5d31263226629aea2125c4bf7370be9` |

Both successful runs used the same upstream revision and Pydantic dependency.
An intervening offline replay could not resolve the wheel for its automatically
chosen interpreter; it produced no report and is not counted as an outcome.
The explicit Python 3.12 replay then completed successfully.

## Open integration limits

- Export ordering is an acknowledged issue:
  [#443](https://github.com/NVIDIA/auto-ontology/issues/443).
  [PR #450](https://github.com/NVIDIA/auto-ontology/pull/450) and
  [PR #457](https://github.com/NVIDIA/auto-ontology/pull/457) were open and
  unmerged at audit time. The probe does not execute their patches.
- Incremental compilation currently selects tables without an existing term.
  Changed sources need explicit reconciliation:
  [#258](https://github.com/NVIDIA/auto-ontology/issues/258) and
  [pipeline source](https://github.com/NVIDIA/auto-ontology/blob/fc43a82600e18b19d159c52023f54f5572f537ac/auto_ontology/semantic/pipeline.py).
- Reviewed names, descriptions, and synonyms need an override layer that
  survives regeneration:
  [#259](https://github.com/NVIDIA/auto-ontology/issues/259) and
  [term upsert](https://github.com/NVIDIA/auto-ontology/blob/fc43a82600e18b19d159c52023f54f5572f537ac/auto_ontology/dal/terms.py#L417).
- Per-element source/version/run/model provenance remains an open concern:
  [#260](https://github.com/NVIDIA/auto-ontology/issues/260).
- Structural split/merge history and atomic reviewed promotion need additional
  guarantees: [#269](https://github.com/NVIDIA/auto-ontology/issues/269) and
  [#268](https://github.com/NVIDIA/auto-ontology/issues/268).
- Ossie export projects a multi-table term onto one chosen table and removes
  attributes outside it. Audit this conversion before claiming lossless graph
  exchange:
  [projection implementation](https://github.com/NVIDIA/auto-ontology/blob/fc43a82600e18b19d159c52023f54f5572f537ac/auto_ontology/server/model_interchange/service.py#L107).
- The README describes OpenAI-compatible model endpoints. No Luna adapter,
  inference, embedding, crawler, SQL query, service, or database integration
  was executed in this audit. There were no model calls or paid evaluations.

## Next evaluation boundary

Keep the component as a candidate. Before adoption, evaluate the adapter on
independently authored document and relational cases with aliases, homonyms,
reviewed definitions, missing evidence, contradictory claims, relation
direction changes, and source updates. Include two independent generations
per unchanged input, stable identity checks, and separate extraction-quality
and canonicalization checks. Preserve both failed and successful results.
Any skill change should then follow the existing development, frozen
validation, and holdout process.

## Repository checks

The repository validators, pattern-ID validation, skill-independence tests,
payload check, and all 17 evaluation-harness tests passed on 2026-11-12.
The upstream checkout remained clean throughout the audit. These checks
validate publication integrity and the evaluation machinery; no skill
behavior was changed or promoted by this research record.
