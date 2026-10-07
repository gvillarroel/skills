#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise supported semantic contracts and reject materially lossy inputs.

Run: uv run --script scripts/test_catalog.py
These are offline contract tests, not remote Lucid fidelity tests.
"""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

import native_catalog as catalog


class CatalogTests(unittest.TestCase):
    def valid(self, type_name, properties=None, width=100, height=60):
        return catalog.validate_properties(type_name, properties or {}, width, height)

    def invalid(self, type_name, properties, width=100, height=60):
        with self.assertRaises(ValueError):
            catalog.validate_properties(type_name, properties, width, height)

    def test_identity_exclusions_and_independent_specs(self):
        self.assertEqual(catalog.native_type("ellipse"), "circle")
        self.assertEqual(catalog.spec("ellipse")["alias"]["fidelity"], "approximation")
        for unsupported in ("image", "orgChart", "mindMap", "umlSequence", "assistedLayout", "entity", "class", "bpmnTask", "Ellipse", None):
            with self.subTest(type=unsupported), self.assertRaises(ValueError):
                catalog.native_type(unsupported)
        changed = catalog.spec("text")
        changed["forbidden_common"].clear()
        self.assertEqual(catalog.spec("text")["forbidden_common"], ["style"])
        for type_name in ("hotspot", "or", "summingJunction"):
            self.assertIn("text", catalog.spec(type_name)["forbidden_common"])
        for type_name in ("table", "swimLanes", "bpmnGroup", "bpmnPool", "namedContainer"):
            self.assertFalse(catalog.spec(type_name)["rotation_supported"])

    def test_primitive_outline_and_numeric_rejection(self):
        triangle = {"vertices": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 0.5, "y": 1}]}
        self.assertEqual(self.valid("flexiblePolygon", triangle), triangle)
        self.valid("polyStar", {"shape": {"numPoints": 5, "innerRadius": 0.4}})
        self.valid("cross", {"indent": {"x": 0.2, "y": 0.5}})
        self.valid("singleArrow", {"orientation": "up"})
        for vertices in (triangle["vertices"][:2], triangle["vertices"] * 34,
                         [{"x": 0, "y": 0}] * 3,
                         [*triangle["vertices"], triangle["vertices"][0]],
                         [{"x": -0.1, "y": 0}, *triangle["vertices"][1:]],
                         [{"x": 0, "y": 0}, {"x": 0.5, "y": 0.5}, {"x": 1, "y": 1}],
                         [{"x": 0, "y": 0}, {"x": 1, "y": 1}, {"x": 0, "y": 1}, {"x": 1, "y": 0}]):
            self.invalid("flexiblePolygon", {"vertices": vertices})
        self.invalid("polyStar", {"shape": {"numPoints": 5.5, "innerRadius": 0.4}})
        self.invalid("polyStar", {"shape": {"numPoints": 5, "innerRadius": 1.1}})
        self.invalid("cross", {"indent": {"x": 0.2}})
        for width in (True, "100", 0, -1, float("nan"), float("inf"), 10 ** 400):
            self.invalid("rectangle", {}, width=width)
        self.invalid("rectangle", {"fill": "#ffffff"})
        self.invalid("rectangle", {"svgPath": "M0,0 L1,1"})

    def test_flowchart_contracts(self):
        self.valid("predefinedProcess", {"sideWidth": 0.1})
        self.valid("braceNote", {"rightFacing": True, "braceWidth": 12})
        for type_name in ("process", "decision", "terminator", "data", "document", "database", "delay", "offPageLink", "connector"):
            self.assertEqual(self.valid(type_name), {})
        self.invalid("predefinedProcess", {})
        self.invalid("predefinedProcess", {"sideWidth": 0.34})
        self.invalid("predefinedProcess", {"sideWidth": True})
        self.invalid("braceNote", {"rightFacing": "right", "braceWidth": 12})

    def test_bpmn_enums_and_nested_participants(self):
        self.valid("bpmnActivity", {"activityType": "task", "taskType": "user", "activityMarker1": "parallelMI"})
        self.valid("bpmnEvent", {"eventGroup": "intermediate", "eventType": "message", "throwing": True})
        self.valid("bpmnGateway", {"gatewayType": "inclusive"})
        self.valid("bpmnDataObject", {"dataType": "collection"})
        participants = [{"text": "Vendor", "multipleParticipants": False}]
        self.valid("bpmnChoreography", {"choreographyType": "task", "participants": participants})
        self.invalid("bpmnActivity", {})
        self.invalid("bpmnActivity", {"activityType": "task", "taskType": "human"})
        self.invalid("bpmnEvent", {"eventGroup": "boundary"})
        self.invalid("bpmnEvent", {"eventGroup": "start", "throwing": 1})
        self.invalid("bpmnGateway", {"gatewayType": "and"})
        self.invalid("bpmnChoreography", {"choreographyType": "task", "participants": []})
        self.invalid("bpmnChoreography", {"choreographyType": "task", "participants": [{"text": "Vendor"}]})
        self.invalid("bpmnChoreography", {"choreographyType": "task", "participants": participants * 101})
        # Schema acceptance never certifies that every marker combination is valid BPMN.
        self.valid("bpmnEvent", {"eventGroup": "start", "throwing": True})

    @staticmethod
    def swimlanes(vertical=True):
        return {"vertical": vertical, "titleBar": {"height": 10, "verticalText": False},
                "lanes": [{"title": "A", "width": 40 if vertical else 30, "headerFill": "#abc", "laneFill": "#0000"},
                          {"title": "B", "width": 60 if vertical else 30, "headerFill": "#123456", "laneFill": "#12345678"}]}

    def test_lane_orientation_sum_and_title_space(self):
        self.valid("swimLanes", self.swimlanes())
        self.valid("swimLanes", self.swimlanes(False))
        self.valid("bpmnPool", {"title": "Pool", "lanes": [{"title": "Owner", "width": 100, "laneFill": "#000000"}]})
        invalid = self.swimlanes()
        invalid["lanes"][0]["width"] = 39
        self.invalid("swimLanes", invalid)
        invalid = self.swimlanes(False)
        invalid["titleBar"]["height"] = 100
        self.invalid("swimLanes", invalid)
        invalid = self.swimlanes()
        invalid["assistedLayout"] = True
        self.invalid("swimLanes", invalid)
        invalid = self.swimlanes()
        invalid["lanes"][0]["width"] = True
        self.invalid("swimLanes", invalid)
        self.invalid("bpmnPool", {"title": "Pool", "lanes": [{"title": "A", "width": 2, "laneFill": "#ffffff"}] * 51})
        self.invalid("diamondContainer", {"containerTitle": {"text": "Unsupported field"}})

    @staticmethod
    def table():
        return {"rowCount": 3, "colCount": 2,
                "cells": [{"xPosition": 0, "yPosition": 0, "mergeCellsRight": 1, "text": "Entity"},
                          {"xPosition": 0, "yPosition": 1, "text": "id (PK)"},
                          {"xPosition": 1, "yPosition": 1, "text": "uuid"},
                          {"xPosition": 0, "yPosition": 2, "mergeCellsRight": 1, "text": "Methods"}]}

    def test_editable_er_and_uml_table_grid(self):
        properties = self.table()
        self.assertEqual(self.valid("table", properties), properties)
        self.valid("table", {**properties, "userSpecifiedRows": [{"index": 0, "size": 10}, {"index": 1, "size": 20}, {"index": 2, "size": 30}],
                             "userSpecifiedCols": [{"index": 0, "size": 40}]})
        mutated = catalog.format_properties("table", self.valid("table", properties))
        mutated["cells"].clear()
        self.assertEqual(len(properties["cells"]), 4)
        for mutation in (
            {"rowCount": 0}, {"colCount": 2.5}, {"rowCount": True},
            {"cells": [*properties["cells"], {"xPosition": 1, "yPosition": 0}]},
            {"cells": [{"xPosition": 0, "yPosition": 0, "mergeCellsDown": 3}]},
            {"cells": [{"xPosition": 2, "yPosition": 0}]},
            {"cells": [{"xPosition": 0, "yPosition": 0, "mergeCellsRight": -1}]},
            {"cells": [{"xPosition": 0, "yPosition": 0, "style": {"stroke": "#fff"}}]},
            {"cells": [{"xPosition": 0, "yPosition": 0, "style": {"fill": {"type": "image", "url": "https://example.com/image"}}}]},
            {"userSpecifiedRows": [{"index": 3, "size": 10}]},
            {"userSpecifiedRows": [{"index": 0, "size": 10}, {"index": 0, "size": 10}]},
            {"userSpecifiedRows": [{"index": 0, "size": 60}]},
            {"userSpecifiedCols": [{"index": 0, "size": 40}, {"index": 1, "size": 40}]},
        ):
            self.invalid("table", {**properties, **mutation})

    def test_cloud_kind_literal_names_and_conflicts(self):
        self.valid("namedShape", {"className": "ArchAmazonEC2AWS2024"})
        self.valid("namedContainer", {"className": "VirtualPrivateCloudVPCAWS2024"})
        self.valid("namedShape", {"className": "VirtualMachineAzure2024"})
        self.valid("namedShape", {"className": "GCP2021CloudStorageIcon"})
        self.invalid("namedShape", {"className": "VirtualPrivateCloudVPCAWS2024"})
        self.invalid("namedContainer", {"className": "ArchAmazonEC2AWS2024"})
        for class_name in ("AmazonEC2AWS2024", "VirtualMachineAzure2021", "VirtualMachinesAzure2021", "PrivateEndpointAzure2021", "GCP2021CloudStorage", "AzureOpenAIAzure2021", True):
            self.invalid("namedShape", {"className": class_name})

    def test_every_catalog_type_and_cloud_class_has_a_usable_contract(self):
        with catalog.CATALOG_PATH.open(encoding="utf-8") as stream:
            data = json.load(stream)
        def sample(rule):
            if rule["kind"] == "boolean": return False
            if rule["kind"] == "string": return rule.get("enum", ["Source label"])[0]
            if rule["kind"] == "color": return "#ffffff"
            if rule["kind"] == "number": return rule.get("minimum", 1)
            if rule["kind"] == "array": return [sample(rule["items"]) for _ in range(rule.get("min_items", 0))]
            if rule["kind"] == "object": return {field: sample(rule["properties"][field]) for field in rule.get("required", [])}
            if rule["kind"] == "cloud_class": return "ArchAmazonEC2AWS2024"
            raise AssertionError(f"Unsupported fixture rule {rule}")
        for type_name, shape_spec in data["types"].items():
            properties = {field: sample(shape_spec["properties"][field]) for field in shape_spec["required_properties"]}
            if type_name == "flexiblePolygon": properties = {"vertices": [{"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 0, "y": 1}]}
            if type_name in ("swimLanes", "bpmnPool"): properties["lanes"][0]["width"] = 100 if properties.get("vertical", True) else 60
            if type_name == "namedContainer": properties["className"] = "AWSAccountAWS2024"
            with self.subTest(type=type_name): self.valid(type_name, properties)
        for library in data["cloud_libraries"].values():
            for collection, type_name in (("shape_classes", "namedShape"), ("container_classes", "namedContainer")):
                for class_name in library[collection]:
                    with self.subTest(className=class_name): self.valid(type_name, {"className": class_name})
        self.assertEqual(catalog.check_catalog()["native_type_count"], 63)

    def test_literal_nested_label_escaping_preserves_identifiers(self):
        table = {"rowCount": 1, "colCount": 1, "cells": [{"xPosition": 0, "yPosition": 0, "text": "<script> & \"quote\"\nnext"}]}
        validated = self.valid("table", table)
        formatted = catalog.format_properties("table", validated)
        self.assertEqual(formatted["cells"][0]["text"], "&lt;script&gt; &amp; &quot;quote&quot;<br/>next")
        self.assertEqual(validated, table)
        cloud = {"className": "ArchAmazonEC2AWS2024"}
        self.assertEqual(catalog.format_properties("namedShape", self.valid("namedShape", cloud)), cloud)
        self.assertEqual(catalog.format_properties("bpmnActivity", self.valid("bpmnActivity", {"activityType": "task"})), {"activityType": "task"})
        self.assertEqual(catalog.format_properties("rectangleContainer", self.valid("rectangleContainer", {"containerTitle": {"text": "A & B"}}))["containerTitle"]["text"], "A &amp; B")

    def test_finite_numbers_with_overflowing_dimension_totals_fail_cleanly(self):
        # Each integer converts to a finite float; their sum exceeds float range.
        huge = 10 ** 308
        with self.assertRaisesRegex(ValueError, "widths must sum"):
            self.valid("bpmnPool", {"title": "Pool", "lanes": [{"title": "A", "width": huge, "laneFill": "#ffffff"}] * 2})
        with self.assertRaisesRegex(ValueError, "sizes must match"):
            self.valid("table", {"rowCount": 1, "colCount": 2, "cells": [],
                                 "userSpecifiedCols": [{"index": 0, "size": huge}, {"index": 1, "size": huge}]})


if __name__ == "__main__":
    unittest.main(verbosity=2)
