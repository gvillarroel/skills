# Assistant plugin UI host separation

Date: November 11, 2026 (America/New_York). Raw runs cross into November 12 UTC.

Six independent host bundles now own their runtime guidance and resources. The original `desktop-plugin-ui` is a cross-host comparison/blueprint entrypoint. Historical references, source work and evidence remain available. All seven backlog records remain `validating`: this split does not establish every signed-in frontend, deployment route, or full generation reliability.

## Bundles and scope

| Skill | Files | Core lines | Runtime bytes |
| --- | ---: | ---: | ---: |
| `desktop-chat-plugin-ui` | 9 | 30 | 45960 |
| `code-native-plugin-ui` | 13 | 30 | 46787 |
| `pi-extension-ui` | 11 | 31 | 50107 |
| `codex-plugin-ui` | 10 | 31 | 51892 |
| `chatgpt-desktop-plugin-ui` | 10 | 31 | 51766 |
| `gemini-enterprise-ui` | 11 | 36 | 51050 |
| `desktop-plugin-ui` | 40 | 75 | 297161 |

All new bundles have their own palettes and design helper. Native Claude retains the tested starter; Pi retains the guarded intent primitive, a command starter, and version probe. Gemini has an original v0.9 panel and bounded checker. Shared runtime helpers/templates were checked byte-for-byte against the original source. Required bundle links and resources stay inside each bundle; no sibling skill is required.

Claude-qualified directory names use `desktop-chat-plugin-ui` and `code-native-plugin-ui` because the existing repository authoring validator reserves `claude` and `anthropic` in skill names. Display names and descriptions identify the actual hosts. No validator was weakened.

## Deterministic and independent checks

- Repository pattern IDs, bundle validation, independence tests, and payload checks pass. Local sync/check validates source-owned installation parity.
- Existing source checker: 81/81; design values: 16/16; version probe: 17/17. Google primary-source ownership and lookalike rejection were also checked. Only exact bundled/allowed URLs are accepted.
- New bounded A2UI checker: 12/12 unit/CLI tests. The starter and three generated streams pass actual upstream envelope and host component schemas. The envelope's relative catalog slot is bound to the official host component union; theme-property semantics are explicitly excluded by that adapter. This is not host paint or A2A transport acceptance.
- Copied Claude starter: strict manifest validation and 13/13 authentic native tests on Claude Code 2.1.302. Three corrected-source generated Claude plugins also pass independent strict validation/native engines.
- Pi starter: 16/16 real Pi 1.4.0 RPC/JSON-print assertions, including discovery, selection, cancel, invalid recovery, direct arguments and zero model turns. Three generated Pi artifacts pass an independent direct JSON-print/no-inference check; RPC test sources/transcripts were reviewed separately.
- Generated MCP packages were independently initialized over stdio, discovered, called for useful text/structured results, and read for actual linked HTML/MIME resources. Portable Codex/ChatGPT manifests were checked against both official schemas using their declared runtime entries. These checks do not establish frontend painting.
- The first generated Desktop Chat app also passes an independently rerun protocol test. Its actual sandbox bridge tests and wide/narrow success/error screenshots were reviewed: readable labels, visible recovery, retained filters and no overflow. These are browser fixture results, not Claude Desktop acceptance.
- Metadata-only routing: 11/11, including eight positive surface requests and three exclusions. No skill was forced and no body was provided. This does not measure automatic product discovery.

## Isolated forward runs

Spark was attempted first and rejected by the ChatGPT account with zero reported usage. The recorded per-run exception uses `openai-codex/gpt-6.1-sol`, medium thinking. Every normal run uses the runtime-only copied bundle, disabled ambient discovery, strict JSON/model/error/output/integrity gates, and exact expected output paths. The copied skill stays read-only.

54 Sol evaluations completed; 38 passed every strict harness gate. Failures are retained. Counts below use the initial run plus two fresh repetitions, including pre-repair failures; they are not a filtered best-of table.

| Skill | Final contract | Naturalistic strict / 3 | Boundary/generalization strict / 3 |
| --- | --- | ---: | ---: |
| `desktop-chat-plugin-ui` | Pass | 0/3 | 3/3 |
| `code-native-plugin-ui` | Pass | 2/3 | 3/3 |
| `pi-extension-ui` | Pass | 2/3 | 3/3 |
| `codex-plugin-ui` | Pass | 0/3 | 3/3 |
| `chatgpt-desktop-plugin-ui` | Pass | 0/3 | 3/3 |
| `gemini-enterprise-ui` | Pass | 3/3 | 3/3 |
| `desktop-plugin-ui` | Pass | 3/3 | 2/3 |

