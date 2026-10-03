#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Bind one research hypothesis to an original, self-contained SVG candidate."""
import json
from pathlib import Path
import sys

from seal_technique_evolution import REPO


PROOF = r'''#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "defusedxml==0.7.1"]
# ///
"""Show scale, transparency and optional-group variants without editing the SVG."""
import argparse
import io
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as XML

from defusedxml import ElementTree as SafeXML
from PIL import Image, ImageDraw
import resvg_py

from render_svg import render


def omit_groups(text, identifiers):
    root = SafeXML.fromstring(text)
    removed = set()
    for parent in list(root.iter()):
        for child in list(parent):
            identifier = child.get("id")
            if child.tag == "{http://www.w3.org/2000/svg}g" and identifier in identifiers:
                parent.remove(child)
                removed.add(identifier)
    return XML.tostring(root, encoding="unicode"), sorted(removed)


def raster(text, size, font_dir=None):
    root = SafeXML.fromstring(text)
    box = [float(v) for v in root.get("viewBox").replace(",", " ").split()]
    scale = size / max(box[2:])
    options = {"font_family": "DejaVu Sans", "sans_serif_family": "DejaVu Sans"}
    if font_dir:
        options.update(font_dirs=[str(font_dir)], skip_system_fonts=True)
    png = resvg_py.svg_to_bytes(svg_string=text,
        width=max(1, round(box[2]*scale)), height=max(1, round(box[3]*scale)), **options)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def on_ground(image, color):
    return Image.alpha_composite(Image.new("RGBA", image.size, color), image).convert("RGB")


def proof(source, output, omit=(), small_size=192, font_dir=None):
    if source.resolve() == output.resolve():
        raise ValueError("Proof must not overwrite the SVG")
    if not 64 <= small_size <= 512:
        raise ValueError("small-size must be between 64 and 512")
    original = source.read_bytes()
    # Validate the complete original before rendering any diagnostic variant.
    with tempfile.TemporaryDirectory(prefix="svg-proof-") as directory:
        check = Path(directory) / "check.png"
        original_receipt = render(source, check, 512, font_dir)
    text = original.decode("utf-8-sig")
    variants = [("Current SVG", text)]
    hidden, removed = omit_groups(text, set(omit))
    missing = sorted(set(omit)-set(removed))
    if removed:
        variants.append(("Without optional groups: " + ", ".join(removed), hidden))
    small_height = small_size + 20
    color_top = 598 + small_height + 35
    sheet = Image.new("RGB", (560*len(variants), color_top + 220), "#e9ebef")
    draw = ImageDraw.Draw(sheet)
    for column, (title, svg) in enumerate(variants):
        x = column*560
        draw.text((x+18, 14), title, fill="black")
        large = raster(svg, 512, font_dir)
        small = raster(svg, small_size, font_dir)
        samples = [(large, "white", 42, 520, "Large view: joins and contours"),
                   (small, "white", 598, small_height, "Small view: hierarchy and recognition")]
        for bitmap, color, top, height, label in samples:
            draw.text((x+18, top-18), label, fill="black")
            draw.rectangle((x+12, top, x+548, top+height), fill=color)
            composed = on_ground(bitmap, color)
            sheet.paste(composed, (x+280-composed.width//2, top+(height-composed.height)//2))
        # A small colored inset exposes opaque white patches in supposed holes.
        inset = on_ground(raster(svg, 152, font_dir), "#8fc8d4")
        draw.text((x+18, color_top-18), "Colored ground: true holes versus white patches", fill="black")
        sheet.paste(inset, (x+280-inset.width//2, color_top+85-inset.height//2))
    if missing:
        draw.text((18, sheet.height-28), "Not omitted (no matching group): " + ", ".join(missing), fill="black")
    else:
        draw.text((18, sheet.height-28), "Diagnostic proof only. Choose by the brief, not by element count.", fill="black")
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG")
    if source.read_bytes() != original:
        raise RuntimeError("Source changed during proof generation")
    return {"proof": str(output), "omitted_groups": removed, "missing_groups": missing,
            "variants": len(variants), "small_size": small_size, "source_unchanged": True,
            "source_preview": {k:v for k,v in original_receipt.items() if k != "preview"},
            "semantic_quality": "not scored; inspect required meaning and composition"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--omit", action="append", default=[])
    parser.add_argument("--small-size", type=int, default=192)
    parser.add_argument("--font-dir", type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(proof(args.svg, args.output, args.omit, args.small_size, args.font_dir)))
    except (ValueError, OSError, SafeXML.ParseError) as error:
        parser.exit(2, f"Cannot make SVG proof: {error}\n")


if __name__ == "__main__":
    main()
'''

