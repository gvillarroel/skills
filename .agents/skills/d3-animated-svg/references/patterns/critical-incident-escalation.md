# Critical Incident Escalation

- **Pattern ID:** `d3-pattern-critical-incident-escalation`
- **Gallery source ID:** `critical-incident-escalation`
- **Family:** Critical
- **Use when:** A SEV-1/SEV-2 incident, outage, security event, production escalation, or on-call response needs to show detection, impact confirmation, incident command, communication cadence, mitigation, recovery, post-incident learning, and SLA pressure.
- **Builder:** `scripts/build_critical_incident_escalation.py`

## Reuse Contract

- Use this file as the pattern source in isolated skill-only workspaces; read the gallery fixture only when maintaining that fixture.
- For standalone HTML artifacts, prefer the bundled builder:

```powershell
uv run --script skills/d3-animated-svg/scripts/build_critical_incident_escalation.py incident.html
```

- Keep the incident timeline deterministic. Time is horizontal, response lanes are fixed, and escalation links connect final event positions.
- In the published D3 gallery, use a `wide` card so the timeline, command panel, mitigation beats, and role cards remain readable instead of compressing the incident response into a standard card.
- Use SVG-native animation for standalone output; do not leave runtime D3, CDN, or external font dependencies in a self-contained deliverable.
- Preserve the incident-response semantics: red is active severity or breach risk, orange is containment or warning, green is mitigation/recovery, blue is detection/signal, and purple is ownership/coordination.
- Keep labels outside moving pulse corridors. Escalation pulses should travel on visible paths, not across event labels.
- Separate the timeline, mitigation action row, communication cadence row, response-role cards, and command-status panel. Do not stack those controls in the same vertical band.

## Data Contract

Use inline records for phases, events, escalation links, teams, and mitigations:

```js
const events = [
  { id: "detect", label: "Alert fires", minute: 0, lane: "signal", severity: "sev1", owner: "monitoring" },
  { id: "ic", label: "IC assigned", minute: 7, lane: "command", severity: "sev1", owner: "incident-commander" },
  { id: "mitigate", label: "Mitigate", minute: 28, lane: "mitigation", severity: "warning", owner: "ops-lead" }
];

const escalations = [
  { id: "detect-triage", source: "detect", target: "triage", kind: "page", critical: true },
  { id: "lead-mitigate", source: "lead", target: "mitigate", kind: "handoff", critical: true }
];

const phases = [
  { id: "detect", start: 0, end: 7, status: "sev1" },
  { id: "coordinate", start: 7, end: 18, status: "command" },
  { id: "contain", start: 18, end: 32, status: "warning" },
  { id: "recover", start: 32, end: 52, status: "stable" }
];

const communicationBeats = [
  { id: "first-update", minute: 16, label: "First update" },
  { id: "sla-update", minute: 31, label: "SLA update" }
];
```

Event minutes are measured from detection. The SLA deadline is a separate value such as `slaMinutes: 30`. Do not silently rescale exact minutes if a prompt gives them.

## Geometry Contract

1. Use a root SVG with `viewBox="0 0 1180 700"`, a `<title>`, a `<desc>`, and `data-pattern-id="d3-pattern-critical-incident-escalation"`.
2. Draw the severity phase strip above the event lanes.
3. Draw time ticks and an SLA marker before events.
4. Render each incident event as `.critical-incident-event` with `data-event-id`, `data-minute`, `data-lane-id`, `data-severity`, and `data-owner`.
5. Render escalation paths as `.escalation-link` with `data-escalation-id`, `data-source-id`, `data-target-id`, `data-kind`, and `data-critical`.
6. Render moving `.escalation-pulse` marks only on escalation links after the corresponding path has started drawing.
7. Render teams or owners as `.response-team` cards. Use them as context, not as the primary visual target.
8. Render mitigation rows as `.mitigation-step` marks with `data-step-id`, `data-minute`, and `data-status`.
9. Render communication cadence as `.communication-beat` marks with `data-beat-id` and `data-minute`.
10. Render the live command-state summary as `.incident-status-card` marks, not as loose annotation text.

