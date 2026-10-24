#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.64.1", "pillow==13.0.0"]
# ///
"""Independently verify the Reflex XY paired-colorset gallery and exports.

Run with the project Python environment or uv. Outputs remain in the project
artifact directory. The verifier reads the canonical repository palette file,
not the gallery's reported color values, to check actual exported SVG paints.
"""

from __future__ import annotations

import argparse
import contextlib
import functools
import hashlib
import io
import json
import re
import threading
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright


MECHANISMS = ("category-scatter", "trend-lines", "grouped-bars", "histogram", "heatmap", "dense-scatter")
EXPECTED_IDS = {f"reflex-xy-{mechanism}-cs{variant}" for mechanism in MECHANISMS for variant in (1, 2)}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


@contextlib.contextmanager
def serve(root):
    handler = functools.partial(QuietHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def normalized_color(value):
    value = value.strip().lower()
    if value in {"none", "transparent", "currentcolor", "inherit", "initial", "unset"} or value.startswith("url("):
        return None
    named = {"black": "#000000", "white": "#ffffff"}
    if value in named:
        return named[value]
    if re.fullmatch(r"#[0-9a-f]{3}", value):
        return "#" + "".join(channel * 2 for channel in value[1:])
    if re.fullmatch(r"#[0-9a-f]{6}", value):
        return value
    match = re.fullmatch(r"rgba?\(([^)]+)\)", value)
    if match:
        channels = re.split(r"[\s, /]+", match.group(1).strip())
        if len(channels) == 4 and float(channels[3]) == 0:
            return None
        rgb = [round(float(channel[:-1]) * 2.55) if channel.endswith("%") else round(float(channel)) for channel in channels[:3]]
        return "#" + "".join(f"{channel:02x}" for channel in rgb)
    return value


def inspect_svg(path, allowed):
    root = ET.parse(path).getroot()
    paints = Counter()
    text_labels = []
    geometry = []
    geometric_attributes = {"d", "points", "x", "y", "x1", "x2", "y1", "y2", "width", "height", "rx", "ry", "r", "cx", "cy", "transform", "viewBox"}
    for element in root.iter():
        local_name = element.tag.rsplit("}", 1)[-1]
        geometry.append([local_name, {key: value for key, value in element.attrib.items() if key in geometric_attributes},
                         "".join(element.itertext()).strip() if local_name == "text" else ""])
        if local_name == "text":
            text_labels.append("".join(element.itertext()).strip())
        declarations = dict(element.attrib)
        declarations.update(dict(re.findall(r"([\w-]+)\s*:\s*([^;]+)", element.attrib.get("style", ""))))
        for property_name in ("fill", "stroke", "stop-color", "color", "flood-color"):
            if property_name in declarations:
                color = normalized_color(declarations[property_name])
                if color:
                    paints[color] += 1
        if local_name == "style":
            for value in re.findall(r"(?:fill|stroke|stop-color|color|flood-color)\s*:\s*([^;}]+)", element.text or ""):
                color = normalized_color(value)
                if color:
                    paints[color] += 1
    return {
        "path": str(path), "width": root.attrib.get("width"), "height": root.attrib.get("height"),
        "paints": dict(paints), "unknown_paints": sorted(set(paints) - allowed),
        "text_count": len(text_labels), "text_labels": text_labels,
        "pattern_id": root.attrib.get("data-pattern-id"), "colorset": root.attrib.get("data-colorset"),
        "geometry_sha256": hashlib.sha256(json.dumps(geometry, sort_keys=True).encode()).hexdigest(),
    }


def image_stats(data, allowed=None):
    with Image.open(io.BytesIO(data)) as image:
        rgb = image.convert("RGB")
        stats = ImageStat.Stat(rgb)
        histogram = Counter(rgb.get_flattened_data())
        exact_palette_counts = {}
        if allowed:
            for color in sorted(allowed):
                pixel = tuple(int(color[index:index + 2], 16) for index in (1, 3, 5))
                if histogram[pixel]:
                    exact_palette_counts[color] = histogram[pixel]
        return {
            "width": rgb.width, "height": rgb.height,
            "stddev": [round(value, 3) for value in stats.stddev],
            "distinct_colors": len(histogram), "palette_pixel_counts": exact_palette_counts,
            "nonblank": rgb.width >= 100 and rgb.height >= 100 and max(stats.stddev) >= 3 and len(histogram) >= 10,
        }


def launch_browser(playwright, result):
    for options in ({"channel": "msedge"}, {"channel": "chrome"}, {}):
        try:
            browser = playwright.chromium.launch(headless=True, chromium_sandbox=True, **options)
            result["browser"] = options.get("channel", "bundled chromium")
            return browser
        except Exception as error:
            result["browser_launch_attempts"].append({"options": options, "error": str(error).splitlines()[0]})
    raise RuntimeError("No Chromium browser could launch.")


def inspect_links(page, root, base_url, result, remote=False):
    references = page.locator("a[href], img[src]").evaluate_all("elements => elements.map(element => ({url: element.href || element.src, label: element.textContent.trim() || element.alt || element.tagName}))")
    unique = {}
    for reference in references:
        url = urllib.parse.urldefrag(reference["url"])[0]
        if url:
            unique[url] = reference["label"]
    for url, label in unique.items():
        if url.startswith(base_url) and not remote:
            relative = urllib.parse.unquote(urllib.parse.urlsplit(url).path.lstrip("/"))
            path = (root / relative).resolve()
            if path.is_dir():
                path /= "index.html"
            result["links"].append({"url": url, "label": label, "local": True, "exists": path.is_relative_to(root) and path.is_file()})
        elif url.startswith(("https://", "http://")):
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "reflex-xy-gallery-validator/1.0"})
                with urllib.request.urlopen(request, timeout=25) as response:
                    status = response.status
                result["links"].append({"url": url, "label": label, "status": status, "exists": status < 400})
            except Exception as error:
                result["links"].append({"url": url, "label": label, "exists": False, "error": str(error)})


