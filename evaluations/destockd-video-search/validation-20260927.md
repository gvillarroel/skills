# Destockd Video Search validation — 2026-09-27

## Outcome

Released a six-file standalone bundle with live discovery, a dated taxonomy,
numbered preview galleries, stable film/shot selection and exact MP4 downloads.
Seventeen deterministic tests pass. Eight isolated Luna executions pass the
strict runtime and independent technical artifact checks. Manual review accepts
three naturalistic cases and two of three generalization descriptions; the
remaining description contains a retained visual interpretation error. The
exact selected download is correct in all four download executions.

The unchanged runtime payload is
`b8c79350e21ad859341048ebde010628d32f4e7af4a8a816dd24948924e138ec`.
It contains `SKILL.md`, UI metadata, two references, the helper and its tests.

## Live observations and implementation

- The site advertised 41,000+ shots, exposed 648 films and returned 12 editorial
  collections. Counts are a snapshot, not a permanent catalog promise.
- Browser navigation verified Collections, visual search, an individual shot's
  player, source links, previous/next, similar shots and download control.
- Direct calls exercised collections, collection pagination, visual searches,
  film-title search, all shots from a film, similar shots and shot metadata.
  Routes were read from the actual public frontend, not guessed.
- Multiple queries deduplicate film/shot identities and combine their ranks.
  Saved options retain query-specific scores without interpreting them as
  confidence percentages. Color/title filters operate on the fetched window.
- The downloader refreshes the chosen identity, uses the returned `clip` field,
  protects existing files and writes a provenance/hash receipt. It verifies
  media response type, transfer length, MP4 signature and an ffprobe video stream
  when ffprobe exists. Temporary files are cleaned after failure.
- The generated six-card gallery has six distinct IDs, six preview players and
  no horizontal overflow at the available desktop viewport. A preview played to
  3.005 seconds with readyState 4, 1920×1080 dimensions and no media error.
  The final example's six keyframes were independently reviewed. No mobile
  viewport claim is made.

Manual real download: **Women Astronauts Training / shot_050**, 8,127,696 bytes,
5.387 seconds, 1920×1080, H.264, 24 fps, audio stream present. SHA-256:
`8676cf0f44078e7afee9193dde5c588752a241dee51aa3c250f7b411f629dfd0`.
Both ffprobe and complete ffmpeg decoding pass. Artifacts stay under
`projects/destockd-discovery/artifacts/`; source captures and videos are ignored.

## Isolated protocol and all attempts

Pi 0.84.2, Python 3.13.12, Windows 11, runtime profile, strict JSON mode,
high reasoning, no ambient context/extensions/skills/templates/themes, exact
required output paths and a read-only copied bundle.

The required first Spark attempt,
`destockd-contract-20260927-spark-1`, failed before any tool call because the
provider reported that Spark is not supported for this ChatGPT account. This is
an infrastructure failure, not a passing trial. The deliberate model exception
`openai-codex/gpt-5.6-luna` was recorded in SKILLS.md before the subsequent runs.

| Case / run IDs | Strict execution | Independent technical checks | Manual review |
| --- | --- | --- | --- |
| `destockd-contract-20260927-luna-1` | 1/1 | 1/1 | Exact known shot and provenance pass. |
| `destockd-naturalistic-20260927-luna-{1,2,3}` | 3/3 | 3/3 | 3/3 within the prompt's candidate contract. Runs 1–2 explicitly leave visual matches unverified. Run 3 reads six keyframes and describes their visible content with appropriate motion uncertainty. |
| `destockd-generalization-20260927-luna-{1,2,3}` | 3/3 | 3/3 | 2/3 descriptions accepted. Run 2 calls a mountain painting a dragon-like figure. All runs inspect keyframes and download saved option 3 correctly. |
| `destockd-boundary-20260927-luna-1` | 1/1 | 1/1 | Asks which of two candidates “download it” means; downloads neither. |
| `destockd-routing-20260927-luna-1` | Model/event check passes | 10/10 classifications | Metadata-only control with no forced skill; not a native Codex discovery measurement. |

