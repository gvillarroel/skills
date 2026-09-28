# Free resource source skills validation

## Result and scope

Created five independent source bundles: Poly Haven, ambientCG, Pexels, Iconify,
and Kenney. Each has its own instructions, source guide, UI metadata, standard
library Python helper, transfer module and deterministic tests. Runtime scripts
use `uv` and Python 3.11 or later. No sibling bundle or repository file is required
to use an installed skill.

Poly Haven, ambientCG, Iconify and Kenney pass their release checks and are
`done`. Pexels is authored and locally installable, but remains `validating`:
`PEXELS_API_KEY` was absent, so authenticated live search/download and the browser
fallback were not exercised. Its missing-key workflow and offline photo/video
contracts pass. No credentials were printed or saved.

Validation used the local date **2026-09-27**; some UTC timestamps are September
28. Default Spark was tried first and rejected by this ChatGPT account before
any tool call. `openai-codex/gpt-5.6-luna`, high effort, was recorded in the
backlog as the model exception before subsequent trials.

## Release evidence

The final frozen bundles pass **36/36** strict isolated trials and independent
artifact checks. The release cohorts are fresh runs of the final payloads, not
the best runs selected from earlier revisions.

| Source | Command contract | Naturalistic request | Generalization | Ambiguity boundary | Live scope |
| --- | --- | --- | --- | --- | --- |
| Poly Haven | 1/1 | 3/3 | 3/3 | 1/1 | Texture search/JPEG, sunset HDRI, model dependency bundle |
| ambientCG | 1/1 | 3/3 | 3/3 | 1/1 | Concrete/brick search, JPG and PNG material ZIPs |
| Pexels | 1/1 | 3/3 | Not run | Not run | Access recovery and offline contracts only |
| Iconify | 1/1 | 3/3 | 3/3 | 1/1 | Lucide/MDI family search, exact colored SVG export |
| Kenney | 1/1 | 3/3 | 3/3 | 1/1 | Pattern and nature packs, exact ZIP and member extraction |

All 36 trials preserve the copied seven-file skill payload and have zero tool
errors, the expected model, exact requested output paths, and clean runtime read
surfaces. A separate metadata-only routing control passes 15/15, including two
requests per new source, Destockd, technical logos, and three negative requests.
This control is not proof of native Codex skill discovery.

There are **94 deterministic test executions**: 13 shared transfer/selection
tests in each of five self-contained bundles plus 29 source-specific tests
(42 distinct test definitions). Coverage includes exact selection, wrong-provider
manifests, credential redirect isolation, transfer checks, protected outputs,
corrupt/unsafe archives, aliases, typed photo/video IDs, model dependencies,
preview paths and UTF-8 gallery output.

Machine-readable evidence:

- [Final release checks](release-check-20260927.json): fixed cohort IDs, payload
  hashes, exact commands, read surfaces, deterministic checks and 37 explicit
  trace summaries, including the routing control.
- [All artifact audits](artifact-audit-20260927.json): all 66 attempts, including
  earlier failures and the rejected Spark attempt. Overall counts are 55 strict
  passes, 64 artifact passes and 54 joint passes. These aggregate counts must not
  replace the final-cohort table above.
- Raw traces, copied workspaces and output bytes remain under ignored
  `evaluations/runs/free-*-20260927-*` directories.

## Runtime payload hashes

| Skill | SHA-256 |
| --- | --- |
| polyhaven-asset-search | `1f6cb07cbec26804dfa4fccdb61f105fcdf0beeda91d1ed58b0fd4969e7bc87b` |
| ambientcg-material-search | `db0f5c84ee2ec1e71cebb1234a595c38927653a90e005d24eb5533134234d2de` |
| pexels-media-search | `10d4e387a6b757509283f05c94ddaa9ed1dda7d1f0be94c66165abfb547d8133` |
| iconify-icon-search | `446983a41091b8505825e48dd83c1fc9948af35aca7be025a788bbd7472760bb` |
| kenney-asset-search | `79fd3097b1776433062b0d8760781412ba69abc1ff6b76c3ad80b32324afb834` |

## Independent file and browser review

The evaluator checked downloaded bytes against receipts and provider checksums
where supplied. JPEGs and ambientCG maps were decoded with Pillow, ZIP members
passed CRC checks, SVGs retained requested color/height and full icon identities,
and extracted Kenney license bytes matched the selected archive. HDRI checks
verified the Radiance header and requested dimensions; they were not a full HDR
pixel decode.

A separate real Poly Haven `wood_floor_deck` glTF download includes the primary
file, a geometry buffer and three textures. All referenced URIs resolve inside
the bundle, the buffer length matches glTF metadata, and each texture decodes.
This does not claim an import test in a 3D application.

