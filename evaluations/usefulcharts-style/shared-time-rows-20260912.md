# Shared calendar rows: skill update and isolated validation

Date: 2026-09-12. Skill status remains `validating` because the broader density
census, thematic planning reliability and reference parity gates remain open.

## Reusable change

[The runtime guide](../../skills/usefulcharts-style/references/shared-time-rows.md)
now specifies one numeric x mapping, complete measured footprints, local y-track
reuse, disjoint family pockets, independent same-owner state fragments, readable
group headings and separate physical/fragment counts. The helper
`scripts/pack_shared_rows.py` preserves all supplied fixed x coordinates and
retains a deep copy of the input. It assigns only y positions in numeric mode.
Schematic sequence mode is explicitly excluded from time-axis requests.

The skill entry point contains a focused measured-layout-only route, followed
by the full composition route. The early stopping point avoids treating a
measured box-placement request as an entire research and drawing task.

Five deterministic tests pass: exact x preservation/track reuse; unchanged source
and same-owner fragments; disjoint family reuse; title-envelope reservation; and
malformed or incomplete input rejection. The final Star Trek application
independently verifies twenty multi-vessel tracks, up to four vessels per track,
and three different family groups reusing one vertical band.

## Evaluation contract

All isolated runs use Pi, `openai-codex/gpt-5.3-codex-spark`, runtime payload,
strict JSON mode, fresh workspaces, disabled ambient context and two exact outputs:
`deliverables/layout.json` and `deliverables/review.md`. The copied skill is read-only.
The naturalistic task is a synthetic museum fleet layout, not the Star Trek
acceptance fixture. It supplies five measured fragments for four physical ships
and requires both within-family and between-family reuse at fixed x positions.

Prompts:
[command control](../pi-prompts/usefulcharts-shared-time-contract.md) and
[naturalistic request](../pi-prompts/usefulcharts-shared-time-forward.md).
The evaluator-owned
[artifact checker](../contracts/check-usefulcharts-shared-time.py) independently
checks dimensions, y clearances, complete owner identities, family-heading
envelopes, track reuse and shared family bands. It does not import the helper.

```powershell
uv run --script skills/usefulcharts-style/scripts/test_shared_rows.py
uv run --script scripts/run-pi-skill-eval.py usefulcharts-style --prompt-file evaluations/pi-prompts/usefulcharts-shared-time-forward.md --mode json --strict --run-id 20260912-usefulcharts-shared-time-forward-b-1 --expect-output deliverables/layout.json --expect-output deliverables/review.md
```

Repeat with fresh `-b-2` and `-b-3` run IDs. The command case uses its matching
prompt and `--require-exact-command-from-prompt`. All retained runs are enumerated
in [the compact result](shared-time-rows-summary-20260912.json), including failures.

## Outcomes and failure classifications

- Initial command control: correct artifacts and helper execution; strict gate
  failed because the evaluator wrote an inline command instead of a fenced
  command. This was an evaluation-definition error. Corrected control B passed.
- Naturalistic cohort A: strict execution 2/3, complete measured-layout acceptance
  0/3. Run 1 read the guide and used the helper but made three tool errors; run 2
  hand-authored valid boxes while skipping the requested helper; run 3 omitted
  physical-owner data. These are agent procedure/output failures. The successful
  shell status did not make the final artifact acceptable.
- After promoting the focused measured-layout route, cohort B passes 3/3 strict
  execution and 3/3 independent geometry/identity checks. Complete acceptance is
  2/3: manual shell review found that B2 redirected two JSON-formatting checks to
  `/tmp/`, outside its requested workspace. The harness's read-policy gate did
  not catch these shell writes. The geometry is correct, but this workflow fails
  the workspace boundary. All three read only
  the prompt, skill and focused reference plus their own task files, executed
  the helper, retained owner identity, and avoided tool errors. The copied
  payloads remained unchanged.
- Final-payload command control C passed strict execution but changed beta's x1
  from 320 to 240 while transcribing the supplied input. Independent grading
  rejected it. This failure is retained; it demonstrates why source comparison
  is required in addition to helper success.
- Fresh command control D, using the same final payload and prompt, passes strict
  execution and independent source/geometry checks. Both the failed C and passed D
  remain in the summary; one success does not erase transcription variability.

The final runtime contains 120 files, SHA-256
`07a619b7356ab46c80a5901a1c8e1fd2ef898c606b05f3f804ddcd5df57a1136`.
The three cohort-B prose reviews were read directly; they preserve the physical
identity distinction, explain reuse and leave visual review pending. No visual
artifact was requested in this measured-layout case.

The bounded forward result validates measured temporal compaction, not research,
image generation, aesthetic similarity or the complete knowledge-density floor.
The final application selects compact printed information; its full viewer
records do not inflate the poster's measured density.

Repository pattern IDs, skill structure, independence, payload, local skill sync
and relevant script tests are part of the handoff. No published example source
or Pages catalog changed, so no Pages publication is claimed.

Final handoff checks pass: 1,222 canonical pattern IDs, repository structure,
skill independence, payload limits and whitespace validation. Local synchronization
copied four changed files; a subsequent targeted check matches all 137 canonical
source files. Final read-surface summaries for B1, B2, B3 and control D confirm
the observed Spark model, valid JSON and zero tool errors; the independent manual
boundary rejection of B2 remains separate from that machine pass.
