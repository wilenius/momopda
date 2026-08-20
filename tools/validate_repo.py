#!/usr/bin/env python3
"""Deterministically validate the MoMoPDA repository without dependencies."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
SKILL_DIR = SKILLS_DIR / "moodle-plugin-development"
FIXTURES_DIR = SKILL_DIR / "assets" / "fixtures"
ERRORS: list[str] = []
NOTES: list[str] = []


def error(message: str) -> None:
    ERRORS.append(message)


def load_json(path: Path) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        error(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return None


def parse_frontmatter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        error(f"{path.relative_to(ROOT)}: missing opening frontmatter delimiter")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        error(f"{path.relative_to(ROOT)}: missing closing frontmatter delimiter")
        return {}

    values: dict[str, object] = {}
    current_mapping: dict[str, str] | None = None
    for number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace():
            if not line.startswith("  ") or line.startswith("   ") or "\t" in line[:2]:
                error(f"{path.relative_to(ROOT)}:{number}: nested frontmatter must use exactly two spaces")
                continue
            if current_mapping is None or ":" not in line:
                error(f"{path.relative_to(ROOT)}:{number}: unsupported frontmatter structure")
                continue
            key, raw_value = line.strip().split(":", 1)
            if key in current_mapping:
                error(f"{path.relative_to(ROOT)}:{number}: duplicate metadata key {key}")
            raw_value = raw_value.strip()
            if not raw_value:
                error(f"{path.relative_to(ROOT)}:{number}: metadata values must be non-empty strings")
            current_mapping[key] = parse_frontmatter_scalar(path, number, raw_value)
            continue
        if ":" not in line:
            error(f"{path.relative_to(ROOT)}:{number}: invalid frontmatter entry")
            continue
        key, raw_value = line.split(":", 1)
        if key in values:
            error(f"{path.relative_to(ROOT)}:{number}: duplicate frontmatter key {key}")
            continue
        if raw_value.strip():
            values[key] = parse_frontmatter_scalar(path, number, raw_value.strip())
            current_mapping = None
        else:
            if key != "metadata":
                error(f"{path.relative_to(ROOT)}:{number}: only metadata may be a mapping")
            current_mapping = {}
            values[key] = current_mapping
    return values


def parse_frontmatter_scalar(path: Path, number: int, raw_value: str) -> str:
    if not raw_value:
        return ""
    if raw_value[0] in {'"', "'"}:
        quote = raw_value[0]
        if len(raw_value) < 2 or raw_value[-1] != quote:
            error(f"{path.relative_to(ROOT)}:{number}: unterminated quoted value")
            return raw_value
        if quote == '"':
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError as exc:
                error(f"{path.relative_to(ROOT)}:{number}: invalid quoted value: {exc}")
                return raw_value
            if not isinstance(value, str):
                error(f"{path.relative_to(ROOT)}:{number}: scalar must be a string")
                return raw_value
            return value
        return raw_value[1:-1].replace("''", "'")
    yaml_implicit = re.fullmatch(
        r"(?i:true|false|null|yes|no|on|off|~|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[-+]?\d+)?|"
        r"[-+]?\.(?:inf|nan)|\d{4}-\d{2}-\d{2})",
        raw_value,
    )
    if yaml_implicit:
        error(f"{path.relative_to(ROOT)}:{number}: implicit YAML scalars must be quoted strings")
    if (
        ":" in raw_value
        or "#" in raw_value
        or raw_value.startswith(('{', '[', '&', '*', '!', '|', '>', '@', '`', '- ', '? '))
    ):
        error(f"{path.relative_to(ROOT)}:{number}: unsupported unquoted YAML value")
    return raw_value


def validate_skill_manifest() -> None:
    manifests = sorted(SKILLS_DIR.rglob("SKILL.md"))
    expected = SKILL_DIR / "SKILL.md"
    if manifests != [expected]:
        rendered = ", ".join(str(path.relative_to(ROOT)) for path in manifests)
        error(f"expected one canonical SKILL.md, found: {rendered or 'none'}")
        return

    values = parse_frontmatter(expected)
    allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
    unknown = sorted(set(values) - allowed)
    if unknown:
        error(f"{expected.relative_to(ROOT)}: unsupported fields: {', '.join(unknown)}")

    name = values.get("name")
    description = values.get("description")
    if name != SKILL_DIR.name:
        error(f"{expected.relative_to(ROOT)}: name must match {SKILL_DIR.name}")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        error(f"{expected.relative_to(ROOT)}: invalid skill name")
    if isinstance(name, str) and len(name) > 64:
        error(f"{expected.relative_to(ROOT)}: skill name exceeds 64 characters")
    if not isinstance(description, str) or not description:
        error(f"{expected.relative_to(ROOT)}: description is required")
    elif len(description) > 1024:
        error(f"{expected.relative_to(ROOT)}: description exceeds 1024 characters")
    compatibility = values.get("compatibility")
    license_name = values.get("license")
    if license_name is not None and not isinstance(license_name, str):
        error(f"{expected.relative_to(ROOT)}: license must be a string")
    if compatibility is not None and not isinstance(compatibility, str):
        error(f"{expected.relative_to(ROOT)}: compatibility must be a string")
    if isinstance(compatibility, str) and len(compatibility) > 500:
        error(f"{expected.relative_to(ROOT)}: compatibility exceeds 500 characters")
    metadata = values.get("metadata")
    if not isinstance(metadata, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in metadata.items()
    ):
        error(f"{expected.relative_to(ROOT)}: metadata must be a string-to-string mapping")
    allowed_tools = values.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        error(f"{expected.relative_to(ROOT)}: allowed-tools must be a string")
    if len(expected.read_text(encoding="utf-8").splitlines()) > 500:
        error(f"{expected.relative_to(ROOT)}: SKILL.md exceeds 500 lines")


def markdown_without_code(text: str) -> str:
    output: list[str] = []
    in_fence = False
    fence = ""
    for line in text.splitlines():
        match = re.match(r"^\s*(```+|~~~+)", line)
        if match:
            marker = match.group(1)
            if not in_fence:
                in_fence = True
                fence = marker[:3]
            elif marker.startswith(fence):
                in_fence = False
            continue
        if not in_fence:
            output.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(output)


def validate_markdown_links() -> None:
    link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    skill_root = SKILL_DIR.resolve()
    paths = list(SKILL_DIR.rglob("*.md"))
    paths.extend((ROOT / "adapters").rglob("*.md"))
    paths.append(ROOT / "README.md")
    for path in sorted(paths):
        text = markdown_without_code(path.read_text(encoding="utf-8"))
        boundary = skill_root if path.is_relative_to(SKILL_DIR) else ROOT.resolve()
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if target.startswith(("https://", "http://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0].split("?", 1)[0]
            if not target:
                continue
            if target.startswith("/"):
                error(f"{path.relative_to(ROOT)}: absolute local link is not portable: {target}")
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(boundary)
            except ValueError:
                error(f"{path.relative_to(ROOT)}: link escapes its resource boundary: {target}")
                continue
            if not resolved.exists():
                error(f"{path.relative_to(ROOT)}: missing local link target: {target}")


def validate_text_files() -> None:
    roots = [
        ROOT / "README.md",
        SKILL_DIR,
        ROOT / "knowledge",
        ROOT / "scripts",
        ROOT / "tools",
        ROOT / "adapters",
        ROOT / "docs",
        ROOT / "evals",
        ROOT / ".github",
    ]
    paths: list[Path] = []
    for candidate in roots:
        if candidate.is_file():
            paths.append(candidate)
        elif candidate.is_dir():
            paths.extend(path for path in candidate.rglob("*") if path.is_file())
    for path in sorted(set(paths)):
        if path.suffix.lower() not in {
            ".md", ".json", ".map", ".py", ".sh", ".yml", ".yaml", ".php", ".js", ".xml", ".svg"
        }:
            continue
        try:
            data = path.read_bytes()
            data.decode("utf-8")
        except (OSError, UnicodeError) as exc:
            error(f"{path.relative_to(ROOT)}: not valid UTF-8: {exc}")
            continue
        if b"\r" in data:
            error(f"{path.relative_to(ROOT)}: contains CR characters")
        generated_amd = path.parent.name == "build" and path.parent.parent.name == "amd"
        if data and not data.endswith(b"\n") and not generated_amd:
            error(f"{path.relative_to(ROOT)}: missing final newline")


def validate_structured_data() -> None:
    compatibility = load_json(ROOT / "knowledge" / "compatibility.json")
    sources = load_json(ROOT / "knowledge" / "sources.json")
    manifest = load_json(FIXTURES_DIR / "manifest.json")

    if not isinstance(compatibility, dict):
        error("knowledge/compatibility.json: top-level value must be an object")
    else:
        if compatibility.get("schema_version") != 1:
            error("knowledge/compatibility.json: schema_version must be 1")
        releases = compatibility.get("supported_releases")
        if not isinstance(releases, list) or not releases:
            error("knowledge/compatibility.json: supported_releases must be a non-empty list")
        else:
            versions: list[str] = []
            for release in releases:
                if not isinstance(release, dict):
                    error("knowledge/compatibility.json: release entries must be objects")
                    continue
                version = release.get("moodle")
                end = release.get("security_support_ends")
                if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+", version):
                    error("knowledge/compatibility.json: invalid Moodle release number")
                else:
                    versions.append(version)
                if not isinstance(end, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", end):
                    error(f"knowledge/compatibility.json: invalid support date for {version}")
            if len(versions) != len(set(versions)):
                error("knowledge/compatibility.json: Moodle releases must be unique")
            boundaries = compatibility.get("enforced_integration_boundaries")
            if not isinstance(boundaries, list) or not boundaries:
                error("knowledge/compatibility.json: enforced_integration_boundaries must be a non-empty list")
            else:
                boundary_versions = {
                    entry.get("moodle") for entry in boundaries if isinstance(entry, dict)
                }
                if not boundary_versions.issubset(set(versions)):
                    error("knowledge/compatibility.json: integration boundaries must be supported releases")
                for boundary in boundaries:
                    if not isinstance(boundary, dict):
                        error("knowledge/compatibility.json: integration boundaries must be objects")
                        continue
                    if not isinstance(boundary.get("tag"), str) or not re.fullmatch(
                        r"v\d+\.\d+\.\d+", boundary["tag"]
                    ):
                        error("knowledge/compatibility.json: integration boundaries need pinned patch tags")
                    if not isinstance(boundary.get("commit"), str) or not re.fullmatch(
                        r"[a-f0-9]{40}", boundary["commit"]
                    ):
                        error("knowledge/compatibility.json: integration boundaries need pinned commits")
                    if boundary.get("layout") not in {"legacy", "public"}:
                        error("knowledge/compatibility.json: integration boundaries need a known layout")
                validate_integration_matrix(boundaries)

    source_fixture_names: set[str] = set()
    if not isinstance(sources, dict):
        error("knowledge/sources.json: top-level value must be an object")
    else:
        if sources.get("schema_version") != 1:
            error("knowledge/sources.json: schema_version must be 1")
        entries = sources.get("sources")
        if not isinstance(entries, list):
            error("knowledge/sources.json: sources must be a list")
        else:
            ids = [entry.get("id") for entry in entries if isinstance(entry, dict)]
            if len(ids) != len(set(ids)):
                error("knowledge/sources.json: source IDs must be unique")
            for entry in entries:
                if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
                    error("knowledge/sources.json: each source needs a string ID")
                    continue
                fixture = entry.get("fixture")
                if fixture is not None:
                    if not isinstance(fixture, str):
                        error(f"knowledge/sources.json: fixture for {entry.get('id')} must be a string")
                    else:
                        source_fixture_names.add(fixture)

    if not isinstance(manifest, dict):
        error("fixture manifest: top-level value must be an object")
    else:
        if manifest.get("schema_version") != 1:
            error("fixture manifest: schema_version must be 1")
        validate_fixtures(manifest)
        entries = manifest.get("fixtures")
        if isinstance(entries, list):
            manifest_names = {
                entry.get("directory") for entry in entries if isinstance(entry, dict)
            }
            if source_fixture_names != manifest_names:
                error(
                    "knowledge/sources.json: fixture mappings do not match the manifest; "
                    f"missing={sorted(manifest_names - source_fixture_names)}, "
                    f"extra={sorted(source_fixture_names - manifest_names)}"
                )


def validate_fixtures(manifest: dict[str, object]) -> None:
    expected_components = {
        "mod_momopda",
        "block_momopda",
        "enrol_momopda",
        "filter_momopda",
        "local_momopda",
        "qbank_momopda",
        "qtype_momopda",
        "report_momopda",
        "tiny_momopda",
    }
    entries = manifest.get("fixtures")
    if not isinstance(entries, list):
        error("fixture manifest: fixtures must be a list")
        return

    components: set[str] = set()
    directories: set[str] = set()
    minimum = manifest.get("minimum_moodle")
    for entry in entries:
        if not isinstance(entry, dict):
            error("fixture manifest: each fixture must be an object")
            continue
        component = entry.get("component")
        directory = entry.get("directory")
        if not isinstance(component, str) or not isinstance(directory, str):
            error("fixture manifest: component and directory must be strings")
            continue
        components.add(component)
        directories.add(directory)
        fixture = FIXTURES_DIR / directory
        version_file = fixture / "version.php"
        if not version_file.is_file():
            error(f"fixture {directory}: missing version.php")
            continue
        version_text = version_file.read_text(encoding="utf-8")
        if not re.search(rf"\$plugin->component\s*=\s*['\"]{re.escape(component)}['\"]", version_text):
            error(f"fixture {directory}: version.php component does not match manifest")
        if isinstance(minimum, int) and not re.search(
            rf"\$plugin->requires\s*=\s*{minimum}\s*;", version_text
        ):
            error(f"fixture {directory}: version.php must require {minimum}")
        for destination_key in ("legacy_destination", "public_destination"):
            if not isinstance(entry.get(destination_key), str):
                error(f"fixture {directory}: missing {destination_key}")
        if not isinstance(entry.get("core_reference"), str):
            error(f"fixture {directory}: missing core_reference")

    if components != expected_components:
        missing = sorted(expected_components - components)
        extra = sorted(components - expected_components)
        error(f"fixture manifest component mismatch; missing={missing}, extra={extra}")
    actual_directories = {
        path.name for path in FIXTURES_DIR.iterdir() if path.is_dir()
    }
    if directories != actual_directories:
        error(
            "fixture manifest directory mismatch; "
            f"unlisted={sorted(actual_directories - directories)}, missing={sorted(directories - actual_directories)}"
        )

    tiny_build = FIXTURES_DIR / "tiny_momopda" / "amd" / "build" / "plugin.min.js"
    if not tiny_build.is_file():
        error("fixture tiny_momopda: distributable AMD build is missing")
    tiny_map = FIXTURES_DIR / "tiny_momopda" / "amd" / "build" / "plugin.min.js.map"
    if not tiny_map.is_file():
        error("fixture tiny_momopda: distributable AMD source map is missing")


def validate_public_evaluations() -> None:
    path = ROOT / "evals" / "public" / "tasks.json"
    document = load_json(path)
    if not isinstance(document, dict):
        error("evals/public/tasks.json: top-level value must be an object")
        return
    if document.get("schema_version") != 1:
        error("evals/public/tasks.json: schema_version must be 1")
    tasks = document.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        error("evals/public/tasks.json: tasks must be a non-empty list")
        return

    compatibility = load_json(ROOT / "knowledge" / "compatibility.json")
    supported_versions = set()
    if isinstance(compatibility, dict) and isinstance(compatibility.get("supported_releases"), list):
        supported_versions = {
            release.get("moodle")
            for release in compatibility["supported_releases"]
            if isinstance(release, dict)
        }

    ids: list[str] = []
    for task in tasks:
        if not isinstance(task, dict):
            error("evals/public/tasks.json: every task must be an object")
            continue
        task_id = task.get("id")
        plugin_type = task.get("plugin_type")
        fixture_name = task.get("starting_fixture")
        target_moodle = task.get("target_moodle")
        checks = task.get("public_checks")
        if not isinstance(task_id, str) or not task_id:
            error("evals/public/tasks.json: every task needs a string ID")
            task_id = "<unknown>"
        else:
            ids.append(task_id)
        if not isinstance(plugin_type, str) or not plugin_type:
            error(f"evals/public/tasks.json: task {task_id} needs a plugin_type")
        if not isinstance(fixture_name, str) or not (FIXTURES_DIR / fixture_name).is_dir():
            error(f"evals/public/tasks.json: task {task_id} references an unknown fixture")
            fixture = None
        else:
            fixture = FIXTURES_DIR / fixture_name
            if isinstance(plugin_type, str) and not fixture_name.startswith(f"{plugin_type}_"):
                error(f"evals/public/tasks.json: task {task_id} plugin type does not match its fixture")
        if target_moodle not in supported_versions:
            error(f"evals/public/tasks.json: task {task_id} targets an unsupported Moodle release")
        if not isinstance(task.get("prompt"), str) or not task.get("prompt"):
            error(f"evals/public/tasks.json: task {task_id} needs a prompt")
        if not isinstance(checks, list) or not checks or not all(isinstance(check, str) for check in checks):
            error(f"evals/public/tasks.json: task {task_id} needs string public checks")
        elif len(checks) != len(set(checks)):
            error(f"evals/public/tasks.json: task {task_id} public checks must be unique")

        setup = task.get("setup")
        if setup is None:
            continue
        if not isinstance(setup, dict) or fixture is None:
            error(f"evals/public/tasks.json: task {task_id} has an invalid setup")
            continue
        removals = setup.get("remove", [])
        if not isinstance(removals, list) or not all(isinstance(item, str) for item in removals):
            error(f"evals/public/tasks.json: task {task_id} setup removals must be strings")
        else:
            for item in removals:
                resolved = (fixture / item).resolve()
                if not resolved.is_relative_to(fixture.resolve()) or not resolved.exists():
                    error(f"evals/public/tasks.json: task {task_id} removes an invalid fixture path: {item}")
        overlay = setup.get("overlay")
        if not isinstance(overlay, str):
            error(f"evals/public/tasks.json: task {task_id} setup needs an overlay")
        else:
            public_root = (ROOT / "evals" / "public").resolve()
            overlay_path = (public_root / overlay).resolve()
            if not overlay_path.is_relative_to(public_root) or not overlay_path.is_dir():
                error(f"evals/public/tasks.json: task {task_id} has an invalid overlay: {overlay}")

    if len(ids) != len(set(ids)):
        error("evals/public/tasks.json: task IDs must be unique")


def validate_source_syntax() -> None:
    for path in sorted(ROOT.rglob("*.py")):
        if ".git" in path.parts:
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            error(f"{path.relative_to(ROOT)}: invalid Python: {exc}")

    for path in sorted(ROOT.rglob("*.xml")):
        if ".git" in path.parts:
            continue
        try:
            ElementTree.parse(path)
        except (OSError, ElementTree.ParseError) as exc:
            error(f"{path.relative_to(ROOT)}: invalid XML: {exc}")

    bash = shutil.which("bash")
    if bash is None:
        error("bash is required to validate shell scripts")
    else:
        for path in sorted(ROOT.rglob("*.sh")):
            result = subprocess.run(
                [bash, "-n", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode:
                error(f"{path.relative_to(ROOT)}: invalid shell syntax: {result.stderr.strip()}")
            if not os.access(path, os.X_OK):
                error(f"{path.relative_to(ROOT)}: shell script is not executable")

    php = shutil.which("php")
    php_files = sorted(SKILL_DIR.rglob("*.php"))
    if php is None:
        NOTES.append(f"PHP unavailable; skipped syntax checks for {len(php_files)} fixture files")
    else:
        for path in php_files:
            result = subprocess.run(
                [php, "-l", str(path)],
                check=False,
                capture_output=True,
                text=True,
            )
            if result.returncode:
                detail = result.stderr.strip() or result.stdout.strip()
                error(f"{path.relative_to(ROOT)}: PHP syntax check failed: {detail}")


def fixture_snapshot(path: Path) -> dict[str, str]:
    return {
        file.relative_to(path).as_posix(): hashlib.sha256(file.read_bytes()).hexdigest()
        for file in sorted(path.rglob("*"))
        if file.is_file()
    }


def validate_fixture_staging() -> None:
    tool = ROOT / "tools" / "stage_fixtures.py"
    manifest = load_json(FIXTURES_DIR / "manifest.json")
    if not isinstance(manifest, dict) or not isinstance(manifest.get("fixtures"), list):
        return

    source_before = fixture_snapshot(FIXTURES_DIR)
    entries = [entry for entry in manifest["fixtures"] if isinstance(entry, dict)]
    with tempfile.TemporaryDirectory(prefix="momopda-stage-") as temporary:
        for layout in ("legacy", "public"):
            output = Path(temporary) / layout
            command = [
                sys.executable,
                "-I",
                "-B",
                str(tool),
                "--output",
                str(output),
                "--layout",
                layout,
            ]
            result = subprocess.run(command, check=False, capture_output=True, text=True)
            if result.returncode:
                error(f"fixture staging failed for {layout}: {result.stderr.strip() or result.stdout.strip()}")
                continue

            try:
                staged = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
            except (OSError, UnicodeError, json.JSONDecodeError) as exc:
                error(f"fixture staging produced an invalid {layout} manifest: {exc}")
                continue
            if not isinstance(staged, dict):
                error(f"fixture staging produced a non-object {layout} manifest")
                continue
            staged_entries = staged.get("fixtures")
            if staged.get("layout") != layout or not isinstance(staged_entries, list):
                error(f"fixture staging did not record the {layout} layout")
                continue
            if len(staged_entries) != len(entries):
                error(f"fixture staging omitted fixtures for {layout}")
                continue

            for source_entry, staged_entry in zip(entries, staged_entries, strict=True):
                if not isinstance(staged_entry, dict):
                    error(f"fixture staging produced an invalid entry for {layout}")
                    continue
                directory = source_entry.get("directory")
                destination = source_entry.get(f"{layout}_destination")
                staged_path = staged_entry.get("staged_path")
                hashes = staged_entry.get("files")
                if staged_entry.get("destination") != destination:
                    error(f"fixture staging selected the wrong destination for {directory} on {layout}")
                if not isinstance(directory, str) or not isinstance(staged_path, str):
                    error(f"fixture staging produced invalid paths for {layout}")
                    continue
                staged_fixture = output / staged_path
                expected_hashes = fixture_snapshot(FIXTURES_DIR / directory)
                if hashes != expected_hashes or fixture_snapshot(staged_fixture) != expected_hashes:
                    error(f"fixture staging changed {directory} on {layout}")

            existing_result = subprocess.run(command, check=False, capture_output=True, text=True)
            if existing_result.returncode == 0:
                error(f"fixture staging replaced an existing {layout} output directory")

    if fixture_snapshot(FIXTURES_DIR) != source_before:
        error("fixture staging modified the canonical fixture sources")


def validate_integration_matrix(boundaries: list[object]) -> None:
    path = ROOT / ".github" / "workflows" / "moodle-integration.yml"
    try:
        workflow = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        error(f"{path.relative_to(ROOT)}: cannot read integration workflow: {exc}")
        return

    expected = []
    for boundary in boundaries:
        if not isinstance(boundary, dict):
            continue
        values = tuple(boundary.get(key) for key in ("tag", "commit", "php", "layout"))
        if all(isinstance(value, str) for value in values):
            expected.append(values)

    actual = re.findall(
        r"^\s+- moodle: (v\d+\.\d+\.\d+)\n"
        r"\s+commit: ([a-f0-9]{40})\n"
        r'\s+php: "([0-9]+\.[0-9]+)"\n'
        r"\s+layout: (legacy|public)$",
        workflow,
        flags=re.MULTILINE,
    )
    if actual != expected:
        error(
            f"{path.relative_to(ROOT)}: boundary matrix does not match "
            "knowledge/compatibility.json"
        )


def validate_installer() -> None:
    installer = ROOT / "scripts" / "install_skill.py"
    with tempfile.TemporaryDirectory(prefix="momopda-") as temporary:
        project = Path(temporary) / "plugin"
        project.mkdir()
        result = subprocess.run(
            [sys.executable, str(installer), "--client", "all", "--project", str(project)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode:
            error(f"installer smoke test failed: {result.stderr.strip() or result.stdout.strip()}")
            return
        shared = project / ".claude" / "skills" / "moodle-plugin-development"
        duplicate = project / ".opencode" / "skills" / "moodle-plugin-development"
        if not (shared / "SKILL.md").is_file() or shared.is_symlink():
            error(f"installer did not produce a portable shared copy: {shared}")
        if duplicate.exists() or duplicate.is_symlink():
            error(f"installer produced a duplicate OpenCode adapter: {duplicate}")

        update_result = subprocess.run(
            [
                sys.executable,
                str(installer),
                "--client",
                "all",
                "--project",
                str(project),
                "--update",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if update_result.returncode or not (shared / ".momopda-install.json").is_file():
            error(
                "installer update smoke test failed: "
                f"{update_result.stderr.strip() or update_result.stdout.strip()}"
            )

        validate_opencode_discovery(project)

    with tempfile.TemporaryDirectory(prefix="momopda-") as temporary:
        project = Path(temporary) / "plugin"
        project.mkdir()
        result = subprocess.run(
            [
                sys.executable,
                str(installer),
                "--client",
                "opencode",
                "--mode",
                "symlink",
                "--project",
                str(project),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        target = project / ".opencode" / "skills" / "moodle-plugin-development"
        if result.returncode or not target.is_symlink() or target.resolve() != SKILL_DIR.resolve():
            error(f"installer symlink smoke test failed: {result.stderr.strip() or result.stdout.strip()}")


def validate_opencode_discovery(project: Path) -> None:
    opencode = shutil.which("opencode")
    if opencode is None:
        NOTES.append("OpenCode unavailable; skipped client discovery smoke test")
        return
    result = subprocess.run(
        [opencode, "debug", "skill", "--pure"],
        cwd=project,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        error(f"OpenCode discovery smoke test failed: {result.stderr.strip() or result.stdout.strip()}")
        return
    try:
        skills = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        error(f"OpenCode discovery returned invalid JSON: {exc}")
        return
    matches = [entry for entry in skills if entry.get("name") == "moodle-plugin-development"]
    if len(matches) != 1:
        error(f"OpenCode discovery expected one moodle-plugin-development skill, found {len(matches)}")


def main() -> int:
    validate_text_files()
    validate_skill_manifest()
    validate_markdown_links()
    validate_structured_data()
    validate_public_evaluations()
    validate_source_syntax()
    validate_fixture_staging()
    validate_installer()

    for message in sorted(NOTES):
        print(f"NOTE: {message}")
    if ERRORS:
        for message in sorted(ERRORS):
            print(f"ERROR: {message}", file=sys.stderr)
        print(f"Validation failed with {len(ERRORS)} error(s).", file=sys.stderr)
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
