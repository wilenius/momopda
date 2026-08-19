#!/usr/bin/env python3
"""Install the canonical skill into a supported client's project directory."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "moodle-plugin-development"
CLIENT_PATHS = {
    "opencode": Path(".opencode/skills/moodle-plugin-development"),
    "claude-code": Path(".claude/skills/moodle-plugin-development"),
}
SHARED_PATH = Path(".claude/skills/moodle-plugin-development")
MARKER_NAME = ".momopda-install.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--client",
        choices=(*CLIENT_PATHS, "all"),
        required=True,
        help="Client adapter to install. 'all' uses the Claude-compatible path shared by both clients.",
    )
    parser.add_argument(
        "--project",
        type=Path,
        required=True,
        help="Existing plugin project directory.",
    )
    parser.add_argument(
        "--mode",
        choices=("auto", "copy", "symlink"),
        default="auto",
        help="Use a link, a vendored copy, or choose a link only when MoMoPDA is inside the project.",
    )
    parser.add_argument(
        "--update",
        action="store_true",
        help="Replace an existing vendored copy created by this installer.",
    )
    return parser.parse_args()


def existing_ancestor(path: Path) -> Path:
    current = path
    while not current.exists() and not current.is_symlink():
        current = current.parent
    return current


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def is_managed_copy(target: Path) -> bool:
    marker = target / MARKER_NAME
    if target.is_symlink() or not marker.is_file():
        return False
    try:
        value = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return value == {"installer": "momopda", "skill": "moodle-plugin-development"}


def install_copy(target: Path, update: bool) -> None:
    staging = target.with_name(f".{target.name}.momopda-new")
    backup = target.with_name(f".{target.name}.momopda-old")
    if staging.exists() or staging.is_symlink() or backup.exists() or backup.is_symlink():
        raise OSError(f"stale installer staging path exists beside {target}")

    try:
        shutil.copytree(SOURCE, staging)
        marker = {"installer": "momopda", "skill": "moodle-plugin-development"}
        (staging / MARKER_NAME).write_text(json.dumps(marker, sort_keys=True) + "\n", encoding="utf-8")
        if update:
            target.rename(backup)
        staging.rename(target)
        if update:
            shutil.rmtree(backup)
    except OSError:
        if staging.exists() and not staging.is_symlink():
            shutil.rmtree(staging)
        if update and backup.exists() and not target.exists():
            backup.rename(target)
        raise


def main() -> int:
    args = parse_args()
    project = args.project.expanduser().resolve()
    if not project.is_dir():
        print(f"Project directory does not exist: {project}", file=sys.stderr)
        return 1
    if not (SOURCE / "SKILL.md").is_file():
        print(f"Canonical skill is missing: {SOURCE}", file=sys.stderr)
        return 1
    if is_within(project, SOURCE):
        print("Refusing to install a skill inside its own source directory.", file=sys.stderr)
        return 1

    if args.client == "all":
        targets = [("OpenCode and Claude Code", project / SHARED_PATH)]
    else:
        targets = [(args.client, project / CLIENT_PATHS[args.client])]

    if args.mode == "auto":
        mode = "symlink" if is_within(SOURCE, project) else "copy"
    else:
        mode = args.mode

    skipped_targets: set[Path] = set()
    update_targets: set[Path] = set()
    for client, target in targets:
        ancestor = existing_ancestor(target.parent)
        if not is_within(ancestor, project):
            print(f"Refusing adapter path outside the project: {target}", file=sys.stderr)
            return 1
        if is_within(target, SOURCE):
            print(f"Refusing recursive adapter destination: {target}", file=sys.stderr)
            return 1
        if target.is_symlink() and target.resolve() == SOURCE:
            skipped_targets.add(target)
            continue
        if target.exists() or target.is_symlink():
            if mode == "copy" and args.update and is_managed_copy(target):
                update_targets.add(target)
            else:
                print(f"Refusing to replace existing {client} adapter: {target}", file=sys.stderr)
                return 1

    for client, target in targets:
        if target in skipped_targets:
            print(f"Already installed for {client}: {target}")
            continue
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            if mode == "symlink":
                relative_source = os.path.relpath(SOURCE, start=target.parent)
                target.symlink_to(relative_source, target_is_directory=True)
                detail = f"{target} -> {relative_source}"
            else:
                install_copy(target, target in update_targets)
                detail = f"{target} (vendored copy)"
        except OSError as exc:
            print(f"Unable to install the {client} adapter: {exc}", file=sys.stderr)
            return 1
        print(f"Installed for {client}: {detail}")

    print("Restart running clients to reload skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
