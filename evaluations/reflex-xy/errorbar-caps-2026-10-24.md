# Corrected native error-bar cap contract

The single predeclared attempt `20261024-reflex-xy-errorbar-caps-contract-sol-1`
passed its strict harness, independent trace audit, source replay, native geometry
checks, and manual HTML/SVG screenshot review on 2026-10-24. Its isolated subject
was the 18-file runtime digest
`eaab7a3ee1f03faeb9b6cb0b215edecc64c2fa8d06ec37686022ac8914ae9d8d`.
The model was `openai-codex/gpt-5.6-sol`, retaining the recorded Spark
unavailability exception. This is one scoped contract result, separate from the
earlier eight-attempt cohort; the skill remains `validating`.

Run `uv run --script projects/reflex-xy/scripts/run_errorbar_caps_pi.py` to see the
declared harness command and retained one-attempt controls; the runner refuses
to replace the existing run. The task prompt is
[`reflex-xy-capabilities-errorbar-caps.md`](../pi-prompts/reflex-xy-capabilities-errorbar-caps.md).
The harness used `--mode json --strict`, the runtime profile, all six exact
`--expect-output` paths, and the normal disabled ambient context/skill discovery
options. The source declares `xy==0.0.8` in PEP 723 metadata and regenerates both
palettes' HTML/SVG files with `uv run --script app.py`.

Independent native checks found six shafts, twelve horizontal caps, and six
central circles per palette, with the original supplied centers and asymmetric
lower/upper boundaries. The agent chose `cap_size=0.16` in perpendicular data-axis
units: the full cap span is 0.32 of the one-unit observation gap. Both variants
have identical geometry and dimensions, exact canonical paints, and visibly
different red/blue measurement ink. All range ends and caps fit inside the plot.
Both local HTML files rendered without external requests or JavaScript errors.
Manual review of both native SVG renderings and both desktop HTML screenshots
confirmed readable labels, distinct compact caps, and empty margins around the
data. The HTML uses a fixed 960-pixel width and therefore requires horizontal
scrolling on a 390-pixel viewport; responsive width was not required by this
focused task. The notes correctly distinguish supplied fictional ranges from
confidence intervals and describe offline Python callback limits.

Run `uv run --script projects/reflex-xy/scripts/verify_errorbar_caps_pi.py` for the
independent acceptance implementation. Two initial evaluator-only failures are
retained: SVGElement does not support Playwright's HTMLElement `inner_text`, and
Chromium stalled taking a full-page screenshot of a standalone SVG document.
The continuation used `text_content` and embedded the unchanged native SVG XML
in an empty local HTML document for capture. It did not relaunch Pi, change any
task source or output, or rerun source generation. The final continuation command
was `uv run --script projects/reflex-xy/scripts/verify_errorbar_caps_pi.py --resume-evaluator`.
Every original Pi output hash remained unchanged. No task defect, strict failure,
reroll, repair, or waiver was discarded.

The independent trace audit parsed all 3,203 event lines and reconciled all 29
tool calls with completions. It found zero tool errors, zero policy findings,
the required observed model, a prompt-first read, and independent size/hash
equality for all 18 copied runtime files. The additional trace command was
`uv run --script scripts/summarize-pi-json-events.py evaluations/runs/20261024-reflex-xy-errorbar-caps-contract-sol-1/events.jsonl --require-model gpt-5.6-sol --fail-on-invalid-json --fail-on-tool-error`.

Raw run evidence is retained under
`evaluations/runs/20261024-reflex-xy-errorbar-caps-contract-sol-1/`.
The frozen plan, snapshots, harness result, retained evaluator errors, final
independent check, geometry data, source replay, trace audit, manual review,
summary, and screenshots are under
`projects/reflex-xy/artifacts/errorbar-caps-pi/`.
