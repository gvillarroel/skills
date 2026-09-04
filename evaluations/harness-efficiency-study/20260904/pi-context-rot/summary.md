# Pi context-rot cost-quality sensitivity summary

This is an offline model-conditional simulation. It did not execute Pi, Copilot, or any model API. The quality mechanism is hypothetical; historical benchmark slopes are explicitly non-GPT-5.6 proxies.

## Primary case

The named primary case uses onset 200,000 tokens, beta = ln(2)/(31/13), per-compaction fidelity 0.95, uniform evidence positions, and at most three attempts.

| Model | Strategy | Cost/attempt (USD) | Completion | Cost/assigned (USD) | Cost/success (USD) | SLO >=95% |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| luna | cap_200k_cache_read | 0.451200 | 0.967227 | 0.598048 | 0.618313 | yes |
| luna | cap_200k_cache_write | 0.635200 | 0.967227 | 0.841933 | 0.870462 | yes |
| luna | cap_200k_uncached | 0.595200 | 0.967227 | 0.788915 | 0.815647 | yes |
| luna | cap_pricing_threshold_uncached | 0.595200 | 0.967227 | 0.788915 | 0.815647 | yes |
| luna | grow_to_800k | 1.020400 | 0.921484 | 1.530381 | 1.660778 | no |
| sol | cap_200k_cache_read | 8.548000 | 0.967227 | 11.330049 | 11.713956 | yes |
| sol | cap_200k_cache_write | 12.228000 | 0.967227 | 16.207749 | 16.756932 | yes |
| sol | cap_200k_uncached | 11.428000 | 0.967227 | 15.147380 | 15.660633 | yes |
| sol | cap_pricing_threshold_uncached | 11.288000 | 0.967000 | 14.973792 | 15.484789 | yes |
| sol | grow_to_800k | 19.598000 | 0.921484 | 29.392799 | 31.897227 | no |
| terra | cap_200k_cache_read | 4.512000 | 0.967227 | 5.980485 | 6.183127 | yes |
| terra | cap_200k_cache_write | 6.352000 | 0.967227 | 8.419335 | 8.704615 | yes |
| terra | cap_200k_uncached | 5.952000 | 0.967227 | 7.889150 | 8.156466 | yes |
| terra | cap_pricing_threshold_uncached | 5.842000 | 0.967000 | 7.749547 | 8.014009 | yes |
| terra | grow_to_800k | 9.904000 | 0.921484 | 14.853877 | 16.119509 | no |

## Primary decision boundaries

`fidelity-boundaries.csv` reports, for every priced model and the uncached/cache-read 200k caps, the minimum per-compaction survival needed to beat grow on cost per successful session, the minimum survival needed to meet the 95% completion SLO, and the minimum context-rot beta at fixed f=0.95 needed to beat grow on cost per success. Each value is an exact analytic-model bisection over documented bounds.

## How to explore

Use `quality-contrast-results.csv.gz` for matched compact-minus-grow comparisons, `scale-results.csv.gz` for 1,000 and 1,000,000 assigned sessions, and `explore.sql` for starter DuckDB queries. `monte-carlo-summary.csv` checks a few primary analytic contrasts with paired common random numbers without retaining task-level rows.

## Evidence curves

The authored evidence input produced 54 threshold rows; 12 are bracketed interpolations. Unbracketed thresholds are marked `unidentifiable`; none are extrapolated.

## Interpretation boundary

These results support or challenge strategies only under the declared equations and assumptions. External task-level validation is required before treating any quality or break-even result as a production forecast.
