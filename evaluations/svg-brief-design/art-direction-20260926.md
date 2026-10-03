# Curated SVG art-direction evaluation

Historical record: this evaluator was superseded by [purpose-specific technique v6.3](technique-20260926.md) after the user identified insufficient discrimination of print character, integrated voids, circular junctions and label compactness. The results and interpretations below preserve the earlier contract; the later report records the corrected purpose and brief.

The v5.2 development evaluator, **`curated_design_quality`**, compares anonymous artwork pairs against a curated quality anchor under an explicit editorial graphic-asset purpose. The eighteen existing current-skill outputs score **68.53–70.19** on its bounded scale. Matching the curated anchor is defined as **90**. That 90 is a scale convention, not an independently measured absolute rating of purchased artwork.

Jev's separate overall judgments prefer the original in **10/18** comparisons, report parity in **4/18**, and abstain in **4/18**. No overall judgment prefers the generated drawing. Individual dimensions can favor a generated drawing; one circular ornament reaches 91. Purchased artwork is not forced to win every comparison.

The [active configuration](../../projects/svg-brief-design/evaluation/active-evaluator.json), [compact results](art-direction-20260926.json), and [local comparison gallery](../runs/svg-art-v5/review-v5.2/index.html) are the current deliverables. The canonical skill and local installation retain the same eight files and experimental `validating` status. Changing the evaluator does not establish skill improvement or independent promotion.

## What was missing

The previous v3 rubric awarded full credit when it found no specific defect in brief adherence, geometry, composition or legibility. Twelve of eighteen current outputs reached 100; their mean was 94.17. Recognizable subject matter, clean paths and regular spacing were insufficient evidence of the professional character the user wanted.

An initial broader v4 rubric also failed. Absolute categories clustered around 70–75: originals averaged 72.17 and current outputs 71.33. Pairing their independently written critiques preferred the original in only one of six families, despite perfect order agreement. Those runs remain preserved and were never activated.

The important correction was the review context and direct visual comparison. An expressive science-fiction/editorial/vintage-scientific asset pack requires authored mass, silhouette, internal voids and controlled tension. Generic app-icon smoothness, precise chart behavior or dashboard readability are insufficient. Simplicity, geometric restraint, asymmetry and organic marks can each be excellent when their relationships serve the brief.

| Dimension | Weight | Observable evidence |
| --- | ---: | --- |
| Silhouette and design intent | 20% | Expressive proportions, character, meaningful changes of direction |
| Optical balance and negative space | 20% | Black mass distribution, breathing room, shaped internal openings |
| Shape language and rhythm | 15% | Related curvature and angles, repetition with controlled variation |
| Contour and junction finish | 20% | Terminations, tapers, attachments, cutouts and unintended tangencies |
| Hierarchy and scale | 10% | Primary and supporting forms, coherent smaller-size reading |
| Art direction and restraint | 15% | Appropriate mood, integrated detail, consistent visual language |

