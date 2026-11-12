# Evidence-classification repair: naturalistic v1 review

Date: October 25, 2026, America/New_York. Three fresh first attempts use the
frozen 23-file `desktop-plugin-ui` runtime. Preserve previous offerings and
follow-up cohorts separately. No tested output was repaired or rerun.

## Result

| Run | Strict | Final typed checker | Semantic content | Allowed scratch/read scope | Full manual / joint |
| --- | --- | --- | --- | --- | --- |
| 1 | Fail | Pass | Fail: one mixed-basis coverage gap | Fail | Fail / Fail |
| 2 | Pass | Pass | Pass, with scope caveat below | Pass | Pass / Pass |
| 3 | Fail | Pass | Pass, with scope caveat below | Fail | Fail / Fail |
| Total | **1/3** | **3/3** | **2/3** | **1/3** | **1/3 / 1/3** |

The new workflow improves the central classification behavior in all three:
expected policy/schema/runtime-gate refusals are passing checks, source and
documentation records stay nonexecuted, and skipped Copilot Chat acceptance is
untested. However, the frozen joint naturalistic threshold of at least 2/3 is
not met. Execution and scope failures remain failures even after final recovery.

All exact outputs exist, requested fields and false task flags pass, the three
copied skill payloads remain unchanged, and all final typed checkers pass. The
independent numeric/format subset also passes: **28 exact path assertions, 31
explicit binding assertions, 20 independently recomputed ratios and 30
canonical H1-H10 ID/label checks**. These are scoped positives, not acceptance
of failed runs. Across the final two-file checks, 80 official URL checks
and 53 normalized evidence records pass. URL checking deduplicates each URL
within each report; this is not a count of every textual citation occurrence.

## Frozen identities

- Runtime/source/full: 23 files, SHA-256
  `a06c9f918308160272427d8a97f40d19ebfa82db65a7f2ff0a5571406f3a1799`.
- Prompt: `evaluations/pi-prompts/desktop-plugin-ui-evidence-naturalistic.md`,
  raw SHA-256 `ee44ad5752083b38ea153182d63eb31955fb790e8c86969c01ebd42c3134a390`.
- Independent criteria: `evaluations/desktop-plugin-ui/evidence-repair-review-criteria.md`,
  raw SHA-256 `c2ab5be36ad037328dd1cc1011b0fac0f01b32eaf761405309538cdf2c2608d2`.
- Manifest-normalized prompt SHA-256:
  `899e81598d1a99f13df9d5e5212ea69817239e4eb3ec2f275d6c14c696482e6d`.
  The source and copied prompt bytes are 2,217 bytes with 35 CRLF sequences;
  the manifest hashes the 2,182-byte LF-normalized text. Text is identical.
- Model: deliberate existing `openai-codex/gpt-5.6-luna` exception, high
  reasoning, JSON strict mode, 600-second limit. No Claude/Copilot inference.

| Run suffix | Duration | Completed tool calls | Observed Luna records | Retained tool errors |
| --- | --- | --- | --- | --- |
| `1` | 185.653s | 37 | 24 | Two failed reads |
| `2` | 154.873s | 29 | 18 | Zero |
| `3` | 173.405s | 35 | 24 | Three shell/Python errors |

All three `pi` subprocesses exit 0; the strict wrapper correctly rejects runs
1 and 3. All event streams are valid JSON, and model identity matches. Independent
event summaries retain the forbidden-read/tool-error findings. Final artifact
SHA-256 values, prompt/criteria hashes and 23-file integrity checks are retained
per run in `independent-review-identities.json`.

## Execution and path failures

