#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Verify release resources against exact Git blobs and an exact Pages workflow artifact.

Plan before publication:
  uv run --script projects/grayscale-interleave/scripts/renderer-verify-publication.py --expected-ref COMMIT --base-ref BASE --plan-only
Verify after the exact successful Pages run:
  uv run --script projects/grayscale-interleave/scripts/renderer-verify-publication.py --expected-ref COMMIT --base-ref BASE --workflow-run RUN_ID

Expected content never comes from the working tree or dist/pages. Static source
resources replay the target commit's Pages transforms. Built Slidev/ThreeJS
resources use the artifact downloaded from the explicitly named, SHA-matched run.
Canonical palette definitions outside Pages are checked at exact-commit GitHub
raw URLs, explicitly distinguished from deployed gallery URLs in the report.
"""

from __future__ import annotations

import argparse
import ast
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import fnmatch
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import tempfile
import threading
from urllib.parse import quote
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects/grayscale-interleave"
PUBLIC = "https://gvillarroel.github.io/skills/"
REPOSITORY = "gvillarroel/skills"


def git(*arguments: str) -> bytes:
    return subprocess.run(["git", *arguments], cwd=ROOT, check=True, capture_output=True).stdout


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(ref: str, source: str) -> bytes:
    return git("show", f"{ref}:{source}")


def git_files(ref: str, prefix: str = "") -> list[str]:
    arguments = ["ls-tree", "-r", "--name-only", "-z", ref]
    if prefix:
        arguments.extend(["--", prefix])
    return [item for item in git(*arguments).decode("utf-8").split("\0") if item]


@dataclass(frozen=True)
class CopySpec:
    source: str
    route: str
    owner: str | None
    generated: bool


def load_builder(ref: str) -> tuple[dict, list[CopySpec], dict, list[str], str]:
    source = git_blob(ref, "scripts/build-pages.py")
    filename = ROOT / "scripts/build-pages.py"
    namespace = {"__name__": "exact_commit_publication_builder", "__file__": str(filename)}
    exec(compile(source, str(filename), "exec"), namespace)
    # Source mapping must not require any current checkout directory to exist.
    namespace["example_source"] = lambda name: namespace["EXAMPLE_SOURCES"][name]
    tree = ast.parse(source)
    build = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build_docs")
    context = dict(namespace)
    specs, patches = [], {}
    for statement in build.body:
        if isinstance(statement, ast.Assign):
            value = eval(compile(ast.Expression(statement.value), str(filename), "eval"), context)
            for target in statement.targets:
                if isinstance(target, ast.Name):
                    context[target.id] = value
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            continue
        call = statement.value
        if not isinstance(call.func, ast.Name):
            continue
        if call.func.id == "copy_tree":
            origin = eval(compile(ast.Expression(call.args[0]), str(filename), "eval"), context)
            destination = eval(compile(ast.Expression(call.args[1]), str(filename), "eval"), context)
            relative = origin.relative_to(namespace["ROOT"]).as_posix()
            route = destination.relative_to(namespace["PAGES_ROOT"]).as_posix()
            parts = PurePosixPath(relative).parts
            owner = parts[1] if len(parts) > 1 and parts[0] == "skills" else None
            generated = relative.startswith("projects/") or relative.endswith("/dist")
            specs.append(CopySpec(relative, route, owner, generated))
        elif call.func.id == "patch_file":
            target = eval(compile(ast.Expression(call.args[0]), str(filename), "eval"), context)
            replacement = ast.literal_eval(call.args[1])
            if not isinstance(replacement, dict) or not all(isinstance(a, str) and isinstance(b, str) for a, b in replacement.items()):
                raise ValueError("Exact Pages patch must be a literal string mapping")
            patches[target.relative_to(namespace["PAGES_ROOT"]).as_posix()] = replacement
    copying = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "copy_tree")
    ignored = next(call for call in ast.walk(copying)
                   if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                   and call.func.attr == "ignore_patterns")
    patterns = [ast.literal_eval(argument) for argument in ignored.args]
    if not all(isinstance(pattern, str) for pattern in patterns):
        raise ValueError("Exact Pages ignore patterns must be literal strings")
    return namespace, specs, patches, patterns, sha(source)


def transform(namespace: dict, patches: dict, route: str, data: bytes) -> bytes:
    suffix = PurePosixPath(route).suffix.lower()
    if suffix not in namespace["TEXT_SUFFIXES"]:
        return data
    try:
        content = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError:
        return data
    for before, after in patches.get(route, {}).items():
        content = content.replace(before, after)
    card = next((item for item in namespace["PUBLISHED_EXAMPLE_SETS"]
                 if route == item["href"] + "index.html"), None)
    if card:
        content = namespace["ensure_html_head_meta"](content, card["id"])
        content = namespace["ensure_html_favicon"](content)
        for name, value in {"data-example-id": card["id"], "data-pattern-id": card["id"], "data-pattern-page": "true"}.items():
            content = namespace["ensure_body_attribute"](content, name, value)
    scratch = PROJECT / "artifacts/publication-expected"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        path = Path(directory) / PurePosixPath(route).name
        path.write_text(content, encoding="utf-8", newline="\n")
        namespace["normalize_text_file"](path)
        return path.read_bytes()


def generated_metadata(namespace: dict) -> dict[str, bytes]:
    """Run only exact committed pure writers into an owned temporary directory."""
    scratch = PROJECT / "artifacts/publication-expected"
    scratch.mkdir(parents=True, exist_ok=True)
    original = namespace["PAGES_ROOT"]
    try:
        with tempfile.TemporaryDirectory(dir=scratch) as directory:
            output = Path(directory)
            namespace["PAGES_ROOT"] = output
            (output / "examples/plantuml-colorset-renderer-cs1").mkdir(parents=True)
            for name in ("write_index", "write_catalog", "write_favicon", "write_plantuml_legacy_redirect"):
                namespace[name]()
            namespace["normalize_text_tree"](output)
            return {path.relative_to(output).as_posix(): path.read_bytes()
                    for path in output.rglob("*") if path.is_file()}
    finally:
        namespace["PAGES_ROOT"] = original


def plan_resources(ref: str, base: str, repository: str, public: str) -> tuple[dict, dict]:
    namespace, specs, patches, ignored, builder_sha = load_builder(ref)
    changed = [item for item in git("diff", "--name-only", "-z", base, ref).decode().split("\0") if item]
    owners = {PurePosixPath(name).parts[1] for name in changed
              if name.startswith("skills/") and len(PurePosixPath(name).parts) > 1}
    # Generated roots are discovered by committed catalog ownership; their
    # build input paths can point outside the skill's example directory.
    generated_owners = {}
    for spec in specs:
        if not spec.generated:
            continue
        card = next((item for item in namespace["PUBLISHED_EXAMPLE_SETS"]
                     if item["href"].rstrip("/") == spec.route), None)
        owner = spec.owner or (card["source"] if card else None)
        generated_owners[spec.route] = owner
    resources = {}
    affected = []
    for spec in specs:
        owner = generated_owners.get(spec.route, spec.owner)
        if owner not in owners and not any(name.startswith(spec.source + "/") for name in changed):
            continue
        affected.append({"source": spec.source, "route": spec.route, "owner": owner, "generated": spec.generated})
        if spec.generated:
            continue
        for source in git_files(ref, spec.source):
            tail = PurePosixPath(source).relative_to(spec.source)
            if any(fnmatch.fnmatch(part, pattern) for part in tail.parts for pattern in ignored):
                continue
            route = (PurePosixPath(spec.route) / tail).as_posix()
            expected = transform(namespace, patches, route, git_blob(ref, source))
            resources[route] = {"kind": "pages-copy", "source": source, "route": route,
                                "url": public.rstrip("/") + "/" + quote(route), "expected": expected}
    # ECharts' committed baseline gallery is intentionally verified even when
    # its current uncommitted local index and builder remain excluded.
    for route, expected in generated_metadata(namespace).items():
        resources[route] = {"kind": "pages-generated-metadata", "source": "scripts/build-pages.py",
                            "route": route, "url": public.rstrip("/") + "/" + quote(route), "expected": expected}
    palette_sources = [name for name in git_files(ref)
                       if name == "docs/colorsets.json" or name.endswith("/assets/palettes/colorsets.json")]
    if not palette_sources:
        raise ValueError("No committed canonical palette definitions found")
    for source in palette_sources:
        expected = git_blob(ref, source)
        resources["git-source:" + source] = {
            "kind": "exact-commit-git-palette", "source": source, "route": None,
            "url": f"https://raw.githubusercontent.com/{repository}/{ref}/{quote(source)}", "expected": expected,
        }
    context = {"expectedRef": ref, "baselineRef": base, "repository": repository,
               "builderSha256": builder_sha, "changedSourceCount": len(changed),
               "affectedCopies": affected, "canonicalPaletteDefinitions": len(palette_sources),
               "generatedRoutesRequiringExactWorkflowArtifact": [row["route"] for row in affected if row["generated"]],
               "expectationMethod": "Exact target Git blobs and target Pages writer/patch/normalization functions; generated bundles come only from an explicitly SHA-matched successful Pages workflow artifact. No current worktree or dist/pages bytes are expectations.",
               "echartsPublicationDecision": "Keep committed baseline index and builder. User's local drafts and ignored staged candidate are never release expectations."}
    return context, resources


def gh_json(endpoint: str) -> dict:
    return json.loads(subprocess.run(["gh", "api", endpoint], cwd=ROOT, check=True, capture_output=True).stdout)


def verify_artifact_digest(archive: bytes, declared: str | None) -> bool:
    if declared is None:
        return False
    if declared != "sha256:" + sha(archive):
        raise ValueError("Downloaded Pages archive does not match the declared API artifact SHA256")
    return True


def workflow_pages(repository: str, run_id: str, ref: str, output: Path) -> tuple[dict, dict[str, bytes]]:
    run = gh_json(f"repos/{repository}/actions/runs/{run_id}")
    if run["head_sha"] != ref or run["status"] != "completed" or run["conclusion"] != "success":
        raise ValueError("The supplied Pages run must be successful and belong to the exact expected commit")
    if run["path"].split("@")[0] != ".github/workflows/pages.yml":
        raise ValueError("The supplied run is not the repository's Pages workflow")
    listing = gh_json(f"repos/{repository}/actions/runs/{run_id}/artifacts")
    candidates = [row for row in listing["artifacts"] if row["name"] == "github-pages" and not row["expired"]]
    if len(candidates) != 1:
        raise ValueError("Expected one unexpired github-pages artifact from the exact workflow run")
    artifact = candidates[0]
    archive = subprocess.run(["gh", "api", f"repos/{repository}/actions/artifacts/{artifact['id']}/zip"],
                             cwd=ROOT, check=True, capture_output=True).stdout
    archive_path = output / f"github-pages-run-{run_id}-artifact-{artifact['id']}.zip"
    archive_path.write_bytes(archive)
    digest_verified = verify_artifact_digest(archive, artifact.get("digest"))
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        names = [name for name in zipped.namelist() if not name.endswith("/")]
        if len(names) != 1 or PurePosixPath(names[0]).name != "artifact.tar":
            raise ValueError("Expected the Pages upload archive to contain one artifact.tar")
        packed = zipped.read(names[0])
    pages = {}
    with tarfile.open(fileobj=io.BytesIO(packed), mode="r:*") as tar:
        for member in tar.getmembers():
            name = member.name.removeprefix("./")
            if member.isdir():
                continue
            path = PurePosixPath(name)
            if not member.isfile() or path.is_absolute() or ".." in path.parts or "\\" in name:
                raise ValueError(f"Unsafe or non-file Pages archive member: {member.name}")
            stream = tar.extractfile(member)
            if stream is None or name in pages:
                raise ValueError(f"Missing or duplicate Pages archive member: {name}")
            pages[name] = stream.read()
    proof = {"runId": run_id, "runUrl": run["html_url"], "headSha": run["head_sha"],
             "conclusion": run["conclusion"], "artifactId": artifact["id"], "artifactName": artifact["name"],
             "archiveSha256": sha(archive), "apiArtifactDigest": artifact.get("digest"),
             "apiArtifactDigestVerified": digest_verified,
             "archive": archive_path.relative_to(ROOT).as_posix(), "fileCount": len(pages)}
    return proof, pages


def verify_url(row: dict, ref: str) -> dict:
    separator = "&" if "?" in row["url"] else "?"
    request = Request(row["url"] + separator + "release=" + ref,
                      headers={"User-Agent": "grayscale-exact-commit-verifier"})
    public = {key: value for key, value in row.items() if key != "expected"}
    public["expectedSha256"] = sha(row["expected"])
    try:
        with urlopen(request, timeout=30) as response:
            observed = response.read()
        public.update({"ok": observed == row["expected"], "observedSha256": sha(observed), "sizeBytes": len(observed)})
    except Exception as error:
        public.update({"ok": False, "error": str(error)})
    return public


def add_generated_resources(resources: dict, pages: dict, prefixes: list[str], public: str) -> None:
    for prefix in prefixes:
        entry = prefix + "/index.html"
        if not pages.get(entry):
            raise ValueError(f"Exact workflow artifact lacks a nonempty generated gallery entry page: {entry}")
        for route, expected in pages.items():
            if route.startswith(prefix + "/"):
                resources[route] = {
                    "kind": "pages-workflow-built", "source": "Exact SHA-matched workflow artifact",
                    "route": route, "url": public.rstrip("/") + "/" + quote(route), "expected": expected,
                }


def self_test() -> int:
    ref = git("rev-parse", "HEAD").decode().strip()
    namespace, specs, patches, _, _ = load_builder(ref)
    spec = next(item for item in specs if item.route == "examples/d3-animated-svg")
    route = spec.route + "/index.html"
    expected = transform(namespace, patches, route, git_blob(ref, spec.source + "/index.html"))
    if b"https://cdn.jsdelivr.net/npm/d3@7.9.0" not in expected or b'data-pattern-page="true"' not in expected:
        raise AssertionError("Exact committed CDN and page metadata transforms did not apply")
    data = {"/good": expected, "/tampered": expected + b"!"}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = data.get(self.path.split("?")[0])
            if body is None:
                self.send_error(404)
                return
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *arguments):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        rows = [verify_url({"kind": "self-test", "url": f"http://127.0.0.1:{server.server_port}/{name}", "expected": expected}, ref)
                for name in ("good", "tampered", "missing")]
        if [row["ok"] for row in rows] != [True, False, False]:
            raise AssertionError("Exact bytes/tampering/missing resource gates did not hold")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=10)
    generated_gate = []
    for name, pages, accepted in (
        ("nonempty-entry-page", {"examples/generated/index.html": b"<!doctype html>"}, True),
        ("orphan-script-without-entry-page", {"examples/generated/assets/app.js": b"console.log('orphan')"}, False),
        ("empty-entry-page", {"examples/generated/index.html": b"", "examples/generated/assets/app.js": b"orphan"}, False),
    ):
        try:
            add_generated_resources({}, pages, ["examples/generated"], "https://example.invalid/")
            observed = True
            error = None
        except ValueError as rejection:
            observed = False
            error = str(rejection)
        if observed != accepted:
            raise AssertionError(f"Generated entry-page gate failed: {name}")
        generated_gate.append({"case": name, "expectedAccepted": accepted, "observedAccepted": observed, "error": error})
    digest_bytes = b"owned-artifact-test"
    if not verify_artifact_digest(digest_bytes, "sha256:" + sha(digest_bytes)):
        raise AssertionError("Matching declared artifact digest was not accepted")
    try:
        verify_artifact_digest(digest_bytes, "sha256:" + "0" * 64)
    except ValueError:
        pass
    else:
        raise AssertionError("Mismatched declared artifact digest was not rejected")
    report = {"ok": True, "testedCommit": ref, "cases": rows,
              "verifierSha256": sha(Path(__file__).read_bytes()),
              "generatedEntryPageGate": generated_gate,
              "matchingArtifactDigestAcceptedAndMismatchRejected": True,
              "tested": ["Exact committed builder source mappings and CDN/metadata/normalization transforms", "HTTP exact byte equality", "One-byte-content tampering rejected", "Missing deployed resource rejected", "Nonempty compiled gallery entry page required, orphan/empty negative cases rejected", "Owned local server lifecycle cleanup"]}
    target = PROJECT / "artifacts/reviews/publication-verifier-self-test.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "report": target.relative_to(ROOT).as_posix(), "httpCaseCount": len(rows), "generatedEntryPageCaseCount": len(generated_gate)}, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-ref")
    parser.add_argument("--base-ref", default="daaee75353c63ed6dde204d57cfdbae6b9936586")
    parser.add_argument("--workflow-run")
    parser.add_argument("--repository", default=REPOSITORY)
    parser.add_argument("--public-base", default=PUBLIC)
    parser.add_argument("--plan-only", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not args.expected_ref:
        parser.error("--expected-ref is required unless --self-test is used")
    ref = git("rev-parse", "--verify", args.expected_ref + "^{commit}").decode().strip()
    base = git("rev-parse", "--verify", args.base_ref + "^{commit}").decode().strip()
    output = (args.output_dir or PROJECT / "artifacts/reviews/publication" / ref / ("plan" if args.plan_only else "deployed")).resolve()
    if not output.is_relative_to(PROJECT.resolve()):
        parser.error("Publication evidence must remain inside projects/grayscale-interleave")
    output.mkdir(parents=True, exist_ok=True)
    context, resources = plan_resources(ref, base, args.repository, args.public_base)
    context["verifierSha256"] = sha(Path(__file__).read_bytes())
    if args.plan_only:
        context["planOnly"] = True
        context["resourceCountWithoutGeneratedBundles"] = len(resources)
        context["resources"] = [{key: value for key, value in row.items() if key != "expected"}
                                | {"expectedSha256": sha(row["expected"]), "sizeBytes": len(row["expected"])}
                                for row in resources.values()]
        target = output / "plan.json"
        target.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: value for key, value in context.items() if key != "resources"} | {"report": target.relative_to(ROOT).as_posix()}, indent=2))
        return 0
    if not args.workflow_run:
        parser.error("Release verification requires --workflow-run for exact commit/artifact provenance")
    provenance, pages = workflow_pages(args.repository, args.workflow_run, ref, output)
    artifact_checks = []
    for row in resources.values():
        if row["route"] is None:
            continue
        observed = pages.get(row["route"])
        artifact_checks.append({"route": row["route"], "ok": observed == row["expected"],
                                "expectedSha256": sha(row["expected"]), "artifactSha256": sha(observed) if observed is not None else None})
    add_generated_resources(resources, pages, context["generatedRoutesRequiringExactWorkflowArtifact"], args.public_base)
    print(f"Verifying {len(resources)} exact-commit resources; output: {output.relative_to(ROOT).as_posix()}", flush=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        rows = list(executor.map(lambda row: verify_url(row, ref), resources.values()))
    findings = [row for row in rows if not row["ok"]]
    artifact_findings = [row for row in artifact_checks if not row["ok"]]
    report = context | {"ok": not findings and not artifact_findings, "workflow": provenance,
                        "checkedResources": len(rows), "artifactSourceChecks": artifact_checks,
                        "artifactSourceFindings": artifact_findings, "findings": findings, "resources": rows}
    target = output / "publication.json"
    target.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": report["ok"], "expectedRef": ref, "workflowRun": args.workflow_run,
                      "checkedResources": len(rows), "findings": findings, "artifactSourceFindings": artifact_findings,
                      "report": target.relative_to(ROOT).as_posix()}, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
