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
import re
from html import escape
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES_ROOT = ROOT / "dist" / "pages"
SKILLS = ROOT / "skills"
EXAMPLE_SOURCES = {
    "hierarchy-lens": SKILLS / "hierarchy-lens" / "assets" / "examples" / "hierarchy-lens",
    "usefulcharts-style": SKILLS / "usefulcharts-style" / "assets" / "examples" / "usefulcharts-style",
    "ai-concept-videos": SKILLS
    / "video"
    / "assets"
    / "examples"
    / "ai-concept-videos",
    "compose-synchronized-svg": SKILLS
    / "compose-synchronized-svg"
    / "assets"
    / "examples"
    / "compose-synchronized-svg",
    "d3": SKILLS / "d3" / "assets" / "examples" / "d3",
    "d3-animated-svg": SKILLS / "d3" / "assets" / "examples" / "d3-animated-svg",
    "d3-animated-svg-cs1": SKILLS
    / "d3"
    / "assets"
    / "examples"
    / "d3-animated-svg-cs1",
    "d3-animated-svg-colorset2": SKILLS
    / "d3"
    / "assets"
    / "examples"
    / "d3-animated-svg-colorset2",
    "d3-logo-design": SKILLS
    / "d3"
    / "assets"
    / "examples"
    / "d3-logo-design",
    "d3-logo-textures": SKILLS
    / "d3"
    / "assets"
    / "examples"
    / "d3-logo-textures",
    "echarts-animated-svg": SKILLS
    / "echarts-animated-svg"
    / "assets"
    / "examples"
    / "echarts-animated-svg",
    "mermaid-max-elements": SKILLS
    / "mermaid"
    / "assets"
    / "examples"
    / "mermaid-max-elements",
    "mermaid-max-complexity": SKILLS
    / "mermaid"
    / "assets"
    / "examples"
    / "mermaid-max-complexity",
    "plantuml-colorset-renderer-base": SKILLS
    / "plantuml-colorset-renderer"
    / "assets"
    / "examples"
    / "base",
    "plantuml-colorset-renderer": SKILLS
    / "plantuml-colorset-renderer"
    / "assets"
    / "examples"
    / "plantuml-colorset-renderer",
    "plantuml-colorset-renderer-cs1": SKILLS
    / "plantuml-colorset-renderer"
    / "assets"
    / "examples"
    / "plantuml-colorset-renderer-cs1",
    "procedural-svg-animation": SKILLS
    / "procedural-svg-animation"
    / "assets"
    / "examples"
    / "procedural-svg-animation",
    "slidev-animejs": SKILLS / "slidev-animejs" / "assets" / "examples" / "slidev-animejs",
    "slidev-echarts": SKILLS / "slidev-echarts" / "assets" / "examples" / "slidev-echarts",
    "threejs-animated-3d": SKILLS
    / "threejs-animated-3d"
    / "assets"
    / "examples"
    / "threejs-animated-3d",
    "vectorize-art-patterns": SKILLS
    / "vectorize-art-patterns"
    / "assets"
    / "examples"
    / "vectorize-art-patterns",
    "vectorize-abstract-world-maps": SKILLS
    / "vectorize-art-patterns"
    / "assets"
    / "examples"
    / "vectorize-abstract-world-maps",
}
UNLISTED_EXAMPLE_SOURCES = {
    # Raw source folders copied for linked galleries or verification assets, not standalone landing pages.
    # The unified `d3` hub links these focused views while the old public routes remain stable.
    "d3-animated-svg",
    "d3-animated-svg-cs1",
    "d3-animated-svg-colorset2",
    "d3-logo-design",
    "d3-logo-textures",
    "mermaid-max-elements",
    "plantuml-colorset-renderer-base",
    "plantuml-colorset-renderer-cs1",
}
PUBLISHED_EXAMPLE_SETS = [
    {
        "id": "hierarchy-lens",
        "source": "hierarchy-lens",
        "title": "Hierarchy Lens",
        "href": "examples/hierarchy-lens/",
        "kind": "Hierarchy composition engine",
        "description": "Place 1,200 fictional records one at a time using explicit priorities, parent proximity, attribute affinity, and compactness. Replay decisions, edit rules, and switch color lenses on the resulting pixel map.",
    },
    {
        "id": "usefulcharts-style",
        "source": "usefulcharts-style",
        "title": "Educational Poster Studies",
        "href": "examples/usefulcharts-style/",
        "kind": "Editable SVG posters",
        "description": "Original UsefulCharts-inspired genealogy, branching lineage, and parallel-history posters with semantic color, deliberate connector routing, source data, and zoomable SVG views.",
    },
    {
        "id": "compose-synchronized-svg",
        "source": "compose-synchronized-svg",
        "title": "Synchronized SVG Compositions",
        "href": "examples/compose-synchronized-svg/",
        "kind": "Interactive SVG",
        "description": "A fitted causal megacanvas and a navigable 36-module world share canonical state, explicit structural diagrams, semantic zoom, and deterministic routes for narration or video.",
    },
    {
        "id": "echarts-animated-svg",
        "source": "echarts-animated-svg",
        "title": "ECharts Animated SVG Gallery",
        "href": "examples/echarts-animated-svg/",
        "kind": "Inline SVG",
        "description": "Replayable ECharts chart-type examples rendered as portable SVG.",
    },
    {
        "id": "mermaid-max-complexity",
        "source": "mermaid-max-complexity",
        "title": "Mermaid Maximum Complexity Gallery",
        "href": "examples/mermaid-max-complexity/",
        "kind": "Mermaid SVG",
        "description": "All 31 Mermaid 11.16.0 diagram families at their documented palette or practical complexity boundary, paired in Colorset 1 and Colorset 2 with static and replayable SVG output.",
    },
    {
        "id": "d3",
        "source": "d3",
        "title": "D3 Skill Gallery",
        "href": "examples/d3/",
        "kind": "D3",
        "description": "One entry point for custom charts, networks, maps, simulations, interaction, composition analysis, parametric logos, textures, and portable SVG output.",
    },
    {
        "id": "procedural-svg-animation",
        "source": "procedural-svg-animation",
        "title": "Procedural SVG Animation Patterns",
        "href": "examples/procedural-svg-animation/",
        "kind": "Procedural SVG",
        "description": "A deterministic catalog of procedural SVG motion systems spanning timing, geometry, fields, simulations, growth, compositing, and auditable multi-strata solvers.",
    },
    {
        "id": "plantuml-colorset-renderer",
        "source": "plantuml-colorset-renderer",
        "title": "PlantUML Skill Gallery",
        "href": "examples/plantuml-colorset-renderer/",
        "kind": "PlantUML",
        "description": "One gallery for 28 published PlantUML coverage examples across every available family, switchable Colorset 1 and Colorset 2 renders, SVG/PNG output, replay motion, engine options, and the normalized technical-logo catalog.",
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
        "id": "vectorize-art-patterns",
        "source": "vectorize-art-patterns",
        "title": "Vectorized Art Patterns",
        "href": "examples/vectorize-art-patterns/",
        "kind": "Editable SVG",
        "description": "Thirty distinct open masterpieces by 28 creators, each traced once and shown as a geometry-locked Colorset 1 and Colorset 2 SVG pair.",
    },
    {
        "id": "vectorize-abstract-world-maps",
        "source": "vectorize-abstract-world-maps",
        "title": "Abstract World Map Studies",
        "href": "examples/vectorize-abstract-world-maps/",
        "kind": "Editable SVG",
        "description": "Two Colorset 1 global studies compare a biomorphic Equal Earth silhouette with an intentionally imprecise straight-line continental collage.",
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


def write_favicon() -> None:
    # A valid 1x1 transparent ICO prevents browser favicon 404s across copied example pages.
    icon_header = b"\x00\x00\x01\x00\x01\x00"
    icon_entry = (
        b"\x01\x01\x00\x00"
        + (1).to_bytes(2, "little")
        + (32).to_bytes(2, "little")
        + (48).to_bytes(4, "little")
        + (22).to_bytes(4, "little")
    )
    bitmap_header = (
        (40).to_bytes(4, "little")
        + (1).to_bytes(4, "little", signed=True)
        + (2).to_bytes(4, "little", signed=True)
        + (1).to_bytes(2, "little")
        + (32).to_bytes(2, "little")
        + (0).to_bytes(4, "little")
        + (4).to_bytes(4, "little")
        + (0).to_bytes(4, "little", signed=True)
        + (0).to_bytes(4, "little", signed=True)
        + (0).to_bytes(4, "little")
        + (0).to_bytes(4, "little")
    )
    transparent_pixel = b"\x00\x00\x00\x00"
    transparency_mask = b"\x00\x00\x00\x00"
    (PAGES_ROOT / "favicon.ico").write_bytes(icon_header + icon_entry + bitmap_header + transparent_pixel + transparency_mask)


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


class PageMarkupParser(HTMLParser):
    def __init__(self, content: str) -> None:
        super().__init__(convert_charrefs=False)
        self.line_offsets = [0, *(match.end() for match in re.finditer("\n", content))]
        self.body: tuple[int, str, list[tuple[str, str | None]]] | None = None
        self.head_end: int | None = None
        self.in_head = False
        self.meta_names: set[str] = set()
        self.has_favicon = False

    def source_offset(self) -> int:
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "body" and self.body is None:
            raw_tag = self.get_starttag_text()
            assert raw_tag is not None
            self.body = (self.source_offset(), raw_tag, attrs)
        if tag == "head" and self.head_end is None:
            self.in_head = True
        if self.in_head:
            attributes = {name: value or "" for name, value in attrs}
            if tag == "meta":
                self.meta_names.add(attributes.get("name", "").lower())
            if tag == "link" and "icon" in attributes.get("rel", "").lower().split():
                self.has_favicon = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "head" and self.in_head:
            if self.head_end is None:
                self.head_end = self.source_offset()
            self.in_head = False


def parse_page_markup(content: str) -> PageMarkupParser:
    parser = PageMarkupParser(content)
    parser.feed(content)
    return parser


def ensure_html_head_meta(content: str, example_id: str) -> str:
    parser = parse_page_markup(content)
    if parser.head_end is None:
        return content
    metadata = {"example-id": example_id, "pattern-id": example_id, "pattern-page": "true"}
    missing = "".join(
        f'  <meta name="{name}" content="{escape(value, quote=True)}">\n'
        for name, value in metadata.items()
        if name not in parser.meta_names
    )
    return content[:parser.head_end] + missing + content[parser.head_end:]


def ensure_html_favicon(content: str) -> str:
    parser = parse_page_markup(content)
    if parser.has_favicon or parser.head_end is None:
        return content
    favicon = '  <link rel="icon" href="../../favicon.ico">\n'
    return content[:parser.head_end] + favicon + content[parser.head_end:]


def ensure_body_attribute(content: str, name: str, value: str) -> str:
    parser = parse_page_markup(content)
    if parser.body is None:
        return content
    offset, raw_tag, attributes = parser.body
    if any(attribute == name.lower() for attribute, _ in attributes):
        return content
    # Keep script literals, comments, existing quoting and every other byte intact.
    closing = len(raw_tag) - (2 if raw_tag.endswith("/>") else 1)
    insertion = offset + closing
    return content[:insertion] + f' {name}="{escape(value, quote=True)}"' + content[insertion:]


def patch_page_metadata(example_id: str, index_path: Path) -> None:
    content = index_path.read_text(encoding="utf-8")
    content = ensure_html_head_meta(content, example_id)
    content = ensure_html_favicon(content)
    for name, value in {
        "data-example-id": example_id,
        "data-pattern-id": example_id,
        "data-pattern-page": "true",
    }.items():
        content = ensure_body_attribute(content, name, value)
    index_path.write_text(content, encoding="utf-8", newline="\n")


def write_plantuml_legacy_redirect() -> None:
    legacy_index = PAGES_ROOT / "examples" / "plantuml-colorset-renderer-cs1" / "index.html"
    legacy_index.write_text(
        """<!doctype html>
<html lang="en" data-colorset="colorset2">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="refresh" content="0; url=../plantuml-colorset-renderer/?theme=colorset1">
  <link rel="canonical" href="../plantuml-colorset-renderer/?theme=colorset1">
  <link rel="icon" href="../../favicon.ico">
  <title>PlantUML gallery moved</title>
</head>
<body data-legacy-redirect="plantuml-colorset-renderer-cs1">
  <p>The Colorset 1 examples now live in the unified <a id="canonical-link" href="../plantuml-colorset-renderer/?theme=colorset1">PlantUML Skill Gallery</a>.</p>
  <script>
    const target = new URL("../plantuml-colorset-renderer/", window.location.href);
    target.searchParams.set("theme", "colorset1");
    target.hash = window.location.hash;
    document.querySelector("#canonical-link").href = target.href;
    window.location.replace(target.href);
  </script>
</body>
</html>
""",
        encoding="utf-8",
        newline="\n",
    )


def write_index() -> None:
    links = "\n".join(
        f"""        <a class="card" id="example-set-{card['id']}" data-example-id="{card['id']}" data-pattern-id="{card['id']}" data-example-source="{card['source']}" href="{card['href']}">
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
      --page: #f7f7f7;
      --surface: #ffffff;
      --ink: #000000;
      --muted: #000000;
      --line: #cfcfcf;
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
      border-bottom: 0;
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
      border: 0;
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
      border: 0;
      border-radius: 8px;
      background: var(--surface);
      color: inherit;
      padding: 18px;
      text-decoration: none;
      box-shadow: none;
    }}
    .card:hover {{
      background: #e7e7e7;
    }}
    a:focus-visible {{ outline: 2px solid #9e1b32; outline-offset: 3px; }}
    .kind {{
      width: max-content;
      border-radius: 999px;
      background: #007298;
      color: #ffffff;
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
      border: 0;
      border-radius: 6px;
      background: #f7f7f7;
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
<body data-example-id="codex-skills-examples" data-pattern-id="codex-skills-examples" data-pattern-page="catalog">
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
    (PAGES_ROOT / "index.html").write_text(index, encoding="utf-8", newline="\n")


def write_catalog() -> None:
    catalog = "[\n"
    catalog += ",\n".join(
        "  {\n"
        f"    \"id\": \"{card['id']}\",\n"
        f"    \"source\": \"{card['source']}\",\n"
        f"    \"title\": \"{card['title']}\",\n"
        f"    \"href\": \"{card['href']}\",\n"
        f"    \"kind\": \"{card['kind']}\",\n"
        f"    \"patternId\": \"{card['id']}\",\n"
        "    \"pageFormat\": \"pattern-gallery\",\n"
        f"    \"description\": \"{card['description']}\"\n"
        "  }"
        for card in PUBLISHED_EXAMPLE_SETS
    )
    catalog += "\n]\n"
    (PAGES_ROOT / "example-catalog.json").write_text(catalog, encoding="utf-8", newline="\n")


def normalize_text_file(path: Path) -> None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return
    # Whitespace and Unicode line separators can carry meaning inside web literals.
    if path.suffix.lower() in {".css", ".html", ".js", ".mjs", ".svg", ".ts", ".vue"}:
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


def reset_pages_output() -> None:
    # Refuse symlink/junction escapes or an accidentally widened cleanup target.
    expected = ROOT.resolve() / "dist" / "pages"
    if PAGES_ROOT.resolve() != expected or PAGES_ROOT.is_symlink():
        raise ValueError("Pages cleanup is restricted to the repository's dist/pages directory")
    if PAGES_ROOT.exists():
        shutil.rmtree(PAGES_ROOT)
    PAGES_ROOT.mkdir(parents=True)


def build_docs() -> None:
    reset_pages_output()
    (PAGES_ROOT / ".nojekyll").write_text("", encoding="utf-8")
    write_favicon()

    copy_tree(example_source("hierarchy-lens"), PAGES_ROOT / "examples" / "hierarchy-lens")
    copy_tree(example_source("usefulcharts-style"), PAGES_ROOT / "examples" / "usefulcharts-style")

    copy_tree(example_source("compose-synchronized-svg"), PAGES_ROOT / "examples" / "compose-synchronized-svg")
    copy_tree(example_source("echarts-animated-svg"), PAGES_ROOT / "examples" / "echarts-animated-svg")
    mermaid_gallery = example_source("mermaid-max-complexity")
    copy_tree(mermaid_gallery, PAGES_ROOT / "examples" / "mermaid-max-complexity")
    copy_tree(
        mermaid_gallery / "legacy" / "mermaid-svg-animated",
        PAGES_ROOT / "examples" / "mermaid-svg-animated",
    )
    copy_tree(
        mermaid_gallery / "legacy" / "mermaid-animation-directives",
        PAGES_ROOT / "examples" / "mermaid-animation-directives",
    )

    copy_tree(example_source("d3"), PAGES_ROOT / "examples" / "d3")
    copy_tree(example_source("d3-animated-svg"), PAGES_ROOT / "examples" / "d3-animated-svg")
    patch_file(
        PAGES_ROOT / "examples" / "d3-animated-svg" / "index.html",
        {
            "./node_modules/d3/dist/d3.min.js": "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js",
            "./node_modules/d3-sankey/dist/d3-sankey.min.js": "https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js",
        },
    )
    patch_file(
        PAGES_ROOT / "examples" / "d3-animated-svg" / "composition-sheets.html",
        {
            "./node_modules/d3/dist/d3.min.js": "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js",
            "./node_modules/d3-sankey/dist/d3-sankey.min.js": "https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js",
        },
    )
    patch_file(
        PAGES_ROOT / "examples" / "d3-animated-svg" / "force-beeswarm.html",
        {"./node_modules/d3/dist/d3.min.js": "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"},
    )
    copy_tree(example_source("d3-animated-svg-colorset2"), PAGES_ROOT / "examples" / "d3-animated-svg-colorset2")
    patch_file(
        PAGES_ROOT / "examples" / "d3-animated-svg-colorset2" / "index.html",
        {
            "../d3-animated-svg/node_modules/d3/dist/d3.min.js": "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js",
            "../d3-animated-svg/node_modules/d3-sankey/dist/d3-sankey.min.js": "https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js",
        },
    )
    copy_tree(example_source("d3-animated-svg-cs1"), PAGES_ROOT / "examples" / "d3-animated-svg-cs1")
    patch_file(
        PAGES_ROOT / "examples" / "d3-animated-svg-cs1" / "index.html",
        {
            "../d3-animated-svg/node_modules/d3/dist/d3.min.js": "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js",
            "../d3-animated-svg/node_modules/d3-sankey/dist/d3-sankey.min.js": "https://cdn.jsdelivr.net/npm/d3-sankey@0.12.3/dist/d3-sankey.min.js",
        },
    )
    copy_tree(example_source("d3-logo-design"), PAGES_ROOT / "examples" / "d3-logo-design")
    copy_tree(example_source("d3-logo-textures"), PAGES_ROOT / "examples" / "d3-logo-textures")
    copy_tree(example_source("procedural-svg-animation"), PAGES_ROOT / "examples" / "procedural-svg-animation")
    copy_tree(example_source("plantuml-colorset-renderer"), PAGES_ROOT / "examples" / "plantuml-colorset-renderer")
    copy_tree(example_source("plantuml-colorset-renderer-cs1"), PAGES_ROOT / "examples" / "plantuml-colorset-renderer-cs1")
    write_plantuml_legacy_redirect()
    copy_tree(example_source("vectorize-art-patterns"), PAGES_ROOT / "examples" / "vectorize-art-patterns")
    copy_tree(
        example_source("vectorize-abstract-world-maps"),
        PAGES_ROOT / "examples" / "vectorize-abstract-world-maps",
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

    copy_tree(threejs_project / "dist", PAGES_ROOT / "examples" / "threejs-animated-3d")
    copy_tree(slidev_echarts_html, PAGES_ROOT / "examples" / "slidev-echarts")
    copy_tree(slidev_animejs_html, PAGES_ROOT / "examples" / "slidev-animejs")

    copy_tree(example_source("ai-concept-videos"), PAGES_ROOT / "examples" / "ai-concept-videos")
    patch_file(
        PAGES_ROOT / "examples" / "ai-concept-videos" / "index.html",
        {
            "./node_modules/d3/dist/d3.min.js": "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js",
            "./node_modules/animejs/dist/bundles/anime.umd.min.js": "https://cdn.jsdelivr.net/npm/animejs@4.4.1/dist/bundles/anime.umd.min.js",
        },
    )

    for card in PUBLISHED_EXAMPLE_SETS:
        index_path = PAGES_ROOT / card["href"] / "index.html"
        if not index_path.exists():
            raise FileNotFoundError(f"Published example page is missing: {index_path.relative_to(ROOT).as_posix()}")
        patch_page_metadata(card["id"], index_path)

    write_index()
    write_catalog()
    normalize_text_tree(PAGES_ROOT)


def main() -> int:
    try:
        build_docs()
    except Exception as error:
        print(f"Pages build failed: {error}")
        return 1

    total = sum(path.stat().st_size for path in PAGES_ROOT.rglob("*") if path.is_file())
    files = sum(1 for path in PAGES_ROOT.rglob("*") if path.is_file())
    print(f"Pages built in dist/pages/ with {files} files, {total / 1024 / 1024:.2f} MiB.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
