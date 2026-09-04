Use the loaded `simulation-data-lab` skill to create and validate a minimal
deterministic simulation bundle.

Treat `skills/simulation-data-lab/` as read-only. Write all generated files
under exactly `deliverables/contract-smoke/`. Do not inspect parent directories,
sibling skills, repository documentation, evaluation files, or the network. Do
not install packages. Execute only the model code you create for this task.
Do not inspect the bundled Python script source; its documented command
interfaces and the data-contract reference are authoritative for this task.
The command shell is already Bash: run commands directly, never wrap them in
`bash -lc`, and do not use nested shell quoting. Use the bundled validator as the
authoritative final check instead of constructing an ad hoc multiline checker.

Create a fresh experiment with these fixed requirements:

- experiment ID `cost-contract-smoke`;
- phase `exploratory`, paradigm `custom`, and `uncertaintyMode=deterministic`;
- engine `python-standard-library` with version constraint `>=3.11`, and record
  the concrete installed Python version in `MODEL_METADATA`;
- root seed `20260903`, seed policy `independent-by-run`, and exactly one
  execution per scenario/design-point cell;
- one design point `demand-10`, containing `demand_units=10`, unit `item`, and
  source type `assumed`;
- scenario `baseline`, containing `fixed_cost=5`, unit `USD`, source type
  `assumed`;
- scenario `optimized`, containing `fixed_cost=3`, unit `USD`, source type
  `assumed`;
- one outcome `total_cost`, unit `USD`;
- `total_cost = demand_units + fixed_cost`;
- no declared hypotheses;
- at least one explicit assumption saying that the arithmetic mechanism is
  synthetic.

Create `experiment.json` and a compatible `model.py`. Plan the experiment,
confirm that it contains two runs, execute it, and audit the final bundle with
the skill's validator. Do not overwrite or repair an existing output directory.

After writing the two input files, perform the lifecycle in this exact order:

1. Run the documented `plan` command.
2. Read only `design/plan-manifest.json` to confirm `runCount=2`.
3. Run the documented `run` command.
4. Run the documented validator immediately, with `--report` set to the required
   validation-report path.
5. Only after step 4 may you read `validation-report.json` or inspect the final
   outputs. Do not probe a path before its producing command has run.

These exact non-empty files are required:

- `deliverables/contract-smoke/experiment.json`
- `deliverables/contract-smoke/model.py`
- `deliverables/contract-smoke/design/run-plan.csv`
- `deliverables/contract-smoke/design/scenario-factors.csv`
- `deliverables/contract-smoke/design/design-point-parameters.csv`
- `deliverables/contract-smoke/design/plan-manifest.json`
- `deliverables/contract-smoke/data/runs.csv`
- `deliverables/contract-smoke/data/outcomes.csv`
- `deliverables/contract-smoke/data/observations.csv`
- `deliverables/contract-smoke/data/events.csv`
- `deliverables/contract-smoke/data/diagnostics.csv`
- `deliverables/contract-smoke/analysis/summary.csv`
- `deliverables/contract-smoke/analysis/explore.sql`
- `deliverables/contract-smoke/data-dictionary.json`
- `deliverables/contract-smoke/execution-manifest.json`
- `deliverables/contract-smoke/validation-report.json`

Do not create `analysis/hypothesis-results.json`, because no hypothesis is
declared. The validation report must have `ok: true`, `releaseEligible: true`,
and `executionStatus: complete`. Keep the copied skill unchanged. In the final
response, report the bundle root, run count, both scenario results, and the
validation result.
