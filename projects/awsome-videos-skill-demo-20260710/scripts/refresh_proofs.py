#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Refresh deterministic routing proofs from the asset manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "source" / "asset-manifest.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def resolve_project_path(relative_path: str) -> Path:
    normalized = Path(relative_path.replace("\\", "/"))
    if normalized.is_absolute() or ".." in normalized.parts:
        raise ValueError(f"Routing paths must stay inside the project: {relative_path}")
    resolved = (PROJECT_ROOT / normalized).resolve()
    if not resolved.is_relative_to(PROJECT_ROOT):
        raise ValueError(f"Routing path escapes the project: {relative_path}")
    if not resolved.is_file():
        raise FileNotFoundError(f"Routing artifact does not exist: {relative_path}")
    return resolved


def main() -> None:
    manifest = read_json(MANIFEST_PATH)
    routes = manifest.get("skillRouting")
    assets = manifest.get("assets")
    if not isinstance(routes, list) or not routes:
        raise ValueError("asset-manifest.json must contain a non-empty skillRouting list")
    if not isinstance(assets, list):
        raise ValueError("asset-manifest.json must contain an assets list")

    route_outputs: set[str] = set()
    refreshed_proofs: list[str] = []

    for route in routes:
        if not isinstance(route, dict):
            raise ValueError("Each skillRouting entry must be a JSON object")
        output_paths = route.get("outputPaths")
        proof_path = route.get("proof")
        if not isinstance(output_paths, list) or not output_paths:
            raise ValueError(f"Route {route.get('stage')!r} needs outputPaths")
        if not isinstance(proof_path, str) or not proof_path:
            raise ValueError(f"Route {route.get('stage')!r} needs a proof path")

        artifact_rows: list[dict[str, str]] = []
        for output_path in output_paths:
            if not isinstance(output_path, str) or not output_path:
                raise ValueError(f"Route {route.get('stage')!r} has an invalid output path")
            artifact_path = resolve_project_path(output_path)
            digest = sha256(artifact_path)
            artifact_rows.append({"path": output_path, "sha256": digest})
            route_outputs.add(output_path)

        first_digest = artifact_rows[0]["sha256"]
        proof = {
            "schemaVersion": 1,
            "ok": True,
            "stage": route.get("stage"),
            "skill": route.get("skill"),
            "output": route.get("output"),
            "sha256": first_digest,
            "outputSha256": first_digest,
            "artifacts": artifact_rows,
        }
        proof_file = PROJECT_ROOT / proof_path.replace("\\", "/")
        write_json(proof_file, proof)
        refreshed_proofs.append(proof_path)

    asset_manifest_changed = False
    for asset in assets:
        if not isinstance(asset, dict):
            raise ValueError("Each asset entry must be a JSON object")
        output_path = asset.get("output")
        if not isinstance(output_path, str) or output_path not in route_outputs:
            raise ValueError(
                f"Asset {asset.get('id')!r} output is not covered by skillRouting: {output_path!r}"
            )
        digest = sha256(resolve_project_path(output_path))
        if asset.get("sha256") != digest:
            asset["sha256"] = digest
            asset_manifest_changed = True

    if asset_manifest_changed:
        write_json(MANIFEST_PATH, manifest)

    print(
        json.dumps(
            {
                "ok": True,
                "projectRoot": str(PROJECT_ROOT),
                "proofsRefreshed": refreshed_proofs,
                "assetManifestChanged": asset_manifest_changed,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
