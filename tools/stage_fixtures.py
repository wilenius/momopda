#!/usr/bin/env python3
"""Copy manifest-listed fixtures into a deterministic Plugin CI staging tree."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = (
    ROOT
    / "skills"
    / "moodle-plugin-development"
    / "assets"
    / "fixtures"
    / "manifest.json"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="fixture manifest (default: canonical skill fixture manifest)",
    )
    parser.add_argument("--output", type=Path, required=True, help="new staging directory")
    parser.add_argument(
        "--layout",
        choices=("legacy", "public"),
        required=True,
        help="Moodle repository layout to record in the staged manifest",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    raise ValueError(message)


def load_manifest(path: Path) -> dict[str, object]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        fail(f"cannot read fixture manifest {path}: {exc}")
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        fail("fixture manifest must be a schema_version 1 object")
    entries = document.get("fixtures")
    if not isinstance(entries, list) or not entries:
        fail("fixture manifest must contain a non-empty fixtures list")
    return document


def safe_source(fixtures_dir: Path, directory: object) -> Path:
    if not isinstance(directory, str) or not directory:
        fail("every fixture needs a non-empty directory")
    relative = Path(directory)
    if relative.is_absolute() or len(relative.parts) != 1 or relative.name != directory:
        fail(f"fixture directory must be one relative path segment: {directory!r}")
    source = (fixtures_dir / relative).resolve()
    if source.parent != fixtures_dir or not source.is_dir():
        fail(f"fixture directory does not exist inside the manifest directory: {directory}")
    if not (source / "version.php").is_file():
        fail(f"fixture directory has no version.php: {directory}")
    return source


def safe_destination(value: object, key: str, component: str) -> str:
    if not isinstance(value, str) or not value:
        fail(f"fixture {component} needs a non-empty {key}")
    relative = Path(value)
    if not relative.parts or relative.is_absolute() or ".." in relative.parts or "." in relative.parts:
        fail(f"fixture {component} has an unsafe {key}: {value!r}")
    if key == "public_destination" and relative.parts[0] != "public":
        fail(f"fixture {component} public_destination must be below public/")
    if key == "legacy_destination" and relative.parts[0] == "public":
        fail(f"fixture {component} legacy_destination must not be below public/")
    return relative.as_posix()


def file_hashes(source: Path) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            fail(f"fixture files must not be symbolic links: {path.relative_to(source)}")
        if path.is_dir():
            continue
        if not path.is_file():
            fail(f"fixture contains an unsupported file type: {path.relative_to(source)}")
        relative = path.relative_to(source).as_posix()
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def stage(manifest_path: Path, output: Path, layout: str) -> list[str]:
    manifest_path = manifest_path.resolve()
    document = load_manifest(manifest_path)
    fixtures_dir = manifest_path.parent.resolve()
    output = output.resolve()

    if output.exists():
        fail(f"refusing to replace existing staging path: {output}")
    if output == fixtures_dir or fixtures_dir in output.parents:
        fail("staging output must not be inside the source fixture directory")

    entries = document["fixtures"]
    assert isinstance(entries, list)
    sources: list[tuple[dict[str, object], Path, dict[str, str]]] = []
    seen_directories: set[str] = set()
    seen_components: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            fail("every fixture manifest entry must be an object")
        directory = entry.get("directory")
        component = entry.get("component")
        if not isinstance(component, str) or not component:
            fail("every fixture needs a non-empty component")
        source = safe_source(fixtures_dir, directory)
        assert isinstance(directory, str)
        if directory in seen_directories:
            fail(f"duplicate fixture directory: {directory}")
        if component in seen_components:
            fail(f"duplicate fixture component: {component}")
        seen_directories.add(directory)
        seen_components.add(component)
        safe_destination(entry.get("legacy_destination"), "legacy_destination", component)
        safe_destination(entry.get("public_destination"), "public_destination", component)
        sources.append((entry, source, file_hashes(source)))

    primary_entry, primary_source, primary_hashes = sources[0]
    primary_name = primary_entry["directory"]
    assert isinstance(primary_name, str)
    primary_dir = output / "primary" / primary_name
    extras_dir = output / "extra-plugins"
    primary_dir.parent.mkdir(parents=True)
    extras_dir.mkdir()
    shutil.copytree(primary_source, primary_dir, copy_function=shutil.copy2)
    for entry, source, _ in sources[1:]:
        directory = entry["directory"]
        assert isinstance(directory, str)
        shutil.copytree(source, extras_dir / directory, copy_function=shutil.copy2)

    staged_entries: list[dict[str, object]] = []
    for index, (entry, _, hashes) in enumerate(sources):
        directory = entry["directory"]
        component = entry["component"]
        assert isinstance(directory, str) and isinstance(component, str)
        destination_key = f"{layout}_destination"
        staged_path = (
            Path("primary") / directory if index == 0 else Path("extra-plugins") / directory
        )
        staged_entry = dict(entry)
        staged_entry["destination"] = safe_destination(entry[destination_key], destination_key, component)
        staged_entry["staged_path"] = staged_path.as_posix()
        staged_entry["files"] = hashes
        staged_entries.append(staged_entry)

    staged_manifest = dict(document)
    staged_manifest["layout"] = layout
    staged_manifest["fixtures"] = staged_entries
    (output / "manifest.json").write_text(
        json.dumps(staged_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if file_hashes(primary_dir) != primary_hashes:
        fail(f"staged fixture differs from its source: {primary_name}")
    for entry, _, hashes in sources[1:]:
        directory = entry["directory"]
        assert isinstance(directory, str)
        if file_hashes(extras_dir / directory) != hashes:
            fail(f"staged fixture differs from its source: {directory}")

    return [
        entry["directory"]
        for entry, _, _ in sources
        if isinstance(entry["directory"], str)
    ]


def main() -> int:
    args = parse_args()
    try:
        staged = stage(args.manifest, args.output, args.layout)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Staged {len(staged)} fixtures: {', '.join(staged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
