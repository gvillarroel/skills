# Jev expert technical excellence evaluation

The active evaluation now grades the requested drawing and its technical finish.
Reference resemblance contributes no reward. The complete public retrospective
scores the original baseline at **92.0833/100** and the current procedural skill
at **94.1667/100**, a descriptive difference of **2.0833 points** across 18 outputs
per arm. All 36 original SVGs were assessed without regenerating them.

The canonical skill remains unchanged and experimental (`validating`). These
public results do not establish independent promotion or broad generalization.

## Active contract

- [Active evaluator configuration](../../projects/svg-brief-design/evaluation/active-evaluator.json)
- [Rubric 3.0.0](../../projects/svg-brief-design/evaluation/technical-excellence-v2/rubric-v3.json)
- [Expert Jev instructions](../../projects/svg-brief-design/evaluation/technical-excellence-v2/jev-expert-v4.json)
- [Visual observer instructions](../../projects/svg-brief-design/evaluation/technical-excellence-v2/visual-observer-prompt.txt)
- [Compact measured results](jev-excellence-20260926.json)
- [Local gallery with all drawings, ratings and observations](../runs/svgq2/review-v3/index.html)

Jev is the decision maker, configured as an expert vector designer and technical
art director. The observed model was `typesafe/jev-1.13-20260917`, requested through
the existing `typesafe/jev-1.13` OpenRouter integration. Its native categorical
answers choose one of five concrete quality levels per dimension.

| Dimension | Weight | Full-credit requirement |
| --- | ---: | --- |
| Brief adherence | 35% | Clearly fulfill the actual requested subject, relationships, content and style |
| Geometric finish | 25% | Intentional contours, joins, openings and repeated forms |
| Composition | 20% | Appropriate hierarchy, proportions, spacing, margins and negative space |
| Legibility | 20% | Clear defining forms and any intended text or annotations |

The reward is `sum(weight * selected_level / 4) / 100`. Display multiplies it by
100. Full credit is attainable; it does not require extra ornament, a particular
tool, the reference silhouette, an unspecified wave count or an exact direction.
Native choice confidence is retained separately. A value below 0.3 flags review;
it does not multiply quality. Unknown evidence produces no aggregate reward.
An explicit fundamental brief failure (`level_0`) is a decisive zero, even if an
unrelated aesthetic dimension is unknown. Essential missing content at a brief
level below two caps the remaining weighted reward at 0.49.

Absent, unsafe, invalid or empty SVGs receive zero before model calls. Static
checks enforce the editable vector contract, finite viewBox, two-megabyte limit,
and absence of scripts, raster images and external resources. Render diagnostics
measure actual text visibility, intersecting text ink, margins, color and nearby
overflow; they are interpreted against the request rather than automatically
penalizing intentional overlaps or organic drawing.

## Evidence reaching the judge

