#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Package canonical runtime skills; never edit or install global host settings."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
REPO = PROJECT.parent.parent


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def main():
    spec = json.loads((PROJECT / "package-spec.json").read_text())
    manifest = json.loads((PROJECT / "plugin.json").read_text())
    packages = PROJECT / "artifacts/packages"
    packages.mkdir(parents=True, exist_ok=True)
    bundle = packages / f'{spec["name"]}-{spec["version"]}'
    if bundle.exists():
        raise SystemExit("Package directory exists. Select a new version or archive the previous build explicitly.")
    plugin = bundle / "plugin"
    plugin.mkdir(parents=True)
    save(plugin / "plugin.json", manifest)
    common = {k: v for k, v in manifest.items() if k != "$schema"}
    save(plugin / ".claude-plugin/plugin.json", common)
    save(plugin / ".codex-plugin/plugin.json", {**common, "skills": "./skills/"})
    profile_root=REPO/"skills/line-world-video/assets/plugin-profiles"
    for name in spec["skills"]:
        origin=spec.get("sources",{}).get(name,name)
        source, dest = REPO / "skills" / origin, plugin / "skills" / name
        for file in sorted(source.rglob("*"), key=lambda p: p.relative_to(source).as_posix()):
            rel = file.relative_to(source)
            if not file.is_file() or any(part in {"node_modules", "__pycache__", ".venv", ".cache", "dist", "output"} for part in rel.parts) or rel.parts[:2] == ("assets", "examples") or file.suffix in {".pyc", ".pyo"}:
                continue
            if name in spec.get("profiles",{}) and rel.parts[0]=="references" and file.suffix==".md":
                continue
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
        if name in spec.get("profiles",{}):
            original=(source/"SKILL.md").read_text(encoding="utf-8")
            (dest/"references").mkdir(exist_ok=True)
            operation=name.removeprefix('line-world-')+'-operations.md.in'
            shutil.copyfile(profile_root/operation,dest/"references/producer-workflows.md")
            profile=profile_root/spec["profiles"][name]
            shutil.copyfile(profile,dest/"SKILL.md")
            shutil.copyfile(profile_root/"video-contract.md",dest/"references/video-contract.md")
            display='Line World '+{'d3':'D3','mermaid':'Mermaid','icons':'Icons','hyperframes':'HyperFrames'}[name.removeprefix('line-world-')]
            (dest/"agents").mkdir(exist_ok=True)
            (dest/"agents/openai.yaml").write_text('interface:\n  display_name: '+json.dumps(display)+'\n  short_description: '+json.dumps('Specialized producer for clean synchronized video')+'\n  default_prompt: '+json.dumps('Use $'+name+' for a clean Line World video asset with full-frame composition, shared focus, one parent clock and no unrequested titles.')+'\n',encoding="utf-8")
            patches=[]
            palette=REPO/"skills/line-world-video/assets/palettes/colorsets.json"
            (dest/"assets/palettes").mkdir(parents=True,exist_ok=True)
            shutil.copyfile(palette,dest/"assets/palettes/colorsets.json")
            video_palette=REPO/"skills/line-world-video/assets/palettes/video-colors.json"
            shutil.copyfile(video_palette,dest/"assets/palettes/video-colors.json")
            shutil.copyfile(REPO/'skills/line-world-video/assets/palettes/video-color-direction.json',dest/'assets/palettes/video-color-direction.json')
            adapted_readers=[]
            for reader in sorted((dest/'scripts').rglob('*'), key=lambda p: p.relative_to(dest).as_posix()):
                if reader.suffix not in ('.py','.ts','.js','.mjs','.cjs'):continue
                code=reader.read_text(encoding='utf-8')
                if 'colorsets.json' in code:
                    reader.write_text(code.replace('colorsets.json','video-colors.json'),encoding='utf-8')
                    adapted_readers.append(reader.relative_to(dest).as_posix())
            patches.append('Use primary red first, light/medium gray second and black last in the video palette.')
            patches.append('Route '+str(len(adapted_readers))+' copied runtime palette readers to the video style while preserving the canonical base contract.')
            motion=REPO/"skills/line-world-video/assets/runtime/attention.js"
            (dest/"assets/runtime").mkdir(parents=True,exist_ok=True)
            shutil.copyfile(motion,dest/"assets/runtime/attention.js")
            focus=REPO/"skills/line-world-video/assets/runtime/focus.js"
            shutil.copyfile(focus,dest/"assets/runtime/focus.js")
            for resource in ['theme.css','theme.js','focus-motion.js','photo-focus.js','scene-effects.js']:
                shutil.copyfile(REPO/'skills/line-world-video/assets/runtime'/resource,dest/'assets/runtime'/resource)
            patches.append('Share semantic CSS tokens and the theme runtime for project-owned style changes.')
            patches.append('Bind audio word cues to measured adjacent ports and audit label/stroke clearance.')
            patches.append('Share primary-red size choreography and semantic quantity-point motion.')
            if origin=="d3":
                shutil.copyfile(profile_root/"video_chart.py.in",dest/"scripts/video_chart.py")
                patches.append('Add the bounded video table/comparison builder and browser exporter.')
            if origin=="mermaid":
                renderer=dest/"scripts/animate_mermaid_svg.py"
                code=renderer.read_text(encoding="utf-8")
                call='                native_solid_presentation(root, colorset)'
                import_line='from mermaid_animation.solid import native_solid_presentation, write_native_svg'
                if code.count(call)!=1 or code.count(import_line)!=1:raise RuntimeError('Mermaid source changed: review the video finish patch.')
                code=code.replace(import_line,'from mermaid_animation.solid import write_native_svg\nfrom video_style import native_video_presentation')
                code=code.replace(call,'                native_video_presentation(root, colorset)')
                renderer.write_text(code,encoding="utf-8")
                shutil.copyfile(profile_root/"video_style.py",dest/"scripts/video_style.py")
                patches.append('Replace CS1 standalone solid finish with native_video_presentation.')
            save(dest/"video-profile.json",{"name":name,"sourceSkill":origin,"sourceInstructionSha256":hashlib.sha256(original.encode()).hexdigest(),"profileSha256":hashlib.sha256(profile.read_bytes()).hexdigest(),"sharedContractSha256":hashlib.sha256((profile_root/"video-contract.md").read_bytes()).hexdigest(),"attentionRuntimeSha256":hashlib.sha256(motion.read_bytes()).hexdigest(),"focusRuntimeSha256":hashlib.sha256(focus.read_bytes()).hexdigest(),"paletteSha256":hashlib.sha256(palette.read_bytes()).hexdigest(),"videoPaletteSha256":hashlib.sha256(video_palette.read_bytes()).hexdigest(),"adaptedPaletteReaders":adapted_readers,"patches":patches})
    catalog = {"name": "line-world-local", "interface": {"displayName": "Line World Video"}, "plugins": [{"name": "line-world-video", "source": {"source": "local", "path": "./plugin"}, "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Creativity"}]}
    save(bundle / ".agents/plugins/marketplace.json", catalog)
    save(bundle / ".claude-plugin/marketplace.json", {"name": "line-world-local", "owner": {"name": "Line World"}, "plugins": [{"name": "line-world-video", "source": "./plugin", "description": manifest["description"]}]})
    save(bundle / "package.json", {"name": "line-world-video", "version": spec["version"], "private": True, "keywords": ["pi-package"], "pi": {"skills": ["./plugin/skills"], "extensions": [], "prompts": [], "themes": []}})
    files = [{"path": p.relative_to(plugin).as_posix(), "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(plugin.rglob("*"), key=lambda p: p.relative_to(plugin).as_posix()) if p.is_file()]
    save(plugin / "bundle-manifest.json", {"name": spec["name"], "version": spec["version"], "skills": spec["skills"], "files": files})
    plugin_zip = packages / f'{spec["name"]}-{spec["version"]}.zip'
    market_zip = packages / f'{spec["name"]}-{spec["version"]}-marketplace.zip'
    for root, output in ((plugin, plugin_zip), (bundle, market_zip)):
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(root.rglob("*"), key=lambda p: p.relative_to(root).as_posix()):
                if file.is_file():
                    info = zipfile.ZipInfo(file.relative_to(root).as_posix(), date_time=(2026, 11, 14, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    archive.writestr(info, file.read_bytes())
    extracted = packages / f'{spec["name"]}-{spec["version"]}-extracted'
    extracted.mkdir()
    with zipfile.ZipFile(plugin_zip) as archive:
        archive.extractall(extracted)
    for record in files:
        if hashlib.sha256((extracted / record["path"]).read_bytes()).hexdigest() != record["sha256"]:
            raise RuntimeError("Extracted payload digest mismatch: " + record["path"])
    run = subprocess.run(["uv", "run", "--script", str(extracted / "skills/line-world-video/scripts/line_world.py"), "init", "--project", str(PROJECT / "artifacts" / ("package-smoke-" + spec["version"]))], capture_output=True, text=True)
    report = {"ok": run.returncode == 0, "skills": spec["skills"], "fileCount": len(files), "payloadBytes": sum(f["bytes"] for f in files), "pluginZip": str(plugin_zip), "marketplaceZip": str(market_zip), "archiveSha256": hashlib.sha256(plugin_zip.read_bytes()).hexdigest(), "cleanExtractedSmoke": {"exitCode": run.returncode, "stdout": run.stdout, "stderr": run.stderr}}
    save(packages / "package-check.json", report)
    save(packages / ("package-check-" + spec["version"] + ".json"), report)
    print(json.dumps({"ok": report["ok"], "pluginZip": str(plugin_zip), "marketplaceRoot": str(bundle), "fileCount": len(files)}))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
