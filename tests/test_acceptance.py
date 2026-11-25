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
agy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agy)

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
        return agy.build_tree(version, self.dest, self.root)


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
        """A listed skill's SKILL.md lands at skills/<skill-name>/SKILL.md."""
        self.fake.build()
        self.assertTrue((self.fake.dest / "skills/alpha/SKILL.md").is_file())

    def test_category_folder_is_dropped(self):
        """The skill's Category folder does not appear in the tree."""
        self.fake.build()
        self.assertFalse((self.fake.dest / "skills/kanban").exists())

    def test_unlisted_skill_is_left_out(self):
        """A skill in the checkout but off the max list does not reach the tree."""
        self.fake.skill("kanban/beta")
        self.fake.build()
        self.assertFalse((self.fake.dest / "skills/beta").exists())

    def test_list_is_read_from_the_max_entry_only(self):
        """Skills listed by a plugin other than max do not reach the tree."""
        self.fake.skill("kanban/beta")
        catalog = {"plugins": [
            {"name": "other", "skills": ["./kanban/beta"]},
            {"name": "max", "skills": ["./kanban/alpha"]},
        ]}
        write(self.fake.root / ".claude-plugin/marketplace.json", json.dumps(catalog))
        self.fake.build()
        self.assertEqual(sorted(p.name for p in (self.fake.dest / "skills").iterdir()), ["alpha"])

    def test_bundled_file_travels_with_its_skill(self):
        """A file beside SKILL.md, nested or not, is copied into the skill's tree folder."""
        write(self.fake.root / "kanban/alpha/refs/format.md", "# Format\n")
        self.fake.build()
        self.assertEqual((self.fake.dest / "skills/alpha/refs/format.md").read_text(), "# Format\n")

    def test_skill_files_are_copied_byte_for_byte(self):
        """SKILL.md reaches the tree with its bytes unchanged, mentions and punctuation included."""
        text = "---\nname: alpha\ndescription: Run /beta — then “stop”.\n---\n\nSee ../beta/x.md\n"
        write(self.fake.root / "kanban/alpha/SKILL.md", text.encode("utf-8"))
        self.fake.build()
        self.assertEqual((self.fake.dest / "skills/alpha/SKILL.md").read_bytes(), text.encode("utf-8"))

    def test_non_text_bundled_file_is_copied_byte_for_byte(self):
        """A binary bundled file reaches the tree unchanged."""
        blob = bytes(range(256))
        write(self.fake.root / "kanban/alpha/assets/logo.png", blob)
        self.fake.build()
        self.assertEqual((self.fake.dest / "skills/alpha/assets/logo.png").read_bytes(), blob)

    def test_dotfiles_are_skipped(self):
        """A file whose name starts with a dot is not copied."""
        write(self.fake.root / "kanban/alpha/.DS_Store", b"\x00")
        self.fake.build()
        self.assertFalse((self.fake.dest / "skills/alpha/.DS_Store").exists())

    def test_files_inside_dot_folders_are_skipped(self):
        """A file under a folder whose name starts with a dot is not copied."""
        write(self.fake.root / "kanban/alpha/.cache/notes.md", "scratch\n")
        self.fake.build()
        self.assertFalse((self.fake.dest / "skills/alpha/.cache").exists())

    def test_returns_skill_names_in_marketplace_order(self):
        """The build returns the folder names it wrote, in the order the list gives them."""
        self.fake.skill("behaviour/zeta")
        self.fake.skill("kanban/beta")
        self.fake.list(["./behaviour/zeta", "./kanban/alpha", "./kanban/beta"])
        self.assertEqual(self.fake.build(), ["zeta", "alpha", "beta"])

    def test_agents_md_is_copied_unchanged_to_the_root(self):
        """config/agy/AGENTS.md lands at the tree root with its bytes unchanged."""
        self.fake.build()
        self.assertEqual((self.fake.dest / "AGENTS.md").read_bytes(), RULES.encode())

    def test_no_agy_hooks_reach_the_tree(self):
        """Nothing from config/agy/hooks/ or config/agy/hooks.json is written to the tree."""
        self.fake.build()
        hooks = [f for f in files_under(self.fake.dest) if "hooks" in f]
        self.assertEqual(hooks, [])

    def test_tree_holds_only_skills_rules_and_manifest(self):
        """The tree holds the skills, AGENTS.md and plugin.json, and no other file."""
        write(self.fake.root / "kanban/alpha/refs/format.md", "# Format\n")
        self.fake.build()
        self.assertEqual(
            files_under(self.fake.dest),
            {"AGENTS.md", "plugin.json", "skills/alpha/SKILL.md", "skills/alpha/refs/format.md"},
        )

    def test_manifest_has_exactly_four_keys_in_order(self):
        """plugin.json holds name, version, displayName and description, in that order, and nothing else."""
        self.fake.build()
        self.assertEqual(list(json.loads(self.manifest_text())), ["name", "version", "displayName", "description"])

    def test_manifest_name_is_max(self):
        """The manifest names the plugin max."""
        self.fake.build()
        self.assertEqual(json.loads(self.manifest_text())["name"], "max")

    def test_manifest_carries_the_build_version(self):
        """The manifest's version is the version the build was given."""
        self.fake.build("4.5.6")
        self.assertEqual(json.loads(self.manifest_text())["version"], "4.5.6")

    def test_manifest_display_name_is_the_constant(self):
        """The manifest's displayName is DISPLAY_NAME."""
        self.fake.build()
        self.assertEqual(json.loads(self.manifest_text())["displayName"], agy.DISPLAY_NAME)

    def test_manifest_description_is_the_constant(self):
        """The manifest's description is DESCRIPTION."""
        self.fake.build()
        self.assertEqual(json.loads(self.manifest_text())["description"], agy.DESCRIPTION)

    def test_manifest_keeps_non_ascii_as_written(self):
        """Non-ASCII characters in the manifest are written as themselves, not as escapes."""
        self.fake.build()
        self.assertIn("Åstrand", self.manifest_text())

    def test_manifest_is_indented_two_spaces(self):
        """The manifest is formatted with a two-space indent."""
        self.fake.build()
        self.assertIn('\n  "name": "max",\n', self.manifest_text())

    def test_manifest_ends_in_a_newline(self):
        """The manifest file ends in a newline."""
        self.fake.build()
        self.assertTrue(self.manifest_text().endswith("}\n"))

    def test_rebuild_drops_what_an_earlier_build_left(self):
        """A build replaces the destination whole, so files from an older build are gone."""
        write(self.fake.dest / "skills/retired/SKILL.md", SKILL.format(name="retired"))
        self.fake.build()
        self.assertFalse((self.fake.dest / "skills/retired").exists())

    def test_building_twice_gives_the_same_bytes(self):
        """Two builds of the same version from the same checkout write identical trees."""
        self.fake.build()
        first = {f: (self.fake.dest / f).read_bytes() for f in files_under(self.fake.dest)}
        self.fake.build()
        second = {f: (self.fake.dest / f).read_bytes() for f in files_under(self.fake.dest)}
        self.assertEqual(first, second)

    def test_missing_listed_skill_folder_fails_the_build(self):
        """A listed skill whose folder does not exist raises ValueError."""
        self.fake.list(["./kanban/alpha", "./kanban/ghost"])
        with self.assertRaises(ValueError):
            self.fake.build()

    def test_failed_build_leaves_the_destination_as_it_was(self):
        """A build that raises ValueError writes nothing to the destination."""
        write(self.fake.dest / "keep.txt", "old\n")
        self.fake.list(["./kanban/alpha", "./kanban/ghost"])
        with self.assertRaises(ValueError):
            self.fake.build()
        self.assertEqual(files_under(self.fake.dest), {"keep.txt"})

    def test_version_without_three_numbers_is_refused(self):
        """A version that is not X.Y.Z raises ValueError."""
        for version in ("", "1.2", "v1.2.3", "1.2.3-rc1", "one.two.three"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.fake.build(version)

    def test_catalog_without_a_max_entry_is_refused(self):
        """A marketplace with no max plugin raises ValueError."""
        self.fake.list(["./kanban/alpha"], plugin="other")
        with self.assertRaises(ValueError):
            self.fake.build()

    def test_catalog_with_two_max_entries_is_refused(self):
        """A marketplace with two max plugins raises ValueError."""
        catalog = {"plugins": [{"name": "max", "skills": ["./kanban/alpha"]}] * 2}
        write(self.fake.root / ".claude-plugin/marketplace.json", json.dumps(catalog))
        with self.assertRaises(ValueError):
            self.fake.build()

    def test_max_entry_without_a_skills_list_is_refused(self):
        """A max plugin whose skills is missing or not a list of paths raises ValueError."""
        for skills in (None, "./kanban/alpha", [1]):
            entry = {"name": "max"} if skills is None else {"name": "max", "skills": skills}
            write(self.fake.root / ".claude-plugin/marketplace.json", json.dumps({"plugins": [entry]}))
            with self.subTest(skills=skills), self.assertRaises(ValueError):
                self.fake.build()

    def test_two_listed_folders_with_one_name_are_refused(self):
        """Two listed skills whose folders share a name raise ValueError."""
        self.fake.skill("developer-tools/alpha")
        self.fake.list(["./kanban/alpha", "./developer-tools/alpha"])
        with self.assertRaises(ValueError):
            self.fake.build()

    def test_missing_agents_md_is_refused(self):
        """A checkout without config/agy/AGENTS.md raises ValueError."""
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
        return [m for m in agy.check_tree(self.tree) if path in m]

    def test_valid_tree_passes(self):
        """A tree that keeps every rule yields no messages."""
        self.assertEqual(agy.check_tree(self.tree), [])

    def test_name_differing_from_folder_is_reported(self):
        """A SKILL.md whose frontmatter name differs from its folder name is reported."""
        self.skill("alpha", "---\nname: beta\ndescription: Does things.\n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_missing_name_is_reported(self):
        """A SKILL.md with no name line in its frontmatter is reported."""
        self.skill("alpha", "---\ndescription: Does things.\n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_name_outside_the_frontmatter_does_not_count(self):
        """A name line in the body, below the frontmatter, does not satisfy the name rule."""
        self.skill("alpha", "---\ndescription: Does things.\n---\nname: alpha\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_missing_description_is_reported(self):
        """A SKILL.md with no description line in its frontmatter is reported."""
        self.skill("alpha", "---\nname: alpha\n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_empty_description_is_reported(self):
        """A description line with no value and no folded text below it is reported."""
        self.skill("alpha", "---\nname: alpha\ndescription:\n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_folded_description_passes(self):
        """A description written as > followed by indented text passes."""
        self.skill("alpha", "---\nname: alpha\ndescription: >\n  Does things,\n  over two lines.\n---\n")
        self.assertEqual(agy.check_tree(self.tree), [])

    def test_literal_and_chomped_descriptions_pass(self):
        """A description written as |, >-, |-, >+ or |+ followed by indented text passes."""
        for marker in ("|", ">-", "|-", ">+", "|+"):
            self.skill("alpha", f"---\nname: alpha\ndescription: {marker}\n  Does things.\n---\n")
            with self.subTest(marker=marker):
                self.assertEqual(agy.check_tree(self.tree), [])

    def test_folded_description_with_no_text_is_reported(self):
        """A description of > with no indented text below it is reported."""
        self.skill("alpha", "---\nname: alpha\ndescription: >\n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_folded_description_with_only_blank_lines_is_reported(self):
        """A description of > followed only by blank lines is reported."""
        self.skill("alpha", "---\nname: alpha\ndescription: >\n\n   \n---\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_missing_name_and_description_give_two_messages(self):
        """A skill breaking the name rule and the description rule yields one message for each."""
        self.skill("alpha", "---\ntitle: Alpha\n---\n")
        self.assertEqual(len(self.mentions("skills/alpha")), 2)

    def test_folder_without_skill_md_is_reported(self):
        """A folder in skills/ with no SKILL.md is reported."""
        (self.tree / "skills/empty").mkdir()
        self.assertNotEqual(self.mentions("skills/empty"), [])

    def test_folder_without_skill_md_gives_one_message(self):
        """A folder with no SKILL.md yields one message, not one per frontmatter rule."""
        (self.tree / "skills/empty").mkdir()
        self.assertEqual(len(self.mentions("skills/empty")), 1)

    def test_skill_md_without_frontmatter_is_reported(self):
        """A SKILL.md that does not open with a --- line is reported."""
        self.skill("alpha", "# Alpha\n\nname: alpha\ndescription: Does things.\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_skill_md_without_frontmatter_gives_one_message(self):
        """A SKILL.md with no frontmatter yields one message, not one per frontmatter rule."""
        self.skill("alpha", "# Alpha\n")
        self.assertEqual(len(self.mentions("skills/alpha")), 1)

    def test_unclosed_frontmatter_is_reported(self):
        """A SKILL.md whose frontmatter has no closing --- line is reported."""
        self.skill("alpha", "---\nname: alpha\ndescription: Does things.\n")
        self.assertNotEqual(self.mentions("skills/alpha"), [])

    def test_skill_folder_not_in_kebab_case_is_reported(self):
        """A skill folder whose name is not lowercase kebab-case is reported."""
        for folder in ("Alpha", "alpha_beta", "alpha--beta", "-alpha"):
            with self.subTest(folder=folder):
                tree = Path(tempfile.mkdtemp(dir=self.temp.name))
                write(tree / "plugin.json", json.dumps(self.MANIFEST))
                write(tree / "skills" / folder / "SKILL.md", SKILL.format(name=folder))
                self.assertNotEqual([m for m in agy.check_tree(tree) if folder in m], [])

    def test_empty_skills_folder_is_reported(self):
        """A tree whose skills/ holds no folders is reported."""
        shutil.rmtree(self.tree / "skills/alpha")
        self.assertNotEqual(agy.check_tree(self.tree), [])

    def test_missing_skills_folder_is_reported(self):
        """A tree with no skills/ folder is reported."""
        shutil.rmtree(self.tree / "skills")
        self.assertNotEqual(agy.check_tree(self.tree), [])

    def test_manifest_name_not_in_kebab_case_is_reported(self):
        """A manifest name that is not lowercase kebab-case is reported."""
        for name in ("Max", "max_skills", "max skills", "max-", "", 7):
            self.manifest(dict(self.MANIFEST, name=name))
            with self.subTest(name=name):
                self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_kebab_case_manifest_name_passes(self):
        """A multi-word kebab-case manifest name with digits passes."""
        self.manifest(dict(self.MANIFEST, name="max-skills-2"))
        self.assertEqual(agy.check_tree(self.tree), [])

    def test_missing_manifest_name_is_reported(self):
        """A manifest with no name is reported."""
        self.manifest({k: v for k, v in self.MANIFEST.items() if k != "name"})
        self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_manifest_key_outside_the_schema_is_reported(self):
        """A manifest key that Antigravity's schema does not define is reported."""
        self.manifest(dict(self.MANIFEST, owner="Max"))
        self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_every_schema_key_is_allowed(self):
        """A manifest using every key Antigravity's schema defines passes."""
        self.manifest(dict(
            self.MANIFEST,
            **{"$schema": "https://antigravity.google/schemas/v1/plugin.json"},
            skills=[], disabled=False, author={"name": "Max"}, homepage="https://example.org",
            repository="https://example.org/repo", license="MIT", keywords=["skills"],
            logo="logo.png", suggestedPrompts=["Grill me"],
        ))
        self.assertEqual(agy.check_tree(self.tree), [])

    def test_missing_manifest_is_reported(self):
        """A tree with no plugin.json is reported."""
        (self.tree / "plugin.json").unlink()
        self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_missing_manifest_gives_one_message(self):
        """A tree with no plugin.json yields one manifest message, not one per manifest rule."""
        (self.tree / "plugin.json").unlink()
        self.assertEqual(len(self.mentions("plugin.json")), 1)

    def test_manifest_that_is_not_an_object_is_reported(self):
        """A plugin.json holding a JSON list instead of an object is reported."""
        self.manifest(["max"])
        self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_manifest_that_is_not_json_is_reported(self):
        """A plugin.json that does not parse as JSON is reported."""
        write(self.tree / "plugin.json", "{name: max")
        self.assertNotEqual(self.mentions("plugin.json"), [])

    def test_every_broken_rule_is_reported(self):
        """A tree breaking rules in several places reports each place."""
        self.manifest(dict(self.MANIFEST, name="Max"))
        self.skill("beta", "---\nname: gamma\ndescription: x\n---\n")
        self.skill("delta", "---\nname: delta\n---\n")
        messages = agy.check_tree(self.tree)
        self.assertEqual(
            [any(path in m for m in messages) for path in ("plugin.json", "skills/beta", "skills/delta")],
            [True, True, True],
        )

    def test_manifest_messages_come_before_skill_messages(self):
        """Manifest messages are listed before any skill message."""
        self.skill("alpha", "---\nname: wrong\ndescription: x\n---\n")
        self.manifest(dict(self.MANIFEST, name="Max"))
        messages = agy.check_tree(self.tree)
        self.assertIn("plugin.json", messages[0])

    def test_skill_messages_are_ordered_by_folder_name(self):
        """Skill messages follow the skill folder names in sorted order."""
        for folder in ("zeta", "beta", "mu"):
            self.skill(folder, "---\nname: wrong\ndescription: x\n---\n")
        messages = agy.check_tree(self.tree)
        order = [next(f for f in ("zeta", "beta", "mu") if f"skills/{f}" in m) for m in messages]
        self.assertEqual(order, ["beta", "mu", "zeta"])

    def test_check_leaves_the_tree_unchanged(self):
        """Checking a tree changes no file in it."""
        self.skill("beta", "---\nname: wrong\n---\n")
        before = {f: (self.tree / f).read_bytes() for f in files_under(self.tree)}
        agy.check_tree(self.tree)
        self.assertEqual({f: (self.tree / f).read_bytes() for f in files_under(self.tree)}, before)

    def test_missing_tree_is_refused(self):
        """Checking a folder that does not exist raises ValueError."""
        with self.assertRaises(ValueError):
            agy.check_tree(self.tree / "nowhere")


class RealPluginTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="agy-real-test-")
        self.dest = Path(self.temp.name) / "tree"

    def tearDown(self):
        self.temp.cleanup()

    def test_max_plugin_builds_a_tree_that_passes_the_check(self):
        """The real max Plugin builds into a tree that breaks no Antigravity rule."""
        agy.build_tree("9.9.9", self.dest)
        self.assertEqual(agy.check_tree(self.dest), [])

    def test_max_plugin_tree_holds_every_listed_skill(self):
        """The real build writes one skills/ folder per entry in the max list."""
        catalog = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        listed = next(p for p in catalog["plugins"] if p["name"] == "max")["skills"]
        agy.build_tree("9.9.9", self.dest)
        self.assertEqual(sorted(p.name for p in (self.dest / "skills").iterdir()), sorted(Path(e).name for e in listed))


class CommandLineTests(unittest.TestCase):
    BUILD = ROOT / ".agy-build"

    def run_script(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=ROOT, capture_output=True, text=True)

    def tearDown(self):
        shutil.rmtree(self.BUILD, ignore_errors=True)

    def test_build_writes_the_tree_into_agy_build(self):
        """build VERSION writes a manifest carrying VERSION into .agy-build/."""
        self.run_script("build", "9.9.9")
        self.assertEqual(json.loads((self.BUILD / "plugin.json").read_text())["version"], "9.9.9")

    def test_build_exits_zero(self):
        """build VERSION on the real repo exits 0."""
        self.assertEqual(self.run_script("build", "9.9.9").returncode, 0)

    def test_check_after_build_exits_zero(self):
        """check on a freshly built tree exits 0."""
        self.run_script("build", "9.9.9")
        self.assertEqual(self.run_script("check").returncode, 0)

    def test_check_on_a_broken_tree_exits_one_without_a_traceback(self):
        """check exits 1 cleanly, with no Python traceback, when the built tree breaks a rule."""
        self.run_script("build", "9.9.9")
        write(self.BUILD / "skills/broken/SKILL.md", "no frontmatter\n")
        result = self.run_script("check")
        self.assertEqual((result.returncode, "Traceback" in result.stderr), (1, False))

    def test_check_names_the_broken_skill_on_stderr(self):
        """check prints a message naming the broken skill to stderr."""
        self.run_script("build", "9.9.9")
        write(self.BUILD / "skills/broken/SKILL.md", "no frontmatter\n")
        self.assertIn("skills/broken", self.run_script("check").stderr)

    def test_build_with_a_bad_version_exits_one_with_an_error_line(self):
        """build with a version that is not X.Y.Z exits 1 and prints only an error: line."""
        result = self.run_script("build", "1.2")
        self.assertEqual((result.returncode, result.stderr.startswith("error:")), (1, True))

    def test_unknown_command_exits_one_with_an_error_line(self):
        """A command other than build or check exits 1 and prints only an error: line."""
        result = self.run_script("publish")
        self.assertEqual((result.returncode, result.stderr.startswith("error:")), (1, True))

    def test_build_folder_is_ignored_by_git(self):
        """.agy-build/ is ignored by git, so the tree stays untracked."""
        result = subprocess.run(["git", "check-ignore", "-q", ".agy-build/plugin.json"], cwd=ROOT)
        self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
