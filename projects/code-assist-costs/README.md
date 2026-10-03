# Code-assist cost simulation

An offline mathematical study of coding-assistant token costs, cache behavior,
tool waves, compaction, context-quality loss, validation, retries and monthly
billing. No Pi, Copilot, inference API, real target tools or live benchmark is
executed. The harness is a policy configuration, not an empirically ranked brand.

For the current visual, interactive presentation, open
[the ChatGPT Site](https://code-assist-cost-curves.gvillarroel.chatgpt.site)
(owner-only access), or [the offline $200 budget presentation](artifacts/decision-budget-v2/deck/index.html).
The new 14-scene view translates the frozen model into monthly task-run allowance,
successful-task equivalents, same-use spending and remaining account balance.
It preserves parameter sliders, replay, chart exports and the 46-candidate
inventory. A synthetic 30-day account view and an explicit budget reserve help
explain the tradeoffs. See the [budget method](source/budget-view-method.md) and
[follow-up review](source/budget-view-followup.md). This is a token budget, not a
subscription quota or a guaranteed finite-budget completion count.

The [original 15-scene decision curves](artifacts/decision-curves-v1/deck/index.html)
remain preserved. The reference composition comes from the blog's cost-efficiency
slides and replayable alternate deck. The Google Slides deck below remains a
separate static companion.

Read the [decision-curve method](source/decision-curves-method.md) and
[conditional findings](source/decision-curves-findings.md). The fresh generated
study is `artifacts/decision-curves-v1/study/`. Plotted CSVs are under
`artifacts/decision-curves-v1/data/`. Editable browser sources live in
`source/decision-deck/`; `scripts/build_decision_deck.ts` inlines the data and
the pinned D3 7.9.0 runtime from the generated deck's `vendor/` directory.
The scene export button produces standalone editable SVG charts. Sliders need
the HTML presentation; they are not live Google Slides objects.

Run `node --experimental-strip-types projects/code-assist-costs/scripts/build_budget_deck.ts`
to build and verify the budget view from the preserved data. Its editable sources
are under `source/budget-deck/`; transformed CSVs, their dictionary and verification
records are under `artifacts/decision-budget-v2/`. The dedicated Sites checkout
is under `artifacts/sites/decision-curves/`; do not push the parent skills repository
as a Sites source repository.

For the previous parameters-first static presentation, start with the
[AA-anchored OFAT method and scope](source/aa-ofat-method-20260906.md) and the
[updated Google Slides deck](https://docs.google.com/presentation/d/1I-6EtS6RUjfWaPm4JiAQIDIDd4u0FQaxUFjeAp2URCs/edit).
Its fresh generated bundle is `artifacts/aa-ofat/study-v1/`; it keeps published
AA task aggregates, one-factor ledgers, model-dependent output means, explicitly
assumed token dispersion, and quality/recovery sensitivities separate.

For the preserved earlier study, start with the [durable findings](source/findings-20260906.md),
[method](source/method-20260906.md), and
[frozen inputs and source URLs](source/study-20260906.json).
The current generated bundle is `artifacts/data/20260906-v3/` (ignored by Git).
Its [full report](artifacts/data/20260906-v3/analysis/results.md) and
[SQLite database](artifacts/data/20260906-v3/analysis/exploration/study.sqlite)
are ready for local exploration. Use the matching
[SQL queries](artifacts/data/20260906-v3/analysis/exploration/queries.sql),
[data dictionary](artifacts/data/20260906-v3/analysis/exploration/data-dictionary.json),
[candidate-variable review](artifacts/data/20260906-v3/design/model-review.md), and
[post-run review](artifacts/data/20260906-v3/analysis/model-review-followup.md).

## Reproduce from the repository root

Python 3.14.7 and NumPy 2.3.5 were used. The model and core runner need only the
standard library. The NumPy analysis and validator declare a pinned uv fallback.
Use a new output directory; do not overwrite an existing experiment. Replace
`reproduction-1` below if that directory already exists. Stop on a failed step.

```powershell
python projects/code-assist-costs/scripts/build_study.py --output-dir projects/code-assist-costs/artifacts/data/reproduction-1
python skills/simulation-data-lab/scripts/run_simulation_experiment.py plan --spec projects/code-assist-costs/artifacts/data/reproduction-1/experiment.json --output-dir projects/code-assist-costs/artifacts/data/reproduction-1/design --require-variable-review
python projects/code-assist-costs/scripts/test_cost_model.py
python skills/simulation-data-lab/scripts/run_simulation_experiment.py run --root projects/code-assist-costs/artifacts/data/reproduction-1 --model model.py
python projects/code-assist-costs/scripts/test_cost_model.py --activation-output projects/code-assist-costs/artifacts/data/reproduction-1/analysis/parameter-activation.csv
python skills/simulation-data-lab/scripts/analyze_simulation_hypotheses.py --root projects/code-assist-costs/artifacts/data/reproduction-1
python skills/simulation-data-lab/scripts/validate_simulation_bundle.py --root projects/code-assist-costs/artifacts/data/reproduction-1 --report projects/code-assist-costs/artifacts/data/reproduction-1/validation-report.json
python projects/code-assist-costs/scripts/analyze_study.py --root projects/code-assist-costs/artifacts/data/reproduction-1
python projects/code-assist-costs/scripts/validate_extension.py --root projects/code-assist-costs/artifacts/data/reproduction-1
python projects/code-assist-costs/scripts/report_study.py --root projects/code-assist-costs/artifacts/data/reproduction-1
```

If NumPy is not installed, use `uv run --script` instead of `python` for the
analysis and extension-validation commands. The execution manifests record the
actual runtime. Author a new `analysis/model-review-followup.md` after inspecting
the regenerated evidence; that human review is not certified by the CSV audit.

The study contains 612 exact core cells, a 51840-cell finite policy grid and
320000 synthetic months. The 20000 Monte Carlo months per case describe an
invented stochastic process. They do not provide 95% confidence in the real-world
behavior of current models. Price sources are dated; quality inputs and losses
are assumptions. See the durable record under
`evaluations/simulation-data-lab/code-assist-costs-20260906.md`.
