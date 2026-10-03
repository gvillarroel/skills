#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["harbor==0.18.0", "PyYAML>=6,<7"]
# ///
"""Freeze one documented-entrypoint revision from public development evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from harbor.models.job.config import JobConfig
from prepare_procedural_study import hashes, write

ROOT = Path(__file__).resolve().parents[3] / "evaluations/runs/svp3"


def main():
    source, child = ROOT / "inputs/p/svg-brief-design", ROOT / "inputs/q/svg-brief-design"
    evidence = ROOT / "generation-000/candidates/p/harbor-jobs/harbor-pop-g000-p/vector-004--eb6eabbcb9ca2ad4__tBAg39x"
    result = json.loads((evidence / "result.json").read_text())
    assert result["exception_info"]["exception_message"] == "Pi tool error"
    trace = (evidence / "agent/pi.txt").read_text()
    assert "cannot import name 'svg_to_png'" in trace
    shutil.copytree(source, child)
    path = child / "SKILL.md"
    before = path.read_text()
    old = """With execution tools, render the generated SVG and open the preview. The helper
uses pinned Python dependencies through `uv`; with those dependencies already
installed, the same script also runs with `python`:

```text
uv run --script <skill-root>/scripts/render_svg.py artwork.svg --output preview.png
```"""
    new = """With execution tools, render the generated SVG and open the preview. Use the
bundled renderer as the documented entry point; do not guess a rendering
library's function names or keyword arguments. When the Python dependencies
are already installed, run this exact command with your actual file paths:

```text
python <skill-root>/scripts/render_svg.py artwork.svg --output preview.png
```

If dependencies are missing and `uv` is available, it can provision the pinned
dependencies and invoke the same helper:

```text
uv run --script <skill-root>/scripts/render_svg.py artwork.svg --output preview.png
```"""
    assert before.count(old) == 1
    path.write_text(before.replace(old, new), encoding="utf-8")
    parent_hashes, child_hashes = hashes(source), hashes(child)
    assert [name for name in parent_hashes if parent_hashes[name] != child_hashes[name]] == ["SKILL.md"]
    template = json.loads((ROOT / "templates/development.json").read_text())
    template["job_name"], template["jobs_dir"] = "q", str(ROOT / "jobs")
    template["agents"][0]["skills"] = [str(child)]
    validated = JobConfig.model_validate(template).model_dump(mode="json", exclude_none=True)
    write(ROOT / "q-job.json", validated)
    write(ROOT / "q-mutation.json", {"created_at": datetime.now(timezone.utc).isoformat(),
          "mechanism": "Prefer the actual bundled Python renderer entrypoint in installed-dependency environments; retain uv as a conditional fallback and forbid guessed library API calls.",
          "scope": "SKILL.md render paragraph only; all executable geometry, tests, references and UI metadata remain byte-identical.",
          "evidence_result_sha256": hashlib.sha256((evidence / "result.json").read_bytes()).hexdigest(),
          "evidence_trace_sha256": hashlib.sha256((evidence / "agent/pi.txt").read_bytes()).hexdigest(),
          "parent_files": parent_hashes, "child_files": child_hashes,
          "expected_effect": "Remove the observed avoidable ImportError while retaining correct render-and-inspect behavior and the original brief interpretation.",
          "preservation_check": "All six public tasks, three repeats each, same native image/agent/tools/verifier; compare against the frozen contemporaneous 18-trial baseline. Keep the failed p trial unchanged.",
          "model_call_cap": 18, "native_job_sha256": hashlib.sha256((ROOT / "q-job.json").read_bytes()).hexdigest(),
          "private_gate_opened": False})
    print(json.dumps({"candidate": "q", "changed_files": ["SKILL.md"], "max_new_calls": 18}))


if __name__ == "__main__":
    main()
