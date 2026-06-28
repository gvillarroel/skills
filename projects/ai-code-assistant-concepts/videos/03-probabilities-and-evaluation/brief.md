# Probabilities and Evaluation

Project: AI Code Assistant Concepts
Video ID: 03-probabilities-and-evaluation
Runtime: 42 seconds

## Learning Objective

LLM output is sampled from probabilities; evaluation decides whether the sample is good enough.

## Reused Symbolic Language

- Work packet: moving prompt, task, or data unit.
- Blue context box: visible information available to a model or agent.
- Green check: verified or allowed result.
- Red shield: policy, permission, guardrail, or governance boundary.
- Teal bus: standardized connection surface.
- Amber meter: cost, latency, or operational load.

## Scene Plan

| Time | Beat | Headline | Supporting idea | Screen terms |
|---|---|---|---|---|
| 0.0-8.4s | open | Likely is not guaranteed | The model scores candidate continuations instead of fetching one fixed answer. | probability, sample, variance |
| 8.4-16.8s | define | Context reshapes the distribution | Examples and constraints can move probability toward useful outputs. | context, examples, odds |
| 16.8-25.2s | mechanism | Tests beat vibes when possible | Schemas, unit tests, parsers, and exact checks make quality measurable. | tests, schema, parser |
| 25.2-33.6s | tradeoff | pass@N trades attempts for cost | More samples can improve success, but every attempt consumes time and budget. | pass@N, attempts, cost |
| 33.6-42.0s | landing | Agent evals need traces | For multi-step work, grade the path as well as the final answer. | trace, grader, regression |

## Production Note

This module is intentionally compact and visual-first. Exact product prices, plan limits, and plan names are kept in source notes instead of on-screen copy because those facts change quickly.
