# Desktop plugin UI: evaluation plan and existing evidence

Researched 2026-10-24. This note is evaluator-owned project material, not a
runtime dependency. No model execution, credential access, account installation,
global package installation, or changes to prior adapters were performed.

## Release methodology

The canonical procedure is `evaluations/README.md`. For this new knowledge and
decision skill, use one contract case, three fresh naturalistic repetitions,
three fresh generalization repetitions, and one boundary case. This is eight
runs on one frozen payload. Require contract 1/1, naturalistic at least 2/3,
generalization at least 2/3, and boundary 1/1. Keep every unsuccessful attempt.
Do not count a protocol-fixture result as signed-in host acceptance.

1. Static gates: pattern IDs, skill metadata/links, independence, payload, and
   the evaluation harness tests.
2. Deterministic bundle checks: unique pattern IDs, at least ten patterns,
   complete rule/evidence fields, bounded reference sizes and valid local links.
3. Strict isolated runtime tests with exact outputs.
4. Evaluator-owned artifact grading, independently of the model's self-report.
5. Trace/read-surface and unchanged-payload review.
6. Record frozen hashes, all runs, commands, dates, observed model and grading
   in `evaluations/<skill>/validation-20261024.md`; link it from `SKILLS.md`.

Keep status `validating` until applicable gates and cohort thresholds pass.
Routing metadata testing is a separate unforced control; the normal helper
always loads one specified skill and therefore cannot prove automatic routing.

## Available harness and model policy

Observed read-only commands:

```powershell
Get-Command pi,uv
pi --version
pi --help
pi --offline --no-context-files --no-extensions --no-skills --no-prompt-templates --no-themes --list-models spark
pi --offline --no-context-files --no-extensions --no-skills --no-prompt-templates --no-themes --list-models gpt-5.6
```

Pi is installed at `C:/Users/villa/AppData/Roaming/npm/pi.ps1`, version **1.4.0**.
`uv` is available. The offline Spark search lists only unrelated OpenRouter
Muse Spark models, not the required Codex Spark. The catalog does list
`openai-codex/gpt-5.6-luna`, `gpt-5.6-sol`, and `gpt-5.6-terra`.
Catalog absence does not itself prove a fresh provider rejection.

The repository default remains `openai-codex/gpt-5.3-codex-spark`.
Attempt and retain the mandated model first. If it is rejected before tools,
classify that as infrastructure and document a deliberate model exception in
the new skill's `SKILLS.md` row before substituting an available model. Nearby
`reflex-xy` and `pi-durable` work records a Sol exception after Spark rejection;
`xerj` uses Luna. These are precedents, not an automatic global policy change.
Do not weaken strict gates. The helper checks the requested model, so strict
mode works with an explicitly recorded exception. Pass that actual model to
the separate trace summarizer as well.

The helper already supplies `--no-context-files --no-extensions --no-skills
--no-prompt-templates --no-themes --no-session` and `--skill skills/<skill>`.
It copies the runtime bundle, excludes `assets/examples/`, records hashes,
forces first read `../prompt.md`, checks exact outputs and verifies unchanged
skill resources. Its shell tool is Bash; test prompts should avoid PowerShell.

## Suggested cases

Each versioned prompt must name exact workspace-relative output paths, state
that `skills/<skill>/` is read-only, and prohibit unnecessary network use or
external changes for these closed-book tests. Supply all scenario inputs in
the prompt. Ask for a Markdown recommendation and small machine-readable JSON
decision record, rather than an actual installed desktop plugin.

| Case | User-like request and outputs | Independent acceptance |
| --- | --- | --- |
| Contract smoke, 1 run | Explain a supplied ordinary Claude Desktop chart plugin scenario; create `results/contract.md` and `results/contract.json`, with host, surface, transport, selected pattern IDs, constraints, evidence levels, validation plan. | Exact paths; schema; at least ten distinct bundled patterns with actionable rules and evidence; ordinary Desktop MCP Apps distinguished from Code Mods and ChatGPT; no actual-host claim. |
| Naturalistic forward, 3 runs | A team needs a local desktop inventory tool: table, filters, detail form, export, responsive states, retry, and optional fullscreen. Recommend the plugin/UI approach in `proposal/ui.md` and `proposal/decision.json`. | Selects a real intended host/surface; resolves ordinary chat versus Code; maps controls to suitable patterns; capability-gates optional fullscreen/download; preserves data and last successful state; verifies keyboard, narrow viewport, content paint and host boundary. |
| Generalization, 3 runs | A support workflow targets both Claude Desktop chat and ChatGPT with a shared interactive ticket queue and optional native Claude Code pane. Produce `handoff/cross-host.md` and `handoff/matrix.json`. | Shared MCP Apps core with host-specific deployment/auth/domain handling; local stdio versus reachable HTTPS; Mods treated separately; sensible routing and fallbacks; no static API-key or universally supported SDK-method claim; evidence confidence and dated recheck plan. |
| Boundary/recovery, 1 run | The requester calls the app only "Cloud Desktop", asks to load arbitrary HTML into a native Mod, use `file:` links in Desktop Link, hide an initialized chart frame with `display:none`, and treat a fixture pass as production acceptance. Write `review/boundaries.md` and `review/status.json`. | Acknowledges ambiguous host name; states conditional paths or asks one focused host question without fabricating a Cloud Desktop product/API; classifies incompatible surfaces and tested failures precisely; proposes corrected patterns; honest evidence levels and practical validation. |

