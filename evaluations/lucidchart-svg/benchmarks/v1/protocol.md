# Lucidchart SVG public development benchmark v1

Evaluate the current skill on fresh small tasks beyond its earlier two-node acceptance fixture. This is a public, reproducible development benchmark, not a private holdout or evidence of live Lucidchart rendering fidelity.

## Subject and isolation

Freeze the runtime-only `lucidchart-svg` bundle, all eight prompts, the independent artifact validators and runner controls before any trial. The subject is the 21-file runtime with SHA-256 `0e4d5c69add73792b268cb0890edbb48d39c573e1fdb9a908ba017ad50679f93`. Acceptance examples, sibling skills, repository instructions and earlier results are excluded from every copied workspace. Skill resources remain read-only. Inputs come entirely from each task prompt; outputs have exact workspace-relative paths.

The observed evaluation model is `openai-codex/gpt-5.6-luna`, high thinking, under the existing dated backlog exception after Spark account/provider rejection before tools. The exception changes the model, never isolation, exact paths, zero-error policy or artifact standards. No network or authenticated service is available to the tested agent. Repository Pi tooling uses `--mode json --strict`; the command-contract case additionally requires its exact shell command.

## Predeclared cases and thresholds

| Case | Taxonomy | Fresh trials | Required joint passes | Main question |
| --- | --- | ---: | ---: | --- |
| contract | contract-smoke | 1 | 1 | Can the rich graph compiler retain explicit table/container, annotation and relationship contracts? |
| geometry | naturalistic-forward | 3 | 2 | Does explicit SVG conversion correctly compose nonzero viewBox and ordered positive transforms, preserving each object's styles? |
| relations | generalization | 3 | 2 | Are declared connector endpoints, orthogonal turns, labels and marker adaptations retained with correct source attribution? |
| asset | naturalistic-forward | 3 | 2 | Does a visual-asset route preserve rich artwork bytes and qualify native editability and parser/rendering limits? |
| boundary | boundary-recovery | 1 | 1 | Does blocked resource/active content cause an accurate local diagnosis without invented export/import success? |
| ambiguity | boundary-recovery | 1 | 1 | Can the skill preserve eligible artwork while declining to invent topology from crossing strokes? |
| semantic | generalization | 3 | 2 | Does element selection follow supplied BPMN and relationship roles, with literal text and correct native properties? |
| generated | generalization | 3 | 2 | Are distinct hierarchy data, sequence markup and all four generated-layout families preserved without invented geometry? |

The total is **18 new trials**. The denominator includes every planned trial; absent, failed and unreviewed trials are never counted as passes. Case acceptance requires all planned repetitions to finish and the predeclared joint threshold. Report trial-level and case-level results separately. Three repetitions estimate repeatability on these fixed public inputs; they do not establish broad population accuracy or disjoint holdout performance.

## Joint grading and independent evidence

Run static gates and the 122 deterministic skill tests before trials. Every joint pass requires strict harness success, exact outputs, the frozen model/payload, valid events, zero tool errors, independent artifact assertions, an acceptable read/command surface and a direct manual task/narrative review. Evaluator reports remain outside copied workspaces. Artifacts and failed attempts are never repaired after a run.

Validators import no skill implementation and do not rerun its builders to derive answers. Their oracles come from supplied literal data, formal roles and hand-derived geometry. Verify actual ZIP entries/document bytes, native fields, labels, styles, memberships, endpoints, routed points and generated records. Report/package equality is a consistency check alongside independent expected values. Require status notes but do not grade prose through keywords; the reviewer compares concrete claims with source/output/trace evidence.

Before freezing, challenge graders with separate mutated copies. Check wrong coordinates, source bytes, stroke attribution, labels, topology/routes, native semantics, table/lane properties, generated records/parents, page clipping and fabricated output. Keep these negative controls separate from model trial scores. Use a browser to inspect locally renderable SVG artifacts; source/copy appearance does not simulate Lucid rendering.

Record manual reviews as `manual-benchmark-review.json` beside each workspace: `passed`, `read_surface_passed`, `commands_passed`, `artifact_review_passed`, `narrative_review_passed`, `case`, `run_id`, `findings`, and `evidence_boundary: local-only`. The aggregate requires all component booleans to be true.

Retain every failure and classify it as skill, agent, validator, harness, infrastructure or external-service. Do not silently rerun a failure, select only favorable outputs, pool old passes or adjust thresholds after observing scores. A subject fix requires a separate digest and a clearly labeled new cohort; these public cases may guide development but never become a claimed untouched validation split.

## Resource and scalability measurements

Report observed per-trial Pi wall time and event token totals with coverage. Cached input is included in the model's reported totals; do not present those values as unique prompt size or billed tokens. Trials may run with four concurrent workers, so latency is observational. Cost is unavailable unless the provider actually reports it; do not infer a price or a no-skill baseline improvement.

Separately run the deterministic performance probe for SVG inspection, native compilation and generated hierarchy sizes. Each workload uses one warm-up and three fresh measured outputs, validates counts and unchanged source, and checks deterministic package bytes where applicable. Time includes `uv`/process startup and local machine conditions. These timings establish this machine's observed scaling, not remote import/rendering throughput or a universal performance guarantee.

## Reproduction

```sh
uv run --script evaluations/lucidchart-svg/benchmarks/v1/run_benchmark.py freeze
uv run --script evaluations/lucidchart-svg/benchmarks/v1/run_benchmark.py run --run-prefix 20261007-lucid-benchmark-v1 --jobs 4 --output evaluations/runs/20261007-lucid-benchmark-v1/cohort.json
uv run --script evaluations/lucidchart-svg/benchmarks/v1/run_benchmark.py summarize --runs evaluations/runs/20261007-lucid-benchmark-v1/cohort.json --output evaluations/runs/20261007-lucid-benchmark-v1/summary.json
uv run --script evaluations/lucidchart-svg/benchmarks/v1/run_performance.py --output evaluations/runs/20261007-lucid-benchmark-v1/performance.json
```

The versioned manifest already exists after the initial freeze; do not overwrite it. On another platform, working-tree line endings can change the raw bundle/control digest. Run `run_benchmark.py identity` to obtain the current exact runtime digest, then declare a distinct subject manifest with `freeze --manifest <new-manifest.json> --subject-sha256 <observed-digest>`. Pass that manifest explicitly to every run/summarize command. Keep such alternative manifests under ignored run storage, label the new raw subject and never pool it with the original frozen cohort. Do not normalize tested files or weaken verification. Use a new run prefix and output path for every rerun; summarization becomes final only after evaluator manual reviews exist.

## Service coverage boundary

Authenticated SVG export, formal custom-SVG insertion, Standard Import parser acceptance, rendered fonts/icons, label editing and connector following remain **unverified**. Correct local JSON or a `.lucid` ZIP does not establish those behaviors. Keep the skill's backlog status `validating` while that boundary remains open; never turn structural counts or benchmark pass rates into an overall visual preservation percentage.
