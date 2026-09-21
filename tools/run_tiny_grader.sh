#!/usr/bin/env bash
# Grade one prepared tiny-toolbar-button run in an isolated pinned worker.

set -euo pipefail

if [[ "$#" -ne 1 ]]; then
    printf 'Usage: %s RUN_DIRECTORY\n' "$0" >&2
    exit 2
fi

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
run_dir="$(realpath "$1")"
dockerfile="$repo_root/tools/tiny-grader.Dockerfile"
image="${MOMOPDA_TINY_GRADER_IMAGE:-momopda/tiny-grader:php8.4-node22-plugin-ci4.5.11}"
postgres_image="postgres@sha256:d13db94ae661d517c5ed57c509a578d5ea64aae639871ba25294f4f42d83de28"
suffix="$$-$(date +%s)"
network="momopda-tiny-$suffix"
database="momopda-tiny-db-$suffix"

if [[ ! -f "$run_dir/prepare.json" || ! -f "$run_dir/run.json" ]]; then
    printf 'Run directory is not prepared: %s\n' "$run_dir" >&2
    exit 2
fi
python3 -I -B -c '
import json
import pathlib
import sys

prepared = json.loads((pathlib.Path(sys.argv[1]) / "prepare.json").read_text(encoding="utf-8"))
if prepared.get("task", {}).get("id") != "tiny-toolbar-button":
    raise SystemExit("runner only accepts tiny-toolbar-button")
moodle = prepared.get("revisions", {}).get("moodle", {})
expected = {
    "tag": "v5.2.2",
    "commit": "acfa383c13dd46c83ca82894a8e95fac273fda33",
    "php": "8.4",
    "layout": "public",
    "destination": "public/lib/editor/tiny/plugins/momopda",
}
if any(moodle.get(key) != value for key, value in expected.items()):
    raise SystemExit("prepared run does not match the pinned Moodle 5.2.2 Tiny boundary")
' "$run_dir"

cleanup() {
    docker rm --force --volumes "$database" >/dev/null 2>&1 || true
    docker network rm "$network" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

docker build \
    --quiet \
    --platform linux/amd64 \
    --file "$dockerfile" \
    --tag "$image" \
    "$repo_root/tools"

docker network create "$network" >/dev/null
docker run --detach \
    --name "$database" \
    --network "$network" \
    --network-alias postgres \
    --env POSTGRES_PASSWORD=moodle \
    --tmpfs /var/lib/postgresql/data:rw,nosuid,nodev,size=1g \
    --health-cmd 'pg_isready -U postgres -d postgres' \
    --health-interval 2s \
    --health-timeout 5s \
    --health-retries 30 \
    "$postgres_image" >/dev/null

for _ in {1..60}; do
    health="$(docker inspect --format '{{.State.Health.Status}}' "$database")"
    if [[ "$health" == "healthy" ]]; then
        break
    fi
    if [[ "$health" == "unhealthy" ]]; then
        printf 'PostgreSQL did not become healthy.\n' >&2
        docker logs "$database" >&2
        exit 1
    fi
    sleep 1
done
if [[ "$(docker inspect --format '{{.State.Health.Status}}' "$database")" != "healthy" ]]; then
    printf 'Timed out waiting for PostgreSQL.\n' >&2
    exit 1
fi

docker run --rm \
    --platform linux/amd64 \
    --network "$network" \
    --read-only \
    --tmpfs /tmp:rw,exec,nosuid,nodev,size=2g \
    --cap-drop ALL \
    --security-opt no-new-privileges \
    --user "$(id -u):$(id -g)" \
    --env LANG=en_AU.UTF-8 \
    --env LC_ALL=en_AU.UTF-8 \
    --mount "type=bind,source=$repo_root,target=/repo,readonly" \
    --mount "type=bind,source=$run_dir,target=/run" \
    --workdir /repo \
    "$image" \
    /bin/bash -c '
        set -euo pipefail
        test "$(php -r "echo PHP_MAJOR_VERSION.'"'"'.'"'"'.PHP_MINOR_VERSION;")" = "8.4"
        test "$(node --version)" = "v22.11.0"
        test "$(npm --version)" = "10.9.0"
        server_version="$(PGPASSWORD=moodle psql --host postgres --username postgres --dbname postgres --tuples-only --no-align --command "SHOW server_version")"
        [[ "$server_version" == 17.11* ]]
        cp -a /opt/moodle-plugin-ci /tmp/moodle-plugin-ci
        python3 -I -B /repo/tools/eval_harness.py grade \
            --run-dir /run \
            --plugin-ci /tmp/moodle-plugin-ci/bin/moodle-plugin-ci \
            --db-host postgres \
            --db-port 5432 \
            --db-user postgres \
            --db-pass moodle
        test "$(git -C /run/grading/moodle rev-parse HEAD)" = "acfa383c13dd46c83ca82894a8e95fac273fda33"
        test -f /run/grading/moodle/admin/cli/install_database.php
        test -d /run/grading/moodle/public
        test -f /run/grading/moodle/public/lib/editor/tiny/plugins/momopda/version.php
    '

python3 -I -B "$repo_root/tools/eval_harness.py" validate "$run_dir"
python3 -I -B -c '
import json
import pathlib
import sys

record = json.loads((pathlib.Path(sys.argv[1]) / "run.json").read_text(encoding="utf-8"))
status = record["status"]
if status not in {"pass", "fail"}:
    raise SystemExit(f"grading ended as {status}, not pass or fail")
if any(check["status"] not in {"pass", "fail"} for check in record["checks"]):
    raise SystemExit("one or more declared checks did not produce pass or fail")
moodle = record["revisions"]["moodle"]
if moodle != {
    "release": "5.2",
    "tag": "v5.2.2",
    "commit": "acfa383c13dd46c83ca82894a8e95fac273fda33",
    "php": "8.4",
    "layout": "public",
    "destination": "public/lib/editor/tiny/plugins/momopda",
}:
    raise SystemExit("saved evidence does not match the pinned Tiny boundary")
print(f"Pinned disposable Tiny grade reached every declared check: {status}")
' "$run_dir"
