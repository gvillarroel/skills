Run the exact compact standalone command below and inspect its outputs. Treat `skills/plantuml-colorset-renderer/` as read-only. Use only the copied skill and normal local tools; do not inspect acceptance examples, sibling skills, parent run records, repository context, or outside source files. Keep generated files in this workspace. The contract records the public allocator's returned styles on two actual canvases, including its first overflow slot, or exercises the owning native builder. Do not alter the bundled helpers.

```bash
python - <<'PY'
import json, sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, "skills/plantuml-colorset-renderer/scripts")
import palette_paints as helper
palettes = json.loads(Path("skills/plantuml-colorset-renderer/assets/palettes/colorsets.json").read_text(encoding="utf-8"))["colorsets"]
result = {"colorset": "colorset1", "canvases": []}
for canvas in ("#ffffff", "#000000"):
    count = len([paint for paint in palettes["colorset1"]["solidSequence"] if paint != canvas])
    styles = [helper.solid_style(index, 'colorset1', canvas) for index in range(count + 1)]
    result["canvases"].append({"canvas": canvas, "styles": styles})
Path("contract.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
PY
python - <<'PY'
from pathlib import Path
Path('source').mkdir()
Path('source/priority.puml').write_text('@startuml\ntitle Delivery architecture\ncomponent Intake\ncomponent Review\ndatabase Record\ncloud Archive\nIntake --> Review\nReview --> Record\nRecord --> Archive\n@enduml\n',encoding='utf-8')
PY
uv run --script skills/plantuml-colorset-renderer/scripts/render_plantuml_directory.py source --output renders --colorset colorset1 --engine cli --format svg --format png --report render-report.json
```
