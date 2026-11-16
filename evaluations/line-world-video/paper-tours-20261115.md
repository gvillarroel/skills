# Original-paper walkthrough validation

## Native delivery follow-up

After the user reported that the voice-only Vids draft and local file link did
not meet the delivery need, the six reviewed clips were inserted into their
matching native scenes through the supported UI. The scene inventory confirms
one matching video object and the retained original voice per scene, with
durations 35.067, 29.500, 32.100, 32.000, 39.932 and 39.299 seconds as displayed
by Vids. No permissions were changed. The native file-picker route used the
visible Open dialog and keyboard focus of File name; cached owned-dialog AX
indices were not reliable.

The completed Vids project is
`https://docs.google.com/videos/d/1xE-nlSa3WwpO0CggajlAYQA09OnymGae2ch7l2DcpPA/edit`.
The native Export to Drive result is
`https://drive.google.com/file/d/14QqiYhYFqT1bLxN9ZgWlJYJdIKJmp02-/view`.
Actual Drive playback and its enabled download control were observed; metadata
readback confirms `video/mp4`, 17,119,832 bytes. The complete native download is
`projects/seal-paper-vids/artifacts/videos/seal-google-vids-final.mp4`: 1080p,
6,238 frames, 207.957914-second container duration, full decode pass. A separate
native-export review verifies all 19 source table values and all 36 encoded guide
arrivals. Original local-render evidence below remains a historical comparison.
No source skill behavior or immutable 0.15.2 package changed in this follow-up.

Date: November 15, 2026. Owning skill: `line-world-video`. Final package: `0.15.2`.
The primary skill remains `validating` for the previously recorded broader
composition-generation limit and the naturalistic strict failures below.

## Actual film and source evidence

