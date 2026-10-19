# Pi Durable source and metadata routing review

Date: 2026-10-19. Review mode: independent read-only inspection of the skill source;
only evaluation evidence was authored. No skill source was modified during this
review, and no native service was installed or registered.

## Source findings

No blocking source or routing issue was found in the reviewed surface.

- `SKILL.md` describes an embedded durable application runtime, named agents,
  event admission, saved task chat and Windows/macOS per-user supervision. Its
  opening instruction explicitly routes ordinary interactive Pi Coding Agent work
  to that product rather than this application-building workflow.
- `agents/openai.yaml` uses the name Pi Durable, an event-agent/chat short
  description, and a default prompt invoking `$pi-durable` for PR services and
  reconnectable chat on both desktop platforms. The metadata is aligned with the
  body and template; it does not imply automatic integration with another
  product's task sidebar.
- The skill's routing table points to six focused references, each below roughly
  10 KB. The scaffolder resolves assets from its own bundle and refuses generation
  inside that bundle. Normal operation does not require sibling skills or
  repository-level documentation.
- Runtime-only payloads can omit `assets/examples/`. Both the main instructions
  and operation/lifecycle references condition fixture testing on availability;
  normal use proceeds through build, plan inspection and local offline smoke.
- CLI service plans pass target-platform path overrides directly to the portable
  planner. macOS cross-plans require POSIX absolute paths, a home directory and
  UID. Dry-run is the default; foreign-platform native execution is rejected.
- Version guidance consistently pins the executable starter to 1.3.0, marks
  `sleepUntil`, `wake`, `retryTask` and crash-loop controls as unavailable there,
  and assigns idle waiting to ordinary host event/timer code.
- Event and console guidance distinguishes delivery, logical job, Pi input and
  external effect identities. It describes atomic conversation mapping, stable
  request IDs, one storage owner, authenticated loopback clients, and explicit
  platform/provider validation limits.

This was a targeted source/read-surface review, not a fresh exhaustive audit of
all provider and storage implementation internals.

## Completed isolated trace surfaces inspected

The completed contract trace at
`evaluations/runs/20261019-pi-durable-contract-luna-1/event-check.json` reported
18 tool calls with no errors. It read the prompt, `SKILL.md`, and the compatibility,
template-operations and service-lifecycle references. Remaining reads were its
generated package, configuration and plan. It invoked the scaffolder without
reading the complete template source. No acceptance-fixture or sibling reads
appeared.

The completed generalization trace at
`evaluations/runs/20261019-pi-durable-generalization-luna-1/event-check.json`
reported 11 calls with no errors. It read the prompt, `SKILL.md`, and five compact
references relevant to the broader event-adapter, runtime, console and platform
task. It did not read the GitHub fixture/gallery, acceptance examples, or sibling
skills. Commands queried the host platform and validated its generated JSON and
operations file. No source mutation or native registration was observed in those
traces. Their strict harness and independent artifact acceptance remain the
parent evaluator's separate release gates.

## Metadata-only routing smoke

The durable [prompt](metadata-routing-prompt.md) supplies only the exact skill
name and description plus ten requests. It contains no expected case labels.
The fresh Pi runtime disabled context files, extensions, skill discovery, prompt
templates, themes, tools and session persistence. There was no `--skill` argument
and the model could not read the skill body, references or templates.

Command, from the raw run directory:

```text
pi --model openai-codex/gpt-5.6-luna --thinking low --mode json --print --no-session --no-tools --no-context-files --no-extensions --no-skills --no-prompt-templates --no-themes --offline @prompt.md
```

Observed model: `openai-codex/gpt-5.6-luna`, using the already recorded Spark
account/provider exception. This introduces no new release-test model exception.
The run produced valid event JSON, zero tool calls, zero tool errors and 1,507
reported total tokens. The output was independently parsed and compared against
the ten intended labels.

| Request | Expected | Observed |
| --- | --- | --- |
| PR service on Windows/macOS | yes | yes |
| Real pet recommendation | no | no |
| Embedding the durable host runtime | yes | yes |
| One-time static PR review | no | no |
| Named registry and saved task chat | yes | yes |
| Durable Raspberry Pi protective case | no | no |
| Pi Durable 1.3.0 wake compatibility | yes | yes |
| Generic cron/SMTP email notifier | no | no |
| Local CI event agent service | yes | yes |
| Ordinary Pi Coding Agent terminal | no | no |

Result: **10/10 routing labels match**, including all five positive and all five
negative controls. The compact [machine-readable result](metadata-routing-result.json)
retains justifications, exact command, hashes and limitations. Raw final evidence
is under `evaluations/runs/pi-durable-metadata-routing-20261019-2/`, including
`events.jsonl`, `stderr.txt`, `prompt.md`, `command.txt` and `event-check.json`.

An earlier trial under `evaluations/runs/pi-durable-metadata-routing-20261019/`
is retained but superseded: its schema example included the first case's expected
classification. The final prompt uses neutral placeholders and was rerun in a
fresh runtime. No skill metadata was changed in response to either trial.

This is one bounded metadata routing smoke, not a task-effectiveness benchmark,
an estimate of model quality, or a claim of measured production selection rates.
The requests make their intent explicit; adversarial ambiguity and multilingual
routing were not evaluated. Native macOS activation, login recovery and real
provider/GitHub integrations remain distinct validation work.
