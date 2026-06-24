#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SKILLS = ROOT / ".agents" / "skills"
EXAMPLE_SOURCES = {
    "ai-concept-videos": SKILLS
    / "html-d3-anime-video-workflow"
    / "assets"
    / "examples"
    / "ai-concept-videos",
    "d3-animated-svg": SKILLS / "d3-animated-svg" / "assets" / "examples" / "d3-animated-svg",
    "echarts-animated-svg": SKILLS
    / "echarts-animated-svg"
    / "assets"
    / "examples"
    / "echarts-animated-svg",
    "mermaid": SKILLS / "mermaid-animated-svg" / "assets" / "examples" / "mermaid",
    "mermaid-animation-directives": SKILLS
    / "mermaid-animated-svg"
    / "assets"
    / "examples"
    / "mermaid-animation-directives",
    "mermaid-directive-frames": SKILLS
    / "mermaid-animated-svg"
    / "assets"
    / "examples"
    / "playwright"
    / "mermaid-animation-directives",
    "mermaid-svg-animated": SKILLS
    / "mermaid-animated-svg"
    / "assets"
    / "examples"
    / "mermaid-svg-animated",
    "slidev-animejs": SKILLS / "slidev-animejs" / "assets" / "examples" / "slidev-animejs",
    "slidev-echarts": SKILLS / "slidev-echarts" / "assets" / "examples" / "slidev-echarts",
    "threejs-animated-3d": SKILLS
    / "threejs-animated-3d"
    / "assets"
    / "examples"
    / "threejs-animated-3d",
}
UNLISTED_EXAMPLE_SOURCES = {
    # Raw source folders copied for linked galleries or verification assets, not standalone landing pages.
    "mermaid",
    "mermaid-directive-frames",
}
PUBLISHED_EXAMPLE_SETS = [
    {
        "id": "echarts-animated-svg",
        "source": "echarts-animated-svg",
        "title": "ECharts Animated SVG Gallery",
        "href": "examples/echarts-animated-svg/",
        "kind": "Inline SVG",
        "description": "Replayable ECharts chart-type examples rendered as portable SVG.",
    },
    {
        "id": "d3-animated-svg",
        "source": "d3-animated-svg",
        "title": "D3 Animated SVG Gallery",
        "href": "examples/d3-animated-svg/",
        "kind": "D3",
        "description": "A broad gallery of D3-generated SVG forms with replay controls.",
    },
    {
        "id": "mermaid-svg-animated",
        "source": "mermaid-svg-animated",
        "title": "Mermaid Animated SVG Gallery",
        "href": "examples/mermaid-svg-animated/",
        "kind": "Mermaid",
        "description": "Animated and static SVG pairs for supported Mermaid diagram types.",
    },
    {
        "id": "mermaid-animation-directives",
        "source": "mermaid-animation-directives",
        "title": "Mermaid Animation Directives",
        "href": "examples/mermaid-animation-directives/",
        "kind": "Directive demos",
        "description": "Generated directive examples with animated, static, and inspected frames.",
    },
    {
        "id": "threejs-animated-3d",
        "source": "threejs-animated-3d",
        "title": "Three.js Animated 3D Examples",
        "href": "examples/threejs-animated-3d/",
        "kind": "WebGL",
        "description": "Browser-rendered 3D scenes built from the reusable Three.js skill patterns.",
    },
    {
        "id": "slidev-echarts",
        "source": "slidev-echarts",
        "title": "Slidev ECharts Chart-Type Lab",
        "href": "examples/slidev-echarts/",
        "kind": "Slidev",
        "description": "A single-file validation deck for ECharts chart coverage inside Slidev.",
    },
    {
        "id": "slidev-animejs",
        "source": "slidev-animejs",
        "title": "Slidev Anime.js Animation Lab",
        "href": "examples/slidev-animejs/",
        "kind": "Slidev",
        "description": "A built Slidev deck covering Anime.js animation patterns and SVG assets.",
    },
    {
        "id": "ai-concept-videos",
        "source": "ai-concept-videos",
        "title": "AI Concept Scene Preview",
        "href": "examples/ai-concept-videos/",
        "kind": "Interactive scene",
        "description": "The source scene preview for the video workflow, published without rendered videos.",
    },
]
MEDIA_EXTENSIONS = {
    ".mp4",
    ".webm",
    ".mov",
    ".avi",
    ".mkv",
    ".gif",
    ".apng",
}
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".mjs",
    ".mmd",
    ".svg",
    ".ts",
    ".txt",
    ".vue",
    ".yaml",
    ".yml",
}


def require_path(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"Required Pages source is missing: {path.relative_to(ROOT).as_posix()}")
    return path


def example_source(name: str) -> Path:
    return require_path(EXAMPLE_SOURCES[name])


