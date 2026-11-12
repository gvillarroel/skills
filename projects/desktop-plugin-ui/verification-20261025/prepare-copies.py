#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create corrected project copies without changing isolated-run evidence."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PALETTE = REPO / "skills/desktop-plugin-ui/assets/palettes/colorset1.yml"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contrast(first: str, second: str) -> float:
    def luminance(value: str) -> float:
        channels = [int(value[index:index + 2], 16) / 255 for index in (1, 3, 5)]
        linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in channels]
        return sum(weight * channel for weight, channel in zip((0.2126, 0.7152, 0.0722), linear))
    light, dark = sorted((luminance(first), luminance(second)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


TOKEN_PATHS = {
    "brand": "interface.action.primary.value", "brand-dark": "interface.action.primary_hover.value",
    "text": "interface.text.primary.value", "muted": "interface.text.secondary.value",
    "secondary": "interface.text.secondary.value", "page": "interface.background.page.value",
    "surface": "interface.background.surface.value", "border": "interface.border.dark.value",
    "border-dark": "interface.border.dark.value", "line": "interface.border.dark.value",
    "light-border": "interface.border.light.value", "light-line": "interface.border.light.value",
    "selected": "interface.state.selected.value", "error": "interface.action.destructive.value",
    "critical": "interface.action.destructive.value", "neutral-message": "interface.feedback.neutral.background.value",
    "soft": "interface.feedback.neutral.background.value", "disabled": "interface.state.disabled.value",
    "black": "colors.neutral.black.value",
}

TOOLTIP_CSS = """
    /* Descriptions do not intercept actions; reveal without composited paint. */
    .tooltip-wrap { position: relative; display: inline-flex; max-width: 100%; }
    .tooltip {
      position: absolute; z-index: 2; right: 0; left: auto;
      bottom: calc(100% + 8px); width: 220px; max-width: calc(100vw - 32px);
      padding: 8px 10px; border-radius: 5px;
      background: var(--text); color: var(--surface); font-size: .85rem;
      visibility: hidden; pointer-events: none;
    }
    .tooltip-wrap:hover .tooltip, .tooltip-wrap:focus-within .tooltip { visibility: visible; }
    .tooltip-wrap.dismissed .tooltip { visibility: hidden; }
    @media (max-width: 680px) { .tooltip { left: 0; right: auto; } }
"""

TOOLTIP_SCRIPT = """
  <script>
    document.querySelectorAll('.tooltip-wrap').forEach(wrap => {
      const place = () => {
        const tooltip = wrap.querySelector('.tooltip');
        tooltip.style.transform = '';
        const bounds = tooltip.getBoundingClientRect();
        const shift = Math.max(16 - bounds.left, Math.min(0, innerWidth - 16 - bounds.right));
        tooltip.style.transform = `translateX(${shift}px)`;
      };
      wrap.addEventListener('pointerenter', () => { wrap.classList.remove('dismissed'); place(); });
      wrap.addEventListener('focusin', () => { wrap.classList.remove('dismissed'); place(); });
      window.addEventListener('resize', place);
      wrap.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
          wrap.classList.add('dismissed');
          event.stopPropagation();
        }
      });
    });
  </script>
"""


def replace_once(text: str, before: str, after: str) -> str:
    if text.count(before) != 1:
        raise ValueError(f"Expected one occurrence of correction anchor: {before[:90]}")
    return text.replace(before, after, 1)


def fix_first(html: str) -> str:
    html = replace_once(html,
        '<button id="export" class="button secondary" type="button" title="Exports only the current selection.">Export CSV</button>',
        '<span class="tooltip-wrap"><button id="export" class="button secondary" type="button" aria-describedby="export-tip">Export CSV</button><span id="export-tip" class="tooltip" role="tooltip">Exports only the current selection.</span></span>')
    html = replace_once(html, '.table-wrap { overflow-x: auto;', '.table-wrap { overflow-x: visible;')
    html = replace_once(html, 'min-width: 620px;', 'min-width: 0;')
    html = replace_once(html, '    @media (max-width: 650px) {', """
    .request-cards { display: none; list-style: none; padding: 0; margin: 0; gap: 10px; }
    .request-card {
      width: 100%; min-height: 44px; padding: 12px; text-align: left;
      color: var(--text); background: var(--surface); border: 2px solid var(--border);
      border-radius: 5px; overflow-wrap: anywhere;
    }
    .request-card[aria-pressed="true"] { background: var(--selected); border-color: var(--brand); }
    .request-card span { display: block; }
    @media (max-width: 650px) {
      .table-wrap { display: none; }
      .request-cards { display: grid; }
""")
    anchor = '        els.results.querySelectorAll(\'input[name="ticket"]\').forEach(input => input.addEventListener("change", () => selectTicket(input.value)));'
    replacement = """        const cards = document.createElement("ul");
        cards.className = "request-cards";
        cards.setAttribute("aria-label", "Support requests");
        rows.forEach(ticket => {
          const item = document.createElement("li");
          const button = document.createElement("button");
          button.type = "button";
          button.className = "request-card";
          button.dataset.ticketId = ticket.id;
          button.setAttribute("aria-pressed", String(ticket.id === state.selectedId));
          button.setAttribute("aria-label", `Select ${ticket.id}: ${ticket.title}. Priority: ${ticket.priorityLabel}. Status: ${ticket.statusLabel}.`);
          [ticket.id, ticket.title, `Priority: ${ticket.priorityLabel}`, `Status: ${ticket.statusLabel}`].forEach(text => {
            const line = document.createElement("span");
            line.textContent = text;
            button.append(line);
          });
          button.addEventListener("click", () => {
            selectTicket(ticket.id);
            els.results.querySelector(`[data-ticket-id="${ticket.id}"]`)?.focus();
          });
          item.append(button); cards.append(item);
        });
        els.results.append(cards);
""" + '''        els.results.querySelectorAll('input[name="ticket"]').forEach(input => input.addEventListener("change", () => {
          selectTicket(input.value);
          els.results.querySelector(`input[name="ticket"][value="${input.value}"]`)?.focus();
        }));'''
    html = replace_once(html, anchor, replacement)
    return html


def fix_second(html: str) -> str:
    html = replace_once(html, '      box-shadow: 0 3px 12px rgba(0, 0, 0, .08);\n', '')
    html = replace_once(html, '--border: #9c9c9c;', '--border: #696969;')
    html = replace_once(html,
        '<button class="button secondary" id="refresh-button" type="button">Refresh queue</button>',
        '<button class="button secondary" id="refresh-button" type="button">Refresh queue</button>\n            <button class="button secondary" id="explain" type="button">Explain selection</button>')
    html = replace_once(html, '        refresh.disabled = nextBusy;', '        refresh.disabled = nextBusy;\n        $("explain").disabled = nextBusy;\n        $("export-button").disabled = nextBusy;')
    html = replace_once(html, '      function exportSelection() {', """      function explainSelection() {
        const selected = currentTicket();
        if (!selected) {
          showMessage("Select a request before asking for an explanation.", "error", "!");
          return;
        }
        showMessage(`${selected.id}: ${selected.title}. Saved priority: ${selected.priorityLabel}. Status: ${selected.statusLabel}.`, "neutral", "i");
      }
      function exportSelection() {""")
    html = replace_once(html, '      $("export-button").addEventListener("click", exportSelection);', '      $("export-button").addEventListener("click", exportSelection);\n      $("explain").addEventListener("click", explainSelection);')
    html = replace_once(html, '        showMessage(`Selected ${id}. Priority ${selected.priorityLabel} is ready to edit.`, "neutral", "✓");', '        showMessage(`Selected ${id}. Priority ${selected.priorityLabel} is ready to edit.`, "neutral", "✓");\n        list.querySelector(`[aria-label^="Select ${id},"]`)?.focus();')
    html = re.sub(r'    \.tooltip-wrap \{.*?    \.footer-note', '    .footer-note', html, count=1, flags=re.S)
    return html


def fix_third(html: str) -> str:
    html = replace_once(html, '--line: #9c9c9c;', '--line: #696969;')
    html = replace_once(html, '    .editor[aria-disabled="true"] { opacity: 0.75; }\n', '')
    html = replace_once(html, '<ul id="ticket-list" class="ticket-list" role="listbox" aria-label="Support requests">', '<ul id="ticket-list" class="ticket-list" aria-label="Support requests">')
    html = replace_once(html, "          button.setAttribute('role', 'option');\n", '')
    html = replace_once(html, "          button.setAttribute('aria-selected', String(ticket.id === state.selectedId));\n", '')
    html = replace_once(html, '    .ticket-row:hover {', '    .ticket-row[aria-pressed="true"] .meta { color: var(--text); }\n    .ticket-row:hover {')
    html = replace_once(html, '<button id="export" class="secondary" type="button">Export CSV</button>', '<button id="export" class="secondary" type="button" aria-describedby="export-tip">Export CSV</button>')
    html = re.sub(r'    \.tooltip-wrap \{.*?    \.fixture \{', '    .fixture {', html, count=1, flags=re.S)
    return html


def main() -> None:
    records = []
    for number, fixer in ((1, fix_first), (2, fix_second), (3, fix_third)):
        run_id = f"20261025-desktop-ui-english-components-v1-luna-{number}"
        source = REPO / f"evaluations/runs/{run_id}/workspace/ui"
        original = {name: sha(source / name) for name in ("status-panel.html", "component-copy.json")}
        html = fixer((source / "status-panel.html").read_text(encoding="utf-8"))
        html = replace_once(html, '  </style>', TOOLTIP_CSS + '\n  </style>')
        html = replace_once(html, '</body>', TOOLTIP_SCRIPT + '\n</body>')
        metadata = json.loads((source / "component-copy.json").read_text(encoding="utf-8"))
        bindings = [
            {"css_variable": f"--{name}", "value": value.lower(), "source_token_path": TOKEN_PATHS[name]}
            for name, value in re.findall(r'--([a-z-]+):\s*(#[0-9a-fA-F]{6});', html)
        ]
        pairs = [("#333e48", "#ffffff", "Ordinary body text", 4.5),
                 ("#696969", "#ffffff", "Helper text and identifying control border", 4.5),
                 ("#ffffff", "#333e48", "Header and tooltip text", 4.5),
                 ("#333e48", "#ffccd5", "Selected and error text", 4.5),
                 ("#ffffff", "#9e1b32", "Primary action text", 4.5),
                 ("#9e1b32", "#ffffff", "Focus and selected-control indicator", 3.0)]
        measurements = [{"foreground": front, "background": back, "use": use,
                         "ratio_unrounded": contrast(front, back), "minimum": threshold,
                         "method": "WCAG sRGB relative luminance; base-token computation"}
                        for front, back, use, threshold in pairs]
        if number == 1:
            for pair in metadata["styling_contract"]["contrast_checks"]:
                pair["ratio_unrounded"] = contrast(pair["foreground"], pair["background"])
                pair["ratio_approx"] = f"{pair['ratio_unrounded']:.6f}:1"
            metadata["accessibility_copy"]["narrow_queue"] = "At narrow widths, a named list of selected-state buttons shows ID, subject, priority, and status without horizontal scrolling; the desktop table is hidden from the accessibility tree."
        if number == 2:
            metadata["component"]["palette"]["tokens"]["border"] = "#696969"
            metadata["authored_component_copy"]["explain_action"] = "Explain selection"
            metadata["state_copy"]["explanation"] = "{id}: {title}. Saved priority: {priority}. Status: {status}."
            metadata["native_control_copy"]["controls"].append("Explain selection")
            metadata["terminal_text_fallback_copy"]["actions"] += ", (x) Explain selection"
        if number == 3:
            metadata["styling"]["semantic_tokens"]["border"] = "#696969"
        metadata["revision_provenance"] = {
            "source_run": run_id, "source_hashes": original,
            "purpose": "Corrected local project verification copy; original isolated-run outcomes remain unchanged.",
            "historical_task_flags": "Existing task flags describe the original generation. Independent correction checks are recorded separately.",
        }
        metadata["palette_bindings"] = {
            "source": "skills/desktop-plugin-ui/assets/palettes/colorset1.yml",
            "source_sha256": sha(PALETTE), "palette": "colorset1", "tokens": bindings,
            "contrast_measurements": measurements,
            "scope": "Exact opaque authored CSS colors; native browser controls, forced colors, antialiasing and host chrome remain distinct.",
        }
        metadata["tooltip_contract"] = {
            "accessible_description": "Exports only the current selection.",
            "behavior": "Visible on hover/focus, associated by aria-describedby, dismissed with Escape, and pointer-events:none.",
        }
        destination = HERE / f"component-{number}"
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "status-panel.html").write_text(html, encoding="utf-8")
        (destination / "component-copy.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        after = {name: sha(source / name) for name in original}
        if original != after:
            raise RuntimeError("Historical evidence changed during copy preparation")
        records.append({"component": number, "source_run": run_id, "historical_hashes": original,
                        "corrected_hashes": {name: sha(destination / name) for name in original}})
    (HERE / "provenance.json").write_text(json.dumps({"source_artifacts_unchanged": True, "components": records}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"prepared_components": len(records), "destination": str(HERE), "source_artifacts_unchanged": True}, indent=2))


if __name__ == "__main__":
    main()