**Run 1:** The model uses `TMP=$(mktemp -d)` and writes facts/ledger outputs in
POSIX `/tmp`. Native read-tool attempts at `/tmp/tmp.axeHTnHEmp/ledger.json`
and `ledger.md` fail; the harness normalizes them to `C:/tmp/...` and records
both forbidden reads and tool errors at event lines 6271/6272. The model copies
the files into its workspace through the shell and recovers final artifacts.
It later issues `rm -rf /tmp/tmp.axeHTnHEmp`. This is an actual outside-workspace
scratch/cleanup route in the command trace, not merely an inaccurate filename
in a report. The physical outside directory was not inspected by the reviewer.

**Run 3:** The model targets
`C:/Users/villa/AppData/Local/Temp/desktop-plugin-ui-forward-test/` for
`facts.json`, generated ledger files, `build_json.py` and a pretty JSON output.
The trace includes successful outside writes and an outside ledger read.
The first script fails with an unterminated heredoc/string; later scripts fail
on Python `true` and `false` literals before recovery. The three error events
are 3777, 18742 and 18881; the forbidden ledger read is event 6943.
The reviewer neither reads nor deletes any files in that outside directory.

**Run 2:** Uses workspace-relative `work/` scratch, the typed helper, final
artifacts and final checking without errors. Its cleanup targets that relative
workspace directory. No prohibited host, account, installation, browser or
additional provider action occurs. The trace preserves the user's choice to
skip Copilot sign-in.

These are local execution/isolation failures, distinct from the corrected
classification rules. A portable system temporary directory is still outside
the permitted evaluation workspace. The final artifacts and copied bundle do
not erase that scope violation. Scratch advice needs to stay within the task's
allowed workspace, without a cleanup dependency on outside paths.

## Independent semantic review

All six final artifacts were inspected. Recommendations cover the requested
queue actions, usable text fallbacks, Copilot terminal controls, ordinary
webviews, optional inline MCP Apps and conditional canvases. They separate
ordinary webview CSP/script configuration from MCP App metadata. They offer
conditional stock Codex resource delivery and do not impose an owned-frontend
requirement. Selection/draft/business/preferences have realistic owners and
reload/reconnect/failure plans. Explain and CSV scopes, preserved identifiers,
English copy and host-owned styling boundaries are present.

Source inspection derives `documented`, not an observed runtime request.
Expected `never` policy decline and bare-SDK confirmation rejection derive
`observed-working` with named expectations/actual results. Unperformed
Copilot Chat and stock-front-end checks derive `untested`. User-reported
no-sign-in state is not promoted to authenticated readiness. No current task
claims renderer construction, real host acceptance or a user study.

**Run 1 retains one mixed-basis coverage error.** Its
`canvas-paint-unrun` record is correctly based on `not-run`, but its `reason`
says “canvases:true was observed in negotiation.” That is a separate executed
capability observation, without a matching execution record. The record for
the bare SDK consumer describes all renderer flags false, so it cannot stand
in for the terminal connection's true canvas flag. This is a scope/basis
coverage gap under the frozen criteria, not a hidden row-count or ID rule.

**Stock Codex wording is a caution, not an automatic exclusion failure.**
All three use broad “stock paint was not tested” wording. For example, run 2's
record says “Stock Codex desktop and IDE widget or form paint was not established
by the bundled checks,” while its offering limits transport evidence to the
0.145.0 app-server route, explicitly recommends an optional negotiated component
and requires separate deployment validation. The bundle also includes bounded
historical desktop chart painting. The broad sentence should be narrowed to
the particular backend/proposed-workflow acceptance, but the complete
recommendation does not assert that all historical chart paint failed, that
stock UI is impossible, or that only an owned frontend can supply it. This
wording alone is not used to reject an otherwise valid run.

The same context rule avoids requiring inclusion of every unused historical
fact: a proposal can select relevant evidence. Used facts must still have
appropriate scoped support. A complete negative-test description can group
related checks sharing one host/layer; no hidden minimum record count is used.

## Helper use, exact values and report consistency

