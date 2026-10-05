#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare narrow, skill-only palette authoring cases and backlog state."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
EVAL = ROOT / "evaluations/grayscale-interleave"
LABELS = ["Intake", "Triage", "Research", "Proposal", "Review", "Planning", "Design", "Build",
          "Test", "Repair", "Approval", "Release", "Observe", "Support", "Archive", "Learn", "Iterate"]


def main():
    (EVAL / "prompts").mkdir(parents=True, exist_ok=True)
    skills = sorted(path.parents[2].name for path in (ROOT / "skills").glob("*/assets/palettes/colorsets.json"))
    cases = {}
    for skill in skills:
        common = (f"Use only the copied `{skill}` bundle and normal local tools. Treat `skills/{skill}/` as read-only. "
                  "This is a focused test of the authored palette key that accompanies this skill's output, "
                  "not a request to retrieve or regenerate source media. Do not read acceptance examples, other skills, "
                  "repository documents or external source files. Write all outputs in this workspace.\n\n")
        contract = common + f"""Read the palette's categorical guidance, then run this command verbatim. Inspect its outputs and briefly describe the distinction between categorical allocation and a quantitative ramp.

```bash
python - <<'PY'
import json
from pathlib import Path
p = json.loads(Path('skills/{skill}/assets/palettes/colorsets.json').read_text(encoding='utf-8'))['colorsets']
out = {{'colorset1': p['colorset1'], 'colorset2': p['colorset2'], 'canvases': {{}}}}
for canvas in ('#ffffff', '#000000', '#828282'):
    out['canvases'][canvas] = [token for token in p['colorset1']['solidSequence'] if token != canvas]
Path('contract.json').write_text(json.dumps(out, indent=2) + '\\n', encoding='utf-8')
PY
```
"""
        natural = common + f"""Create a small standalone SVG key for a multi-panel explanation using Colorset1 on a white canvas. The key shows seventeen distinct categories in this exact reading order: {', '.join(LABELS)}. Assign category styles according to the bundle's current solid allocation priority, excluding the actual canvas token. Keep identities stable; exhaust all usable opaque borderless solid fills before using the first overflow style. Put complete, readable labels inside each body using the bundle's black/white contrast choice. Use clear spacing and at least 18 px text. Give the SVG an accessible title and description. No JavaScript or external resources are needed for this supporting key.

Separately show a quantitative legend labeled 'Low', 'Medium-low', 'Medium', 'Medium-high', 'High', using the supplied ordered ramp #1c1c1c, #4f4f4f, #828282, #b5b5b5, #e7e7e7. Keep its quantitative order intact.

Write exactly `key.svg` and `allocation.json`. Mark each actual category body with `data-category-index` from 0 to 16, and mark its label with `data-category-label` equal to that index. Mark each quantitative body with `data-quantitative-index` from 0 to 4. The JSON must contain `canvas`, a `categories` array of seventeen objects with `index`, `label`, `fill`, `text`, and `stroke` (use 'none' for no border), and a `quantitativeRamp` array with the five supplied tokens. Set SVG width and height so every body and complete label is visible at its native size. Inspect the written SVG structure and JSON before finishing.
"""
        for name, prompt in (("contract", contract), ("naturalistic", natural)):
            (EVAL / f"prompts/{skill}-{name}.md").write_text(prompt, encoding="utf-8")
        cases[skill] = {"model": "openai-codex/gpt-5.6-luna", "contract": {"prompt": f"prompts/{skill}-contract.md", "outputs": ["contract.json"], "repetitions": 1},
                        "naturalistic": {"prompt": f"prompts/{skill}-naturalistic.md", "outputs": ["key.svg", "allocation.json"], "repetitions": 3}}
    (EVAL / "cases.json").write_text(json.dumps(cases, indent=2) + "\n", encoding="utf-8")
    backlog = ROOT / "SKILLS.md"
    lines = backlog.read_text(encoding="utf-8").splitlines()
    original = {}
    note = (" Grayscale interleave revision 2026-10-05: validating the categorical dark/middle alternation with unchanged tokens, roles, text choices, Colorset2 and quantitative ramps. "
            "Scoped palette-key forward-test model: `openai-codex/gpt-5.6-luna`, an evaluation-only exception after the retained Spark account/provider rejection. "
            "[Frozen protocol and scope](evaluations/grayscale-interleave/protocol.md).")
    for i, line in enumerate(lines):
        fields = line.split("|")
        if len(fields) > 4 and fields[1].strip() in skills:
            skill = fields[1].strip()
            original[skill] = fields[2].strip().strip('`')
            fields[2] = " `validating` "
            fields[-2] = fields[-2].rstrip() + note + " "
            lines[i] = "|".join(fields)
    state = ROOT / "projects/grayscale-interleave/artifacts/manifests/backlog-before.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    if state.exists():
        raise ValueError("Preparation is one-shot; preserve the recorded original statuses")
    state.write_text(json.dumps(original, indent=2) + "\n", encoding="utf-8")
    backlog.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Prepared {len(cases)} isolated palette-key cohorts and recorded original backlog statuses.")


if __name__ == "__main__":
    main()
