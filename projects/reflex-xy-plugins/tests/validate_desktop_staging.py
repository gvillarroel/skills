#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise staging containment and inventory failures inside an isolated fixture tree."""

from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    project = Path(__file__).resolve().parents[1]
    output = args.output_dir.resolve()
    if not output.is_relative_to(project / "artifacts"):
        parser.error("Evidence must remain in this project's artifacts directory")
    output.mkdir(parents=True, exist_ok=True)
    fixtures = Path(tempfile.mkdtemp(prefix="fixtures-", dir=output))
    helper = project / "scripts/stage_desktop_demo.py"
    spec = importlib.util.spec_from_file_location("xy_stage_subject", helper)
    subject = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(subject)
    results = []

    def check(name, operation):
        try:
            operation()
            results.append({"case": name, "status": "pass"})
        except PermissionError as error:
            if "symlink" not in name:
                raise
            results.append({"case": name, "status": "skip", "reason": str(error)})
        except Exception as error:
            results.append({"case": name, "status": "fail", "error": repr(error)})

    def reject(operation, expected=ValueError):
        try:
            operation()
        except expected:
            return
        raise AssertionError("Unsafe or invalid input was accepted")

    def package(path):
        config = {"mcpServers": {"xy": {"command": "node", "args": ["${PLUGIN_ROOT}/chatgpt/dist/server-bundled.js", "--stdio", "--desktop"], "cwd": "${PLUGIN_ROOT}", "env": {"XY_RENDER_SCRIPT": "${PLUGIN_ROOT}/runtime/render.py", "XY_SKILL_DIR": "${PLUGIN_ROOT}/skills/reflex-xy"}}}}
        files = {
            "mcp.json": json.dumps(config).encode(),
            ".mcp.json": json.dumps(config).encode(),
            "nested/payload.txt": b"Known package bytes.\n",
        }
        for name, data in files.items():
            file = path / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_bytes(data)
        (path / "bundle.json").write_text(json.dumps({"files": [{"path": name, "sha256": hashlib.sha256(data).hexdigest()} for name, data in files.items()]}), encoding="utf-8")
        return path

    valid = package(fixtures / "valid")
    check("valid-inventory", lambda: subject.verify_source(valid))
    modified = package(fixtures / "modified")
    (modified / "nested/payload.txt").write_bytes(b"Changed package bytes.\n")
    check("modified-bytes-rejected", lambda: reject(lambda: subject.verify_source(modified)))
    missing = package(fixtures / "missing")
    (missing / "nested/payload.txt").unlink()
    check("missing-file-rejected", lambda: reject(lambda: subject.verify_source(missing)))
    extra = package(fixtures / "extra")
    (extra / "unlisted.txt").write_text("An undeclared file.", encoding="utf-8")
    check("unlisted-file-rejected", lambda: reject(lambda: subject.verify_source(extra)))
    guarded = fixtures / "guarded"
    guarded.mkdir()
    check("inside-root-accepted", lambda: subject.inside(guarded / "future/file.txt", guarded))
    check("outside-root-rejected", lambda: reject(lambda: subject.inside(fixtures / "outside.txt", guarded)))
    check("parent-traversal-rejected", lambda: reject(lambda: subject.inside(guarded / "../outside.txt", guarded)))

    def root_symlink():
        link = fixtures / "root-link"
        link.symlink_to(valid, target_is_directory=True)
        reject(lambda: subject.verify_source(link))

    def member_symlink():
        root = package(fixtures / "file-link-package")
        (root / "nested/payload.txt").unlink()
        (root / "nested/payload.txt").symlink_to(valid / "nested/payload.txt")
        reject(lambda: subject.verify_source(root))

    def directory_symlink():
        root = package(fixtures / "directory-link-package")
        (root / "extra-link").symlink_to(valid / "nested", target_is_directory=True)
        reject(lambda: subject.verify_source(root))

    def escape_symlink():
        link = guarded / "escape-link"
        link.symlink_to(valid, target_is_directory=True)
        reject(lambda: subject.inside(link / "mcp.json", guarded))

    check("root-symlink-rejected", root_symlink)
    check("member-symlink-rejected", member_symlink)
    check("directory-symlink-rejected", directory_symlink)
    check("symlink-escape-rejected", escape_symlink)

    def fixture(case):
        repo = fixtures / case
        fixture_project = repo / "projects/reflex-xy-plugins"
        release = fixture_project / "artifacts/release"
        package(release / "reflex-xy-chatgpt-desktop")
        package(release / "reflex-xy-claude-code")
        (release / "release.json").write_text('{"version":"0.3.0"}', encoding="utf-8")
        return repo, fixture_project, release

    def invoke(repo, fixture_project, release, *extra):
        log = io.StringIO()
        executable = lambda name: str(repo / "test-bin" / f"{name}.exe")
        with patch.object(subject, "REPO", repo), patch.object(subject, "PROJECT", fixture_project), patch.object(subject.shutil, "which", side_effect=executable), patch("sys.argv", [str(helper), "--release-dir", str(release), *extra]), redirect_stdout(log), redirect_stderr(log):
            code = subject.main()
        if code != 0:
            raise AssertionError(f"Unexpected staging result: {code}")
        return json.loads(log.getvalue())

    def valid_staging():
        repo, fixture_project, release = fixture("successful-staging")
        market = repo / ".agents/plugins/marketplace.json"
        market.parent.mkdir(parents=True)
        prior = {"name": "preserved-marketplace", "interface": {"displayName": "Preserved Label"}, "plugins": [{"name": "unrelated", "source": "./unchanged"}]}
        market.write_text(json.dumps(prior), encoding="utf-8")
        result = invoke(repo, fixture_project, release)
        current = json.loads(market.read_text(encoding="utf-8"))
        assert current["name"] == prior["name"] and current["interface"] == prior["interface"]
        assert current["plugins"][0] == prior["plugins"][0] and len(current["plugins"]) == 2
        assert "Preserved Label" in result["next_steps"][0]
        assert Path(result["chatgpt_plugin"]).is_relative_to(repo)
        for name in result["configured_package_files"]:
            server = json.loads((Path(result["chatgpt_plugin"]) / name).read_text(encoding="utf-8"))["mcpServers"]["xy"]
            assert Path(server["command"]).is_absolute()
            assert Path(server["env"]["XY_RUNTIME_DIR"]).is_relative_to(repo)
            assert server["cwd"] == "./"
            assert server["args"][0] == "chatgpt/dist/server-bundled.js"
            assert server["env"]["XY_RENDER_SCRIPT"] == "runtime/render.py"
            assert server["env"]["XY_SKILL_DIR"] == "skills/reflex-xy"
            assert "${PLUGIN_ROOT}" not in json.dumps(server)

    def portable_paths_unchanged():
        value = {"cwd": "./", "args": ["chatgpt/dist/server-bundled.js"], "env": {"PYTHONDONTWRITEBYTECODE": "1"}}
        assert subject.relative_plugin_paths(value) == value

    def embedded_placeholder_rejected():
        reject(lambda: subject.relative_plugin_paths({"args": ["prefix${PLUGIN_ROOT}/server.js"]}))

    def outside_workspace():
        repo, fixture_project, release = fixture("outside-workspace")
        reject(lambda: invoke(repo, fixture_project, release, "--workspace-dir", str(fixtures / "rejected-workspace")))
        assert not (repo / ".agents/plugins/marketplace.json").exists()

    def outside_release():
        repo, fixture_project, release = fixture("outside-release")
        reject(lambda: invoke(repo, fixture_project, fixtures / "rejected-release"))
        assert not (repo / ".agents/plugins/marketplace.json").exists()

    def duplicate_marketplace():
        repo, fixture_project, release = fixture("duplicate-marketplace")
        market = repo / ".agents/plugins/marketplace.json"
        market.parent.mkdir(parents=True)
        original = b'{"name":"existing","plugins":[{"name":"reflex-xy"}]}\n'
        market.write_bytes(original)
        reject(lambda: invoke(repo, fixture_project, release), SystemExit)
        assert market.read_bytes() == original
        assert not (fixture_project / "artifacts/desktop-demo-0.3.0").exists()

    check("fixture-staging-preserves-marketplace", valid_staging)
    check("portable-relative-paths-unchanged", portable_paths_unchanged)
    check("embedded-plugin-root-rejected", embedded_placeholder_rejected)
    check("outside-workspace-no-marketplace-write", outside_workspace)
    check("outside-release-no-marketplace-write", outside_release)
    check("duplicate-plugin-preserves-marketplace", duplicate_marketplace)
    report = {"subject": str(helper), "subject_sha256": hashlib.sha256(helper.read_bytes()).hexdigest(), "fixtures": str(fixtures), "real_marketplace_written": False, "results": results, "passed": sum(x["status"] == "pass" for x in results), "failed": sum(x["status"] == "fail" for x in results), "skipped": sum(x["status"] == "skip" for x in results)}
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}))
    return 1 if report["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
