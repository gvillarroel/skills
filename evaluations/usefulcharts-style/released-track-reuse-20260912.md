# Reuse of a terminated branch while sibling tracks continue

Date: 2026-09-12, America/New_York. Skill remains `validating` for the broader
reference-density and composition requirements.

The user's additional requirement is implemented in the canonical bundle:
`reuse_tracks: true` places all measured fragments in a shared track pool, with
their group and physical-owner identities retained. A short branch can release
its horizontal suffix to another family even while a sibling branch continues.
This differs from the previously supported compaction of whole family envelopes.

The mode requires `labels_in_footprints: true` and rejects separate rectangular
group-heading reservations. The renderer must make family identity local and
must not connect unrelated neighbors into a false lineage. Complete occupied
footprints, including labels, artwork and clearance, determine release time;
the date endpoint alone does not. See the
[runtime contract](../../skills/usefulcharts-style/references/shared-time-rows.md).

## Deterministic evidence

```powershell
uv run --script skills/usefulcharts-style/scripts/test_shared_rows.py
```

All eight tests pass. Three added cases cover reuse while a long sibling remains
active, rejection of missing local identity or separate headings, and clearance
at an exact boundary. Existing fixed-x, owner, source-copy, whole-family reuse,
title-envelope and malformed-input tests continue to pass.

## Isolated forward evidence

Three fresh runs use Pi 0.84.2, `openai-codex/gpt-5.3-codex-spark`, high reasoning,
strict JSON mode and a runtime-only copied bundle. The exact required paths are
`deliverables/layout.json` and `deliverables/review.md`. The six synthetic
fragments belong to five physical spacecraft. The long survey branch stays
active while the short survey branch's track passes to freight and then science.

```powershell
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-released-track-forward.md --mode json --strict --run-id 20260912-usefulcharts-released-track-1 --expect-output deliverables/layout.json --expect-output deliverables/review.md
uv run --script evaluations/contracts/check-usefulcharts-released-track.py evaluations/runs/20260912-usefulcharts-released-track-1/workspace
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20260912-usefulcharts-released-track-1/events.jsonl --require-model gpt-5.3-codex-spark --fail-on-invalid-json --fail-on-tool-error
```

The same commands were run with fresh IDs ending in `-2` and `-3`.
All three pass strict execution, independent input/owner/coordinate comparison,
actual shared-track handoffs and manual workspace/prose review. The independent
checker imports no skill implementation. All raw traces and copied bundles remain
under the three run directories; no failed run was discarded.

All three runs use the same 120-file runtime SHA-256:
`ee5ae0766063a948f0bc8e5f8b17fcdfed59604d0ad49de53e8cf2c58920210c`.
Every copied skill remains unchanged. Runs 1 and 2 read the entry point and
shared-row guide; run 3 also reads the compact data contract. The read surface
contains no fixture, sibling skill or project artifact. Manual inspection of
every shell command found no write outside its isolated workspace.

Run 1's prose explains the cross-family handoff less clearly than runs 2 and 3,
although its table and output explicitly place survey, freight and science on
the same track. All three distinguish fragments from physical owners and leave
visual identity, label-to-date association and reference parity for real rendering.

This is narrow layout evidence. It does not validate the full research,
image-generation or poster-composition workflow, and it does not establish
UsefulCharts parity. The separate
[Star Trek application review](starships-flow-edition-20260912.md) retains that
distinction and its unresolved composition findings.

Repository pattern IDs, skill structure, independence, payload and whitespace
checks pass. Local installation synchronization is part of the handoff. No
published example or Pages catalog changed in this revision.
