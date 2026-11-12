# Desktop plugin UI: v2 contract and boundary evidence

Checked 2026-10-24. These results belong exclusively to the frozen **v2**
eight-file `desktop-plugin-ui` runtime, SHA-256
`e6595579f0c0ab026a9fa1e60e65578926d583d11f306d2693dd14b69f7e1518`.
The revision added exact-source copying guidance and the host-prompt/render-site
reference. The contract prompt was expanded to cover those surfaces. The
boundary prompt was unchanged. Earlier seven-file results remain separate in
`contract-boundary-20261024.md`; no runs were rerolled or artifacts repaired.

Both fresh runs used **openai-codex/gpt-5.6-luna**, high thinking, strict JSON
mode, runtime payload and a 600-second timeout. The model exception after the
retained Spark rejection is recorded in `SKILLS.md`.

## Results

| Case and run ID | Strict harness | Independent artifacts | Joint outcome |
| --- | --- | --- | --- |
| Contract: `20261024-desktop-ui-v2-contract-luna-1` | Pass, 11 error-free tool calls, 66.033 seconds | Fail: JSON elicitation source changes `.io` to `.org`; all Markdown URLs copy exact bundled strings | Fail; classification `agent` |
| Boundary: `20261024-desktop-ui-v2-boundary-luna-1` | Pass, 10 error-free tool calls, 37.905 seconds | Pass: accurate conditional review and exact source URLs | Pass |

Strict acceptance is **2/2**. Independent and joint acceptance is **1/2**.
The v2 contract gate remains **0/1**, with boundary **1/1**. Do not pool earlier
or later subject results into these totals. No signed-in target host was
available or claimed. These cases do not establish release or routing success.

## Independent contract review

The output pair is exactly `results/reference.md` and `results/decisions.json`.
Both files are nonempty; JSON parses and includes **17** unique canonical
pattern IDs, required fields, snapshot date and
`host_acceptance_verified: false`. Markdown describes additional applicable
patterns with explicit input, rule, failure/fallback and validation content.

The team-facing advice correctly separates Chat MCP Apps, native Code Mods,
MCPB/settings and browser-only evidence. It preserves useful text/data,
explains registration/MIME/bridge mechanics, and scopes optional modes,
downloads, persistence and real-host checks. It labels SDK/browser/native
tests without promoting them to installed host acceptance.

New surfaces are handled correctly. Elicitation is host-rendered constrained
input or an out-of-band URL flow, separate from arbitrary HTML App forms;
Desktop Chat support remains conditional/untested and secret values are kept
out of form mode. Native render sites are distinguished from custom panes;
documented transcript/tool/question sites do not imply access to arbitrary
host permission prompts, toolbars, DOM or OS windows. Other render-site
replacements remain explicitly untested.

The generated Markdown contains **21** unique HTTP(S) URL strings, all exact
members of the copied frozen bundle's URL inventory. However, the JSON has
**11** unique URL strings and one mismatch in the evidence for
`claude-ui-host-elicitation`:

- Output: `https://modelcontextprotocol.org/specification/2025-11-25/client/elicitation`
- Bundle: `https://modelcontextprotocol.io/specification/2025-11-25/client/elicitation`

This is a complete-string mismatch, not a domain-family allowance or a
normalization issue. The correct URL appears in the generated Markdown, but
that does not repair the incorrect JSON citation. The independent artifact
gate fails, classified **agent**, because the copied reference and explicit
source-copying instruction supplied the exact URL. Preserve the output pair.
The failed prose-only mitigation suggests a deterministic all-format source
checker as a next skill revision, followed by a separately frozen cohort.

## Independent boundary review

The output pair is exactly `review/boundaries.md` and `review/status.json`.
JSON includes six assessments, **13** canonical pattern IDs, and false product
confirmation and host-acceptance booleans. It completes the review with a
provisional Claude Desktop assumption rather than inventing a Cloud Desktop
product or waiting for an unavailable answer.

The analysis correctly rejects arbitrary React/iframe content in native Mods
and Client regions, while allowing a separate Chat HTML View. It accurately
reports tested native Link downgrade instead of claiming the entire tree
failed. It rejects SDK method/enum existence as support evidence, keeps mode
and export fallbacks conditional, and distinguishes observed SDK dispatch from
real host permission or OS delivery. The fixture does not become production
acceptance. Hidden-chart initialization is treated as a component sizing
pitfall, with reveal/resize and actual-paint checks, rather than a blanket
HTML restriction. Every assumption receives a useful alternative and an
evidence collection plan.

The Markdown has **8** unique HTTP(S) strings, including the literal localhost
example; all exactly occur in the copied bundle. JSON contains no URLs. Both
formats were checked. No additional semantic defect was found.

## Trace and integrity

Both trace summaries require the observed `gpt-5.6-luna`, contain valid JSON,
and report zero tool errors. The contract reads prompt first, then `SKILL.md`
and all six references. Those focused reads fit its explicit cross-surface
taxonomy request. Boundary reads prompt, entry point and the five references
needed for its combined native/Chat/capability/layout questions; it does not
read the unrelated new host-prompts reference. Neither reads repository files,
sibling skills, example galleries or project artifacts, uses the network, or
changes external applications. Each copied eight-file payload is unchanged.

## Commands and independent checks

```powershell
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-contract.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id 20261024-desktop-ui-v2-contract-luna-1 --expect-output results/reference.md --expect-output results/decisions.json --timeout-seconds 600
uv run --script scripts/run-pi-skill-eval.py desktop-plugin-ui --prompt-file evaluations/pi-prompts/desktop-plugin-ui-boundary.md --model openai-codex/gpt-5.6-luna --mode json --strict --run-id 20261024-desktop-ui-v2-boundary-luna-1 --expect-output review/boundaries.md --expect-output review/status.json --timeout-seconds 600
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-v2-contract-luna-1/events.jsonl --output evaluations/runs/20261024-desktop-ui-v2-contract-luna-1/read-surface.json --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-desktop-ui-v2-boundary-luna-1/events.jsonl --output evaluations/runs/20261024-desktop-ui-v2-boundary-luna-1/read-surface.json --require-model gpt-5.6-luna --fail-on-invalid-json --fail-on-tool-error
```

Evaluator checks parsed JSON, compared output IDs with copied canonical
headings, and reviewed both Markdown/JSON pairs directly. Exact URL checks
extracted complete HTTP(S) strings from **both output formats** and the copied
Markdown bundle, retained fragments, removed only trailing sentence/list
punctuation, and used case-sensitive complete-string membership. No domain
normalization, redirects or scheme substitution was allowed. The mismatch
is independently apparent in the JSON source field. Per-run retained
`source-url-check.json` files record counts and exact mismatches outside the
copied skill. No information was fed back into the evaluated runs.

## Retained artifacts

Raw run manifests, events, output pairs, exact-source checks and trace/integrity
reports remain under each named ignored `evaluations/runs/` directory.

| Output | Bytes | SHA-256 |
| --- | ---: | --- |
| Contract `results/reference.md` | 22,210 | `4da61bf0e5c7e69284f454bee6df03906c760489f94f8896164ab86ac883c944` |
| Contract `results/decisions.json` | 14,454 | `7d4e560df1733ec313493bf0e086c9f1675c5997b7587e94d5f2779dbf63312e` |
| Boundary `review/boundaries.md` | 8,347 | `d1791580ab22bd7f5bf8f2341ef3c3eb010cba2112d7b8bc24c03a1ceaf2b36c` |
| Boundary `review/status.json` | 3,813 | `7112d32ccd2a7fe578fd56ea55c9e16bdaddac9b9715094681da0094fbf3eca1` |
