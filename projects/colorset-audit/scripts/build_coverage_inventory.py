#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Enumerate supported output routes and reproducible palette artifact gates."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[3]
OUTPUTS = {
    "ambientcg-material-search": ["HTML candidate previews", "JSON search/download receipts", "original ZIP/JPG/PNG material assets"],
    "animated-svg-to-gif": ["authored SVG pulse template", "single/batch browser-captured GIF", "conversion JSON manifests"],
    "asciinema-real-command-video": ["plan/preflight JSON", "original v2/v3 cast evidence", "colorset presentation cast", "agg GIF", "H.264 MP4", "bundle manifests/index"],
    "compose-synchronized-svg": ["scaffold SVG", "compiled synchronized SVG", "multi-module camera SVG", "audit/validation JSON", "published HTML/SVG gallery"],
    "d3": ["22 named HTML/SVG/PNG builders", "custom authored charts/networks/maps/simulations", "static/animated self-contained SVG", "logo/texture SVG", "composition SVG", "base/cs1/cs2 galleries"],
    "destockd-video-search": ["HTML shot previews", "JSON shot/source receipts", "original selected MP4"],
    "diagram-composition": ["native compound SVG", "HTML/SVG/PNG composition preview", "grid/icon/connection audit JSON"],
    "echarts-animated-svg": ["SVGRenderer/SSR static chart SVG", "postprocessed animated SVG", "HTML replay gallery", "chart template SVG"],
    "google-cloud-sku-pricing": ["JSON SKU prices", "CSV/TSV price tables", "offline Parquet catalog", "SQL queries", "Markdown comparison tables"],
    "harbor-author-evaluation-datasets": ["dataset task/config/verifier files", "sanitized JSON/Markdown aggregates", "quality-comparison.svg", "resource-comparison.svg", "efficiency-frontier.svg"],
    "hierarchy-lens": ["organic/compact/radial static SVG", "decision replay canvas", "offline interactive HTML", "lens legends and data exports"],
    "hyperframes-explainer": ["composition brief/plan JSON", "HTML/SVG mechanism and readouts", "source asset imports", "HyperFrames MP4", "contact sheets and browser audit JSON"],
    "iconify-icon-search": ["HTML candidate previews", "single-color/currentColor SVG", "original multicolor SVG", "JSON receipts/license metadata"],
    "jev-batch-decisions": ["JSON batch/shard/reducer outputs", "CSV decisions", "Markdown provenance summaries"],
    "kenney-asset-search": ["HTML pack previews", "JSON receipts", "original selected ZIP and extracted sprites/models"],
    "manim-svg-video": ["SVG sequencing/import", "Manim MP4", "authored frame/background/caption", "ffprobe/validation JSON"],
    "mermaid": ["styled Mermaid files/Markdown fences", "31-family static SVG", "31-family animated SVG", "rendered PNG/browser previews", "paired cs1/cs2 HTML galleries"],
    "one-bit-dither-svg": ["original/custom/regional rectangle SVG", "PNG preview", "declarative CSS/SMIL SVG to GIF", "GIF/WebP/APNG source to GIF", "contact sheets and JSON reports"],
    "pexels-media-search": ["HTML media previews", "JSON receipts", "original selected photo/video rendition"],
    "pixel-art-image-video": ["PNG/lossless WebP", "GIF/MP4/FFV1 MKV", "fixed/adaptive/custom reduced colorset modes", "explicit exact-RGB preserve mode", "contact sheets and JSON reports"],
    "plantuml-colorset-renderer": ["themed PlantUML sources", "SVG/PNG via local/server/Kroki", "ditaa raster-only diagrams", "coverage/render reports", "unified HTML theme gallery"],
    "polyhaven-asset-search": ["HTML asset previews", "JSON receipts", "original textures/HDRIs/glTF/models and dependencies"],
    "procedural-svg-animation": ["66 pattern families × full/reduced SVG", "standalone custom animated SVG", "HTML catalog/gallery", "audit/verification JSON"],
    "repository-reviewer-creator": ["generated reviewer SKILL.md/YAML/references", "repository profile JSON", "Markdown review findings", "structural validation JSON"],
    "simulation-data-lab": ["model/config/variable review", "simulation CSV/Parquet/JSON tables", "SQL exploration", "Markdown analysis", "integrity reports"],
    "slidev-animejs": ["Vue animation components", "six SVG runtime asset packs", "Slidev HTML deck", "click-state animations and recording source"],
    "slidev-echarts": ["Vue Canvas/SVG chart components", "dedicated chart-type references", "Slidev HTML deck", "static/animated chart exports"],
    "slidev-quality-audit": ["read-only DOM/SVG/canvas color audit", "desktop/mobile slide screenshots", "Markdown/JSON audit reports"],
    "svg-brief-design": ["editable illustration/ornament/emblem/diagram SVG", "nested detail/scaffold paints", "preview PNG", "audit JSON"],
    "technical-logo-assets": ["exact original-color SVG", "licensed grayscale/black/white/adaptive variants", "baked monochrome colorset SVG", "provenance/license sidecars"],
    "threejs-animated-3d": ["24 WebGL gallery scenes", "custom material/vertex/light scene inputs", "HTML/Vite build", "canvas PNG and motion capture"],
    "usefulcharts-style": ["tree/lineage/parallel-history SVG", "panel/editorial/shared-row poster SVG", "HTML poster viewer", "PDF/PNG poster exports", "audit/critique JSON"],
    "vectorize-art-patterns": ["OpenCV segmented/stippled/pattern SVG", "VTracer curve SVG", "geometry-locked cs1/cs2 pairs", "PNG previews", "art/world-map galleries"],
    "video": ["mixed-media composition MP4", "scene preview HTML", "authored SVG/canvas captions/connectors", "transition manifests", "Slidev capture and contact sheets"],
}
NONVISUAL = {"google-cloud-sku-pricing", "jev-batch-decisions", "repository-reviewer-creator", "simulation-data-lab"}
SOURCE = {"ambientcg-material-search", "animated-svg-to-gif", "asciinema-real-command-video", "destockd-video-search", "hyperframes-explainer", "iconify-icon-search", "kenney-asset-search", "manim-svg-video", "pexels-media-search", "pixel-art-image-video", "polyhaven-asset-search", "technical-logo-assets", "usefulcharts-style", "video", "vectorize-art-patterns", "slidev-quality-audit"}
rows = [{"skill": name, "outputs": outputs, "scope": "nonvisual" if name in NONVISUAL else "authored-colorset", "sourceFidelity": "Preserve explicitly identified source media/brand/evidence/exact-RGB pixels; authored frame, chrome and technical marks remain palette-controlled." if name in SOURCE else None} for name, outputs in sorted(OUTPUTS.items())]
checks = []


