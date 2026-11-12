#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect immutable generated plugin PoCs into local, hash-inventoried packages."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[3]
PACKAGES = ROOT / "projects/desktop-plugin-ui/artifacts/plugin-pocs/packages"
ARTIFACTS = ROOT / "projects/desktop-plugin-ui/artifacts/plugin-pocs"
SAFE_ID = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
RESERVED = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
EXCLUDED_DIRS = {
    "node_modules", ".git", ".hg", ".svn", "__pycache__", ".cache", ".npm", ".npm-cache",
    ".uv-cache", ".pnpm-store", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".yarn-cache",
    "agent-state", "isolated-state", "pi-state", ".pi-state", ".agent-state", "pi-home", ".pi-home", ".check-agent", "sessions", "logs",
    "evaluator-review", "playwright-report", "test-results",
    ".stage", ".test-extract",
}
EXCLUDED_FILES = {".ds_store", "thumbs.db", "events.jsonl", "stdout.txt", "stderr.txt", "auth.json", "models-store.json"}
ARCHIVE_SUFFIXES = {".mcpb", ".zip", ".tgz"}


class CollectionError(ValueError):
    """A collection cannot preserve the requested source or write boundary."""


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def repo_relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def inside_repo(path: Path, label: str) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(ROOT):
        raise CollectionError(f"{label} must stay inside the repository: {path}")
    return resolved


def refuse_links(path: Path, label: str) -> None:
    current = path.absolute()
    while current != ROOT and current.is_relative_to(ROOT):
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise CollectionError(f"{label} cannot traverse a symbolic link or junction: {current}")
        current = current.parent


def safe_relative(value: str, label: str) -> Path:
    if not value or "\\" in value or "\x00" in value:
        raise CollectionError(f"{label} has an ambiguous relative path: {value!r}")
    for candidate in (PurePosixPath(value), PureWindowsPath(value)):
        if candidate.anchor or ".." in candidate.parts or any(":" in part for part in candidate.parts):
            raise CollectionError(f"{label} escapes its root: {value!r}")
    if any(part in {"", "."} or part.endswith((" ", ".")) for part in value.split("/")):
        raise CollectionError(f"{label} is not a canonical portable relative path: {value!r}")
    return Path(value)


def excluded(relative: Path) -> bool:
    if any(part.casefold() in EXCLUDED_DIRS for part in relative.parts[:-1]):
        return True
    name = relative.name.casefold()
    return name in EXCLUDED_FILES or name.endswith((".log", ".pyc", ".pyo", "-transcript.json", "-transcript.jsonl")) or (name.startswith(".env") and name != ".env.example")


def read_json(path: Path) -> dict:
    try:
        result = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        raise CollectionError(f"Cannot read JSON metadata {path}: {error}") from error
    if not isinstance(result, dict):
        raise CollectionError(f"Metadata must be a JSON object: {path}")
    return result


def parent_run(source: Path) -> tuple[Path, Path, dict]:
    for parent in (source, *source.parents):
        if not parent.is_relative_to(ROOT):
            break
        candidate = parent / "run-manifest.json"
        if candidate.is_file():
            manifest = read_json(candidate)
            workspace = parent / "workspace"
            if not workspace.is_dir() or source == workspace or not source.is_relative_to(workspace):
                raise CollectionError("Select a generated project folder below the run's workspace, not the whole run/workspace.")
            skill = manifest.get("skill")
            if not isinstance(skill, dict) or not re.fullmatch(r"[0-9a-f]{64}", str(skill.get("payloadSha256", ""))):
                raise CollectionError(f"Parent manifest lacks an exact skill payload digest: {candidate}")
            return parent, workspace, manifest
    raise CollectionError(f"No parent isolated run-manifest.json found for {source}")


