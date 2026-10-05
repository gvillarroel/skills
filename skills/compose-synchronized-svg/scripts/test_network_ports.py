#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression tests for deterministic ports in implicit dependency networks."""

from __future__ import annotations

import re
import json
import math
import sys
import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).parent))
import compose_synchronized_svg as composer  # noqa: E402
import compile_synchronized_svg_plan as compiler  # noqa: E402
import scaffold_synchronized_svg as scaffold  # noqa: E402
from arrow_routing import overlaps, path_points  # noqa: E402


class NetworkPortTests(unittest.TestCase):
    @staticmethod
    def points(path: str) -> list[tuple[float, float]]:
        points = []
        x = y = 0.0
        for command, values in re.findall(r"([MHV])\s*([^MHV]+)", path):
            numbers = [float(item) for item in values.split()]
            if command == "M":
                x, y = numbers
            elif command == "H":
                x = numbers[0]
            else:
                y = numbers[0]
            points.append((x, y))
        return points

    def _render(self, label: str | None = None) -> str:
        ids = ["parent-a", "parent-b", "derived", "child-a", "child-b", "grandchild"]
        infos = [
            composer.BindingInfo(i, {"selector": "[data-role='value']", "channel": "text"}, "role", value_id, "text", float(i), float(i), "#1d4ed8", "count", (0, 10), str(i))
            for i, value_id in enumerate(ids)
        ]
        if label is not None:
            for info in infos:
                info.binding["label"] = label
        plan = {
            "concepts": [{"id": value_id, "domain": [0, 10]} for value_id in ids],
            "derived": [
                {"id": "derived", "dependsOn": ["parent-a", "parent-b"]},
                {"id": "child-a", "dependsOn": ["derived"]},
                {"id": "child-b", "dependsOn": ["derived"]},
                {"id": "grandchild", "dependsOn": ["derived", "parent-a"]},
            ],
        }
        module = {"id": "network", "region": [0, 0, 420, 400 if label is not None else 260], "claim": "Dependencies", "question": "How does this flow?"}
        return composer.render_network_family(plan, module, infos)

    def test_exact_edges_and_unique_fan_ports(self) -> None:
        svg = self._render()
        edges = re.findall(r'data-dependency-edge="([^"]+)"', svg)
        self.assertEqual(edges, ["parent-a:derived", "parent-b:derived", "derived:child-a", "derived:child-b", "parent-a:grandchild", "derived:grandchild"])
        paths = [node for node in ET.fromstring(svg).iter() if node.get("data-dependency-edge")]
        self.assertEqual(len(paths), 6)
        incoming = [self.points(path.get("d"))[-1][1] for path in paths if path.get("data-dependency-edge").endswith(":derived")]
        outgoing = [self.points(path.get("d"))[0][1] for path in paths if path.get("data-dependency-edge").startswith("derived:")]
        self.assertEqual(len(set(incoming)), 2)
        self.assertEqual(len(set(outgoing)), 3)
        self.assertIn('stroke="var(--ink)"', svg)
        self.assertIn('data-dependency-edge="parent-a:grandchild"', svg)

    def test_render_is_deterministic_and_paths_stay_in_body(self) -> None:
        first = self._render()
        self.assertEqual(first, self._render())
        root = ET.fromstring(first)
        nodes = {
            node.get("data-dependency-node"): tuple(float(node.get(key)) for key in ("x", "y", "width", "height"))
            for node in root.iter() if node.get("data-dependency-node")
        }
        self.assertEqual(len(nodes), 6)
        for edge in root.iter():
            if not edge.get("data-dependency-edge"):
                continue
            source, target = edge.get("data-dependency-edge").split(":")
            points = self.points(edge.get("d"))
            for x, y in points:
                self.assertGreaterEqual(x, 0)
                self.assertLessEqual(x, 420)
                self.assertGreaterEqual(y, 0)
                self.assertLessEqual(y, 154)
            # An arrow must approach the destination horizontally from its left.
            self.assertLess(points[-2][0], points[-1][0])
            self.assertEqual(points[-2][1], points[-1][1])
            self.assertLess(points[-1][0], nodes[target][0])
            for x, y in (points[0], points[-1]):
                node = nodes[source if (x, y) == points[0] else target]
                self.assertGreater(y, node[1])
                self.assertLess(y, node[1] + node[3])
            for node_id, (left, top, width, height) in nodes.items():
                if node_id in (source, target):
                    continue
                for (x1, y1), (x2, y2) in zip(points, points[1:]):
                    if y1 == y2:
                        intersects = top < y1 < top + height and max(min(x1, x2), left) < min(max(x1, x2), left + width)
                    else:
                        intersects = left < x1 < left + width and max(min(y1, y2), top) < min(max(y1, y2), top + height)
                    self.assertFalse(intersects, f"{source}:{target} crosses {node_id}")

    def test_fan_lanes_keep_full_arrowhead_approach(self) -> None:
        paths = [node for node in ET.fromstring(self._render()).iter() if node.get("data-dependency-edge")]
        for path in paths:
            points = path_points(path.get("d"))
            self.assertGreaterEqual(math.dist(points[-2], points[-1]), 8.0)
        verticals = [
            (a, b) for path in paths for a, b in zip(path_points(path.get("d")), path_points(path.get("d"))[1:])
            if a[0] == b[0] and a != b
        ]
        for index, (a, b) in enumerate(verticals):
            for c, d in verticals[index + 1:]:
                self.assertFalse(overlaps(a, b, c, d), f"Merged network lanes: {a,b} and {c,d}")

    def test_competing_module_routes_have_clear_lanes_and_terminal_runs(self) -> None:
        template = Path(__file__).parent.parent / "assets/templates/composition-brief.json"
        brief = json.loads(template.read_text(encoding="utf-8"))
        plan, _ = compiler.compile_brief(brief)
        self.assertEqual(plan["layout"]["gap"], 40)
        markup = scaffold.relationship_markup(plan)
        paths = [node for node in ET.fromstring(markup).iter() if node.get("class") == "relationship-path"]
        occupied = []
        for path in paths:
            points = path_points(path.get("d"))
            self.assertGreaterEqual(math.dist(points[0], points[1]), 10)
            self.assertGreaterEqual(math.dist(points[-2], points[-1]), 10)
            for a, b in zip(points, points[1:]):
                self.assertFalse(any(overlaps(a, b, c, d) for c, d in occupied))
            occupied.extend(zip(points, points[1:]))
        # A sparse composition retains the small baseline gap.
        brief["relationships"] = []
        sparse, _ = compiler.compile_brief(brief)
        self.assertEqual(sparse["layout"]["gap"], 24)

    def test_complete_labels_wrap_instead_of_ellipsizing(self) -> None:
        root = ET.fromstring(self._render())
        labels = {node.get("data-dependency-label"): " ".join(t.text or "" for t in node)
                  for node in root.iter() if node.get("data-dependency-label")}
        self.assertEqual(labels["grandchild"], "Role")
        self.assertFalse(any("…" in text for text in labels.values()))
        rendered = ET.fromstring(self._render("Processing capacity"))
        full = [" ".join(t.text or "" for t in node) for node in rendered.iter()
                if node.get("data-dependency-label")]
        self.assertTrue(full)
        self.assertTrue(all(text == "Processing capacity" for text in full))
        self.assertTrue(any(len(list(node)) == 2 for node in rendered.iter()
                            if node.get("data-dependency-label")))
        with self.assertRaisesRegex(ValueError, "without losing readability"):
            self._render("Long unabridged descriptive processing capacity measure")

    def test_true_crossings_have_local_bridges_without_changing_edges(self) -> None:
        root = ET.fromstring(self._render())
        bridges = [node for node in root.iter() if node.get("data-crossing-bridge")]
        self.assertTrue(bridges)
        tips = [path_points(node.get("d"))[-1] for node in root.iter() if node.get("data-dependency-edge")]
        for bridge in bridges:
            length = math.hypot(float(bridge.get("x2")) - float(bridge.get("x1")),
                                float(bridge.get("y2")) - float(bridge.get("y1")))
            self.assertEqual(length, 6)
            center = ((float(bridge.get("x1")) + float(bridge.get("x2"))) / 2,
                      (float(bridge.get("y1")) + float(bridge.get("y2"))) / 2)
            self.assertTrue(all(math.dist(center, tip) >= 8 for tip in tips), "Crossing gap would cover an arrowhead")
        self.assertEqual(len([node for node in root.iter() if node.get("data-dependency-edge")]), 6)


if __name__ == "__main__":
    unittest.main()
