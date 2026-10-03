#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Download the exact successful Pages artifact and safely extract it locally."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[3]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--commit", required=True)
    args = parser.parse_args()
    if not args.run_id.isdigit():
        raise SystemExit("Run ID must contain only digits.")
    workflow = json.loads(subprocess.check_output(["gh", "run", "view", args.run_id,
        "--json", "headSha,status,conclusion,url,workflowName,jobs"], cwd=ROOT, text=True))
    deployed = any(step["name"] == "Deploy Pages" and step["conclusion"] == "success"
                   for job in workflow["jobs"] for step in job["steps"])
    if (workflow["headSha"] != args.commit or workflow["workflowName"] != "Publish GitHub Pages"
            or workflow["status"] != "completed" or workflow["conclusion"] != "success" or not deployed):
        raise SystemExit("The requested commit has no successful Pages deployment in this run.")
    repository = json.loads(subprocess.check_output(["gh", "repo", "view", "--json", "nameWithOwner"],
                                                   cwd=ROOT, text=True))["nameWithOwner"]
    artifacts = json.loads(subprocess.check_output(["gh", "api",
        f"repos/{repository}/actions/runs/{args.run_id}/artifacts"], cwd=ROOT, text=True))["artifacts"]
    matches = [item for item in artifacts if item["name"] == "github-pages" and not item["expired"]]
    if len(matches) != 1:
        raise SystemExit("Expected one nonexpired github-pages artifact for this run.")
    artifact = matches[0]
    if (artifact.get("workflow_run", {}).get("id") != int(args.run_id)
            or artifact["workflow_run"].get("head_sha") != args.commit):
        raise SystemExit("Pages artifact metadata does not bind the requested run and commit.")
    destination = ROOT / "projects/arrow-contrast/artifacts/publication" / args.run_id
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / "artifact.tar"
    provenance_path = destination / "pages-provenance.json"
    if archive.exists():
        if not provenance_path.is_file():
            raise SystemExit("A cached artifact has no verified provenance; use a fresh run directory.")
        prior = json.loads(provenance_path.read_text())
        if (prior["runId"] != args.run_id or prior["sourceCommit"] != args.commit
                or prior["artifact"]["id"] != artifact["id"]
                or prior["artifact"].get("digest") != artifact.get("digest")
                or prior["tarSha256"] != hashlib.sha256(archive.read_bytes()).hexdigest()):
            raise SystemExit("Cached Pages artifact differs from the verified workflow provenance.")
    if not archive.is_file():
        subprocess.run(["gh", "run", "download", args.run_id, "--name", "github-pages",
                        "--dir", str(destination)], cwd=ROOT, check=True)
    extracted = destination / "pages"
    extracted.mkdir(exist_ok=True)
    with tarfile.open(archive) as bundle:
        for member in bundle.getmembers():
            target = (extracted / member.name).resolve()
            if not target.is_relative_to(extracted.resolve()) or member.issym() or member.islnk():
                raise SystemExit(f"Unsafe artifact member: {member.name}")
            if not member.isfile() and not member.isdir():
                raise SystemExit(f"Unsupported artifact member: {member.name}")
        bundle.extractall(extracted, filter="data")
    if not (extracted / "index.html").is_file():
        raise SystemExit("Extracted Pages artifact has no root index.html.")
    files = {path.relative_to(extracted).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(extracted.rglob("*")) if path.is_file()}
    proof = {"runId": args.run_id, "sourceCommit": args.commit, "repository": repository,
             "workflow": workflow, "artifact": artifact,
             "tarSha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
             "buildRoot": extracted.relative_to(ROOT).as_posix(), "files": files,
             "downloadCommand": ["gh", "run", "download", args.run_id, "--name", "github-pages",
                                 "--dir", str(destination)],
             "scope": "Fresh authenticated CLI download from the named successful Pages run; cached tar reuse requires matching run/SHA/artifact metadata and tar hash. GitHub artifact digest describes its outer archive, not this extracted tar hash."}
    provenance_path.write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8")
    print(extracted.relative_to(ROOT).as_posix())


if __name__ == "__main__":
    main()
