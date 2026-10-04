Run the exact compact standalone command below and inspect its outputs. Treat `skills/mermaid/` as read-only. Use only the copied skill and normal local tools; do not inspect acceptance examples, sibling skills, parent run records, repository context, or outside source files. Keep generated files in this workspace. The contract records the public allocator's returned styles on two actual canvases, including its first overflow slot, or exercises the owning native builder. Do not alter the bundled helpers.

```bash
python - <<'PY'
import json, sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, "skills/mermaid/scripts")
import palette_paints as helper
palettes = json.loads(Path("skills/mermaid/assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
result = {"colorset": "colorset1", "canvases": []}
for canvas in ("#ffffff", "#000000"):
    count = len([paint for paint in palettes["colorset1"]["solidSequence"] if paint != canvas])
    styles = [helper.solid_style(index, 'colorset1', canvas) for index in range(count + 1)]
    result["canvases"].append({"canvas": canvas, "styles": styles})
Path("contract.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
PY
python - <<'PY'
import json
from pathlib import Path
record=json.loads(Path('contract.json').read_text(encoding='utf-8'))
styles=record['canvases'][0]['styles']
lines=['flowchart TB','accTitle: Category allocation','accDescr: Seventeen ordered category nodes with directed relationships.']
for index,style in enumerate(styles):
    lines.append(f'N{index}["Group {index}"]:::slot{index}')
    lines.append(f'classDef slot{index} fill:{style["fill"]},color:{style["text"]},stroke:{style["stroke"]},stroke-width:{style["strokeWidth"]}px;')
    if index: lines.append(f'N{index-1} --> N{index}')
Path('priority.mmd').write_text('\n'.join(lines)+'\n',encoding='utf-8')
PY
uv run --script skills/mermaid/scripts/style_mermaid_directory.py priority.mmd --colorset colorset1 --write --require-accessibility --report style-report.json
uv run --script skills/mermaid/scripts/animate_mermaid_svg.py priority.mmd --static-output priority.svg --output priority.animated.svg --animation none --require-accessibility
```
