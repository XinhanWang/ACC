"""Content checks for the standalone communication coach skill (no API calls)."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / ".agents" / "skills" / "communication-coach"
ENTRY = SKILL / "SKILL.md"


def cards(filename, prefix):
    text = (SKILL / "references" / filename).read_text(encoding="utf-8")
    pattern = rf"^### ({prefix}\d{{2}}) [^\n]+\n(.*?)(?=^#{{1,3}} |\Z)"
    return re.findall(pattern, text, flags=re.MULTILINE | re.DOTALL)


class CoachContentTests(unittest.TestCase):
    def test_entry(self):
        text = ENTRY.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        _, frontmatter, body = text.split("---\n", 2)
        self.assertIn(f"name: {SKILL.name}", frontmatter.splitlines())
        self.assertRegex(frontmatter, r"(?m)^description: \S.+$")
        for filename in ("curriculum.md", "scenarios.md"):
            self.assertIn(f"(references/{filename})", body)

    def test_local_links(self):
        for doc in [ROOT / "README.md", *SKILL.rglob("*.md")]:
            for dest in re.findall(r"\[[^\]]+\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
                if "://" not in dest and not dest.startswith("#"):
                    with self.subTest(doc=doc.name, dest=dest):
                        self.assertTrue((doc.parent / dest.split("#")[0]).exists())

    def test_three_drills_per_lesson(self):
        lessons = cards("curriculum.md", "K")
        self.assertTrue(lessons)
        for i, (lesson_id, body) in enumerate(lessons, start=1):
            with self.subTest(lesson=lesson_id):
                self.assertEqual(lesson_id, f"K{i:02d}")
                self.assertEqual(re.findall(r"^(\d+)\. \S", body, re.MULTILINE), ["1", "2", "3"])

    def test_scenes_reference_existing_lessons(self):
        lessons = {key for key, _ in cards("curriculum.md", "K")}
        scenes = cards("scenarios.md", "S")
        self.assertTrue(scenes)
        covered = set()
        for i, (scene_id, body) in enumerate(scenes, start=1):
            with self.subTest(scene=scene_id):
                self.assertEqual(scene_id, f"S{i:02d}")
                refs = set(re.findall(r"K\d{2}", body))
                self.assertTrue(refs)
                self.assertFalse(refs - lessons)
                covered.update(refs)
        self.assertEqual(covered, lessons)


if __name__ == "__main__":
    unittest.main()