These questions draw on balance, emphasis, rhythm, unity, proportion and figure-ground relationships in the [Hammer Museum graphic-design guide](https://hammer.ucla.edu/fileadmin/media/EDU/PDFs/Teacher_Guide_GraphicDesign.pdf). They are observable design principles, not a universal formula for beauty.

## Evidence, model and scale

Jev remains the final decision maker: requested `typesafe/jev-1.13`, observed `typesafe/jev-1.13-20260917`. [Jev is text-only](https://docs.typesafe.ai/models), so an isolated `gpt-6-astra` critic at high reasoning effort views paired complete renders plus thumbnails and supplies concrete comparative evidence. The critic has no tools and supplies no grades. Jev receives the brief, purpose and critique through the existing typed decision API.

Neither model receives purchase status, author, treatment identity, previous score, source filename or which side is expected to win. A/B position is deterministically assigned; six repeated comparisons reverse the order and collect a fresh critique. A renderer standardizes viewing size and fonts. No pixel, path or silhouette similarity contributes to the reward.

Each dimension places the candidate clearly below (50), slightly below (75), comparable (90), slightly above (95), or clearly above (100) the anchor. The six weights produce artistic quality. Brief fulfillment is a separate gate: wrong subject scores zero, a missing essential caps the reward at 49, and a supported secondary mismatch caps it at 79. Invalid, unsafe or empty SVGs fail before inference. Decoration and source complexity earn no points by themselves.

An unresolved artistic dimension retains its entire possible **50–100** band. The report propagates that interval without inventing a point estimate; Harbor uses its lower bound as the conservative optimization reward. This describes unresolved categorical choices, **not a statistical confidence interval**. Unknown candidate subject yields no numeric reward. Overall preference is a separate diagnostic, not a seventh weighted dimension. Confidence is also separate and never multiplies quality points.

Do not promote a selected skill automatically from this score. Resolve material uncertain dimensions or global preferences by human review and require an untouched disjoint evaluation for promotion. Fifteen of eighteen generated records carry a review flag, including low confidence in any one of nine decisions. Two have unresolved weighted dimensions; four have an unresolved overall preference. The directional calibration is useful, but fine individual rankings remain less reliable.

## Results and controls

All eighteen existing outputs across six public development families were retained. Purchased originals serve only as evaluator-side quality anchors. Six cropped-original controls and four original synthetic fixtures are also retained. No private cohort was opened.

| Family | Generated mean or range | Overall original preference |
| --- | ---: | ---: |
| Android head | 51.67–55.00 | 3/3 |
| Circular ornament | 89.67 | 0/3; all parity |
| HUD bar | 50.50 | 3/3 |
| Industrial label | 68.50 | 2/3; one parity |
| Vintage oscillation | 82.17 | 1/3; two unresolved |
| Space insignia | 68.67–75.33 | 1/3; two unresolved |

The recurring distinction is integration. The generated android places familiar robot symbols inside an outline; the original combines a heavy forehead, eye voids, stretched neck and directional cuts to produce an unsettling character. The HUD original coordinates terminal slashes, a stepped opening and unequal black weight; generated versions often append crowded marks to an arrow-like frame. Industrial labels benefit from a stronger overall proportion and relationship between typography, solid areas and empty space.

The circular ornament is a useful counterexample. Its brief requests soft interlacing, which the airy generated network satisfies. The purchased example has stronger black mass and directional tension. Calling the former inferior in every respect would confuse quality with a prescribed aesthetic. Likewise, regular scientific notation and gestural organic ink can legitimately serve different interpretations of the wave brief.

All retained acceptance thresholds pass, using the **upper** uncertainty bound for candidate quality and the worst possible interval distance for order stability:

- All 34 source artifacts accounted for through 32 pairs and the invalid pre-inference check.
- All six generated family means remain below 90 at their upper bounds; the ring's 0.33-point difference is practical parity.
- The mean gap is at least 19.81 points, exceeding the original 15-point rule.
- All six cropped controls score below 80.
- All six swapped-order score distances stay within 10 points; five of six global preference states agree. The space-insignia result remains uncertain.
- The rough synthetic HUD scores 55, wrong subject scores zero, invalid XML is rejected, and the native visible-identity control scores exactly 90.

Order controls are motivated by documented position and verbosity biases in [LLM-as-a-judge research](https://arxiv.org/abs/2306.05685). They do not prove human agreement or general aesthetic validity.

## Revisions and failure accounting

This is exploratory development calibration, not a preregistered confirmation study. v4, v5 and v5.1 decisions remain intact. Prompts, model jobs and source identities were frozen before each corresponding inference batch.

v5 introduced direct anonymous comparisons but left one weighted judgment unresolved and classified the wrong-subject fixture as merely incomplete. v5.1 clarified parity versus insufficient evidence and absent versus incomplete subject, uniformly across all 32 records. It corrected the subject control but retained abstentions. v5.2 adds bounded scoring using those same v5.1 judgments, with **no further model inference**. It preserves every decision and the original numerical acceptance thresholds. Uncertainty handling was designed after observing these failures; it must not be described as independently validated or preregistered.

One Astra stream terminated during incomplete JSON. Its partial text, receipt and events are preserved; one identical-input external recovery provided the first complete comparison. One Jev response failed the existing typed contract because its selected choice disagreed with its maximum reported probability. The original failed run and two accepted checkpoints are preserved; continuation reused those checkpoints, replaced only the invalid envelope, and made the 29 unstarted calls. Neither recovery repeated an accepted semantic result. Append-only amendments record exact limits.

Across exploratory configurations and integration, Jev made 111 HTTP attempts, accepted 110 envelopes, and reported USD 0.021619122. Astra made 67 attempts with 66 complete observations. Observer monetary cost is unavailable; zero cost fields from the signed-in account do not establish zero economic cost. The terminated stream underreports token use. See the [accounting record](../runs/svg-art-v5/accounting.json).

## Native integration and future generation

The frozen trusted-host verifier is `SvgCuratedVerifier`, Harbor 0.18.0. Its Oracle control uses two visibly identical synthetic HUDs with different SVG metadata. It completed with `artifact_valid=1.0`, `curated_design_quality=0.9`, no error, no retry, identical rendered pixels and parity on every design dimension. The [native final report](../runs/svg-art-v5/native-probe-report/final-report.md) records this integration control; it is not a skill-generation trial.

Purchased SVGs remain in an ignored, host-only evaluator bundle. They are never mounted in the generator environment, packaged with the skill, or published. The generator receives only the short natural brief plus this quoted Spanish quality introduction:

> Busco un recurso gráfico editorial con carácter propio y acabado de un pack curado: silueta expresiva, masas y vacíos bien trabajados y detalles integrados en el conjunto.

This states the desired purpose without exact paths, anatomy or layout. Both future baseline/skill jobs use the same six task definitions, introduction and sealed evaluator. Generation remains exact GPT-6 Luna with existing matched tools. Historical outputs predate the introduction; this reevaluation does not demonstrate improvement under the new contract. No new baseline comparison has been run with this reward.

The signal supports development toward designed silhouette, optical mass, shaped negative space and integrated detail. It should not teach copying anchor geometry or turning every task into one style.

## Reproducibility and checks

Versioned sources are under `projects/svg-brief-design/evaluation/art-direction-v5.2/` and `projects/svg-brief-design/scripts/`. Large immutable evidence is under `evaluations/runs/svg-art-v4/` and `evaluations/runs/svg-art-v5/`. The activation receipt binds the native result, eight unchanged skill files, previous evaluator and frozen lock. Bundle lock SHA-256: `96c738df42d976370833840d92b2de77705c3672317e238187863782ad292286`.

```powershell
uv run --script projects/svg-brief-design/scripts/test_svg_art_direction.py
uv run --script projects/svg-brief-design/scripts/test_svg_curated_pairs.py
uv run --script projects/svg-brief-design/scripts/test_curated_bounds.py
uv run --script scripts/validate-pattern-ids.py
uv run --script scripts/validate-skills.py
uv run --script scripts/test-skill-independence.py
uv run --script scripts/check-repo-payload.py
```

The 27 evaluator tests cover source-independent decisions, side mapping, brief gates, missing evidence, uncertainty propagation and confidence separation. Browser inspection confirms all 36 images load across 18 comparison cards without horizontal overflow. Original SVG hashes, generated artifacts and the eight-file canonical/local skill bundle remain unchanged.

Repository pattern, skill, independence and payload gates pass. Both future JobConfig files validate under native Harbor 0.18.0. Source syntax, frozen-input hashes, active-configuration binding and whitespace checks pass. The [validation receipt](../runs/svg-art-v5/validation-receipt.json) records these checks.
