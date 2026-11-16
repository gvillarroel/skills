# Website screenshot tours: November 16, 2026

## Scope

Line World Video 0.25.0 adds a bounded screenshot-tour builder and renderer.
Inputs are actual source captures, explicit source-pixel crops and control
boxes, adjacent guide ports, narration files and measured local cue times.
The renderer preserves the screenshot pixels, uses one parent clock, routes
the guide around annotated controls, keeps a stable scale within each scene
and blends scene joins. It does not automate a website or invent its UI.

The Reddit walkthrough uses actual signed-out browser screenshots. Navigation
covered public search, communities, rules, a thread, comment controls and the
account dialog. No votes, joins, posts, comments, credentials or account
creation were submitted. Spanish narration uses Microsoft Edge speech through
edge-tts, with provider word boundaries and measured MP3 extents. This is a
local MP4, not a Google Vids export; the earlier native upload restriction
remains unresolved.

## Utility and installed-package checks

Commands:

```powershell
uv run --script skills/line-world-video/scripts/test_website_video.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

Seven new utility tests pass. They exercise invalid crops and clipped controls,
blank captures and escaping paths, cue ordering, measured audio overflow,
actual multi-scene encoding and decoding, exact frame counts, full and partial
cache reuse, changed capture rejection and a blocked guide route. A changed
first scene invalidates its own clip and the dependent next-scene blend while
reusing the independent third clip.

The actual 0.25.0 ZIP extraction, task-local native installation and
app-server discovery pass with all six plugin-qualified skills. All 22
installed utility suites pass. The package contains 344 payload files,
including 152 primary-skill files and 22 Google Vids adapter files. Native
discovery has zero model turns and does not establish desktop UI activation.

## Isolated agent runs

All runs use the recorded model exception
`openai-codex/gpt-6.1-sol --thinking medium`; Spark remains unavailable.
The runtime-only bundle is copied into an isolated workspace, ambient context
is disabled, the copied payload stays unchanged and all exact output paths
are required. Prompts are
[the contract](../pi-prompts/line-world-website-tour-contract.md) and
[the natural task](../pi-prompts/line-world-website-tour-natural.md).

| Run ID | Result | Seconds | Payload qualification |
| --- | --- | --- | --- |
| `20261116-website-tour-contract-sol` | Strict pass | 82.837 | Candidate before the producer contract's six-line website clarification |
| `20261116-website-tour-natural-1-sol` | Strict pass | 132.851 | Same candidate |
| `20261116-website-tour-natural-2-sol` | Strict pass | 129.566 | Same candidate |
| `20261116-website-tour-natural-3-sol` | Strict pass | 168.563 | Same candidate |
| `20261116-website-tour-final-contract-sol` | Strict pass | 79.642 | 0.25.0 packaged primary payload |
| `20261116-website-tour-light-contract-sol` | Strict pass | 69.745 | Final 0.25.1 light-theme payload |

The contract traces read the skill, visual direction, rendering, timing and the
website-tour reference. It does not read acceptance examples, sibling skills
or repository instructions. The helper produces an actual six-second MP4;
the agent inspects its poster and encoded frames. These are synthetic UI
fixtures, not live website captures. The earlier three natural runs support
the unchanged renderer but are not described as exact final-payload runs.

Final strict command:

```powershell
uv run --script scripts/run-pi-skill-eval.py line-world-video --prompt-file evaluations/pi-prompts/line-world-website-tour-contract.md --mode json --strict --model openai-codex/gpt-6.1-sol --thinking medium --run-id 20261116-website-tour-light-contract-sol --expect-output film/story.json --expect-output film/index.html --expect-output film/preview.html --expect-output film/tour.json --expect-output film/final.mp4 --expect-output film/review.json --expect-output film/poster.png --expect-output review.md
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261116-website-tour-light-contract-sol/events.jsonl --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
```

## Limits

The subsequent 0.25.1 revision requires native light UI captures. The real
Reddit source was recaptured after selecting Display Mode > Light. A new
regression test rejects declared dark themes and predominantly dark neutral
UI regions while preserving the exact rejected image bytes; all eight
website utility tests pass. This heuristic does not certify a site setting
and is separate from the composition color guidelines. The final light-theme
payload passes strict validation in `20261116-website-tour-light-contract-sol`
in 69.745 seconds. The actual 0.25.1 extracted package also passes all six
native skill discoveries and all 22 installed utility suites. The earlier
contract and natural runs above remain evidence for their own candidate bytes.

The helper audits annotated controls and source containment; it cannot infer
the purpose of every unannotated pixel or prove speech pronunciation. Actual
captures, content selection, visual balance, target identification and
editorial review remain necessary. Narration caches preserve voice bytes
when only crops or timing change. Frame caches include the runtime, renderer,
capture bytes and preceding scene dependency. Google Vids account permission
and native export are separate from a successful local encode. Keep the
primary skill `validating` under the earlier generality limits.

All required repository validators pass in the selected clean publication
worktree. In the dirty authoring workspace, full validation and global sync
still report four pre-existing unrelated reference-route findings in the
semantic-model/ontology skills. The scoped Line World validator passes and
the scoped local sync verifies 152 primary and 22 adapter files. No unrelated
skill changes are included in the publication.

The final native-light Reddit encode is 104.866667 seconds, 3146 frames at
30 fps, 1920 by 1080 with H.264/AAC. Full decoding and all-frame content scan
pass with zero insufficient-content frames. Manual inspection covers all nine
encoded scene contact sheets, cue reading poses and joins; 137 encoded samples
pass and the exact-movie visual review is recorded. Provider word boundaries
and measured extents supply the speech alignment; independent audio listening
is not claimed. Movie SHA-256:
`1fe07d040ab505a1accc8be1232aaa0f71439d80a4b6c0f1a0df1d7127e5bcc3`.
