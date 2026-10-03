#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["resvg-py==0.2.6", "Pillow==11.3.0", "defusedxml==0.7.1"]
# ///
"""Check original scaffold geometry and output contracts with an independent renderer."""
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from PIL import Image
import resvg_py
import scaffold
from render_svg import render


def rgba(svg):
    return Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg, width=480))).convert("RGBA")


class ScaffoldTests(unittest.TestCase):
    def test_renderer_rejects_custom_off_palette_gradient(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "invalid.svg"
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80"><defs><linearGradient id="g"><stop stop-color="#123456"/></linearGradient></defs><rect width="80" height="80" fill="url(#g)"/></svg>')
            with self.assertRaisesRegex(ValueError, "violates colorset1"):
                render(source, Path(directory) / "preview.png")

    def test_palette_applies_to_nested_details_and_underlay(self):
        recipe = scaffold.defaults("radial")
        self.assertEqual(ET.fromstring(scaffold.build(recipe)).get("data-colorset"), "colorset1")
        recipe["style"]["color"] = "#007298"
        with self.assertRaises(ValueError):
            scaffold.build(recipe)
        recipe["style"]["colorset"] = "colorset2"
        scaffold.build(recipe)
        recipe["details"] = [{"tag": "g", "children": [{"tag": "path", "attrs": {"fill": "#123456", "d": "M0 0L1 1"}}]}]
        with self.assertRaises(ValueError):
            scaffold.build(recipe)
        recipe["details"] = []
        recipe["underlay"] = [{"tag": "rect", "attrs": {"fill": "rgb(0, 0, 0)", "width": 50, "height": 50}}]
        with self.assertRaises(ValueError):
            scaffold.build(recipe)

    def test_orbit_reserves_empty_center(self):
        recipe = scaffold.defaults("orbit")
        image = rgba(scaffold.build(recipe))
        alpha = image.getchannel("A")
        self.assertIsNone(alpha.crop((150, 150, 330, 330)).getbbox())
        self.assertIsNotNone(alpha.getbbox())
        root = ET.fromstring(scaffold.build(recipe))
        bands = [e for e in root.iter() if e.get("id", "").startswith("orbit-band-")]
        self.assertEqual(len(bands), 5)
        self.assertTrue(all(e.get("stroke") == "none" for e in bands))

    def test_orbit_boundary_and_parameter_extremes(self):
        for n, coverage, inner, taper, direction in [(3,.25,.2,.5,1),(24,1.8,.9,3,-1),(8,1.5,.55,1,1)]:
            recipe = scaffold.defaults("orbit")
            recipe["parameters"].update(count=n,coverage=coverage,inner_ratio=inner,taper=taper,direction=direction)
            alpha = rgba(scaffold.build(recipe)).getchannel("A")
            box = alpha.getbbox()
            self.assertIsNotNone(box)
            self.assertTrue(20 <= box[0] < box[2] <= 460 and 20 <= box[1] < box[3] <= 460)
            self.assertEqual(alpha.getpixel((240,240)),0)

    def test_orbit_rejects_invalid_geometry(self):
        for key,value in [("inner_ratio",0),("inner_ratio",1),("count",3.5),("coverage",2),("taper",float("nan")),("direction",0)]:
            recipe = scaffold.defaults("orbit")
            recipe["parameters"][key]=value
            with self.assertRaises(ValueError): scaffold.build(recipe)

    def test_deterministic_and_visible(self):
        for kind in scaffold.DRAW:
            with self.subTest(kind=kind):
                recipe = scaffold.defaults(kind)
                if kind == "composition":
                    recipe["parameters"]["items"] = [{"kind": "globe", "box": [40, 40, 180, 300]}, {"kind": "radial", "box": [240, 180, 180, 220]}]
                first = scaffold.build(recipe)
                self.assertEqual(first, scaffold.build(recipe))
                image = rgba(first)
                bounds = image.getchannel("A").getbbox()
                self.assertIsNotNone(bounds)
                self.assertGreater(bounds[0], 0)
                self.assertGreater(bounds[1], 0)
                self.assertLess(bounds[2], image.width)
                self.assertLess(bounds[3], image.height)

    def test_radial_opening_is_transparent(self):
        for n in (3, 7, 16):
            recipe = scaffold.defaults("radial")
            recipe["parameters"]["count"] = n
            image = rgba(scaffold.build(recipe))
            self.assertEqual(image.getpixel((240, 240))[3], 0)
            alpha = image.getchannel("A")
            self.assertGreater(sum(alpha.getdata()), 480 * 480 * 255 * .05)

    def test_flow_ports_and_exact_text(self):
        for direction in ("horizontal", "vertical"):
            recipe = scaffold.defaults("flow")
            recipe["canvas"].update(width=800, height=800)
            names = ["A & B", "Review <draft>", "Done"]
            recipe["parameters"].update(labels=names, direction=direction)
            root = ET.fromstring(scaffold.build(recipe))
            self.assertEqual([e.text for e in root.iter() if e.tag.endswith("}text")], names)
            ids = {e.get("id"): e for e in root.iter() if e.get("id")}
            for i in range(2):
                before, after, edge = ids[f"node-{i}"], ids[f"node-{i+1}"], ids[f"edge-{i}-{i+1}-shaft"]
                axis, extent = ("x", "width") if direction == "horizontal" else ("y", "height")
                self.assertAlmostEqual(float(edge.get(axis + "1")), float(before.get(axis)) + float(before.get(extent)), places=4)
                self.assertAlmostEqual(float(edge.get(axis + "2")), float(after.get(axis)), places=4)

    def test_panel_retains_requested_strings(self):
        recipe = scaffold.defaults("panel")
        recipe["parameters"].update(title="MUESTRA 07", rows=["LAB-A"], header="")
        root = ET.fromstring(scaffold.build(recipe))
        text = [e for e in root.iter() if e.tag.endswith("}text")]
        self.assertEqual([e.text for e in text], ["MUESTRA 07", "LAB-A"])
        self.assertGreater(float(text[0].get("font-size")), float(text[1].get("font-size")))
        self.assertLess(float(text[0].get("y")), float(text[1].get("y")))

    def test_nonfinite_and_duplicate_ids_fail(self):
        recipe = scaffold.defaults("radial")
        recipe["canvas"]["width"] = float("nan")
        with self.assertRaises(ValueError):
            scaffold.build(recipe)

        recipe = scaffold.defaults("blank")
        recipe["details"] = [{"tag": "circle", "attrs": {"id": "structure", "r": 3}}]
        with self.assertRaises(ValueError):
            scaffold.build(recipe)

    def test_rotated_frond_stays_inside_canvas(self):
        for angle in (-130, -45, 40, 90):
            recipe = scaffold.defaults("frond")
            recipe["parameters"].update(rotation=angle, bend=.6, spread=.47)
            image = rgba(scaffold.build(recipe))
            bounds = image.getchannel("A").getbbox()
            self.assertGreaterEqual(bounds[0], 26)
            self.assertGreaterEqual(bounds[1], 26)
            self.assertLessEqual(bounds[2], 454)
            self.assertLessEqual(bounds[3], 454)

    def test_composition_namespaces_and_bounds(self):
        recipe = scaffold.defaults("composition")
        recipe["parameters"]["items"] = [{"id": "one", "kind": "frond", "box": [30, 30, 180, 400]}, {"id": "two", "kind": "frond", "box": [240, 30, 180, 400]}]
        root = ET.fromstring(scaffold.build(recipe))
        ids = [e.get("id") for e in root.iter() if e.get("id")]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("one-stem", ids)
        self.assertIn("two-stem", ids)
        recipe["parameters"]["items"][0]["box"][0] = -2
        with self.assertRaises(ValueError):
            scaffold.build(recipe)

    def test_invalid_detail_and_small_text_fail(self):
        recipe = scaffold.defaults("blank")
        recipe["details"] = [{"tag": "image", "attrs": {"href": "https://example.com/x.svg"}}]
        with self.assertRaises(ValueError):
            scaffold.build(recipe)
        recipe = scaffold.defaults("flow")
        recipe["parameters"]["labels"] = ["x" * 200, "B"]
        with self.assertRaises(ValueError):
            scaffold.build(recipe)

    def test_cli_paths_and_no_init_overwrite(self):
        with tempfile.TemporaryDirectory(prefix=".svg-test-", dir=Path.cwd()) as raw:
            folder = Path(raw).resolve()
            self.assertTrue(folder.is_relative_to(Path.cwd().resolve()))
            recipe, output = folder / "recipe with spaces.json", folder / "nested/artwork.svg"
            argv = [sys.executable, str(Path(scaffold.__file__).resolve()), "init", "flow", "--recipe", str(recipe), "--output", str(output)]
            first = subprocess.run(argv, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            before = output.read_bytes()
            self.assertNotEqual(subprocess.run(argv, capture_output=True).returncode, 0)
            self.assertEqual(output.read_bytes(), before)
            data = json.loads(recipe.read_text())
            data["parameters"]["labels"] = ["Source", "Destination"]
            recipe.write_text(json.dumps(data))
            rebuilt = subprocess.run([sys.executable, str(Path(scaffold.__file__).resolve()), "build", str(recipe), "--output", str(output)], capture_output=True, text=True)
            self.assertEqual(rebuilt.returncode, 0, rebuilt.stderr)
            self.assertIn("Destination", output.read_text())

    def test_preview_and_external_resource_rejection(self):
        with tempfile.TemporaryDirectory(prefix=".svg-test-", dir=Path.cwd()) as raw:
            folder = Path(raw).resolve()
            self.assertTrue(folder.is_relative_to(Path.cwd().resolve()))
            source, preview = folder / "source.svg", folder / "preview.png"
            source.write_text(scaffold.build(scaffold.defaults("radial")))
            result = render(source, preview, 320)
            self.assertEqual(result["size"], [320, 320])
            self.assertFalse(result["touches_canvas_edge"])
            with Image.open(preview) as image:
                self.assertEqual(image.format, "PNG")
            source.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><image href="https://example.com/x.png"/></svg>')
            with self.assertRaises(ValueError):
                render(source, preview)


if __name__ == "__main__":
    unittest.main()
