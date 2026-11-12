# Plugin authoring metadata routing control

- Date: October 25, 2026.
- Skill: `desktop-plugin-ui`; case type: metadata-only routing control.
- Run: `20261025-plugin-build-routing-sol-1`; one attempt, no rerolls.
- Runtime: Pi 1.4.0, Windows; requested and observed model
  `openai-codex/gpt-6.1-sol`, thinking `high`.
- Model exception: use the existing Sol exception recorded in `SKILLS.md`.
  The parent rechecked Spark provider rejection before tools for this revision;
  this control is Sol evidence, not Spark evidence.
- Outcome: **Pass, 10/10 decisions**, with passing exact-output and trace gates.
- Failure classification: none.

The [runner](plugin-build-routing-control.py) reads only the YAML frontmatter
from the current source skill, then supplies it in the
[versioned prompt](plugin-build-routing-prompt.md). No skill body or runtime
bundle is copied, loaded or forced. The evaluator's expected decisions are
frozen in `EXPECTED` and written to the run's `acceptance.json` before Pi starts;
they are not supplied to the agent. The fresh workspace contains no skill.

## Commands and isolation

```powershell
uv run --script evaluations/desktop-plugin-ui/plugin-build-routing-control.py
```

The runner refuses to reuse the run workspace. It resolves the installed Pi
launcher through the repository harness and runs from
`evaluations/runs/20261025-plugin-build-routing-sol-1/workspace`:

```powershell
pi --model openai-codex/gpt-6.1-sol --thinking high --mode json --no-context-files --no-extensions --no-skills --no-prompt-templates --no-themes --no-session --no-mcp --print "Use the read tool to read ../prompt.md first, then follow that task. No skill body is loaded."
```

Independent trace summary:

```powershell
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-plugin-build-routing-sol-1/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error --require-tool-call --require-read ../prompt.md --forbid-read-regex '^(?!\.\./prompt\.md$).+' --output evaluations/runs/20261025-plugin-build-routing-sol-1/read-surface.json
```

## Frozen expectations and observed decisions

| Case | Expected use | Observed use | Result |
| --- | --- | --- | --- |
| `claude-desktop-build` | true | true | Pass |
| `chatgpt-desktop-build` | true | true | Pass |
| `codex-build` | true | true | Pass |
| `pi-extension-build` | true | true | Pass |
| `claude-code-build` | true | true | Pass |
| `plugin-host-compatibility` | true | true | Pass |
| `plugin-nielsen-review` | true | true | Pass |
| `generic-website` | false | false | Pass |
| `general-nielsen-review` | false | false | Pass |
| `api-pricing` | false | false | Pass |

The independent grader requires exactly the ten ordered IDs, JSON booleans,
nonempty reasons, no extra fields, the exact nonempty artifact
`results/routing.json`, and no extra workspace files. Direct inspection confirms
the reasons distinguish assistant plugin/extension work from unrelated website,
mobile-app heuristic review and API-pricing work.

## Trace, identity and limits

- Pi exit code `0`; sole observed provider/model `openai-codex/gpt-6.1-sol`.
- Agent tools: one `read` of `../prompt.md`, then one `write` of
  `results/routing.json`; no shell, browser or other tool call.
- Invalid JSON lines, invalid event records and tool errors: all `0`.
- Metadata SHA-256:
  `42bdce890653147e66a96c94fe5c442504fd37482d13ab5f34a581dbad98d873`.
- Output SHA-256:
  `a4172b3263cd9474f3309c951a5d5f2e813efabd8da3fa5463014862d81eea43`.
- Trace-reported usage: 6,300 total tokens including cache accounting.
- Raw prompt, frozen acceptance map, command, manifest, JSONL events, stderr,
  artifact, independent grading and trace summaries remain under the ignored
  run directory. No host installation or global configuration change was made.

This is a controlled decision task using only metadata. It does not establish
automatic skill selection in any product, skill-body execution quality, plugin
installation, host UI painting, user satisfaction or a universal model pass.
The harness imports repository code outside the tested agent's read surface;
the agent itself reads only the prompt.
