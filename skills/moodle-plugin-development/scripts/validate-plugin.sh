#!/usr/bin/env bash
# Read-only Moodle plugin validation.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SOURCE_PLUGIN="${1:-.}"
FAILED=0
INCOMPLETE=0

if [[ ! -d "$SOURCE_PLUGIN" ]]; then
    printf 'Plugin path does not exist: %s\n' "$SOURCE_PLUGIN" >&2
    exit 1
fi

SOURCE_PLUGIN="$(cd "$SOURCE_PLUGIN" && pwd -P)"

if [[ -n "${MOODLE_PLUGIN_CI_BIN:-}" ]]; then
    CI_BIN="$MOODLE_PLUGIN_CI_BIN"
elif command -v moodle-plugin-ci >/dev/null 2>&1; then
    CI_BIN="$(command -v moodle-plugin-ci)"
elif [[ -x "$SOURCE_PLUGIN/../moodle-plugin-ci/bin/moodle-plugin-ci" ]]; then
    CI_BIN="$SOURCE_PLUGIN/../moodle-plugin-ci/bin/moodle-plugin-ci"
else
    printf '%s\n' 'Moodle Plugin CI was not found.' >&2
    printf '%s\n' 'Set MOODLE_PLUGIN_CI_BIN or add moodle-plugin-ci to PATH.' >&2
    exit 2
fi

WORK_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/momopda-plugin-ci.XXXXXX")"
trap 'rm -rf -- "$WORK_ROOT"' EXIT
PLUGIN_PATH="$WORK_ROOT/plugin"
mkdir "$PLUGIN_PATH"
if ! cp -a "$SOURCE_PLUGIN/." "$PLUGIN_PATH/"; then
    printf '%s\n' 'Unable to create an isolated validation copy.' >&2
    exit 1
fi

run_check() {
    local label="$1"
    shift

    printf '\n== %s ==\n' "$label"
    if "$CI_BIN" "$@"; then
        printf '[OK] %s\n' "$label"
    else
        printf '[FAIL] %s\n' "$label" >&2
        FAILED=1
    fi
}

run_check 'PHP syntax' phplint "$PLUGIN_PATH"
run_check 'Moodle coding style' codechecker --max-warnings 0 "$PLUGIN_PATH"

if [[ -f "$PLUGIN_PATH/db/upgrade.php" ]]; then
    run_check 'Upgrade savepoints' savepoints "$PLUGIN_PATH"
fi

if [[ -n "${MOODLE_DIR:-}" && -f "$MOODLE_DIR/config.php" ]]; then
    MOODLE_ROOT="$(cd "$MOODLE_DIR" && pwd -P)"
    run_check 'Plugin validation' validate -m "$MOODLE_DIR" "$PLUGIN_PATH"
    run_check 'PHP documentation' phpdoc --max-warnings 0 -m "$MOODLE_DIR" "$PLUGIN_PATH"
    if [[ -d "$PLUGIN_PATH/templates" ]]; then
        run_check 'Mustache templates' mustache -m "$MOODLE_DIR" "$PLUGIN_PATH"
    fi
    if [[ -d "$PLUGIN_PATH/amd/src" || -f "$PLUGIN_PATH/styles.css" ]]; then
        run_check 'Frontend build' grunt --max-lint-warnings 0 -m "$MOODLE_DIR" "$PLUGIN_PATH"
    fi
    if [[ -d "$SOURCE_PLUGIN/tests" ]]; then
        INSTALLED_PLUGIN="$(php "$SCRIPT_DIR/resolve-installed-plugin.php" "$MOODLE_ROOT" "$SOURCE_PLUGIN" 2>/dev/null || true)"
        if [[ -n "$INSTALLED_PLUGIN" && "$INSTALLED_PLUGIN" = "$SOURCE_PLUGIN" ]]; then
            PLUGIN_IS_INSTALLED=true
        else
            PLUGIN_IS_INSTALLED=false
        fi
    else
        PLUGIN_IS_INSTALLED=false
    fi
    if [[ -d "$SOURCE_PLUGIN/tests" && "$PLUGIN_IS_INSTALLED" = true ]]; then
        run_check 'PHPUnit' phpunit -m "$MOODLE_DIR" "$SOURCE_PLUGIN"
    elif [[ -d "$SOURCE_PLUGIN/tests" ]]; then
        printf '\n[INCOMPLETE] PHPUnit was not run because the source plugin is not inside MOODLE_DIR.\n' >&2
        INCOMPLETE=1
    fi
    if [[ -d "$SOURCE_PLUGIN/tests/behat" && "$PLUGIN_IS_INSTALLED" = true ]]; then
        run_check 'Behat' behat -m "$MOODLE_DIR" "$SOURCE_PLUGIN"
    elif [[ -d "$SOURCE_PLUGIN/tests/behat" ]]; then
        printf '\n[INCOMPLETE] Behat was not run because the source plugin is not inside MOODLE_DIR.\n' >&2
        INCOMPLETE=1
    fi
else
    printf '\n[INCOMPLETE] Moodle-dependent checks were skipped.\n' >&2
    printf 'Set MOODLE_DIR to a configured Moodle installation containing config.php.\n' >&2
    INCOMPLETE=1
fi

printf '\n== Validation summary ==\n'
if [[ "$FAILED" -ne 0 ]]; then
    printf '%s\n' 'One or more checks failed.' >&2
    exit 1
fi
if [[ "$INCOMPLETE" -ne 0 ]]; then
    printf '%s\n' 'Available checks passed, but validation is incomplete.' >&2
    exit 2
fi

printf '%s\n' 'All applicable checks passed.'
