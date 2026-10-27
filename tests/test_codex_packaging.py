import contextlib
import importlib.util
import json
import os
import pty
import select
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("build_codex", ROOT / "scripts/build-codex.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="custom-skills-test-")
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def build_brainstorming(self):
        builder.sync(self.root, builder.build_files(["brainstorming"], builder.live_skills()), False)

    def test_excluded_skill_can_supply_shared_files(self):
        self.build_brainstorming()
        self.assertTrue((self.root / "brainstorming/../architect-ticket/RECORD-FORMAT.md").is_file())

    def test_excluded_skill_supplying_shared_files_is_not_available(self):
        self.build_brainstorming()
        self.assertEqual(list(self.root.glob("*/SKILL.md")), [self.root / "brainstorming/SKILL.md"])

    def test_codex_skill_drops_the_claude_invocation_key(self):
        files = builder.build_files(["brainstorming"], builder.live_skills())
        self.assertNotIn(b"disable-model-invocation:", files["brainstorming/SKILL.md"])

    def test_skill_hidden_from_the_model_stays_hidden_on_codex(self):
        files = builder.build_files(["brainstorming"], builder.live_skills())
        self.assertIn(b"allow_implicit_invocation: false", files["brainstorming/agents/openai.yaml"])

    def test_skill_open_to_the_model_gets_no_codex_policy(self):
        files = builder.build_files(["unslop"], builder.live_skills())
        self.assertNotIn("unslop/agents/openai.yaml", files)

    def test_skill_mentions_become_codex_mentions(self):
        files = builder.build_files(["brainstorming"], builder.live_skills())
        self.assertIn(b"$grilling", files["brainstorming/SKILL.md"])

    def test_marketplace_skill_mentions_carry_the_plugin_prefix(self):
        files = builder.build_files(["brainstorming"], builder.live_skills(), "max:")
        self.assertIn(b"$max:grilling", files["brainstorming/SKILL.md"])

    def build_then_drop_pro_con(self):
        skills = builder.live_skills()
        builder.sync(self.root, builder.build_files(["unslop", "pro-con"], skills), False)
        return builder.build_files(["unslop"], skills)

    def test_check_refuses_output_holding_an_excluded_skill(self):
        files = self.build_then_drop_pro_con()
        with self.assertRaises(ValueError):
            builder.sync(self.root, files, True)

    def test_rebuild_removes_excluded_skills(self):
        files = self.build_then_drop_pro_con()
        builder.sync(self.root, files, False)
        self.assertFalse((self.root / "pro-con/SKILL.md").exists())

    def test_check_detects_source_changes(self):
        files = builder.build_files(["unslop"], builder.live_skills())
        builder.sync(self.root, files, False)
        changed = dict(files, **{"unslop/SKILL.md": files["unslop/SKILL.md"] + b"\nChanged source.\n"})
        with self.assertRaises(ValueError):
            builder.sync(self.root, changed, True)

    def add_unexpected_skill(self):
        files = builder.build_files(["unslop"], builder.live_skills())
        builder.sync(self.root, files, False)
        unexpected = self.root / "personal/SKILL.md"
        unexpected.parent.mkdir()
        unexpected.write_text("Private skill")
        return files, unexpected

    def test_check_refuses_an_unexpected_skill(self):
        files, _ = self.add_unexpected_skill()
        with self.assertRaises(ValueError):
            builder.sync(self.root, files, True)

    def test_rebuild_refuses_an_unexpected_skill(self):
        files, _ = self.add_unexpected_skill()
        with self.assertRaises(ValueError):
            builder.sync(self.root, files, False)

    def test_rebuild_leaves_an_unexpected_skill_alone(self):
        files, unexpected = self.add_unexpected_skill()
        with contextlib.suppress(ValueError):
            builder.sync(self.root, files, False)
        self.assertEqual(unexpected.read_text(), "Private skill")

    def installer(self):
        """A copy of the repo and an install target already holding an unrelated unslop folder."""
        repo = self.root / "repo"
        for category in builder.CATEGORIES:
            shutil.copytree(ROOT / category, repo / category)
        shutil.copytree(ROOT / "scripts", repo / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(ROOT / "install.sh", repo / "install.sh")
        target = self.root / "installed"
        target.mkdir()
        (target / "unslop").mkdir()
        (target / "unslop/keep.txt").write_text("User's existing skill")
        return repo, target

    def install(self, repo, target, *names):
        return subprocess.run(
            ["bash", str(repo / "install.sh"), "--codex", *names],
            env=dict(os.environ, CUSTOM_SKILLS_CODEX_DIR=str(target)),
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20,
        )

    def test_installer_links_the_named_skill(self):
        repo, target = self.installer()
        self.install(repo, target, "brainstorming")
        self.assertTrue((target / "brainstorming").is_symlink())

    def test_installed_skill_reaches_shared_files(self):
        repo, target = self.installer()
        self.install(repo, target, "brainstorming")
        self.assertTrue((target / "brainstorming/../architect-ticket/RECORD-FORMAT.md").is_file())

    def test_reinstall_brings_source_edits_to_codex(self):
        repo, target = self.installer()
        self.install(repo, target, "brainstorming")
        source = repo / "developer-tools/brainstorming/SKILL.md"
        source.write_text(source.read_text() + "\nSource edit reaches Codex.\n")
        self.install(repo, target, "brainstorming")
        self.assertIn("Source edit reaches Codex.", (target / "brainstorming/SKILL.md").read_text())

    def test_installer_refuses_to_replace_an_unrelated_skill(self):
        repo, target = self.installer()
        self.assertNotEqual(self.install(repo, target, "unslop").returncode, 0)

    def test_installer_keeps_an_unrelated_skill(self):
        repo, target = self.installer()
        self.install(repo, target, "unslop")
        self.assertEqual((target / "unslop/keep.txt").read_text(), "User's existing skill")

    def test_codex_marketplace_ships_exactly_the_claude_marketplace_skills(self):
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        plugin = next(p for p in marketplace["plugins"] if p["name"] == "max")
        expected = {Path(path).name for path in plugin["skills"]}
        actual = {p.parent.name for p in (ROOT / "plugins/max/skills").glob("*/SKILL.md")}
        self.assertEqual(actual, expected)

    def test_skill_mentions_change_but_paths_and_urls_do_not(self):
        names = ["grilling", "pr-ticket"]
        source = "\n".join([
            "Run `/grilling` first.",
            "```",
            "Next     /pr-ticket opens the PR",
            "```",
            "See ~/.claude/skills/grilling and ../grilling/notes.md",
            "https://example.com/grilling",
            "/grilling/notes.md and /grillings",
        ])
        expected = "\n".join([
            "Run `$max:grilling` first.",
            "```",
            "Next     $max:pr-ticket opens the PR",
            "```",
            "See ~/.claude/skills/grilling and ../grilling/notes.md",
            "https://example.com/grilling",
            "/grilling/notes.md and /grillings",
        ])
        self.assertEqual(builder.convert(source, names, prefix="max:"), expected)

    def test_generated_shared_file_links_resolve(self):
        output = ROOT / "plugins/max/skills"
        for path in output.rglob("*.md"):
            for owner, filename in builder.SIBLING_FILE.findall(path.read_text()):
                with self.subTest(path=str(path), link=f"{owner}/{filename}"):
                    self.assertTrue((path.parent / ".." / owner / filename).is_file())

    def menu_target(self):
        """An install target holding a foreign link and a stale link from this repo."""
        target = self.root / "installed"
        target.mkdir()
        foreign = target / "foreign"
        foreign.symlink_to(self.root / "another-repo", target_is_directory=True)
        stale = target / "retired-skill"
        stale.symlink_to(ROOT / "archive/retired-skill", target_is_directory=True)
        # A short PATH exercises the numbered picker even on machines with fzf.
        bin_dir = self.root / "bin"
        bin_dir.mkdir()
        (bin_dir / "python3").symlink_to(shutil.which("python3"))
        return target

    def menu(self, target, answers):
        env = dict(
            os.environ, CUSTOM_SKILLS_CODEX_DIR=str(target), PATH=f"{self.root / 'bin'}:/usr/bin:/bin",
        )
        master, slave = pty.openpty()
        proc = subprocess.Popen(
            ["bash", str(ROOT / "install.sh"), "--codex"],
            env=env, stdin=slave, stdout=slave, stderr=slave,
        )
        os.close(slave)
        output = b""
        try:
            os.write(master, answers.encode())
            deadline = time.monotonic() + 20
            while proc.poll() is None and time.monotonic() < deadline:
                if select.select([master], [], [], 0.1)[0]:
                    try:
                        output += os.read(master, 65536)
                    except OSError:
                        break
            proc.wait(timeout=2)
            self.assertEqual(proc.returncode, 0, output.decode(errors="replace"))
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.wait()
            os.close(master)

    def test_interactive_menu_links_a_picked_skill(self):
        target = self.menu_target()
        self.menu(target, "none\n1\n\ny\n")
        self.assertTrue((target / "architect-ticket").is_symlink())

    def test_interactive_menu_removes_a_stale_link_owned_by_this_repo(self):
        target = self.menu_target()
        self.menu(target, "none\n1\n\ny\n")
        self.assertFalse((target / "retired-skill").is_symlink())

    def test_interactive_menu_keeps_a_link_owned_by_another_repo(self):
        target = self.menu_target()
        self.menu(target, "none\n1\n\ny\n")
        self.assertTrue((target / "foreign").is_symlink())

    def test_interactive_menu_removes_an_unpicked_skill(self):
        target = self.menu_target()
        self.menu(target, "none\n1\n\ny\n")
        self.menu(target, "none\n\ny\n")
        self.assertFalse((target / "architect-ticket").is_symlink())

    def test_codex_builder_leaves_the_plugin_version_alone(self):
        root = self.root
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
