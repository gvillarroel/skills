# Lucidchart SVG validation — 2026-10-07

## Scope and status

The standalone `lucidchart-svg` bundle provides editor SVG export, SVG/custom-library insertion, source inspection and byte-preserving preparation, and semantic reconstruction through native Mermaid or a locally compiled Standard Import package. It does not infer a graph automatically from arbitrary SVG paths.

Keep the backlog status **validating** until authenticated live SVG export, custom SVG insertion, and Standard Import parser/native editing acceptance are verified. The present request creates the skill; its offline trials do not mutate a Lucid account. Existing project evidence also records SVG download timeouts and untested custom SVG insertion; successful PDF/raster exports do not count as SVG acceptance.

Official sources were checked on this date. SVG export is supported through the editor; the current REST document-image endpoint documents JSON/PNG, not SVG. Custom-library SVG import is documented as premium. Standard Import SVG images become PNG; native editability requires reconstruction into shapes and attached connectors. The dedicated multipart endpoint is `/v1/documents/create`, while the older overview example still uses `/v1/documents`; the bundle records this discrepancy and prefers the endpoint reference.

- [Editor export](https://help.lucid.co/hc/en-us/articles/16324571257492-Export-or-print-a-Lucid-document)
- [SVG shape libraries](https://help.lucid.co/hc/en-us/articles/14931750819476-Shape-libraries-in-Lucidchart)
- [REST export formats](https://developer.lucid.co/reference/getorexportdocument)
- [Standard Import endpoint](https://developer.lucid.co/reference/createdocumentwithstandardimport)
- [Standard Import images](https://developer.lucid.co/docs/images-si)
- [Official native Mermaid update](https://community.lucid.co/community-news-and-announcements-9/copy-paste-mermaid-syntax-for-editable-diagrams-13659)

The earlier [project acceptance record](../../projects/lucid-native-compatibility/reviews/acceptance.md) is contextual evidence only. No project file or sibling skill is required at runtime. No existing project or unrelated ECharts change was modified.

## Deterministic machinery

The final bundle has nine files. Runtime payload SHA-256, as measured by the isolated harness:

```text
64dbb4ba9d63b2527fee684d0e7cf0361fb01dcb832652a992add8770cc8f9e6
```

Twenty-five deterministic tests pass: 16 SVG checks and 9 native-package checks. They cover actual XML/HTML distinction, dimension validity, byte-preserved output, source protection, dependencies, active content and stylesheet instructions, `foreignObject`, internal fragments, legacy Windows pipe encoding, native IDs/bounds/colors/text/ports, endpoint existence, deterministic ZIP bytes, exact output paths, escaped labels, optional edges, duplicate JSON keys, invalid Unicode/numbers, and document size limits.

```powershell
uv run --script skills/lucidchart-svg/scripts/test_svg.py
uv run --script skills/lucidchart-svg/scripts/test_native.py
uv run --with pyyaml python C:/Users/villa/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/lucidchart-svg
```

The inspector is a conservative static review, not a sanitizer or browser security boundary. The native compiler implements only the documented rectangle/circle/diamond/text subset with straight attached connectors. Its `ellipse` input maps to `circle` with supplied bounds and explicitly reports that approximation. Local schema/package checks do not prove upstream rendering.

## Isolated trials

Default Spark was tried first in `20261007-lucid-svg-contract-spark-1`. The provider rejected `gpt-5.3-codex-spark` with this ChatGPT account before any tools; no outputs were created. This is an infrastructure failure, retained as evidence. The recorded evaluation-only model exception is `openai-codex/gpt-5.6-luna`, high thinking. Strict JSON, exact outputs, clean runtime reads, zero tool errors, observed model, and immutable payload gates remain enforced.

Reusable inputs are in the four [Lucidchart SVG prompts](../pi-prompts/lucidchart-svg-contract.md); the matching naturalistic, boundary, and generalization prompts live beside it. The evaluator-owned [semantic validator](validate_artifacts.py) checks actual source geometry, labels decoded from Lucid HTML, source colors, native object types, graph/package consistency, attached directional ports, exact SVG bytes/hash, and absence of fabricated native output on ambiguous input. Status notes are reviewed manually, without prose matching.

Final frozen-source results are **8/8 joint passes**: contract 1/1, boundary 1/1, naturalistic 3/3, and generalization 3/3. Each passes strict harness, observed model, exact outputs, unchanged payload, independent artifacts and manual status review. Raw manifests, events, outputs, integrity checks, independent reports and read-surface summaries remain under ignored `evaluations/runs/`.

| Case | Run ID | Scope |
| --- | --- | --- |
| Contract | `20261007-lucid-svg-contract-luna-final2` | Two rectangles, literal angle/ampersand label, one attached edge, exact package/JSON paths |
| Boundary | `20261007-lucid-svg-boundary-luna-final2` | External image, HTML content, unknown graph topology, unavailable remote operations |
| Naturalistic | `2026-10-07-lucidchart-svg-naturalistic-final-luna-1` through `-3` | SVG asset identity plus three native approval nodes and two semantic connectors |
| Generalization | `2026-10-07-lucidchart-svg-generalization-final-luna-1` through `-3` | Translated vertical flow, ellipse approximation, independent text object, colors and top/bottom ports |

Final generalization resolves the four boxes to `(110,40,140,60)`, `(110,190,140,60)`, `(110,340,140,60)`, and `(260,200,130,40)`, with native circle/rectangles/text, preserved literal labels/colors, and attached vertical ports. All final notes explicitly state that no authenticated Lucid acceptance occurred. The six repeated cohorts retain `independent-artifact-review.json`, `read-surface-review.json`, and `manual-status-review.json`; the root contract/boundary retain `independent-artifacts.json` and `read-surface.json`, with status text reviewed directly.

Run commands use:

```powershell
uv run --script scripts/run-pi-skill-eval.py lucidchart-svg `
  --prompt-file evaluations/pi-prompts/lucidchart-svg-<case>.md `
  --model openai-codex/gpt-5.6-luna --mode json --strict `
  --run-id <recorded-run-id> --expect-output <each-exact-required-path>

uv run --script evaluations/lucidchart-svg/validate_artifacts.py `
  <case> evaluations/runs/<run-id>/workspace `
  --report evaluations/runs/<run-id>/independent-artifacts.json --compact

uv run --script scripts/summarize-pi-json-events.py `
  evaluations/runs/<run-id>/events.jsonl `
  --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error `
  --output evaluations/runs/<run-id>/read-surface.json
```

The prompts enumerate all required outputs; every path is repeated as an `--expect-output` argument. The contract also uses `--require-exact-command-from-prompt`. Normal runtime reads are the prompt, `SKILL.md`, only relevant compact references, and task outputs; no acceptance gallery, repo document, project artifact, or sibling skill is a runtime dependency.

## Retained development attempts and promoted repairs

All earlier attempts remain retained; they are not counted as final release passes.

- Initial contract runs `20261007-lucid-svg-contract-luna-1`, `-final`, and `-release` passed local/harness checks on earlier payloads. `20261007-lucid-svg-boundary-luna-1` also passed. Documentation was then corrected to distinguish the canvas-paste native Mermaid route and limit the documented raster conversion statement to SVG.
- Naturalistic development runs `2026-10-07-lucidchart-svg-naturalistic-luna-1` through `-3` passed strict and independent checks 3/3.
- Generalization development runs `2026-10-07-lucidchart-svg-generalization-luna-1` through `-3` passed strict harness checks 3/3 but semantic artifact checks 2/3. Run 3 omitted the ancestor translation on the ellipse and incorrectly reported that it had resolved it. The raw output remains unmodified. A compact transform formula and endpoint cross-check were promoted into the native reference before the final cohort.
- `20261007-lucid-svg-boundary-luna-release` produced correct diagnostics/status but failed strict zero-error gates after unnecessary repeated `prepare` calls on a known blocked SVG, including an existing-report collision. The entry point now checks eligibility from the saved report first and avoids rewriting that report during preparation. No strict gate was relaxed.
- Independent review found stylesheet-processing instructions and nested HTML content could evade an earlier inspector pass; those inputs now receive blockers. Broken internal references now receive a portability warning.
- A directly reproduced Windows cp1252 pipe failure with an arrow label led to explicit UTF-8 stdout/stderr and two regression tests. The final isolated cohorts use the corrected payload.
- Evaluator implementation errors were repaired independently: use the documented `diamond` type, judge edge semantics/identity mapping rather than requiring unrequested literal SVG path IDs, and encode stdout safely on Windows. No generated agent artifact was repaired by the evaluator.

## Visual review and remaining limits

The final naturalistic SVG was served locally and opened in the hidden in-app browser. Browser accessibility and screenshot observations showed all four labels and the three source shapes. The prepared SVG deliberately retains the source's text placement and unstyled paths: some labels extend beyond their boxes and the source paths have no visible stroke. The native mapping notes disclose centered labels and added destination arrows. This visual review verifies source identity/appearance, not a polished live Lucid document.

Playwright CLI Chrome launch failed; a bundled Playwright/browser attempt then reached the page but timed out during screenshot capture. These are browser infrastructure limitations, not isolated trial tool failures. The supported in-app browser completed the screenshot review. Browser output and transient profiles stay in ignored evaluation paths; no example set was published.

Manual metadata routing review: Lucid SVG export, custom SVG upload, and editable SVG-to-Lucid requests match; generic SVG illustration without Lucid context does not. All authored skill text, references, metadata and validation material are English.

Live acceptance still needs a source Lucid document, a usable authenticated download/upload surface, and an authorized Standard Import integration. Verify actual SVG bytes, imported asset appearance, returned document metadata, separate shape label editing, movement with connector following, and undo. Keep `validating` until those checks pass; do not start a paid trial or issue new credentials to make a local evaluation look complete.

## Repository gates

Required repository structure, independence, pattern-ID and payload checks are run at handoff. The isolated harness's 17 regression tests pass. A focused source/runtime/full-copy authoring audit passes for this skill; an accidentally mis-scoped audit and a broad all-skill audit were not treated as results for this bundle. The final source is synchronized into the ignored repository-local installation and checked for drift.

```powershell
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
uv run --script scripts/test-pi-eval-harness.py
uv run --script scripts/sync-local-skills.py
uv run --script scripts/sync-local-skills.py --check
```
