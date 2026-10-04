#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Reuse the existing independent native-surface audit in a fresh evidence directory."""

from pathlib import Path

root = Path(__file__).resolve().parents[3]
source = root / "projects/solid-colorset-style/scripts/review-native-mermaid.ts"
target = root / "projects/colorset-priority/scripts/review_mermaid.ts"
text = source.read_text(encoding="utf-8")
text = text.replace("npx tsx projects/solid-colorset-style/scripts/review-native-mermaid.ts", "node --experimental-strip-types projects/colorset-priority/scripts/review_mermaid.ts [--published]")
text = text.replace("import {readFileSync,writeFileSync}", "import {readFileSync,writeFileSync,mkdirSync}")
text = text.replace("const artifactRoot=new URL('projects/solid-colorset-style/artifacts/',root);", "const published=process.argv.includes('--published');\nconst artifactRoot=new URL(`projects/colorset-priority/artifacts/mermaid-${published?'public':'local'}/`,root);\nmkdirSync(artifactRoot,{recursive:true});")
text = text.replace("const gallery=new URL('skills/mermaid/assets/examples/mermaid-max-complexity/',root);", "const gallery=new URL('skills/mermaid/assets/examples/mermaid-max-complexity/',root);\nconst visibleGallery=published?new URL('https://gvillarroel.github.io/skills/examples/mermaid-max-complexity/'):gallery;")
text = text.replace("page.goto(new URL(item.staticSvg,gallery).href)", "page.goto(new URL(item.staticSvg,visibleGallery).href)")
text = text.replace("['sequence','venn','radar','cynefin']", "['flowchart','state','gantt','treemap','sequence','venn','radar','cynefin']")
text = text.replace("page.goto(new URL(`svg/colorset1/${family}.static.svg`,gallery).href)", "page.goto(new URL(`svg/colorset1/${family}.static.svg`,visibleGallery).href)")
target.write_text(text, encoding="utf-8", newline="\n")
print("Prepared the native Mermaid priority review.")
