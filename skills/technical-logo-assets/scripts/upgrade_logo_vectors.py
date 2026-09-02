#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml==6.0.3"]
# ///
"""Replace raster/symlink wrappers using exact, source-mapped vector artwork."""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

import yaml

from logo_svg import digest, embedded_source, inspect_vector
from sync_normalized_logos import wrapped_svg, license_log


AWS_ZIP = "https://d1.awsstatic.com/onedam/marketing-channels/website/public/shared/architecture-icon-release/Icon-package_07312026.5846e92413caa21490223536cc97f1269e44fa92.zip"
GCP_ZIP = "https://services.google.com/fh/files/misc/google-cloud-legacy-icons.zip"
ARCHIVE_REPO = "https://github.com/DataDog/pathfinding.cloud"
ARCHIVE_COMMIT = "a81659da620b83399f98025f8de001816d9adec6"
GCP_ALIASES = {
    "AIPlatformDataLabelingService": "data_labeling", "CloudAutoML": "automl",
    "CloudSpeechtoText": "speech-to-text", "CloudTexttoSpeech": "text-to-speech",
    "CloudVideoIntelligenceAPI": "video_intelligence_api", "DialogFlowEnterpriseEdition": "dialogflow",
    "GPU": "cloud_gpu", "KubernetesEngine": "google_kubernetes_engine",
    "CloudDataCatalog": "data_catalog", "CloudDataflow": "dataflow", "CloudDatalab": "datalab",
    "CloudDataprep": "dataprep", "CloudDataproc": "dataproc", "CloudPubSub": "pubsub",
    "CloudBigtable": "bigtable", "CloudDatastore": "datastore", "CloudFirestore": "firestore",
    "CloudMemorystore": "memorystore", "CloudToolsforPowerShell": "tools_for_powershell",
    "CloudIoTCore": "iot_core", "CloudServiceMesh": "anthos_service_mesh", "Logging": "cloud_logging",
    "DedicatedInterconnect": "cloud_interconnect", "CloudIAM": "identity_and_access_management",
    "CloudSecurityCommandCenter": "security_command_center", "CloudFilestore": "filestore",
}


