# Delivery tool improvements, plugin 0.16.0

Date: November 15, 2026. Scope: reusable Google Vids adapter utilities and the
six-skill OpenAI/Codex plugin. No new account action was needed for this pass.
The existing native SEAL movie remains unchanged.

## Observed friction and promoted behavior

The evidence comes from the completed SEAL production, its saved native scene
inventory, cloud export receipt and actual downloaded MP4. These were real
observations from the prior production; this pass replays them locally.

| Tool or surface | Observed friction | Reusable improvement |
| --- | --- | --- |
| CUA AX observations | Diffs omitted unchanged controls; first post-action tree could be stale | Require a full fresh state for control lookup and return one recommendation at a time |
| Background Chrome tab | Browser AX worked while native Open dialog stayed hidden | Verify the intended foreground tab before Upload; observe after raising/selecting it |
| Native owned Open dialog | Filename indices appeared but were unavailable in cached app state | After observing Open, focus File name with `Alt_L+n`, paste exact path and press Return |
| Upload progress | Delayed dialog or media could invite duplicate insertion | Explicit await-dialog/await-insertion phases recommend observation before retry |
| Timeline media | Semantic IDs differed from numbered clip names | Match actual `clip` basenames and separately preserve stable scene IDs |
| Drive connector search | Fresh export was absent from search | After one focused search, use authorized Drive UI to identify the export, then known-ID metadata |
| Copy link | Immediate clipboard read was empty | Reobserve stable URL/share dialog; never guess a file ID or expose signed downloads |
| Delivery handoff | A voice-only Vids draft and local path did not satisfy native/cloud delivery | Gate scene inventory, visuals, retained narration, native provenance, actual bytes, metadata, playback, Download and continuity |
| Repeated MP4 checks | Unchanged media was verified again | Cache full decode by MP4 SHA-256 and measured timing; invalidate on changed bytes/timing |

`vids-ui.js` remains pure: no UI, file or network operations. It never confirms
an upload. `vids_delivery.py` compiles supplied observations and local checks;
it cannot produce native evidence. The final receipt states this limitation.
No browser permission change, hidden endpoint, public sharing or alternate
transport after a policy stop is part of the promoted workflow.

## Deterministic and real-file validation

The isolated command contract ran all four changed/related utility suites:
11 UI recommendation tests, 17 delivery tests, 25 batch tests and 5 inventory
tests, all passing (58 total). Cases include late dialogs, missing full state,
wrong project, missing selection, another scene's filename, policy stop,
voice-only scenes, stale receipts, metadata mismatch, missing playback/download,
missing audio, corrupt cache and actual encoded media.

An additional evaluator-side batch integration passes the full
init/observe/build/confirm/deliver sequence with a real local fixture and
explicitly synthetic account observations. It checks automatic template
creation, complete delivery, resumption from a custom evidence path, stale
status after that evidence changes, and the subsequent missing-playback gate.
The report is `projects/line-world-video/artifacts/reviews/batch-delivery-0.16.0/integration.json`.
This check performed no account action and did not change the frozen skill.

Replayed the existing six-scene native SEAL export with:

```text
uv run --script projects/line-world-video/scripts/replay_seal_delivery.py
```

The 17,119,832-byte file has SHA-256
`6cdeeefffc7f93831a4bf6a5ef89b79b2b87cbc20832281202c02d0a12ffb332`.
All delivery checks pass using saved real observations. Initial verification
took 1.3585 seconds; unchanged repeat took 0.0363 seconds and reused the decode.
Missing playback produces `cloud-delivery-needed`; a voice-only scene produces
`native-scenes-incomplete`. This is a local verification measurement, not a
token-cost or entire-production speed claim. The replay is stored under
`projects/seal-paper-vids/artifacts/reviews/delivery-0.16.0/`.

## Isolated skill-only forward tests

All runs use runtime payload, exact required outputs, strict JSON, disabled
ambient discovery and unchanged read-only skill resources. Model exception:
`openai-codex/gpt-6.1-sol --thinking medium`, continuing the recorded account
limitation that prevents Spark use. No zero-error, output or isolation gate
was waived.

| Case and run suffix | Result | Duration | Exact outputs |
| --- | --- | --- | --- |
| `line-world-vids-delivery-contract-20261115-sol-1` | Strict pass | 39.607 s | 1 |
| `line-world-vids-delivery-natural-20261115-sol-1` | Strict and independent artifact pass | 97.191 s | 8 |
| `line-world-vids-delivery-natural-20261115-sol-2` | Strict and independent artifact pass | 113.429 s | 8 |
| `line-world-vids-delivery-natural-20261115-sol-3` | Strict and independent artifact pass | 102.907 s | 8 |

