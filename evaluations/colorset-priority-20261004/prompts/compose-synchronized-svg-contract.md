Run the exact compact standalone command below and inspect its outputs. Treat `skills/compose-synchronized-svg/` as read-only. Use only the copied skill and normal local tools; do not inspect acceptance examples, sibling skills, parent run records, repository context, or outside source files. Keep generated files in this workspace. The contract records the public allocator's returned styles on two actual canvases, including its first overflow slot, or exercises the owning native builder. Do not alter the bundled helpers.

```bash
python - <<'PY'
import json, sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, "skills/compose-synchronized-svg/scripts")
import palette_contract as helper
palettes = json.loads(Path("skills/compose-synchronized-svg/assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
result = {"colorset": "colorset1", "canvases": []}
for canvas in ("#ffffff", "#000000"):
    count = len([paint for paint in palettes["colorset1"]["solidSequence"] if paint != canvas])
    styles = [helper.category_style(index, 'colorset1', canvas) for index in range(count + 1)]
    result["canvases"].append({"canvas": canvas, "styles": styles})
Path("contract.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
PY
python - <<'PY'
import json
from pathlib import Path
plan=json.loads(Path('skills/compose-synchronized-svg/assets/templates/composition-plan.json').read_text(encoding='utf-8'))
plan['theme']={'preset':'colorset1'}
Path('composition-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
PY
uv run --script skills/compose-synchronized-svg/scripts/compose_synchronized_svg.py --spec composition-plan.json --output priority.svg --report priority-report.json
```
