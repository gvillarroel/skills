#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2"]
# ///
"""Exercise standalone metadata, navigation, and profile boundary failures."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from check_skill_authoring import check_skill, without_fences


class AuthoringTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="authoring-check-", dir=Path.cwd())
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "demo-skill"
        self.root.mkdir()
        self.metadata = "name: demo-skill\ndescription: Reviews changes. Use when reviewing Demo."
        self.body = "\n# Demo\n\nReview the supplied changes.\n"

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def report(self, *, profile: str = "source") -> dict:
        self.write("SKILL.md", f"---\n{self.metadata}\n---\n{self.body}")
        return check_skill(self.root, profile=profile)

    def codes(self, **kwargs) -> set[str]:
        return {issue["code"] for issue in self.report(**kwargs)["issues"]}

    def test_valid_skill(self) -> None:
        self.assertTrue(self.report()["passed"])

    def test_missing_entry(self) -> None:
        self.assertEqual(check_skill(self.root)["issues"][0]["code"], "missing-entry")

    def test_empty_frontmatter(self) -> None:
        self.metadata = ""
        self.assertIn("frontmatter-fields", self.codes())

    def test_duplicate_metadata(self) -> None:
        self.metadata += "\ndescription: Other value."
        self.assertIn("frontmatter", self.codes())

    def test_non_mapping_metadata(self) -> None:
        self.metadata = "[name, description]"
        self.assertIn("frontmatter-fields", self.codes())

    def test_extra_metadata(self) -> None:
        self.metadata += "\nmetadata: extra"
        self.assertIn("frontmatter-fields", self.codes())

    def test_name_must_match(self) -> None:
        self.metadata = self.metadata.replace("demo-skill", "other-skill")
        self.assertIn("skill-name", self.codes())

    def test_reserved_vendor_name(self) -> None:
        self.root = self.root.with_name("claude-reviewer")
        self.root.mkdir()
        self.metadata = self.metadata.replace("demo-skill", self.root.name)
        self.assertIn("reserved-name", self.codes())

    def test_name_length_boundary(self) -> None:
        self.root = self.root.with_name("a" * 63)
        self.root.mkdir()
        self.metadata = self.metadata.replace("demo-skill", self.root.name)
        self.assertTrue(self.report()["passed"])
        self.root = self.root.with_name("a" * 64)
        self.root.mkdir()
        self.metadata = self.metadata.replace("a" * 63, self.root.name)
        self.assertIn("skill-name", self.codes())

    def test_description_length_boundary(self) -> None:
        self.metadata = "name: demo-skill\ndescription: " + "a" * 1024
        self.assertTrue(self.report()["passed"])
        self.metadata += "a"
        self.assertIn("description-length", self.codes())

    def test_xml_in_description(self) -> None:
        self.metadata += " <review>"
        self.assertIn("description-tags", self.codes())

    def test_first_and_second_person(self) -> None:
        for description in ("I can review changes.", "We review changes.", "You can review changes.", "Review your changes."):
            with self.subTest(description=description):
                self.metadata = "name: demo-skill\ndescription: " + description
                self.assertIn("description-person", self.codes())

    def test_io_is_not_first_person(self) -> None:
        self.metadata = "name: demo-skill\ndescription: Inspects I/O performance. Use for disk profiles."
        self.assertTrue(self.report()["passed"])

    def test_imperative_description_is_rejected(self) -> None:
        self.metadata = "name: demo-skill\ndescription: Review Demo changes. Use for change reviews."
        self.assertIn("description-voice", self.codes())

    def test_body_length_boundary(self) -> None:
        self.body = "Instruction.\n" * 499
        self.assertTrue(self.report()["passed"])
        self.body += "Instruction.\n"
        self.assertIn("body-size", self.codes())

    def test_empty_body(self) -> None:
        self.body = "\n"
        self.assertIn("empty-body", self.codes())

    def test_unrouted_reference(self) -> None:
        self.write("references/detail.md", "# Detail\n")
        self.assertIn("reference-route", self.codes())

    def test_individual_reference_routes(self) -> None:
        self.write("references/detail.md", "# Detail\n")
        for route in ("Read `references/detail.md`.", "Read [detail](references/detail.md)."):
            self.body = route
            self.assertTrue(self.report()["passed"])

    def test_collection_directory_does_not_replace_direct_file_links(self) -> None:
        self.write("references/charts/line.md", "# Line\n")
        self.body += "Choose a file from [chart recipes](references/charts/). Read it in full.\n"
        self.assertIn("reference-route", self.codes())

    def test_catchall_directory_does_not_replace_routing(self) -> None:
        self.write("references/detail.md", "# Detail\n")
        self.body += "Read [everything](references/).\n"
        self.assertIn("reference-route", self.codes())

    def test_fake_route_in_fence(self) -> None:
        self.write("references/detail.md", "# Detail\n")
        self.body += "````md\n[detail](references/detail.md)\n```\n````\n"
        self.assertIn("reference-route", self.codes())

    def test_long_reference_requires_contents(self) -> None:
        self.body += "Read `references/detail.md`.\n"
        self.write("references/detail.md", "# Detail\n\n## Workflow\n" + "Instruction.\n" * 100)
        self.assertIn("reference-contents", self.codes())

    def test_working_contents(self) -> None:
        self.body += "Read `references/detail.md`.\n"
        self.write("references/detail.md", "# Detail\n\n## Contents\n\n- [Workflow](#workflow)\n\n## Workflow\n" + "Instruction.\n" * 100)
        self.assertTrue(self.report()["passed"])

    def test_broken_contents(self) -> None:
        self.body += "Read `references/detail.md`.\n"
        self.write("references/detail.md", "# Detail\n\n## Contents\n\n- [Workflow](#missing)\n\n## Workflow\n" + "Instruction.\n" * 100)
        self.assertIn("reference-contents-links", self.codes())

    def test_fake_contents_in_code(self) -> None:
        self.body += "Read `references/detail.md`.\n"
        self.write("references/detail.md", "# Detail\n\n```md\n## Contents\n- [Workflow](#workflow)\n```\n\n## Workflow\n" + "Instruction.\n" * 100)
        self.assertIn("reference-contents", self.codes())

    def test_duplicate_heading_anchors(self) -> None:
        self.body += "Read `references/detail.md`.\n"
        self.write("references/detail.md", "# Detail\n\n## Contents\n\n- [First](#workflow)\n- [Second](#workflow-1)\n\n## Workflow\n" + "Instruction.\n" * 100 + "\n## Workflow\n")
        self.assertTrue(self.report()["passed"])

    def test_unicode_reference_encoding_error(self) -> None:
        self.body += "Read `references/detail.md`.\n"
        (self.root / "references").mkdir()
        (self.root / "references/detail.md").write_bytes(b"\xff\xfe")
        self.assertIn("reference-encoding", self.codes())

    def test_windows_path_in_command(self) -> None:
        self.body += "```powershell\npython C:\\tools\\helper.py\n```\n"
        self.assertIn("windows-path", self.codes())

    def test_runtime_excludes_fixtures(self) -> None:
        self.write("assets/examples/fixture.txt", "Fixture")
        self.assertTrue(self.report()["passed"])
        self.assertIn("runtime-fixtures", self.codes(profile="runtime"))

    def test_four_backtick_fence(self) -> None:
        self.assertEqual(without_fences("A\n````md\n## Hidden\n```\n````\nB"), "A\n\n\n\n\nB")


if __name__ == "__main__":
    unittest.main()
