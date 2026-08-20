#!/usr/bin/env python3
"""Offline tests for the public generation harness."""

from __future__ import annotations

import importlib.util
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "tools" / "eval_harness.py"
SKILL = ROOT / "skills" / "moodle-plugin-development"


def load_harness_module():
    spec = importlib.util.spec_from_file_location("momopda_eval_harness", HARNESS)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load evaluation harness")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EvalHarnessTest(unittest.TestCase):
    """Exercises preparation, client failures, records, and summaries."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="momopda-eval-test-")
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(self, *arguments: object, expected: int = 0) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, "-I", "-B", str(HARNESS), *(str(value) for value in arguments)]
        result = subprocess.run(command, cwd=ROOT, check=False, capture_output=True, text=True)
        self.assertEqual(expected, result.returncode, result.stderr or result.stdout)
        return result

    def prepare(self, name: str, task: str = "filter-modern-contract", condition: str = "none", *extra: object) -> Path:
        destination = self.root / name
        self.run_cli(
            "prepare",
            "--task",
            task,
            "--condition",
            condition,
            "--output",
            destination,
            "--run-id",
            name,
            *extra,
        )
        return destination

    @staticmethod
    def record(run_dir: Path) -> dict[str, object]:
        return json.loads((run_dir / "run.json").read_text(encoding="utf-8"))

    def test_all_declared_tasks_prepare_without_source_changes(self) -> None:
        document = json.loads((ROOT / "evals" / "public" / "tasks.json").read_text(encoding="utf-8"))
        fixture = ROOT / "skills" / "moodle-plugin-development" / "assets" / "fixtures" / "filter_momopda"
        setup = ROOT / "evals" / "public" / "setups" / "filter-modern-contract" / "filter.php"
        fixture_before = {path.relative_to(fixture): path.read_bytes() for path in fixture.rglob("*") if path.is_file()}
        setup_before = setup.read_bytes()
        for task in document["tasks"]:
            run_dir = self.prepare(f"prepare-{task['id']}", task["id"])
            self.assertTrue((run_dir / "agent" / "plugin" / "version.php").is_file())
        fixture_after = {path.relative_to(fixture): path.read_bytes() for path in fixture.rglob("*") if path.is_file()}
        self.assertEqual(fixture_before, fixture_after)
        self.assertEqual(setup_before, setup.read_bytes())

    def test_filter_setup_and_skill_conditions_are_isolated(self) -> None:
        candidate = self.prepare("candidate", condition="candidate")
        plugin = candidate / "agent" / "plugin"
        self.assertTrue((plugin / "filter.php").is_file())
        self.assertFalse((plugin / "classes" / "text_filter.php").exists())
        candidate_skill = candidate / "client-config" / "opencode" / "skills" / "moodle-plugin-development"
        self.assertTrue((candidate_skill / "SKILL.md").is_file())
        self.assertFalse(candidate_skill.is_symlink())

        none = self.prepare("none")
        self.assertFalse((none / "agent" / ".opencode").exists())

        released_source = self.root / "released-skill"
        shutil.copytree(SKILL, released_source)
        released = self.prepare(
            "released",
            "filter-modern-contract",
            "released",
            "--skill",
            released_source,
        )
        released_skill = released / "client-config" / "opencode" / "skills" / "moodle-plugin-development"
        self.assertTrue((released_skill / "SKILL.md").is_file())
        self.assertNotEqual(candidate, released)

        result = self.run_cli(
            "prepare",
            "--task",
            "filter-modern-contract",
            "--condition",
            "candidate",
            "--output",
            candidate,
            expected=1,
        )
        self.assertIn("refusing to reuse", result.stderr)

    def test_released_condition_rejects_candidate_skill(self) -> None:
        result = self.run_cli(
            "prepare",
            "--task",
            "filter-modern-contract",
            "--condition",
            "released",
            "--skill",
            SKILL,
            "--output",
            self.root / "bad-released",
            expected=1,
        )
        self.assertIn("cannot silently reuse", result.stderr)

    @unittest.skipUnless(shutil.which("opencode"), "OpenCode is unavailable")
    def test_opencode_discovers_only_the_selected_skill(self) -> None:
        candidate = self.prepare("discover-candidate", condition="candidate")
        none = self.prepare("discover-none")
        for run_dir, expected in ((candidate, 1), (none, 0)):
            environment = dict(os.environ)
            environment.update(
                {
                    "OPENCODE_DISABLE_EXTERNAL_SKILLS": "1",
                    "OPENCODE_DISABLE_CLAUDE_CODE_SKILLS": "1",
                    "OPENCODE_DISABLE_PROJECT_CONFIG": "1",
                    "OPENCODE_PURE": "1",
                    "XDG_CONFIG_HOME": str(run_dir / "client-config"),
                }
            )
            result = subprocess.run(
                ["opencode", "debug", "skill", "--pure"],
                cwd=run_dir / "agent" / "plugin",
                env=environment,
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            skills = json.loads(result.stdout)
            matches = [skill for skill in skills if skill.get("name") == "moodle-plugin-development"]
            self.assertEqual(expected, len(matches))

    def test_fake_client_success_and_failure_modes(self) -> None:
        expected = {
            "success": ("succeeded", "incomplete", True),
            "nonzero": ("client_error", "error", False),
            "timeout": ("timeout", "timeout", False),
            "malformed": ("malformed", "error", False),
        }
        runs: list[Path] = []
        for outcome, (execution_status, run_status, usage_available) in expected.items():
            run_dir = self.prepare(f"fake-{outcome}")
            timeout = "0.05" if outcome == "timeout" else "5"
            self.run_cli(
                "run",
                "--run-dir",
                run_dir,
                "--client",
                "fake",
                "--fake-outcome",
                outcome,
                "--timeout",
                timeout,
            )
            record = self.record(run_dir)
            self.assertEqual(execution_status, record["execution"]["status"])
            self.assertEqual(run_status, record["status"])
            self.assertEqual(usage_available, record["execution"]["usage_available"])
            self.assertTrue((run_dir / "artifacts" / "events.jsonl").is_file())
            self.assertTrue((run_dir / "artifacts" / "stderr.log").is_file())
            self.assertTrue(all(check["status"] == "incomplete" for check in record["checks"]))
            self.run_cli("validate", run_dir)
            runs.append(run_dir)

        success = self.record(runs[0])
        self.assertEqual("fake-client.txt", success["workspace"]["changes"][0]["path"])
        summary = self.run_cli("summarize", *runs)
        summary_document = json.loads(summary.stdout)
        self.assertEqual(4, summary_document["total"])
        self.assertEqual(1, summary_document["counts"]["incomplete"])
        self.assertEqual(2, summary_document["counts"]["error"])
        self.assertEqual(1, summary_document["counts"]["timeout"])
        self.assertIsNone(summary_document["ranking"])

    def test_opencode_without_model_is_incomplete_not_pass(self) -> None:
        run_dir = self.prepare("skipped-real")
        self.run_cli("run", "--run-dir", run_dir, "--client", "opencode", "--timeout", "1")
        record = self.record(run_dir)
        self.assertEqual("skipped", record["execution"]["status"])
        self.assertEqual("incomplete", record["status"])
        self.assertFalse(record["execution"]["usage_available"])
        self.assertTrue(all(check["status"] == "incomplete" for check in record["checks"]))

    def test_missing_exact_php_marks_grading_incomplete(self) -> None:
        run_dir = self.prepare("grade-prerequisite")
        self.run_cli("run", "--run-dir", run_dir, "--client", "fake")
        fake_php = self.root / "fake-php"
        fake_php.write_text("#!/bin/sh\nprintf '9.9'\n", encoding="utf-8")
        fake_php.chmod(0o755)
        self.run_cli(
            "grade",
            "--run-dir",
            run_dir,
            "--plugin-ci",
            fake_php,
            "--php",
            fake_php,
        )
        record = self.record(run_dir)
        self.assertEqual("incomplete", record["status"])
        self.assertIn("requires PHP 8.1", record["checks"][0]["evidence"])
        self.assertFalse((run_dir / "grading").exists())

    def test_grader_rejects_candidate_control_files(self) -> None:
        run_dir = self.prepare("grader-control")
        self.run_cli(
            "run",
            "--run-dir",
            run_dir,
            "--client",
            "fake",
            "--fake-outcome",
            "control-file",
        )
        fake_php = self.root / "php81"
        fake_php.write_text("#!/bin/sh\nprintf '8.1'\n", encoding="utf-8")
        fake_php.chmod(0o755)
        fake_ci = self.root / "moodle-plugin-ci"
        fake_ci.write_text("#!/bin/sh\nprintf 'Moodle Plugin CI 4.5.11\\n'\n", encoding="utf-8")
        fake_ci.chmod(0o755)
        self.run_cli(
            "grade",
            "--run-dir",
            run_dir,
            "--plugin-ci",
            fake_ci,
            "--php",
            fake_php,
        )
        record = self.record(run_dir)
        self.assertEqual("fail", record["status"])
        self.assertTrue(all(check["status"] == "fail" for check in record["checks"]))
        self.assertIn("phpunit.xml", record["checks"][0]["evidence"])
        self.assertIn("classes/.moodle-plugin-ci.yml", record["checks"][0]["evidence"])
        self.assertEqual("Moodle Plugin CI 4.5.11", record["revisions"]["grader"]["plugin_ci_version"])

    def test_safe_relative_paths_reject_traversal_and_ambiguity(self) -> None:
        harness = load_harness_module()
        self.assertEqual("classes/text_filter.php", harness.safe_relative("classes/text_filter.php", "test").as_posix())
        for value in ("", ".", "../file", "classes/../file", "/absolute", "classes\\file"):
            with self.subTest(value=value), self.assertRaises(harness.HarnessError):
                harness.safe_relative(value, "test")

    def test_record_validation_rejects_inconsistent_nested_values(self) -> None:
        harness = load_harness_module()
        run_dir = self.prepare("record-mutations")
        prepared = json.loads((run_dir / "prepare.json").read_text(encoding="utf-8"))
        record = self.record(run_dir)
        mutations = []

        passing_without_checks = copy.deepcopy(record)
        passing_without_checks["status"] = "pass"
        mutations.append(passing_without_checks)

        invalid_hash = copy.deepcopy(record)
        invalid_hash["workspace"]["input_sha256"] = "invalid"
        mutations.append(invalid_hash)

        escaping_artifact = copy.deepcopy(record)
        escaping_artifact["artifacts"]["events"] = "../events.jsonl"
        mutations.append(escaping_artifact)

        invalid_revision = copy.deepcopy(record)
        invalid_revision["revisions"] = {}
        mutations.append(invalid_revision)

        negative_duration = copy.deepcopy(record)
        negative_duration["timing"]["duration_ms"] = -1
        mutations.append(negative_duration)

        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(harness.HarnessError):
                harness.validate_record(mutation, prepared["task"])

    def test_event_redaction_terminal_order_and_usage_detection(self) -> None:
        harness = load_harness_module()
        line = json.dumps(
            {
                "type": "text",
                "authorization": "Bearer sk-secret",
                "access_token": "secret-token",
                "text": "Authorization: Bearer sk-secret",
            }
        )
        events, malformed = harness.parse_events(line, ("sk-secret", "secret-token"))
        self.assertFalse(malformed)
        rendered = json.dumps(events)
        self.assertNotIn("sk-secret", rendered)
        self.assertNotIn("secret-token", rendered)
        common_secret = harness.redact_text("/tmp/moodle PGPASSWORD=moodle", ("moodle",))
        self.assertIn("/tmp/moodle", common_secret)
        self.assertNotIn("PGPASSWORD=moodle", common_secret)

        partial_usage = [
            {
                "type": "step_finish",
                "part": {
                    "reason": "stop",
                    "tokens": {"input": 1, "output": 1, "cache": {"read": 0, "write": 0}},
                    "cost": 0,
                },
            }
        ]
        self.assertIsNone(harness.event_usage(partial_usage))


if __name__ == "__main__":
    unittest.main()