TESTS = r'''#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "defusedxml==0.7.1"]
# ///
"""Check reversible proofing, true holes and preserved source material."""
from pathlib import Path
import tempfile
import unittest

from PIL import Image
from proof_svg import omit_groups, raster, on_ground, proof


class ProofTests(unittest.TestCase):
    def test_transparent_hole_and_white_patch_are_different(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path fill-rule="evenodd" d="M5 5H95V95H5Z M30 30H70V70H30Z"/></svg>'
        transparent = raster(svg, 100)
        self.assertEqual(transparent.getpixel((50, 50))[3], 0)
        self.assertEqual(on_ground(transparent, "#8fc8d4").getpixel((50, 50)), (143, 200, 212))
        painted = svg.replace('</svg>', '<rect x="30" y="30" width="40" height="40" fill="white"/></svg>')
        self.assertEqual(on_ground(raster(painted, 100), "#8fc8d4").getpixel((50, 50)), (255, 255, 255))

    def test_omission_preserves_required_group_and_does_not_rewrite_source(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><g id="required"><rect x="10" y="10" width="25" height="70"/></g><g id="accents"><circle cx="75" cy="50" r="10"/></g></svg>'
        variant, removed = omit_groups(svg, {"accents"})
        image = raster(variant, 100)
        self.assertEqual(removed, ["accents"])
        self.assertEqual(image.getpixel((75, 50))[3], 0)
        self.assertEqual(image.getpixel((20, 50))[3], 255)
        with tempfile.TemporaryDirectory() as temporary:
            source, target = Path(temporary)/"art.svg", Path(temporary)/"proof.png"
            source.write_text(svg, encoding="utf-8")
            original = source.read_bytes()
            receipt = proof(source, target, ["accents"])
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(receipt["variants"], 2)
            self.assertEqual(Image.open(target).size, (1120, 1065))

    def test_absent_optional_group_is_explicit_and_source_overwrite_is_rejected(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><circle cx="5" cy="5" r="3"/></svg>'
        with tempfile.TemporaryDirectory() as temporary:
            source, target = Path(temporary)/"art.svg", Path(temporary)/"proof.png"
            source.write_text(svg, encoding="utf-8")
            receipt = proof(source, target, ["accents"])
            self.assertEqual(receipt["missing_groups"], ["accents"])
            self.assertEqual(receipt["variants"], 1)
            with self.assertRaises(ValueError):
                proof(source, source)
            self.assertEqual(source.read_text(), svg)

    def test_active_source_cannot_be_hidden_to_bypass_validation(self):
        svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="8" height="8"/><g id="accents"><script>alert(1)</script></g></svg>'
        with tempfile.TemporaryDirectory() as temporary:
            source, target = Path(temporary)/"art.svg", Path(temporary)/"proof.png"
            source.write_text(svg, encoding="utf-8")
            with self.assertRaises(ValueError):
                proof(source, target, ["accents"])
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
'''

