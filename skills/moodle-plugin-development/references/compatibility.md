# Compatibility

## Supported Range

MoMoPDA targets Moodle 4.5 LTS and Moodle 5.x branches that still receive upstream security support. Check the project's own compatibility promise before broadening or narrowing that range.

## Detect The Version

Use this evidence in order:

1. `$MOODLE_DIR/public/version.php` when present.
2. `$MOODLE_DIR/version.php` for pre-5.1 layouts.
3. The plugin's `$plugin->requires` and CI matrix.
4. An explicit user requirement.

If evidence conflicts, stop and clarify rather than silently choosing the newest API.

## Public Directory Restructure

Moodle 5.1 moved web-accessible code beneath `public/`. A checkout can therefore contain either `filter/example` or `public/filter/example`. URLs and Frankenstyle component names did not gain a `public` segment.

Use `$CFG->dirroot`, `$CFG->libdir`, plugin discovery APIs, and Moodle Plugin CI instead of hard-coded repository paths.

## Cross-Version Design

- Use an API available throughout the declared range when that remains supported.
- Isolate unavoidable version differences behind a narrow compatibility boundary.
- Do not use deprecated compatibility shims merely because they still exist.
- Do not claim compatibility based only on PHP syntax. Install and exercise contract fixtures against boundary versions.
- Record an explicit minimum Moodle build in `version.php`.

The repository support data is in `knowledge/compatibility.json`. That file is maintenance metadata, not a substitute for inspecting the target project.
