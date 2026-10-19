# Pi Durable metadata routing smoke

Classify whether one candidate skill should be selected for each request. Use only
the candidate name and description supplied below. The skill body, templates and
references are intentionally unavailable. Do not inspect files, run commands,
search the internet, or infer capabilities from repository knowledge.

Select `yes` when the request's core task matches this metadata. Select `no` for
incidental word matches or a task belonging to a different product/workflow. A
request mentioning agents or Pi does not automatically match.

Candidate metadata:

```yaml
name: pi-durable
description: Builds and operates Pi Durable agent applications with persistent named agents, event-triggered tasks, reconnectable chat, and per-user background services on Windows and macOS. Use for PR-triggered agents, durable task queues, agent registries, crash recovery, or selecting Pi Durable runtime features.
```

Requests:

1. `desktop-pr-daemon`: Create named agent services on Windows and macOS that wait
   for new pull requests, queue their work durably, and let me reopen each agent's chat.
2. `real-pet`: Recommend a real pet for a family with children and a durable outdoor
   enclosure. We are comparing rabbits and guinea pigs.
3. `host-runtime`: Embed `@earendil-works/pi-durable` into a Node application with
   SQLite, persistent conversations, stable task request IDs, and crash recovery.
4. `one-shot-review`: Review this pull request diff once and report the defects.
   I do not want a background process, agent registry, or persistent application.
5. `saved-task-chat`: Keep a registry of named agents and their saved task sessions.
   When I select one in a local console, reconnect to its chat and continue the task.
6. `raspberry-case`: Find a durable protective case for my Raspberry Pi 5 computer,
   with good cooling and access to its GPIO pins.
7. `version-wake`: Our Pi Durable service is pinned to 1.3.0. Determine whether we
   can use wake, sleepUntil, retryTask, and background task features correctly, and
   select a compatible host waiting strategy.
8. `generic-email`: Write a simple scheduled email notifier using cron and SMTP.
   It sends a fixed message daily; there is no model, named agent, chat, or durable
   agent runtime involved.
9. `local-ci-event`: Build a local agent service that waits for a CI build_finished
   event, persists matching jobs across restarts, and exposes a chat for its agent.
10. `coding-terminal`: Help me use the normal Pi Coding Agent interactive terminal
    to edit source code in my current repository. I am not embedding a runtime or
    building a persistent event service.

Return exactly one JSON object, without Markdown fences, using this schema:

```json
{
  "candidate": "pi-durable",
  "cases": [
    {"id": "<request ID>", "select": "<yes or no>", "justification": "A short reason grounded in the supplied metadata."}
  ]
}
```

Include all ten cases in their original order. Use `yes` or `no` for `select` and
one concise English sentence for each justification. Do not perform the tasks.