def add(glob: str, mode: str = "auto", required: bool = True):
    checks.append({"glob": glob, "colorset": mode, "required": required})


add("skills/animated-svg-to-gif/assets/templates/*.svg", "colorset1")
add("skills/echarts-animated-svg/assets/templates/static-bar-chart.svg", "colorset1")
for mode in ("colorset1", "colorset2"):
    add(f"skills/mermaid/assets/examples/mermaid-max-complexity/svg/{mode}/*.svg", mode)
    add(f"projects/colorset-audit/artifacts/svgs/procedural-{mode}-full/*.svg", mode, False)
    add(f"projects/colorset-audit/artifacts/svgs/procedural-{mode}-reduced/*.svg", mode, False)
    add(f"projects/colorset-audit/artifacts/html/build_*-{mode}.html", mode, False)
add("skills/mermaid/assets/examples/mermaid-max-elements/**/*.svg", "colorset2", False)
add("skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer/svg/*.svg", "colorset2")
add("skills/plantuml-colorset-renderer/assets/examples/plantuml-colorset-renderer-cs1/svg/*.svg", "colorset1")
add("skills/procedural-svg-animation/assets/examples/procedural-svg-animation/patterns/*.svg", "colorset1")
add("skills/vectorize-art-patterns/assets/examples/vectorize-art-patterns/**/*.svg")
add("skills/vectorize-art-patterns/assets/examples/vectorize-abstract-world-maps/**/*.svg", "colorset1")
add("skills/usefulcharts-style/assets/examples/usefulcharts-style/**/*.svg", "colorset2")
add("skills/compose-synchronized-svg/assets/examples/compose-synchronized-svg/**/*.svg")
for skill in ("slidev-animejs",):
    add(f"skills/{skill}/assets/templates/**/*.svg", "colorset2", False)
for skill in ("ambientcg-material-search", "iconify-icon-search", "kenney-asset-search", "pexels-media-search", "polyhaven-asset-search"):
    add(f"skills/{skill}/scripts/asset_io.py", "colorset1")
add("skills/destockd-video-search/scripts/destockd.py", "colorset1")
add("skills/harbor-author-evaluation-datasets/scripts/consolidate_harbor_reports.py", "colorset2")
add("skills/technical-logo-assets/assets/logo-audit.html", "colorset2")
add("dist/pages/index.html", "colorset2", False)
add("skills/echarts-animated-svg/assets/examples/echarts-animated-svg/index.html", "colorset2")
for skill in ("d3", "hierarchy-lens", "compose-synchronized-svg", "usefulcharts-style", "procedural-svg-animation", "vectorize-art-patterns", "mermaid", "plantuml-colorset-renderer"):
    add(f"skills/{skill}/assets/examples/**/*.html", required=False)
    add(f"skills/{skill}/assets/examples/**/*.css", required=False)
inventory = {"schemaVersion": 1, "date": "2026-10-02", "contract": "docs/colorsets.json", "claim": "Supported output-route inventory and authored paint checks; source pixels and renderer-derived tones have explicit scopes. This is not an exhaustive proof of all arbitrary user-authored scenes.", "skills": rows, "artifactChecks": checks}
path = ROOT / "evaluations/colorset-audit/coverage.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
print(f"Recorded {len(rows)} skills and {len(checks)} artifact gates.")
