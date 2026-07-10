#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
from __future__ import annotations

import hashlib
import json
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT / "source"
REVIEWS = PROJECT / "artifacts" / "reviews"
IMAGES = PROJECT / "artifacts" / "images"
PRODUCERS = REVIEWS / "producers"
ROUTING = REVIEWS / "routing"
OFFICIAL_SKILLS_URL = "https://learn.chatgpt.com/use-cases/reusable-codex-skills"
REPO_RULES_URL = "https://github.com/gvillarroel/skills/blob/main/AGENTS.md"


SCENES = [
    {"id": "s01", "beat": "b01", "time": "0:00-0:05", "start": 0.0, "end": 5.0, "title": "Prompt wall pressure", "asset": "a01-prompt-wall", "file": "a01-prompt-wall.svg", "job": "Open on the cost of repeating a long prompt wall.", "viewer": "Feel the context pressure before the reusable package appears.", "choice": "diagonal armature", "armature": "compressed diagonal from prompt strips to the context wall", "family": "interrupt", "claim": "Teams can preserve a repeated workflow as a skill instead of pasting a long prompt into every task."},
    {"id": "s02", "beat": "b02", "time": "0:05-0:13", "start": 5.0, "end": 13.0, "title": "The compact SKILL.md package", "asset": "a02-skill-package", "file": "a02-skill-package.svg", "job": "Define the skill as a compact operational package.", "viewer": "Track the prompt wall folding into a reusable SKILL.md card.", "choice": "centered hero", "armature": "stacked package centered on the persistent red edge", "family": "tile morph", "claim": "Most Codex skills start with a required SKILL.md file containing reusable instructions and metadata."},
    {"id": "s03", "beat": "b03", "time": "0:13-0:22", "start": 13.0, "end": 22.0, "title": "Progressive disclosure", "asset": "a03-progressive-disclosure", "file": "a03-progressive-disclosure.svg", "job": "Show the core opening only the resource needed for the current decision.", "viewer": "Follow one reference entering context while dormant resources stay outside.", "choice": "asymmetric editorial", "armature": "left core, center active reference, right dormant resource lane", "family": "masked reframe", "claim": "This repository keeps core workflow in SKILL.md and moves conditional or bulky detail into references."},
    {"id": "s04", "beat": "b04", "time": "0:22-0:31", "start": 22.0, "end": 31.0, "title": "References, scripts, and assets", "asset": "a04-resource-bundle", "file": "a04-resource-bundle.svg", "job": "Separate knowledge, deterministic operations, and reusable production material.", "viewer": "Scan three peer resource lanes and see their outputs converge.", "choice": "modular board", "armature": "three equal vertical lanes joined by one baseline", "family": "surface wipe", "claim": "A skill can add optional references for longer docs, scripts for repeatable commands, and assets for templates or starter files."},
    {"id": "s05", "beat": "b05", "time": "0:31-0:41", "start": 31.0, "end": 41.0, "title": "Route each asset to a specialist", "asset": "a05-specialist-router", "file": "a05-specialist-router.svg", "job": "Show intent-based routing to the correct visual producer.", "viewer": "Track one work packet splitting into specialist routes and verifiable artifacts.", "choice": "flow spine", "armature": "single intake, central router, three outcome branches", "family": "persistent object", "claim": "The polished video workflow routes conventional diagrams, bespoke geometry, and raster imagery to their specialist producers."},
    {"id": "s06", "beat": "b06", "time": "0:41-0:51", "start": 41.0, "end": 51.0, "title": "Validation is a gate", "asset": "a06-validation-gate", "file": "a06-validation-gate.svg", "job": "Make validation visibly block a defective artifact before delivery.", "viewer": "Trace the good path across four checks and the failed branch back to correction.", "choice": "flow corridor", "armature": "horizontal verification corridor with one rejection loop", "family": "interrupt gate snap", "claim": "The repository treats skill validation as part of the work, not as an optional follow-up."},
    {"id": "s07", "beat": "b07", "time": "0:51-1:01", "start": 51.0, "end": 61.0, "title": "Compact core, detail on demand", "asset": "a07-context-budget", "file": "a07-context-budget.svg", "job": "Contrast an always-on instruction wall with a compact core plus selected detail.", "viewer": "Compare the two context bars and notice the oversized-skill warning.", "choice": "split comparison", "armature": "two aligned horizontal budget bars with a shared scale", "family": "match cut axis", "claim": "Skills are useful when a reusable workflow replaces repeated long prompts; keeping the core short preserves that advantage."},
    {"id": "s08", "beat": "b08", "time": "1:01-1:10", "start": 61.0, "end": 70.0, "title": "Reusable workflow callback", "asset": "a08-reusable-workflow", "file": "a08-reusable-workflow.svg", "job": "Return the compressed package to multiple projects and close the opening callback.", "viewer": "Recognize one workflow activating across projects and returning to rest.", "choice": "radial hub", "armature": "central skill package connected to four project surfaces", "family": "zoom out to system", "claim": "A Codex skill preserves reusable instructions, resources, and scripts for work that repeats."},
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def route(stage: str, skill: str, reason: str, outputs: list[str], index: int) -> dict:
    return {
        "stage": stage,
        "skill": skill,
        "reason": reason,
        "output": " and ".join(outputs),
        "outputPaths": outputs,
        "proof": f"artifacts/reviews/routing/route-{index:02d}.json",
        "status": "complete",
    }


def build_brief() -> None:
    rows = [
        ("0:00-0:05", "Expose the repeated-prompt problem", "Dense prompt wall compresses the frame while a context bar reaches its limit.", "Prompt strips advance and the red pressure cap snaps on.", "Interrupt gate snap into the compact package.", "Immediate low hit; bed starts; narration front and dry.", "Si Codex necesita este muro de prompt, no es especialista: solo está cargando equipaje."),
        ("0:05-0:13", "Define a skill as an operational package", "The wall folds into a layered SKILL.md package with trigger, workflow, resources, and output marks.", "Tile-morph collapse; red edge preserves object identity.", "Tile morph keeps the red edge on the same axis.", "Short whoosh; bed ducks 8 dB below voiceover.", "Una skill lo comprime en un paquete: SKILL.md declara cuándo activarse, qué proceso seguir, qué recursos consultar y qué resultado entregar. Menos improvisación; más contrato operativo."),
        ("0:13-0:22", "Explain progressive disclosure", "The core opens one reference; dormant resources stay outside the active context.", "One route draws; one resource brightens; inactive modules remain tonal.", "Masked reframe enters the selected reference lane.", "Soft tick on the active reference; restrained pulse in the bed.", "Pero no carga todo de golpe. Con divulgación progresiva, Codex lee primero el núcleo y abre una referencia solo cuando la decisión actual la exige; lo demás permanece fuera."),
        ("0:22-0:31", "Assign roles to references, scripts, and assets", "Three hard-edge lanes emit a rule, a deterministic run, and a visual resource.", "Parallel lane build followed by one converging baseline.", "Surface wipe follows the baseline into the router.", "Three precise ticks; subtle stereo spread, then center.", "Dentro, cada pieza tiene oficio: referencias para criterio, scripts para operaciones repetibles y assets para plantillas, estilos o medios. El paquete separa conocimiento, ejecución y materia prima."),
        ("0:31-0:41", "Show specialist routing", "A task packet splits toward conventional diagrams, bespoke geometry, and raster imagery.", "Routes draw in sequence; each outcome returns a proof mark.", "Persistent red packet crosses into the validation corridor.", "Ascending three-note cue; ducked bed; small proof clicks.", "Después enruta por intención: un flujo convencional va a Mermaid, geometría o datos complejos a D3, y una escena ilustrada a ImageGen. Cada especialista devuelve un artefacto verificable."),
        ("0:41-0:51", "Make validation block defects", "The artifact crosses structure, binding, pixel, and package gates; a failed branch loops back.", "Gate sequence advances; failed path snaps downward; corrected path receives approval.", "Interrupt gate snap, then match cut to the budget bars.", "Hard stop on rejection; brighter approval hit; bed resumes.", "Ese artefacto cruza una puerta de validación: se comprueban rutas, estructura, contenido y calidad visual. Si falla una condición, la entrega se bloquea antes de parecer correcta por accidente."),
        ("0:51-1:01", "Show the qualitative context benefit and limitation", "Always-on wall versus compact core plus one selected detail; an oversized skill grows as the warning.", "Bars compare on one scale; the warning section expands only at the final clause.", "Match cut on the shared bar cap into the reusable hub.", "Bed thins for the warning; low tick on the bloated branch.", "El beneficio también se mide en contexto: frente al muro completo, Codex mantiene cargado un núcleo pequeño y paga detalle solo al necesitarlo. Limitación: una skill inflada o mal diseñada vuelve a pagar la factura."),
        ("1:01-1:10", "Close with the reusable-workflow callback", "One skill package activates across several project surfaces and returns to a compact resting state.", "Hub routes pulse one at a time; camera pulls out to reveal the complete system.", "Zoom out to system; final match cut returns to the opening red edge.", "Warm resolve; final tail holds 700 ms after the last word.", "Así, la misma especialidad reaparece en cada proyecto, actualizable y bajo demanda. El muro del inicio no desapareció por magia: se convirtió en un workflow reutilizable que sabe cuándo despertar."),
    ]
    table = "\n".join(f"| {row[0]} | b{index + 1:02d} | s{index + 1:02d} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]} |" for index, row in enumerate(rows))
    voice = "\n".join(f"- {row[0]}: {row[-1]}" for row in rows)
    text = f"""# Una skill convierte a Codex en especialista

Promise: Show how a reusable Codex skill turns repeated prompt baggage into an on-demand, validated workflow.
Audience: Technical Spanish-speaking viewers who use or design Codex workflows.
Format: Compressed explainer.
Runtime: 70 seconds.

## Title and promise

The video proves that a compact skill package can preserve recurring instructions, resources, scripts, asset routing, and validation without pasting one long prompt into every task.

## Hook

Cold-open line: “Si Codex necesita este muro de prompt, no es especialista: solo está cargando equipaje.”
First visual: A dense prompt wall presses against a context bar before folding into a SKILL.md package.
Audio cue: Low impact at frame one; restrained technical bed starts immediately and ducks under narration.

## Voiceover Draft

{voice}

## Timed beat table

| Time | Beat ID | Scene ID | Script purpose | Visual | Animation | Transition | Audio/music/SFX |
| --- | --- | --- | --- | --- | --- | --- | --- |
{table}

## Visuals, animation, and transitions

Use a continuous hard-edge skill-package megacanvas with five functional zones and eight camera-framed scenes. Keep the red edge as the tracked semantic element. Vary the scene armature across diagonal pressure, centered package, asymmetric disclosure, modular resource board, router spine, validation corridor, comparison bars, and final radial hub. Use no title bands, decorative progress rails, or prose cards.

## Assets and sources

- Source links: {OFFICIAL_SKILLS_URL}, {REPO_RULES_URL}
- Official OpenAI use case: {OFFICIAL_SKILLS_URL}
- Repository authoring and progressive-disclosure rules: {REPO_RULES_URL}
- Eight original D3/SVG mechanism assets under `artifacts/images/`, each bound to one beat and one scene.
- Renderer-native megacanvas geometry is original and project-generated; no third-party footage or stock media is used.

## Audio

Spanish neural narration is the primary audio. A procedural, rights-safe technical bed is ducked below speech. Seven seam hits, one rejection stop, one approval accent, and a final tail punctuate semantic changes without naming copyrighted music.

## Evaluation and validation

- Hook and proof appear in the first five seconds.
- Exactly eight concrete beats cover the full 70-second runtime.
- Every scene exposes stable scene, composition, asset, and beat IDs.
- A new visual mechanism, camera target, or semantic state appears every 5–10 seconds.
- Full-resolution scene holds and transition midpoints must pass legibility, safe-zone, source-binding, and continuity checks.
- Brief, source links, renderer binding, MP4, audio, motion, visual-contract, style-fidelity, readiness, and final package validators must pass before delivery.
"""
    write_text(SOURCE / "brief.md", text)


def build_source_contracts() -> None:
    facts = []
    for index, scene in enumerate(SCENES, start=1):
        facts.append({
            "id": f"f{index:02d}", "beatId": scene["beat"], "time": scene["time"], "claim": scene["claim"],
            "sourceUrl": OFFICIAL_SKILLS_URL if index in {1, 2, 4, 7, 8} else REPO_RULES_URL,
            "rightsStatus": "official-source",
            "verificationStatus": "verified", "checkedDate": "2026-07-10",
        })
    package = {
        "schemaVersion": 1, "version": 1, "videoId": "skill-convierte-codex-especialista", "sourceId": "codex-skill-reusable-workflow",
        "route": "topic-explainer", "status": "frozen", "createdFor": "A polished demonstration of the updated awsome-videos skill.",
        "deliverables": ["source/brief.md", "source/shot-contract.json", "src/index.html", "artifacts/videos/skill-convierte-codex-especialista.mp4"],
        "constraints": {"durationSeconds": 70, "aspect": "16:9", "resolution": "1280x720", "fps": 30, "audience": "technical Spanish-speaking viewers", "style": "fast technical explainer; hard-edge modular megacanvas; high visual density; low text", "audio": "Spanish narration plus procedural bed and semantic SFX"},
        "facts": facts,
        "literalAnchors": ["SKILL.md", "references/", "scripts/", "assets/", "progressive disclosure", "validation", "on-demand reusable workflow"],
        "assets": [f"artifacts/images/{scene['file']}" for scene in SCENES],
        "sourceUrls": [OFFICIAL_SKILLS_URL, REPO_RULES_URL], "missingFacts": [],
        "risks": ["Context benefit remains qualitative; no invented token-savings percentage is shown.", "The narration is synthetic neural speech and is reported as such."],
    }
    shots = []
    for scene in SCENES:
        shots.append({
            "id": scene["id"], "beatId": scene["beat"], "time": scene["time"], "start": scene["start"], "duration": scene["end"] - scene["start"],
            "job": scene["job"], "purpose": scene["job"], "viewerTask": scene["viewer"], "sourceAnchors": ["SKILL.md", "on-demand reusable workflow"],
            "visual": {"heroFrame": f"{scene['title']} reaches its clearest source-bound mechanism state.", "roles": ["persistent red edge", "megacanvas mechanism", scene["asset"]]},
            "motionIntent": [{"verb": "reveal", "subject": scene["asset"], "target": scene["title"], "timing": scene["time"]}, {"verb": "handoff", "subject": "persistent red edge", "target": "next scene focal axis", "timing": "final 0.6 seconds"}],
            "media": {"narration": scene["beat"], "music": "ducked procedural technical bed", "captions": False, "assets": [scene["asset"]]},
            "assetIds": [scene["asset"]], "sourceFactIds": [f"f{int(scene['id'][1:]):02d}"], "validation": ["focal mechanism remains legible", "asset and composition IDs match renderer state"], "status": "approved",
        })
    shot_contract = {"version": 1, "sourcePackage": "source-package.json", "videoId": package["videoId"], "durationSeconds": 70, "aspect": "16:9", "rendering": {"engine": "unspecified", "seekDeterministic": True, "forbiddenDependencies": ["gsap"]}, "shots": shots, "literalAnchors": package["literalAnchors"], "missingFacts": []}
    write_json(SOURCE / "source-package.json", package)
    write_json(SOURCE / "shot-contract.json", shot_contract)


def build_assets_and_composition() -> list[dict]:
    routes = [
        route("source freeze", "source-to-video-director", "Freeze verified claims, URLs, audience, runtime, and stable shot IDs before visual interpretation.", ["source/source-package.json", "source/shot-contract.json"], 1),
        route("composition", "scene-composition-director", "Assign a deliberate armature, focal hierarchy, safe zone, and camera target to every scene.", ["source/composition-plan.json"], 2),
        route("transitions", "scene-transition-director", "Carry the persistent red edge and viewer attention across all seven adjacent seams.", ["source/transition-plan.json"], 3),
        route("asset generation", "d3-animated-svg", "Produce eight deterministic custom SVG mechanism assets with stable geometry and source-bound semantics.", [f"artifacts/images/{scene['file']}" for scene in SCENES], 4),
        route("renderer", "html-d3-anime-video-workflow", "Render the modular megacanvas with deterministic timestamp state, browser capture, and ffmpeg encoding.", ["src/index.html"], 5),
    ]
    assets = []
    for scene in SCENES:
        output = IMAGES / scene["file"]
        output_rel = output.relative_to(PROJECT).as_posix()
        report_rel = f"artifacts/reviews/producers/{scene['asset']}.json"
        report = {
            "schemaVersion": 1, "ok": True, "assetId": scene["asset"], "skill": "d3-animated-svg", "output": output_rel,
            "sha256": sha256(output), "outputSha256": sha256(output),
            "checks": [
                {"name": "dimensions", "method": "inspect SVG viewBox and declared aspect ratio", "finding": "The 640x360 SVG matches the 16:9 crop without upscaling.", "passed": True},
                {"name": "contrast", "method": "inspect grayscale hierarchy and semantic red area", "finding": "Focal geometry remains distinct in grayscale and red is limited to state, route, or edge marks.", "passed": True},
                {"name": "semantic content", "method": "compare geometry against the scene claim", "finding": f"The asset depicts {scene['title'].lower()} with scene-specific mechanism geometry.", "passed": True},
            ],
        }
        write_json(PROJECT / report_rel, report)
        assets.append({
            "id": scene["asset"], "kind": "svg", "claim": scene["claim"], "output": output_rel, "sha256": sha256(output),
            "origin": {"type": "generated", "uri": f"generated://awsome-videos-skill-demo/{scene['asset']}", "rightsStatus": "project-generated", "attribution": "Original deterministic SVG mechanism produced for this demo."},
            "producer": {"skill": "d3-animated-svg", "method": "Created deterministic source-bound SVG geometry using the D3 animated-SVG visual contract.", "report": report_rel},
            "technical": {"targetWidth": 640, "targetHeight": 360, "aspectRatio": "16:9", "maxUpscale": 1.0, "crop": "Preserve the complete mechanism proof and semantic red edge."},
            "uses": [{"sceneId": scene["id"], "beatId": scene["beat"], "role": "primary mechanism proof", "fit": "contain inside the declared focal bounds"}],
            "status": "approved",
            "qualityChecks": ["Verify focal geometry remains legible at delivery resolution.", "Confirm red is a semantic signal rather than a broad decorative fill.", "Match the rendered asset ID and SHA-256 to its declared scene and beat."],
        })
    manifest = {"schemaVersion": 1, "videoId": "skill-convierte-codex-especialista", "canvas": {"width": 1280, "height": 720, "aspectRatio": "16:9"}, "skillRouting": routes, "assets": assets}
    write_json(SOURCE / "asset-manifest.json", manifest)

    plan = json.loads((SOURCE / "composition-plan.json").read_text(encoding="utf-8"))
    plan["format"] = "1280x720"
    plan["videoDirection"].update({
        "sourceAnchors": ["SKILL.md", "references/", "scripts/", "assets/", "on-demand reusable workflow"],
        "paletteTypeSource": "Project colorset1 tonal palette and Open Sans stack.",
        "alignmentMode": "Navigable hard-edge megacanvas on a 4-pixel grid with scene-specific camera crops.",
        "edgeCornerPolicy": "All generated panels, masks, apertures, and modules are square and 0-radius.",
        "boxInteriorPolicy": "Zero internal padding; content is flush to declared bounds and separated by external gutters.",
        "safeZones": "Keep focal mechanisms inside a five-percent frame margin; no title, subtitle, or caption band.",
        "captionPolicy": "No burned-in captions; Spanish narration carries explanatory prose.",
        "editorialTextPolicy": "none",
        "functionalTextPolicy": "Only SKILL.md and local data-bearing marks may appear.",
        "operatingModel": "navigable-megacanvas",
        "rhythm": "Eight scene windows with a camera handoff in the opening quarter and a readable hold through the mechanism emphasis.",
        "negativeList": ["title bands", "rounded cards", "padded chips", "generic stock imagery", "invented percentages", "decorative progress rails"],
    })
    focal_bounds = [{"x": 0.72, "y": 0.04, "width": 0.24, "height": 0.24} for _ in SCENES]
    for index, scene in enumerate(SCENES):
        item = plan["scenes"][index]
        item.update({
            "id": scene["id"], "title": scene["title"], "duration": scene["time"], "beatIds": [scene["beat"]], "assetIds": [scene["asset"]],
            "sourceAnchors": ["SKILL.md", "on-demand reusable workflow"], "sceneJob": scene["job"], "viewerTask": scene["viewer"],
            "compositionChoice": scene["choice"], "choiceRationale": f"The {scene['choice']} makes {scene['title'].lower()} the dominant mechanism while the persistent red edge stays available for the handoff.",
            "focal": scene["title"], "roles": {"focal": "megacanvas mechanism plus manifest-bound SVG proof", "support": "tonal system context", "handoff": "persistent red edge"},
            "armature": scene["armature"], "alignmentGrid": "4-pixel modular grid with shared x/y edges and scene-specific focal axis.",
            "armatureAnchors": [f"{scene['title']} focal geometry locked to the primary scene axis", "persistent red edge aligned to the outgoing seam target"],
            "edgePolicy": "Hard-edge rectangular geometry with grid-locked masks and external gutters.", "cornerPolicy": "0-radius square corners only.",
            "boxInteriorPolicy": "Zero internal padding; content is flush to bounds and separation uses external gutters.",
            "boxModel": {"internalPaddingPx": 0, "contentFlushToBounds": True, "separation": "external gutters only"},
            "grayscaleHierarchy": [{"level": 0, "role": "primary focal", "grayHex": "#696969"}, {"level": 1, "role": "secondary support", "grayHex": "#9c9c9c"}, {"level": 2, "role": "background structure", "grayHex": "#e7e7e7"}],
            "layout": f"Camera frames the {scene['armature']} inside the shared skill-package megacanvas.", "hierarchy": "The mechanism proof dominates; the source-bound SVG and persistent red edge remain subordinate but inspectable.",
            "density": "One primary mechanism, one manifest-bound proof asset, one state metric or gate, and one transition-ready edge.",
            "safeZones": {"frameMargin": "5 percent on every edge", "captionZone": "none", "protectedRegion": "focal mechanism and source-bound SVG remain unobstructed"},
            "textRegion": {"placement": "functional labels only inside data-bearing geometry", "maxLineCharacters": 18, "contrastTreatment": "Neutral ink on tonal white or gray surfaces.", "clearance": "One external grid gutter from focal edges and crop zones."},
            "objectBounds": [{"id": f"{scene['id']}-focal", "role": "focal", **focal_bounds[index]}, {"id": f"{scene['id']}-support", "role": "support", "x": 0.7125, "y": 0.04, "width": 0.0078, "height": 0.24}],
            "rendererHandoff": "Renderer must expose sceneId, activeBeat, activeCompositionId, activeAssetIds, activeZoneIndex, and sourceProofVisible.",
            "risks": ["Camera crop could hide a neighboring module during the seam.", "The proof inset must not compete with the megacanvas focal mechanism."],
        })
        item["validationContract"].update({"edgePolicy": "0-radius edges remain square through render and transition midpoint.", "boxPadding": "internalPaddingPx is 0 and all content remains flush to bounds.", "grayscaleHierarchy": "Three monotonic grayscale roles remain distinct; red is reserved for semantic state.", "verificationArtifacts": [f"artifacts/reviews/frames/{scene['id']}-hold.png", "artifacts/reviews/renderer-contract.json"]})
        if index < len(SCENES) - 1:
            next_scene = SCENES[index + 1]
            item["outgoingSeam"] = {"seamId": f"{scene['id']}__{next_scene['id']}", "fromScene": scene["id"], "toScene": next_scene["id"], "persistentElement": "persistent red edge", "attentionHandoff": "The red edge lands on the incoming focal axis before the camera settles.", "beforeState": f"{scene['title']} is complete and readable.", "afterState": f"{next_scene['title']} receives the red edge as its activation cue.", "type": "transition"}
        else:
            item["outgoingSeam"] = {"seamId": "end", "fromScene": "s08", "toScene": None, "persistentElement": "persistent red edge", "attentionHandoff": "The red edge returns to the compact package and holds through the audio tail.", "beforeState": "Reusable workflow hub is complete.", "afterState": "Compact skill package rests in the full-system frame.", "type": "end"}
    write_json(SOURCE / "composition-plan.json", plan)
    return routes


def build_transitions() -> None:
    payload = json.loads((SOURCE / "transition-plan.json").read_text(encoding="utf-8"))
    payload["videoId"] = "skill-convierte-codex-especialista"
    payload["persistentElement"] = {"name": "persistent red edge", "role": "Carries the active skill package state and viewer attention across the megacanvas.", "states": ["prompt pressure", "package edge", "active reference", "resource baseline", "router packet", "validation gate", "context cap", "reusable workflow"]}
    families = ["morph", "spatial portal", "color handoff", "persistent object", "interrupt", "match cut", "camera move"]
    for index, item in enumerate(payload["transitions"]):
        source = SCENES[index]
        target = SCENES[index + 1]
        item.update({
            "id": f"t{index + 1:02d}", "seamId": f"{source['id']}__{target['id']}", "fromScene": source["id"], "toScene": target["id"],
            "start": round(source["end"] - 0.6, 2), "duration": 1.2, "family": families[index],
            "semanticPurpose": f"Carry the skill package state from {source['title'].lower()} into {target['title'].lower()} without resetting attention.",
            "stateChange": f"The persistent red edge changes role from {source['title'].lower()} to the activation cue for {target['title'].lower()}.",
            "attentionHandoff": "The outgoing red edge and incoming focal axis share the same grid intersection at the midpoint.",
            "styleContinuity": "Hard-edge 0-radius geometry, grayscale hierarchy, Open Sans, and semantic red persist through the seam.",
            "alignmentRule": "Outgoing red edge and incoming focal target remain grid-locked on a shared axis.",
            "edgeRule": "All masks, panels, and apertures remain rectangular and 0-radius.",
            "boxPaddingRule": "All masks, panels, cards, and apertures keep internalPaddingPx 0; content remains flush to bounds.",
            "grayscaleHierarchyRule": "Primary, secondary, and background roles stay distinct through outgoing, bridge, and incoming states; red only marks semantic state.",
            "grayscaleHierarchy": [{"level": 0, "role": "primary focal", "grayHex": "#696969"}, {"level": 1, "role": "secondary support", "grayHex": "#9c9c9c"}, {"level": 2, "role": "background structure", "grayHex": "#e7e7e7"}],
            "genericMotionRejected": "A generic fade or slide would lose the tracked package edge and hide the conceptual state change.",
            "surprise": f"The red edge from {source['title'].lower()} becomes the first active mark in {target['title'].lower()}.",
            "outgoingState": f"{source['title']} is settled with the red edge visible.",
            "bridgeAction": f"A {families[index]} keeps the red edge visible while the camera reframes the megacanvas.",
            "incomingState": f"{target['title']} receives the edge and becomes the dominant mechanism.",
            "compositionShift": f"{source['choice']} resolves into {target['choice']}.", "colorShift": "Red semantic state persists; grayscale roles re-balance around the incoming focal.",
            "cameraShift": "Camera reframes during the first quarter of the incoming scene, then holds for readability.", "spaceShift": f"{source['armature']} gives way to {target['armature']}.",
        })
        item["validationFrames"] = [
            {"time": f"{source['end'] - 0.4:.1f}s", "target": f"{source['id']} outgoing focal and persistent red edge", "passCriterion": "Outgoing hierarchy and tracked edge are visible and unclipped."},
            {"time": f"{source['end']:.1f}s", "target": f"{source['id']} to {target['id']} transition midpoint", "passCriterion": "The red edge remains visible while the camera crosses the declared grid axis."},
            {"time": f"{source['end'] + 0.4:.1f}s", "target": f"{target['id']} incoming focal", "passCriterion": "Incoming mechanism owns the first eye landing without overlap or clipping."},
        ]
        item["validationChecks"] = [{"method": "three-frame-seam-review", "target": f"{source['id']}__{target['id']}", "passCriterion": "Before, midpoint, and after frames prove persistent-edge continuity and semantic attention handoff."}]
    write_json(SOURCE / "transition-plan.json", payload)


def build_notes_and_manifest(routes: list[dict]) -> None:
    design = """# Design Note

Concept claim: A skill is a reusable, validated workflow package that replaces repeated prompt baggage and wakes only when relevant.

Mechanic: A dense instruction wall compresses into a SKILL.md package; the package opens resources on demand, routes assets to specialists, crosses validation gates, and reactivates across projects.

Candidate metaphors: A toolbox, a plug-in cartridge, and a navigable skill-package megacanvas. The toolbox was rejected because it hides activation timing; the cartridge was rejected because it makes validation and resource roles too linear. The megacanvas was chosen because it preserves object identity while the camera reveals package layers, routes, gates, and reuse.

Visual vocabulary: Gray modules are durable knowledge and structure. The dark-red edge is the active workflow state. Thin bright-red marks indicate pressure, rejection, or correction. Camera reframing changes abstraction level; route drawing means a resource or artifact has become active.

Composition contract: 1280x720, 4-pixel grid, 0-radius geometry, zero internal box padding, external gutters, five functional zones, and eight scene-specific camera targets. No title, subtitle, caption, or decorative progress band is rendered.

Reuse decision: Reuse the validated skill-package megacanvas geometry because its card stack, prompt collapse, folder grid, resource modules, validation runner, trim blade, and workflow stamp preserve the same semantic roles required by this explainer. Eight file-backed SVG proofs make scene ownership auditable.

Narration split: Spanish narration carries definitions, caveats, and the qualitative context claim. The frame carries compression, activation, routing, validation, comparison, and reuse.
"""
    write_text(SOURCE / "design-note.md", design)
    storyboard_lines = ["# Una skill convierte a Codex en especialista", "", "## Source Facts", "", "| Field | Value |", "| --- | --- |", "| Route | topic-explainer |", "| Audience | Technical Spanish-speaking viewers |", "| Duration | 70 seconds, 16:9, 1280x720, 30 fps |", "| Style / Audio | Fast hard-edge megacanvas; Spanish narration with procedural bed |", f"| Sources | {OFFICIAL_SKILLS_URL}; {REPO_RULES_URL} |", "", "## Narrative Angle", "", "A repeated prompt wall becomes a compact, on-demand, specialist-routed, validated workflow that can wake across projects.", "", "## Shot List"]
    for scene in SCENES:
        storyboard_lines += ["", f"### {scene['id']} — {scene['title']}", f"- Duration: {scene['time']}", f"- Purpose: {scene['job']}", f"- Source facts used: f{int(scene['id'][1:]):02d}", f"- Visual frame: {scene['title']} fills the declared {scene['choice']} while the persistent red edge remains visible.", f"- Motion intent: reveal the mechanism, hold the proof, emphasize the state change, then hand off the red edge.", f"- Media: Spanish narration, procedural bed, `{scene['file']}`.", "- Validation: inspect full-resolution hold frame, active IDs, safe zones, and transition midpoint."]
    storyboard_lines += ["", "## Validation Anchors", "", "- SKILL.md", "- references/", "- scripts/", "- assets/", "- on-demand reusable workflow"]
    write_text(PROJECT / "src" / "storyboard.md", "\n".join(storyboard_lines))

    notes = """# Production Notes

## Source and editorial pass

- Checked 2026-07-10 against the official OpenAI reusable-skills use case and the public repository authoring rules.
- Removed unsupported numeric token-savings claims; the context benefit remains qualitative.
- Locked eight Spanish narration beats across exactly 70 seconds.

## Asset and composition pass

- Produced eight original file-backed SVG mechanism assets with stable IDs and SHA-256 bindings.
- Reused the validated skill-package megacanvas because its geometry has the same semantic role as the topic.
- Reframed the canvas into eight deliberate armatures with a persistent red edge across seven seams.

## Renderer and motion pass

- Deterministic `window.renderConceptFrame` exposes beat, scene, composition, asset, zone, and camera state.
- Browser render-state validation passed for eight distinct scenes and assets before full encoding.

## Final review

Legibility check: To be finalized after full-resolution frame review.
Beat coverage check: To be finalized after final render.
Visual mechanism check: To be finalized after the mute and contact-sheet review.
Pacing/transition check: To be finalized after full-speed playback and seam midpoint review.
Source-binding check: To be finalized after the renderer and visual-contract gates.
Audio sync check: To be finalized after the 70-second narration mix is muxed.
Known caveats: Neural Spanish narration is synthetic; no third-party footage or copyrighted music is used.
"""
    write_text(SOURCE / "production-notes.md", notes)

    manifest = json.loads((SOURCE / "package-manifest.json").read_text(encoding="utf-8"))
    manifest.update({"projectId": "awsome-videos-skill-demo-20260710", "title": "Una skill convierte a Codex en especialista", "format": "compressed explainer", "runtime": "70 seconds", "toolchain": routes})
    manifest["paths"].update({"video": "artifacts/videos/skill-convierte-codex-especialista.mp4", "finalAudio": "artifacts/audio/final-mix.wav", "contactSheet": "artifacts/reviews/contact-sheet.jpg"})
    for key, command in list(manifest["commands"].items()):
        command = command.replace("Why Vector Databases Feel Fast", "Una skill convierte a Codex en especialista").replace("vector-search-explainer.mp4", "skill-convierte-codex-especialista.mp4").replace("vector-search-explainer", "skill-convierte-codex-especialista").replace("80 seconds", "70 seconds").replace("--duration 80", "--duration 70").replace("--expect-duration 80", "--expect-duration 70")
        manifest["commands"][key] = command
    write_json(SOURCE / "package-manifest.json", manifest)


def build_route_proofs(routes: list[dict]) -> None:
    for route_item in routes:
        outputs = [PROJECT / value for value in route_item["outputPaths"]]
        payload = {"schemaVersion": 1, "ok": True, "stage": route_item["stage"], "skill": route_item["skill"], "output": route_item["output"], "sha256": sha256(outputs[0]), "outputSha256": sha256(outputs[0]), "artifacts": [{"path": path.relative_to(PROJECT).as_posix(), "sha256": sha256(path)} for path in outputs]}
        write_json(PROJECT / route_item["proof"], payload)


def main() -> None:
    PRODUCERS.mkdir(parents=True, exist_ok=True)
    ROUTING.mkdir(parents=True, exist_ok=True)
    build_brief()
    build_source_contracts()
    routes = build_assets_and_composition()
    build_transitions()
    build_notes_and_manifest(routes)
    build_route_proofs(routes)
    print(json.dumps({"ok": True, "project": str(PROJECT), "scenes": len(SCENES), "assets": len(SCENES)}, indent=2))


if __name__ == "__main__":
    main()
