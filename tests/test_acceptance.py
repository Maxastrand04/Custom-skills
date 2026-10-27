import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("release", ROOT / "scripts/release.py")
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)

MANIFESTS = (
    ".claude-plugin/marketplace.json",
    "plugins/max/plugin.json",
    "ci/.claude-plugin/plugin.json",
)


def catalog_entry(catalog, name):
    return next(p for p in catalog["plugins"] if p["name"] == name)


class LastReleaseTests(unittest.TestCase):
    def test_no_tags_means_no_release(self):
        """With no tags at all there is no earlier release."""
        self.assertIsNone(release.last_release([]))

    def test_tags_without_a_version_shape_mean_no_release(self):
        """Tags that aren't vX.Y.Z don't count as releases."""
        self.assertIsNone(release.last_release(["latest", "release", "v2.0"]))

    def test_versions_compare_as_numbers(self):
        """v1.10.0 is a later release than v1.9.0."""
        self.assertEqual(release.last_release(["v1.9.0", "v1.10.0", "v1.2.0"]), "1.10.0")

    def test_other_tags_are_skipped(self):
        """A highest release is found among tags that aren't releases."""
        self.assertEqual(release.last_release(["v3.0.0-rc1", "v1.2.3", "latest"]), "1.2.3")


class PlanReleaseTests(unittest.TestCase):
    def test_first_release_is_1_0_0_whatever_the_commits_say(self):
        """With no earlier release, a breaking change still releases 1.0.0."""
        self.assertEqual(release.plan_release(None, ["feat!: Rework everything"]).version, "1.0.0")

    def test_first_release_is_1_0_0_with_no_raising_commits(self):
        """With no earlier release, commits that raise nothing still release 1.0.0."""
        self.assertEqual(release.plan_release(None, ["Add license"]).version, "1.0.0")

    def test_fix_raises_patch(self):
        """A fix raises the last number."""
        self.assertEqual(release.plan_release("1.2.3", ["fix: Stop a crash"]).version, "1.2.4")

    def test_feat_raises_minor_and_resets_patch(self):
        """A feature raises the middle number and resets the last."""
        self.assertEqual(release.plan_release("1.2.3", ["feat: Add a skill"]).version, "1.3.0")

    def test_bang_raises_major_and_resets_the_rest(self):
        """A type with "!" raises the first number and resets the others."""
        self.assertEqual(release.plan_release("1.2.3", ["feat!: Rename skills"]).version, "2.0.0")

    def test_breaking_change_line_in_body_raises_major(self):
        """A body line starting "BREAKING CHANGE:" makes the commit breaking."""
        message = "feat: Rename skills (#30)\n\nBREAKING CHANGE: old names stop working"
        self.assertEqual(release.plan_release("1.2.3", [message]).version, "2.0.0")

    def test_breaking_change_mid_line_is_not_breaking(self):
        """"BREAKING CHANGE:" only counts at the start of a body line."""
        message = "fix: Stop a crash\n\nThis is not a BREAKING CHANGE: nothing moves"
        self.assertEqual(release.plan_release("1.2.3", [message]).version, "1.2.4")

    def test_largest_raise_wins(self):
        """Several commits raise the version once, by the largest kind among them."""
        messages = ["fix: One", "feat: Two", "fix: Three"]
        self.assertEqual(release.plan_release("1.2.3", messages).version, "1.3.0")

    def test_type_matches_in_any_case(self):
        """"Fix:" counts the same as "fix:"."""
        self.assertEqual(release.plan_release("1.2.3", ["Fix: Stop a crash"]).version, "1.2.4")

    def test_scope_is_allowed(self):
        """A "(scope)" after the type keeps the commit conventional."""
        self.assertEqual(release.plan_release("1.2.3", ["fix(ci): Stop a crash"]).version, "1.2.4")

    def test_other_types_release_nothing(self):
        """Commits of types other than feat and fix leave nothing to release."""
        with self.assertRaisesRegex(ValueError, "no feat, fix, or breaking change"):
            release.plan_release("1.2.3", ["chore: Tidy", "docs: Reword", "refactor: Split"])

    def test_no_commits_since_last_release_releases_nothing(self):
        """No commits since the last release leave nothing to release."""
        with self.assertRaisesRegex(ValueError, "no feat, fix, or breaking change"):
            release.plan_release("1.2.3", [])

    def test_unconventional_commits_release_nothing(self):
        """Commits without a type prefix leave nothing to release."""
        with self.assertRaisesRegex(ValueError, "no feat, fix, or breaking change"):
            release.plan_release("1.2.3", ["Merge pull request #19 from x/y", "Add license"])

    def test_codex_build_commit_releases_nothing(self):
        """The commit the per-merge Codex build makes doesn't raise the version."""
        with self.assertRaisesRegex(ValueError, "no feat, fix, or breaking change"):
            release.plan_release("1.2.3", ["chore: Build Codex marketplace skills"])

    def test_unconventional_subjects_are_listed(self):
        """The plan lists the subjects of commits without a type prefix, oldest first."""
        messages = ["Add license\n\nMIT, with notices", "fix: Stop a crash", "Merge pull request #19"]
        plan = release.plan_release("1.2.3", messages)
        self.assertEqual(plan.unconventional, ["Add license", "Merge pull request #19"])

    def test_deciding_lists_the_raising_subjects(self):
        """The plan lists the subjects of the commits that raised the version, oldest first."""
        messages = ["chore: Tidy", "fix: Stop a crash (#3)\n\nDetails", "Add license", "feat: Add a skill (#4)"]
        plan = release.plan_release("1.2.3", messages)
        self.assertEqual(plan.deciding, ["fix: Stop a crash (#3)", "feat: Add a skill (#4)"])

    def test_release_commit_finishes_the_unfinished_release(self):
        """A release commit since the last tag makes the plan that release's version."""
        messages = ["fix: Stop a crash", "chore(release): v1.2.4"]
        self.assertEqual(release.plan_release("1.2.3", messages).version, "1.2.4")

    def test_commits_after_a_release_commit_do_not_change_its_version(self):
        """Work merged after an unfinished release commit never moves its number."""
        messages = ["fix: Stop a crash", "chore(release): v1.2.4", "feat!: Rename skills"]
        self.assertEqual(release.plan_release("1.2.3", messages).version, "1.2.4")

    def test_two_release_commits_are_refused(self):
        """Two release commits since the last tag stop the plan."""
        messages = ["fix: One", "chore(release): v1.2.4", "fix: Two", "chore(release): v1.2.5"]
        with self.assertRaises(ValueError):
            release.plan_release("1.2.3", messages)

    def test_release_commit_not_above_last_release_is_refused(self):
        """A release commit naming a version already released stops the plan."""
        with self.assertRaises(ValueError):
            release.plan_release("1.2.3", ["fix: Stop a crash", "chore(release): v1.2.3"])


