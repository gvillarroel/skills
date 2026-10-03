#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Freeze the complete-bundle study before live model comparisons."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svg-brief-design-procedural-20260926"
NEW_IMAGE = "sha256:1c1ac1dfdc903a9f3a64f4a3a75be7ab883a94647edac0045105d89674b4cbf8"
OLD_IMAGE = "sha256:f154aa38e1aad0dd0739800e9931a59e84252de6e934fe5a58b4ac181919110a"


def wsl(path):
    text = str(path).replace("\\", "/")
    return "/mnt/" + text[0].lower() + text[2:] if len(text) > 1 and text[1] == ":" else text


def hashes(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob("*")) if p.is_file() and p.suffix in {".md", ".yaml", ".py"}}


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(data, indent=2) + "\n")


def main():
    if (ROOT / "protocol.json").exists():
        raise SystemExit("The protocol is already frozen; do not replace it")
    source = REPO / "skills/svg-brief-design"
    baseline = ROOT / "baseline/skills/svg-brief-design"
    candidate = ROOT / "procedural-v1/skills/svg-brief-design"
    if candidate.exists():
        raise SystemExit("Candidate snapshot already exists")
    for name in hashes(source):
        target = candidate / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / name, target)
    base = json.loads((REPO / "evaluations/runs/svg-brief-design-20260925-r2/jobs/development.json").read_text())
    base.update(job_name="svg-procedural-development", n_attempts=3, n_concurrent_trials=3,
                jobs_dir=wsl(ROOT / "native-jobs"))
    base["environment"] = {"import_path": "procedural_environment:ProceduralEnvironment", "delete": True,
                           "kwargs": {"agent_image": NEW_IMAGE, "source_agent_image": OLD_IMAGE}}
    base["agents"] = [{"name": "pi-svg-procedural", "import_path": "pi_svg_procedural:PiSvgProcedural",
                       "model_name": "openai-codex/gpt-6-luna", "kwargs": {"version": "0.84.2"}}]
    write(ROOT / "templates/development.json", base)
    previous = json.loads((REPO / "evaluations/runs/svg-brief-design-deadline-20260926/evolution-async-compatible.json").read_text())
    validation = json.loads(json.dumps(base))
    validation["job_name"] = "svg-procedural-independent-validation"
    paths = previous["splits"]["validation"]
    validation["datasets"] = [{"path": str(Path(paths[0]).parent), "task_names": [Path(p).name for p in paths]}]
    write(ROOT / "templates/validation.json", validation)
    helpers = ["pi_svg_procedural.py", "procedural_environment.py", "run_procedural_population.py", "prepare_procedural_study.py"]
    protocol = {
        "schema_version": 1, "study": ROOT.name, "registered_at": datetime.now(timezone.utc).isoformat(),
        "authorization": "The user now permits original procedural SVG generators and editing guides. Purchased artwork and copied distinctive geometry remain excluded.",
        "method": "Installed harbor-population-search, complete-bundle development ranking, digest-frozen optimizer-invisible first validation gate; optional unused reserve remains closed.",
        "model": "openai-codex/gpt-6-luna", "thinking": "medium", "pi": "0.84.2", "transport": "sse",
        "tools_both_arms": ["read", "write", "bash"], "retries": 0, "attempts_per_task": 3,
        "budget": {"max_generations": 2, "max_development_calls": 72, "max_validation_calls": 18, "max_forward_calls": 7,
                   "rule": "One initial full-bundle comparison. At most one additional development revision, only if specific development evidence supports it. Stop after the second generation or unsupported/flat mechanisms. Freeze the highest qualified development candidate including baseline before private validation. No mutation after opening validation."},
        "reward": {"key": "visual_similarity", "formula": "Existing verifier v1.1.0: 0.6 shape + 0.4 style; unchanged", "pass_threshold": 0,
                   "required": {"artifact_valid": 1}, "minimum_development_pass_rate": 1,
                   "minimum_validation_mean_gain": .015, "allow_task_regressions": True,
                   "regression_policy": "Mean improvement may include per-task regressions because short briefs leave composition choices open. Every regression and visual defect must be reported. Any execution/provenance/validity failure disqualifies the candidate; no rerun of semantic outcomes."},
        "hypothesis": "Deterministic original scaffolds reduce incoherent repetition and attachment errors; recipes, boxed composition and a visible render/edit loop make detail refinement easier while preserving custom geometry for unsuitable subjects.",
        "preservation": "Exact prompt labels, output paths, monochrome transparent editable vectors, no asset copies; compare all six fixed public task families and inspect every output.",
        "discovery": "All 24 public development briefs and earlier public trials were available. An independent Luna pilot succeeded on a vertical flow but clipped a two-frond ornament; that retained failure motivated boxed composition and control-hull fitting before this comparison.",
        "privacy": "Only three previously unopened cyber-tribal validation cases enter the first independent gate. Generic foliage was exercised during discovery, so no family-unseen claim is made for the unused organic reserve. Purchased reference files never enter agent environments or skill bundles. No private instruction, reward or diagnostic may guide mutation.",
        "candidate_files": {"baseline": hashes(baseline), "procedural-v1": hashes(candidate)},
        "templates": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT / "templates").glob("*.json")},
        "runtime": {"agent_image": NEW_IMAGE, "source_agent_image": OLD_IMAGE,
                    "verifier_image": "sha256:f82f3a08d40b954417f8040d05f71213824906e312f477ac7ba0370e6b6427f7",
                    "declared_override": "Custom native environment changes only the old pinned agent image. The original separate tests/Dockerfile remains unchanged; source task checksums are preserved.",
                    "helpers": {name: hashlib.sha256((REPO / "projects/svg-brief-design/scripts" / name).read_bytes()).hexdigest() for name in helpers},
                    "dockerfile_sha256": hashlib.sha256((REPO / "projects/svg-brief-design/runtime/procedural-agent/Dockerfile").read_bytes()).hexdigest()},
        "limitations": "Similarity is a visual proxy, not semantic accuracy, copying detection, a license audit or a confidence estimate. Historical writing-only scores are not pooled with this full-tool condition. All failed trials and rejected candidates remain part of the record."
    }
    write(ROOT / "protocol.json", protocol)
    argv = ["--job-template", wsl(ROOT / "templates/development.json"), "--candidate", "baseline=" + wsl(baseline),
            "--candidate", "procedural-v1=" + wsl(candidate), "--baseline", "baseline", "--generation", "0",
            "--reward-key", "visual_similarity", "--pass-threshold", "0", "--minimum-development-pass-rate", "1",
            "--required-reward", "artifact_valid=1", "--minimum-holdout-gain", ".015", "--allow-task-regressions",
            "--output", wsl(ROOT / "population")]
    write(ROOT / "generation-000-argv.json", argv)
    print(json.dumps({"protocol": str(ROOT / "protocol.json"), "candidate_files": len(hashes(candidate)), "private_gate": "closed"}))


if __name__ == "__main__":
    main()
