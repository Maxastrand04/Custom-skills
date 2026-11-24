import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("sync_helper_skill", ROOT / "scripts/sync-helper-skill.py")
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)

BASE = ("grill-docs", "new-ticket", "pr-ticket", "map-epic", "amend-pcr")


class HelperSkillTests(unittest.TestCase):
    def test_every_copy_matches_its_original(self):
        self.assertEqual(sync.stale_copies(), [])

    def test_no_kanban_skill_reads_a_base_file_by_path(self):
        for skill in sorted((ROOT / "kanban").iterdir()):
            if skill.name in BASE or skill.name == "helper-skill" or not skill.is_dir():
                continue
            for path in skill.rglob("*.md"):
                text = path.read_text()
                for base in BASE:
                    self.assertFalse(f"../{base}/" in text, f"{path.relative_to(ROOT)} reads {base} by path")

    def test_no_base_skill_names_a_kanban_or_behaviour_skill(self):
        names = [p.name for p in (ROOT / "kanban").iterdir()
                 if p.is_dir() and p.name not in BASE and p.name != "helper-skill"]
        names += ["gloss-me", "unslop", "kanban"]
        for base in BASE:
            for path in (ROOT / "kanban" / base).rglob("*.md"):
                text = path.read_text()
                for name in names:
                    self.assertFalse(name in text, f"{path.relative_to(ROOT)} names {name}")