The user requested a narrated explanation using a research paper itself, with
screen captures, source highlights, diagram navigation and tables. The selected
paper is [Self-Adapting Language Models](https://arxiv.org/abs/2506.10943v2), by
Zweiger, Pari, Guo, Akyurek, Kim and Agrawal, September 18, 2025 revision,
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The captured PDF digest
is `3abf83bcf05862d5e6e72078dc0e47ebfcf2e72866e9fdfe1dbc3663c72a9dc6`.
Original figures retain their original colors and typography. Spanish narration,
red guide/attention marks, close-ups and two linked bar views are additions.

The final local MP4 is `projects/seal-paper-vids/artifacts/videos/seal-paper-final.mp4`:
1920x1080, 30 fps, 207.9 seconds and 6,237 frames. Six actual native Nyla voiceovers
were generated and exported from Google Vids. Native scene announcements measured
35.040, 29.481, 32.081, 32.000, 39.920 and 39.280 seconds. Final silence padding
fills the frame-rounded budgets without changing speech speed. All decoded source
voice samples are retained byte for byte in the intermediate WAV; final AAC is a
new encode. The native project is a narration draft, not a final visual edit.
The browser's file-chooser permission check and subsequent URL-verification stop
were respected. No extension permission or alternate browser transport was used.

Current receipts live under `projects/seal-paper-vids/artifacts/reviews/`:

- `delivery.json`: final file/probe identity and complete voice sample partition.
- `paper-body-clearance.json`: every source frame checked against extractable
  PDF words and annotated figure bodies; zero findings.
- `render-clearance.json`: actual rerenders of revised scenes and their successor.
- `encoded-content.json`: all 6,237 decoded frames pass unchanged content-presence
  thresholds; zero empty or guide-only intervals.
- `encoded-review.json`: all 19 derived values match numeric extraction from the
  actual two PDF tables; all 36 encoded red guide arrivals pass.
- `visual-decisions.json`: hash-bound manual inspection of 90 encoded samples,
  eight contact sheets and full-resolution reading/close-up frames.
- `source-bundle.json`: actual ZIP extraction, every source digest, standalone
  rebuild, exact timing preservation and browser trajectory/poster check.

The route includes Figures 1, 2, 3 and 6, Tables 1 and 2, and the cost/evaluation
paragraphs on page 9. The narration distinguishes the selected eight-task ARC
subset from the full benchmark, percentage points from percentages, and the
single-passage comparison from both CPT reversals. It does not claim statistical
superiority, indefinite continual learning or absence of forgetting.

## Transferable tooling

`paper_video.py` and `assets/paper-video/` are self-contained runtime resources.
They provide verified page reuse, bounded source inspection, PDF-point lookup,
source-preserving rendering, full-frame table partitions, reversible close-ups,
semantic cue/column selection, raster-body avoidance, within-scene page shots,
an exact poster option and full trajectory inspection. Static reading holds reuse
one image. A changed ending invalidates the immediate successor's opening pose.

The new deterministic suite passes 12 tests, including actual PDF capture,
source/image cache invalidation, coordinate/data/timing boundaries, source-page
changes, browser repeat seeking, exact poster dimensions and harmless inspection
budget clamping. Native archive/discovery/installed runtime verification is
recorded in `projects/line-world-video/artifacts/host-checks/openai-0.15.2/`.
No global plugin installation or public marketplace publication is claimed.

## Isolated forward tests and retained failures

Model exception: `openai-codex/gpt-6.1-sol`, medium thinking, follows the recorded
Spark account rejection for this skill. Use runtime-only payloads, strict JSON,
exact output assertions, no ambient context and an unchanged copied skill.

1. `line-world-paper-tour-20261115-sol-1`: real-paper naturalistic development
   case, six exact artifacts produced, 14-second browser tour and 420-frame
   artifact checks pass. Strict result fails: an ad hoc PDF-text print hits
   Windows CP1252, and unescaped source line separators create 15 malformed
   event lines. Preserve the original failed trace. The resulting improvement
   is bounded ASCII-safe `inspect` plus an exact poster option.
2. `line-world-paper-tour-20261115-sol-2`: revised real-paper naturalistic
   development case, six exact artifacts produced, no malformed event JSON,
   copied payload unchanged. Strict result still fails: the agent requests a
   14,000-character inspection against a 12,000-character hard maximum, then
   recovers. Preserve the failed command and trace. The resulting improvement
   caps and reports positive inspection budgets without failing the call.
3. `line-world-paper-contract-20261115-sol-1`: current exact contract using
   reviewed paper regions, original table values, the oversized-budget boundary
   and the bundled browser/poster path. **Strict PASS**: seven exact outputs,
   observed Sol/medium, valid event JSON, zero tool errors, unchanged runtime
   payload and a clean read surface. Actual source/browser inspection covers
   420 frames; the 1920x1080 poster was independently inspected. Runtime reads
   are the entry point, one compact paper reference and the task's own outputs.
   No fixture, vendor source, sibling skill or project-context reads occur.
   The trace uses 14 tool calls over 70.746 seconds; this is a bounded contract,
   not a matched efficiency comparison with the naturalistic cases.

Native task-local 0.15.2 installation discovers all six plugin skills, verifies
exact archive/installed/canonical bytes and passes **89 installed utility tests**,
including the 12 new paper tests. The portable archive contains 301 declared
files and 5,198,109 payload bytes. Bounded local sync verifies 121 primary and
18 Google Vids files. The extracted editable archive verifies all 47 declared
source files and rebuilds with unchanged timing and a complete passing browser
audit using only its own bundled tools.

Final MP4 SHA-256: `671f7fd4a21eedd84186593779b82666f4fe06ce0c498900e4a52a3928a1b19a`.
Editable archive SHA-256: `2de62e7961a47047dae46be65f35216d16b8c763faf7736c5cd835978ea497ae`.

The two naturalistic cases are development measurements, not two clean release
passes. They prompted distinct, reproducible simplifications. A bounded contract
pass does not erase them or establish broader generation reliability. Embedded
raster labels require visual review; extractable PDF words are not OCR coverage.

## Commands and repository scope

```text
uv run --script skills/line-world-video/scripts/test_paper_video.py
uv run --script projects/seal-paper-vids/scripts/finish_video.py
uv run --script projects/seal-paper-vids/scripts/review_delivery.py
uv run --script skills/line-world-video/scripts/content_scan.py --video projects/seal-paper-vids/artifacts/videos/seal-paper-final.mp4 --output projects/seal-paper-vids/artifacts/reviews/encoded-content.json
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
uv run --script projects/seal-paper-vids/scripts/package_project.py
uv run --script projects/seal-paper-vids/scripts/check_source.py
```

Run definitions are versioned under `evaluations/pi-prompts/line-world-paper-*.md`;
full raw traces, copied payloads and outputs remain under ignored `evaluations/runs/`.
Pattern IDs, independence and payload checks pass. Global structure validation
and the global local-skill sync retain the four pre-existing semantic-reference
route findings in other skills. Keep the scoped video sync and validation results
separate. No published Pages source or catalog changed.