Additional corrected-source diagnostics are separate from that matrix: native Claude `sol-recovery`, `repeat-2`, and `repeat-3` are all strict/independent passes. Pi `sol-recovery` retained a wrong test assertion about disposition; after promoting the exact JSON response into its reference, `repeat-2` and `repeat-3` passed strictly. Earlier outside-workspace host-doc reads remain failed isolation results.

Failure classification and repairs:

- Harness: two original contract prompts used a fence the exact-command parser did not recognize. Corrected bash fences and standalone-command wording passed in fresh workspaces; original failures remain.
- Agent/isolation: initial Pi reads used installed documentation outside the allowed workspace. Explicit source isolation was clarified; later runs used only supplied guidance and normal executables.
- Skill/agent: an added native render guard assumed an absent plugin event field. The host reference now distinguishes mount fixtures from real render events. Corrected-source generated plugins passed three strict runs and independent native checks.
- Skill/agent: Pi's compact reference lacked the exact handled-prompt response. It now names `response.data.disposition === "handled"` and `response.data.commands`; the two subsequent runs passed strictly.
- Agent/tooling: web runs retained exploratory commands with nonzero exits, dependency/peer-resolution or audit failures, browser setup/fixture issues, and a TypeScript check failure. Final artifacts can work while strict history remains failed; a repaired artifact does not erase a tool error.
- Runtime budget: ChatGPT Desktop `repeat-2` reached the 600-second timeout. Its expected artifacts exist and its declared package later passes independent stdio/schema checks, but completed event gates are absent and the run remains a strict failure. The trace summarizer now explicitly records this case rather than inventing missing gate results.
- Evaluator: an initial independent ChatGPT probe started the editable root server instead of the declared bundled entry. Its failure is preserved; the unchanged package passes after the evaluator reads `mcp.json`. An initial Pi starter verifier also read disposition at the wrong level; the corrected evaluator passes 16/16. A first official-schema probe tried to fetch the envelope's catalog placeholder; binding the actual host catalog fixed the evaluator and was promoted into the Gemini reference.

## Reproduction and retained evidence

Prompts are versioned under `evaluations/pi-prompts/host-split-*.md`; the precise case/output manifest is `projects/plugin-ui-host-split/evaluation-cases.json`. Run controls and independent validators live in that project's `scripts/`. Bulky workspaces, JSONL, packages, schemas, logs and images remain ignored under `evaluations/runs/20261111-host-split-*` and `projects/plugin-ui-host-split/artifacts/`.

Representative contract:

```powershell
uv run --script scripts/run-pi-skill-eval.py gemini-enterprise-ui --prompt-file evaluations/pi-prompts/host-split-gemini-enterprise-ui-contract.md --mode json --strict --require-exact-command-from-prompt --model openai-codex/gpt-6.1-sol --thinking medium --expect-output deliverables/design.json --expect-output deliverables/route.md
```

Exact run commands and required paths are retained in each run manifest. `summarize_evaluations.py` applies `summarize-pi-json-events.py --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error` to every completed trace and separately checks requested artifact schemas. Full per-run results and final source digests are in [the durable record](host-split-20261111.json).

Required repository gates:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
```

Skill-specific commands:

```powershell
python skills/gemini-enterprise-ui/scripts/test_check_a2ui.py
python projects/desktop-plugin-ui/scripts/test-source-checker.py
python projects/desktop-plugin-ui/scripts/test-design-values.py
python projects/desktop-plugin-ui/scripts/test-runtime-probe.py
node projects/plugin-ui-host-split/scripts/verify_pi_starter.ts
uv run --script projects/plugin-ui-host-split/scripts/verify_generated_native.py
```

For official catalog and MCP package checks, use `validate_a2ui_catalog.py <stream.json> --label <run-label>` and `verify_mcp_package.py <package-dir> --label <run-label>`. Keep the chosen input run and output label distinct to preserve evidence.

## Remaining acceptance

Current work does not install into personal accounts, alter approval policy, deploy cloud services, register Gemini agents, or publish GitHub changes. Actual Claude Desktop Chat/Code, Pi TUI or custom RPC-client paint, stock Codex desktop/IDE rendering, ChatGPT Desktop local UI, and Gemini Enterprise signed-in A2A/action/paint checks remain separately scoped. Existing historical observations are retained in host references and are not promoted to current acceptance. Broader release repetition and generation reliability still need work for the failing routes.

Primary Gemini sources reviewed: [registration](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/register-and-manage-an-a2ui-agent), [component catalog](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/a2ui-component-gallery-reference), [hosting](https://docs.cloud.google.com/gemini/enterprise/docs/a2ui-agents/tutorial-host-agent-cloud-run), and [A2A compatibility](https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-a2a-agent). The documented host route is A2UI v0.8/v0.9 over version-compatible A2A; a newer upstream version does not establish host support.