def semantic(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def raw_url(repository: str, commit: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repository.removeprefix('https://github.com/')}/{commit}/{quote(path, safe='/')}"


def prepare_replacements(manifest: dict, sources: Path) -> tuple[dict, dict[str, bytes]]:
    upgraded = copy.deepcopy(manifest)
    aws_config = yaml.safe_load((sources / "aws/scripts/config.yml").read_text(encoding="utf-8"))
    aws_map = {(category, row["Target"]): row for category, data in aws_config["Categories"].items() for row in data.get("Icons", [])}
    gcp_config = yaml.safe_load((sources / "gcp/scripts/config.yml").read_text(encoding="utf-8"))
    gcp_map = {(category["Name"], row["Target"]): row for category in gcp_config["Categories"] for row in category.get("Services", [])}
    gcp_files = {semantic(path.stem): path for path in (sources / "gcp-legacy").rglob("*.svg")}
    payloads = {}
    missing = []
    aws_zip_hash = digest((sources / "aws-official.zip").read_bytes())
    gcp_zip_hash = digest((sources / "gcp-legacy.zip").read_bytes())
    for item in upgraded["logos"]:
        original = copy.deepcopy(item)
        base_source = original.get("previousSource", original)
        target = Path(base_source["sourcePath"]).stem
        path = None
        source_info = {}
        if item["provider"] == "AWS":
            dark = target.endswith("_Dark")
            row = aws_map.get((item["category"], target.removesuffix("_Dark")))
            if not row:
                missing.append(item["id"] + ": no upstream target mapping")
                continue
            file_name = Path(row.get("SourceDark" if dark else "Source", "")).with_suffix(".svg").name
            source_dir = row.get("SourceDirDark" if dark else "SourceDir", "")
            official_dir = re.sub(r"_01302026(?=/|$)", "_07312026", source_dir)
            candidate = sources / "aws-official" / official_dir / file_name
            if candidate.is_file():
                path = candidate
                member = path.relative_to(sources / "aws-official").as_posix()
                source_info = {"sourcePath": member, "sourceUrl": AWS_ZIP, "sourceArchiveMember": member,
                               "sourceArchiveSha256": aws_zip_hash, "sourceRepository": "https://aws.amazon.com/architecture/icons/",
                               "sourceCommit": "release-2026-07-31", "artworkStatus": "official-release"}
            else:
                candidate = sources / "aws" / "source/unofficial" / source_dir / file_name
                if candidate.is_file():
                    path = candidate
                    relative = path.relative_to(sources / "aws").as_posix()
                    source_info = {"sourcePath": relative, "sourceUrl": raw_url(base_source["sourceRepository"], base_source["sourceCommit"], relative),
                                   "sourceRepository": base_source["sourceRepository"], "sourceCommit": base_source["sourceCommit"], "artworkStatus": "pinned-group-artwork"}
                else:
                    candidate = sources / "aws-archive/docs/img/aws-icons" / source_dir / file_name
                    if candidate.is_file():
                        path = candidate
                        relative = path.relative_to(sources / "aws-archive").as_posix()
                        source_info = {"sourcePath": relative, "sourceUrl": raw_url(ARCHIVE_REPO, ARCHIVE_COMMIT, relative),
                                       "sourceRepository": ARCHIVE_REPO, "sourceCommit": ARCHIVE_COMMIT,
                                       "artworkStatus": "archived-2026-01-release", "originalSource": "https://aws.amazon.com/architecture/icons/"}
            source_info["identityMatch"] = "upstream-category-and-target-map"
            source_info["background"] = "dark" if dark else "light-or-dark"
        elif item["provider"] == "GCP":
            row = gcp_map[(item["category"], target)]
            name = GCP_ALIASES.get(target, Path(row["Source"]).stem)
            path = gcp_files.get(semantic(name))
            if path:
                member = path.relative_to(sources / "gcp-legacy").as_posix()
                source_info = {"sourcePath": member, "sourceUrl": GCP_ZIP, "sourceArchiveMember": member,
                               "sourceArchiveSha256": gcp_zip_hash, "sourceRepository": "https://cloud.google.com/icons",
                               "sourceCommit": "legacy-console-download-2026-08-28", "artworkStatus": "legacy-official-console",
                               "identityMatch": "explicit-product-alias" if target in GCP_ALIASES else "upstream-product-name"}
                if target in GCP_ALIASES:
                    source_info["sourceNameAlias"] = {"from": target, "to": name}
        elif item["id"] == "code-assistant-opencode":
            path = sources / "opencode-fixed/favicon-v3.svg"
            relative = "packages/ui/src/assets/favicon/favicon-v3.svg"
            source_info = {"sourcePath": relative, "sourceUrl": raw_url(base_source["sourceRepository"], base_source["sourceCommit"], relative),
                           "identityMatch": "resolved-official-git-symlink", "artworkStatus": "official-project"}
        elif item["id"] == "code-assistant-gemini-cli":
            path = sources / "lobe-icons/packages/static-svg/icons/geminicli-color.svg"
            source = manifest["sources"]["lobe-icons"]
            relative = path.relative_to(sources / "lobe-icons").as_posix()
            source_info = {"sourcePath": relative, "sourceUrl": raw_url(source["repository"], source["commit"], relative),
                           "sourceRepository": source["repository"], "sourceCommit": source["commit"],
                           "licenseId": source["licenseId"], "licenseUrl": source["licenseUrl"], "attribution": source["attribution"],
                           "identityMatch": "exact-product-mark-not-generic-gemini", "artworkStatus": "curated-project-mark"}
        else:
            continue
        if path is None or not path.is_file():
            missing.append(item["id"] + ": missing exact vector source")
            continue
        payload = path.read_bytes()
        try:
            inspect_vector(payload)
        except ValueError as error:
            raise ValueError(f"{item['id']}: {error}") from error
        if "previousSource" not in item:
            item["previousSource"] = {key: value for key, value in original.items() if key.startswith("source")}
        for key in ("sourceArchiveMember", "sourceArchiveSha256"):
            item.pop(key, None)
        item.update(source_info)
        item.update({"sourceFormat": "svg", "sourceSha256": digest(payload), "vectorOnly": True})
        payloads[item["id"]] = payload
    if missing:
        raise ValueError("Unresolved vector identities: " + "; ".join(missing))
    return upgraded, payloads


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True, help="Prepared, pinned source directories")
    parser.add_argument("--assets", type=Path, default=Path(__file__).resolve().parents[1] / "assets/logos")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--backup", type=Path, help="Required unused backup directory when applying")
    args = parser.parse_args()
    assets = args.assets.resolve()
    old = json.loads((assets / "logo_manifest.json").read_text(encoding="utf-8"))
    manifest, replacements = prepare_replacements(old, args.sources.resolve())
    for item in manifest["logos"]:
        payload = replacements.get(item["id"])
        if payload is None:
            payload = embedded_source((assets / item["assetPath"]).read_bytes())
        try:
            inspect_vector(payload)
        except ValueError as error:
            raise ValueError(f"{item['id']}: {error}") from error
        if digest(payload) != item["sourceSha256"]:
            raise ValueError(f"Source hash mismatch: {item['id']}")
        item["vectorOnly"] = True
    manifest["schemaVersion"] = 3
    manifest["vectorOnly"] = True
    manifest["vectorAuditDate"] = "2026-08-28"
    manifest["variantManifest"] = "logo_variants.json"
    source_groups = {
        "aws-official-svg": ("AWS", "https://aws.amazon.com/architecture/icons/", "release-2026-07-31", "CC-BY-ND-2.0"),
        "aws-archived-svg": ("AWS", ARCHIVE_REPO, ARCHIVE_COMMIT, "CC-BY-ND-2.0"),
        "gcp-legacy-svg": ("GCP", "https://cloud.google.com/icons", "legacy-console-download-2026-08-28", "CC-BY-ND-2.0"),
    }
    for key, (provider, repository, commit, license_id) in source_groups.items():
        manifest["sources"][key] = {"provider": provider, "repository": repository, "commit": commit,
                                    "licenseId": license_id, "licenseUrl": "https://creativecommons.org/licenses/by-nd/2.0/",
                                    "attribution": "Amazon Web Services" if provider == "AWS" else "Google Cloud"}
    lock = {"schemaVersion": 1, "replacements": {item["id"]: item for item in manifest["logos"] if item["id"] in replacements}}
    if args.apply:
        if not args.backup:
            parser.error("--apply requires a fresh --backup directory")
        backup = args.backup.resolve()
        if backup.exists() or backup == assets or backup.is_relative_to(assets) or assets.is_relative_to(backup):
            parser.error("Backup must be unused and separate from the logo asset directory")
        backup.mkdir(parents=True)
        shutil.copy2(assets / "logo_manifest.json", backup / "logo_manifest.json")
        shutil.copy2(assets / "license_log.md", backup / "license_log.md")
        for item in manifest["logos"]:
            source = assets / item["assetPath"]
            target = backup / item["assetPath"]
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        # No source is changed until every replacement and original passes inspection.
        for item in manifest["logos"]:
            source = replacements.get(item["id"])
            if source is None:
                source = embedded_source((assets / item["assetPath"]).read_bytes())
            (assets / item["assetPath"]).write_text(wrapped_svg(item, source, manifest["normalization"]), encoding="utf-8", newline="\n")
        (assets / "logo_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
        (assets / "vector_source_lock.json").write_text(json.dumps(lock, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
        (assets / "license_log.md").write_text(license_log(manifest), encoding="utf-8", newline="\n")
    print(json.dumps({"ok": True, "logoCount": len(manifest["logos"]), "vectorOnly": True, "replacedSources": len(replacements), "applied": args.apply}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
