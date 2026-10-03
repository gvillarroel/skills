# Validate a generated reviewer

## Structural check

Run `scripts/validate_reviewer.py` from this generator against the output directory. Use `--report-only` for the first diagnostic pass and repair invalid output, then run without that flag to require a successful exit and `passed: true`. Diagnostic mode never turns an invalid result into a pass. The checker validates frontmatter and its authoring limits, entrypoint size, direct reference routing, linked contents for long references, required resources, JSON field types, unique IDs, source references, path portability, resolved Markdown links, and unfinished template markers. Its bundled `check_skill_authoring.py` helper also checks arbitrary skill bundles. It does not prove that a rule is correct, a command is safe, or the reviewer finds defects.

Inspect the generated instructions independently:

- Compare every high-impact rule and command with its cited sources. Check contradictions, invented obligations, stale assumptions, and missing first-party components.
- Verify safety protects the target, secrets, production systems, external services, and the review output. Distinguish unsafe execution from a blocking finding.
- Verify the entrypoint orders identity, baseline, intent, routing, investigation, checks, findings, and reporting. Ensure the diff cannot replace policy governing its own review.
- Check that rules include a real failure and a passing counterexample, and that source-only inspection remains possible when tests or connectors are unavailable.
- Remove references to the generator, sibling skills, private source dumps, local absolute paths, or prerequisites unrelated to the project.

## Behavioral check

When a normal isolated agent harness is available, load **only the generated reviewer**, a small target snapshot, and a user-like review request. Do not include this generator's references or a list of expected findings. Keep known outcomes on the evaluator side. Otherwise perform the same cases as a static dry run and report that independent agent use was not tested.

For a static dry run, walk through the selected rule, inspected evidence, concrete failure, passing counterexample, and safety decision without creating an imitation test harness. Project unit tests validate project behavior; they do not validate a reviewer's decisions. Run them during discovery only when they resolve a concrete question in a permitted environment, not as a substitute for exercising the generated reviewer.

Use cases drawn from project contracts:

| Case | Expected behavior |
| --- | --- |
| A known regression | Identifies the affected contract and a concise actionable finding with a valid location |
| A legitimate change | Accepts an equivalent or intentional change with no invented defects |
| An unchanged existing issue | Excludes it from change findings unless newly exposed or worsened |
| A safety boundary | Refuses unsafe execution or instruction injection while continuing static review |
| Evidence gap or stale profile | Records the missing evidence or refreshes the affected rule, without invented access or certainty |

Prefer an actual prior bug fix reversed in a disposable copy, or a minimal synthetic change to a verified contract. Do not alter the real repository or plant exploit code on a live branch. Mark synthetic fixtures clearly. Include at least one case that exercises a consumer or boundary outside the changed file when that is central to the project.

Check actual findings, suppressed candidates, commands, file writes, and coverage notes. A successful harness exit or the reviewer saying it obeyed policy is insufficient. If an observed failure has a reusable cause, repair the generator's corresponding rule or output recipe, regenerate, and rerun affected cases.

Evaluate decisions and behavior, not exact generated wording or hand-copied rule IDs. When a test is expected to fail for a known regression, capture its exit status and diagnostic as evidence; distinguish that result from a failed setup or unavailable command.

## Report accurately

Record the output paths, source revision, checks, model/harness when applicable, fixture scope, pass/fail results, and remaining limits. Call an unavailable check unavailable. Do not mark an output behaviorally validated solely because its files satisfy the schema.