Playwright reviewed the four initial provider galleries and one final isolated
naturalistic gallery per live source. The final views each contain four cards
and four loaded previews, with no horizontal overflow. Screenshots were inspected
visually. The final Poly Haven mobile view at 390px also passes; the earlier
Iconify mobile gallery passes. Only a missing favicon was reported by the
localhost server. Images, screenshots, downloads and detailed review logs are in
ignored `projects/free-resource-skills/artifacts/` subdirectories.

Manual visual review is sampled, not exhaustive. Search keywords do not certify
semantic suitability: for example, ambientCG's broad `brick` search can return
ground with brick fragments. Skills require preview inspection and disclosure of
unverified criteria. PBR map selection, exact animation content, audio listening
and target-application compatibility depend on the user's actual task.

## Retained failures and repairs

1. **Provider limitation:** Spark was unsupported before tools ran. Retained at
   `free-iconify-contract-20260927-spark-1`; this was not a skill execution error.
2. **Windows preview paths:** initial Poly Haven, ambientCG and Kenney agents
   used shell `/tmp` paths that image tools resolved differently. Those trials
   failed strict isolation/tool gates even when their final artifacts were
   usable. Added bounded workspace-local preview commands and path guidance.
3. **Repeated preview directory:** one first-revision Poly Haven run tried to
   recreate an existing preview directory. The helper correctly refused it;
   the release instructions explain using a fresh directory or existing files.
4. **Agent-authored gallery:** one first-revision Poly Haven run wrote Windows
   default-encoded HTML that declared UTF-8 and used broken relative image
   paths. Added a gallery regeneration command and explicit UTF-8 guidance.
   Its replacement naturalistic cohort passes 3/3.
5. **Agent verification command:** one initial Poly Haven HDRI run used incorrect
   Windows path escaping despite a correct download. Helper file receipts now
   return portable paths. Later cohorts pass.
6. **Evaluator repairs:** the first live harness decoded Windows stdout as
   UTF-8 before helpers explicitly configured UTF-8; the repeat passed. The
   artifact checker initially assumed consecutive option numbers and one Pexels
   status schema. Those were not prompt requirements; the checker now accepts
   preserved unique option numbers and both truthful missing-key schemas.
7. **Manual browser tooling:** an unsupported `file:` navigation and an early
   CLI callback-format attempt were corrected by localhost serving and the
   documented callback interface. No skill output was changed to hide them.

Earlier artifacts and traces remain intact. Outside-workspace temporary images
created by failed isolated trials were not deleted because repository write
authority is limited to the project root.

## Reproduction

Run the source-specific command-contract and naturalistic prompts through the
repository harness. `run_forward.py` records the exact helper invocation,
`--mode json --strict`, model, required artifact paths and every attempt:

```powershell
uv run --script evaluations/free-resource-skills/run_forward.py --case naturalistic --source polyhaven --repeat 3 --suffix fresh-luna --workers 2
uv run --script evaluations/free-resource-skills/run_forward.py --case generalization --source kenney --repeat 3 --suffix fresh-luna --workers 2
uv run --script evaluations/free-resource-skills/audit_runs.py
uv run --script evaluations/free-resource-skills/check_release.py
uv run --script projects/free-resource-skills/scripts/audit_live_files.py
```

Use a new suffix for new trials; never overwrite retained run directories.
`check_release.py` rechecks the recorded release cohorts and current payload
hashes. It explicitly runs `summarize-pi-json-events.py` with the required Luna
model, invalid-JSON failure and tool-error failure flags. Each manifest records
all exact expected artifact paths. The generalization prompts download saved
option 2, rather than an independently re-searched asset.

Final repository checks and targeted installation commands:

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/sync-local-skills.py --source skills/<skill-name> --destination .agents/skills/<skill-name>
uv run --script scripts/sync-local-skills.py --source skills/<skill-name> --destination .agents/skills/<skill-name> --check
```

Quick skill metadata validation also passes for all five bundles. No Pages
examples were added. The initial validation completed before the user requested
source publication on 2026-09-28.

## Remaining coverage

- Configure the user's free Pexels API key in the environment, then run live
  photo/video search, exact rendition downloads and three fresh naturalistic
  and generalization repetitions before marking that skill `done`.
- Pexels browser fallback is documented but untested in this pass.
- Provider catalogs, endpoints and licenses can change. Source guides include
  verified official documentation links and recovery instructions. The skills
  refresh the selected identity and reject unavailable variants rather than
  silently replacing them.
