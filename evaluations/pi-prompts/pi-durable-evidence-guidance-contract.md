Use the supplied pi-durable skill to prepare an independent agent project and a practical evidence-collection handoff. Work only in this evaluation workspace and treat `skills/pi-durable/` as read-only. Generate the service at exactly `outputs/agent` using this command:

```sh
uv run --script skills/pi-durable/scripts/scaffold.py outputs/agent
```

Do not install dependencies, start services, use credentials, contact external services or call a nested model. Leave the generated source and initial scaffold manifest unchanged. Inspect the generated runbook and default active prompt. Write exactly `outputs/handoff.md` explaining how an operator should prepare useful task evidence, verify outcomes and assess whether a requested evolution has enough support. Include how the running model receives collection instructions, what remains an operator step, how missing observations and an incomplete reflection pack should be handled, and which controls the current runtime actually enforces. The handoff must remain understandable without access to the skill. Distinguish a reproducible bug fix from general improvement of an agent's decisions, and describe an honest baseline/candidate comparison and post-release check. Do not imply that this exercise measured real task quality.
