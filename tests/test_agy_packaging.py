import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts/build-agy.py"
spec = importlib.util.spec_from_file_location("build_agy", SCRIPT)
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

SKILL = "---\nname: {name}\ndescription: Does {name} things.\n---\n\nBody of {name}.\n"
RULES = "# Rules\n\nStay plain.\n"
VERSION = "1.2.3"
TAG = "v1.2.3"
TITLE = "chore(release): v1.2.3"
BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"

# Git run by the tests and by publish_tree ignores the user's own config.
GIT_ENV = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.com",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.com",
}


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


def git(cwd, *args):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def snapshot(folder):
    return {f: (folder / f).read_bytes() for f in files_under(folder)}


def write_tree(folder, version=VERSION):
    """A plugin tree as build_tree writes it, plus a root README.md and .github/ file of its own."""
    manifest = {"name": "max", "version": version, "displayName": "Max", "description": "Skills."}
    write(folder / "plugin.json", json.dumps(manifest, indent=2) + "\n")
    write(folder / "AGENTS.md", "# Rules\n")
    write(folder / "skills/alpha/SKILL.md", "---\nname: alpha\ndescription: Alpha.\n---\n")
    write(folder / "skills/alpha/README.md", "Alpha's own readme.\n")
    write(folder / "skills/alpha/icon.bin", bytes(range(256)))
    write(folder / "README.md", "The tree's readme, which must not land.\n")
    write(folder / ".github/workflows/ci.yml", "name: from the tree\n")


class FakeRemote:
    """A local bare repo standing in for Custom-skills-agy, default branch main."""

    README = "Custom-skills-agy readme.\n"
    CI = "name: agy ci\n"
    FUNDING = "github: someone\n"

    def __init__(self, base, name="remote.git"):
        self.path = base / name
        self.url = str(self.path)
        self.work = base / f"{name}-work"
        git(base, "init", "-q", "--bare", "-b", "main", str(self.path))
        git(base, "init", "-q", "-b", "main", str(self.work))
        git(self.work, "remote", "add", "origin", self.url)

    def seed(self):
        """Give the remote what Custom-skills-agy holds before the first publish."""
        write(self.work / "README.md", self.README)
        write(self.work / ".github/workflows/ci.yml", self.CI)
        write(self.work / ".github/FUNDING.yml", self.FUNDING)
        write(self.work / "skills/old/SKILL.md", "---\nname: old\ndescription: Old.\n---\n")
        write(self.work / ".gitignore", "*.tmp\n")
        self.commit("chore(release): v1.2.2")

    def commit(self, message):
        git(self.work, "add", "-A")
        git(self.work, "commit", "-q", "--allow-empty", "-m", message)
        git(self.work, "push", "-q", "origin", "HEAD:refs/heads/main")

    def run(self, *args):
        return git(self.path, *args)

    def head(self):
        return self.run("rev-parse", "main")

    def files(self):
        return set(self.run("ls-tree", "-r", "--name-only", "main").splitlines())

    def show(self, path):
        return subprocess.run(
            ["git", "show", f"main:{path}"], cwd=self.path, capture_output=True, check=True
        ).stdout

    def subject(self):
        return self.run("log", "-1", "--format=%s", "main")

    def tags(self):
        return self.run("tag", "--list").splitlines()


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


