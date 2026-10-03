# Code-assist cost study: mathematical application validation

- Skill: `simulation-data-lab`.
- Case: exploratory project application with arithmetic, accounting, variable
  review, sensitivity and structural-challenge checks; not a Spark forward test.
- Date: 2026-09-06.
- Executed models: none. Local mathematical engine: Python 3.14.7; NumPy 2.3.5
  PCG64 for synthetic monthly sampling. No Pi, Copilot or inference call.
- Source: `projects/code-assist-costs/`.
- Final bundle: `projects/code-assist-costs/artifacts/data/20260906-v3/`.
- Required outputs: frozen spec and preflight review, run/outcome/summary CSVs,
  generated contrasts, core audit, policy-grid and monthly-risk extension,
  independent extension audit, SQLite/SQL exploration, report and post-run review.

## Results

The core passed all 612 cells with zero failed or invalid runs and 8568 outcome
rows. It contains 24 declared direction-screening contrasts (20 supported and
four challenged under the model). The variable-review status remains
`limitations-required`, identifying ten decision-critical unresolved/excluded
groups; computational eligibility does not certify completeness or real-world
validity.

Nine mathematical test methods passed, covering 128 terminal-probability
settings and exact/boundary cases. All 49 parameters have activation witnesses.
The extension exhausts 5760 policies across nine workload/world points (51840
cells), independently rebills 4328 core-ledger rows, and simulates/replays
320000 months in sixteen 20000-month cases. Thirteen CSV tables are hash-bound.
SQLite integrity and four exploration queries pass.

Repository pattern-ID validation (1222 canonical IDs), skill validation,
independence tests and payload checks also passed. No skill-source edit or
installation synchronization was required for this application.

See [durable findings](../../projects/code-assist-costs/source/findings-20260906.md)
for numerical conclusions and [method](../../projects/code-assist-costs/source/method-20260906.md)
for assumptions, selection rules, uncertainty and scope. The user requested
simulation only: external quality evidence remains a gap, not a follow-up action.

## Commands

The complete fresh-bundle sequence is in
[the project entry point](../../projects/code-assist-costs/README.md).
For the final bundle the executed validation commands were:

```powershell
python projects/code-assist-costs/scripts/test_cost_model.py --activation-output projects/code-assist-costs/artifacts/data/20260906-v3/analysis/parameter-activation.csv
python skills/simulation-data-lab/scripts/analyze_simulation_hypotheses.py --root projects/code-assist-costs/artifacts/data/20260906-v3
python skills/simulation-data-lab/scripts/validate_simulation_bundle.py --root projects/code-assist-costs/artifacts/data/20260906-v3 --report projects/code-assist-costs/artifacts/data/20260906-v3/validation-report.json
python projects/code-assist-costs/scripts/validate_extension.py --root projects/code-assist-costs/artifacts/data/20260906-v3
python projects/code-assist-costs/scripts/report_study.py --root projects/code-assist-costs/artifacts/data/20260906-v3
```

## Recoveries and classification

The v1 runner correctly refused a pre-existing analysis directory; classify
this as author orchestration recovery, not a model failure. V2 completed, then
dependency metadata was pinned to the actual installed NumPy version; unchanged
model and experiment bytes were rerun in fresh v3. One read-only PowerShell SQL
inspection failed quoting and was replaced with CSV inspection. All attempts
remain locally retained; they are not independent statistical repetitions.

No skill behavior was changed by this application. The skill's backlog remains
`validating`; the user prohibits the real Pi/model forward gate. Do not promote
it on the strength of numerical checks alone.
