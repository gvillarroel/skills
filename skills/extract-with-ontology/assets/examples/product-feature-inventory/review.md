# Review of the reference inventory

Source revision `f309096a83abde7c311523f8ca97fc587388b0e1` of GitHub Docs. This reviewed
reference covers the thirteen capabilities scoped by the example.

## Classification still open

**GitHub Copilot usage metrics dashboard** is a documented capability.
The source establishes an instrumentation and dashboard feature that measures use of AI-assisted workflows. It does not establish AI execution or a decisive manual or rule-based classification mechanism for this scoped dashboard.

Does the dashboard use a model to compute or interpret the metrics,
or does it aggregate measured activity using fixed rules? A source
that specifies the dashboard's computation would resolve the class.
[Pinned evidence](https://github.com/github/docs/blob/f309096a83abde7c311523f8ca97fc587388b0e1/content/copilot/concepts/billing-and-usage/copilot-usage-metrics/copilot-metrics.md#L32-L32)

## Identity boundaries

- Human pull request review and Copilot code review are separate operations.
- Pull request auto-merge enforces merge conditions. Agent Merge addresses blockers.
- Dependabot security updates and version updates have separate triggers.
- Automatic Copilot code review is a trigger mode for the same review feature.

Documentation and quoted evidence are attributed to GitHub Docs contributors
under the [Creative Commons Attribution 4.0 license](https://github.com/github/docs#license).

The quotes retain GitHub Docs' original Liquid variable references.
The scoped product name uses the publisher's displayed terminology.
