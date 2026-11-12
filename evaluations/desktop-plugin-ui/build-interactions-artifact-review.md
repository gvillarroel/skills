# Plugin authoring and interaction artifact review

Date: October 25, 2026. Independent evaluator review against
[criteria frozen before implementation review](build-interactions-review-criteria.md).
The evaluator prepared the prompts from the pre-revision skill and user task,
then reviewed completed forward artifacts only after each harness wrote its
`evaluation-result.json`. No forward artifact or copied skill was repaired.
Evaluator output is confined to each completed workspace's `evaluator-review/`.

## V1 subject and methods

Observed forward model: `openai-codex/gpt-6.1-sol`, medium, strict JSON runtime
profile. This is the explicitly recorded per-run model exception; it is not
Spark evidence. Frozen runtime subject: 26 files, SHA-256
`2eed59901630cd5c552e248c1e719ae53a2624365f0a1252f40a867dfb3cdefb`.
Raw workspaces use `evaluations/runs/20261025-plugin-build-<case>-sol-<rep>/`.
Consult their manifests for prompt hashes, commands, outputs, environment and
strict read-surface/model/integrity checks.

Final evaluator script SHA-256:
`a5e339059321736372c1801781b4a0c882c885b71b68b84904203a046a7895a0`.

Executable artifact validation runs the actual TypeScript initializer and
registered handler through evaluator-owned API stubs in a constrained VM.
Node 24.18.0 type stripping erases type-only imports. Checks exercise all
three filter choices, exact row membership and field values, cancellation,
headless output and recovery, and forbidden model/network/process/persistent
actions. Agent-authored check assertions cannot establish behavioral success.
JSON structure and false live-paint/user-study claims are independently checked.

Commands, run from the repository root:

```powershell
node projects/desktop-plugin-ui/scripts/test-build-interactions-verifier.ts
node projects/desktop-plugin-ui/scripts/verify-build-interactions.ts evaluations/runs/20261025-plugin-build-contract-sol-1/workspace contract
node projects/desktop-plugin-ui/scripts/verify-build-interactions.ts evaluations/runs/20261025-plugin-build-naturalistic-sol-1/workspace naturalistic
node projects/desktop-plugin-ui/scripts/verify-build-interactions.ts evaluations/runs/20261025-plugin-build-naturalistic-sol-2/workspace naturalistic
node projects/desktop-plugin-ui/scripts/verify-build-interactions.ts evaluations/runs/20261025-plugin-build-naturalistic-sol-3/workspace naturalistic
```

The verifier selftest passes **8/8**: valid contract/naturalistic fixtures are
accepted; implicit cancel default, ignored filter, wrong priority, headless
notification no-op, unexpected model turn and wrong release state are rejected.
Ignored generated fixtures/results live under
`projects/desktop-plugin-ui/artifacts/verifier-selftest/`.

## V1 completed outcomes

| Run suffix | Strict harness | Independent artifact checks | Semantic review | Joint outcome |
| --- | --- | --- | --- | --- |
| contract-sol-1 | pass | 34/34 | pass | pass |
| naturalistic-sol-1 | pass | 33/33 | pass | pass |
| naturalistic-sol-2 | pass | 33/33 | pass | pass |
| naturalistic-sol-3 | pass | 33/33 after retained evaluator correction | pass | pass |
| boundary-sol-1 | pass | direct document/JSON review | pass | pass |
| generalization-sol-1 | fail: 360-second timeout | both artifacts present; JSON parses | pass on existing documents | fail |
| generalization-sol-2 | fail: 360-second timeout | both artifacts present; JSON parses | pass on existing documents | fail |
| generalization-sol-3 | pass | both artifacts present; JSON parses; 11 palette bindings resolve | pass | pass |

V1 totals: **6/8 joint**, **8/8 semantic artifact review**. Family outcomes are
contract 1/1, naturalistic 3/3, boundary 1/1 and generalization 1/3 jointly.
The generalization threshold of at least 2/3 is **not met**. The two strict
timeouts remain failures despite the favorable document review.

