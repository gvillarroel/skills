# LLM Billing

Project: AI Code Assistant Concepts
Video ID: 02-llm-billing
Runtime: 42 seconds

## Learning Objective

Cost follows model work, even when a product wraps usage as seats, credits, or subscriptions.

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
| 0.0-8.4s | open | The same work can wear different price labels | Subscription, credit, API, and local costs are packaging around real compute. | seat, credit, API |
| 8.4-16.8s | define | Input and output both matter | Long prompts, long answers, and repeated tool loops add up. | input, output, retry |
| 16.8-25.2s | mechanism | Model choice changes the meter | A stronger model can cost more but may reduce retries on hard work. | model, latency, success |
| 25.2-33.6s | tradeoff | Cache and trim before scaling | Repeated context should be cached or summarized when the harness supports it. | cache, trim, reuse |
| 33.6-42.0s | landing | Track cost per accepted result | The useful metric is completed work, not one isolated call. | accepted, task, budget |

## Production Note

This module is intentionally compact and visual-first. Exact product prices, plan limits, and plan names are kept in source notes instead of on-screen copy because those facts change quickly.
