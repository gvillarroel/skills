#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Independently inspect a freshly generated Durable subagent/evolution project.

This evaluator reads generated outputs; it does not import the skill, trust a
candidate's self-report, install dependencies, or mutate the generated project.
Run: uv run --script evaluations/contracts/pi-durable-templates.py WORKSPACE
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path, PurePosixPath


class Contract:
    def __init__(self, workspace: Path, project: Path):
        self.workspace = workspace.resolve()
        self.project = project.resolve()
        self.checks: list[dict] = []

    def check(self, name, action):
        try:
            details = action()
            self.checks.append({"name": name, "passed": True, "details": details})
        except (AssertionError, OSError, ValueError, KeyError, TypeError, SyntaxError, subprocess.SubprocessError) as error:
            self.checks.append({"name": name, "passed": False, "error": str(error) or type(error).__name__})

    def local(self, relative: str) -> Path:
        assert isinstance(relative, str) and relative, "Expected a nonempty project-relative path."
        parts = PurePosixPath(relative).parts
        assert not relative.startswith("/") and "\\" not in relative and ":" not in relative, f"Nonportable path: {relative}"
        assert all(part not in (".", "..") for part in parts), f"Escaping path: {relative}"
        result = self.project.joinpath(*parts)
        current = self.project
        assert not current.is_symlink() and not getattr(current, "is_junction", lambda: False)(), "Project root must not be a link."
        for part in parts:
            current /= part
            assert not current.is_symlink() and not getattr(current, "is_junction", lambda: False)(), f"Linked project input: {relative}"
        assert result.resolve().is_relative_to(self.project), f"Escaping project input: {relative}"
        assert result.is_file(), f"Missing project file: {relative}"
        return result

    def load(self, relative: str):
        return json.loads(self.local(relative).read_text(encoding="utf-8"))


def require(condition, message):
    assert condition, message


def bounded_integer(value, low, high, name):
    require(type(value) is int and low <= value <= high, f"{name} must be an integer between {low} and {high}.")


