# Local Pi Durable agent pilots

Two named agents run in one resident application, with separate Pi Durable Harness databases and task conversations. The complete application is in [app/](app/); it operates without the generating skill. This project targets the `gvillarroel/skills` repository and uses its existing read-only GitHub CLI authentication.

The pilots were selected from a bounded, authorized Codex activity sample. Assessment notes remain private under `artifacts/reviews/activity-assessment.md`; the versioned project records the reusable roles and mechanisms without publishing personal transcripts or activity-index counts.

| Agent | Event source | Useful result |
|---|---|---|
| `repo-quality` | Stable repository source changes, including committed HEAD and dirty/untracked source content | Observed validator outcomes, failures and remaining coverage limits |
| `delivery-watch` | Local HEAD/dirty status, open PR heads, review/check state and recent workflow transitions | Delivery blockers and the next concrete reviewable action |

The host owns event polling and a durable SQLite queue. The model runs after an admitted change; it does not poll for events. Source changes require 30 seconds of stability. Automatic admission is limited to four jobs per agent per UTC day, at least 15 minutes apart, with one job running per agent. Each job has an eight-minute deadline. The real provider uses low thinking effort, a two-minute request timeout and bounded retries. The wrapper requests a 4,096 output-token limit, but pinned Pi AI's Codex request builder does not serialize it; it is not a server-side token or spending cap. Human chat is user-triggered work and is separate from the automatic watcher admission cap.

All source inspection and GitHub tools are read-only. Reports and versioned public decision evidence remain under the ignored `artifacts/state/` directory. Source validation cannot establish visual quality or isolated skill authoring quality. Self-improvement remains inactive until a trusted user requests the application's explicit request/reflection/evaluation/promotion workflow.

The delivery pilot samples open PRs and the latest 20 workflow runs. A PR opened
and closed entirely between polls can be absent from that snapshot. When every
opened event must be retained, configure the starter's separate all-state PR
poller or signed webhook ingress and its GitHub credentials. The automatic
watcher cap described above applies to local snapshot admission, not direct PR
events or human chat.

## Operate the pilot

For a native Pi terminal console, use the [agent console extension](pi-extension/README.md).
It provides `/agents` and `/agent` for listing, task history and direct chat.

From this repository root:

```powershell
node projects/pi-agent-services/app/dist/src/manage.js status
node projects/pi-agent-services/app/dist/src/manage.js list
node projects/pi-agent-services/app/dist/src/manage.js jobs repo-quality
node projects/pi-agent-services/app/dist/src/manage.js chat repo-quality
node projects/pi-agent-services/app/dist/src/manage.js chat delivery-watch
node projects/pi-agent-services/app/dist/src/manage.js stop
node projects/pi-agent-services/app/dist/src/manage.js start
```

Use `chat <agent> --job <saved-job-id>` to reconnect to a particular task, or omit `--job` for the independent control conversation. `/exit` leaves chat. `abort <agent> --job <id>` cancels that conversation. Status and chat use a private loopback API at `127.0.0.1:4792` with a local bearer file. There is no public browser console or automatic Codex-sidebar registration.

`start` launches a hidden background Node process and writes logs under `artifacts/state/logs/`. It survives closing a terminal. Automatic login registration is not installed; machine reboot/logout can stop the process. The application retains the existing Windows Task Scheduler/macOS LaunchAgent planner for an explicitly scoped later startup deployment. Native macOS operation has not been tested on this Windows machine.

Build and test from `app/` with `npm ci --cache .cache/npm --ignore-scripts --no-audit --no-fund`, `npm run build`, and `npm test`. The project-local helper and [application runbook](app/AGENTS.md) also cover smoke checks, native plans, evidence and requested evolution. `manage.js` and live verification prefer the ignored `config.local.json` when present; `PI_PILOT_CONFIG` can select another config. Versioned `config.json` is an explicitly labeled faux/offline default. For live deployment, copy it to `config.local.json`, select `openai-codex` and `gpt-6.1-sol`, set `provider.piCliPath` to the installed Pi JavaScript entry point, and enable desired desktop notifications. Adjust `pilot.repositoryRoot`/repository allowlist for another checkout.

## Authentication and notifications

The live pilot uses Pi AI/Durable 1.3.0 and the installed Pi CLI 0.84.2. Its initial validation used `gpt-5.6-sol`; both agents now select `openai-codex/gpt-6.1-sol` at the owner's request, including their existing task chats. Use `status` for the current model. The provider captures `pi auth check --provider openai-codex --no-refresh --json --credentials` in memory. It never prints or copies the bearer and never refreshes the account. If that credential expires, the work fails visibly and the normal Pi sign-in must be renewed separately; then reconnect to the retained task or submit a new trusted task. This is a local pilot using an existing account, not unattended credential provisioning.

The durable notification outbox deduplicates start/completion/failure events and retries bounded transient failures. Desktop notifications contain only agent ID, fixed status and a short job reference. `provider_accepted` means the Windows notification API or messaging provider accepted an attempt; it does not prove a visible balloon, phone delivery or reading.

Desktop notifications are enabled. Telegram is implemented but disabled until the owner chooses it and configures a bot and private chat. For Telegram, create a bot with BotFather, start its private chat, set `pilot.telegramNotifications: true`, and put the following secrets in `artifacts/state/environment.env` (never in Git or chat):

```text
PI_NOTIFY_TELEGRAM_ENABLED=1
PI_NOTIFY_TELEGRAM_TOKEN=<bot-token>
PI_NOTIFY_TELEGRAM_CHAT_ID=<private-chat-id>
```

Restart the host after configuration. The console loopback address is not reachable from a phone. The current notification adapter sends fixed progress only; it does not receive phone chat commands.

WhatsApp requires its own sender account, recipient consent and approved templates for proactive messages outside the customer-service window. It was researched, not connected. See [WhatsApp policy](https://whatsappbusiness.com/policy/?iframe=yes), [Telegram bot setup](https://core.telegram.org/bots/tutorial), and [sendMessage](https://core.telegram.org/bots/api#sendmessage). No paid account or external mobile delivery was created.

## Retained verification

Local generated evidence is kept in `artifacts/`, including live before/after-restart receipts, source/GitHub observations, test logs and operational reports. The versioned [validation record](validation.md) distinguishes deterministic tests, real model executions, desktop acceptance and untested mobile/macOS behavior. Do not commit live state, console tokens, credentials, raw Codex sessions, dependency trees or generated logs.
