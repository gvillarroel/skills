# Prospective evaluation design for short-brief SVG generation

Research date: 2026-09-26. Status: proposal only. This review browsed primary
papers and official research repositories; it installed nothing, made no judging
or generation model calls, changed no benchmark or reward, and accessed no
private tasks.

## Recommendation

Keep prompt adherence, reference resemblance, and artifact usability as separate
reported dimensions. Do not replace the frozen similarity reward with an
unvalidated multimodal score or combine the dimensions into a new scalar after
seeing the current candidates.

The motivating local observation is a label whose text became more observable
while reference similarity declined. The independent
[layout diagnostic report](layout-diagnostics-20260926.md) documents that result
and its limits. A recognizable, legible diagram can legitimately differ from a
specific reference; conversely, a visually similar picture can omit an explicit
requirement. The existing verifier's combined shape/style similarity should be
called **reference resemblance**, not semantic correctness or pure style.

## Primary-source findings

1. **TIFA** evaluates text-to-image faithfulness through questions derived from
   the prompt, using a visual question-answering model. Its reference-free,
   question-level approach supports interpretable checks of individual
   requirements. For these SVG briefs, a human-reviewed question set derived
   only from the short request is a useful design pattern. The paper does not
   validate those questions or its models on this monochrome SVG collection.
   [TIFA, ICCV 2023, official proceedings](https://openaccess.thecvf.com/content/ICCV2023/html/Hu_TIFA_Accurate_and_Interpretable_Text-to-Image_Faithfulness_Evaluation_with_Question_Answering_ICCV_2023_paper.html).

2. **VQAScore** measures the model probability of an affirmative answer to an
   image/prompt question and reports improved compositional alignment on its
   studied benchmarks. It is a plausible comparison metric in a future pilot,
   but a single whole-prompt score is less diagnostic than individual criteria.
   Its probability is not a calibrated probability that our SVG meets every
   requirement. [VQAScore, ECCV 2024, authors' project page](https://linzhiqiu.github.io/papers/vqascore/).

3. **GenEval 2 / Soft-TIFA** stores prompt primitives with associated questions
   and skill categories. Its official implementation distinguishes arithmetic
   aggregation of per-primitive soft scores from geometric aggregation for
   prompt-level evaluation. This supports retaining both individual failure
   categories and an explicit aggregation rule; it does not establish an
   appropriate threshold, aggregation, or judge for our illustrations.
   [GenEval 2, official research repository](https://github.com/facebookresearch/GenEval2).

4. **T2IScoreScore (TS2)** evaluates metrics against controlled semantic-error
   orderings. Its authors found that tested VLM-based metrics did not reliably
   outperform simpler feature metrics on challenging errors. This motivates
   testing the proposed judge on targeted SVG failures before relying on it for
   selection. A larger or newer multimodal model is not sufficient validation.
   [TS2, authors' NeurIPS 2024 paper record](https://arxiv.org/abs/2404.04251).

These sources motivate the design below; all SVG-specific procedures and
threshold proposals are our prospective methodological choices, not published
validation results.

## Concrete evaluation dimensions

| Dimension | Inputs and observations | Reporting rule |
| --- | --- | --- |
| Explicit brief adherence | Short user prompt plus rendered candidate. Review subject identity, explicitly requested parts, relationships, arrangement, and exclusions. | Criterion-level pass, fail, or uncertain with a visible explanation. Record coverage and uncertainty separately. |
| Reference resemblance | Candidate and reference rendered under the frozen verifier. Retain shape similarity and all style components alongside the existing combined score. | Preserve the native score and provenance. Do not treat differences in unspecified details as semantic failures. |
| Technical validity | Original SVG and fixed deterministic verifier. | Keep validity separate from visual and semantic scores. |
| Usability | Render at a declared intended size and a thumbnail. Check text occlusion, clipping, readable hierarchy, and meaningful diagram connections. | Report deterministic diagnostics plus blinded human review. The current ink intervention is not a calibrated legibility score. |

For a short request for a camera-aperture symbol made of angular pieces around
an opening, valid semantic criteria concern an aperture-like arrangement,
angular pieces, and the central opening. An exact blade count, exact coordinates,
or a border must not become requirements unless the user asked for them. Keep
the user's prompt short; the evaluator's criterion sheet stays outside the
generation context and the skill.

The semantic reviewer must not see the purchased reference, candidate identity,
skill text, or similarity score. The style reviewer can see the reference but
should receive a separate style/resemblance rubric. Text content extracted from
SVG elements may help deterministic checks; it cannot prove those letters are
visible. Unsupported scientific correctness or code decodability remains a
specialist check when the brief actually requires it.

## Prospective validation plan

1. Author a new pilot using independently created SVGs and short briefs, without
   opening the current sealed tasks. Freeze the briefs and explicit criteria
   before comparing candidate generators. Include symbols, labels, decorative
   diagrams, and illustrations, and keep development and test families separate.
2. Build a small controlled set with at least 24 briefs. For each brief, create
   cases crossing semantic correctness with reference resemblance: correct and
   similar, correct and stylistically different, incorrect and similar, and
   incorrect and different. Include hidden text, missing openings, disconnected
   endpoints, changed requested relationships, and extra unrequested features.
   Add harmless font, stroke, and canvas variations as invariance checks.
3. Have two blinded human reviewers independently annotate each explicit
   criterion and usability issue. Adjudicate disagreements and preserve the
   individual judgments. Treat this as a calibration pilot, not sufficient
   evidence of population-wide performance.
4. Compare a criterion-based VQA judge with whole-prompt VQAScore and a simple
   embedding baseline on the same development examples. Measure error-detection
   precision/recall, uncertainty coverage, human agreement, and controlled
   error ordering by family. Examine the style/semantic conflict cases directly;
   overall correlation alone is inadequate.
5. Freeze judge version, prompts, renderer, image resolutions, question sheet,
   aggregation, and any thresholds before evaluating the new disjoint test
   portion. Estimate uncertainty by resampling briefs rather than treating
   correlated variants as independent observations. Keep unstable or unsupported
   dimensions as human-reviewed diagnostics.
6. Only after that validation, preregister a future generator study. Prefer
   separate semantic/usability requirements and a reference-resemblance
   comparison over an improvised weighted total. Any future promotion rule must
   be declared before new outputs are observed and must use a fresh sealed gate.

No CLIP, VQA, multimodal-judge, or OCR result has been demonstrated valid for this
collection by this research pass. Current trial outcomes, rejected candidates,
private gates, and installed skill remain unchanged.
