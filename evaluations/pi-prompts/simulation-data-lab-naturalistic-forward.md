Create a reproducible, analysis-ready simulation experiment for a call-center
staffing decision. The result must be an executable and validated data bundle,
not merely a chart or prose recommendation.

Treat `skills/simulation-data-lab/` as read-only. Write everything under exactly
`deliverables/call-center/`. Do not inspect parent directories, sibling skills,
repository documentation, evaluation files, or the network. Do not install
packages. Use the Python standard library and execute only the model you create.
Do not inspect the bundled Python script source; follow the documented commands
and contracts.
The command shell is already Bash: run commands directly and never wrap them in
`bash -lc` or use nested shell quoting.

Model one 480-minute operating day:

- Calls arrive as a Poisson process using exponential interarrival times.
- Service times are exponential with a mean of 8 minutes.
- Service is FIFO.
- Accept arrivals before minute 480 and finish accepted calls after closing.
- `overtime_minutes` is the final completion time minus 480, bounded below by
  zero.
- Generate complete arrival and service sequences independently of the staffing
  scenario. Derive separate, stable named random substreams for arrivals and
  service from the assigned run seed so common random numbers remain meaningful.
- Declare top-level `timeUnit` as `minute`.

Compare `three-agents` as the baseline with `four-agents` as the comparison. Use
three design points: `weekday` with arrival rate `0.30` calls per minute,
`low-load` with arrival rate `0.10`, and `surge` with arrival rate `0.42`. Put
the 8-minute mean service time in every design point as
`service_mean_minutes`, unit `minute`, source type `assumed`; do not hard-code
it in the model. Use 60 replications per cell, root seed
`4102026`, `uncertaintyMode=stochastic`, and `paired-across-scenarios`.

Record replication-level outcomes `mean_wait_minutes`, `p95_wait_minutes`, and
`overtime_minutes`, all in minutes. Add diagnostics for nonnegative waits and
overtime, finite outcomes, and complete customer accounting.

Declare one confirmatory hypothesis `h1-wait`. Its exact estimand is:

`paired mean difference in mean_wait_minutes (four-agents minus three-agents)`

Use a structured `scenario-contrast` analysis with `mean-difference`, baseline
`three-agents`, comparison `four-agents`, primary design point `weekday`,
challenge design points `low-load` and `surge`, paired sampling, normal
approximation, interval level `0.95`, and `all-design-points` aggregation. The practical threshold is
unit `minute`, operator `le`, value `-3`. The narrative decision rule must agree:
support only when every primary and challenge interval has a high endpoint at
or below `-3`; challenge when any low endpoint is above `-3`; otherwise report
inconclusive. Mark external validation as required and identify the uncalibrated
arrival and service distributions as assumptions.

Run the skill's planner and runner, then run its automatic hypothesis analyzer.
Do not hand-author or edit inferential numbers or statuses. Finally run the
bundle validator and write a short `analysis/conclusion.md` that reports each
design-point estimate, interval, MCSE, threshold decision, failed-run count,
strongest challenge result, limitations, and need for external validation.

After writing `experiment.json` and `model.py`, follow the lifecycle exactly:

1. Run the documented `plan` command exactly as shown in `SKILL.md`.
2. Run the documented `run` command exactly as shown in `SKILL.md`.
3. Run the documented analyzer command exactly as shown in `SKILL.md`, without
   adding an output flag or editing its generated result.
4. Run the documented validator command exactly as shown in `SKILL.md`, using
   the required validation-report path.
5. Read the generated hypothesis result and validation report, then write the
   conclusion once. Do not modify the model or spec after planning, and do not
   run extra shell probes or ad hoc verification scripts; the evaluation harness
   checks the required files.

These exact non-empty files are required:

- `deliverables/call-center/experiment.json`
- `deliverables/call-center/model.py`
- `deliverables/call-center/design/run-plan.csv`
- `deliverables/call-center/design/scenario-factors.csv`
- `deliverables/call-center/design/design-point-parameters.csv`
- `deliverables/call-center/design/plan-manifest.json`
- `deliverables/call-center/data/runs.csv`
- `deliverables/call-center/data/outcomes.csv`
- `deliverables/call-center/data/observations.csv`
- `deliverables/call-center/data/events.csv`
- `deliverables/call-center/data/diagnostics.csv`
- `deliverables/call-center/analysis/summary.csv`
- `deliverables/call-center/analysis/explore.sql`
- `deliverables/call-center/analysis/hypothesis-results.json`
- `deliverables/call-center/analysis/conclusion.md`
- `deliverables/call-center/data-dictionary.json`
- `deliverables/call-center/execution-manifest.json`
- `deliverables/call-center/validation-report.json`

The validation report must have `ok: true`, `releaseEligible: true`, and
`executionStatus: complete`. Keep the copied skill unchanged.
