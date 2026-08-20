#!/usr/bin/env python3
"""Prepare, run, grade, and summarize public MoMoPDA evaluations."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import subprocess
import sys
import time
import uuid


ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = ROOT / "evals" / "public" / "tasks.json"
GRADERS_PATH = ROOT / "evals" / "public" / "graders.json"
FIXTURES_DIR = ROOT / "skills" / "moodle-plugin-development" / "assets" / "fixtures"
FIXTURE_MANIFEST = FIXTURES_DIR / "manifest.json"
SETUPS_DIR = ROOT / "evals" / "public" / "setups"
COMPATIBILITY_PATH = ROOT / "knowledge" / "compatibility.json"
CANDIDATE_SKILL = ROOT / "skills" / "moodle-plugin-development"
FAKE_CLIENT = ROOT / "tools" / "fake_eval_client.py"
FILTER_GRADER = (
    ROOT
    / "evals"
    / "public"
    / "graders"
    / "filter-modern-contract"
    / "harness_contract_test.php"
)
RESULT_SCHEMA_VERSION = 1
TERMINAL_STATUSES = {"pass", "fail", "error", "timeout", "incomplete"}
CHECK_STATUSES = {"pass", "fail", "error", "incomplete"}
EXECUTION_STATUSES = {"succeeded", "client_error", "timeout", "malformed", "skipped"}
SECRET_KEY_PATTERN = re.compile(r"(?i)(auth|api.?key|password|secret|token)")
SECRET_VALUE_KEY_PATTERN = re.compile(
    r"(?i)^(?:authorization|authentication|apikey|password|secret|access_?token|refresh_?token|id_?token|token)$"
)
AUTHORIZATION_PATTERN = re.compile(r"(?i)(authorization\s*[:=]\s*)[^\r\n,;]+")
CREDENTIAL_PATTERN = re.compile(
    r"(?i)((?:api[-_]?key|password|secret|token)\s*[:=]\s*)[^\s,;]+"
)


class HarnessError(ValueError):
    """Raised for an invalid or unsafe harness operation."""


def fail(message: str) -> None:
    raise HarnessError(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"cannot read JSON {path}: {exc}")


def write_json(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def tree_snapshot(root: Path) -> dict[str, str]:
    if not root.is_dir():
        fail(f"tree does not exist: {root}")
    files: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            fail(f"symbolic links are not allowed: {root.name}/{relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            fail(f"unsupported file type: {root.name}/{relative}")
        files[relative] = sha256_bytes(path.read_bytes())
    return files


def snapshot_hash(snapshot: dict[str, str]) -> str:
    payload = "".join(f"{path}\0{digest}\n" for path, digest in sorted(snapshot.items()))
    return sha256_text(payload)


def safe_relative(value: object, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        fail(f"{label} must be a non-empty POSIX relative path")
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or value != relative.as_posix()
        or not relative.parts
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        fail(f"unsafe {label}: {value!r}")
    return relative


def path_lexists(path: Path) -> bool:
    return os.path.lexists(path)


def copy_tree(source: Path, destination: Path) -> dict[str, str]:
    expected = tree_snapshot(source)
    if path_lexists(destination):
        fail(f"refusing to replace existing destination: {destination}")
    shutil.copytree(source, destination, copy_function=shutil.copy2)
    if tree_snapshot(destination) != expected:
        fail(f"copied tree differs from source: {source}")
    return expected


def apply_overlay(source: Path, destination: Path) -> None:
    tree_snapshot(source)
    for path in sorted(source.rglob("*")):
        relative = path.relative_to(source)
        target = destination / relative
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def git_output(arguments: list[str], cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={cwd}", "-C", str(cwd), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        return None
    return result.stdout.strip()


def repository_revision() -> dict[str, object]:
    commit = git_output(["rev-parse", "HEAD"], ROOT)
    status = git_output(["status", "--porcelain"], ROOT)
    return {
        "commit": commit or "unknown",
        "dirty": bool(status) if status is not None else None,
    }


def containing_git_revision(path: Path) -> str | None:
    root = git_output(["rev-parse", "--show-toplevel"], path)
    if root is None:
        return None
    return git_output(["rev-parse", "HEAD"], Path(root))


def harness_artifact_hash() -> str:
    paths = [
        Path(__file__).resolve(),
        FAKE_CLIENT,
        GRADERS_PATH,
        FILTER_GRADER,
        ROOT / "evals" / "public" / "run-result.schema.json",
    ]
    snapshot = {
        path.relative_to(ROOT).as_posix(): sha256_bytes(path.read_bytes())
        for path in paths
        if path.is_file()
    }
    return snapshot_hash(snapshot)


def load_contracts() -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    tasks_document = load_json(TASKS_PATH)
    manifest_document = load_json(FIXTURE_MANIFEST)
    compatibility_document = load_json(COMPATIBILITY_PATH)
    if not isinstance(tasks_document, dict) or tasks_document.get("schema_version") != 1:
        fail("public tasks must be a schema_version 1 object")
    if not isinstance(manifest_document, dict) or manifest_document.get("schema_version") != 1:
        fail("fixture manifest must be a schema_version 1 object")
    if not isinstance(compatibility_document, dict) or compatibility_document.get("schema_version") != 1:
        fail("compatibility data must be a schema_version 1 object")

    raw_tasks = tasks_document.get("tasks")
    raw_fixtures = manifest_document.get("fixtures")
    raw_boundaries = compatibility_document.get("enforced_integration_boundaries")
    if not isinstance(raw_tasks, list) or not raw_tasks:
        fail("public tasks must contain tasks")
    if not isinstance(raw_fixtures, list) or not raw_fixtures:
        fail("fixture manifest must contain fixtures")
    if not isinstance(raw_boundaries, list) or not raw_boundaries:
        fail("compatibility data must contain integration boundaries")

    tasks: dict[str, dict[str, object]] = {}
    allowed_task_keys = {
        "id", "plugin_type", "starting_fixture", "target_moodle", "prompt", "setup", "public_checks",
    }
    for task in raw_tasks:
        if not isinstance(task, dict):
            fail("every public task must be an object")
        unknown = set(task) - allowed_task_keys
        if unknown:
            fail(f"task has unknown fields: {', '.join(sorted(unknown))}")
        task_id = task.get("id")
        checks = task.get("public_checks")
        if not isinstance(task_id, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", task_id):
            fail("every public task needs a safe ID")
        if task_id in tasks:
            fail(f"duplicate task ID: {task_id}")
        if not isinstance(task.get("prompt"), str) or not task["prompt"]:
            fail(f"task {task_id} needs a prompt")
        if (
            not isinstance(checks, list)
            or not checks
            or not all(isinstance(check, str) and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", check) for check in checks)
            or len(checks) != len(set(checks))
        ):
            fail(f"task {task_id} has invalid public checks")
        setup = task.get("setup")
        if setup is not None:
            if not isinstance(setup, dict) or set(setup) != {"remove", "overlay"}:
                fail(f"task {task_id} setup must contain only remove and overlay")
            removals = setup.get("remove")
            if not isinstance(removals, list) or len(removals) != len(set(removals)):
                fail(f"task {task_id} setup removals must be a unique list")
            for removal in removals:
                safe_relative(removal, f"task {task_id} removal")
            safe_relative(setup.get("overlay"), f"task {task_id} overlay")
        tasks[task_id] = task

    fixtures: dict[str, dict[str, object]] = {}
    for fixture in raw_fixtures:
        if not isinstance(fixture, dict) or not isinstance(fixture.get("directory"), str):
            fail("every fixture manifest entry needs a directory")
        directory = fixture["directory"]
        relative = safe_relative(directory, "fixture directory")
        if len(relative.parts) != 1:
            fail(f"fixture directory must be one path segment: {directory}")
        source = (FIXTURES_DIR / directory).resolve()
        if source.parent != FIXTURES_DIR.resolve() or not source.is_dir():
            fail(f"fixture directory does not exist inside the manifest: {directory}")
        if directory in fixtures:
            fail(f"duplicate fixture directory: {directory}")
        fixtures[directory] = fixture

    boundaries: dict[str, dict[str, object]] = {}
    for boundary in raw_boundaries:
        if not isinstance(boundary, dict) or not isinstance(boundary.get("moodle"), str):
            fail("every integration boundary needs a Moodle release")
        boundaries[boundary["moodle"]] = boundary

    for task_id, task in tasks.items():
        fixture_name = task.get("starting_fixture")
        if fixture_name not in fixtures:
            fail(f"task {task_id} references an unknown fixture")
        if task.get("target_moodle") not in boundaries:
            fail(f"task {task_id} does not target an enforced integration boundary")
    return tasks, fixtures, boundaries


def load_graders(tasks: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    document = load_json(GRADERS_PATH)
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        fail("grader registry must be a schema_version 1 object")
    graders = document.get("graders")
    if not isinstance(graders, dict):
        fail("grader registry must contain a graders object")
    for task_id, grader in graders.items():
        if task_id not in tasks or not isinstance(grader, dict):
            fail(f"grader registry references an unknown task: {task_id}")
        checks = grader.get("checks")
        if checks != tasks[task_id].get("public_checks"):
            fail(f"grader registry check mapping differs for {task_id}")
        assertion = grader.get("assertion")
        if not isinstance(assertion, str):
            fail(f"grader {task_id} needs an assertion path")
        assertion_path = ROOT / assertion
        if not assertion_path.is_file() or not assertion_path.resolve().is_relative_to((ROOT / "evals" / "public").resolve()):
            fail(f"grader {task_id} has an invalid assertion path")
    return graders


def task_context(task_id: str) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    tasks, fixtures, boundaries = load_contracts()
    load_graders(tasks)
    if task_id not in tasks:
        fail(f"unknown task: {task_id}")
    task = tasks[task_id]
    fixture_name = task["starting_fixture"]
    target_moodle = task["target_moodle"]
    assert isinstance(fixture_name, str) and isinstance(target_moodle, str)
    return task, fixtures[fixture_name], boundaries[target_moodle]


def make_check_records(task: dict[str, object], evidence: str) -> list[dict[str, str]]:
    checks = task["public_checks"]
    assert isinstance(checks, list)
    return [
        {"id": check, "status": "incomplete", "evidence": evidence}
        for check in checks
        if isinstance(check, str)
    ]


def file_changes(before: dict[str, str], after: dict[str, str]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for path in sorted(set(before) | set(after)):
        if path not in before:
            changes.append({"path": path, "change": "added", "sha256": after[path]})
        elif path not in after:
            changes.append({"path": path, "change": "removed", "sha256": before[path]})
        elif before[path] != after[path]:
            changes.append({"path": path, "change": "modified", "sha256": after[path]})
    return changes


def verify_source_snapshots(prepared: dict[str, object], run_dir: Path) -> None:
    snapshots = prepared.get("source_snapshots")
    if not isinstance(snapshots, dict):
        fail("prepared run has no canonical source snapshots")
    if snapshots.get("fixtures_sha256") != snapshot_hash(tree_snapshot(FIXTURES_DIR)):
        fail("canonical fixtures changed since workspace preparation")
    if snapshots.get("setups_sha256") != snapshot_hash(tree_snapshot(SETUPS_DIR)):
        fail("evaluation setups changed since workspace preparation")
    revisions = prepared.get("revisions")
    if not isinstance(revisions, dict) or not isinstance(revisions.get("harness"), dict):
        fail("prepared run has no harness revision")
    if revisions["harness"].get("artifact_sha256") != harness_artifact_hash():
        fail("harness or public grader files changed since workspace preparation")
    skill = revisions.get("skill")
    if not isinstance(skill, dict):
        fail("prepared run has no skill revision")
    if skill.get("condition") != "none":
        installed_skill = (
            run_dir
            / "client-config"
            / "opencode"
            / "skills"
            / "moodle-plugin-development"
        )
        if skill.get("artifact_sha256") != snapshot_hash(tree_snapshot(installed_skill)):
            fail("installed evaluation skill changed since workspace preparation")


def prepare_run(args: argparse.Namespace) -> dict[str, object]:
    run_dir = args.output.resolve()
    root = ROOT.resolve()
    if path_lexists(run_dir):
        fail(f"refusing to reuse existing run destination: {run_dir}")
    if run_dir == root or run_dir.is_relative_to(root):
        fail("evaluation runs must be outside this repository")
    if not run_dir.parent.is_dir():
        fail(f"run destination parent does not exist: {run_dir.parent}")

    task, fixture, boundary = task_context(args.task)
    fixtures_before = tree_snapshot(FIXTURES_DIR)
    setups_before = tree_snapshot(SETUPS_DIR)
    run_id = args.run_id or f"{args.task}-{uuid.uuid4().hex[:12]}"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", run_id):
        fail("run ID contains unsafe characters")
    run_dir.mkdir()
    agent_root = run_dir / "agent"
    plugin_dir = agent_root / "plugin"
    artifacts_dir = run_dir / "artifacts"
    artifacts_dir.mkdir()
    agent_root.mkdir()

    fixture_name = fixture["directory"]
    assert isinstance(fixture_name, str)
    fixture_source = FIXTURES_DIR / fixture_name
    copy_tree(fixture_source, plugin_dir)
    setup = task.get("setup")
    if isinstance(setup, dict):
        removals = setup["remove"]
        assert isinstance(removals, list)
        for value in removals:
            relative = safe_relative(value, f"task {args.task} removal")
            target = plugin_dir.joinpath(*relative.parts)
            if not target.exists() or not target.is_file() or target.is_symlink():
                fail(f"task {args.task} removes a missing or non-file path: {value}")
            target.unlink()
        overlay_value = setup["overlay"]
        relative_overlay = safe_relative(overlay_value, f"task {args.task} overlay")
        overlay = (ROOT / "evals" / "public").joinpath(*relative_overlay.parts)
        if not overlay.is_dir():
            fail(f"task {args.task} overlay does not exist: {overlay_value}")
        apply_overlay(overlay, plugin_dir)

    skill_record: dict[str, object]
    if args.condition == "none":
        if args.skill is not None:
            fail("the none condition cannot receive a skill path")
        skill_record = {"condition": "none", "artifact_sha256": None, "git_commit": None}
    else:
        if args.condition == "candidate":
            if args.skill is not None:
                fail("the candidate condition always uses the canonical repository skill")
            source_skill = CANDIDATE_SKILL
        else:
            if args.skill is None:
                fail("the released condition requires an explicit --skill path")
            source_skill = args.skill.resolve()
            if source_skill == CANDIDATE_SKILL.resolve():
                fail("the released condition cannot silently reuse the candidate skill")
        if not (source_skill / "SKILL.md").is_file():
            fail(f"skill path has no SKILL.md: {source_skill}")
        skill_destination = (
            run_dir
            / "client-config"
            / "opencode"
            / "skills"
            / "moodle-plugin-development"
        )
        skill_source_snapshot = copy_tree(source_skill, skill_destination)
        skill_record = {
            "condition": args.condition,
            "artifact_sha256": snapshot_hash(skill_source_snapshot),
            "git_commit": containing_git_revision(source_skill),
        }

    input_snapshot = tree_snapshot(plugin_dir)
    if tree_snapshot(FIXTURES_DIR) != fixtures_before:
        fail("workspace preparation modified canonical fixtures")
    if tree_snapshot(SETUPS_DIR) != setups_before:
        fail("workspace preparation modified evaluation setups")

    prompt = task["prompt"]
    assert isinstance(prompt, str)
    prepare_document: dict[str, object] = {
        "schema_version": 1,
        "run_id": run_id,
        "task": task,
        "condition": args.condition,
        "created_at": utc_now(),
        "prompt_sha256": sha256_text(prompt),
        "input_workspace_sha256": snapshot_hash(input_snapshot),
        "input_files": input_snapshot,
        "source_snapshots": {
            "fixtures_sha256": snapshot_hash(fixtures_before),
            "setups_sha256": snapshot_hash(setups_before),
        },
        "revisions": {
            "repository": repository_revision(),
            "harness": {
                "schema_version": RESULT_SCHEMA_VERSION,
                "artifact_sha256": harness_artifact_hash(),
            },
            "skill": skill_record,
            "moodle": {
                "release": boundary.get("moodle"),
                "tag": boundary.get("tag"),
                "commit": boundary.get("commit"),
                "php": boundary.get("php"),
                "layout": boundary.get("layout"),
                "destination": fixture.get(f"{boundary.get('layout')}_destination"),
            },
            "grader": {
                "plugin_ci_version": None,
                "plugin_ci_sha256": None,
                "php_version": None,
                "database_name": None,
            },
        },
        "paths": {
            "workspace": "agent/plugin",
            "events": "artifacts/events.jsonl",
            "stderr": "artifacts/stderr.log",
            "grader": "artifacts/grader.log",
            "tools": "artifacts/tools.log",
            "result": "run.json",
        },
    }
    write_json(run_dir / "prepare.json", prepare_document)
    record = initial_record(prepare_document)
    validate_record(record, task)
    write_json(run_dir / "run.json", record)
    return record


def initial_record(prepared: dict[str, object]) -> dict[str, object]:
    task = prepared["task"]
    assert isinstance(task, dict)
    input_hash = prepared["input_workspace_sha256"]
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "run_id": prepared["run_id"],
        "task_id": task["id"],
        "condition": prepared["condition"],
        "status": "incomplete",
        "prompt_sha256": prepared["prompt_sha256"],
        "workspace": {
            "input_sha256": input_hash,
            "output_sha256": input_hash,
            "changes": [],
        },
        "revisions": prepared["revisions"],
        "timing": {
            "started_at": None,
            "duration_ms": None,
            "timeout_seconds": None,
        },
        "execution": {
            "client": None,
            "client_version": None,
            "model": None,
            "variant": None,
            "agent": None,
            "status": "skipped",
            "exit_code": None,
            "signal": None,
            "timed_out": False,
            "usage": None,
            "usage_available": False,
            "argv": [],
            "evidence": "generation has not run",
        },
        "artifacts": prepared["paths"],
        "checks": make_check_records(task, "generation and grading have not completed"),
    }


def load_prepared(run_dir: Path) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    prepared = load_json(run_dir / "prepare.json")
    record = load_json(run_dir / "run.json")
    if not isinstance(prepared, dict) or prepared.get("schema_version") != 1:
        fail("run has no valid prepare.json")
    task = prepared.get("task")
    if not isinstance(task, dict):
        fail("prepared run has no task")
    if not isinstance(record, dict):
        fail("run has no valid run.json")
    validate_record(record, task)
    return prepared, record, task


def clone_readonly_moodle(source: Path, destination: Path, expected_commit: str) -> Path:
    source = source.resolve()
    actual = git_output(["rev-parse", "HEAD"], source)
    if actual != expected_commit:
        fail(f"target Moodle source is {actual or 'not a Git checkout'}, expected {expected_commit}")
    destination.parent.mkdir()
    result = subprocess.run(
        ["git", "clone", "--shared", "--no-checkout", str(source), str(destination)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        fail(f"cannot clone target Moodle source: {result.stderr.strip()}")
    result = subprocess.run(
        ["git", "-C", str(destination), "checkout", "--detach", expected_commit],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        fail(f"cannot check out target Moodle commit: {result.stderr.strip()}")
    for path in sorted(destination.rglob("*"), reverse=True):
        mode = path.stat().st_mode
        path.chmod(mode & ~0o222)
    destination.chmod(destination.stat().st_mode & ~0o222)
    return destination


def restore_owner_write(root: Path) -> None:
    if not root.exists():
        return
    root.chmod(root.stat().st_mode | 0o200)
    for path in root.rglob("*"):
        path.chmod(path.stat().st_mode | 0o200)


def environment_secrets(environment: dict[str, str]) -> tuple[str, ...]:
    return tuple(
        value
        for key, value in environment.items()
        if SECRET_KEY_PATTERN.search(key) and len(value) >= 4
    )


def redact_text(value: str, secrets: tuple[str, ...] = ()) -> str:
    redacted = AUTHORIZATION_PATTERN.sub(r"\1<redacted>", value)
    redacted = CREDENTIAL_PATTERN.sub(r"\1<redacted>", redacted)
    for secret in secrets:
        if len(secret) >= 8:
            redacted = redacted.replace(secret, "<redacted>")
    return redacted


def sanitize_event(value: object, secrets: tuple[str, ...]) -> object:
    if isinstance(value, dict):
        if value.get("type") in {"reasoning", "thinking"}:
            return {
                key: "<reasoning redacted>"
                if key in {"text", "content"}
                else sanitize_event(item, secrets)
                for key, item in value.items()
            }
        output: dict[str, object] = {}
        for key, item in value.items():
            normalized_key = re.sub(r"[^a-z_]", "", key.lower())
            if SECRET_VALUE_KEY_PATTERN.fullmatch(normalized_key):
                output[key] = "<redacted>"
            else:
                output[key] = sanitize_event(item, secrets)
        return output
    if isinstance(value, list):
        return [sanitize_event(item, secrets) for item in value]
    if isinstance(value, str):
        return redact_text(value, secrets)
    return value


def parse_events(stdout: str, secrets: tuple[str, ...] = ()) -> tuple[list[dict[str, object]], bool]:
    events: list[dict[str, object]] = []
    malformed = False
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            malformed = True
            continue
        if not isinstance(event, dict):
            malformed = True
            continue
        sanitized = sanitize_event(event, secrets)
        assert isinstance(sanitized, dict)
        events.append(sanitized)
    if not events:
        malformed = True
    return events, malformed


def event_usage(events: list[dict[str, object]]) -> dict[str, object] | None:
    totals = {"input": 0, "output": 0, "reasoning": 0, "cache_read": 0, "cache_write": 0}
    cost = 0.0
    found = False
    for event in events:
        if event.get("type") != "step_finish":
            continue
        part = event.get("part")
        if not isinstance(part, dict) or not isinstance(part.get("tokens"), dict):
            continue
        tokens = part["tokens"]
        cache = tokens.get("cache")
        if (
            not all(isinstance(tokens.get(key), int) for key in ("input", "output", "reasoning"))
            or not isinstance(cache, dict)
            or not all(isinstance(cache.get(key), int) for key in ("read", "write"))
            or not isinstance(part.get("cost"), (int, float))
        ):
            return None
        found = True
        for key in ("input", "output", "reasoning"):
            value = tokens.get(key)
            if isinstance(value, int):
                totals[key] += value
        totals["cache_read"] += cache["read"]
        totals["cache_write"] += cache["write"]
        if isinstance(part.get("cost"), (int, float)):
            cost += float(part["cost"])
    if not found:
        return None
    return {**totals, "cost": cost}


def run_process(command: list[str], cwd: Path, timeout: float, environment: dict[str, str]) -> tuple[int | None, int | None, bool, str, str, int]:
    started = time.monotonic()
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGTERM)
        try:
            stdout, stderr = process.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
    duration_ms = round((time.monotonic() - started) * 1000)
    returncode = process.returncode
    exit_code = returncode if returncode is not None and returncode >= 0 else None
    exit_signal = -returncode if returncode is not None and returncode < 0 else None
    return exit_code, exit_signal, timed_out, stdout, stderr, duration_ms


def executable_version(command: list[str]) -> str | None:
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    return result.stdout.strip() or result.stderr.strip() or None


def run_generation(args: argparse.Namespace) -> dict[str, object]:
    run_dir = args.run_dir.resolve()
    prepared, record, task = load_prepared(run_dir)
    verify_source_snapshots(prepared, run_dir)
    execution = record["execution"]
    assert isinstance(execution, dict)
    if execution.get("evidence") != "generation has not run":
        fail("refusing to run generation more than once in the same run directory")
    plugin_dir = run_dir / "agent" / "plugin"
    input_files = prepared["input_files"]
    if not isinstance(input_files, dict) or tree_snapshot(plugin_dir) != input_files:
        fail("prepared input workspace changed before generation")

    prompt = task["prompt"]
    assert isinstance(prompt, str)
    started_at = utc_now()
    timeout = float(args.timeout)
    environment = dict(os.environ)
    environment["OPENCODE_DISABLE_EXTERNAL_SKILLS"] = "1"
    environment["OPENCODE_DISABLE_CLAUDE_CODE_SKILLS"] = "1"
    environment["OPENCODE_DISABLE_PROJECT_CONFIG"] = "1"
    environment["OPENCODE_PURE"] = "1"
    client_config = run_dir / "client-config"
    client_config.mkdir(exist_ok=True)
    environment["XDG_CONFIG_HOME"] = str(client_config)
    command: list[str]
    client_version: str | None
    readonly_reference: Path | None = None

    if args.client == "opencode" and not args.model:
        events: list[dict[str, object]] = []
        malformed = False
        exit_code = None
        exit_signal = None
        timed_out = False
        stdout = ""
        stderr = ""
        duration_ms = 0
        command = []
        client_version = executable_version([args.opencode, "--version"])
        execution_status = "skipped"
        evidence = "OpenCode execution skipped because no explicit model was supplied"
    else:
        if args.client == "fake":
            command = [
                sys.executable,
                "-I",
                "-B",
                str(FAKE_CLIENT),
                "--workspace",
                str(plugin_dir),
                "--outcome",
                args.fake_outcome,
            ]
            client_version = f"fake/{sha256_bytes(FAKE_CLIENT.read_bytes())[:12]}"
        else:
            if args.moodle_source is None:
                fail("OpenCode execution with a model requires --moodle-source")
            revisions = prepared["revisions"]
            assert isinstance(revisions, dict) and isinstance(revisions.get("moodle"), dict)
            expected_commit = revisions["moodle"].get("commit")
            if not isinstance(expected_commit, str):
                fail("prepared run has no pinned Moodle commit")
            reference = clone_readonly_moodle(
                args.moodle_source,
                run_dir / "reference" / "moodle",
                expected_commit,
            )
            readonly_reference = reference
            permission = {
                "edit": "allow",
                "read": "allow",
                "glob": "allow",
                "grep": "allow",
                "list": "allow",
                "bash": "deny",
                "task": "deny",
                "skill": "allow",
                "webfetch": "deny",
                "websearch": "deny",
                "external_directory": {str(reference / "**"): "allow"},
            }
            environment["OPENCODE_CONFIG_CONTENT"] = json.dumps(
                {
                    "permission": permission,
                    "references": {
                        "target-moodle": {
                            "path": str(reference),
                            "description": "Read-only source for the pinned target Moodle release",
                        }
                    },
                },
                separators=(",", ":"),
            )
            command = [
                args.opencode,
                "run",
                "--pure",
                "--format",
                "json",
                "--dir",
                str(plugin_dir),
                "--model",
                args.model,
            ]
            if args.variant:
                command.extend(["--variant", args.variant])
            if args.agent:
                command.extend(["--agent", args.agent])
            command.append(prompt)
            client_version = executable_version([args.opencode, "--version"])

        spawn_error = False
        try:
            exit_code, exit_signal, timed_out, stdout, stderr, duration_ms = run_process(
                command,
                plugin_dir,
                timeout,
                environment,
            )
        except OSError as exc:
            spawn_error = True
            exit_code, exit_signal, timed_out = None, None, False
            stdout, stderr, duration_ms = "", str(exc), 0
        secrets = environment_secrets(environment)
        events, malformed = parse_events(stdout, secrets)
        tool_error = any(
            event.get("type") == "tool_use"
            and (
                not isinstance(event.get("part"), dict)
                or not isinstance(event["part"].get("state"), dict)
                or event["part"]["state"].get("status") != "completed"
            )
            for event in events
        )
        final_stop = bool(
            events
            and events[-1].get("type") == "step_finish"
            and isinstance(events[-1].get("part"), dict)
            and events[-1]["part"].get("reason") == "stop"
        )
        if timed_out:
            execution_status = "timeout"
            evidence = f"client exceeded the {timeout:g} second timeout"
        elif spawn_error:
            execution_status = "client_error"
            evidence = "client process could not be started"
        elif malformed:
            execution_status = "malformed"
            evidence = "client output was not a complete JSON event stream"
        elif exit_code != 0 or exit_signal is not None or tool_error or not final_stop:
            execution_status = "client_error"
            evidence = "client exited unsuccessfully or emitted a failed/incomplete tool sequence"
        else:
            execution_status = "succeeded"
            evidence = "client emitted a terminal stop event without tool errors"

    if readonly_reference is not None:
        restore_owner_write(readonly_reference)

    events_path = run_dir / "artifacts" / "events.jsonl"
    stderr_path = run_dir / "artifacts" / "stderr.log"
    if events:
        events_path.write_text(
            "".join(json.dumps(event, sort_keys=True) + "\n" for event in events),
            encoding="utf-8",
        )
    else:
        events_path.write_text("", encoding="utf-8")
    if malformed and stdout:
        with events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"type": "malformed_output", "sha256": sha256_text(stdout)}) + "\n")
    persisted_secrets = environment_secrets(environment)
    stderr_path.write_text(redact_text(stderr, persisted_secrets), encoding="utf-8")

    output_files = tree_snapshot(plugin_dir)
    verify_source_snapshots(prepared, run_dir)
    usage = event_usage(events)
    redacted_argv = []
    for value in command:
        if value == prompt:
            redacted_argv.append(f"<prompt sha256:{sha256_text(prompt)}>")
        else:
            redacted_argv.append(redact_text(value))
    record["workspace"] = {
        "input_sha256": prepared["input_workspace_sha256"],
        "output_sha256": snapshot_hash(output_files),
        "changes": file_changes(input_files, output_files),
    }
    record["timing"] = {
        "started_at": started_at,
        "duration_ms": duration_ms,
        "timeout_seconds": timeout,
    }
    record["execution"] = {
        "client": args.client,
        "client_version": client_version,
        "model": args.model if args.client == "opencode" else "fake/deterministic",
        "variant": args.variant if args.client == "opencode" else None,
        "agent": args.agent if args.client == "opencode" else None,
        "status": execution_status,
        "exit_code": exit_code,
        "signal": exit_signal,
        "timed_out": timed_out,
        "usage": usage,
        "usage_available": usage is not None,
        "argv": redacted_argv,
        "evidence": evidence,
    }
    if execution_status == "timeout":
        record["status"] = "timeout"
    elif execution_status in {"client_error", "malformed"}:
        record["status"] = "error"
    else:
        record["status"] = "incomplete"
    check_evidence = "grading has not completed" if execution_status == "succeeded" else evidence
    record["checks"] = make_check_records(task, check_evidence)
    validate_record(record, task)
    write_json(run_dir / "run.json", record)
    return record


def redact_argv(arguments: list[str], secrets: tuple[str, ...]) -> list[str]:
    output: list[str] = []
    redact_next = False
    for argument in arguments:
        if redact_next:
            output.append("<redacted>")
            redact_next = False
            continue
        output.append(redact_text(argument, secrets))
        if argument in {"--db-pass", "--password", "-p"}:
            redact_next = True
    return output


def run_logged_command(
    arguments: list[str],
    log: Path,
    cwd: Path,
    secrets: tuple[str, ...] = (),
    timeout: float = 1800,
    environment: dict[str, str] | None = None,
) -> tuple[int | None, bool, str]:
    started = time.monotonic()
    try:
        exit_code, exit_signal, timed_out, stdout, stderr, _ = run_process(
            arguments,
            cwd,
            timeout,
            environment or dict(os.environ),
        )
        returncode = exit_code if exit_signal is None else -exit_signal
        output = stdout + stderr
    except OSError as exc:
        returncode = None
        timed_out = False
        output = str(exc)
    with log.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "argv": redact_argv(arguments, secrets),
                    "duration_ms": round((time.monotonic() - started) * 1000),
                    "exit_code": returncode,
                    "timed_out": timed_out,
                },
                sort_keys=True,
            )
            + "\n"
        )
        handle.write(redact_text(output, secrets))
        if output and not output.endswith("\n"):
            handle.write("\n")
    return returncode, timed_out, output


def set_all_checks(record: dict[str, object], status: str, evidence: str) -> None:
    checks = record.get("checks")
    assert isinstance(checks, list)
    for check in checks:
        assert isinstance(check, dict)
        check["status"] = status
        check["evidence"] = evidence


def set_check(record: dict[str, object], check_id: str, status: str, evidence: str) -> None:
    checks = record.get("checks")
    assert isinstance(checks, list)
    for check in checks:
        if isinstance(check, dict) and check.get("id") == check_id:
            check["status"] = status
            check["evidence"] = evidence
            return
    fail(f"run record has no declared check: {check_id}")


def grade_run(args: argparse.Namespace) -> dict[str, object]:
    run_dir = args.run_dir.resolve()
    prepared, record, task = load_prepared(run_dir)
    verify_source_snapshots(prepared, run_dir)
    execution = record["execution"]
    assert isinstance(execution, dict)
    if execution.get("status") != "succeeded":
        fail("grading requires a successful generation execution")
    workspace = record.get("workspace")
    assert isinstance(workspace, dict)
    if workspace.get("output_sha256") != snapshot_hash(tree_snapshot(run_dir / "agent" / "plugin")):
        fail("generated workspace changed after execution was recorded")
    graders = load_graders(load_contracts()[0])
    task_id = task["id"]
    assert isinstance(task_id, str)
    if task_id not in graders:
        set_all_checks(record, "incomplete", f"no public grader is implemented for {task_id}")
        record["status"] = "incomplete"
        validate_record(record, task)
        write_json(run_dir / "run.json", record)
        return record
    if path_lexists(run_dir / "grading"):
        fail("refusing to reuse an existing grading workspace")

    revisions = prepared["revisions"]
    assert isinstance(revisions, dict) and isinstance(revisions.get("moodle"), dict)
    moodle_revision = revisions["moodle"]
    expected_php = moodle_revision.get("php")
    php_version = executable_version([args.php, "-r", "echo PHP_MAJOR_VERSION.'.'.PHP_MINOR_VERSION;"])
    if php_version != expected_php:
        evidence = f"grading requires PHP {expected_php}; found {php_version or 'unavailable'}"
        set_all_checks(record, "incomplete", evidence)
        record["status"] = "incomplete"
        verify_source_snapshots(prepared, run_dir)
        validate_record(record, task)
        write_json(run_dir / "run.json", record)
        return record

    plugin_ci = args.plugin_ci.resolve()
    if not plugin_ci.is_file() or not os.access(plugin_ci, os.X_OK):
        fail(f"Moodle Plugin CI is not executable: {plugin_ci}")
    plugin_ci_version = executable_version([str(plugin_ci), "--version"])
    if plugin_ci_version != "Moodle Plugin CI 4.5.11":
        evidence = f"grading requires Moodle Plugin CI 4.5.11; found {plugin_ci_version or 'unavailable'}"
        set_all_checks(record, "incomplete", evidence)
        record["status"] = "incomplete"
        validate_record(record, task)
        write_json(run_dir / "run.json", record)
        return record
    db_name = args.db_name or f"momopda_{uuid.uuid4().hex[:20]}"
    if not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_]{0,62}", db_name):
        fail("database name must be a safe PostgreSQL identifier")
    record_revisions = record.get("revisions")
    assert isinstance(record_revisions, dict)
    grader_revision = record_revisions.get("grader")
    assert isinstance(grader_revision, dict)
    grader_revision.update(
        {
            "plugin_ci_version": plugin_ci_version,
            "plugin_ci_sha256": sha256_bytes(plugin_ci.read_bytes()),
            "php_version": php_version,
            "database_name": db_name,
        }
    )
    prohibited_control_names = {
        ".moodle-plugin-ci.yml",
        ".moodle-plugin-ci.yaml",
        "thirdpartylibs.xml",
        "phpunit.xml",
        "phpunit.xml.dist",
        "tests/harness_contract_test.php",
    }
    generated_plugin = run_dir / "agent" / "plugin"
    present_controls = sorted(
        path.relative_to(generated_plugin).as_posix()
        for path in generated_plugin.rglob("*")
        if path.is_file()
        and (
            path.name in prohibited_control_names
            or path.relative_to(generated_plugin).as_posix() == "tests/harness_contract_test.php"
        )
    )
    if present_controls:
        evidence = f"generated plugin contains grader control files: {', '.join(present_controls)}"
        set_all_checks(record, "fail", evidence)
        record["status"] = "fail"
        validate_record(record, task)
        write_json(run_dir / "run.json", record)
        return record
    missing_tools = [
        tool
        for tool in ("composer", "git", "npm", "npx", "psql")
        if shutil.which(tool) is None
    ]
    if missing_tools:
        evidence = f"grading prerequisites are unavailable: {', '.join(missing_tools)}"
        set_all_checks(record, "incomplete", evidence)
        record["status"] = "incomplete"
        validate_record(record, task)
        write_json(run_dir / "run.json", record)
        return record
    grading = run_dir / "grading"
    plugin = grading / "plugin"
    grading.mkdir()
    copy_tree(run_dir / "agent" / "plugin", plugin)
    tests_dir = plugin / "tests"
    tests_dir.mkdir(exist_ok=True)
    shutil.copy2(FILTER_GRADER, tests_dir / FILTER_GRADER.name)
    moodle = grading / "moodle"
    data = grading / "moodledata"
    grader_log = run_dir / "artifacts" / "grader.log"
    tools_log = run_dir / "artifacts" / "tools.log"
    grader_log.write_text("", encoding="utf-8")
    tools_log.write_text("", encoding="utf-8")
    admin_password = "M0mopda-eval-only!"
    secrets = (args.db_pass, admin_password)
    selected_php = shutil.which(args.php)
    if selected_php is None:
        fail(f"PHP executable is unavailable: {args.php}")
    bin_dir = grading / "bin"
    home_dir = grading / "home"
    temporary_dir = grading / "tmp"
    bin_dir.mkdir()
    home_dir.mkdir()
    temporary_dir.mkdir()
    (bin_dir / "php").symlink_to(Path(selected_php).resolve())
    grading_environment = {
        "PATH": f"{bin_dir}{os.pathsep}{os.environ.get('PATH', os.defpath)}",
        "HOME": str(home_dir),
        "TMPDIR": str(temporary_dir),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": os.environ.get("LC_ALL", "C.UTF-8"),
        "GIT_TERMINAL_PROMPT": "0",
    }
    for key in ("CI", "NVM_DIR", "TERM"):
        if key in os.environ:
            grading_environment[key] = os.environ[key]
    install = [
        str(plugin_ci),
        "install",
        "--branch",
        str(moodle_revision["tag"]),
        "--moodle",
        str(moodle),
        "--data",
        str(data),
        "--plugin",
        str(plugin),
        "--db-type",
        "pgsql",
        "--db-host",
        args.db_host,
        "--db-port",
        str(args.db_port),
        "--db-name",
        db_name,
        "--db-user",
        args.db_user,
        "--db-pass",
        args.db_pass,
    ]
    returncode, timed_out, _ = run_logged_command(
        install,
        grader_log,
        grading,
        secrets,
        environment=grading_environment,
    )
    if returncode != 0 or timed_out:
        set_all_checks(record, "error", "isolated pinned Moodle installation failed; see artifacts/grader.log")
        record["status"] = "error"
        validate_record(record, task)
        write_json(run_dir / "run.json", record)
        return record

    actual_commit = git_output(["rev-parse", "HEAD"], moodle)
    if actual_commit != moodle_revision.get("commit"):
        set_all_checks(record, "error", f"Moodle checkout commit was {actual_commit or 'unknown'}, not the pinned revision")
        record["status"] = "error"
        validate_record(record, task)
        write_json(run_dir / "run.json", record)
        return record

    site_install = [
        args.php,
        str(moodle / "admin" / "cli" / "install_database.php"),
        "--lang=en",
        "--adminuser=admin",
        f"--adminpass={admin_password}",
        "--adminemail=admin@example.invalid",
        "--fullname=MoMoPDA evaluation",
        "--shortname=MoMoPDA",
        "--agree-license",
    ]
    returncode, timed_out, _ = run_logged_command(
        site_install,
        grader_log,
        grading,
        secrets,
        environment=grading_environment,
    )
    if returncode != 0 or timed_out:
        set_all_checks(record, "error", "isolated Moodle database installation failed; see artifacts/grader.log")
        record["status"] = "error"
        validate_record(record, task)
        write_json(run_dir / "run.json", record)
        return record

    plugin_ci_commands = [
        [str(plugin_ci), "phplint", str(plugin)],
        [str(plugin_ci), "codechecker", "--max-warnings", "0", str(plugin)],
        [str(plugin_ci), "validate", "--moodle", str(moodle), str(plugin)],
        [str(plugin_ci), "phpdoc", "--moodle", str(moodle), "--max-warnings", "0", str(plugin)],
        [str(plugin_ci), "savepoints", str(plugin)],
    ]
    plugin_ci_passed = True
    for command in plugin_ci_commands:
        returncode, timed_out, _ = run_logged_command(
            command,
            tools_log,
            grading,
            environment=grading_environment,
        )
        if returncode != 0 or timed_out:
            plugin_ci_passed = False
    set_check(
        record,
        "plugin-ci",
        "pass" if plugin_ci_passed else "fail",
        "all non-fixing Plugin CI checks passed" if plugin_ci_passed else "one or more Plugin CI checks failed; see artifacts/tools.log",
    )

    phpunit_base = [
        str(plugin_ci),
        "phpunit",
        "--moodle",
        str(moodle),
        "--fail-on-incomplete",
        "--fail-on-risky",
        "--fail-on-skipped",
        "--fail-on-warning",
    ]
    modern_result, modern_timeout, modern_output = run_logged_command(
        [
            *phpunit_base,
            "--filter",
            r"^filter_momopda\\harness_contract_test::test_modern_contract$",
            str(plugin),
        ],
        grader_log,
        grading,
        environment=grading_environment,
    )
    escaped_result, escaped_timeout, escaped_output = run_logged_command(
        [
            *phpunit_base,
            "--filter",
            r"^filter_momopda\\harness_contract_test::test_escaped_output$",
            str(plugin),
        ],
        grader_log,
        grading,
        environment=grading_environment,
    )
    modern_passed = (
        modern_result == 0
        and not modern_timeout
        and "OK (1 test, 6 assertions)" in modern_output
    )
    escaped_passed = (
        escaped_result == 0
        and not escaped_timeout
        and "OK (1 test, 2 assertions)" in escaped_output
    )
    set_check(
        record,
        "modern-filter-class",
        "pass" if modern_passed else "fail",
        "Moodle runtime class and marker assertions passed" if modern_passed else "Moodle runtime class or marker assertions did not execute exactly once or failed; see artifacts/grader.log",
    )
    set_check(
        record,
        "escaped-output",
        "pass" if escaped_passed else "fail",
        "hostile localized replacement content was escaped" if escaped_passed else "escaped-output assertion did not execute exactly once or failed; see artifacts/grader.log",
    )
    statuses = {check["status"] for check in record["checks"] if isinstance(check, dict)}
    if "error" in statuses:
        record["status"] = "error"
    elif "fail" in statuses:
        record["status"] = "fail"
    elif statuses == {"pass"}:
        record["status"] = "pass"
    else:
        record["status"] = "incomplete"
    verify_source_snapshots(prepared, run_dir)
    validate_record(record, task)
    write_json(run_dir / "run.json", record)
    return record


def validate_record(record: dict[str, object], task: dict[str, object] | None = None) -> None:
    required = {
        "schema_version", "run_id", "task_id", "condition", "status", "prompt_sha256",
        "workspace", "revisions", "timing", "execution", "artifacts", "checks",
    }
    if set(record) != required:
        fail(f"run record fields differ from schema: missing={sorted(required - set(record))}, extra={sorted(set(record) - required)}")
    if record.get("schema_version") != RESULT_SCHEMA_VERSION:
        fail("run record has an unsupported schema version")
    if record.get("condition") not in {"candidate", "released", "none"}:
        fail("run record has an invalid condition")
    if record.get("status") not in TERMINAL_STATUSES:
        fail("run record has an invalid terminal status")
    for key in ("run_id", "task_id"):
        if not isinstance(record.get(key), str) or not record[key]:
            fail(f"run record needs {key}")
    if not isinstance(record.get("prompt_sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", record["prompt_sha256"]):
        fail("run record has an invalid prompt hash")
    workspace = record.get("workspace")
    if not isinstance(workspace, dict) or set(workspace) != {"input_sha256", "output_sha256", "changes"}:
        fail("run record has invalid workspace metadata")
    for key in ("input_sha256", "output_sha256"):
        if not isinstance(workspace.get(key), str) or not re.fullmatch(r"[a-f0-9]{64}", workspace[key]):
            fail(f"run record has an invalid workspace {key}")
    changes = workspace.get("changes")
    if not isinstance(changes, list):
        fail("run record workspace changes must be a list")
    change_paths: list[str] = []
    for change in changes:
        if not isinstance(change, dict) or set(change) != {"path", "change", "sha256"}:
            fail("run record has invalid file change metadata")
        path = change.get("path")
        if not isinstance(path, str):
            fail("run record change paths must be strings")
        safe_relative(path, "run record change path")
        if change.get("change") not in {"added", "modified", "removed"}:
            fail("run record has an invalid file change type")
        if not isinstance(change.get("sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", change["sha256"]):
            fail("run record has an invalid file change hash")
        change_paths.append(path)
    if change_paths != sorted(set(change_paths)):
        fail("run record file changes must have unique sorted paths")

    revisions = record.get("revisions")
    if not isinstance(revisions, dict) or set(revisions) != {"repository", "harness", "skill", "moodle", "grader"}:
        fail("run record has invalid revision metadata")
    repository = revisions.get("repository")
    if not isinstance(repository, dict) or set(repository) != {"commit", "dirty"}:
        fail("run record has invalid repository revision")
    if not isinstance(repository.get("commit"), str) or not repository["commit"]:
        fail("run record needs a repository commit")
    if repository.get("dirty") not in {True, False, None}:
        fail("run record has an invalid repository dirty state")
    harness = revisions.get("harness")
    if (
        not isinstance(harness, dict)
        or set(harness) != {"schema_version", "artifact_sha256"}
        or harness.get("schema_version") != RESULT_SCHEMA_VERSION
        or not isinstance(harness.get("artifact_sha256"), str)
        or not re.fullmatch(r"[a-f0-9]{64}", harness["artifact_sha256"])
    ):
        fail("run record has an invalid harness revision")
    skill = revisions.get("skill")
    if not isinstance(skill, dict) or set(skill) != {"condition", "artifact_sha256", "git_commit"}:
        fail("run record has invalid skill revision metadata")
    if skill.get("condition") != record.get("condition"):
        fail("run record skill condition does not match the run condition")
    if record.get("condition") == "none":
        if skill.get("artifact_sha256") is not None or skill.get("git_commit") is not None:
            fail("no-skill run records must not identify a skill artifact")
    elif not isinstance(skill.get("artifact_sha256"), str) or not re.fullmatch(r"[a-f0-9]{64}", skill["artifact_sha256"]):
        fail("skill run record needs an artifact hash")
    moodle = revisions.get("moodle")
    moodle_keys = {"release", "tag", "commit", "php", "layout", "destination"}
    if not isinstance(moodle, dict) or set(moodle) != moodle_keys:
        fail("run record has invalid Moodle revision metadata")
    if (
        not all(isinstance(moodle.get(key), str) and moodle[key] for key in moodle_keys)
        or not re.fullmatch(r"[a-f0-9]{40}", moodle["commit"])
        or moodle.get("layout") not in {"legacy", "public"}
    ):
        fail("run record has invalid pinned Moodle values")
    grader = revisions.get("grader")
    grader_keys = {"plugin_ci_version", "plugin_ci_sha256", "php_version", "database_name"}
    if not isinstance(grader, dict) or set(grader) != grader_keys:
        fail("run record has invalid grader revision metadata")
    grader_values = [grader[key] for key in grader_keys]
    grading_terminal = record.get("status") in {"pass", "fail"} or (
        record.get("status") == "error"
        and isinstance(record.get("execution"), dict)
        and record["execution"].get("status") == "succeeded"
    )
    if grading_terminal and not any(value is not None for value in grader_values):
        fail("graded terminal records must identify the grader toolchain")
    if any(value is not None for value in grader_values):
        if (
            grader.get("plugin_ci_version") != "Moodle Plugin CI 4.5.11"
            or not isinstance(grader.get("plugin_ci_sha256"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", grader["plugin_ci_sha256"])
            or grader.get("php_version") != moodle.get("php")
            or not isinstance(grader.get("database_name"), str)
            or not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_]{0,62}", grader["database_name"])
        ):
            fail("run record has an incomplete or invalid grader toolchain revision")

    timing = record.get("timing")
    if not isinstance(timing, dict) or set(timing) != {"started_at", "duration_ms", "timeout_seconds"}:
        fail("run record has invalid timing metadata")
    if timing.get("started_at") is not None and not isinstance(timing["started_at"], str):
        fail("run record has an invalid start time")
    if timing.get("duration_ms") is not None and (not isinstance(timing["duration_ms"], int) or timing["duration_ms"] < 0):
        fail("run record has an invalid duration")
    if timing.get("timeout_seconds") is not None and (
        not isinstance(timing["timeout_seconds"], (int, float)) or timing["timeout_seconds"] <= 0
    ):
        fail("run record has an invalid timeout")
    execution = record.get("execution")
    execution_keys = {
        "client", "client_version", "model", "variant", "agent", "status", "exit_code", "signal",
        "timed_out", "usage", "usage_available", "argv", "evidence",
    }
    if not isinstance(execution, dict) or set(execution) != execution_keys or execution.get("status") not in EXECUTION_STATUSES:
        fail("run record has an invalid execution status")
    if not isinstance(execution.get("usage_available"), bool):
        fail("run record must identify usage availability")
    if execution.get("exit_code") is not None and (not isinstance(execution["exit_code"], int) or execution["exit_code"] < 0):
        fail("run record has an invalid client exit code")
    if execution.get("signal") is not None and (not isinstance(execution["signal"], int) or execution["signal"] < 1):
        fail("run record has an invalid client signal")
    if not isinstance(execution.get("timed_out"), bool):
        fail("run record has an invalid timeout flag")
    if not isinstance(execution.get("argv"), list) or not all(isinstance(value, str) for value in execution["argv"]):
        fail("run record has an invalid redacted argument vector")
    if not isinstance(execution.get("evidence"), str) or not execution["evidence"]:
        fail("run record needs execution evidence")
    usage = execution.get("usage")
    usage_keys = {"input", "output", "reasoning", "cache_read", "cache_write", "cost"}
    if execution["usage_available"]:
        if not isinstance(usage, dict) or set(usage) != usage_keys:
            fail("run record has incomplete usage metadata")
        if not all(isinstance(usage[key], (int, float)) and usage[key] >= 0 for key in usage_keys):
            fail("run record has invalid usage values")
    elif usage is not None:
        fail("run record cannot contain usage when usage_available is false")

    artifacts = record.get("artifacts")
    artifact_keys = {"workspace", "events", "stderr", "grader", "tools", "result"}
    if not isinstance(artifacts, dict) or set(artifacts) != artifact_keys:
        fail("run record has invalid artifact paths")
    for key, value in artifacts.items():
        safe_relative(value, f"run record {key} artifact")
    checks = record.get("checks")
    if not isinstance(checks, list) or not checks:
        fail("run record needs check outcomes")
    check_ids: list[str] = []
    for check in checks:
        if not isinstance(check, dict) or set(check) != {"id", "status", "evidence"}:
            fail("run record has an invalid check outcome")
        if check.get("status") not in CHECK_STATUSES or not isinstance(check.get("evidence"), str) or not check["evidence"]:
            fail("run record has an invalid check status or evidence")
        if not isinstance(check.get("id"), str):
            fail("run record check IDs must be strings")
        check_ids.append(check["id"])
    if len(check_ids) != len(set(check_ids)):
        fail("run record contains duplicate check outcomes")
    if task is not None:
        if record.get("task_id") != task.get("id") or check_ids != task.get("public_checks"):
            fail("run record does not match its task check contract")
    execution_status = execution["status"]
    check_statuses = {check["status"] for check in checks if isinstance(check, dict)}
    status = record["status"]
    if execution_status == "timeout" and status != "timeout":
        fail("timed-out execution must produce a timeout run")
    if execution_status in {"client_error", "malformed"} and status != "error":
        fail("failed client execution must produce an error run")
    if execution_status == "skipped" and status != "incomplete":
        fail("skipped execution must produce an incomplete run")
    if status == "pass" and (execution_status != "succeeded" or check_statuses != {"pass"}):
        fail("passing runs require successful execution and passing checks")
    if status == "fail" and ("fail" not in check_statuses or "error" in check_statuses):
        fail("failed runs require a failed check and no errored checks")
    if status == "error" and execution_status not in {"client_error", "malformed"} and "error" not in check_statuses:
        fail("error runs require a client or check error")


def validate_record_path(path: Path) -> dict[str, object]:
    record = load_json(path)
    if not isinstance(record, dict):
        fail(f"run record is not an object: {path}")
    tasks, _, _ = load_contracts()
    task_id = record.get("task_id")
    if not isinstance(task_id, str) or task_id not in tasks:
        fail(f"run record references an unknown task: {task_id}")
    validate_record(record, tasks[task_id])
    return record


def summarize(paths: list[Path]) -> dict[str, object]:
    records: list[dict[str, object]] = []
    for path in paths:
        candidate = path / "run.json" if path.is_dir() else path
        records.append(validate_record_path(candidate))
    counts = {status: 0 for status in ("pass", "fail", "error", "timeout", "incomplete")}
    condition_counts = {
        condition: {status: 0 for status in counts}
        for condition in ("candidate", "released", "none")
    }
    runs: list[dict[str, object]] = []
    for record in records:
        status = record["status"]
        condition = record["condition"]
        assert isinstance(status, str) and isinstance(condition, str)
        counts[status] += 1
        condition_counts[condition][status] += 1
        runs.append(
            {
                "run_id": record["run_id"],
                "task_id": record["task_id"],
                "condition": condition,
                "status": status,
            }
        )
    return {
        "schema_version": 1,
        "total": len(records),
        "counts": counts,
        "conditions": condition_counts,
        "runs": sorted(runs, key=lambda item: str(item["run_id"])),
        "ranking": None,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    prepare = subparsers.add_parser("prepare", help="prepare one isolated task workspace")
    prepare.add_argument("--task", required=True)
    prepare.add_argument("--condition", choices=("candidate", "released", "none"), required=True)
    prepare.add_argument("--skill", type=Path, help="explicit released skill directory")
    prepare.add_argument("--output", type=Path, required=True)
    prepare.add_argument("--run-id")

    run = subparsers.add_parser("run", help="run a fake or OpenCode generation client")
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument("--client", choices=("fake", "opencode"), required=True)
    run.add_argument(
        "--fake-outcome",
        choices=("success", "control-file", "nonzero", "timeout", "malformed"),
        default="success",
    )
    run.add_argument("--opencode", default="opencode")
    run.add_argument("--model")
    run.add_argument("--variant")
    run.add_argument("--agent")
    run.add_argument("--moodle-source", type=Path)
    run.add_argument("--timeout", type=float, default=900.0)

    grade = subparsers.add_parser("grade", help="grade a successful generated workspace")
    grade.add_argument("--run-dir", type=Path, required=True)
    grade.add_argument("--plugin-ci", type=Path, required=True)
    grade.add_argument("--php", default="php")
    grade.add_argument("--db-host", default="127.0.0.1")
    grade.add_argument("--db-port", type=int, default=5432)
    grade.add_argument("--db-name")
    grade.add_argument("--db-user", default="postgres")
    grade.add_argument("--db-pass", default="moodle")

    summary = subparsers.add_parser("summarize", help="summarize saved run records")
    summary.add_argument("records", nargs="+", type=Path)
    summary.add_argument("--output", type=Path)

    validate = subparsers.add_parser("validate", help="validate one saved run record")
    validate.add_argument("record", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "prepare":
            record = prepare_run(args)
            print(f"Prepared {record['run_id']} at {args.output.resolve()}")
        elif args.command == "run":
            record = run_generation(args)
            print(f"Generation {record['execution']['status']}; run status {record['status']}")
        elif args.command == "grade":
            record = grade_run(args)
            print(f"Grading completed with run status {record['status']}")
        elif args.command == "summarize":
            document = summarize(args.records)
            rendered = json.dumps(document, indent=2, sort_keys=True) + "\n"
            if args.output:
                args.output.write_text(rendered, encoding="utf-8")
            else:
                print(rendered, end="")
        else:
            record_path = args.record / "run.json" if args.record.is_dir() else args.record
            validate_record_path(record_path)
            print(f"Valid run record: {record_path}")
    except (HarnessError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