All strict runs preserve the same payload digest, produce valid JSON events,
and have zero tool errors. Read surfaces contain the prompt, `SKILL.md`, the
two relevant short references when needed, and generated task artifacts. No
examples, source script reads, sibling skills, repository documentation or
external local files were needed. Shell commands were reviewed as well.

The generalization visual error is an agent interpretation failure. It does not
change the successful byte/identity checks. It meets the repository's at-least
two-of-three generalization threshold, but it prevents a claim of universal
semantic accuracy. A keyframe proves only visible static content; action and
historical identity can require playback and source review. The naturalistic
unverified fallback likewise must not be presented as verified scene matching.

The [independent artifact audit](artifact-audit-20260927.json) records all eight
technical checks. Original prompts, events, receipts and outputs remain under
`evaluations/runs/<run-id>/`. No failed attempt was replaced or discarded.

## Reproduction

Bundled and repository checks:

```powershell
uv run --script skills/destockd-video-search/scripts/test_destockd.py
uv run --with pyyaml python -X utf8 C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/destockd-video-search
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/sync-local-skills.py --source skills/destockd-video-search --destination .agents/skills/destockd-video-search
uv run --script scripts/sync-local-skills.py --source skills/destockd-video-search --destination .agents/skills/destockd-video-search --check
```

The first quick-validator invocation lacked PyYAML; the next hit Windows' default
text encoding. Supplying PyYAML and `python -X utf8` passed without changing the
validator or skill. These were local validation-environment corrections.

Strict contract run (use a fresh run ID for another execution):

```powershell
uv run --script scripts/run-pi-skill-eval.py destockd-video-search --prompt-file evaluations/pi-prompts/destockd-contract.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id destockd-contract-20260927-luna-1 --expect-output catalog.json --expect-output selected.json --expect-output chosen.mp4 --expect-output chosen.mp4.json --expect-output-json-field 'chosen.mp4.json::shot.shot=shot_050'
```

Naturalistic runs use `destockd-naturalistic.md` with outputs `options.json`,
`options.html`, `reply.md`. Generalization runs use `destockd-generalization.md`
with outputs `animation-options.json`, `animation-options.html`, `animation.mp4`,
`animation.mp4.json`, `reply.md`. Each was repeated in three fresh workspaces.
The boundary prompt requires `reply.md` and `decision.json`, asserting
`download_performed=false` and `needs_selection=true`.

```powershell
uv run --script evaluations/destockd-video-search/run-routing.py --run-id destockd-routing-20260927-luna-1
uv run --script evaluations/destockd-video-search/audit-runs.py evaluations/runs/destockd-contract-20260927-luna-1 evaluations/runs/destockd-boundary-20260927-luna-1 evaluations/runs/destockd-naturalistic-20260927-luna-1 evaluations/runs/destockd-naturalistic-20260927-luna-2 evaluations/runs/destockd-naturalistic-20260927-luna-3 evaluations/runs/destockd-generalization-20260927-luna-1 evaluations/runs/destockd-generalization-20260927-luna-2 evaluations/runs/destockd-generalization-20260927-luna-3 --out evaluations/destockd-video-search/artifact-audit-20260927.json
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/destockd-naturalistic-20260927-luna-3/events.jsonl --require-model gpt-5.6-luna --require-tool-call --fail-on-invalid-json --fail-on-tool-error
```

The final command was applied to all eight strict traces and the routing trace.
The strict harness separately enforces prompt-first, exact outputs, permitted
reads and unchanged payload. Compact trace outputs live under the project
artifact review directory.

## Operational limits

Destockd's GET API is a website implementation detail that can change. Browser
fallback remains necessary if its public contract changes. Search similarity
does not guarantee an exact requested scene, and editorial membership can be
broader than the collection's title. Full-film download remains a source-page
workflow. `ffprobe` is optional; without it, metadata and validation are more
limited and the receipt says so. The tested download filesystem is NTFS; atomic
no-replace promotion uses same-directory hard links. Destockd's source links
describe provenance rather than independently clearing all reuse rights.

No published example set or Pages source was added, so no Pages deployment was
required. Existing unrelated working-tree changes were preserved.