Contract review: a single native selector correctly returns all, pending or
high-priority rows, including closed/high `T-106`. Undefined cancellation
returns without acceptance, shortcuts validate inputs, and the no-UI branch
emits all rows and recovery instructions using `triggerTurn:false`. The design
counts one initial selector, one required decision, one primary acceptance and
zero added processes. H1-H10 findings are concrete and distinguish handler
checks from real terminal behavior. The reviewer independently checked
`pi --help`: the proposed Bash trial's `--offline`, `--no-session`, `--no-mcp`,
`-e`, `--no-extensions`, context/template/theme-discovery flags exist. The
reviewer did not run the loader, TUI or a provider.

All three naturalistic artifacts correctly return ready checks `R-21/R-23`,
blocked check `R-22`, or all checks. Each cancellation is distinct from
acceptance, and each no-UI path supplies correct rows and deterministic
command recovery. There is no runtime import, added service, custom renderer,
provider call or extension-owned persistent state. H1-H10 findings, host-owned
styling and complexity counts are supported by the artifacts. Repetitions 2
and 3 add a 30-second native selection timeout; it exits safely, but whether
that timeout benefits this read-only task needs real user/host evaluation.
Native notification lifetime and readability also remain pending.

Boundary review: the recommendation preserves task success using direct
foreground text prompts, with an optional existing form only after exact
frontend negotiation and visible-control checks. It neither fabricates a
stock-CLI sidebar API nor converts absent paint evidence into a product
exclusion. It preserves draft values, validates and revalidates a literal
folder path, separates blank/decline/cancel/EOF from acceptance, and avoids
an extra frontend, persistent service, host setting or provider call. Missing
business option names/types/defaults are explicitly unresolved instead of
invented. All H1-H10 checks and the future acceptance sequence are concrete.
Both live acceptance and user-study flags remain false.

Generalization repetitions 1 and 2 reached their 360-second budget and were
terminated. Repetition 1 records `returnCode:124`, `timedOut:true` and total
harness duration 373.091 seconds. Both artifacts exist and the JSON parses.
The existing documents cover seven
separate adapters/files/transports, pure shared domain logic, opt-in Explain,
truthful Codex orchestration-turn budgets, draft and authoritative commit
ownership, revision/idempotency checks, complexity tradeoffs, H1-H10 and
keyboard/narrow-layout acceptance. Host/user flags are false. This favorable
document review cannot recover the strict timeout: the attempt is retained
as a joint failure. Its timestamped trace shows the second artifact completed
359.72 seconds after harness start; the final bash consistency check completed
at 367.81 seconds and final assistant/agent-settled events followed. This
supports a verification/generation time-budget overrun, not a demonstrated long
hang after agent settlement. Repetition 2 records the same timeout code with
442.903 seconds total harness duration. Repetition 3 completed strictly in
350.277 seconds. All three plans cover the stated semantic contract;
repetition 3's eleven exact palette token paths and values were independently
resolved with `design_values.py` and match the bundled asset. No higher-layer
UI acceptance is inferred.

## V2 scoped revision

After the V1 timeouts, the author changed only `SKILL.md` and
`references/plugin-authoring.md` to emphasize compact multi-host blueprints:
write shared interaction/Nielsen contracts once, keep adapters terse, use JSON
for precise contracts and Markdown for decisions, and read deeper catalogs
only for unresolved questions. A blueprint is distinguished from a formal
capability/evidence study. Prompts, thresholds, model/effort and 360-second
budget remain unchanged. V1 is retained as a separate frozen subject.

The new subject receives a fresh contract smoke plus three generalization
attempts under `evaluations/runs/20261025-plugin-build-v2-<case>-sol-<rep>/`.
This is a scoped revision/regression cohort. Naturalistic and boundary V1
results remain historical; they cannot establish an eight-case pass on V2.
All V2 outcomes below received independent review after completion.

V2 frozen runtime subject: 26 files, SHA-256
`ed3f7529ae344b2bf9c29dbb73c2e3a787c99ed1ce39bca769dc747588fb66d7`.

| V2 run suffix | Strict harness | Independent artifact checks | Semantic review | Joint outcome |
| --- | --- | --- | --- | --- |
| contract-sol-1 | fail: two tool errors | 34/34 | pass | fail |
| generalization-sol-1 | pass: 347.579 seconds | seven complete host contracts; JSON parses | pass | pass |
| generalization-sol-2 | fail: timeout, 387.485 seconds total | seven complete host contracts; JSON parses | pass on existing documents | fail |
| generalization-sol-3 | pass: 359.904 seconds | seven complete host contracts; JSON parses | pass | pass |

