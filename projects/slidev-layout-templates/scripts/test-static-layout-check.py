#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Regression checks for the read-only bundled Slidev layout deck checker."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[3]
SKILLS = ("slidev-echarts", "slidev-animejs")
RUNTIME = ("components/SlidevLayout.vue", "lib/slidev-layouts.mjs", "components/SlidevCollection.vue")
EXPECTED_RUNTIME = (
    "227f1258f0a7695e4551c8d5310a3d34c77ed3b0ac89029971d7684ad69389b3",
    "99fc6d415bd59417e59045703b02653a1f789b63ad1e209582b19ae6a4c0c439",
    "e15f3dcf7cbd0680aaa6f1e9a618750b058da7b4ee46ab5fe312fcd6318724b2",
)
ARTIFACTS = ROOT / "projects/slidev-layout-templates/artifacts/static-check"
SOURCE = """---
theme: default
fonts:
  sans: Open Sans
---
# A legal deck

<SlidevLayout :items="cards" mode="grid" :columns="3" :rows="3" />

---

```mermaid
flowchart LR
  A[Request] --> B[Deliver]
```

~~~text
This fenced text is legal.
~~~
"""


def snapshot(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(directory)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in directory.rglob("*") if path.is_file()
    }


class StaticLayoutCheckerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        cls.checkers = []
        for name in SKILLS:
            script = ROOT / "skills" / name / "scripts/check_layout_deck.py"
            spec = importlib.util.spec_from_file_location(name.replace("-", "_") + "_checker", script)
            assert spec and spec.loader
            checker = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(checker)
            cls.checkers.append((name, script, checker))
        cls.checker_hash = hashlib.sha256(cls.checkers[0][1].read_bytes()).hexdigest()

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="regression-", dir=ARTIFACTS)
        self.addCleanup(self.temporary.cleanup)
        self.workspace = Path(self.temporary.name).resolve()
        self.deck = self.workspace / "deck"
        self.deck.mkdir()
        self.make_deck()

    def make_deck(self) -> None:
        for relative in RUNTIME:
            target = self.deck / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / "skills/slidev-echarts/assets/templates/slidev-layouts" / relative, target)
        (self.deck / "slides.md").write_text(SOURCE, encoding="utf-8")
        (self.deck / "style.css").write_text(".custom-slot { font-size: 18px; }\n", encoding="utf-8")
        self.package = {"scripts": {"build": "slidev build"}, "dependencies": {"vue": "^3.5.0"}, "devDependencies": {"@slidev/cli": "52.16.0", "@slidev/theme-default": "latest"}}
        self.write_package()
        self.items = [{"id": f"card-{index + 1}", "title": f"Card {index + 1}", "body": "Complete content.", "category": f"category-{index + 1}", "width": 180 + index} for index in range(11)]
        self.write_data()

    def write_package(self) -> None:
        (self.deck / "package.json").write_text(json.dumps(self.package), encoding="utf-8")

    def write_data(self, payload: object | None = None) -> None:
        (self.deck / "cards.json").write_text(json.dumps({"items": self.items} if payload is None else payload), encoding="utf-8")

    def check_both(self, *, data: str | None = "cards.json", count: int | None = 11, require_bundled: bool = True):
        return [checker.check(self.deck.resolve(), data, count, require_bundled) for _, _, checker in self.checkers]

    def assert_rejected(self, text: str, **options) -> None:
        for result in self.check_both(**options):
            self.assertFalse(result["passed"], result)
            self.assertIn(text, " ".join(result["errors"]))

    def test_shipped_checkers_and_runtime_are_identical_and_frozen(self) -> None:
        self.assertEqual(self.checkers[0][1].read_bytes(), self.checkers[1][1].read_bytes())
        for relative in RUNTIME:
            self.assertEqual((ROOT / "skills/slidev-echarts/assets/templates/slidev-layouts" / relative).read_bytes(), (ROOT / "skills/slidev-animejs/assets/templates/slidev-layouts" / relative).read_bytes())
        for relative, digest in zip(RUNTIME, EXPECTED_RUNTIME, strict=True):
            baseline = ROOT / "skills/slidev-echarts/assets/templates/slidev-layouts" / relative
            self.assertEqual(hashlib.sha256(baseline.read_bytes()).hexdigest(), digest)
            self.assertEqual(baseline.read_bytes(), (ROOT / "skills/slidev-animejs/assets/templates/slidev-layouts" / relative).read_bytes())

    def test_legal_headmatter_extra_css_eleven_unique_items_pass_read_only(self) -> None:
        before = snapshot(self.workspace)
        for result in self.check_both():
            self.assertTrue(result["passed"], result)
            self.assertEqual(result["itemCount"], 11)
            self.assertTrue(result["balancedFences"])
            self.assertEqual(result["completedFences"], 2)
            self.assertEqual(result["declaredThemePackages"], ["@slidev/theme-default"])
        self.assertEqual(snapshot(self.workspace), before)

    def test_cli_emits_json_and_does_not_modify_files(self) -> None:
        before = snapshot(self.workspace)
        for _, script, _ in self.checkers:
            process = subprocess.run([sys.executable, str(script), "--deck", str(self.deck), "--data", "cards.json", "--expect-items", "11", "--require-bundled-runtime"], capture_output=True, text=True, check=False)
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertEqual(process.stderr, "")
            self.assertTrue(json.loads(process.stdout)["passed"])
        self.assertEqual(snapshot(self.workspace), before)

    def test_missing_runtime_is_rejected(self) -> None:
        (self.deck / RUNTIME[0]).unlink()
        self.assert_rejected("Cannot read components/SlidevLayout.vue")

    def test_empty_runtime_is_rejected(self) -> None:
        (self.deck / RUNTIME[1]).write_bytes(b"")
        self.assert_rejected("Required file is empty: lib/slidev-layouts.mjs")

    def test_missing_parent_component_is_rejected(self) -> None:
        (self.deck / "components/SlidevCollection.vue").unlink()
        self.assert_rejected("Cannot read components/SlidevCollection.vue")

    def test_empty_parent_component_is_rejected(self) -> None:
        (self.deck / "components/SlidevCollection.vue").write_bytes(b"")
        self.assert_rejected("Required file is empty: components/SlidevCollection.vue")

    def test_modified_runtime_rejected_when_bundle_copy_required(self) -> None:
        (self.deck / RUNTIME[1]).write_text("// Deliberately modified runtime.\n", encoding="utf-8")
        self.assert_rejected("Runtime copy differs from the loaded bundle")
        for result in self.check_both(require_bundled=False):
            self.assertTrue(result["passed"], result)

    def test_unclosed_fence_rejected_without_counting_slide_separators(self) -> None:
        (self.deck / "slides.md").write_text(SOURCE + "\n```vue\n<SlidevLayout />\n", encoding="utf-8")
        self.assert_rejected("Unclosed Markdown fence")

    def test_missing_or_empty_vue_declaration_is_rejected(self) -> None:
        self.package["dependencies"].pop("vue")
        self.write_package()
        self.assert_rejected("Declare vue")
        self.package["dependencies"]["vue"] = "  "
        self.write_package()
        self.assert_rejected("Declare vue")

    def test_dependencies_can_be_split_across_groups(self) -> None:
        self.package["devDependencies"]["vue"] = self.package["dependencies"].pop("vue")
        self.package["dependencies"]["@slidev/cli"] = self.package["devDependencies"].pop("@slidev/cli")
        self.write_package()
        self.assertTrue(all(result["passed"] for result in self.check_both()))

    def test_duplicate_item_identity_is_rejected(self) -> None:
        self.items[-1]["id"] = self.items[0]["id"]
        self.write_data()
        self.assert_rejected("item ids must be unique")

    def test_wrong_item_count_is_rejected(self) -> None:
        self.assert_rejected("Expected 12 data items; found 11", count=12)

    def test_data_array_and_cards_object_are_accepted(self) -> None:
        for payload in (self.items, {"cards": self.items}):
            self.write_data(payload)
            self.assertTrue(all(result["passed"] for result in self.check_both()))

    def test_invalid_numeric_widths_are_rejected(self) -> None:
        for width in (0, -1, True, "140", float("nan"), float("inf"), float("-inf")):
            with self.subTest(width=width):
                self.items[0]["width"] = width
                self.write_data()
                self.assert_rejected("width must be positive")

    def test_invalid_data_identity_and_text_are_rejected(self) -> None:
        for field, value, message in (("id", "", "nonempty string id"), ("title", 123, "must be a string"), ("body", None, "must be a string"), ("category", False, "must be a string")):
            original = self.items[0][field]
            self.items[0][field] = value
            self.write_data()
            self.assert_rejected(message)
            self.items[0][field] = original

    def test_outside_data_path_is_rejected_before_any_read(self) -> None:
        outside = self.workspace / "outside.json"
        outside.write_text("private fixture marker", encoding="utf-8")
        original_read = Path.read_text
        reads = []

        def guarded_read(path: Path, *args, **kwargs):
            if path.resolve() == outside:
                reads.append(str(path))
                raise AssertionError("The checker attempted to read outside the deck.")
            return original_read(path, *args, **kwargs)

        before = snapshot(self.workspace)
        with patch.object(Path, "read_text", guarded_read):
            self.assert_rejected("Path must stay within the deck", data="../outside.json")
            self.assert_rejected("Path must stay within the deck", data=str(outside))
        self.assertEqual(reads, [])
        self.assertEqual(snapshot(self.workspace), before)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(StaticLayoutCheckerTests)
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    if outcome.wasSuccessful():
        print(json.dumps({"status": "pass", "tests": outcome.testsRun, "skills": list(SKILLS), "checkerSha256": StaticLayoutCheckerTests.checker_hash, "runtimeSha256": list(EXPECTED_RUNTIME)}))
    raise SystemExit(0 if outcome.wasSuccessful() else 1)
