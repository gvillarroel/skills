#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["Pillow>=11,<13"]
# ///
"""Independently audit exact identities, downloaded bytes, and runtime traces."""
import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
from PIL import Image

PROVIDERS = {"polyhaven": "Poly Haven", "ambientcg": "ambientCG", "iconify": "Iconify", "kenney": "Kenney", "pexels": "Pexels"}
CONTRACTS = {"polyhaven": ("deck.jpg", "wood_floor_deck", "Diffuse/1k/jpg"), "ambientcg": ("wood.zip", "Wood095", "1K-JPG/zip"),
             "iconify": ("house.svg", "lucide:house", "svg"), "kenney": ("patterns.zip", "pattern-pack", "kenney_pattern-pack.zip")}
GENERALIZATION = {"polyhaven": ("sunset.hdr", "hdri/1k/hdr"), "ambientcg": ("brick.zip", "1K-PNG/zip"),
                  "iconify": ("search.svg", "svg"), "kenney": ("nature.zip", None)}


class Gallery(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.images = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "img": self.images.append(dict(attrs).get("src", ""))


def read(path):
    return json.loads(path.read_text(encoding="utf8"))


def digest(path):
    with path.open("rb") as f: return hashlib.file_digest(f, "sha256").hexdigest()


def audit(run):
    source, case = run.name.split("-")[1:3]
    if source not in PROVIDERS or case not in ("contract", "naturalistic", "generalization", "boundary"):
        return None
    evaluation = run / "evaluation-result.json"
    if not evaluation.exists(): return None
    result = {"run_id": run.name, "source": source, "case": case, "strict_passed": read(evaluation)["passed"], "independent_passed": False}
    try:
        manifest = read(run / "run-manifest.json")
        result["payload_sha256"] = manifest["skill"]["payloadSha256"]
        result["model"] = manifest["pi"]["model"]
        events = read(run / "event-check.json")
        result["read_surface"] = [c["path"] for c in events["calls"] if c["tool"] == "read"]
        result["tool_errors"] = sum(bool(c.get("isError")) for c in events["calls"])
        workspace = run / "workspace"
        artifacts = workspace / "artifacts"
        result["files"] = [{"path": p, "bytes": (workspace / p).stat().st_size, "sha256": digest(workspace / p)} for p in manifest["expectedOutputs"]]
        if source == "pexels":
            access = read(artifacts / "access.json")
            if "api_key_configured" in access:
                assert access["api_key_configured"] is False
            else:
                assert access.get("api_key_present") is False and access.get("api_access") is False
            assert not list(artifacts.glob("*.jpeg")) and not list(artifacts.glob("*.mp4"))
            result["scope"] = "Access recovery and offline contract only; live authenticated search/download untested."
        elif case == "boundary":
            assert {p.name for p in artifacts.iterdir()} == {"reply.md"}
            reply = (artifacts / "reply.md").read_text(encoding="utf8")
            assert "?" in reply
            assert not any(" download " in str(c.get("command", "")) for c in events["calls"])
        else:
            options = None
            if case in ("naturalistic", "generalization"):
                options = read(artifacts / "options.json")
                assert options["provider"] == PROVIDERS[source]
                rows = options["results"]
                assert len(rows) == (4 if case == "naturalistic" else 3)
                # Curated subsets preserve their original numbers, which may have gaps.
                assert all(isinstance(r["option"], int) and r["option"] > 0 for r in rows)
                assert len({r["option"] for r in rows}) == len(rows)
                assert len({r["id"] for r in rows}) == len(rows)
                page = (artifacts / "options.html").read_text(encoding="utf8")
                assert page.count('data-resource-id="') == len(rows)
                for src in Gallery(page).images:
                    parsed = urlsplit(src)
                    assert src and parsed.scheme in ("", "https", "data")
                    if not parsed.scheme:
                        assert (artifacts / unquote(parsed.path)).is_file(), "Broken local preview: " + src
                if source == "iconify":
                    prefix = "lucide:" if case == "naturalistic" else "mdi:"
                    assert all(r["id"].startswith(prefix) for r in rows)
                if source == "polyhaven":
                    assert all(r["type"] == ("textures" if case == "naturalistic" else "hdris") for r in rows)
                result["option_ids"] = [r["id"] for r in rows]
            if case != "naturalistic":
                if case == "contract": filename, expected_id, variant = CONTRACTS[source]
                else:
                    filename, variant = GENERALIZATION[source]
                    expected_id = next(r["id"] for r in options["results"] if r["option"] == 2)
                path = artifacts / filename
                receipt = read(Path(str(path) + ".json"))
                assert receipt["provider"] == PROVIDERS[source]
                assert receipt["asset_id"] == expected_id == receipt["source"]["id"]
                if variant: assert receipt["variant"] == variant
                assert receipt["file"]["sha256"] == digest(path)
                assert receipt["file"]["bytes"] == path.stat().st_size > 0
                if receipt["file"].get("provider_md5"):
                    with path.open("rb") as f: assert hashlib.file_digest(f, "md5").hexdigest() == receipt["file"]["provider_md5"]
                result["selected_id"] = expected_id
                result["variant"] = receipt["variant"]
                if path.suffix == ".jpg":
                    with Image.open(path) as image:
                        image.load(); assert image.width == 1024 and image.height == 1024
                        result["decoded_dimensions"] = list(image.size)
                if path.suffix == ".hdr":
                    header = path.read_bytes()[:2048]
                    match = re.search(rb"-Y (\d+) \+X (\d+)", header)
                    assert match and int(match[2]) == 1024
                    result["hdr_dimensions"] = [int(match[2]), int(match[1])]
                if path.suffix == ".svg":
                    root = ElementTree.parse(path).getroot()
                    assert root.tag.endswith("svg")
                    color, height = ("#334155", "32") if case == "contract" else ("#2563eb", "40")
                    assert root.get("height") == height
                    assert color in path.read_text(encoding="utf8")
                    assert receipt["source"]["export"] == {"color": color, "height": int(height)}
                if path.suffix == ".zip":
                    with zipfile.ZipFile(path) as z:
                        assert z.testzip() is None
                        result["zip_members"] = len(z.infolist())
                        if source == "ambientcg":
                            images = [n for n in z.namelist() if n.lower().endswith((".png", ".jpg"))]
                            for name in images:
                                with Image.open(io.BytesIO(z.read(name))) as image: image.load()
                            result["decoded_maps"] = images
                            assert len(images) >= 3
                        if source == "kenney" and case == "generalization":
                            extraction = read(artifacts / "license-only/extraction.json")
                            assert extraction["archive_sha256"] == digest(path)
                            assert extraction["files"]
                            for item in extraction["files"]:
                                assert re.search(r"licen[cs]e|copying", item["path"], re.I)
                                assert (artifacts / "license-only" / item["path"]).read_bytes() == z.read(item["path"])
        result["independent_passed"] = True
    except Exception as exc:
        result["error"] = type(exc).__name__ + ": " + str(exc)
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="evaluations/free-resource-skills/artifact-audit-20260927.json")
    args = p.parse_args()
    results = [r for run in sorted(Path("evaluations/runs").glob("free-*-20260927-*")) if (r := audit(run))]
    report = {"date": "2026-09-27", "results": results}
    Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps({"completed_runs": len(results), "strict_passes": sum(r["strict_passed"] for r in results),
                      "independent_passes": sum(r["independent_passed"] for r in results),
                      "joint_passes": sum(r["strict_passed"] and r["independent_passed"] for r in results),
                      "failures": [{"run_id": r["run_id"], "error": r.get("error")} for r in results if not r["strict_passed"] or not r["independent_passed"]]}, indent=2))


if __name__ == "__main__": main()
