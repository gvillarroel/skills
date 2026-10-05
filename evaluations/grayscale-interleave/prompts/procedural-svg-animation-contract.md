Use only the copied `procedural-svg-animation` bundle and normal local tools. Treat `skills/procedural-svg-animation/` as read-only. This is a focused test of the authored palette key that accompanies this skill's output, not a request to retrieve or regenerate source media. Do not read acceptance examples, other skills, repository documents or external source files. Write all outputs in this workspace.

Read the palette's categorical guidance, then run this command verbatim. Inspect its outputs and briefly describe the distinction between categorical allocation and a quantitative ramp.

```bash
python - <<'PY'
import json
from pathlib import Path
p = json.loads(Path('skills/procedural-svg-animation/assets/palettes/colorsets.json').read_text(encoding='utf-8'))['colorsets']
out = {'colorset1': p['colorset1'], 'colorset2': p['colorset2'], 'canvases': {}}
for canvas in ('#ffffff', '#000000', '#828282'):
    out['canvases'][canvas] = [token for token in p['colorset1']['solidSequence'] if token != canvas]
Path('contract.json').write_text(json.dumps(out, indent=2) + '\n', encoding='utf-8')
PY
```
