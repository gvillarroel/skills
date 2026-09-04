-- DuckDB exploration queries for the deterministic Pi cost study.
-- Run from the bundle directory. No network access or provider calls are needed.

CREATE OR REPLACE VIEW calls AS
SELECT * FROM read_csv_auto('call-ledger.csv', header = true);

CREATE OR REPLACE VIEW scenarios AS
SELECT * FROM read_csv_auto('scenario-results.csv', header = true);

CREATE OR REPLACE VIEW contrasts AS
SELECT * FROM read_csv_auto('contrast-results.csv', header = true);

CREATE OR REPLACE VIEW scaled AS
SELECT * FROM read_csv_auto('scale-results.csv', header = true);

-- Highest monthly deltas at one million hypothetical executions.
SELECT contrast_id, model, cost_delta_usd, savings_usd
FROM scaled
WHERE volume_executions = 1000000
ORDER BY abs(cost_delta_usd) DESC;

-- Verify the mutually exclusive input-token partition.
SELECT count(*) AS invalid_rows
FROM calls
WHERE full_input_tokens !=
      input_uncached_tokens + cache_read_tokens + cache_write_tokens;

-- Show the pricing discontinuity around each model-specific threshold.
SELECT contrast_id, role, model, max_input_tokens, long_context_calls,
       provider_cost_usd
FROM scenarios
WHERE contrast_id LIKE 'system-threshold-%'
ORDER BY contrast_id, model, role;

-- Compare sequential and batched marginal fifth-tool costs.
SELECT contrast_id, model, cost_delta_usd, call_count_delta,
       cache_read_token_delta, cache_write_token_delta
FROM contrasts
WHERE contrast_id IN ('sequential-tools-4-to-5', 'batched-tools-4-to-5')
ORDER BY model, contrast_id;

-- Long-session economics and maximum tolerable quality loss.
SELECT c.contrast_id, c.model, c.baseline_provider_cost_usd,
       c.comparison_provider_cost_usd, c.savings_usd,
       b.quality_loss_budget_usd_per_compaction
FROM contrasts c
JOIN read_csv_auto('break-even.csv', header = true) b
  USING (contrast_id, model)
WHERE b.failure_loss_usd = 100
ORDER BY c.contrast_id, c.model;