For the boundary case, do not reveal all desired corrections in the prompt.
Present the requested behaviors as the user's proposed plan and ask for a
review. The evaluator contract can contain the expected distinctions above.

For direct information work, grade whether rules are specific, bounded,
evidence-backed and useful; do not demand application code absent a user
request. Avoid a simplistic string count as the only grader: a confident wrong
host recommendation can contain every keyword.

## Exact release commands

Replace `<skill>` with the final skill directory name and use actual prompt
filenames. Commands are shown in PowerShell for the evaluator; these are not
instructions to the isolated agent's Bash tool.

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py

uv run --script scripts/run-pi-skill-eval.py <skill> --prompt-file evaluations/pi-prompts/<skill>-contract.md --mode json --strict --run-id 20261024-<skill>-contract-spark-1 --expect-output results/contract.md --expect-output results/contract.json

uv run --script scripts/run-pi-skill-eval.py <skill> --prompt-file evaluations/pi-prompts/<skill>-naturalistic.md --mode json --strict --run-id 20261024-<skill>-naturalistic-spark-1 --expect-output proposal/ui.md --expect-output proposal/decision.json

uv run --script scripts/run-pi-skill-eval.py <skill> --prompt-file evaluations/pi-prompts/<skill>-generalization.md --mode json --strict --run-id 20261024-<skill>-generalization-spark-1 --expect-output handoff/cross-host.md --expect-output handoff/matrix.json

uv run --script scripts/run-pi-skill-eval.py <skill> --prompt-file evaluations/pi-prompts/<skill>-boundary.md --mode json --strict --run-id 20261024-<skill>-boundary-spark-1 --expect-output review/boundaries.md --expect-output review/status.json

uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/read-surface.json --require-model gpt-5.3-codex-spark --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\\/])assets[\\/]examples([\\/]|$)' --forbid-read-regex '(?i)^skills[\\/](?!<skill>([\\/]|$))'

uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
```

Repeat naturalistic and generalization commands with fresh `-2` and `-3` run
IDs. Add `--model openai-codex/gpt-5.6-sol` or the documented alternative only
after recording the exception, and change run labels/summarizer model to match.
Do not use `--require-exact-command-from-prompt` for these open-ended tasks.
Only add `--expect-output-json-field` for stable objective decisions explicitly
required by the prompt.

`sync-local-skills.py` refreshes the ignored installation from canonical
`skills/`, preserves extra local files and checks both source and destination.
Its interface is `--source`, `--destination`, `--check`; it has no `--skill`.
All writes remain inside the authorized repository root by default.

Publishing an informational skill without a public example does not require a
Pages gallery. If adding an example gallery, use the owning `assets/examples/`,
register its stable set ID in `PUBLISHED_EXAMPLE_SETS`, build Pages and run
validators; published pattern publication additionally requires commit, push
and verified deployment under the repository's normal authorization rules.

## Reusable prior evidence: surfaces and known boundaries

The repository already has substantial local evidence checked on 2026-10-24.
Copy compact reusable findings into the new skill; do not point its runtime at
these project paths. Recheck primary-source URLs for new platform claims.

| Finding | Evidence strength and reusable rule |
| --- | --- |
| Ordinary Claude Desktop chat uses a local stdio MCP server with an MCP Apps resource; `.mcpb` is the installable extension package. | Official guides and real packaged stdio/schema acceptance; signed-in Desktop installation/paint remains unverified. Do not confuse packaging with the UI protocol. |
| Desktop Code tab and VS Code use native Claude Code Mods; terminal is a different native surface. | Official Mods docs, native scanner/test kit and portable tests. Cloud/headless execution lacks the same pane surface. |
| Native `Svg` is for Desktop/VS Code; terminal uses `Image`; mobile has fewer elements. | Native/portable tests inspect supported element trees. Capability-check and provide text/image fallbacks; do not promise identical controls everywhere. |
| Native Mods are not arbitrary browser DOM/HTML and run without Node APIs. | Official Mods API. Use host primitives for panes and explicit `process.run` argument arrays for external rendering. |
| Desktop `Link` rejects `file:`. | Observed native test failure. Use explicit Open buttons with fixed OS-opener argv or Copy path; do not OS-open executable source by association. |
| Clipboard uses `ui.copy({text})`. | Observed native test failure/correction. Keep visible path fallback and catch unavailable clipboard behavior. |
| ChatGPT MCP Apps needs reachable HTTPS for remote MCP and separate UI/download asset routes in this adapter. | Official OpenAI sources and real HTTP tests. Local protocol success is not reachability from the account. A private MCP tunnel does not automatically proxy arbitrary artifact routes. |
| Local stdio Claude MCP Apps must omit `ui.domain`; remote host rules differ. | Official Claude troubleshooting and shipped manifest checks. Do not reuse a ChatGPT domain blindly. |
| Portable MCP Apps should use the bridge and capability-negotiated host methods. | Official SDK/protocol host fixture. Do not assume `window.openai`, fullscreen or file-download capability is universally present. |
| Download can use host `ui/download-file` with host open-link fallback. | Independent real-service browser fixture, two capability variants. This proves fallback implementation, not every host version. |
| Own-origin HTML iframe embedding needs host CSP/frame allowlists. | Official OpenAI iframe policy plus resource/CSP tests. Public submission can require justification/review; local fixture success is not submission approval. |
| Static API key configuration is not a ChatGPT OAuth substitute. | Official OpenAI authentication docs. No-auth is only appropriate to intended public/non-sensitive demo data; private deployment needs supported OAuth. |
| Initialize nested charts only after layout exists; hiding a live frame with `display:none` caused intermittent blank/underfilled charts. | Retained independent browser failures in progressive-controls report. Keep inactive frame laid out, visually hidden/inert, and verify actual canvas paint at narrow and wide sizes. |
| Toggling native chart chrome by navigation lost view state. | Retained product correction. A parent-only fixed Boolean message changes preview CSS without navigation; original exported HTML stays intact. |
| State must be per session and retain previous good data after failure. | Native tests and real-service browser checks. Clear session state at end, keep current successful data as palette/edit target and label sample replacement. |
| Advanced controls fit one disclosure area with accessible native controls. | NN/g and W3C sources plus fixture keyboard/target checks. The project's maximum initial-action count and 44px target choice are local rules, not measured universal UX laws. |
| Native hook tests, MCP protocol tests, browser host fixtures and actual installed-host acceptance are distinct evidence layers. | Explicit limitations in every release note. Name the measured layer and keep unknown platform/client behavior unknown. |

## Source inventory

- `docs/reflex-xy-plugins.md`: concise three-host matrix, install/transport/auth
  distinctions, current adapter limits and commands.
- `projects/reflex-xy-plugins/notes/claude-sources.md`: primary Claude URLs,
  exact-host native corrections, local MCPB/stdio/domain contract.
- `projects/reflex-xy-plugins/notes/chatgpt-sources.md`: primary OpenAI URLs,
  portable bridge, current plugin flow, CSP/auth and tested SDK compatibility.
- `projects/reflex-xy-plugins/notes/interaction-sources.md`: NN/g/W3C sources
  and precise distinction between design rationale and measured behavior.
- `evaluations/reflex-xy/plugins-20261024.md`: retained release failures,
  protocol/renderer/native/browser/package acceptance and limits.
- `evaluations/reflex-xy/progressive-controls-20261024.md`: latest 0.2.0
  acceptance, frame lifecycle failures, strict scoped Pi evidence and hashes.
- `projects/reflex-xy-plugins/claude/tests/native.test.ts`: actual host-engine
  element dispatch, clipboard, successful-state and native UI contracts.
- `projects/reflex-xy-plugins/chatgpt/tests/browser.ts` and `boundaries.test.ts`:
  real service with official bridge, declared fixture capability variants,
  frame CSP, expiry and artifact path controls.

Primary URLs already recorded in those notes include:

- https://code.claude.com/docs/en/plugins/mods/reference
- https://code.claude.com/docs/en/plugins/mods/api
- https://code.claude.com/docs/en/plugins/mods/test
- https://claude.com/docs/connectors/building/mcp-apps/getting-started
- https://claude.com/docs/connectors/building/mcp-apps/troubleshooting#ui-domain-validation-fails
- https://developers.openai.com/plugins/build/chatgpt-ui
- https://developers.openai.com/plugins/build/app-quickstart
- https://developers.openai.com/plugins/reference
- https://developers.openai.com/plugins/build/auth
- https://developers.openai.com/plugins/plugin-guidelines#iframes-and-embedded-pages

Existing skills are mostly implementation workflows rather than lightweight
informational catalogs. `reflex-xy` demonstrates conditional compact-reference
routing, dated API baselines and explicit host boundaries. Use those structural
ideas without copying its chart-specific requirements.
