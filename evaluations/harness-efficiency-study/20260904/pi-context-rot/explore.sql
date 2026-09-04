-- DuckDB starter queries for the deterministic context-rot bundle.
CREATE OR REPLACE VIEW quality_aggregate AS
SELECT * FROM read_csv_auto('quality-aggregate-results.csv.gz', header=true);

CREATE OR REPLACE VIEW quality_strata AS
SELECT * FROM read_csv_auto('quality-stratum-results.csv.gz', header=true);

CREATE OR REPLACE VIEW quality_contrasts AS
SELECT * FROM read_csv_auto('quality-contrast-results.csv.gz', header=true);

CREATE OR REPLACE VIEW break_even AS
SELECT * FROM read_csv_auto('break-even.csv.gz', header=true);

CREATE OR REPLACE VIEW scaled_monthly AS
SELECT * FROM read_csv_auto('scale-results.csv.gz', header=true);

CREATE OR REPLACE VIEW primary_boundaries AS
SELECT * FROM read_csv_auto('fidelity-boundaries.csv', header=true);

-- Primary cost/quality frontier by model.
SELECT model, strategy_id, completion_probability,
       provider_cost_per_assigned_session_usd,
       provider_cost_per_successful_session_usd,
       completion_slo_met
FROM quality_aggregate
WHERE parameter_set_id = 'primary-onset-200k-half-odds-f095-k3-uniform'
ORDER BY model, provider_cost_per_assigned_session_usd;

-- Assumption cells where compacting beats grow on both completion and assigned cost.
SELECT model, comparison_strategy_id, COUNT(*) AS cells
FROM quality_contrasts
WHERE dominance_status = 'comparison_dominates_or_ties'
GROUP BY model, comparison_strategy_id
ORDER BY model, comparison_strategy_id;

-- One-million-session primary projection.
SELECT model, strategy_id, expected_completed_sessions,
       expected_unresolved_sessions, expected_provider_spend_usd
FROM scaled_monthly
WHERE parameter_set_id = 'primary-onset-200k-half-odds-f095-k3-uniform'
  AND assigned_sessions = 1000000
ORDER BY model, strategy_id;