class PublishCase(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.dict(os.environ, GIT_ENV)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.temp = tempfile.TemporaryDirectory(prefix="agy-publish-test-")
        self.base = Path(self.temp.name)
        self.tree = self.base / "tree"
        write_tree(self.tree)
        self.remote = FakeRemote(self.base)
        self.remote.seed()

    def tearDown(self):
        self.temp.cleanup()

    def publish(self, version=VERSION, tree=None, remote=None):
        return builder.publish_tree(version, tree or self.tree, remote or self.remote.url)


class PublishTreeTests(PublishCase):
    def test_tree_skill_lands_on_the_default_branch(self):
        self.publish()
        self.assertIn("skills/alpha/SKILL.md", self.remote.files())

    def test_tree_manifest_lands_at_the_root(self):
        self.publish()
        self.assertEqual(self.remote.show("plugin.json"), (self.tree / "plugin.json").read_bytes())

    def test_file_bytes_are_unchanged(self):
        self.publish()
        self.assertEqual(self.remote.show("skills/alpha/icon.bin"), bytes(range(256)))

    def test_commit_is_titled_with_the_version(self):
        self.publish()
        self.assertEqual(self.remote.subject(), TITLE)

    def test_commit_author_name_is_the_actions_bot(self):
        self.publish()
        self.assertEqual(self.remote.run("log", "-1", "--format=%an", "main"), BOT_NAME)

    def test_commit_author_email_is_the_actions_bot(self):
        self.publish()
        self.assertEqual(self.remote.run("log", "-1", "--format=%ae", "main"), BOT_EMAIL)

    def test_committer_is_the_actions_bot(self):
        self.publish()
        self.assertEqual(self.remote.run("log", "-1", "--format=%cn", "main"), BOT_NAME)

    def test_commit_lands_on_top_of_the_existing_history(self):
        before = self.remote.head()
        self.publish()
        self.assertEqual(self.remote.run("rev-parse", "main^"), before)

    def test_tag_names_the_pushed_commit(self):
        self.publish()
        self.assertEqual(self.remote.run("rev-parse", f"{TAG}^{{commit}}"), self.remote.head())

    def test_tag_is_lightweight(self):
        self.publish()
        self.assertEqual(self.remote.run("cat-file", "-t", TAG), "commit")

    def test_returns_the_tagged_commit_hash(self):
        self.assertEqual(self.publish(), self.remote.head())

    def test_tree_is_left_unchanged(self):
        before = snapshot(self.tree)
        self.publish()
        self.assertEqual(snapshot(self.tree), before)

    def test_commit_is_made_even_when_no_file_changed(self):
        shutil.rmtree(self.remote.work / "skills")
        for path, content in snapshot(self.tree).items():
            if path != "README.md" and not path.startswith(".github/"):
                write(self.remote.work / path, content)
        (self.remote.work / ".gitignore").unlink()
        self.remote.commit("docs: Match the tree")
        self.publish()
        self.assertEqual(self.remote.subject(), TITLE)

    def test_folder_that_became_a_file_is_published(self):
        write(self.remote.work / "skills/alpha/notes/old/one.md", "old\n")
        self.remote.commit("docs: Add notes")
        write(self.tree / "skills/alpha/notes", "now a file\n")
        self.publish()
        self.assertEqual(self.remote.show("skills/alpha/notes"), b"now a file\n")

    def test_skill_dropped_from_the_list_is_deleted(self):
        self.publish()
        self.assertNotIn("skills/old/SKILL.md", self.remote.files())

    def test_root_dotfile_not_in_the_tree_is_deleted(self):
        self.publish()
        self.assertNotIn(".gitignore", self.remote.files())

    def test_root_readme_is_unchanged(self):
        self.publish()
        self.assertEqual(self.remote.show("README.md"), FakeRemote.README.encode())

    def test_github_file_is_unchanged(self):
        self.publish()
        self.assertEqual(self.remote.show(".github/workflows/ci.yml"), FakeRemote.CI.encode())

    def test_github_file_absent_from_the_tree_stays(self):
        self.publish()
        self.assertEqual(self.remote.show(".github/FUNDING.yml"), FakeRemote.FUNDING.encode())

    def test_nested_readme_is_published(self):
        self.publish()
        self.assertEqual(self.remote.show("skills/alpha/README.md"), b"Alpha's own readme.\n")

    def test_version_without_three_numbers_is_refused(self):
        write_tree(self.tree, version="1.2")
        with self.assertRaises(ValueError):
            self.publish(version="1.2")

    def test_version_with_v_prefix_is_refused(self):
        write_tree(self.tree, version=TAG)
        with self.assertRaises(ValueError):
            self.publish(version=TAG)

    def test_missing_tree_is_refused(self):
        with self.assertRaises(ValueError):
            self.publish(tree=self.base / "no-tree")

    def test_tree_without_a_manifest_is_refused(self):
        (self.tree / "plugin.json").unlink()
        with self.assertRaises(ValueError):
            self.publish()

    def test_tree_built_for_another_version_is_refused(self):
        write_tree(self.tree, version="1.2.2")
        with self.assertRaises(ValueError):
            self.publish()

    def test_bad_input_is_found_before_the_clone(self):
        with self.assertRaises(ValueError):
            self.publish(version="1.2", remote=str(self.base / "nowhere.git"))

    def test_refused_input_pushes_nothing(self):
        before = self.remote.head()
        write_tree(self.tree, version="1.2.2")
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(self.remote.head(), before)

    def test_remote_with_no_default_branch_raises_runtime_error(self):
        empty = FakeRemote(self.base, "empty.git")
        with self.assertRaisesRegex(RuntimeError, "git"):
            self.publish(remote=empty.url)

    def test_failed_clone_raises_runtime_error_naming_it(self):
        with self.assertRaisesRegex(RuntimeError, "clone"):
            self.publish(remote=str(self.base / "nowhere.git"))

    def test_empty_negative_or_suffixed_version_is_refused(self):
        for version in ("", "-1.2.3", "1.2.3-rc1"):
            write_tree(self.tree, version=version)
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.publish(version=version)

    def test_version_that_is_not_a_string_is_refused(self):
        for version in (None, 123):
            write_tree(self.tree, version=version)
            with self.subTest(version=version), self.assertRaises(ValueError):
                self.publish(version=version)

    def test_tree_whose_manifest_names_no_version_is_refused(self):
        for text in ("{name: max", '["max"]', "{}"):
            write(self.tree / "plugin.json", text)
            with self.subTest(manifest=text), self.assertRaises(ValueError):
                self.publish()

    def test_git_folder_in_the_tree_is_not_copied(self):
        write(self.tree / ".git/config", "not a git config\n")
        self.publish()
        self.assertEqual(self.remote.subject(), TITLE)

    def test_refused_tag_push_raises_runtime_error(self):
        hook = self.remote.path / "hooks/update"
        write(hook, '#!/bin/sh\ncase "$1" in refs/tags/*) exit 1 ;; esac\n')
        hook.chmod(0o755)
        with self.assertRaisesRegex(RuntimeError, "push"):
            self.publish()


class PublishAlreadyTaggedTests(PublishCase):
    def setUp(self):
        super().setUp()
        self.remote.run("tag", TAG, "main")
        self.before = self.remote.head()

    def test_returns_none(self):
        self.assertIsNone(self.publish())

    def test_default_branch_is_unchanged(self):
        self.publish()
        self.assertEqual(self.remote.head(), self.before)

    def test_tag_is_unchanged(self):
        self.publish()
        self.assertEqual(self.remote.run("rev-parse", TAG), self.before)


class PublishUntaggedCommitTests(PublishCase):
    """An earlier run pushed the release commit and then failed to push the tag."""

    def setUp(self):
        super().setUp()
        self.remote.commit(TITLE)
        self.before = self.remote.head()

    def test_no_second_release_commit_is_made(self):
        self.publish()
        self.assertEqual(self.remote.head(), self.before)

    def test_existing_release_commit_is_tagged(self):
        self.publish()
        self.assertEqual(self.remote.run("rev-parse", f"{TAG}^{{commit}}"), self.before)


class PublishToMovedBranchTests(PublishCase):
    """The remote's default branch gains a commit between the clone and the push.

    Clones read from self.remote, while pushes to that URL go to self.ahead,
    which holds the same history plus one newer commit.
    """

    def setUp(self):
        super().setUp()
        self.ahead = FakeRemote(self.base, "ahead.git")
        git(self.ahead.work, "pull", "-q", self.remote.url, "main")
        self.ahead.commit("docs: Land while the release runs")
        self.ahead_head = self.ahead.head()
        redirect = {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": f"url.{self.ahead.url}.pushInsteadOf",
            "GIT_CONFIG_VALUE_0": self.remote.url,
        }
        patcher = mock.patch.dict(os.environ, redirect)
        patcher.start()
        self.addCleanup(patcher.stop)

    def refused_publish(self):
        """Publish, expecting the git push to be refused."""
        with self.assertRaisesRegex(RuntimeError, "push"):
            self.publish()

    def test_push_is_refused_with_runtime_error(self):
        self.refused_publish()

    def test_newer_commit_survives(self):
        self.refused_publish()
        self.assertEqual(self.ahead.head(), self.ahead_head)

    def test_nothing_is_tagged(self):
        self.refused_publish()
        self.assertEqual(self.ahead.tags(), [])


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

    def test_build_reads_the_source_folder_when_given(self):
        with tempfile.TemporaryDirectory(prefix="agy-source-test-") as temp:
            fake = FakeCheckout(Path(temp))
            fake.skill("kanban/alpha")
            fake.list(["./kanban/alpha"])
            self.run_script("build", "9.9.9", str(fake.root))
        self.assertEqual([p.name for p in (self.BUILD / "skills").glob("*")], ["alpha"])

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
        result = self.run_script("deploy")
        self.assertEqual((result.returncode, result.stderr.startswith("error:")), (1, True))

    def test_build_folder_is_ignored_by_git(self):
        result = subprocess.run(["git", "check-ignore", "-q", ".agy-build/plugin.json"], cwd=ROOT)
        self.assertEqual(result.returncode, 0)


class PublishCommandLineTests(PublishCase):
    """build-agy.py publish VERSION REMOTE, run from a copy of the script beside a built tree."""

    def setUp(self):
        super().setUp()
        self.checkout = self.base / "checkout"
        write(self.checkout / "scripts/build-agy.py", SCRIPT.read_bytes())
        write_tree(self.checkout / ".agy-build")

    def run_publish(self, *args):
        return subprocess.run(
            [sys.executable, str(self.checkout / "scripts/build-agy.py"), "publish", *args],
            cwd=self.checkout, capture_output=True, text=True, timeout=60,
        )

    def test_publish_prints_the_pushed_commit(self):
        result = self.run_publish(VERSION, self.remote.url)
        self.assertIn(f"Published {TAG} as {self.remote.head()}", result.stdout)

    def test_publish_reads_the_built_tree(self):
        self.run_publish(VERSION, self.remote.url)
        self.assertIn("skills/alpha/SKILL.md", self.remote.files())

    def test_already_published_prints_so(self):
        self.remote.run("tag", TAG, "main")
        result = self.run_publish(VERSION, self.remote.url)
        self.assertIn(f"{TAG} is already published, nothing pushed", result.stdout)

    def test_already_published_exits_zero(self):
        self.remote.run("tag", TAG, "main")
        self.assertEqual(self.run_publish(VERSION, self.remote.url).returncode, 0)

    def test_failed_clone_exits_one_with_an_error_line(self):
        result = self.run_publish(VERSION, str(self.base / "nowhere.git"))
        self.assertEqual(
            (result.returncode, result.stderr.startswith("error: ")), (1, True), result.stderr
        )

    def test_publish_without_a_remote_exits_one_with_an_error_line(self):
        result = self.run_publish(VERSION)
        self.assertEqual((result.returncode, result.stderr.startswith("error: usage:")), (1, True))


if __name__ == "__main__":
    unittest.main()