Each trace actually calls `evidence_ledger.py`, copies normalized records into
JSON, includes the helper table, and runs typed-mode `check_reports.py` after
both exact output files are written. The reviewer independently repeats the
two-file typed check with `--fail-on-findings`. Original files remain unchanged.

Run 1 has 17 records/26 URL checks; run 2 has 19/22; run 3 has 17/32. All IDs
resolve and required derived fields pass. The helper's scope limitation remains:
it cannot establish the truth of a supplied execution or find omitted claims.

The independent project reviewer parses the frozen palette hex leaves without
calling the bundled resolver for its expected values, and recomputes relative
luminance/contrast independently with 1e-9 tolerance. All 20 explicit ratios
match. Authored focus uses dark red, not sole gray focus; ordinary critical
text uses dark ink, with red limited to redundant accents. Actual helper use
for token/contrast claims appears in every trace. H1-H10 labels and concrete
interaction checks are correct in all three.

An initial evaluator byte-exact table probe reports run 2 false because it
removed only the helper's escaped underscores (`design\_values`,
`primary\_hover`, `reported\_result`). Diff review finds identical claim,
basis, scope, label and result content. The reviewer accepts this formatting
equivalence rather than inventing a byte-for-byte output requirement. Initial
`independent-content-check-byte-exact-v0.json` receipts are retained; the final
subset checker records literal and underscore-equivalent matches separately.
No tested artifact was changed and no semantic requirement was relaxed.

The project reviewer is
`projects/desktop-plugin-ui/scripts/review-evidence-naturalistic.py`. It writes
only ignored per-run evaluation receipts. It checks structural/numeric subsets;
the manual evidence/path review above remains necessary.

## Read surface and retained evidence

The first completed read is `../prompt.md` in every run. Subsequent bundle reads
are the relevant skill, host/pattern/report/design references and, in runs 2/3,
the palette source; runs 1/3 also inspect script implementations. Run 1 broadly
reads native/host-prompt references while comparing mechanisms. No large gallery,
acceptance example, repository document or sibling skill is read. No file above
50 KB is a normal source read. Generated outputs and ledgers are task artifacts;
the forbidden scratch paths are explicitly rejected as described above.

Raw evidence lives under
`evaluations/runs/20261025-desktop-ui-evidence-naturalistic-v1-luna-{1,2,3}/`:
manifests, JSONL events, stdout/stderr, all strict gate reports, independent
event/content receipts, identity receipts and the unchanged final artifacts.
No outside temporary directory is examined or cleaned during this review.

## Reproduction

From the repository root, substitute `N` with 1, 2 or 3 when reading commands;
those exact retained run IDs must not be reused for another attempt:

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-evidence-naturalistic.md --run-id 20261025-desktop-ui-evidence-naturalistic-v1-luna-N --model openai-codex/gpt-5.6-luna --mode json --strict --expect-output offerings/recommendation.md --expect-output offerings/recommendation.json --expect-output-json-field offerings/recommendation.json::host_acceptance_verified=false --expect-output-json-field offerings/recommendation.json::task_empirical_tests_performed=false --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261025-desktop-ui-evidence-naturalistic-v1-luna-N/events.jsonl --output evaluations/runs/20261025-desktop-ui-evidence-naturalistic-v1-luna-N/independent-event-summary.json --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error --require-read ../prompt.md --forbid-read-regex '(?i)(^|[\/])assets[\/]examples([\/]|$)' --forbid-read-regex '(?i)^skills[\/](?!desktop-plugin-ui([\/]|$))' --forbid-read-regex '(?i)^(?:[A-Za-z]:[\/]|/|\\)'
uv run --script projects/desktop-plugin-ui/scripts/review-evidence-naturalistic.py --prefix 20261025-desktop-ui-evidence-naturalistic-v1-luna
```

This cohort clears no broader release or live-host gate. It consumes only
OpenAI forward-test inference, preserves no-Copilot-sign-in steering, and
changes no canonical skill, backlog, account or original evaluation output.
