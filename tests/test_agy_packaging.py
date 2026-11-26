import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/build-agy.py"
spec = importlib.util.spec_from_file_location("build_agy", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

SKILL = "---\nname: {name}\ndescription: Does {name} things.\n---\n\nBody of {name}.\n"
RULES = "# Rules\n\nStay plain.\n"


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content)


def files_under(folder):
    return {p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()}


class FakeCheckout:
    """A throwaway Custom-skills checkout holding only what a build reads."""

    def __init__(self, base):
        self.root = base / "checkout"
        self.dest = base / "tree"
        write(self.root / "config/agy/AGENTS.md", RULES)
        write(self.root / "config/agy/hooks.json", '{"unslop": {}}\n')
        write(self.root / "config/agy/hooks/inject_unslop.py", "print('hi')\n")
        self.list([])

    def skill(self, path, name=None):
        folder = self.root / path
        write(folder / "SKILL.md", SKILL.format(name=name or folder.name))
        return folder

    def list(self, entries, plugin="max"):
        catalog = {"name": "custom-skills", "plugins": [{"name": plugin, "source": ".", "skills": entries}]}
        write(self.root / ".claude-plugin/marketplace.json", json.dumps(catalog, indent=2) + "\n")

    def build(self, version="1.2.3"):
        return builder.build_tree(version, self.dest, self.root)


class BuildTreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agy-build-test-")
        self.fake = FakeCheckout(Path(self.temp.name))
        self.fake.skill("kanban/alpha")
        self.fake.list(["./kanban/alpha"])

    def tearDown(self):
        self.temp.cleanup()

    def manifest_text(self):
        return (self.fake.dest / "plugin.json").read_text(encoding="utf-8")

    def test_listed_skill_lands_flat_under_skills(self):
        self.fake.build()
        self.assertTrue((self.fake.dest / "skills/alpha/SKILL.md").is_file())

    def test_category_folder_is_dropped(self):
        self.fake.build()
        self.assertFalse((self.fake.dest / "skills/kanban").exists())

    def test_unlisted_skill_is_left_out(self):
        self.fake.skill("kanban/beta")
        self.fake.build()
        self.assertFalse((self.fake.dest / "skills/beta").exists())

    def test_list_is_read_from_the_max_entry_only(self):
        self.fake.skill("kanban/beta")
        catalog = {"plugins": [
            {"name": "other", "skills": ["./kanban/beta"]},
            {"name": "max", "skills": ["./kanban/alpha"]},
        ]}
        write(self.fake.root / ".claude-plugin/marketplace.json", json.dumps(catalog))
        self.fake.build()
        self.assertEqual(sorted(p.name for p in (self.fake.dest / "skills").iterdir()), ["alpha"])

    def test_bundled_file_travels_with_its_skill(self):
        write(self.fake.root / "kanban/alpha/refs/format.md", "# Format\n")
        self.fake.build()
        self.assertEqual((self.fake.dest / "skills/alpha/refs/format.md").read_text(), "# Format\n")

    def test_skill_files_are_copied_byte_for_byte(self):
        text = "---\nname: alpha\ndescription: Run /beta — then “stop”.\n---\n\nSee ../beta/x.md\n"
        write(self.fake.root / "kanban/alpha/SKILL.md", text.encode("utf-8"))
        self.fake.build()
        self.assertEqual((self.fake.dest / "skills/alpha/SKILL.md").read_bytes(), text.encode("utf-8"))

    def test_non_text_bundled_file_is_copied_byte_for_byte(self):
        blob = bytes(range(256))
        write(self.fake.root / "kanban/alpha/assets/logo.png", blob)
        self.fake.build()
        self.assertEqual((self.fake.dest / "skills/alpha/assets/logo.png").read_bytes(), blob)

    def test_dotfiles_are_skipped(self):
        write(self.fake.root / "kanban/alpha/.DS_Store", b"\x00")
        self.fake.build()
        self.assertFalse((self.fake.dest / "skills/alpha/.DS_Store").exists())

    def test_files_inside_dot_folders_are_skipped(self):
        write(self.fake.root / "kanban/alpha/.cache/notes.md", "scratch\n")
        self.fake.build()
        self.assertFalse((self.fake.dest / "skills/alpha/.cache").exists())

    def test_returns_skill_names_in_marketplace_order(self):
        self.fake.skill("behaviour/zeta")
        self.fake.skill("kanban/beta")
        self.fake.list(["./behaviour/zeta", "./kanban/alpha", "./kanban/beta"])
        self.assertEqual(self.fake.build(), ["zeta", "alpha", "beta"])

    def test_agents_md_is_copied_unchanged_to_the_root(self):
        self.fake.build()
        self.assertEqual((self.fake.dest / "AGENTS.md").read_bytes(), RULES.encode())

    def test_no_agy_hooks_reach_the_tree(self):
        self.fake.build()
        hooks = [f for f in files_under(self.fake.dest) if "hooks" in f]
        self.assertEqual(hooks, [])

    def test_tree_holds_only_skills_rules_and_manifest(self):
        write(self.fake.root / "kanban/alpha/refs/format.md", "# Format\n")
        self.fake.build()
        self.assertEqual(
            files_under(self.fake.dest),
            {"AGENTS.md", "plugin.json", "skills/alpha/SKILL.md", "skills/alpha/refs/format.md"},
        )

    def test_manifest_has_exactly_four_keys_in_order(self):
        self.fake.build()
        self.assertEqual(list(json.loads(self.manifest_text())), ["name", "version", "displayName", "description"])

    def test_manifest_name_is_max(self):
        self.fake.build()
        self.assertEqual(json.loads(self.manifest_text())["name"], "max")

    def test_manifest_carries_the_build_version(self):
        self.fake.build("4.5.6")
        self.assertEqual(json.loads(self.manifest_text())["version"], "4.5.6")

    def test_manifest_display_name_is_the_constant(self):
        self.fake.build()
        self.assertEqual(json.loads(self.manifest_text())["displayName"], builder.DISPLAY_NAME)

    def test_manifest_description_is_the_constant(self):
        self.fake.build()
        self.assertEqual(json.loads(self.manifest_text())["description"], builder.DESCRIPTION)

    def test_manifest_keeps_non_ascii_as_written(self):
        self.fake.build()
        self.assertIn("Åstrand", self.manifest_text())

    def test_manifest_is_indented_two_spaces(self):
        self.fake.build()
        self.assertIn('\n  "name": "max",\n', self.manifest_text())

    def test_manifest_ends_in_a_newline(self):
        self.fake.build()
        self.assertTrue(self.manifest_text().endswith("}\n"))

    def test_rebuild_drops_what_an_earlier_build_left(self):
        write(self.fake.dest / "skills/retired/SKILL.md", SKILL.format(name="retired"))
        self.fake.build()
        self.assertFalse((self.fake.dest / "skills/retired").exists())

    def test_building_twice_gives_the_same_bytes(self):
        self.fake.build()
        first = {f: (self.fake.dest / f).read_bytes() for f in files_under(self.fake.dest)}
        self.fake.build()
        second = {f: (self.fake.dest / f).read_bytes() for f in files_under(self.fake.dest)}
        self.assertEqual(first, second)

    def test_missing_listed_skill_folder_fails_the_build(self):
        self.fake.list(["./kanban/alpha", "./kanban/ghost"])
        with self.assertRaises(ValueError):
            self.fake.build()

    def test_failed_build_leaves_the_destination_as_it_was(self):
        write(self.fake.dest / "keep.txt", "old\n")
        self.fake.list(["./kanban/alpha", "./kanban/ghost"])
        with self.assertRaises(ValueError):
            self.fake.build()
        self.assertEqual(files_under(self.fake.dest), {"keep.txt"})

    def test_version_without_three_numbers_is_refused(self):
        for version in ("", "1.2", "v1.2.3", "1.2.3-rc1", "one.two.three"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.fake.build(version)

    def test_catalog_without_a_max_entry_is_refused(self):
        self.fake.list(["./kanban/alpha"], plugin="other")
        with self.assertRaises(ValueError):
            self.fake.build()

    def test_missing_catalog_is_refused(self):
        (self.fake.root / ".claude-plugin/marketplace.json").unlink()
        with self.assertRaises(ValueError):
            self.fake.build()

    def test_catalog_without_a_plugins_list_is_refused(self):
        write(self.fake.root / ".claude-plugin/marketplace.json", json.dumps({"name": "custom-skills"}))
        with self.assertRaises(ValueError):
            self.fake.build()

    def test_catalog_with_two_max_entries_is_refused(self):
        catalog = {"plugins": [{"name": "max", "skills": ["./kanban/alpha"]}] * 2}
        write(self.fake.root / ".claude-plugin/marketplace.json", json.dumps(catalog))
        with self.assertRaises(ValueError):
            self.fake.build()

    def test_max_entry_without_a_skills_list_is_refused(self):
        for skills in (None, "./kanban/alpha", [1]):
            entry = {"name": "max"} if skills is None else {"name": "max", "skills": skills}
            write(self.fake.root / ".claude-plugin/marketplace.json", json.dumps({"plugins": [entry]}))
            with self.subTest(skills=skills), self.assertRaises(ValueError):
                self.fake.build()

    def test_two_listed_folders_with_one_name_are_refused(self):
        self.fake.skill("developer-tools/alpha")
        self.fake.list(["./kanban/alpha", "./developer-tools/alpha"])
        with self.assertRaises(ValueError):
            self.fake.build()

    def test_missing_agents_md_is_refused(self):
        (self.fake.root / "config/agy/AGENTS.md").unlink()
        with self.assertRaises(ValueError):
            self.fake.build()


class CheckTreeTests(unittest.TestCase):
    MANIFEST = {"name": "max", "version": "1.2.3", "displayName": "Max", "description": "Skills."}

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agy-check-test-")
        self.tree = Path(self.temp.name)
        self.manifest(self.MANIFEST)
        self.skill("alpha")

    def tearDown(self):
        self.temp.cleanup()

    def manifest(self, value):
        write(self.tree / "plugin.json", json.dumps(value, indent=2) + "\n")

    def skill(self, folder, text=None):
        write(self.tree / "skills" / folder / "SKILL.md", SKILL.format(name=folder) if text is None else text)

    def mentions(self, path):
        return [m for m in builder.check_tree(self.tree) if path in m]

    def test_valid_tree_passes(self):
        self.assertEqual(builder.check_tree(self.tree), [])

    def test_name_differing_from_folder_is_reported(self):
        self.skill("alpha", "---\nname: beta\ndescription: Does things.\n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_missing_name_is_reported(self):
        self.skill("alpha", "---\ndescription: Does things.\n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_name_outside_the_frontmatter_does_not_count(self):
        self.skill("alpha", "---\ndescription: Does things.\n---\nname: alpha\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_missing_description_is_reported(self):
        self.skill("alpha", "---\nname: alpha\n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_empty_description_is_reported(self):
        self.skill("alpha", "---\nname: alpha\ndescription:\n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_folded_description_passes(self):
        self.skill("alpha", "---\nname: alpha\ndescription: >\n  Does things,\n  over two lines.\n---\n")
        self.assertEqual(builder.check_tree(self.tree), [])

    def test_literal_and_chomped_descriptions_pass(self):
        for marker in ("|", ">-", "|-", ">+", "|+"):
            self.skill("alpha", f"---\nname: alpha\ndescription: {marker}\n  Does things.\n---\n")
            with self.subTest(marker=marker):
                self.assertEqual(builder.check_tree(self.tree), [])

    def test_folded_description_with_no_text_is_reported(self):
        self.skill("alpha", "---\nname: alpha\ndescription: >\n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_folded_description_with_only_blank_lines_is_reported(self):
        self.skill("alpha", "---\nname: alpha\ndescription: >\n\n   \n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_folded_description_followed_by_an_unindented_line_is_reported(self):
        self.skill("alpha", "---\ndescription: >\nname: alpha\n---\n")
        self.assertIn("skills/alpha/SKILL.md: frontmatter needs a description", builder.check_tree(self.tree))

    def test_missing_name_and_description_give_two_messages(self):
        self.skill("alpha", "---\ntitle: Alpha\n---\n")
        self.assertEqual(len(self.mentions("skills/alpha")), 2)

    def test_folder_without_skill_md_is_reported(self):
        (self.tree / "skills/empty").mkdir()
        self.assertNotEqual(self.mentions("skills/empty"), [])

    def test_folder_without_skill_md_gives_one_message(self):
        (self.tree / "skills/empty").mkdir()
        self.assertEqual(len(self.mentions("skills/empty")), 1)

    def test_skill_md_without_frontmatter_is_reported(self):
        self.skill("alpha", "# Alpha\n\nname: alpha\ndescription: Does things.\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_skill_md_without_frontmatter_gives_one_message(self):
        self.skill("alpha", "# Alpha\n")
        self.assertEqual(len(self.mentions("skills/alpha")), 1)

    def test_unclosed_frontmatter_is_reported(self):
        self.skill("alpha", "---\nname: alpha\ndescription: Does things.\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_skill_folder_not_in_kebab_case_is_reported(self):
        for folder in ("Alpha", "alpha_beta", "alpha--beta", "-alpha"):
            with self.subTest(folder=folder):
                tree = Path(tempfile.mkdtemp(dir=self.temp.name))
                write(tree / "plugin.json", json.dumps(self.MANIFEST))
                write(tree / "skills" / folder / "SKILL.md", SKILL.format(name=folder))
                self.assertNotEqual([m for m in builder.check_tree(tree) if folder in m], [])

    def test_empty_skills_folder_is_reported(self):
        shutil.rmtree(self.tree / "skills/alpha")
        self.assertNotEqual(builder.check_tree(self.tree), [])

    def test_missing_skills_folder_is_reported(self):
        shutil.rmtree(self.tree / "skills")
        self.assertNotEqual(builder.check_tree(self.tree), [])

    def test_manifest_name_not_in_kebab_case_is_reported(self):
        for name in ("Max", "max_skills", "max skills", "max-", "", 7):
            self.manifest(dict(self.MANIFEST, name=name))
            with self.subTest(name=name):
                self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_kebab_case_manifest_name_passes(self):
        self.manifest(dict(self.MANIFEST, name="max-skills-2"))
        self.assertEqual(builder.check_tree(self.tree), [])

    def test_missing_manifest_name_is_reported(self):
        self.manifest({k: v for k, v in self.MANIFEST.items() if k != "name"})
        self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_manifest_key_outside_the_schema_is_reported(self):
        self.manifest(dict(self.MANIFEST, owner="Max"))
        self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_every_schema_key_is_allowed(self):
        self.manifest(dict(
            self.MANIFEST,
            **{"$schema": "https://antigravity.google/schemas/v1/plugin.json"},
            skills=[], disabled=False, author={"name": "Max"}, homepage="https://example.org",
            repository="https://example.org/repo", license="MIT", keywords=["skills"],
            logo="logo.png", suggestedPrompts=["Grill me"],
        ))
        self.assertEqual(builder.check_tree(self.tree), [])

    def test_missing_manifest_is_reported(self):
        (self.tree / "plugin.json").unlink()
        self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_missing_manifest_gives_one_message(self):
        (self.tree / "plugin.json").unlink()
        self.assertEqual(len(self.mentions("plugin.json")), 1)

    def test_manifest_that_is_not_an_object_is_reported(self):
        self.manifest(["max"])
        self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_manifest_that_is_not_json_is_reported(self):
        write(self.tree / "plugin.json", "{name: max")
        self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_every_broken_rule_is_reported(self):
        self.manifest(dict(self.MANIFEST, name="Max"))
        self.skill("beta", "---\nname: gamma\ndescription: x\n---\n")
        self.skill("delta", "---\nname: delta\n---\n")
        messages = builder.check_tree(self.tree)
        self.assertEqual(
            [any(path in m for m in messages) for path in ("plugin.json", "skills/beta", "skills/delta")],
            [True, True, True],
        )

    def test_manifest_messages_come_before_skill_messages(self):
        self.skill("alpha", "---\nname: wrong\ndescription: x\n---\n")
        self.manifest(dict(self.MANIFEST, name="Max"))
        messages = builder.check_tree(self.tree)
        self.assertIn("plugin.json", messages[0])

    def test_skill_messages_are_ordered_by_folder_name(self):
        for folder in ("zeta", "beta", "mu"):
            self.skill(folder, "---\nname: wrong\ndescription: x\n---\n")
        messages = builder.check_tree(self.tree)
        order = [next(f for f in ("zeta", "beta", "mu") if f"skills/{f}" in m) for m in messages]
        self.assertEqual(order, ["beta", "mu", "zeta"])

    def test_check_leaves_the_tree_unchanged(self):
        self.skill("beta", "---\nname: wrong\n---\n")
        before = {f: (self.tree / f).read_bytes() for f in files_under(self.tree)}
        builder.check_tree(self.tree)
        self.assertEqual({f: (self.tree / f).read_bytes() for f in files_under(self.tree)}, before)

    def test_missing_tree_is_refused(self):
        with self.assertRaises(ValueError):
            builder.check_tree(self.tree / "nowhere")


class RealPluginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agy-real-test-")
        self.dest = Path(self.temp.name) / "tree"

    def tearDown(self):
        self.temp.cleanup()

    def test_max_plugin_builds_a_tree_that_passes_the_check(self):
        builder.build_tree("9.9.9", self.dest)
        self.assertEqual(builder.check_tree(self.dest), [])

    def test_max_plugin_tree_holds_every_listed_skill(self):
        catalog = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        listed = next(p for p in catalog["plugins"] if p["name"] == "max")["skills"]
        builder.build_tree("9.9.9", self.dest)
        self.assertEqual(sorted(p.name for p in (self.dest / "skills").iterdir()), sorted(Path(e).name for e in listed))


class CommandLineTests(unittest.TestCase):
    BUILD = ROOT / ".agy-build"

    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, capture_output=True, text=True)

    def tearDown(self):
        shutil.rmtree(self.BUILD, ignore_errors=True)

    def test_build_writes_the_tree_into_agy_build(self):
        self.run_script("build", "9.9.9")
        self.assertEqual(json.loads((self.BUILD / "plugin.json").read_text())["version"], "9.9.9")

    def test_build_exits_zero(self):
        self.assertEqual(self.run_script("build", "9.9.9").returncode, 0)

    def test_check_after_build_exits_zero(self):
        self.run_script("build", "9.9.9")
        self.assertEqual(self.run_script("check").returncode, 0)

    def test_check_on_a_broken_tree_exits_one_without_a_traceback(self):
        self.run_script("build", "9.9.9")
        write(self.BUILD / "skills/broken/SKILL.md", "no frontmatter\n")
        result = self.run_script("check")
        self.assertEqual((result.returncode, "Traceback" in result.stderr), (1, False))

    def test_check_names_the_broken_skill_on_stderr(self):
        self.run_script("build", "9.9.9")
        write(self.BUILD / "skills/broken/SKILL.md", "no frontmatter\n")
        self.assertIn("skills/broken", self.run_script("check").stderr)

    def test_build_with_a_bad_version_exits_one_with_an_error_line(self):
        result = self.run_script("build", "1.2")
        self.assertEqual((result.returncode, result.stderr.startswith("error:")), (1, True))

    def test_unknown_command_exits_one_with_an_error_line(self):
        result = self.run_script("publish")
        self.assertEqual((result.returncode, result.stderr.startswith("error:")), (1, True))

    def test_build_folder_is_ignored_by_git(self):
        result = subprocess.run(["git", "check-ignore", "-q", ".agy-build/plugin.json"], cwd=ROOT)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