def validate_archive(path: Path) -> None:
    try:
        if path.suffix.casefold() == ".tgz":
            with tarfile.open(path, "r:gz") as archive:
                seen: set[str] = set()
                for entry in archive.getmembers():
                    name = entry.name.rstrip("/")
                    if ".." in PurePosixPath(name).parts or "\\" in name:
                        raise CollectionError(f"Runtime tar member escapes its root: {path}: {name}")
                    normalized_name = PurePosixPath(name).as_posix()
                    safe_relative(normalized_name, f"Tar member in {path.name}")
                    normalized = normalized_name.casefold()
                    if normalized in seen:
                        raise CollectionError(f"Runtime tar has duplicate/case-colliding members: {path}: {name}")
                    seen.add(normalized)
                    if entry.issym() or entry.islnk() or not (entry.isfile() or entry.isdir()):
                        raise CollectionError(f"Runtime tar contains a link or special file: {path}: {name}")
            return
        with zipfile.ZipFile(path) as archive:
            seen: set[str] = set()
            for entry in archive.infolist():
                name = entry.filename.rstrip("/")
                if not name:
                    raise CollectionError(f"Runtime archive has an empty member: {path}")
                safe_relative(name, f"Archive member in {path.name}")
                normalized = name.casefold()
                if normalized in seen:
                    raise CollectionError(f"Runtime archive has duplicate/case-colliding members: {path}: {name}")
                seen.add(normalized)
                if stat.S_ISLNK(entry.external_attr >> 16):
                    raise CollectionError(f"Runtime archive contains a symbolic link: {path}: {name}")
    except (OSError, zipfile.BadZipFile, tarfile.TarError) as error:
        raise CollectionError(f"Invalid ZIP/MCPB/TGZ runtime archive {path}: {error}") from error


def inspect_host(host: str, source_argument: str, includes: list[str] | None = None) -> dict:
    if not SAFE_ID.fullmatch(host) or host in RESERVED:
        raise CollectionError(f"Host ID must be safe lowercase hyphen-case: {host!r}")
    raw_source = Path(source_argument).absolute()
    refuse_links(raw_source, "PoC source")
    source = inside_repo(raw_source, "PoC source")
    if not source.is_dir():
        raise CollectionError(f"PoC source is not a directory: {source}")
    run, workspace, manifest = parent_run(source)
    expected = manifest.get("expectedOutputs", [])
    if not isinstance(expected, list) or any(not isinstance(item, str) for item in expected):
        raise CollectionError(f"Parent expectedOutputs must be a string array: {run}")
    recorded: dict[str, dict] = {}
    artifact_check = run / "artifact-check.json"
    if artifact_check.is_file():
        for item in read_json(artifact_check).get("outputs", []):
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                recorded[item["path"]] = item
    files: list[dict] = []
    archives: dict[Path, dict] = {}
    directories: list[Path] = []
    omitted: list[str] = []
    for current, directory_names, filenames in os.walk(source, followlinks=False):
        directory = Path(current)
        kept = []
        for name in sorted(directory_names):
            child = directory / name
            relative = child.relative_to(source)
            if name.casefold() in EXCLUDED_DIRS:
                omitted.append(relative.as_posix() + "/")
                continue
            refuse_links(child, "PoC source directory")
            kept.append(name)
        directory_names[:] = kept
        directories.append(directory.relative_to(workspace))
        for name in sorted(filenames):
            candidate = directory / name
            relative = candidate.relative_to(source)
            if excluded(relative):
                omitted.append(relative.as_posix())
                continue
            refuse_links(candidate, "PoC source file")
            if not candidate.is_file():
                raise CollectionError(f"Source entry is not an ordinary file: {candidate}")
            if candidate.suffix.casefold() in ARCHIVE_SUFFIXES:
                archives[candidate] = {"declaredExpectedOutput": candidate.relative_to(workspace).as_posix() in expected}
            else:
                files.append({"path": candidate, "relative": candidate.relative_to(workspace), "explicitSupport": False})
    for value in expected:
        relative = safe_relative(value, "Expected output")
        candidate = workspace / relative
        if candidate.suffix.casefold() not in ARCHIVE_SUFFIXES or not candidate.is_file() or excluded(relative):
            continue
        refuse_links(candidate, "Declared runtime archive")
        inside_repo(candidate, "Declared runtime archive")
        if not candidate.resolve().is_relative_to(workspace):
            raise CollectionError(f"Declared archive escapes the run workspace: {candidate}")
        archives[candidate] = {"declaredExpectedOutput": True}
    for value in includes or []:
        relative = safe_relative(value, "Explicit support file")
        if excluded(relative):
            raise CollectionError(f"Explicit support file is excluded state, secret, dependency, cache or log data: {value}")
        candidate = workspace / relative
        refuse_links(candidate, "Explicit support file")
        candidate = inside_repo(candidate, "Explicit support file")
        if not candidate.is_relative_to(workspace) or not candidate.is_file():
            raise CollectionError(f"Explicit support file must be an ordinary file inside its run workspace: {value}")
        if candidate.suffix.casefold() in ARCHIVE_SUFFIXES:
            archives.setdefault(candidate, {"declaredExpectedOutput": relative.as_posix() in expected})["explicitSupport"] = True
        else:
            existing = next((item for item in files if item["path"] == candidate), None)
            if existing is not None:
                existing["explicitSupport"] = True
            else:
                files.append({"path": candidate, "relative": relative, "explicitSupport": True})
    if not files:
        raise CollectionError(f"No authored/runtime source files selected for host {host}")
    source_records = []
    runtime_records = []
    for item in files:
        candidate, relative = item["path"], item["relative"]
        checksum = digest(candidate)
        previous = recorded.get(relative.as_posix(), {})
        if previous.get("sha256") and previous["sha256"] != checksum:
            raise CollectionError(f"Recorded generated artifact changed after the forward run: {candidate}")
        source_records.append({"path": candidate, "relative": relative, "sha256": checksum, "sizeBytes": candidate.stat().st_size,
                               "recordedArtifactMatch": "matched" if previous.get("sha256") else "not-recorded-by-forward-harness", "explicitSupport": item["explicitSupport"]})
    for candidate, declaration in sorted(archives.items()):
        validate_archive(candidate)
        relative = candidate.relative_to(workspace)
        checksum = digest(candidate)
        previous = recorded.get(relative.as_posix(), {})
        if previous.get("sha256") and previous["sha256"] != checksum:
            raise CollectionError(f"Recorded runtime archive changed after the forward run: {candidate}")
        runtime_records.append({"path": candidate, "relative": relative, "sha256": checksum, "sizeBytes": candidate.stat().st_size,
                                "recordedArtifactMatch": "matched" if previous.get("sha256") else "not-recorded-by-forward-harness", **declaration})
    evaluation_path = run / "evaluation-result.json"
    evaluation = read_json(evaluation_path) if evaluation_path.is_file() else None
    return {"host": host, "source": source, "run": run, "workspace": workspace, "runManifest": manifest,
            "runManifestSha256": digest(run / "run-manifest.json"), "files": source_records, "runtime": runtime_records,
            "directories": directories, "omitted": sorted(omitted), "explicitIncludes": sorted(set(includes or [])), "forwardEvaluation": evaluation}


