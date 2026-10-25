# Pi Durable subagent and evolution templates — 2026-10-25

## Subject and scope

Canonical skill: `skills/pi-durable`. Pi Durable remains pinned at 1.3.0;
Node 24+, Windows 11, Python 3.13.12, uv 0.10.12 and installed Pi 1.4.0 were
used. Real generated agents select `openai-codex/gpt-6.1-sol`. The isolated
authoring cohort retains the previously documented Spark-unavailable exception,
`openai-codex/gpt-5.6-sol`, with thinking `low`.

| Frozen subject | Files | SHA-256 |
|---|---:|---|
| Initial runtime cohort | 81 | `f38af1f75f291bd5f559de738893c511f0a65f74c7027a403402aee95e3eebf7` |
| Runbook runtime cohort | 81 | `3e7cacb5265b007a32c99a3d1226373458e8d9494eb894e7192e5b27128a7db4` |
| Runbook full bundle with relocation acceptance | 97 | `05aa2afb9ed4d3c856f215c95f20a3f7f922ecee51695669a19953fcb73dd6b1` |
| Final runtime with configured author-prompt correction | 81 | `b8686c9fefe16d9572a1cd20f848f6fdf34bb90d8b33135192aacc351846d25e` |
| Final full bundle, including acceptance sources | 97 | `5fe3195fa3bee8ed62a56ec54b17d24bda9d0a1889a2297ace638216e1d2cb62` |

Hashes use the repository harness's `snapshot_tree` / `snapshot_digest` contract.
Runtime excludes `assets/examples/`; full includes acceptance sources. The final
runbook change adds complete study preparation commands to generated `AGENTS.md`.
The relocation-test enhancement changes only the full acceptance payload. Final
review found that a protected-code filename check also matched the role name
`author`; exact configured prompts now bypass that code-only name check while
management/security code remains protected. A real request regression covers it.

## Local source research

Read the user's documentation outside this repository without modifying it:

- `knowledge/docs/knowledge-skill-evolution-playbook.md`, especially strategies
  A–E and trace-to-Pareto, lines 344–475.
- `knowledge/docs/knowledge-skill-evolution-roadmap.md`, explicit mutation surfaces,
  bounds and frozen finalist rules.
- `knowledge/docs/retrieval-profile-evolution.md`.
- `skill-arena/skills/harbor-{trace-distillation,reflective-pareto-search,population-search,operator-coevolution,metaskill-evolution}/`.
- `skill-arena/skills/harbor-organize-evaluations/references/development-memory.md`.
- `blog/presentations/harnesses-skills-context-alternate-hour/templates/evolution-release-record.md`.
- `zx-harness/skills/zx-workflow-author/references/evolution.md` and ADRs 0050/0051.

Adapted knowledge lives inside the generated bundle; source repositories are not
runtime dependencies. The implementation provides local trace/population/Pareto
controllers. It does not claim to run Harbor, GEPA, trained operator coevolution
or automatic metaskill optimization. Operator attribution is development-only
input for a separately frozen next study.

## Delivered behavior and direct validation

- `scaffold.py --profile supervisor|map-reduce|review-refine` emits complete
  independent projects. `scaffold-evolution.py --strategy
  trace-distillation|population|pareto --profile ...` composes both capabilities.
  All four base profiles pass generation, refusal and fresh-hash checks; all
  three evolution strategies have exact initial manifests.
- Native foreground `delegate_tasks` supports parallel joins and dependent
  pipelines. Children get fresh contexts and an exact read/evidence allowlist
  without recursive delegation. One durable charge/create transaction enforces
  total child limits across calls; replay reuses owner-index children and stable
  inputs. The three-stage pipeline carries draft plus review within one shared
  prior-text budget. Recovered-child evidence reports stored model/prompt choices.
- The final generated service builds and passes **88/88 native tests**, including
  nine subagent tests, configuration scope/versioning, cancellation, interrupted
  SQLite recovery, source promotion/rollback and the expanded relocation case.
- The relocated project contains evolution plans and its optional Codex example.
  From an unrelated caller it builds, runs event smoke, renders a native plan,
  invokes evolution/study help and runs the compiled subagent smoke. Every copied
  authored byte remains unchanged. Ordinary installed dependencies are reused;
  no original skill is present in the moved application.
- Offline subagent smoke rejects network access and runs two parallel children
  plus three pipeline children: nine faux calls, stable duplicate inputs, SQLite
  reopen with no additional calls. Event smoke retains duplicate-event and chat
  recovery behavior with zero reopen calls.
- **8/8 evolution unit tests** cover seals, generation, path bounds, finite Pareto
  vectors, tied complementary candidates, exclusive lock contention and cleanup.
  The real CLI integration passes **11/11 checks**: paired development
  `0.75 → 1.0`, independent validation `0.75 → 1.0`, holdout `0.6 → 1.0`, exact
  finalist reuse, no activation, rejected duplicate/closed/failed gates and a
  live development process preventing concurrent selection. Study model calls: 0.

Representative commands, from the repository root unless a project cwd is named:

```text
uv run --script skills/pi-durable/scripts/test-scaffold-profiles.py
uv run --script skills/pi-durable/scripts/test-evolution-templates.py --output projects/pi-durable-templates/artifacts/final-template-unit
uv run --script skills/pi-durable/scripts/scaffold-evolution.py projects/pi-durable-templates/artifacts/final-release --strategy pareto --profile review-refine --with-tests
```

The fresh `final-release` project passes `npm run build`, `npm test`, `npm run
smoke` and `npm run subagents:smoke`. The final lock integration used:

```text
uv run --script projects/pi-durable-lab/artifacts/evolution-study-lock-v2/tests/evolution-study.integration.py --project projects/pi-durable-lab/artifacts/evolution-study-lock-v2
```

Its controller SHA-256 is
`5c404206e307b73e1f50ffe01922c083cbcc0da99e11acb0deec14124e016cd8`.
The acceptance fixture remains bundled for reproduction with a fresh project.

## Actual Sol 6.1 integration

A separate tiny live task used the existing read-only Codex bridge and
`gpt-6.1-sol` for the coordinator and both specialists. Two explicit facts were
delegated once in parallel. Both children settled, and the coordinator returned
the correct synthesis: four model responses/provider calls in total. No GitHub
request, posting, source activation or native registration was performed.

Local result: `projects/pi-durable-templates/artifacts/live-sol61-result.json`.
This is an integration probe, not a review-quality benchmark. The probe used an
earlier equivalent runtime before the stored-child profile-reporting correction;
that correction has separate native recovery coverage. Its durable ledger
confirmed `runtime.closed`; the already-completed owned probe process retained
provider resources and was explicitly stopped after checking its exact PID and
command. Functional completion does not imply normal one-shot process exit.

## Isolated forward cohorts and retained failures

Prompts: [contract](../pi-prompts/pi-durable-templates-contract.md) and
[naturalistic](../pi-prompts/pi-durable-templates-naturalistic.md).
Independent evaluator: [artifact contract](../contracts/pi-durable-templates.py).

Each run uses the runtime profile, no ambient context/extensions/other skills,
JSON strict mode, prompt-first read, exact nine output paths and immutable skill
hashes. Run prefixes are `pi-durable-templates-20261025`,
`pi-durable-templates-v2-20261025` and `pi-durable-templates-v3-20261025`, with
suffixes `contract`, `natural-1`, `natural-2`, `natural-3` under ignored
`evaluations/runs/`.

| Cohort | Strict | Independent artifacts | Manual result |
|---|---:|---:|---|
| Initial contract | 1/1 | 1/1 | 0/1: incomplete curator preparation and misleading study `--input` recipe |
| Initial naturalistic | 3/3 | 3/3 | 3/3 generation/selection/limits |
| Runbook contract | 1/1 | 1/1 | 1/1, complete gate preparation and release commands |
| Runbook naturalistic | 2/3 | 3/3 | 3/3 artifacts and guidance; one retained strict tool error |
| Final configured-prompt contract | 1/1 | 1/1 | 1/1 complete generation and operations guidance |
| Final configured-prompt naturalistic | 3/3 | 3/3 | 3/3 complete artifacts, selection, release and limits |

The runbook naturalistic failure first invoked project-local study help from the
workspace root, then corrected cwd. Keep that attempt as an agent command error,
not a pass. The required two-of-three naturalistic threshold is satisfied.
After the independently discovered configured-author-prompt correction, the final
subject receives its own fresh contract and three naturalistic repetitions.
All four pass strict/artifact/manual checks; no earlier cohort passes are pooled.
The independent validator initially required the unrelated word `operator` in
notes; corrected that hidden requirement to finalist selection/next-study scope.
The initial contract's substantive manual failure remains a failure despite its
structural pass. The generated runbook was corrected, then a fresh cohort ran.

All final read surfaces use only the prompt, skill entry/routed compact references
and relevant generated project files. No acceptance gallery, sibling skill,
external source repository or credential read was needed. Successful traces have
valid JSON, the declared model, no tool errors and unchanged runtime payloads.

Other retained observations: one intermediate 87-test run had a transient local
HTTP fixture network error in unsafe-pagination testing; its focused 25-test file
passed. Closing ephemeral fixture connections explicitly prevents pooled socket
reuse across rapidly recycled ports; final full suite passes 88/88. The first
study-lock integration made a Windows launcher/interpreter PID assumption; the
corrected fixture observes and awaits the same live process and verifies lock
cleanup. Neither failure was silently discarded or counted as a final pass.

## Release boundaries

Repository pattern-ID, skill, independence and payload gates pass. Local skill
sync preserves additional installed files; verify canonical Pi bundle hashes after
sync. Keep overall backlog status `validating`: earlier installer strict 0/1 and
broader service-authoring naturalistic 0/3 remain historical evidence. This new
cohort establishes the requested templates, not all historical trigger surfaces.

Synthetic cases are visible mechanics tests. Real quality improvement, semantic
family transfer, private curator isolation, all-provider token/cost caps and
native macOS launch remain separate work. Native 1.3.0 hooks do not enforce a
model-call cap by throwing; only the documented child/attempt/generation/text/
host-wait bounds are claimed. The low-level explicit promoter remains available;
operators must preserve final-gate policy and drain/stop/build/smoke/rollback.