V2 scoped totals: **2/4 joint**, **4/4 semantic artifact review**. The
generalization family meets its unchanged **2/3 joint** threshold; contract
smoke is **0/1 joint**, despite **34/34 independent behavior checks**. This
does not establish a complete V2 release pass. All requested host plans are
semantically covered, with real-host acceptance and representative-user
usability still unverified.

The V2 contract extension passes the same independent filter, value,
cancellation, no-UI and deterministic-action checks. Its review is concrete
about Nielsen, complexity, host ownership and pending paint. The strict
event gate nevertheless retains two errors: `command -v tsc` returned 1 in
an optional availability probe, and the first inline test fixture had a
missing closing brace. The agent corrected its fixture and recorded 12/12
local checks; correction does not erase the strict errors. Classification:
`agent` workflow/tool errors, with no independently observed extension defect.

Independent contract command:

```powershell
node projects/desktop-plugin-ui/scripts/verify-build-interactions.ts evaluations/runs/20261025-plugin-build-v2-contract-sol-1/workspace contract
```

All three V2 multi-host plans distinguish the seven required surfaces and
provide their actual mechanisms, files, shared/adapter logic, conditions,
fallback and local validation. They preserve immutable inputs, separate
drafts from reviewed snapshots and authoritative receipts, reject invalid or
stale commits, retain inputs during correction/cancel/error, and make model
explanation explicit-only. They distinguish direct operations from Codex
model orchestration, with text/local-command fallback and honest model
budgets. H1-H10 findings name concrete interactions, planned checks and their
evidence limits. Complexity counts have defined counting rules and explain
tradeoffs rather than claiming measured user improvements. Styling separates
authored iframe tokens from host-owned/native paint, preserves accessibility
overrides and leaves actual keyboard/narrow/host tests pending. Both flags
remain false in every plan. V2 repetition 2's favorable document review does
not recover its strict timeout, which remains a separate failed attempt.

### Descriptive generalization output/read metrics

The byte total counts only the two required blueprint artifacts. The read
count is the number of unique target-bundle paths visible in `read` tool
records, including `SKILL.md`, excluding the task prompt and generated files.
These counts are descriptive; they neither count all possible indirect shell
reads nor prove a causal improvement from the compactness instruction.

| Subject / repetition | Required output bytes | Unique observed read-tool bundle files | Strict outcome |
| --- | ---: | ---: | --- |
| V1 / 1 | 58,782 | 16 | timeout |
| V1 / 2 | 68,725 | 15 | timeout |
| V1 / 3 | 55,818 | 15 | pass |
| V2 / 1 | 54,405 | 13 | pass |
| V2 / 2 | 54,749 | 13 | timeout |
| V2 / 3 | 52,608 | 13 | pass |

V1 output total is 183,325 bytes; V2 total is 161,762 bytes. The two subjects
and all failures remain separate; a smaller output or narrower read surface
does not itself certify quality, efficiency, host support or user satisfaction.

## Retained evaluator correction

The first validator application to naturalistic repetition 3 produced 32/33:
its recovery regex demanded a literal `interactive`, `TUI` or `terminal`
keyword. The naturalistic prompt asks for a useful no-UI summary and recovery;
the actual fallback includes all rows plus the actionable
`/release-checks [all|ready|blocked]` syntax and selection/key guidance.
The missing keyword was an evaluator overconstraint, not a demonstrated
artifact defect. The stricter explicit interactive-route requirement belongs
to the contract prompt, which requests it.

The original result is retained as
`evaluations/runs/20261025-plugin-build-naturalistic-sol-3/workspace/evaluator-review/build-interactions-validator-v1.json`.
The evaluator was corrected to honor each prompt's stated contract, its 8/8
positive/negative selftests reran, and the same unchanged contract plus three
naturalistic artifacts were rechecked. No model rerun or skill revision was
used to obtain the corrected 34/34 and 33/33 results. Failure classification:
`validator`.

## Limits

VM/stub execution does not prove native Pi painting, real SDK type checking,
loader/RPC/print integration, terminal accessibility, host-wide inference or
network counts, or representative-user usability. Unsupported runtime imports
would require evaluator review rather than an invented host exclusion. Manual
review supplements checks for English copy, Nielsen evidence, complexity
tradeoffs, source scope and runnable-host instructions. These scoped outcomes
do not close earlier broader skill failures or live-host gaps.
