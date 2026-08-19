#!/usr/bin/env python3
"""Check MoMoPDA support metadata and authoritative source availability."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
COMPATIBILITY = ROOT / "knowledge" / "compatibility.json"
SOURCES = ROOT / "knowledge" / "sources.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network", action="store_true", help="Check authoritative HTTP sources.")
    parser.add_argument(
        "--max-review-age",
        type=int,
        default=90,
        help="Maximum days since the knowledge registry was reviewed.",
    )
    parser.add_argument(
        "--support-window",
        type=int,
        default=60,
        help="Flag releases whose security support ends within this many days.",
    )
    return parser.parse_args()


def read_object(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Unable to read {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": "momopda-freshness-check/1"})
    with urlopen(request, timeout=30) as response:
        if response.status < 200 or response.status >= 300:
            raise HTTPError(url, response.status, "unexpected status", response.headers, None)
        return response.read().decode("utf-8", errors="replace")


def main() -> int:
    args = parse_args()
    today = date.today()
    findings: list[str] = []
    notes: list[str] = []

    try:
        compatibility = read_object(COMPATIBILITY)
        sources = read_object(SOURCES)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    review_dates: list[tuple[str, date]] = []
    for name, document in (("compatibility", compatibility), ("sources", sources)):
        raw_date = document.get("reviewed_on")
        try:
            reviewed = date.fromisoformat(str(raw_date))
        except ValueError:
            findings.append(f"{name} has an invalid reviewed_on date: {raw_date}")
            continue
        review_dates.append((name, reviewed))
        if reviewed > today:
            findings.append(f"{name} has a future reviewed_on date: {reviewed.isoformat()}")
            continue
        age = (today - reviewed).days
        if age > args.max_review_age:
            findings.append(f"{name} was last reviewed {age} days ago on {reviewed.isoformat()}")

    releases = compatibility.get("supported_releases", [])
    if not isinstance(releases, list):
        findings.append("supported_releases is not a list")
        releases = []
    for release in releases:
        if not isinstance(release, dict):
            findings.append("supported_releases contains a non-object entry")
            continue
        version = release.get("moodle", "unknown")
        raw_end = release.get("security_support_ends")
        try:
            support_end = date.fromisoformat(str(raw_end))
        except ValueError:
            findings.append(f"Moodle {version} has an invalid security support date: {raw_end}")
            continue
        remaining = (support_end - today).days
        if remaining < 0:
            findings.append(f"Moodle {version} security support ended on {support_end.isoformat()}")
        elif support_end <= today + timedelta(days=args.support_window):
            findings.append(
                f"Moodle {version} security support ends in {remaining} days on {support_end.isoformat()}"
            )
        else:
            notes.append(f"Moodle {version} security support: {remaining} days remaining")

    if args.network:
        entries = sources.get("sources", [])
        if not isinstance(entries, list):
            findings.append("sources is not a list")
            entries = []
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("url"), str):
                continue
            source_id = entry.get("id", "unknown")
            url = entry["url"]
            try:
                content = fetch(url)
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                findings.append(f"Authoritative source {source_id} is unavailable: {url} ({exc})")
                continue
            if not content.strip():
                findings.append(f"Authoritative source {source_id} returned no content: {url}")
            else:
                notes.append(f"Authoritative source reachable: {source_id}")

    print(f"MoMoPDA freshness report for {today.isoformat()}")
    for note in sorted(notes):
        print(f"OK: {note}")
    for finding in sorted(findings):
        print(f"REVIEW: {finding}")

    if findings:
        print(f"Freshness review required for {len(findings)} item(s).")
        return 1
    print("Knowledge metadata is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