[Jev accepts text rather than image inputs](https://docs.typesafe.ai/models).
An initial source-only configuration passed simple controls but saturated the
eligible existing outputs at 100. Visual inspection showed that this missed
relevant distinctions. That failed discriminative screen is retained.

The active pipeline renders each complete SVG and uses exact
`openai-codex/gpt-6-luna`, medium reasoning, Pi 0.84.2 and SSE as a **factual visual
observer**. It receives the original request, a request-only checklist and the
render. It has no tools and supplies observations rather than grades. Jev makes
the final judgments from those observations plus deterministic measurements.
Complete source is included as a crosscheck when it fits the fixed 12 KB limit.
The 83,610-byte SVG was assessed through its full render and original-source
measurements; its paths were neither truncated nor simplified.

The observer is fallible. During calibration it overlooked a black square; exact
source and render measurements provide a crosscheck. Its text and the image it
saw are retained for every call. All 51 observer receipts confirm an actual image
input, the requested model, and no tool use. Neither model receives purchased
reference artwork, historical similarity scores, generation traces, skill text
or arm identities. Jev's categorical distribution and confidence are preserved;
[native Choice semantics](https://docs.typesafe.ai/primitives/choice) are not
misrepresented as continuous expected scores.

## Current results

| Public task family | Original baseline | Current skill | Difference |
| --- | ---: | ---: | ---: |
| Android head | 100.00 | 100.00 | 0.00 |
| Circular frame | 74.17 | 78.33 | +4.17 |
| HUD bar | 92.50 | 97.92 | +5.42 |
| Industrial label | 93.33 | 94.58 | +1.25 |
| Periodic graph | 92.50 | 94.17 | +1.67 |
| Space insignia | 100.00 | 100.00 | 0.00 |
| **All 18 outputs per arm** | **92.08** | **94.17** | **+2.08** |

Full-credit counts are 10/18 for the baseline and 12/18 for the current skill.
There are four review flags: three baseline outputs and one current graph.
Their numeric ratings remain visible rather than being excluded selectively.
There are no unscored current outputs in the final version.

The current space insignia ending `iZfrKPH`, formerly the lowest resemblance
score, receives 100 under the technical contract. The periodic graph ending
`6Rsua8R` also receives 100. The ring ending `SDPAF9u`, formerly highest by
resemblance, receives 70: Jev assigns level two to brief adherence and geometric
finish given the observations about interlacing and crossings. This is an
auditable judgment under this rubric, not a claim that the drawing has one
objectively correct artistic rating.

## Calibration and integration evidence

The final pipeline passes all **17 original controls**: valid alternatives of
different sizes and wave counts, clipped geometry, wrong subject/color, invisible
or overlapping text, absent required features, inert injection, malformed XML,
external images and empty output. Full-credit controls reach 100. The same
acceptance inequalities were retained throughout. Sixteen deterministic tests
exercise failure gates, uncertainty, confidence separation, numeric boundaries,
visibility, injection handling and visual evidence shape.

Configuration development and all unsuccessful stages are preserved under
`evaluations/runs/svgq2`. Expected-score v1 passed 4/17 controls; categorical v2
passed 17/17 but saturated the existing population; visual v3 passed 15/17; the
source crosscheck passed 16/17; the explicit fundamental-brief gate completed the
final 17/17. The final observer prompt, Jev job, rubric and bundle were frozen
before current visual observation and scoring. Because public outputs had
already informed the source-only failure diagnosis, this is an evaluator
development retrospective rather than a sealed validation cohort.

The native Harbor integration uses
[SvgExcellenceVerifier](../../projects/svg-brief-design/scripts/harbor_svg_excellence.py).
It runs on the trusted host after generation. Only the SVG is downloaded from
the agent environment. Evaluator credentials, code and observations are never
uploaded to the generation container. A one-task Oracle integration run completed
with `artifact_valid=1` and `technical_excellence=1`, zero errors and no retries.
The stock Harbor reporter independently accepted the native artifacts:
[native report](../runs/svgq2/native-probe-report/final-report.md).

The first Oracle fixture had a Windows CRLF shebang and exited 127 before
creating an SVG or calling either model. Its zero result is preserved. A new
fixture version with LF endings supplied the successful integration check; no
generated SVG outcome was retried. A separate checkpoint-key collection repair
reused original validated Jev responses and made no additional model calls.

New public task definitions and matched future job configurations live at:

- `evaluations/runs/svgq2/ds/` — six public tasks, no reference artwork.
- `evaluations/runs/svgq2/future-job.json` — current skill, three attempts per task.
- `evaluations/runs/svgq2/future-baseline-job.json` — immutable original baseline,
  otherwise identical conditions.

Future optimizers must consume the active configuration's
`harbor.rewardKey=technical_excellence`, retain `artifact_valid=1` as a required
constraint, and explicitly load the declared custom verifier. Historical
`svp3` and earlier job configurations and rewards remain immutable. The legacy
standalone source-only verifier entrypoint is not the active v3 entrypoint.

## Reproduction and checks

On Windows, use the scripts' declared `uv` dependencies. For the native Harbor
run, the existing Harbor 0.18.0 WSL runtime was used with project-local renderer
dependencies copied from the pinned verifier image, without changing that
runtime environment. Set `PYTHONDONTWRITEBYTECODE=1`, include
`evaluations/runs/svgq2/python-deps` and `projects/svg-brief-design/scripts` in
`PYTHONPATH`, and supply the existing `FOX_PI_AUTH` and `OPENROUTER_API_KEY`
environment variables without printing or persisting their values.

```text
uv run --script projects/svg-brief-design/scripts/test_svg_excellence.py
python projects/svg-brief-design/scripts/run_excellence_probe.py --config probe-lf-job.json --seal harbor-integration-lf-lock.json --tag probe-lf
python <harbor-run-results>/scripts/report_harbor_jobs.py evaluations/runs/svgq2/jobs/probe-lf --reward-key technical_excellence --pass-threshold 1 --output-dir <new-report-directory>
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

Live-run commands require a fresh output directory; the recorded probe is
already completed and must not be overwritten. Gallery checks verified all 36
images loaded and the current-skill filter displayed 18 cards. Repository gates
passed. A digest audit confirms all 36 original native generation results, all
36 original SVGs, and the frozen evaluator files remain unchanged.

Across configuration search, both retrospective versions and the integration
probe, Jev made **131 accepted calls**, reporting **$0.020802348**, 495,294 input
tokens and 41,974 output tokens. The observer made **51 calls**, reporting 84,135
total tokens. Its dollar cost is unavailable through this account-backed Pi
transport; zero-valued cost fields are not treated as a verified free service.

The rubric still has a ceiling: 22/36 outputs receive full categorical credit.
Confidence is not calibrated accuracy, and the visual observer uses the same
model family as generation. The sample contains six public task families and
three repetitions per arm. Private cohorts were not opened, and neither scores
nor qualitative inspection justify an independent skill-promotion claim.
