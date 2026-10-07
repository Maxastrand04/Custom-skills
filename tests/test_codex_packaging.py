import importlib.util
import json
import os
import pty
import select
import shutil
import subprocess
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

    def test_excluded_skill_can_supply_shared_files_without_becoming_available(self):
        skills = builder.live_skills()
        files = builder.build_files(["brainstorming"], skills)
        builder.sync(self.root, files, False)
        selected = self.root / "brainstorming"
        shared = selected / ".." / "architect-ticket" / "RECORD-FORMAT.md"
        self.assertTrue(shared.is_file())
        self.assertFalse((self.root / "architect-ticket/SKILL.md").exists())
        self.assertEqual(list(self.root.glob("*/SKILL.md")), [selected / "SKILL.md"])

    def test_codex_policy_preserves_source_invocation_rules(self):
        files = builder.build_files(["brainstorming", "unslop"], builder.live_skills())
        self.assertNotIn(b"disable-model-invocation:", files["brainstorming/SKILL.md"])
        self.assertIn(b"allow_implicit_invocation: false", files["brainstorming/agents/openai.yaml"])
        self.assertNotIn("unslop/agents/openai.yaml", files)
        self.assertIn(b"$grilling", files["brainstorming/SKILL.md"])
        marketplace = builder.build_files(["brainstorming"], builder.live_skills(), "max:")
        self.assertIn(b"$max:grilling", marketplace["brainstorming/SKILL.md"])

    def test_rebuild_removes_excluded_skills_and_check_detects_source_changes(self):
        skills = builder.live_skills()
        first = builder.build_files(["unslop", "pro-con"], skills)
        builder.sync(self.root, first, False)
        second = builder.build_files(["unslop"], skills)
        with self.assertRaises(ValueError):
            builder.sync(self.root, second, True)
        builder.sync(self.root, second, False)
        self.assertFalse((self.root / "pro-con/SKILL.md").exists())
        builder.sync(self.root, second, True)
        changed = dict(second)
        changed["unslop/SKILL.md"] += b"\nChanged source.\n"
        with self.assertRaises(ValueError):
            builder.sync(self.root, changed, True)

    def test_unexpected_skill_cannot_silently_enter_marketplace_output(self):
        files = builder.build_files(["unslop"], builder.live_skills())
        builder.sync(self.root, files, False)
        unexpected = self.root / "personal/SKILL.md"
        unexpected.parent.mkdir()
        unexpected.write_text("Private skill")
        for check in (True, False):
            with self.assertRaises(ValueError):
                builder.sync(self.root, files, check)
        self.assertEqual(unexpected.read_text(), "Private skill")

    def test_installer_adds_refreshes_and_preserves_existing_unrelated_skills(self):
        repo = self.root / "repo"
        for category in builder.CATEGORIES:
            shutil.copytree(ROOT / category, repo / category)
        shutil.copytree(ROOT / "scripts", repo / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copy2(ROOT / "install.sh", repo / "install.sh")
        target = self.root / "installed"
        target.mkdir()
        unrelated = target / "unslop"
        unrelated.mkdir()
        (unrelated / "keep.txt").write_text("User's existing skill")
        env = dict(os.environ, CUSTOM_SKILLS_CODEX_DIR=str(target))

        def install(*names):
            return subprocess.run(
                ["bash", str(repo / "install.sh"), "--codex", *names],
                env=env, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=20,
            )

        result = install("brainstorming")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        installed = target / "brainstorming"
        self.assertTrue(installed.is_symlink())
        self.assertTrue((installed / "../architect-ticket/RECORD-FORMAT.md").is_file())
        source = repo / "developer-tools/brainstorming/SKILL.md"
        source.write_text(source.read_text() + "\nSource edit reaches Codex.\n")
        result = install("brainstorming")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Source edit reaches Codex.", (installed / "SKILL.md").read_text())
        result = install("unslop")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((unrelated / "keep.txt").read_text(), "User's existing skill")

    def test_codex_marketplace_ships_exactly_the_claude_marketplace_skills(self):
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
        plugin = next(p for p in marketplace["plugins"] if p["name"] == "max")
        expected = {Path(path).name for path in plugin["skills"]}
        actual = {p.parent.name for p in (ROOT / "plugins/max/skills").glob("*/SKILL.md")}
        self.assertEqual(actual, expected)

    def test_bump_version_raises_only_the_last_number(self):
        manifest = self.root / "plugin.json"
        manifest.write_text('{\n  "name": "max",\n  "version": "1.4.9",\n  "x": 1\n}\n')
        self.assertEqual(builder.bump_version(manifest), "1.4.10")
        self.assertEqual(manifest.read_text(), '{\n  "name": "max",\n  "version": "1.4.10",\n  "x": 1\n}\n')

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
                self.assertTrue((path.parent / ".." / owner / filename).is_file(), str(path))

    def test_interactive_menu_removes_only_links_owned_by_this_repo(self):
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
        env = dict(os.environ, CUSTOM_SKILLS_CODEX_DIR=str(target), PATH=f"{bin_dir}:/usr/bin:/bin")

        def menu(answers):
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

        menu("none\n1\n\ny\n")
        self.assertTrue((target / "architect-ticket").is_symlink())
        self.assertFalse(stale.is_symlink())
        self.assertTrue(foreign.is_symlink())
        menu("none\n\ny\n")
        self.assertFalse((target / "architect-ticket").is_symlink())
        self.assertTrue(foreign.is_symlink())


if __name__ == "__main__":
    unittest.main()