GUIDE = '''# Information and editing decisions

Use this guide when a short brief leaves the amount of detail open, or when a
drawing looks busy, generic or poorly joined. Choose techniques by the defect;
do not apply every operation to every drawing.

## Budget by function

Before drawing, distinguish required meaning, supporting structure and optional
accents. A requested opening, crossing relationship, code, facial feature or
series of marks is required meaning, even if it looks decorative. Supporting
structure makes those features belong to the same object. Optional accents
add atmosphere or rhythm but can be removed without changing what was requested.
Keep this decision to a few notes; do not invent a larger specification.

Allocate the strongest shape and clearest space to the focal subject. Give
annotations enough size to work, then reduce their competing contrast or area.
There is no universal number of labels, paths or details: keep everything needed
to identify, explain or navigate; omit invented facts and repeated information.
On a compact label, group related identifiers and keep the longest real string
clear. On an illustration, articulation and distinctive proportions may matter
more than a low element count. Simplicity must not erase character or connections.

## Select an editing operation

| Symptom | Operation | Preservation check |
| --- | --- | --- |
| Separate pieces do not form one body | Align related contours and build shared openings between neighboring masses | Preserve the subject's distinctive proportions and required articulation |
| Curves collide or look arbitrary | Use common anchors and tangent direction; choose a continuous join, an intentional corner, or a clear over/under crossing | A gap must clarify connectivity, not sever a requested connection |
| Dense black areas hide structure | Subtract meaningful channels or use compound-path holes; let some openings connect to the exterior | Check on a colored ground; white paint is opaque |
| Too many labels or rules compete | Remove redundant optional content, group related information, adjust relative weight | All requested information must remain readable at its intended size |
| Outline looks lumpy | Reduce unnecessary nodes locally and align adjacent curve handles | Keep extrema, corners and shared edges; do not globally smooth away identity |
| Printed line work looks fragile | Strengthen the principal ink shape and simplify competing details | Keep the trace or main relation dominant; do not thicken every mark equally |

Union fuses touching material; difference cuts it away. SVG evenodd compound
paths make nested holes, but overlapping holes can fill their overlap. Use a
self-contained mask for a reversible cut when compound geometry is awkward.
Clip paths constrain visibility rather than merging shapes. Keep a source copy
before destructive Boolean edits or outlining text. Available tools may differ;
direct editable SVG geometry is a complete fallback and needs no desktop editor.

## Compare before committing detail

When adding genuinely optional ornaments, place them in `<g id="accents">`.
Keep requested information and identifying structure outside that group. Do
not create optional marks just to use this workflow. Generate and open a proof:

```text
python <skill-root>/scripts/proof_svg.py artwork.svg --output proof.png --omit accents
```

The proof shows a large view, a 192-pixel view and a colored transparency inset.
If the optional group exists, a second column hides it only in a diagnostic
copy. If it does not exist, the receipt says so and shows one column. Use
`--small-size` (64..512) for an appropriate intended display size and
`--font-dir` when font reproducibility matters. The source SVG is never edited.

Keep optional content when it improves useful rhythm, identity or communication;
remove it when it consumes space without doing that work. If both versions look
generic, revise proportions, junctions or characteristic features rather than
adding decorations. A proof sheet cannot judge meaning or choose a winner.
Make the chosen changes in the editable SVG or recipe and render the final file.
The proof and any alternate files are working material, not extra deliverables.

## Basis and limits

These are applied design heuristics, not guarantees of aesthetic quality:
[information sufficiency](https://www.nngroup.com/articles/aesthetic-minimalist-design/),
[visual hierarchy](https://www.nngroup.com/articles/visual-hierarchy-ux-definition/),
[perceptual grouping](https://assets.interaction-design.org/literature/article/laws-of-proximity-uniform-connectedness-and-continuation-gestalt-principles-2),
[controlled path simplification](https://helpx.adobe.com/illustrator/desktop/draw-shapes-and-paths/modify-paths/manually-simplify-paths.html),
[reversible editing](https://helpx.adobe.com/ca/photoshop/using/nondestructive-editing.html),
and [SVG fill semantics](https://www.w3.org/TR/SVG2/painting.html#FillRuleProperty).
The workflow works offline; these links explain provenance and are not runtime
dependencies. It contains no reference artwork or recovered geometry.
'''


def main():
    root = REPO / 'evaluations/runs' / sys.argv[1]
    parent = root / 'inputs/b/svg-brief-design'
    assert parent.is_dir() and not (root / 'started-b.json').exists()
    main_text = (parent / 'SKILL.md').read_text(encoding='utf-8')
    old = 'read [purpose and construction](references/construction-decisions.md) before'
    assert old in main_text
    route = '''
When the amount of detail is unspecified, read
[references/information-editing.md](references/information-editing.md) before
choosing it. Separate required meaning, supporting structure and optional
accents; preserve recognition before reducing detail. For optional ornament,
use the reversible proof there to compare its presence and absence. Inspect
the small view and colored inset before choosing the final version. Use the
actual linked file paths; link titles are not alternative filenames.
'''
    plan = {'operator':'information-roles-and-reversible-proof',
        'hypothesis':'Use semantic information roles and a deterministic multiscale/transparency/optional-group proof to choose useful detail while preserving required meaning. Preserve all existing construction generators and the frozen evaluator. Align one ambiguous link label with its actual path. Estimate the combined bundle, not an isolated causal effect.',
        'development_evidence':['research.md'],
        'files':{
            'SKILL.md':[{'replace':old,'with':'read [references/construction-decisions.md](references/construction-decisions.md) before'},
                        {'replace':'## Build a useful base','with':route+'\n## Build a useful base'}],
            'references/information-editing.md':[{'append':GUIDE}],
            'scripts/proof_svg.py':[{'append':PROOF}],
            'scripts/test_proof_svg.py':[{'append':TESTS}]}}
    uv = str(Path('C:/Users/villa/AppData/Local/Programs/Python/Python314/Scripts/uv.EXE'))
    plan['validation_commands'] = [{'id':name,'argv':[uv,'run','--script',f'scripts/{script}'],'timeoutSeconds':180}
        for name, script in [('scaffold-regressions','test_scaffold.py'),('proof-invariants','test_proof_svg.py')]]
    with (root / 'mutation-c.json').open('x',encoding='utf-8') as handle:
        json.dump(plan,handle,indent=2)
    print(json.dumps({'plan':'c','files':list(plan['files']),'private_evidence_used':False}))


if __name__ == '__main__': main()
