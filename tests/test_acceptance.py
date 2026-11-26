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


def git(cwd, *args):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def snapshot(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob("*") if p.is_file()}


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


class Remote:
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


class PublishCase(unittest.TestCase):
    def setUp(self):
        patcher = mock.patch.dict(os.environ, GIT_ENV)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.temp = tempfile.TemporaryDirectory(prefix="agy-publish-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.tree = self.base / "tree"
        write_tree(self.tree)
        self.remote = Remote(self.base)
        self.remote.seed()

    def publish(self, version=VERSION, tree=None, remote=None):
        return builder.publish_tree(version, tree or self.tree, remote or self.remote.url)


class PublishTreeTests(PublishCase):
    def test_tree_skill_lands_on_the_default_branch(self):
        """A skill in the tree is on the remote's default branch after the publish."""
        self.publish()
        self.assertIn("skills/alpha/SKILL.md", self.remote.files())

    def test_tree_manifest_lands_at_the_root(self):
        """The tree's plugin.json is at the remote's root after the publish."""
        self.publish()
        self.assertEqual(self.remote.show("plugin.json"), (self.tree / "plugin.json").read_bytes())

    def test_file_bytes_are_unchanged(self):
        """A binary file reaches the remote byte for byte."""
        self.publish()
        self.assertEqual(self.remote.show("skills/alpha/icon.bin"), bytes(range(256)))

    def test_commit_is_titled_with_the_version(self):
        """The pushed commit is titled chore(release): vX.Y.Z."""
        self.publish()
        self.assertEqual(self.remote.subject(), TITLE)

    def test_commit_author_name_is_the_actions_bot(self):
        """The pushed commit's author is github-actions[bot]."""
        self.publish()
        self.assertEqual(self.remote.run("log", "-1", "--format=%an", "main"), BOT_NAME)

    def test_commit_author_email_is_the_actions_bot(self):
        """The pushed commit's author email is the Actions bot's noreply address."""
        self.publish()
        self.assertEqual(self.remote.run("log", "-1", "--format=%ae", "main"), BOT_EMAIL)

    def test_committer_is_the_actions_bot(self):
        """The pushed commit's committer is github-actions[bot]."""
        self.publish()
        self.assertEqual(self.remote.run("log", "-1", "--format=%cn", "main"), BOT_NAME)

    def test_commit_lands_on_top_of_the_existing_history(self):
        """The publish adds one commit whose parent is the remote's previous head."""
        before = self.remote.head()
        self.publish()
        self.assertEqual(self.remote.run("rev-parse", "main^"), before)

    def test_tag_names_the_pushed_commit(self):
        """The tag vX.Y.Z on the remote points at the commit pushed to the default branch."""
        self.publish()
        self.assertEqual(self.remote.run("rev-parse", f"{TAG}^{{commit}}"), self.remote.head())

    def test_tag_is_lightweight(self):
        """The tag is a lightweight tag, a plain pointer to the commit."""
        self.publish()
        self.assertEqual(self.remote.run("cat-file", "-t", TAG), "commit")

    def test_returns_the_tagged_commit_hash(self):
        """publish_tree returns the full hash of the commit it tagged."""
        self.assertEqual(self.publish(), self.remote.head())

    def test_tree_is_left_unchanged(self):
        """Publishing never changes the tree it publishes."""
        before = snapshot(self.tree)
        self.publish()
        self.assertEqual(snapshot(self.tree), before)

    def test_commit_is_made_even_when_no_file_changed(self):
        """A remote that already holds the tree's files still gets a release commit."""
        shutil.rmtree(self.remote.work / "skills")
        for path, content in snapshot(self.tree).items():
            if path != "README.md" and not path.startswith(".github/"):
                write(self.remote.work / path, content)
        (self.remote.work / ".gitignore").unlink()
        self.remote.commit("docs: Match the tree")
        self.publish()
        self.assertEqual(self.remote.subject(), TITLE)


class RemovedFileTests(PublishCase):
    def test_skill_dropped_from_the_list_is_deleted(self):
        """A skill the remote holds but the tree lacks is gone after the publish."""
        self.publish()
        self.assertNotIn("skills/old/SKILL.md", self.remote.files())

    def test_root_dotfile_not_in_the_tree_is_deleted(self):
        """A tracked root file outside the kept paths and absent from the tree is deleted."""
        self.publish()
        self.assertNotIn(".gitignore", self.remote.files())


class KeptPathTests(PublishCase):
    def test_root_readme_is_unchanged(self):
        """README.md at the remote root keeps its bytes even though the tree has its own."""
        self.publish()
        self.assertEqual(self.remote.show("README.md"), Remote.README.encode())

    def test_github_file_is_unchanged(self):
        """A file under .github/ keeps its bytes even though the tree has one at the same path."""
        self.publish()
        self.assertEqual(self.remote.show(".github/workflows/ci.yml"), Remote.CI.encode())

    def test_github_file_absent_from_the_tree_stays(self):
        """A file under .github/ that the tree lacks is not deleted."""
        self.publish()
        self.assertEqual(self.remote.show(".github/FUNDING.yml"), Remote.FUNDING.encode())

    def test_nested_readme_is_published(self):
        """Only the root README.md is kept; a skill's own README.md is published."""
        self.publish()
        self.assertEqual(self.remote.show("skills/alpha/README.md"), b"Alpha's own readme.\n")


class AlreadyTaggedTests(PublishCase):
    def setUp(self):
        super().setUp()
        self.remote.run("tag", TAG, "main")
        self.before = self.remote.head()

    def test_returns_none(self):
        """publish_tree returns None when the remote already has the tag."""
        self.assertIsNone(self.publish())

    def test_default_branch_is_unchanged(self):
        """Nothing is pushed to the default branch when the remote already has the tag."""
        self.publish()
        self.assertEqual(self.remote.head(), self.before)

    def test_tag_is_unchanged(self):
        """The existing tag keeps pointing where it did."""
        self.publish()
        self.assertEqual(self.remote.run("rev-parse", TAG), self.before)


class UntaggedReleaseCommitTests(PublishCase):
    """An earlier run pushed the release commit and then failed to push the tag."""

    def setUp(self):
        super().setUp()
        self.remote.commit(TITLE)
        self.before = self.remote.head()

    def test_no_second_release_commit_is_made(self):
        """The default branch's head stays the release commit already there."""
        self.publish()
        self.assertEqual(self.remote.head(), self.before)

    def test_existing_release_commit_is_tagged(self):
        """The tag lands on the release commit an earlier run pushed."""
        self.publish()
        self.assertEqual(self.remote.run("rev-parse", f"{TAG}^{{commit}}"), self.before)


class MovedAheadTests(PublishCase):
    """The remote's default branch gains a commit between the clone and the push.

    Clones read from self.remote, while pushes to that URL go to self.ahead,
    which holds the same history plus one newer commit.
    """

    def setUp(self):
        super().setUp()
        self.ahead = Remote(self.base, "ahead.git")
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
        """A default branch that moved ahead rejects the push, and publish_tree raises RuntimeError naming it."""
        self.refused_publish()

    def test_newer_commit_survives(self):
        """The push is not forced, so the commit that landed meanwhile stays on the branch."""
        self.refused_publish()
        self.assertEqual(self.ahead.head(), self.ahead_head)

    def test_nothing_is_tagged(self):
        """A failed commit push leaves the remote with no tag."""
        self.refused_publish()
        self.assertEqual(self.ahead.tags(), [])


class FailureTests(PublishCase):

    def test_remote_with_no_default_branch_raises_runtime_error(self):
        """A remote with no commits has no default branch, and publish_tree raises RuntimeError naming git."""
        empty = Remote(self.base, "empty.git")
        with self.assertRaisesRegex(RuntimeError, "git"):
            self.publish(remote=empty.url)

    def test_remote_with_no_default_branch_gets_no_tag(self):
        """A failed publish to a remote with no default branch tags nothing."""
        empty = Remote(self.base, "empty.git")
        with self.assertRaisesRegex(RuntimeError, "git"):
            self.publish(remote=empty.url)
        self.assertEqual(empty.tags(), [])

    def test_failed_clone_raises_runtime_error_naming_it(self):
        """A clone that fails raises RuntimeError naming the clone."""
        with self.assertRaisesRegex(RuntimeError, "clone"):
            self.publish(remote=str(self.base / "nowhere.git"))


class InvalidInputTests(PublishCase):
    def test_version_without_three_numbers_is_refused(self):
        """A version that isn't X.Y.Z raises ValueError."""
        with self.assertRaises(ValueError):
            self.publish(version="1.2")

    def test_version_with_v_prefix_is_refused(self):
        """A version written as vX.Y.Z raises ValueError."""
        with self.assertRaises(ValueError):
            self.publish(version=TAG)

    def test_missing_tree_is_refused(self):
        """A tree that is not an existing folder raises ValueError."""
        with self.assertRaises(ValueError):
            self.publish(tree=self.base / "no-tree")

    def test_tree_without_a_manifest_is_refused(self):
        """A tree with no plugin.json raises ValueError."""
        (self.tree / "plugin.json").unlink()
        with self.assertRaises(ValueError):
            self.publish()

    def test_tree_built_for_another_version_is_refused(self):
        """A tree whose plugin.json names another version raises ValueError."""
        write_tree(self.tree, version="1.2.2")
        with self.assertRaises(ValueError):
            self.publish()

    def test_bad_input_is_found_before_the_clone(self):
        """A bad version raises ValueError even when the remote can't be cloned."""
        with self.assertRaises(ValueError):
            self.publish(version="1.2", remote=str(self.base / "nowhere.git"))

    def test_refused_input_pushes_nothing(self):
        """A refused tree leaves the remote's default branch as it was."""
        before = self.remote.head()
        write_tree(self.tree, version="1.2.2")
        with self.assertRaises(ValueError):
            self.publish()
        self.assertEqual(self.remote.head(), before)


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
        """A publish that pushes prints the version and the commit it tagged."""
        result = self.run_publish(VERSION, self.remote.url)
        self.assertIn(f"Published {TAG} as {self.remote.head()}", result.stdout)

    def test_publish_reads_the_built_tree(self):
        """The command publishes .agy-build/ from the checkout it runs in."""
        self.run_publish(VERSION, self.remote.url)
        self.assertIn("skills/alpha/SKILL.md", self.remote.files())

    def test_already_published_prints_so(self):
        """When the tag exists the command says nothing was pushed."""
        self.remote.run("tag", TAG, "main")
        result = self.run_publish(VERSION, self.remote.url)
        self.assertIn(f"{TAG} is already published, nothing pushed", result.stdout)

    def test_already_published_exits_zero(self):
        """When the tag exists the command still succeeds."""
        self.remote.run("tag", TAG, "main")
        self.assertEqual(self.run_publish(VERSION, self.remote.url).returncode, 0)

    def test_failed_clone_prints_an_error_line(self):
        """A failed git command prints error: <reason> to stderr, not a traceback."""
        result = self.run_publish(VERSION, str(self.base / "nowhere.git"))
        self.assertTrue(result.stderr.startswith("error: "), result.stderr)


if __name__ == "__main__":
    unittest.main()
