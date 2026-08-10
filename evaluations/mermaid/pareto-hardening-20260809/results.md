# Mermaid hardening Pareto study

Date: 2026-08-10

## Outcome

Harbor 0.18.0 promoted `visible-data-canonical-family` with skill digest `sha256:bc4dd6810999f700fcbe4e9f217c2b48c58c05748af50ead534ada429d27f3f8`. The promoted bundle is byte-identical to `skills/mermaid`, contains 14 files / 398,345 bytes, and keeps the progressive-disclosure entry point at 57 physical lines.

| Split | Frozen baseline | Promoted candidate | Gain | Errors | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: |
| Hard development, 8 cases x 2 attempts | 6/16 (0.375) | 16/16 (1.000) | +0.625 | 0 | 0 |
| Fresh V6 holdout, 5 cases x 2 attempts | 5/10 (0.500) | 10/10 (1.000) | +0.500 | 0 | 0 |

The final holdout decision was `PROMOTE`. Its sealed development profile digest is `sha256:ee762635b069c182a6a2adf58285a01080827d27ece4c2cf97c2cd7b852e4214`, and its untouched V6 holdout job signature is `sha256:32c9abaa64957cb1a8ea795a4795a14374898b34e5e9ef8cf10987911f26bd95`.

## Evaluation contract

- Run every trial with `gpt-5.6-luna` at medium reasoning and two independent attempts per case.
- Require all eight rewards at exactly 1.0: routing, palette declaration, visible palette, palette influence, render, visual fidelity, data fidelity, and routing metadata.
- Render every answer to SVG and PNG. Parse visible SVG text and geometry, measure alpha-weighted palette pixels in the PNG, and compare a counterfactual render with the generated palette configuration removed.
- Reject missing or off-screen terms, excessive aspect ratios, forbidden extended colors in standard mode, weak extended-color coverage, palette configuration that does not materially alter visible pixels, wrong family IDs/declarations, lost values, invented values, and malformed Mermaid.
- Freeze the selected skill before opening holdout. The earlier V5 holdout was discarded without execution after a post-authoring candidate change; V6 was newly authored, sealed, and used only for the final comparison.

## Hard cases

Development covered conflicting Pie requests with signed data, inferred XY, Timeline, multipredecessor Gantt, quantitative Treemap, quoted Sankey, software Class structure, and a Treemap whose smallest branches had to remain visible. The fresh holdout changed domains and values while testing a capacity Treemap with visible smallest labels, a truthful rejection of Pie for signed values, a dated Timeline, document-type Class structure, and a deployment Gantt with multiple predecessors.

The baseline failed both holdout attempts for extended Timeline and Treemap and passed only one of two conflicting-Pie attempts. The candidate passed both attempts of every holdout case while retaining the baseline's passing Gantt and Class behavior.

## Promoted changes

- Preserve colorset1 for ordinary color requests and explicit negations of extended styling; use colorset2 only for affirmative extended/full-color language.
- Distinguish canonical routing IDs from Mermaid declarations and synchronize a recognized four-field `decision.json` deterministically.
- Keep XY observations out of category labels, expand parser-incompatible grouped Class assignments, and preserve functional Sankey and Treemap YAML options without duplicate mappings.
- Add family-specific visible Timeline and Treemap palette variables. Give Treemap enough deterministic geometry and contrast for small labels and colorset2 pixels to survive the rendered-output gate.
- Clarify Treemap quoting/value grammar and Gantt status-tag ordering in the conditional selection reference.

No runtime file was added. The candidate modified only `SKILL.md`, `references/diagram-selection.md`, and `scripts/style_mermaid_directory.py`; all animation and renderer resources remained unchanged.

## Durable evidence

- Development Pareto config: `config-final-v6-development-generation-000.yaml`
- Final holdout config: `config-final-v6-holdout-generation-000.yaml`
- Local ignored run archive: `evaluations/runs/mermaid-hardening-20260809-v8/search-output-final-v6/`
- Dataset builder and independent verifier: `evaluations/mermaid/build_harbor_dataset.py`

Infrastructure-only startup failures from earlier exploratory runs were excluded from model scoring. The final development and holdout comparisons completed every expected trial with zero provider or infrastructure errors.

## Post-promotion validation

- Canonical source matched the promoted candidate file-for-file: 14 files / 398,345 bytes. The local `.agents/skills/mermaid` installation then matched all 14 canonical files with no extras or omissions.
- Deterministic XY, Treemap, and Class regression fixtures passed styler write/check idempotence and Mermaid 11.16.0 rendering. XY labels were separated from signed observations, Treemap retained one functional YAML mapping plus `showValues`/`valueFormat`, and grouped Class assignments expanded into valid individual assignments.
- Manual review of a 3,992 x 1,362 Treemap PNG confirmed that every leaf label and value remained inside its rectangle. Independent pixel analysis found four visible colorset2 tokens, 2.9182% palette coverage, and an 80.8678% rendered-pixel difference from the counterfactual palette.
- Strict isolated Pi run `mermaid-hardening-20260810-spark-1` used the repository-required `gpt-5.3-codex-spark` model at medium thinking as an independent generalization check. It created all three exact outputs, selected `treemap` / `treemap-beta` / `colorset2`, preserved every value, had no invalid events or tool errors, kept the copied payload unchanged, and read only the prompt, core instruction, two conditional references, and its generated artifacts.
- Diagram taxonomy validation passed 31/31 Mermaid families and 48 renderable declarations. Pattern IDs, repository skill validation, skill independence, payload, synchronization, Python compilation, and diff checks passed.
- Durable evaluation source was pruned from 109 files to 15. Superseded organized snapshots and exploratory Pareto configs were removed after their decisive metrics were consolidated; final builders, verifiers, protocols, summaries, the disclosure winner config, and all four V6 execution/analysis configs remain.