def collect(host_arguments: list[str], output_argument: str, include_arguments: list[str] | None = None) -> dict:
    raw_output = Path(output_argument).absolute()
    refuse_links(raw_output, "Collection output")
    output = inside_repo(raw_output, "Collection output")
    packages = inside_repo(PACKAGES, "Package root")
    if output.parent != packages or not SAFE_ID.fullmatch(output.name) or output.name in RESERVED:
        raise CollectionError(f"Output must be a new lowercase release directory directly below {repo_relative(packages)}/")
    if output.exists():
        raise CollectionError(f"Refusing to overwrite an existing collection: {output}")
    hosts = []
    identities: set[str] = set()
    parsed_hosts: list[tuple[str, str]] = []
    for argument in host_arguments:
        if "=" not in argument:
            raise CollectionError(f"--host requires HOST=PATH: {argument!r}")
        host, source = argument.split("=", 1)
        if host in identities:
            raise CollectionError(f"Duplicate host ID: {host}")
        identities.add(host)
        parsed_hosts.append((host, source))
    support: dict[str, list[str]] = {host: [] for host in identities}
    for argument in include_arguments or []:
        if "=" not in argument:
            raise CollectionError(f"--include requires HOST=WORKSPACE_RELATIVE_FILE: {argument!r}")
        host, relative = argument.split("=", 1)
        if host not in support:
            raise CollectionError(f"--include refers to an unselected host: {host!r}")
        safe_relative(relative, "Explicit support file")
        support[host].append(relative)
    for host, source in parsed_hosts:
        inspected = inspect_host(host, source, support[host])
        if output.is_relative_to(inspected["source"]) or inspected["source"].is_relative_to(output):
            raise CollectionError("Collection output and source must not contain one another.")
        hosts.append(inspected)
    if not hosts:
        raise CollectionError("Provide at least one --host HOST=PATH.")
    # All source, archive, provenance and output checks finish before creating
    # the output. Any later I/O failure leaves a visible partial folder; never
    # remove user files or silently reuse a release ID.
    output.mkdir(parents=True, exist_ok=False)
    manifest = {"schemaVersion": 1, "createdAtUtc": datetime.now(timezone.utc).isoformat(), "releaseId": output.name,
                "collectionStatus": "copied-and-hash-verified", "hostAcceptance": "not-assessed-by-collector",
                "boundary": "Copied source and archive integrity only. Parent forward results are provenance, not host installation, rendering or usability acceptance.", "hosts": []}
    index = ["# Local plugin proof-of-concepts", "", "This collection preserves selected generated source and supplied runtime archives with SHA-256 inventories. Collection does not install, trust, execute or approve a plugin in any host.", "",
             "Extract a source ZIP into a fresh folder and treat that folder as the original generated workspace root. Original workspace-relative paths and authored filenames are preserved; follow the included usage instructions after reviewing the source.", "",
             "| Host | Source archive | Authored usage | Runtime archives | Recorded forward result |", "| --- | --- | --- | --- | --- |"]
    for host in hosts:
        name = host["host"]
        destination = output / name
        source_destination = destination / "source"
        for relative in host["directories"]:
            (source_destination / relative).mkdir(parents=True, exist_ok=True)
        file_records = []
        for item in host["files"]:
            copied = source_destination / item["relative"]
            copied.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item["path"], copied)
            if digest(copied) != item["sha256"]:
                raise CollectionError(f"Copied file failed hash verification: {copied}")
            file_records.append({"sourcePath": repo_relative(item["path"]), "workspaceRelativePath": item["relative"].as_posix(),
                                 "collectionPath": copied.relative_to(output).as_posix(), "sha256": item["sha256"], "sizeBytes": item["sizeBytes"], "recordedArtifactMatch": item["recordedArtifactMatch"], "explicitSupport": item["explicitSupport"]})
        source_archive = destination / f"{name}-source.zip"
        with zipfile.ZipFile(source_archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for relative in sorted(set(host["directories"])):
                info = zipfile.ZipInfo(relative.as_posix().rstrip("/") + "/", (1980, 1, 1, 0, 0, 0))
                info.external_attr = (stat.S_IFDIR | 0o755) << 16
                archive.writestr(info, b"")
            for item in host["files"]:
                name_in_archive = item["relative"].as_posix()
                safe_relative(name_in_archive, "Generated source ZIP entry")
                info = zipfile.ZipInfo(name_in_archive, (1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | stat.S_IMODE(item["path"].stat().st_mode)) << 16
                archive.writestr(info, (source_destination / item["relative"]).read_bytes())
        validate_archive(source_archive)
        runtime_records = []
        for item in host["runtime"]:
            copied = destination / "runtime" / item["relative"]
            copied.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item["path"], copied)
            if digest(copied) != item["sha256"]:
                raise CollectionError(f"Copied runtime archive failed hash verification: {copied}")
            runtime_records.append({"sourcePath": repo_relative(item["path"]), "workspaceRelativePath": item["relative"].as_posix(), "collectionPath": copied.relative_to(output).as_posix(),
                                    "sha256": item["sha256"], "sizeBytes": item["sizeBytes"], "declaredExpectedOutput": item["declaredExpectedOutput"], "recordedArtifactMatch": item["recordedArtifactMatch"], "explicitSupport": item.get("explicitSupport", False)})
        for item in (*host["files"], *host["runtime"]):
            if digest(item["path"]) != item["sha256"]:
                raise CollectionError(f"Source changed during collection: {item['path']}")
        if digest(host["run"] / "run-manifest.json") != host["runManifestSha256"]:
            raise CollectionError(f"Parent run manifest changed during collection: {host['run']}")
        run_manifest = host["runManifest"]
        result = host["forwardEvaluation"]
        manifest["hosts"].append({"host": name, "sourceRoot": repo_relative(host["source"]), "sourceRun": repo_relative(host["run"]),
                                  "sourceRunManifest": repo_relative(host["run"] / "run-manifest.json"), "sourceRunManifestSha256": host["runManifestSha256"],
                                  "runId": run_manifest.get("runId"), "skill": run_manifest["skill"], "requestedModelSettings": run_manifest.get("pi", {}),
                                  "promptSha256": run_manifest.get("prompt", {}).get("sha256"), "parentForwardEvaluation": result,
                                  "hostAcceptance": "not-assessed-by-collector", "sourceFiles": file_records,
                                  "sourceArchive": {"collectionPath": source_archive.relative_to(output).as_posix(), "sha256": digest(source_archive), "sizeBytes": source_archive.stat().st_size},
                                  "runtimeArchives": runtime_records, "explicitSupportFiles": host["explicitIncludes"], "excludedSourcePaths": host["omitted"]})
        usage = next((item for item in file_records if Path(item["workspaceRelativePath"]).name.casefold() in {"usage.md", "readme.md"}), None)
        usage_link = f"[Usage]({quote(usage['collectionPath'], safe='/')})" if usage else "See source files"
        archives_link = ", ".join(f"[{Path(item['collectionPath']).name}]({quote(item['collectionPath'], safe='/')})" for item in runtime_records) or "None supplied"
        forward_label = "unavailable" if result is None else "passed" if result.get("passed") is True else "failed or incomplete"
        index.append(f"| {name} | [Source ZIP]({source_archive.relative_to(output).as_posix()}) | {usage_link} | {archives_link} | {forward_label}; host acceptance unassessed |")
    index.extend(["", "`manifest.json` records the selected source run, exact frozen skill subject, recorded forward result, and hashes/sizes for every copied file and archive. A passing recorded forward result does not certify installation, native paint, permissions or user testing. Failed or incomplete forward results are preserved rather than promoted to acceptance.", "",
                  "Dependencies, caches, logs, known isolated agent-state folders, Git data and evaluator review folders are excluded. Authored compiled assets such as `dist/` and `build/` are retained. Explicit support files preserve their original workspace paths without discovering entire work directories. Runtime ZIP/MCPB/TGZ files are copied separately and checked for unsafe or duplicate member paths and links; tar special files are refused. Archives are never extracted or executed.", ""])
    (output / "USAGE.md").write_text("\n".join(index), encoding="utf-8")
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return {"collected": True, "hostCount": len(hosts), "output": str(output), "manifest": str(output / "manifest.json"), "hostAcceptance": "not-assessed-by-collector"}


def self_test() -> dict:
    identity = uuid.uuid4().hex[:12]
    fixture = ARTIFACTS / "collector-selftests" / identity
    run = fixture / "run"
    source = run / "workspace/poc"
    source.mkdir(parents=True)
    authored = {"server.ts": b"export const value = 7;\n", "USAGE.md": b"# Synthetic fixture\nRun from the extracted workspace root.\n", "dist/server.js": b"export const value = 7;\n", "assets/sample.bin": bytes(range(32)), ".env.example": b"DEMO=synthetic\n"}
    for relative, content in authored.items():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    support_files = {
        ".agents/plugins/marketplace.json": b'{"fixture":"local-catalog"}\n',
        "work/docs/plugin.schema.json": b'{"type":"object","fixture":"plugin"}\n',
        "work/docs/mcp.schema.json": b'{"type":"object","fixture":"mcp"}\n',
    }
    for relative, content in support_files.items():
        target = run / "workspace" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    for relative in ["node_modules/dep/index.js", ".npm-cache/record", "agent-state/auth.json", "pi-home/models-store.json", ".pi-home/settings.json", ".check-agent/settings.json", "models-store.json", "rpc-transcript.json", "mode-transcript.jsonl", ".stage/runtime.js", ".test-extract/manifest.json", "evaluator-review/result.json", "logs/run.txt", "debug.log", ".env"]:
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("synthetic omitted fixture\n", encoding="utf-8")
    (source / "build").mkdir()
    runtime = run / "workspace/releases/fixture.mcpb"
    runtime.parent.mkdir()
    for archive in (source / "build/fixture.zip", runtime):
        with zipfile.ZipFile(archive, "x") as bundle:
            bundle.writestr("manifest.json", '{"fixture":true}')
    supplied_tgz = run / "workspace/releases/provided.tgz"

    def make_tar(target: Path, entries: list[tuple[str, bytes, bytes | None]]) -> None:
        with tarfile.open(target, "w:gz") as archive:
            for name, member_type, content in entries:
                info = tarfile.TarInfo(name)
                info.type = member_type
                if member_type in {tarfile.SYMTYPE, tarfile.LNKTYPE}:
                    info.linkname = "package/target.json"
                if content is not None:
                    info.size = len(content)
                archive.addfile(info, io.BytesIO(content) if content is not None else None)

    make_tar(supplied_tgz, [("package/plugin.json", tarfile.REGTYPE, b'{"fixture":true}')])
    manifest = {"runId": "synthetic-collector-fixture", "skill": {"name": "fixture-skill", "profile": "runtime", "fileCount": 1, "payloadSha256": "a" * 64},
                "pi": {"model": "synthetic-no-model"}, "expectedOutputs": ["poc/server.ts", "poc/build/fixture.zip", "releases/fixture.mcpb"]}
    (run / "run-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (run / "evaluation-result.json").write_text('{"passed":false,"returnCode":4,"fixture":true}', encoding="utf-8")
    (run / "artifact-check.json").write_text(json.dumps({"outputs": [{"path": "poc/server.ts", "sha256": digest(source / "server.ts")}]}), encoding="utf-8")
    output = PACKAGES / f"collector-selftest-{identity}-valid"
    checks = []

    def check(name: str, passed: bool, detail: str = "") -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})

    def invoke(target: Path, selected: Path = source, include_values: list[str] | None = None) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(Path(__file__).resolve()), "--host", f"fixture={selected}", "--output", str(target)]
        for relative in (list(support_files) + ["releases/provided.tgz"]) if include_values is None else include_values:
            command.extend(["--include", f"fixture={relative}"])
        return subprocess.run(command, capture_output=True, text=True, encoding="utf-8", timeout=30)

    result = invoke(output)
    check("valid-collection-cli", result.returncode == 0, result.stdout + result.stderr)
    collected = read_json(output / "manifest.json")
    host = collected["hosts"][0]
    check("source-fidelity", all((output / "fixture/source/poc" / relative).read_bytes() == content for relative, content in authored.items()))
    check("explicit-support-file-fidelity", all((output / "fixture/source" / relative).read_bytes() == content for relative, content in support_files.items()))
    copied = {item["workspaceRelativePath"] for item in host["sourceFiles"]}
    check("dependencies-cache-state-logs-evaluator-excluded", copied == {f"poc/{relative}" for relative in authored} | set(support_files))
    check("authored-build-runtime-retained", (output / "fixture/source/poc/dist/server.js").is_file())
    with zipfile.ZipFile(output / "fixture/fixture-source.zip") as archive:
        entries = archive.namelist()
        check("source-zip-safe-fidelity", len(entries) == len(set(entries)) and all(not name.startswith(("/", "..")) and "\\" not in name for name in entries)
              and archive.read("poc/assets/sample.bin") == authored["assets/sample.bin"] and not any("node_modules" in name for name in entries))
        check("catalog-and-schema-workspace-paths-in-zip", all(archive.read(relative) == content for relative, content in support_files.items()))
    check("runtime-archives-separate-exact", len(host["runtimeArchives"]) == 3 and all(digest(output / item["collectionPath"]) == item["sha256"] for item in host["runtimeArchives"]))
    check("explicit-sibling-tgz-preserved-with-provenance", any(item["workspaceRelativePath"] == "releases/provided.tgz" and item["explicitSupport"] and not item["declaredExpectedOutput"] for item in host["runtimeArchives"]))
    check("exact-subject-and-failed-forward-preserved", host["skill"]["payloadSha256"] == "a" * 64 and host["parentForwardEvaluation"]["passed"] is False and host["hostAcceptance"] == "not-assessed-by-collector")
    before = digest(output / "manifest.json")
    repeated = invoke(output)
    check("overwrite-refused-without-mutation", repeated.returncode != 0 and "overwrite" in repeated.stderr and digest(output / "manifest.json") == before)
    escape = fixture / "forbidden-output"
    refused = invoke(escape)
    check("output-path-escape-refused-before-write", refused.returncode != 0 and not escape.exists())
    invalid = PACKAGES / f"collector-selftest-{identity}-invalid-source"
    refused = invoke(invalid, ROOT.parent)
    check("source-outside-repository-refused", refused.returncode != 0 and not invalid.exists())
    for suffix, relative in [("support-escape", "../run-manifest.json"), ("support-secret", "poc/.env"), ("support-directory", "work/docs")]:
        refused_output = PACKAGES / f"collector-selftest-{identity}-{suffix}"
        refused = invoke(refused_output, include_values=[relative])
        check(suffix + "-refused-before-write", refused.returncode != 0 and not refused_output.exists())
    bad_tars = [
        ("traversal", [("../escape.txt", tarfile.REGTYPE, b"fixture")]),
        ("absolute", [("/escape.txt", tarfile.REGTYPE, b"fixture")]),
        ("symlink", [("package/link", tarfile.SYMTYPE, None)]),
        ("hardlink", [("package/link", tarfile.LNKTYPE, None)]),
        ("special", [("package/pipe", tarfile.FIFOTYPE, None)]),
        ("duplicate", [("package/file.json", tarfile.REGTYPE, b"one"), ("package/FILE.json", tarfile.REGTYPE, b"two")]),
    ]
    for suffix, entries in bad_tars:
        bad_tar = run / "workspace/releases" / f"unsafe-{suffix}.tgz"
        make_tar(bad_tar, entries)
        refused_output = PACKAGES / f"collector-selftest-{identity}-tar-{suffix}"
        refused = invoke(refused_output, include_values=[bad_tar.relative_to(run / "workspace").as_posix()])
        check(f"runtime-tgz-{suffix}-refused-before-write", refused.returncode != 0 and not refused_output.exists())
    unsafe = source / "build/unsafe.zip"
    with zipfile.ZipFile(unsafe, "x") as archive:
        archive.writestr("../escape.txt", "synthetic unsafe fixture")
    unsafe_output = PACKAGES / f"collector-selftest-{identity}-unsafe"
    refused = invoke(unsafe_output)
    check("runtime-zip-escape-refused-before-write", refused.returncode != 0 and "escapes" in refused.stderr and not unsafe_output.exists())
    # Preserve the unsafe ZIP fixture while placing it in an excluded directory
    # for the separate immutable-source test; no recursive deletion is needed.
    excluded_fixture = source / "evaluator-review/unsafe.zip"
    unsafe.rename(excluded_fixture)
    (source / "server.ts").write_text("export const value = 99;\n", encoding="utf-8")
    changed_output = PACKAGES / f"collector-selftest-{identity}-changed"
    refused = invoke(changed_output)
    check("recorded-source-tampering-refused-before-write", refused.returncode != 0 and "changed after" in refused.stderr and not changed_output.exists())
    report = {"passed": all(item["passed"] for item in checks), "fixtureRoot": repo_relative(fixture), "checks": checks}
    (fixture / "result.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", action="append", default=[], metavar="HOST=PATH", help="Generated project directory below an isolated run workspace; repeat for each host.")
    parser.add_argument("--include", action="append", default=[], metavar="HOST=WORKSPACE_RELATIVE_FILE", help="Include one explicit support file or supplied runtime archive from that host's run workspace; repeat as needed.")
    parser.add_argument("--output", help="New release directory directly below projects/desktop-plugin-ui/artifacts/plugin-pocs/packages/.")
    parser.add_argument("--self-test", action="store_true", help="Run local positive/negative collector checks with synthetic fixtures inside project artifacts.")
    args = parser.parse_args()
    if args.self_test:
        if args.host or args.output or args.include:
            parser.error("--self-test cannot be combined with --host, --include or --output")
        report = self_test()
        print(json.dumps({"passed": report["passed"], "checks": len(report["checks"]), "fixtureRoot": report["fixtureRoot"]}))
        return 0 if report["passed"] else 1
    if not args.host or not args.output:
        parser.error("Provide --output and at least one --host HOST=PATH, or use --self-test")
    try:
        result = collect(args.host, args.output, args.include)
    except (CollectionError, OSError) as error:
        print(f"Collection refused: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