def npm_executable() -> str:
    return "npm.cmd" if sys.platform == "win32" else "npm"


def run_command(args: list[str], cwd: Path) -> None:
    print(f"Running {' '.join(args)} in {cwd.relative_to(ROOT).as_posix()}", flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def ensure_node_dependencies(project: Path) -> None:
    require_path(project / "package-lock.json")
    if (project / "node_modules").exists():
        return
    run_command([npm_executable(), "ci", "--no-audit", "--no-fund"], project)


def run_npm_script(project: Path, script: str) -> None:
    ensure_node_dependencies(project)
    run_command([npm_executable(), "run", script], project)


def copy_file(src: Path, dst: Path) -> None:
    require_path(src)
    if src.suffix.lower() in MEDIA_EXTENSIONS:
        raise ValueError(f"Refusing to copy rendered media into docs: {src.relative_to(ROOT).as_posix()}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    require_path(src)
    ignored = shutil.ignore_patterns(
        "node_modules",
        ".vite",
        "dist",
        "__pycache__",
        "*.mp4",
        "*.webm",
        "*.mov",
        "*.avi",
        "*.mkv",
        "*.gif",
        "*.apng",
    )
    shutil.copytree(src, dst, ignore=ignored, dirs_exist_ok=True)


def patch_file(path: Path, replacements: dict[str, str]) -> None:
    content = path.read_text(encoding="utf-8")
    for before, after in replacements.items():
        content = content.replace(before, after)
    path.write_text(content, encoding="utf-8", newline="\n")


def write_index() -> None:
    links = "\n".join(
        f"""        <a class="card" id="example-set-{card['id']}" data-example-id="{card['id']}" data-example-source="{card['source']}" href="{card['href']}">
          <span class="kind">{card['kind']}</span>
          <strong>{card['title']}</strong>
          <code>{card['id']}</code>
          <span>{card['description']}</span>
        </a>"""
        for card in PUBLISHED_EXAMPLE_SETS
    )
    index = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <title>Codex Skills Examples</title>
  <style>
    :root {{
      color-scheme: light;
      --page: #f6f7f9;
      --surface: #ffffff;
      --ink: #28313b;
      --muted: #66717f;
      --line: #d7dde5;
      --red: #9e1b32;
      --blue: #007298;
      --green: #45842a;
      --yellow: #f1c319;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-width: 320px;
      background: var(--page);
      color: var(--ink);
      font: 15px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: var(--surface);
    }}
    .wrap {{
      width: min(1180px, calc(100% - 32px));
      margin: 0 auto;
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 22px;
      align-items: end;
      padding: 34px 0 24px;
    }}
    h1 {{
      margin: 0;
      color: var(--red);
      font-size: clamp(28px, 4vw, 44px);
      line-height: 1.05;
      letter-spacing: 0;
    }}
    .lede {{
      max-width: 760px;
      margin: 10px 0 0;
      color: var(--muted);
      font-size: 16px;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(3, auto);
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
      white-space: nowrap;
    }}
    .pill {{
      border: 1px solid var(--line);
      border-radius: 999px;
      background: #fff;
      padding: 6px 10px;
    }}
    main {{
      padding: 24px 0 42px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
      gap: 14px;
    }}
    .card {{
      min-height: 178px;
      display: grid;
      align-content: start;
      gap: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--surface);
      color: inherit;
      padding: 18px;
      text-decoration: none;
      box-shadow: 0 8px 20px rgba(40, 49, 59, .06);
    }}
    .card:hover {{
      border-color: #93bfdb;
      box-shadow: 0 12px 28px rgba(40, 49, 59, .10);
    }}
    .kind {{
      width: max-content;
      border-radius: 999px;
      background: #eef7fb;
      color: #075673;
      padding: 4px 9px;
      font-size: 12px;
      font-weight: 700;
    }}
    strong {{
      color: var(--ink);
      font-size: 20px;
      line-height: 1.18;
      letter-spacing: 0;
    }}
    .card code {{
      width: max-content;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f9fafb;
      color: var(--muted);
      padding: 3px 6px;
      font: 700 12px/1.2 Consolas, "Liberation Mono", "Courier New", monospace;
      overflow-wrap: anywhere;
    }}
    .card span:last-child {{
      color: var(--muted);
    }}
    footer {{
      margin-top: 22px;
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 720px) {{
      .hero {{
        grid-template-columns: 1fr;
      }}
      .summary {{
        grid-template-columns: 1fr;
        white-space: normal;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="wrap hero">
      <div>
        <h1>Codex Skills Examples</h1>
        <p class="lede">Generated example galleries and validation fixtures for the skills in this repository. Rendered videos and bulky local artifacts are intentionally excluded.</p>
      </div>
      <div class="summary" aria-label="Published artifact summary">
        <span class="pill">{len(PUBLISHED_EXAMPLE_SETS)} example sets</span>
        <span class="pill">No videos</span>
        <span class="pill">Static Pages</span>
      </div>
    </div>
  </header>
  <main class="wrap">
    <section class="grid" aria-label="Example galleries">
{links}
    </section>
    <footer>Generated by <code>uv run --script scripts/build-pages.py</code>.</footer>
  </main>
</body>
</html>
"""
    (DOCS / "index.html").write_text(index, encoding="utf-8", newline="\n")


def write_catalog() -> None:
    catalog = "[\n"
    catalog += ",\n".join(
        "  {\n"
        f"    \"id\": \"{card['id']}\",\n"
        f"    \"source\": \"{card['source']}\",\n"
        f"    \"title\": \"{card['title']}\",\n"
        f"    \"href\": \"{card['href']}\",\n"
        f"    \"kind\": \"{card['kind']}\",\n"
        f"    \"description\": \"{card['description']}\"\n"
        "  }"
        for card in PUBLISHED_EXAMPLE_SETS
    )
    catalog += "\n]\n"
    (DOCS / "example-catalog.json").write_text(catalog, encoding="utf-8", newline="\n")


def normalize_text_file(path: Path) -> None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    lines = [line.rstrip(" \t") for line in content.splitlines()]
    while lines and lines[-1] == "":
        lines.pop()
    normalized = "\n".join(lines) + "\n"
    if normalized == content:
        return
    for attempt in range(5):
        try:
            path.write_text(normalized, encoding="utf-8", newline="\n")
            return
        except OSError:
            if attempt == 4:
                raise
            time.sleep(0.1)


def normalize_text_tree(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_file():
            normalize_text_file(path)


def build_docs() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")

    copy_tree(example_source("echarts-animated-svg"), DOCS / "examples" / "echarts-animated-svg")

    copy_tree(example_source("d3-animated-svg"), DOCS / "examples" / "d3-animated-svg")
    patch_file(
        DOCS / "examples" / "d3-animated-svg" / "index.html",
        {
            "./node_modules/d3/dist/d3.min.js": "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js",
            "./node_modules/d3-sankey/dist/d3-sankey.min.js": "https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js",
        },
    )
    patch_file(
        DOCS / "examples" / "d3-animated-svg" / "force-beeswarm.html",
        {"./node_modules/d3/dist/d3.min.js": "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"},
    )
    copy_tree(example_source("mermaid"), DOCS / "examples" / "mermaid")
    copy_tree(example_source("mermaid-svg-animated"), DOCS / "examples" / "mermaid-svg-animated")
    copy_tree(example_source("mermaid-animation-directives"), DOCS / "examples" / "mermaid-animation-directives")
    copy_tree(
        example_source("mermaid-directive-frames"),
        DOCS / "examples" / "playwright" / "mermaid-animation-directives",
    )

    threejs_project = example_source("threejs-animated-3d")
    slidev_echarts_project = example_source("slidev-echarts")
    slidev_animejs_project = example_source("slidev-animejs")
    slidev_echarts_html = ROOT / "projects" / "slidev-echarts-validation" / "artifacts" / "html"
    slidev_animejs_html = ROOT / "projects" / "slidev-animejs-validation" / "artifacts" / "html"

    run_npm_script(threejs_project, "build")
    shutil.rmtree(slidev_echarts_html, ignore_errors=True)
    shutil.rmtree(slidev_animejs_html, ignore_errors=True)
    run_npm_script(slidev_echarts_project, "build:html")
    run_npm_script(slidev_animejs_project, "export:html")

    copy_tree(threejs_project / "dist", DOCS / "examples" / "threejs-animated-3d")
    copy_tree(slidev_echarts_html, DOCS / "examples" / "slidev-echarts")
    copy_tree(slidev_animejs_html, DOCS / "examples" / "slidev-animejs")

    copy_tree(example_source("ai-concept-videos"), DOCS / "examples" / "ai-concept-videos")
    patch_file(
        DOCS / "examples" / "ai-concept-videos" / "index.html",
        {
            "./node_modules/d3/dist/d3.min.js": "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js",
            "./node_modules/animejs/dist/bundles/anime.umd.min.js": "https://cdn.jsdelivr.net/npm/animejs@4.4.1/dist/bundles/anime.umd.min.js",
        },
    )

    write_index()
    write_catalog()
    normalize_text_tree(DOCS)


def main() -> int:
    try:
        build_docs()
    except Exception as error:
        print(f"Pages build failed: {error}")
        return 1

    total = sum(path.stat().st_size for path in DOCS.rglob("*") if path.is_file())
    files = sum(1 for path in DOCS.rglob("*") if path.is_file())
    print(f"Pages built in docs/ with {files} files, {total / 1024 / 1024:.2f} MiB.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
