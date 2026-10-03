# Budget-view verification and remaining gaps

The builder passed 11,756 arithmetic checks over all 2,124 source curve cells.
The short-task whole-run baseline is 5,449. The isolated changes produce 5,397
runs with 1,000 extra stable system tokens, 5,597 with four tools, 6,571 with
20% less output and 5,215 at 90% cache reuse. The 180k cap yields 252 long runs
versus 149 without a cap. These are different task bases, not equivalent work.

The quality challenge remains material: 95% versus 99% summary fact retention
changes the preferred strategy. Keeping $40 unplanned buys 25% mean-cost
headroom, but provides no calibrated confidence level. The revised presentation
does not close the original benchmark-transfer or unknown-variable gaps.

Evidence: `artifacts/decision-budget-v2/qa/arithmetic-report.json`,
`artifacts/decision-budget-v2/data/budget-curves.csv`,
`artifacts/decision-budget-v2/data/dictionary.json`,
`artifacts/decision-budget-v2/qa/browser-report.json` and its scene screenshots.
All 14 scenes were checked at 1600, 900 and 360 pixels, including sliders,
downloads, replay and reduced motion. The original generated study and first
Site publication remain preserved. No modeled target systems were executed.
