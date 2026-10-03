#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "numpy==2.2.6", "defusedxml==0.7.1"]
# ///
"""Blindly curate a fresh three-case pilot gate, without exposing its content."""
import base64
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import zipfile

from PIL import Image, ImageDraw, ImageOps
from svg_art_direction import PROGRAM, IMAGE, IMAGE_ID
from svg_excellence import make_evidence, read, write, sha

REPO = Path(__file__).resolve().parents[3]
ROOT = REPO / "evaluations/runs/svt1"
PRIOR = REPO / "evaluations/runs/svg-technique-v6.3"
PERSONAL = Path("C:/Users/villa/OneDrive/Documentos/ChatGPT/personal")


def wsl(path):
    return "/mnt/c/" + Path(path).resolve().as_posix()[3:]


def curate(root=None, prior_roots=(), samples_per_pack=2):
    global ROOT
    if root is not None:
        ROOT = Path(root)
    ROOT.mkdir(parents=True, exist_ok=False)
    private = ROOT / "private"
    private.mkdir()
    catalog = read(PERSONAL / "assets/fox-rockett/catalogo.json")
    registry = read(PRIOR / "frozen/evaluator/anchor-registry.json")
    seen = {x["sha256"] for x in registry.values()}
    excluded_packs = {a["pack_id"] for a in catalog["assets"] if a["sha256"] in seen}
    historical = []
    for prior_root in prior_roots:
        prior_root = Path(prior_root)
        rows = read(prior_root / "private/manifest.json")
        excluded_packs.update(row["pack"] for row in rows)
        seen.update(row["sha256"] for row in read(prior_root / "private/pool.json"))
        for row in rows:
            historical.append((prior_root / "private" / f"pool-{row['pool_index']}.png", row))
    # The entire public sample inventory and all packs used by this development
    # comparison are excluded before any candidate scores exist.
    eligible = [a for a in catalog["assets"] if a["pack_id"] not in excluded_packs and a["sha256"] not in seen
                and not a["sample_id"] and not a["contains_raster"]
                and not a["external_references"] and not a["active_content"]]
    seed = secrets.token_hex(32)
    write(private / "seed.json", {"seed": seed})
    pool = []
    for pack in sorted({a["pack_id"] for a in eligible}):
        rows = sorted([a for a in eligible if a["pack_id"] == pack],
                      key=lambda a: sha((seed + a["sha256"]).encode()))
        pool.extend(rows[:samples_per_pack])
    write(private / "pool.json", pool)
    write(ROOT / "authoring-commitment.json", {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "seed_commitment": sha(seed.encode()), "pool_digest": sha((private / "pool.json").read_bytes()),
        "candidate_scores_seen": False, "curator_calls_cap": 1,
        "selection": f"{samples_per_pack} digest-seeded items per unused development or consumed-validation pack; omit all prior pool sources, catalog preview items, raster, active content and external references. Isolated curator chooses exactly three distinct construction families from three packs or rejects the gate.",
        "limitations": "Small pilot; publisher/style population is shared. New construction and source families, not unseen authors or general vector art. Optimizer has host privileges but must not inspect sealed files; generator isolation is independently runtime-audited.",
    })
    fonts = PRIOR / "frozen/evaluator/fonts"
    tiles = []
    def tile(render, label):
        raw = Image.open(render).convert("RGBA")
        matte = Image.new("RGBA",raw.size,"white"); matte.alpha_composite(raw)
        small = ImageOps.contain(matte.convert("RGB"),(375,310))
        cell = Image.new("RGB",(400,350),"white")
        cell.paste(small,((400-small.width)//2,30+(310-small.height)//2))
        ImageDraw.Draw(cell).text((10,8),label,fill="black")
        return cell
    dev_briefs = []
    for index, task in enumerate(sorted((PRIOR / "ds").iterdir())):
        spec = read(task / "tests/quality-anchor.json")
        dst = private / f"dev-{index}.png"
        make_evidence((PRIOR / "frozen/evaluator" / spec["file"]).read_bytes(),"",{},fonts,dst)
        tiles.append(tile(dst,f"DEVELOPMENT {index + 1}: exclude this construction"))
        dev_briefs.append((task / "instruction.md").read_text().split("\n\n")[0])
    for index, (render, row) in enumerate(historical):
        tiles.append(tile(render, f"CONSUMED FAMILY {index + 1}: exclude this construction"))
        dev_briefs.append("Consumed construction: " + row["family"])
    for index, item in enumerate(pool):
        with zipfile.ZipFile(Path(catalog["source_root"]) / item["archive"]) as archive:
            raw = archive.read(item["member"])
        assert sha(raw) == item["sha256"]
        (private / f"pool-{index}.svg").write_bytes(raw)
        dst = private / f"pool-{index}.png"
        evidence = make_evidence(raw,"",{},fonts,dst)
        if not evidence["artifact_valid"]:
            raise ValueError("Private source failed deterministic vector validation")
        tiles.append(tile(dst,f"CANDIDATE SOURCE {index} / group {item['pack_id']}"))
    board = Image.new("RGB",(1600,350*((len(tiles)+3)//4)),"white")
    for i, cell in enumerate(tiles): board.paste(cell,((i%4)*400,(i//4)*350))
    buffer = io.BytesIO(); board.save(buffer,format="PNG"); png = buffer.getvalue()
    (private / "curator-board.png").write_bytes(png)
    profiles = read(PRIOR / "frozen/evaluator/use-profiles.json")
    prompt = """You are the independent dataset curator, not the skill optimizer. The first six drawings are already exposed development families; the remaining drawings are possible private sources. Choose exactly three suitable private sources from THREE DIFFERENT groups. Reject any near-duplicate, transformed sibling, or same solution/construction template as the six exposed drawings or another chosen drawing. Sharing broad monochrome capability is fine; merely changing a face, a circular intertwined ring, an oscillation, an arrow HUD, a compact label or a spaceship's proportions is NOT fresh construction. Also reject a source if none of the fixed purpose profiles honestly fits it. Do not change the profiles. If three cannot satisfy both conditions, return {\"passed\":false,\"reason\":\"...\",\"selected\":[]}.
For each accepted source, author a short natural Spanish human request (one or two sentences, <=65 words). It must honestly describe the main subject and purpose visible in the source, leave stylistic latitude, contain no precise coordinates/counts/path instructions, no asset identity and no discussion of evaluators. Do not add a required feature not present in the source. Do not just reuse a development prompt. Give the source its best legitimate use, not an invented space or vintage story. We evaluate skill transfer, not reconstruction.
For passed=true return JSON only: {\"passed\":true,\"selected\":[{\"pool_index\":0,\"profile\":\"fixed profile key\",\"brief\":\"short Spanish request\",\"family\":\"distinct construction mechanism\",\"source_fit\":\"located facts showing the reference satisfies this brief\",\"independence\":\"how construction differs from all exposed families\",\"valid_alternative\":\"a materially different drawing that would also satisfy the request\"}],\"limitations\":[\"...\"]}.
This is curator review only: no quality scores, no skill candidates or generated results are available.
""" + "\nFIXED PROFILES:\n" + json.dumps(profiles) + "\nEXPOSED BRIEFS:\n" + json.dumps(dev_briefs,ensure_ascii=False)
    if historical:
        prompt = prompt.replace("The first six drawings are already exposed development families;", f"The first {6 + len(historical)} drawings are excluded development or previously consumed validation families;")
        prompt += "\nAlso reject any sibling or transformed solution template of EVERY consumed family pictured before the candidate sources. These earlier validation outcomes are not available and must not inform quality ranking. All source packs used by those consumed families have already been excluded."
    write(private / "curator-input.json",{"prompt":prompt,"image_sha256":sha(png)})
    docker = ["wsl","-e","docker"]
    assert json.loads(subprocess.check_output(docker+["image","inspect",IMAGE]))[0]["Id"] == IMAGE_ID
    auth = {"openai-codex": read(Path("C:/Users/villa/.pi/agent/auth.json"))["openai-codex"]}
    result = subprocess.run(docker+["run","--rm","-i","--network","bridge",IMAGE,"python3","-c",PROGRAM],
                            input=json.dumps({"auth":auth,"model":"gpt-6-astra","prompt":prompt,"image":base64.b64encode(png).decode()}),
                            capture_output=True,text=True,encoding="utf-8",timeout=390)
    (private / "curator-events.jsonl").write_text(result.stdout,encoding="utf-8")
    (private / "curator-stderr.txt").write_text(result.stderr,encoding="utf-8")
    events = [json.loads(x) for x in result.stdout.splitlines() if x.startswith("{")]
    assert not any(e.get("type")=="tool_execution_start" for e in events)
    messages = [e["message"] for e in events if e.get("type")=="message_end" and e.get("message",{}).get("role")=="assistant"]
    assert result.returncode == 0 and messages and all(m.get("model")=="gpt-6-astra" for m in messages)
    assert messages[-1].get("stopReason") not in {"error","aborted"}
    answer = "\n".join(x["text"] for x in messages[-1]["content"] if x.get("type")=="text").strip()
    if answer.startswith("```json"): answer = answer[7:-3].strip()
    review = json.loads(answer)
    write(private / "curation.json",review)
    write(ROOT / "curation-status.json",{"passed":review["passed"],"selected_count":len(review["selected"]),
                                        "review_sha256":sha((private / "curation.json").read_bytes()),"model":"gpt-6-astra","usage":messages[-1].get("usage")})
    if not review["passed"]:
        print(json.dumps({"passed":False,"selected_count":0,"reason":"Independent curator could not establish three disjoint suitable families; no candidate inference authorized."}))
        return
    materialize()


def materialize(expected_families=3):
    # This phase is restartable after a local file-write failure. It never
    # calls a model or selects another source from the fixed curator result.
    private = ROOT / "private"
    review = read(private / "curation.json")
    assert review["passed"]
    pool = read(private / "pool.json")
    profiles = read(PRIOR / "frozen/evaluator/use-profiles.json")
    selected = review["selected"]
    assert 1 <= expected_families <= 3
    assert len(selected)==expected_families and len({x["pool_index"] for x in selected})==expected_families
    assert len({pool[x["pool_index"]]["pack_id"] for x in selected})==expected_families
    bundle = ROOT / "evaluator"
    if not bundle.exists(): shutil.copytree(PRIOR / "frozen/evaluator",bundle)
    template = next((PRIOR / "ds").iterdir())
    private_manifest = []
    for i, row in enumerate(selected):
        assert row["profile"] in profiles and len(row["brief"].split())<=65
        assert row["source_fit"] and row["independence"] and row["valid_alternative"]
        raw = (private / f"pool-{row['pool_index']}.svg").read_bytes()
        anchor = f"anchors/{sha(raw)}.svg"; (bundle / anchor).write_bytes(raw)
        task = private / "validation" / f"case-{i+1}"
        if not task.exists(): shutil.copytree(template,task)
        output = f"/logs/artifacts/{['delivery/illustration.svg','final/asset.svg','result/vector.svg'][i]}"
        instruction = row["brief"] + "\n\nEntrégalo como un SVG autocontenido y editable, negro sobre fondo transparente, solo con formas vectoriales. Incluye un viewBox válido; no uses imágenes incrustadas, scripts ni recursos externos. El archivo debe pesar como máximo 2 MB. Guarda el resultado en `" + output + "`.\n"
        (task / "instruction.md").write_text(instruction,encoding="utf-8",newline="\n")
        (task / "tests/quality-anchor.json").write_text(json.dumps({"file":anchor,"sha256":sha(raw),"profile":row["profile"]},indent=2),encoding="utf-8")
        (task / "tests/request-contract.json").write_text(json.dumps({"brief":row["brief"],"use_profile":row["profile"],"artifact_path":output},indent=2),encoding="utf-8")
        # No source solution is copied into the executor or its build context.
        private_manifest.append({"task":task.name,"pool_index":row["pool_index"],"source_sha256":sha(raw),"pack":pool[row['pool_index']]['pack_id'],"family":row['family'],"output":output})
    write(private / "manifest.json",private_manifest)
    shutil.copytree(PRIOR / "ds",ROOT / "development")
    # Extend only the evaluator's anchor inventory. Every executable scoring
    # byte, judge model, purpose profile and prompt stays bit-identical to 6.3.
    lock = read(bundle / "lock.json")
    for p in (bundle / "anchors").glob("*.svg"):
        lock["files"][p.relative_to(bundle).as_posix()] = sha(p.read_bytes())
    (bundle / "lock.json").write_text(json.dumps(lock,indent=2)+"\n",encoding="utf-8")
    for rel, expected in read(PRIOR / "frozen/evaluator/lock.json")["files"].items():
        assert sha((bundle / rel).read_bytes()) == expected
    write(ROOT / "evaluator-extension.json",{"parent_lock_sha256":sha((PRIOR / "frozen/evaluator/lock.json").read_bytes()),
        "lock_sha256":sha((bundle / "lock.json").read_bytes()),"added_anchors":expected_families,"scoring_bytes_unchanged":True})
    print(json.dumps({"passed":True,"selected_count":expected_families,"source_pack_groups":expected_families,"scoring_bytes_unchanged":True,"private_content_disclosed":False}))


if __name__ == "__main__":
    materialize() if sys.argv[1:] == ["materialize"] else curate()
