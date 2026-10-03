# Aggregate report input

Use the consolidator for completed native `final-report.json` files, or for clearly labeled synthetic offline fixtures when explicitly requested. Do not run Harbor jobs to create an offline comparison.

Honor the requested input filename and output directory exactly:

```sh
uv run --script <skill-root>/scripts/consolidate_harbor_reports.py final-report.json --output-dir comparison
```

Read and write JSON, Markdown and SVG with UTF-8. The script emits exactly `comparison-report.json`, `comparison-report.md`, `quality-comparison.svg`, `resource-comparison.svg` and `efficiency-frontier.svg` beneath the specified directory. Keep helper scripts and generated artifacts outside the copied skill.

The smallest useful complete native job has this shape. This is synthetic data, not evaluation evidence:

```json
{
  "schemaVersion": 1,
  "source": "harbor",
  "title": "Synthetic offline report",
  "generatedAt": "2026-10-03T12:00:00+00:00",
  "comparison": {"enabled": true, "fairnessBasis": "same synthetic contract", "warning": null},
  "jobs": [{
    "jobId": "baseline-job",
    "label": "baseline",
    "complete": true,
    "startedAt": "2026-10-03T11:00:00+00:00",
    "finishedAt": "2026-10-03T11:01:00+00:00",
    "summary": {
      "requestedTrials": 2, "completedTrials": 2,
      "passedTrials": 1, "verifierFailedTrials": 1, "erroredTrials": 0,
      "passRate": 0.5,
      "reward": {"count": 2, "total": 1.0, "average": 0.5},
      "totalTokens": {"count": 2, "total": 360, "average": 180},
      "agentLatencyMs": {"count": 2, "total": 3000, "average": 1500},
      "costUsd": {"count": 2, "total": 0.30, "average": 0.15}
    },
    "trials": [
      {"tokens": {"input": 100, "cachedInput": 40, "output": 20, "total": 120}},
      {"tokens": {"input": 200, "cachedInput": 50, "output": 40, "total": 240}}
    ]
  }]
}
```

For another synthetic job, add a new job object with a unique `jobId` and `label`, and make its counts, metrics and trial values consistent. Keep task names, prompts, answers and private paths out of the fixture.

For every trial, **total tokens equal input plus output**. Cached input is a subset of input: never add it again or subtract it from input when calculating total. Optional reasoning is reported separately because provider accounting can overlap output. In the example, input sums to 300, cache to 90 and output to 60; total is 360. The summary's observed total and average must agree with its trial counts. Incomplete coverage remains incomplete and does not produce efficiency deltas.

For SVG paint checks, a value such as `url(#background)` names a local paint server. Inspect its stops rather than treating the URL as a literal color. Filled marks are opaque and borderless; meaningful frontier connector lines and chart grids remain. Direct labels identify baseline and frontier points without decorative rings. The local [palette](../assets/palettes/colorsets.json) supplies all solid tokens; maximum 24 runs fits the 36 available colorset2 solids on the default stage, so no outline overflow is needed.
