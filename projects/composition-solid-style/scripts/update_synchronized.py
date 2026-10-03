#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply synchronized node/chrome solid-first paint changes."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3] / "skills/compose-synchronized-svg"
path=ROOT/'scripts/compose_synchronized_svg.py'
s=path.read_text(encoding='utf-8')
s=s.replace('f\'stroke="{esc(color)}" stroke-opacity="0.28" stroke-width="5"/>\'','f\'stroke="none" stroke-width="0"/>\'')
s=s.replace('f\'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(radius)}" fill="var(--surface)" \'\n                f\'stroke="{esc(color)}" stroke-width="3"/>\'', 'f\'<circle cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(radius)}" fill="{esc(color)}" \'\n                f\'stroke="none" stroke-width="0"/>\'')
s=s.replace('f\'fill="var(--surface)" stroke="{esc(color)}" \'\n                    f\'stroke-opacity="0.36" stroke-width="1.2"/>\'', 'f\'fill="{esc(color)}" stroke="none" stroke-width="0"/>\'')
s=s.replace('module_id,\n                        info,\n                        x,\n                        y + 4,', 'module_id,\n                        solid_binding(plan, info),\n                        x,\n                        y + 4,')
s=s.replace('f\'font-size="14" font-weight="780" fill="var(--ink)" aria-hidden="true">\'', 'f\'font-size="14" font-weight="780" fill="{text_on_fill(color if color.startswith("#") else "#696969")}" aria-hidden="true">\'')
s=s.replace('fill="var(--surface)" stroke="var(--line)" stroke-width="1"/>', 'fill="var(--surface)" stroke="none" stroke-width="0"/>')
s=s.replace('for info in texts:\n            x, y = positions[info.value_id]', 'for info in texts:\n            info = solid_binding(plan, info)\n            x, y = positions[info.value_id]')
s=s.replace('data-dependency-node="{esc(info.value_id)}" fill="var(--surface)" stroke="{esc(info.color)}"', 'data-dependency-node="{esc(info.value_id)}" fill="{esc(info.color)}" stroke="none"')
s=s.replace('font-size="{8 if dense else 10}" fill="var(--muted)"', 'font-size="{8 if dense else 10}" fill="{esc(info.text_color)}"')
s=s.replace('fill="var(--surface-subtle)" stroke="var(--line)"', 'fill="var(--surface-subtle)" stroke="none"')
path.write_text(s,encoding='utf-8',newline='\n')

path=ROOT/'scripts/scaffold_synchronized_svg.py'
s=path.read_text(encoding='utf-8').replace('from palette_contract import require_color','from palette_contract import require_color, text_on_fill')
# The solid index is semantic; labels on separate light plaques remain black.
s=s.replace('style="--district-accent: {esc(district["accent"])};"', 'style="--district-accent: {esc(district["accent"])}; --on-district: {text_on_fill(district["accent"])};"')
s=s.replace('style="--district-accent: {district_accent};"', 'style="--district-accent: {district_accent}; --on-district: {text_on_fill(district_accent) if district_accent.startswith("#") else "#ffffff"};"')
s=s.replace('.module-frame {{ fill: var(--surface); fill-opacity: 1; stroke: var(--line);', '.module-frame {{ fill: var(--surface); fill-opacity: 1; stroke: none;')
s=s.replace('.placeholder-mark {{ fill: var(--accent-soft); stroke: var(--accent);', '.placeholder-mark {{ fill: var(--accent); stroke: none;')
s=s.replace('fill: var(--surface); stroke: var(--district-accent);', 'fill: var(--district-accent); stroke: none;')
s=s.replace('.world-module-node-halo {{ fill: var(--district-accent); fill-opacity: 0.14; stroke: var(--district-accent);', '.world-module-node-halo {{ fill: none; fill-opacity: 0; stroke: none;')
s=s.replace('.district-hub-halo {{ fill: var(--district-accent); fill-opacity: 0.12; stroke: var(--district-accent);', '.district-hub-halo {{ fill: none; fill-opacity: 0; stroke: none;')
s=s.replace('.world-module-node-index {{ font-size: 40px; font-weight: 840; fill: var(--ink);', '.world-module-node-index {{ font-size: 40px; font-weight: 840; fill: var(--on-district);')
s=s.replace('.district-index {{ font-size: 42px; font-weight: 820; fill: var(--ink);', '.district-index {{ font-size: 42px; font-weight: 820; fill: var(--on-district);')
s=s.replace('fill: var(--surface); fill-opacity: 1; stroke: var(--district-accent);', 'fill: var(--surface); fill-opacity: 1; stroke: none;')
s=s.replace('fill: var(--surface-subtle); stroke: var(--district-accent);', 'fill: var(--surface-subtle); stroke: none;')
s=s.replace('fill-opacity: 1; stroke: var(--district-accent); stroke-width: 2;', 'fill-opacity: 1; stroke: none; stroke-width: 0;')
s=s.replace('.header-plaque {{ fill: var(--surface-subtle); fill-opacity: 1; stroke: var(--line);', '.header-plaque {{ fill: var(--surface-subtle); fill-opacity: 1; stroke: none;')
s=s.replace('.control-button rect {{ fill: var(--surface); stroke: var(--line);', '.control-button rect {{ fill: var(--surface); stroke: none;')
s=s.replace('.module-focus-control rect {{ fill: var(--accent-soft); stroke: var(--muted);', '.module-focus-control rect {{ fill: var(--accent); stroke: none;')
s=s.replace('.module-focus-control text {{', '.module-focus-control text {{ fill: #ffffff;')
s=s.replace('.navigation-hud-panel {{ fill: var(--ink); fill-opacity: 1; stroke: var(--ink);', '.navigation-hud-panel {{ fill: var(--ink); fill-opacity: 1; stroke: none;')
s=s.replace('.navigation-control rect {{ fill: var(--ink); stroke: var(--on-ink-muted);', '.navigation-control rect {{ fill: var(--ink); stroke: none;')
path.write_text(s,encoding='utf-8',newline='\n')
print('Updated synchronized surface painting.')
