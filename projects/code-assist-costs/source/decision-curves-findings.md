# Conditional decision-curve findings

The interactive deck contains 15 scenes, starting with the parameter families,
then isolating a parameter within each fixed workload or pair of policies.
It follows the large-chart/small-copy composition of the user's blog artifacts.
No file in the blog repository changed.

The fresh exploratory core completed 2,124 deterministic cells with no failed
or invalid runs. It reuses the reviewed offline request ledger and the September
6, 2026 evidence snapshot. No Pi, Copilot, inference API or real agent tool ran.

## Boundaries visible in the presentation

| Decision | Conditional result | Important limitation |
| --- | --- | --- |
| Stable system prefix | +1k tokens adds $0.35 per 1k tasks or $350 per 1m tasks. | One write and five cached reads, same short workload. |
| One fewer tool | Five to four saves about $976 per million tasks. | Total output and quality stay fixed. |
| Less output | A 20% reduction saves about $6,271 per million tasks. | The model does not identify the resulting quality change. |
| Compaction cap | The 1k grid minimum is 156k–160k, $0.763372 per long attempt versus $1.337628 without a cap. | Lossless quality, cold summarizer and rebuilt cache, searched range 50k–400k. |
| Simulated payback | The first 180k-policy summary adds expense at main call 8; cumulative savings turn positive at call 12 and stay positive through call 40. | One fixed simulated sequence, not empirical historical data. |
| Summary retention | Critical-fact break-even is about 96.45% per summary. | The average-fidelity rival has no crossing in 90%–100%. |
| Failure value | Luna max and Sol xhigh exchange preference at $3.821253 per failed task. | AA aggregate cost and success proxies, two-model comparison. |
| Persistent retries | Three attempts meet 95% completion only for rho at most 23.38%. | Equal attempt cost and a declared persistent-failure mixture. |
| Escalation recovery | Luna followed by Sol needs conditional recovery at least 73.82% to reach 95% completion. | Perfect validator; conditional fallback cost equals its published mean by assumption. |

The 500-token cap challenge grid returns the same minimum cost and extends the
tied sampled plateau through 160.5k. The displayed 156k–160k range explicitly
refers to the primary 1k grid. Neither grid proves continuous global optimality.

## Evidence and uncertainty

The [Artificial Analysis Terminal-Bench v2.1 snapshot](https://artificialanalysis.ai/evaluations/terminalbench-v2-1)
supplies the retained model-specific average output tokens, mean task cost and
pass@1. It covers 89 tasks with three repeats per task. The retrieved aggregate
does not provide empirical token dispersion or paired uncertainty for these
comparisons. It does not calibrate the simulated Pi/Copilot workload.

[GitHub's Copilot model-pricing reference](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)
supplies the frozen token rates. The ledger separates ordinary input, cache
reads, cache writes and output. Tariff selection uses total request input,
including summarizer calls. Token value before allowances is not an invoice.

Context degradation, fact retention, fallback recovery and shared shocks remain
assumptions. Deterministic arithmetic has no Monte Carlo error, but that does
not quantify confidence that the modeled system is true. Monthly standard
deviations are exact moments under the declared hypothetical CV assumptions,
not confidence intervals inferred from AA means.

## Artifacts and reproduction

- Method: [decision-curves-method.md](decision-curves-method.md).
- Presentation: `artifacts/decision-curves-v1/deck/index.html`.
- Curves: `artifacts/decision-curves-v1/data/curves.csv` and `analytic-curves.csv`.
- Core integrity: `artifacts/decision-curves-v1/study/validation-report.json`.
- Extension arithmetic and hashes: `artifacts/decision-curves-v1/extension-audit.json`.
- Browser source: `source/decision-deck/`.

The build script refuses to overwrite an existing mathematical study. A new
reproduction needs a fresh study ID/output path. After planning and running the
reviewed core with simulation-data-lab, use `analyze_decision_curves.py` for the
extension and `node --experimental-strip-types scripts/build_decision_deck.ts`
for the browser file, resolving those scripts within this project. The generated
HTML embeds D3 7.9.0 and the data, so reading the delivered presentation needs no
network connection or dependency installation.