class ReleaseNotesTests(unittest.TestCase):
    MIXED = [
        "fix: Stop a crash (#3)",
        "feat: Add a skill (#4)",
        "feat!: Rename skills (#5)",
    ]

    def test_groups_appear_in_order(self):
        """Breaking changes come before Features, which come before Fixes."""
        notes = release.release_notes(self.MIXED)
        positions = [notes.index(h) for h in ("Breaking changes", "Features", "Fixes")]
        self.assertEqual(positions, sorted(positions))

    def test_entries_drop_the_type_prefix(self):
        """An entry reads without its "feat:" prefix."""
        self.assertNotIn("feat:", release.release_notes(["feat: Add a skill (#4)"]))

    def test_entries_keep_the_pr_number(self):
        """An entry keeps the subject text and its PR number."""
        self.assertIn("Add a skill (#4)", release.release_notes(["feat: Add a skill (#4)"]))

    def test_breaking_feature_is_listed_only_under_breaking_changes(self):
        """A breaking feat sits under Breaking changes and not under Features."""
        notes = release.release_notes(self.MIXED)
        self.assertNotIn("Rename skills", notes[notes.index("Features"):])

    def test_breaking_change_line_in_body_lists_under_breaking_changes(self):
        """A commit made breaking by its body appears under Breaking changes."""
        notes = release.release_notes(["fix: Change paths\n\nBREAKING CHANGE: old paths fail"])
        self.assertIn("Breaking changes", notes)

    def test_empty_group_is_left_out(self):
        """With no features, there is no Features heading."""
        self.assertNotIn("Features", release.release_notes(["fix: Stop a crash (#3)"]))

    def test_commits_that_raise_nothing_are_left_out(self):
        """Other types and unconventional commits don't appear in the notes."""
        notes = release.release_notes(["fix: Stop a crash", "chore: Tidy up", "Add license"])
        self.assertFalse("Tidy up" in notes or "Add license" in notes)


class WriteVersionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="custom-skills-test-")
        self.root = Path(self.temp.name)
        for manifest in MANIFESTS:
            (self.root / manifest).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / manifest, self.root / manifest)

    def tearDown(self):
        self.temp.cleanup()

    def read(self, manifest):
        return json.loads((self.root / manifest).read_text())

    def test_claude_max_entry_gets_the_version(self):
        """The max entry in the Claude catalog carries the written version."""
        release.write_version("1.2.3", self.root)
        entry = catalog_entry(self.read(".claude-plugin/marketplace.json"), "max")
        self.assertEqual(entry["version"], "1.2.3")

    def test_codex_plugin_gets_the_version(self):
        """The Codex max manifest carries the written version."""
        release.write_version("1.2.3", self.root)
        self.assertEqual(self.read("plugins/max/plugin.json")["version"], "1.2.3")

    def test_kanban_ci_plugin_gets_the_version(self):
        """The kanban-ci manifest carries the written version."""
        release.write_version("1.2.3", self.root)
        self.assertEqual(self.read("ci/.claude-plugin/plugin.json")["version"], "1.2.3")

    def test_kanban_ci_catalog_entry_stays_without_a_version(self):
        """kanban-ci's version lives in its plugin.json only, never also in the catalog."""
        release.write_version("1.2.3", self.root)
        entry = catalog_entry(self.read(".claude-plugin/marketplace.json"), "kanban-ci")
        self.assertNotIn("version", entry)

    def test_nothing_else_in_the_catalog_changes(self):
        """Apart from the max entry's version, the Claude catalog is unchanged."""
        before = self.read(".claude-plugin/marketplace.json")
        release.write_version("1.2.3", self.root)
        after = self.read(".claude-plugin/marketplace.json")
        catalog_entry(after, "max").pop("version")
        catalog_entry(before, "max").pop("version", None)
        self.assertEqual(after, before)

    def test_nothing_else_in_the_plugin_manifests_changes(self):
        """Apart from the version, both plugin.json files are unchanged."""
        paths = ("plugins/max/plugin.json", "ci/.claude-plugin/plugin.json")
        before = [dict(self.read(p), version="1.2.3") for p in paths]
        release.write_version("1.2.3", self.root)
        self.assertEqual([self.read(p) for p in paths], before)

    def test_writing_the_same_version_again_changes_nothing(self):
        """A second write of the version the manifests hold leaves every byte alone."""
        release.write_version("1.2.3", self.root)
        first = [(self.root / m).read_bytes() for m in MANIFESTS]
        release.write_version("1.2.3", self.root)
        self.assertEqual([(self.root / m).read_bytes() for m in MANIFESTS], first)

    def test_version_without_three_numbers_is_refused(self):
        """A version that isn't X.Y.Z raises ValueError."""
        with self.assertRaises(ValueError):
            release.write_version("1.2", self.root)

    def test_version_with_v_prefix_is_refused(self):
        """The version is written bare, so "v1.2.3" raises ValueError."""
        with self.assertRaises(ValueError):
            release.write_version("v1.2.3", self.root)

    def test_missing_manifest_is_refused(self):
        """A missing manifest raises ValueError."""
        (self.root / "ci/.claude-plugin/plugin.json").unlink()
        with self.assertRaises(ValueError):
            release.write_version("1.2.3", self.root)


class CodexBuildTests(unittest.TestCase):
    def test_codex_builder_no_longer_raises_the_version(self):
        """The Codex builder offers no way to raise the plugin version."""
        with tempfile.TemporaryDirectory(prefix="custom-skills-test-") as temp:
            root = Path(temp)
            (root / "scripts").mkdir()
            shutil.copy2(ROOT / "scripts/build-codex.py", root / "scripts/build-codex.py")
            manifest = root / "plugins/max/plugin.json"
            manifest.parent.mkdir(parents=True)
            shutil.copy2(ROOT / "plugins/max/plugin.json", manifest)
            before = manifest.read_text()
            subprocess.run(
                [sys.executable, str(root / "scripts/build-codex.py"), "--bump-version"],
                capture_output=True, timeout=20,
            )
            self.assertEqual(manifest.read_text(), before)


if __name__ == "__main__":
    unittest.main()