def validate(args) -> dict:
    workspace = args.workspace.resolve()
    project = args.project or Path("outputs/team")
    if not project.is_absolute():
        project = workspace / project
    contract = Contract(workspace, project)
    allowed_changes = set(args.allow_changed)

    def required_files():
        names = ["AGENTS.md", "package.json", "package-lock.json", "tsconfig.json", "config.json",
                 "config.codex.example.json", "scaffold-manifest.json", "scripts/project.py",
                 "src/subagents.ts", "src/subagents-smoke.ts", "src/runtime.ts", "src/evolution.ts",
                 "src/evolve-cli.ts", "evolution-plans/study.py", "evolution-plans/plan.json",
                 "evolution-plans/catalog.json", "evolution-plans/reflection.md",
                 "evolution-plans/sources.md", "evolution-plans/release-record.md",
                 "evolution-plans/validation-gate.json", "evolution-plans/holdout-gate.json"]
        for name in names:
            contract.local(name)
        return {"files": names}
    contract.check("complete_independent_project", required_files)

    def manifest_hashes():
        manifest = contract.load("scaffold-manifest.json")
        require(manifest.get("runtimeIndependent") is True, "Manifest must declare runtime independence.")
        require(manifest.get("runtimeSource", {}).get("version") == "1.3.0", "Expected pinned Durable runtime source identity.")
        if args.profile:
            require(manifest.get("profile") == args.profile, "Generated profile differs from the requested profile.")
        if args.strategy:
            require(manifest.get("evolutionStrategy") == args.strategy, "Generated strategy differs from the requested strategy.")
        files = manifest.get("files")
        require(isinstance(files, dict) and len(files) >= 25, "Manifest must inventory the complete application, not a placeholder.")
        require("scaffold-manifest.json" not in files, "Manifest must not claim to hash itself.")
        protected = {"src/subagents.ts", "src/subagents-smoke.ts", "src/runtime.ts", "src/evolution.ts",
                     "src/evolve-cli.ts", "evolution-plans/study.py", "evolution-plans/plan.json",
                     "evolution-plans/task-verifier.mjs", "scripts/task-policy.mjs", "package-lock.json"}
        require(protected <= files.keys(), "Initial inventory omits required executable or evaluator resources.")
        require(allowed_changes <= files.keys(), "Every authorized changed path must belong to the initial manifest.")
        differences = []
        for name, expected in files.items():
            require(isinstance(expected, str) and re.fullmatch(r"[a-f0-9]{64}", expected), f"Invalid initial hash: {name}")
            observed = hashlib.sha256(contract.local(name).read_bytes()).hexdigest()
            if observed != expected:
                differences.append(name)
        require(set(differences) <= allowed_changes, f"Unapproved source changes after scaffolding: {differences}")
        return {"initial_files": len(files), "authorized_changes": sorted(allowed_changes), "observed_changes": differences,
                "profile": manifest.get("profile"), "strategy": manifest.get("evolutionStrategy")}
    contract.check("portable_initial_source_hashes", manifest_hashes)

    def dependencies_and_commands():
        package = contract.load("package.json")
        dependencies = package.get("dependencies", {})
        require(dependencies.get("@earendil-works/pi-durable") == "1.3.0", "Durable dependency must be pinned to the tested runtime.")
        require(package.get("type") == "module", "Generated project must declare its JavaScript module format.")
        scripts = package.get("scripts", {})
        for name in ("build", "smoke", "subagents:smoke", "evolve"):
            require(isinstance(scripts.get(name), str) and scripts[name], f"Missing runnable project command: {name}")
        require("subagents-smoke" in scripts["subagents:smoke"], "Specialist smoke command must invoke its own runtime fixture.")
        require(contract.load("package-lock.json").get("lockfileVersion") in (2, 3), "Missing standalone npm lockfile.")
        return {"runtime": dependencies["@earendil-works/pi-durable"], "scripts": scripts}
    contract.check("pinned_runtime_and_local_commands", dependencies_and_commands)

    def roles_and_models():
        config = contract.load("config.json")
        require(config.get("provider", {}).get("kind") == "faux", "Default generated project must remain offline.")
        require(config.get("github", {}).get("mode") == "off", "Fresh generated project must not watch live repositories automatically.")
        require(config.get("host") == "127.0.0.1", "Default console must bind loopback.")
        data_dir = config.get("dataDir", "")
        require(isinstance(data_dir, str) and data_dir and not re.match(r"^(?:[a-zA-Z]:|[/\\])", data_dir), "Fresh project state must use a portable relative location.")
        agents = config.get("agents")
        require(isinstance(agents, list) and agents, "A named resident coordinator is required.")
        identities, role_ids = set(), []
        for agent in agents:
            require(re.fullmatch(r"[a-z][a-z0-9-]{0,47}", agent.get("id", "")), "Agent identity must be portable and explicit.")
            require(agent["id"] not in identities, "Agent identities must be unique.")
            identities.add(agent["id"])
            if agent.get("instructionsFile"):
                require(contract.local(agent["instructionsFile"]).read_text(encoding="utf-8").strip(), "Empty coordinator prompt.")
            settings = agent.get("subagents")
            require(isinstance(settings, dict), "The generated coordinator must configure specialist delegation.")
            for name, low, high in (("maxChildrenPerCall", 1, 8), ("maxChildrenPerRun", 1, 32),
                                    ("maxTaskChars", 128, 24000), ("maxResultChars", 256, 48000)):
                bounded_integer(settings.get(name), low, high, name)
            require(settings["maxChildrenPerCall"] <= settings["maxChildrenPerRun"], "Per-run cap must permit at least one configured call.")
            roles = settings.get("roles")
            require(isinstance(roles, list) and 1 <= len(roles) <= 8, "Configure from one to eight explicit roles.")
            seen = set()
            for role in roles:
                identity = role.get("id", "")
                require(re.fullmatch(r"[a-z][a-z0-9-]{0,47}", identity) and identity not in seen, "Specialist IDs must be unique portable names.")
                seen.add(identity)
                require(isinstance(role.get("instructions"), str) and role["instructions"].strip(), "Every role requires explicit instructions.")
                require(isinstance(role.get("instructionsFile"), str), "Every role requires its standalone prompt file.")
                require(contract.local(role["instructionsFile"]).read_text(encoding="utf-8").strip(), "Empty specialist prompt.")
                role_ids.append(identity)
        live = contract.load("config.codex.example.json")
        require(live.get("provider", {}).get("kind") == "openai-codex" and live["provider"].get("model") == args.live_model, "Live example must preserve the explicitly expected model or selection policy.")
        if args.live_model == "latest":
            require(live["provider"].get("catalogMode") == "refresh", "A latest live example must refresh its current catalog.")
        require([agent.get("id") for agent in live.get("agents", [])] == [agent["id"] for agent in agents], "Live example must preserve the named agents.")
        return {"agents": sorted(identities), "roles": role_ids, "default_provider": "faux", "live_model": "openai-codex/" + args.live_model}
    contract.check("explicit_specialists_bounds_and_models", roles_and_models)

    def evolution_plan():
        plan = contract.load("evolution-plans/plan.json")
        strategy = plan.get("strategy")
        require(strategy in ("trace-distillation", "population", "pareto"), "Choose an implemented local evolution strategy.")
        if args.strategy:
            require(strategy == args.strategy, "Plan does not implement the requested strategy.")
        require(plan.get("version") == 1, "Unsupported evolution plan version.")
        config = contract.load("config.json")
        require(plan.get("agentId") in {agent["id"] for agent in config["agents"]}, "Evolution plan must target a configured agent.")
        require(isinstance(plan.get("goal"), str) and len(plan["goal"]) > 20, "Evolution needs a concrete observable goal.")
        for name, low, high in (("maxCandidates", 1, 32), ("maxGenerations", 1, 8), ("maxWallSeconds", 30, 86400), ("timeoutMs", 100, 600000)):
            bounded_integer(plan.get(name), low, high, name)
        gain = plan.get("minimumImprovement")
        require(type(gain) in (int, float) and math.isfinite(gain) and 0 < gain <= 1, "Minimum improvement must be finite and positive.")
        paths = plan.get("allowedPaths")
        require(isinstance(paths, list) and paths and len(set(paths)) == len(paths), "Declare exact unique mutable task files.")
        for path in paths:
            contract.local(path)
            require(path.startswith(("prompts/", "src/tools/", "scripts/")), f"Evolution target is outside task/prompt surfaces: {path}")
            require(path not in ("scripts/project.py",), "Operational manager cannot be a task-policy mutation target.")
        fixtures_by_stage = {}
        for stage, gate in (("development", plan.get("development")), ("validation", contract.load("evolution-plans/validation-gate.json")), ("holdout", contract.load("evolution-plans/holdout-gate.json"))):
            require(isinstance(gate, dict) and set(gate) == {"verifierPath", "fixturePaths"}, f"Invalid {stage} gate contract.")
            contract.local(gate["verifierPath"])
            require(gate["verifierPath"] not in paths, "Verifier must be outside the editable candidate surface.")
            fixtures = gate["fixturePaths"]
            require(isinstance(fixtures, list) and fixtures and len(set(fixtures)) == len(fixtures), f"Missing unique {stage} fixtures.")
            for fixture in fixtures:
                contract.local(fixture)
                require(fixture not in paths, "Frozen fixtures must be outside the editable candidate surface.")
            fixtures_by_stage[stage] = fixtures
        require(not (set(fixtures_by_stage["development"]) & set(fixtures_by_stage["validation"])), "Development and validation cannot reuse fixture paths.")
        require(not (set(fixtures_by_stage["holdout"]) & set(fixtures_by_stage["development"] + fixtures_by_stage["validation"])), "Holdout must use separate fixture paths.")
        for stage in ("validation", "holdout"):
            name = plan.get(stage + "Commitment")
            require(isinstance(name, str) and name.startswith("evolution-plans/") and ".." not in PurePosixPath(name).parts, f"Declare a local opaque {stage} commitment path before opening the study.")
        return {"strategy": strategy, "allowed_paths": paths, "fixture_paths": fixtures_by_stage,
                "qualification_scope": "Structural separation only; semantic independence and private access require curator review."}
    contract.check("bounded_evolution_and_separate_curator_contracts", evolution_plan)

    def independent_source_surface():
        manifest = contract.load("scaffold-manifest.json")
        problem_paths = []
        for relative in manifest["files"]:
            path = contract.local(relative)
            if path.suffix.lower() not in (".py", ".ts", ".js", ".mjs", ".cjs", ".json", ".md", ".yaml", ".yml"):
                continue
            text = path.read_text(encoding="utf-8")
            # Repository-relative provenance such as knowledge:docs/... is allowed.
            if re.search(r"(?i)(?:[a-z]:[/\\]|/Users/|/home/)[^\r\n\"']*(?:\.agents[/\\]skills|dev[/\\]skills|skills[/\\]pi-durable)", text):
                problem_paths.append(relative)
            if path.suffix.lower() == ".json" and relative in ("package.json", "package-lock.json") and re.search(r'"(?:file:|link:)[^\"]+"', text):
                problem_paths.append(relative)
        require(not problem_paths, f"Generated project depends on source installation paths: {sorted(set(problem_paths))}")
        return {"authored_files_inspected": len(manifest["files"]), "external_skill_paths": []}
    contract.check("no_original_skill_runtime_dependency", independent_source_surface)

    def syntax_checks():
        python_files = ("scripts/project.py", "evolution-plans/study.py")
        for name in python_files:
            compile(contract.local(name).read_text(encoding="utf-8"), name, "exec")
        node = shutil.which("node")
        require(node is not None, "Node is required for independent JavaScript syntax checks.")
        checked = []
        for name in ("scripts/task-policy.mjs", "evolution-plans/task-verifier.mjs"):
            result = subprocess.run([node, "--check", str(contract.local(name))], cwd=contract.project,
                                    capture_output=True, text=True, encoding="utf-8", timeout=20, shell=False)
            require(result.returncode == 0, f"Node syntax check failed for {name}: {result.stderr[-2000:]}")
            checked.append(name)
        return {"python_compiled_without_writes": list(python_files), "node_syntax_checks": checked,
                "dependency_installation_performed": False}
    contract.check("generated_entrypoint_syntax", syntax_checks)

    def claimed_report():
        report_path = workspace / args.claimed_report
        require(report_path.is_file(), f"Missing required generated report: {args.claimed_report}")
        value = json.loads(report_path.read_text(encoding="utf-8"))
        require(isinstance(value, dict) and value, "Generated report must be a nonempty JSON object.")
        return {"path": str(report_path), "keys": sorted(value), "claims_are_not_verification": True}
    contract.check("required_model_report_is_valid_json", claimed_report)

    notes = args.notes
    if notes is None and (workspace / "outputs/notes.md").is_file():
        notes = Path("outputs/notes.md")
    if notes is not None:
        def inspect_notes():
            path = notes if notes.is_absolute() else workspace / notes
            require(path.is_file(), "Requested notes artifact is missing.")
            text = path.read_text(encoding="utf-8")
            require(len(text.strip()) >= 200, "Notes must explain the generated choices and operational limits.")
            require(re.search(r"(?i)select|finalist|next.study", text), "Notes must explain finalist selection or next-study scope.")
            require(re.search(r"(?i)curator|independent|validation", text), "Notes must explain independent evaluation ownership.")
            require(re.search(r"(?i)synthetic|mechanic|not (?:prove|establish|implement)|unverified|limitation", text), "Notes must state the evidence limits.")
            return {"path": str(path), "characters": len(text), "semantic_review_required": True}
        contract.check("operational_notes_cover_selection_and_limits", inspect_notes)

    return {"passed": all(item["passed"] for item in contract.checks), "project": str(contract.project),
            "checks": contract.checks, "scope": "Independent fresh-generation structural and syntax contract; no live model, native service launch, or semantic improvement claim.",
            "manual_review_required": ["Task-specific prompt fit", "Selection/operator explanation fidelity", "Curator semantic-family separation", "Actual native and model execution evidence"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--project", type=Path, help="Generated project path, absolute or relative to workspace; default outputs/team.")
    parser.add_argument("--profile", choices=("supervisor", "map-reduce", "review-refine"))
    parser.add_argument("--strategy", choices=("trace-distillation", "population", "pareto"))
    parser.add_argument("--allow-changed", action="append", default=[], metavar="RELATIVE_PATH", help="Preauthorized configuration/prompt edits after generation; initial hashes remain preserved.")
    parser.add_argument("--claimed-report", type=Path, default=Path("outputs/check.json"))
    parser.add_argument("--notes", type=Path)
    parser.add_argument("--live-model", default="gpt-6.1-sol", help="Exact expected live model or policy; legacy cohorts retain their original default.")
    parser.add_argument("--output", type=Path, help="Write evaluator JSON here only when explicitly requested; never overwrite the candidate report.")
    args = parser.parse_args()
    report = validate(args)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        output = args.output.resolve()
        claimed = (args.workspace / args.claimed_report).resolve()
        if output == claimed:
            parser.error("Evaluator output must not overwrite the candidate report.")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
