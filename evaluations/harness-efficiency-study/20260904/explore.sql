-- Run from this directory with: duckdb :memory: -c ".read explore.sql"
CREATE OR REPLACE VIEW scenario_summary AS
SELECT * FROM read_csv_auto('scenario-summary.csv', header = true);

CREATE OR REPLACE VIEW workload_ranking AS
SELECT * FROM read_csv_auto('workload-ranking.csv', header = true);

CREATE OR REPLACE VIEW pairwise_deltas AS
SELECT * FROM read_csv_auto('pairwise-deltas.csv', header = true);

CREATE OR REPLACE VIEW pareto_frontier AS
SELECT * FROM read_csv_auto('pareto-frontier.csv', header = true);

CREATE OR REPLACE VIEW break_even AS
SELECT * FROM read_csv_auto('break-even.csv', header = true);

-- Headline portfolio comparison.
SELECT
  study,
  design_group,
  scenario_id,
  outcome_name,
  round(mean, 6) AS mean
FROM scenario_summary
WHERE outcome_name IN (
  'accepted_task_fraction',
  'provider_cost_usd_per_task',
  'allocated_cash_cost_usd_per_task',
  'economic_loss_usd_per_task',
  'wall_seconds_per_task'
)
ORDER BY study, design_group, scenario_id, outcome_name;

-- Best modeled scenario by economic loss within each workload/design point.
SELECT
  study,
  design_point_id,
  workload,
  scenario_id,
  accepted_task_fraction,
  economic_loss_usd_per_task,
  wall_seconds_per_task
FROM workload_ranking
QUALIFY row_number() OVER (
  PARTITION BY study, design_point_id
  ORDER BY economic_loss_usd_per_task, wall_seconds_per_task
) = 1
ORDER BY study, workload, design_point_id;

-- Every registered challenge reversal.
SELECT
  study,
  hypothesis_id,
  design_point_id,
  outcome_name,
  estimate_comparison_minus_baseline,
  threshold_value,
  point_status
FROM pairwise_deltas
WHERE role = 'challenge'
  AND point_status = 'challenges'
ORDER BY abs(estimate_comparison_minus_baseline - threshold_value) DESC;

-- Cost/quality/time Pareto options only.
SELECT *
FROM pareto_frontier
WHERE pareto_frontier
ORDER BY study, workload, design_point_id, scenario_id;

-- Monthly break-even evidence and interpolation status.
SELECT *
FROM break_even
ORDER BY workload, record_type, monthly_tasks;