Naturalistic cohort: 3/3 joint passes. The synthetic offline cases create a real
two-second MP4, complete and blocked receipts, stale-revision rejection, cached
verification and five UI next-step recommendations. They explicitly disclaim
live uploads/playback. Evaluator-side inspection checks actual file hash/size,
full decode, 320x180/30 fps geometry, white/gray/red pixels, audible 440 Hz tone,
cloud-first links, missing-playback failure and old-revision rejection. All three
generated fixture frames were visually inspected and retain clear separated
gray objects and red marks.

Read surfaces contain the entry skill, the relevant delivery/UI/handoff/timing
references, the directly used verifier/parser scripts and generated outputs.
No acceptance examples, sibling skills, repository docs or outside files were
read. Trace summaries show valid JSON, zero tool errors and unchanged bundles.
The source of `vids_delivery.py` was read in all three naturalistic runs; it is
a directly used 13 KB utility, not a gallery. There is no measured token-savings
comparison for this release.

Repeat the contract with:

```text
uv run --script scripts/run-pi-skill-eval.py line-world-google-vids --prompt-file evaluations/pi-prompts/line-world-vids-delivery-contract.md --model openai-codex/gpt-6.1-sol --thinking medium --mode json --strict --run-id <fresh-contract-id> --expect-output artifacts/contract.json
```

For naturalistic repetitions, use `line-world-vids-delivery-natural.md` and
eight `--expect-output` paths: `artifacts/01-method.mp4`, `ready.json`, `ready.md`,
`blocked.json`, `blocked.md`, `stale.json`, `ui-next.json`, `checks.json` (all under
`artifacts/`). Inspect each with:

```text
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/<run-id>/events.jsonl --output evaluations/runs/<run-id>/read-surface.json --require-model gpt-6.1-sol --fail-on-invalid-json --fail-on-tool-error
uv run --script evaluations/contracts/verify-line-world-delivery.py evaluations/runs/<run-id>
```

Retained development corrections: source preflight caught the missing contents
section on the expanded UI reference before Pi began; it was fixed. The external
media validator initially used `.5`, which this FFmpeg rejects as a duration;
changing the evaluator to `0.5` fixed it without touching agent outputs. Neither
is counted as a failed or waived runtime pass. No Pi cohort outputs were repaired.

## Release and repository verification

Both runtime archives contain the same 305 declared files. Canonical parity
matches all 121 primary and 22 adapter files. Native task-local Codex marketplace
installation and app-server `skills/list` discover all six plugin-qualified
skills. All **151 installed utility tests** across 13 suites pass, including all
58 delivery/batch/UI/inventory tests. No global desktop plugin activation or
account publication is claimed.

Run the checks in this order because the first verifier fetches the official
plugin schema used by the second:

```text
uv run --script projects/line-world-video/scripts/package_plugin.py
uv run --script projects/line-world-video/scripts/verify_plugin.py
uv run --script projects/line-world-video/scripts/verify_openai_package.py
```

The first OpenAI package-check attempt ran before its schema dependency had
finished and failed with a missing `plugin.schema.json`. The subsequent ordered
run passes; its earlier `clean-*` work directory is retained. This was a local
verification-order error, not a package or skill failure.

| Artifact | Bytes | SHA-256 |
| --- | --- | --- |
| `line-world-video-0.16.0.zip` | 1,840,833 | `40b8d04f73f57dc322254f51fdd45657cd40cbb88f2d232743a284fcc7fc86af` |
| `line-world-video-0.16.0-marketplace.zip` | 1,846,133 | `7b24414bcf9422d373b4b6fe2890a0fd57483d1938b9f2d5fe08e1a4face37df` |

Archives live under `projects/line-world-video/artifacts/packages/`; native
installation evidence is under `artifacts/host-checks/openai-0.16.0/verification.json`.
Prior release archives remain immutable.

Pattern-ID validation passes (1,348 IDs), independence validator tests pass and
the payload check passes. The global skill validator and global synchronization
report only the same four pre-existing unrelated reference-route findings:
`schema-validation-review.md` in curate-semantic-model, `premise-reuse.md` in
extract-ontologies, and `keyword-witnesses.md`/`product-crawl.md` in
extract-with-ontology. The bounded sync validates and refreshes the owning two
skills (121/22 files); 13 adapter files changed. No Pages source/catalog changed,
so no publication or Pages build was required.

```text
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py
uv run --script projects/line-world-video/scripts/sync_local.py
```

The adapter returns to `done` for this qualified delivery scope. The primary
video skill remains `validating` for its earlier broader generation reliability
limitation; this scoped adapter cohort does not remove that limitation.