def visible_ids(page):
    return page.locator("article[data-pattern-id]:visible").evaluate_all("elements => elements.map(element => element.dataset.patternId)")


def wait_for_canvas(frame):
    canvas = frame.locator("canvas").first
    canvas.wait_for(state="visible", timeout=45000)
    frame.wait_for_timeout(500)
    return canvas


def verify_browser(root, route, manifest, output, palettes, result, public_base_url=None):
    server = contextlib.nullcontext(public_base_url) if public_base_url else serve(root)
    with server as base_url, sync_playwright() as playwright:
        browser = launch_browser(playwright, result)
        try:
            context = browser.new_context(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
            page = context.new_page()
            page.on("console", lambda message: result["console_errors"].append(message.text) if message.type == "error" else None)
            page.on("pageerror", lambda error: result["page_errors"].append(str(error)))

            def route_request(request_route):
                url = request_route.request.url
                if url.startswith(("https://", "http://")) and not url.startswith(base_url):
                    result["external_browser_requests"].append(url)
                    request_route.abort()
                else:
                    request_route.continue_()

            context.route("**/*", route_request)
            gallery_url = urllib.parse.urljoin(base_url, route.strip("/") + "/")
            page.goto(gallery_url, wait_until="networkidle", timeout=45000)
            result["gallery_url"] = gallery_url
            result["dom_ids"] = page.locator("article[data-pattern-id]").evaluate_all("elements => elements.map(element => element.dataset.patternId)")
            inspect_links(page, root, base_url, result, remote=bool(public_base_url))

            for name, viewport in (("desktop", {"width": 1440, "height": 1000}), ("mobile", {"width": 390, "height": 844})):
                page.set_viewport_size(viewport)
                for filter_name in ("colorset1", "colorset2", "all"):
                    page.locator(f'button[data-filter="{filter_name}"]').click()
                    page.wait_for_timeout(150)
                    for preview in page.locator("article:visible img.chart-preview").all():
                        preview.scroll_into_view_if_needed()
                        loaded = preview.evaluate("""async image => {
                            if (image.complete) return image.naturalWidth > 0;
                            return await Promise.race([
                                new Promise(resolve => { image.addEventListener('load', () => resolve(image.naturalWidth > 0), {once:true}); image.addEventListener('error', () => resolve(false), {once:true}); }),
                                new Promise(resolve => setTimeout(() => resolve(false), 10000))
                            ]);
                        }""")
                        if not loaded:
                            result["errors"].append(f"A lazy preview image failed to load: {preview.get_attribute('src')}")
                    page.evaluate("scrollTo({top:0,left:0,behavior:'instant'})")
                    page.wait_for_timeout(80)
                    ids = visible_ids(page)
                    expected = EXPECTED_IDS if filter_name == "all" else {identifier for identifier in EXPECTED_IDS if identifier.endswith("cs" + filter_name[-1])}
                    overflow = page.evaluate("({scroll: document.documentElement.scrollWidth, viewport: innerWidth})")
                    screenshot = output / f"gallery-{name}-{filter_name}.png"
                    page.screenshot(path=str(screenshot), full_page=(name == "mobile" and filter_name != "all"))
                    result["responsive_filters"].append({"viewport": name, "filter": filter_name, "ids": ids,
                        "passed": set(ids) == expected and len(ids) == len(expected) and overflow["scroll"] <= overflow["viewport"] + 1,
                        "overflow": overflow, "screenshot": str(screenshot)})

            page.set_viewport_size({"width": 1440, "height": 1000})
            page.locator('button[data-filter="all"]').click()
            for identifier in ("reflex-xy-category-scatter-cs1", "reflex-xy-trend-lines-cs2"):
                card = page.locator(f'article[data-pattern-id="{identifier}"]')
                card.locator('button[data-action="explore"]').click()
                iframe = page.locator("iframe")
                iframe.wait_for(state="visible", timeout=15000)
                frame = iframe.element_handle().content_frame()
                canvas = wait_for_canvas(frame)
                result["explore_frames"].append({"id": identifier, "count": iframe.count(), "src": iframe.get_attribute("src"),
                    "canvas": image_stats(canvas.screenshot(type="png")), "passed": iframe.count() == 1})
            page.screenshot(path=str(output / "gallery-desktop-explore.png"), full_page=False)

            for item in manifest["items"]:
                chart_page = context.new_page()
                chart_page.on("console", lambda message: result["console_errors"].append(message.text) if message.type == "error" else None)
                chart_page.on("pageerror", lambda error: result["page_errors"].append(str(error)))
                chart_url = urllib.parse.urljoin(gallery_url, item["html"])
                chart_page.goto(chart_url, wait_until="networkidle", timeout=45000)
                canvas = wait_for_canvas(chart_page)
                image_before = canvas.screenshot(type="png")
                box = canvas.bounding_box()
                chart_page.mouse.move(box["x"] + box["width"] * 0.5, box["y"] + box["height"] * 0.5)
                chart_page.mouse.wheel(0, -180)
                chart_page.wait_for_timeout(250)
                image_after = canvas.screenshot(type="png")
                screenshot = output / f"chart-{item['id']}.png"
                chart_page.screenshot(path=str(screenshot), full_page=True)
                result["interactive_charts"].append({"id": item["id"], "url": chart_url,
                    "canvas": image_stats(image_before, palettes[item["colorset"]]),
                    "wheel_changes_canvas": hashlib.sha256(image_before).digest() != hashlib.sha256(image_after).digest(),
                    "screenshot": str(screenshot)})
                chart_page.close()
            for item in manifest["items"]:
                identifier = item["id"]
                mobile_page = context.new_page()
                mobile_page.set_viewport_size({"width": 390, "height": 844})
                mobile_page.on("console", lambda message: result["console_errors"].append(message.text) if message.type == "error" else None)
                mobile_page.on("pageerror", lambda error: result["page_errors"].append(str(error)))
                mobile_page.goto(urllib.parse.urljoin(gallery_url, item["html"]), wait_until="networkidle", timeout=45000)
                canvas = wait_for_canvas(mobile_page)
                screenshot = output / f"mobile-chart-{identifier}.png"
                mobile_page.screenshot(path=str(screenshot), full_page=True)
                overflow = mobile_page.evaluate("({scroll: document.documentElement.scrollWidth, viewport: innerWidth})")
                outside_text = mobile_page.locator("[data-xy-slot]").evaluate_all("""elements => elements.filter(element => {
                    const box = element.getBoundingClientRect(), style = getComputedStyle(element);
                    return !element.children.length && element.textContent.trim() && box.width > 1 && box.height > 1 && style.display !== 'none' && style.visibility === 'visible' && Number(style.opacity) > 0 && (box.top < -1 || box.left < -1 || box.right > innerWidth + 1);
                }).map(element => ({slot: element.dataset.xySlot, text: element.textContent, bounds: element.getBoundingClientRect().toJSON()}))""")
                result["mobile_charts"].append({"id": identifier, "overflow": overflow,
                    "canvas": image_stats(canvas.screenshot(type="png"), palettes[item["colorset"]]), "screenshot": str(screenshot),
                    "text_outside_viewport": outside_text,
                    "passed": overflow["scroll"] <= overflow["viewport"] + 1 and not outside_text})
                mobile_page.close()
            context.close()
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pages-root", default="dist/pages")
    parser.add_argument("--route", default="examples/reflex-xy-colorsets")
    parser.add_argument("--output-dir", default="projects/reflex-xy/artifacts/colorset-gallery-review")
    parser.add_argument("--base-url", help="Optional live Pages root URL, such as https://gvillarroel.github.io/skills/.")
    args = parser.parse_args()
    repository = Path(__file__).resolve().parents[3]
    root = Path(args.pages_root).resolve()
    output = Path(args.output_dir).resolve()
    gallery = root / args.route
    output.mkdir(parents=True, exist_ok=True)
    result = {"schema_version": 1, "passed": False, "browser_launch_attempts": [], "console_errors": [], "page_errors": [],
        "external_browser_requests": [], "responsive_filters": [], "explore_frames": [], "interactive_charts": [], "mobile_charts": [],
        "links": [], "svgs": [], "pngs": [], "errors": []}
    try:
        if args.base_url:
            public_base_url = args.base_url.rstrip("/") + "/"
            if urllib.parse.urlsplit(public_base_url).scheme not in {"https", "http"}:
                raise ValueError("The public base URL must use HTTPS or HTTP.")
            gallery_url = urllib.parse.urljoin(public_base_url, args.route.strip("/") + "/")
            gallery = output / "published-assets"
            gallery.mkdir(parents=True, exist_ok=True)
            result["public_downloads"] = []

            def download(relative):
                destination = (gallery / relative).resolve()
                if not destination.is_relative_to(gallery):
                    raise ValueError(f"Published asset escapes its download directory: {relative}")
                url = urllib.parse.urljoin(gallery_url, relative)
                request = urllib.request.Request(url, headers={"User-Agent": "reflex-xy-gallery-validator/1.0"})
                with urllib.request.urlopen(request, timeout=45) as response:
                    data = response.read()
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                result["public_downloads"].append({"url": url, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})

            download("manifest.json")
            manifest = json.loads((gallery / "manifest.json").read_text(encoding="utf-8"))
            paths = {"index.html", "source/colorsets.json", "source/xy_colorsets.py", "source/gallery.html", "source/patterns.json"}
            paths.update(item["svg"] for item in manifest["items"])
            paths.update(item["source"] for item in manifest["items"])
            for relative in sorted(paths):
                download(relative)
        else:
            public_base_url = None
        manifest = json.loads((gallery / "manifest.json").read_text(encoding="utf-8"))
        if public_base_url and (root / args.route / "manifest.json").is_file():
            local_manifest = json.loads((root / args.route / "manifest.json").read_text(encoding="utf-8"))
            result["published_manifest_matches_local_release"] = manifest == local_manifest
            if not result["published_manifest_matches_local_release"]:
                result["errors"].append("The public manifest does not match the locally verified release manifest.")
        if public_base_url:
            catalog_request = urllib.request.Request(urllib.parse.urljoin(public_base_url, "example-catalog.json"), headers={"User-Agent": "reflex-xy-gallery-validator/1.0"})
            with urllib.request.urlopen(catalog_request, timeout=45) as response:
                catalog_text = response.read().decode("utf-8")
            index_request = urllib.request.Request(public_base_url, headers={"User-Agent": "reflex-xy-gallery-validator/1.0"})
            with urllib.request.urlopen(index_request, timeout=45) as response:
                index_text = response.read().decode("utf-8")
            (output / "published-catalog.json").write_text(catalog_text, encoding="utf-8")
            (output / "published-index.html").write_text(index_text, encoding="utf-8")
        else:
            catalog_text = (root / "example-catalog.json").read_text(encoding="utf-8") if (root / "example-catalog.json").is_file() else "[]"
            index_text = (root / "index.html").read_text(encoding="utf-8") if (root / "index.html").is_file() else ""
        catalog_matches = [entry for entry in json.loads(catalog_text) if entry.get("id") == "reflex-xy-colorsets"]
        result["catalog_discoverability"] = {
            "entries": catalog_matches,
            "index_card": bool(re.search(r'''data-example-id=["']reflex-xy-colorsets["']''', index_text)),
            "index_route": args.route.strip("/") + "/" in index_text,
        }
        if len(catalog_matches) != 1 or not result["catalog_discoverability"]["index_card"] or not result["catalog_discoverability"]["index_route"]:
            result["errors"].append("The main Pages catalog and index do not uniquely expose the colorset gallery.")
        canonical_profile = json.loads((repository / "docs/colorsets.json").read_text(encoding="utf-8"))
        palettes = {name: set(profile["allowed"]) for name, profile in canonical_profile["colorsets"].items()}
        bundle_profile = json.loads((repository / "skills/reflex-xy/assets/palettes/colorsets.json").read_text(encoding="utf-8"))
        result["palette_snapshot_matches_canonical"] = bundle_profile == canonical_profile
        if not result["palette_snapshot_matches_canonical"]:
            result["errors"].append("Skill palette snapshot does not exactly match docs/colorsets.json.")
        published_profile = json.loads((gallery / "source/colorsets.json").read_text(encoding="utf-8"))
        result["published_palette_snapshot_matches_canonical"] = published_profile == canonical_profile
        if not result["published_palette_snapshot_matches_canonical"]:
            result["errors"].append("Published palette snapshot does not exactly match docs/colorsets.json.")
        result["canonical_palette_sizes"] = {name: len(colors) for name, colors in palettes.items()}
        result["manifest_ids"] = [item["id"] for item in manifest["items"]]
        if set(result["manifest_ids"]) != EXPECTED_IDS or len(result["manifest_ids"]) != 12:
            result["errors"].append("Manifest does not contain exactly the expected twelve canonical IDs.")
        for item in manifest["items"]:
            svg = inspect_svg(gallery / item["svg"], palettes[item["colorset"]])
            svg["id"] = item["id"]
            result["svgs"].append(svg)
            if svg["pattern_id"] != item["id"] or svg["colorset"] != item["colorset"]:
                result["errors"].append(f"Native SVG metadata does not match the manifest in {item['id']}.")
            if svg["unknown_paints"]:
                result["errors"].append(f"Undeclared SVG paint in {item['id']}: {svg['unknown_paints']}")
            if not svg["text_count"]:
                result["errors"].append(f"Missing SVG text labels in {item['id']}.")
            png_path = (gallery / item["svg"]).with_suffix(".png")
            if png_path.is_file():
                result["pngs"].append({"id": item["id"], **image_stats(png_path.read_bytes(), palettes[item["colorset"]])})
        result["paired_geometry"] = []
        for mechanism in MECHANISMS:
            pair = [item for item in result["svgs"] if item["id"].startswith(f"reflex-xy-{mechanism}-cs")]
            same_geometry = len(pair) == 2 and pair[0]["geometry_sha256"] == pair[1]["geometry_sha256"]
            result["paired_geometry"].append({"mechanism": mechanism, "same_geometry": same_geometry})
            if not same_geometry:
                result["errors"].append(f"Paired colorsets change geometry or text in {mechanism}.")
        verify_browser(root, args.route, manifest, output, palettes, result, public_base_url=public_base_url)
        if set(result.get("dom_ids", [])) != EXPECTED_IDS or len(result.get("dom_ids", [])) != 12:
            result["errors"].append("Gallery DOM does not contain exactly the expected twelve canonical IDs.")
        if any(not item["passed"] for item in result["responsive_filters"]):
            result["errors"].append("A responsive viewport or colorset filter failed.")
        if any(not item["passed"] or not item["canvas"]["nonblank"] for item in result["explore_frames"]):
            result["errors"].append("Explore iframe uniqueness or canvas paint failed.")
        if any(not item["canvas"]["nonblank"] for item in result["interactive_charts"]):
            result["errors"].append("An interactive chart canvas is blank.")
        if any(not item["wheel_changes_canvas"] for item in result["interactive_charts"]):
            result["errors"].append("A chart wheel interaction did not visibly change its canvas.")
        if any(not item["passed"] or not item["canvas"]["nonblank"] for item in result["mobile_charts"]):
            result["errors"].append("A mobile interactive chart is blank or overflows its viewport.")
        if any(not item["nonblank"] for item in result["pngs"]):
            result["errors"].append("A PNG export is blank.")
        if any(not item["exists"] for item in result["links"]):
            result["errors"].append("A gallery documentation, source, or asset link is broken.")
        if result["console_errors"] or result["page_errors"] or result["external_browser_requests"]:
            result["errors"].append("Browser reported JavaScript errors or attempted an external request.")
    except Exception as error:
        result["errors"].append(str(error))
    result["passed"] = not result["errors"]
    report = output / "gallery-verification.json"
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"passed": result["passed"], "errors": result["errors"], "svgs": len(result["svgs"]),
        "interactive_charts": len(result["interactive_charts"]), "report": str(report)}))
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
