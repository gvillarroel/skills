# Procedural development observations — 2026-09-26

These are development-only observations, outside every candidate and runtime
agent workspace. They must not include private validation feedback.

## First complete generation

Native generation: `evaluations/runs/svp3/generation-000/`. The unchanged guide
completed 18/18 trials without errors, with visual-proxy mean 0.508428. Candidate
`p` completed 17 evaluable trials and one agent tool failure. Its population
fitness is zero because it is unqualified; the engine's mean including the
unavailable trial's aggregate accounting is 0.488159. Do not present that as a
complete 18-trial visual-quality estimate.

All 36 generated outputs, including the unscored artifact, were rendered in
`generation-000-review/`. The input/model/tool/integrity audit passes 35/36 and
retains the one explicit tool failure. No source SVG was exposed to either arm.

Observed visible behavior:

- Robot heads remain recognizable in both arms but differ markedly from the
  reference's proportions and dark silhouette. The short prompt does not fix
  every such choice. No source contour or reference coordinates may be learned
  as a required construction.
- The organic ring case is weaker in the procedural arm: repeated thin loops
  distract from the broad central opening, and one variant crosses that opening.
  Some baseline variants also overcomplicate it. This supports checking the
  dominant opening and occupied shape, not copying the source's curve count.
- HUD strips generally read as horizontal technical ornaments. Some add small
  unrequested ticks or change the side of the diagonal accent; unspecified
  geometry is not automatically a semantic failure.
- Two procedural industrial labels have dark filled bodies that hide the
  information and barcode; one also overlaps header text. They passed static SVG
  validity and obtained nontrivial visual scores. Neither trace ran a render.
  The procedural label that rendered and inspected its preview is visibly
  readable. This is concrete evidence that validity and similarity do not
  establish visibility of the requested content.
- Wave drawings are valid illustrative curves but differ in frequency, offset
  and annotation from the source. The brief does not specify the reference's
  exact cycle count; do not tune a generator default to that count.
- Space ornaments are recognizable sharp silhouettes in both arms, with large
  compositional differences from the reference. The source's exact arrangement
  is not a hidden requirement of the general human request.

## Accepted second-generation hypothesis

Candidate `q` changes only the rendering paragraph in SKILL.md. The executable
renderer command with `python` is now primary when dependencies are installed;
`uv` is a conditional fallback. The agent is told to use the documented helper
instead of guessing low-level library entry points.

Primary native evidence:
`vector-004--eb6eabbcb9ca2ad4__tBAg39x` tried importing the nonexistent
`resvg_py.svg_to_png`, raised an ImportError and failed the strict tool gate.
The public result/trace hashes and exact parent/child files are frozen in
`evaluations/runs/svp3/q-mutation.json`. The two unrendered industrial labels
provide additional observational support for making the available entry point
unambiguous; they do not establish that the wording change will fix rendering
adherence. No executable geometry, prompt, score, image or gate changed.

The second candidate receives exactly 18 new native trials on the same public
cohort and uses the original contemporaneous baseline for comparison. The first
candidate, its failure and all its outputs remain unchanged. The private gate
stays closed during this work.

## Completed revision and forward review

The native population analyzer selected `q`: 18/18 valid trials, no execution
errors, verified provenance, and mean 0.531102 versus the unchanged baseline's
0.508428 (+0.022674, +4.46% relative). All six task-level means increased, but
three repetitions per task and a proxy reward do not establish significance or
broad style equivalence. The candidate used the renderer and opened its preview
in 12/18 development trials; the baseline did neither. No development trial
called the scaffold generator. The measured bundle effect therefore cannot be
attributed to generator use. Mean reported trace tokens were 23,511 for `q`
versus 9,126 for the baseline; these are not billed-token or cost estimates.

All 18 revision outputs and their 18 baseline counterparts were visually
inspected in `evaluations/runs/svp3/revision-review/`. Revision labels have
visible content rather than the first candidate's obscuring black slabs,
although the third label's secondary text is tiny at reduced size. Robot
proportions remain simplified; the organic rings use thin overlapping loops
instead of a strong filled contour; some HUD variants add stray accents. Wave
and space compositions remain plausible original interpretations with clear
differences from the source. No hidden cycle count or original contour became
a requirement. These findings are retained as limitations, not silently passed
as reference equivalence.

Seven prospectively registered unforced forward controls passed their automatic
checks. Direct inspection of all six generated previews also passed the broad
human briefs: the three coffee-service flows have the exact four editable
labels, correct order and clear arrows; the three vertical emblems separate a
thin wireframe globe above a smaller solid radial mark. The third emblem uses
curved asymmetric rays, which the brief permits. No output is clipped. The
unrelated Python explanation did not read the skill or create an artifact.
Only two forward cases ran the renderer and only one opened its preview, so
render-review adherence is still incomplete. No forward case called a scaffold.

The candidate was frozen by digest before the independent gate. These public
observations are final; no private feedback may be appended here or used for
further mutation in this study.