## Animation Contract

- Incident shell, title, phase strip, and time ticks reveal first from `0.00s` to `0.45s`.
- Event nodes reveal in incident-time order.
- Escalation links draw after both endpoint events have appeared.
- Escalation pulses begin after link drawing starts and remain hidden before their first `animateMotion` begin time.
- SLA countdown marker sweeps from detection toward the deadline and freezes at the current mitigation minute.
- Communication beats reveal after the bridge/comms event is visible.
- Mitigation steps reveal after ownership is established.
- The final frame must contain all events, escalation links, phase bands, SLA marker, response-team cards, command-status cards, communication beats, and mitigation steps.

## Semantic Color Roles

- Red: SEV-1, breach risk, page escalation, or active customer impact.
- Orange: containment, warning, degraded service, or risk burn-down.
- Green: mitigation, recovery, validation, or stable state.
- Blue: detection signals, telemetry, or monitoring evidence.
- Purple: ownership, incident command, comms, or cross-functional coordination.
- Neutral gray: timeline ticks, lane rules, inactive context, and panel borders.

## Minimal D3 Renderer Pattern

Use D3 to scale minutes and compute paths, then write SVG-native animation:

```js
const width = 1180;
const height = 700;
const left = 176;
const right = 890;
const maxMinute = 52;
const x = d3.scaleLinear().domain([0, maxMinute]).range([left, right]);
const laneY = new Map([["signal", 214], ["command", 324], ["mitigation", 434]]);
const eventById = new Map(events.map(d => [d.id, d]));

function eventPoint(event) {
  return { x: x(event.minute), y: laneY.get(event.lane) };
}

function escalationPath(link) {
  const source = eventPoint(eventById.get(link.source));
  const target = eventPoint(eventById.get(link.target));
  const dx = Math.max(36, Math.abs(target.x - source.x) * 0.42);
  return `M${source.x},${source.y} C${source.x + dx},${source.y} ${target.x - dx},${target.y} ${target.x},${target.y}`;
}

const svg = d3.select("svg")
  .attr("viewBox", `0 0 ${width} ${height}`)
  .attr("data-pattern-id", "d3-pattern-critical-incident-escalation")
  .attr("data-pattern-family", "critical-incident")
  .attr("data-event-count", events.length)
  .attr("data-escalation-count", escalations.length)
  .attr("role", "img");

const links = svg.append("g")
  .attr("class", "escalation-links")
  .selectAll("path")
  .data(escalations)
  .join("path")
  .attr("id", d => `escalation-link-${d.id}`)
  .attr("class", d => `escalation-link${d.critical ? " critical-escalation" : ""}`)
  .attr("data-escalation-id", d => d.id)
  .attr("data-source-id", d => d.source)
  .attr("data-target-id", d => d.target)
  .attr("data-kind", d => d.kind)
  .attr("data-critical", d => String(d.critical))
  .attr("d", escalationPath)
  .attr("pathLength", 1)
  .attr("stroke-dasharray", "1 1")
  .attr("stroke-dashoffset", 0);
```

## Validation Hooks

- Root SVG exposes `data-pattern-id="d3-pattern-critical-incident-escalation"` and `data-pattern-family="critical-incident"`.
- Root counts match rendered marks: `data-event-count`, `data-escalation-count`, `data-critical-escalation-count`, `data-phase-count`, `data-team-count`, `data-mitigation-count`, `data-communication-count`, and `data-status-card-count`.
- Every `.critical-incident-event` has a minute, lane, severity, and owner data attribute.
- Every `.escalation-link` has a non-empty `d` attribute and source/target data attributes.
- Every critical escalation has a matching `.escalation-pulse` with `<animateMotion>`.
- The SVG exposes one `.sla-countdown` and one `.incident-clock`.
- `.communication-beat`, `.incident-status-card`, `.response-team`, and `.mitigation-step` marks are visible in distinct rows or panels without overlapping timeline labels.
- A screenshot after about `2.8s` must show a nonblank incident timeline, visible severity transition, readable event labels, visible SLA pressure, visible command state, communication cadence, and no pre-start pulse at `(0,0)`.
