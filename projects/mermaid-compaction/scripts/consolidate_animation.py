#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Snapshot the runtime bundle and consolidate animation without changing AST bodies."""
from __future__ import annotations

import ast
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILL = ROOT / "skills/mermaid"
ARTIFACTS = ROOT / "projects/mermaid-compaction/artifacts"
BASELINE = ARTIFACTS / "baseline"
MODULES = ("common", "diagrams", "discovery", "planning", "style", "directives", "rendering")


def main() -> None:
    if BASELINE.exists():
        raise SystemExit("Baseline already exists; preserve it and do not repeat this migration.")
    files = sorted(p for p in SKILL.rglob("*") if p.is_file()
                   and not {"__pycache__", "examples", "node_modules"}.intersection(p.parts))
    inventory = []
    for source in files:
        target = BASELINE / source.relative_to(SKILL)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        inventory.append({"path": source.relative_to(SKILL).as_posix(),
                          "bytes": source.stat().st_size,
                          "sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    (ARTIFACTS / "baseline-manifest.json").write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")

    paths = [BASELINE / f"scripts/mermaid_animation/{name}.py" for name in MODULES]
    paths.append(BASELINE / "scripts/animate_mermaid_svg.py")
    imports, bodies, bindings = {}, [], {}
    for path in paths:
        source = path.read_text(encoding="utf-8")
        lines = source.splitlines(keepends=True)
        nodes = ast.parse(source).body
        for node in nodes:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.ImportFrom) and (node.module == "__future__" or node.module.startswith("mermaid_animation")):
                    continue
                imports.setdefault(ast.dump(node), ast.get_source_segment(source, node))
                continue
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                continue
            names = [node.name] if isinstance(node, (ast.FunctionDef, ast.ClassDef)) else []
            if isinstance(node, ast.Assign):
                names = [target.id for target in node.targets if isinstance(target, ast.Name)]
            for name in names:
                if name in bindings:
                    raise RuntimeError(f"Global name collision: {name}: {bindings[name]} / {path}")
                bindings[name] = path.name
        omitted = set()
        for node in nodes:
            if isinstance(node, (ast.Import, ast.ImportFrom)) or (
                isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
            ):
                omitted.update(range(node.lineno - 1, node.end_lineno))
        first_body = next(node for node in nodes if not isinstance(node, (ast.Import, ast.ImportFrom))
                          and not (isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)))
        start = min([first_body.lineno] + [decorator.lineno for decorator in getattr(first_body, "decorator_list", [])]) - 1
        body = "".join(line for i, line in enumerate(lines) if i >= start and i not in omitted).strip()
        bodies.append(f"# --- {path.stem}: consolidated runtime section ---\n\n{body}")
    header = '''#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Render and animate Mermaid SVGs. Execute this CLI; read sections only for debugging."""
from __future__ import annotations
'''
    output = header + "\n" + "\n".join(imports.values()) + "\n\n\n" + "\n\n\n".join(bodies) + "\n"
    ast.parse(output)
    (SKILL / "scripts/animate_mermaid_svg.py").write_text(output, encoding="utf-8", newline="\n")
    print(json.dumps({"baselineFiles": len(inventory), "baselineBytes": sum(f["bytes"] for f in inventory),
                      "consolidatedBytes": len(output.encode()), "globalBindings": len(bindings)}, indent=2))


if __name__ == "__main__":
    main()
