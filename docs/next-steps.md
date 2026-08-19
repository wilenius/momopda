# Next Implementation Steps

This document is the context-clear handoff for the modernization work started on 19 August 2026.

## Repository State

- Branch: `feature/agent-skills-conversion`.
- Starting HEAD: `2e2eee2`.
- The modernization changes are intentionally uncommitted.
- The worktree contains deletion of the ten old skills and addition of the single canonical skill, fixtures, tools, workflows, adapters, knowledge metadata, and evaluation scaffolding.
- Do not restore the deleted skill files or the tracked `tags` artifact.
- Do not modify or discard unrelated user changes if any appear after this handoff.

The canonical entry point is `skills/moodle-plugin-development/SKILL.md`. There must remain exactly one `SKILL.md` under `skills/`.

## Verified Local Environment

| Tool | Verified value |
|---|---|
| PHP | 8.5.9 |
| `ext-iconv` | Enabled |
| Composer | 2.10.2 |
| Moodle Plugin CI | 4.5.11 |
| OpenCode | Discovery smoke test passes through `tools/validate_repo.py` |

The temporary Moodle Plugin CI installation is `/tmp/opencode/moodle-plugin-ci`. It now installs normally and passes `composer check-platform-reqs`; no platform requirement is ignored.

Recreate it if the temporary directory is removed:

```bash
composer create-project moodlehq/moodle-plugin-ci /tmp/opencode/moodle-plugin-ci 4.5.11 \
    --no-interaction --no-progress --prefer-dist
```

The Composer install reports one moderate npm advisory in Moodle Plugin CI's `moodle-local_ci` development dependency. It is not a dependency committed by this repository and did not block the checks.

## Verified Commands

Repository validation:

```bash
python3 -I -B tools/validate_repo.py
git diff --check
```

Knowledge and link freshness without the intentional 60-day support warning:

```bash
python3 -I -B tools/check_freshness.py --network --support-window 30
```

Strict fixture checks:

```bash
ci=/tmp/opencode/moodle-plugin-ci/bin/moodle-plugin-ci
for fixture in skills/moodle-plugin-development/assets/fixtures/*/version.php; do
    plugin="${fixture%/version.php}"
    "$ci" phplint "$plugin"
    "$ci" codechecker --max-warnings 0 "$plugin"
    "$ci" savepoints "$plugin"
done
```

All nine fixtures pass these checks with zero coding-style warnings.

The default freshness window is intentionally 60 days. As of this handoff, it exits non-zero because Moodle 5.0 security support ends on 5 October 2026. The scheduled workflow should create or update one review issue for this condition.

## Moodle Source Checkout

`../moodle` was used read-only to derive the contracts.

- Revision: `e3e51a0613c4e370911f9c84db685acc7df791f1`.
- Source reports `5.1dev+ (Build: 20250826)`.
- The checkout uses the Moodle 5.1 `public/` layout.
- Local tag `v4.5.6` was used for 4.5 contract comparisons.
- The checkout is not configured: root `config.php` is absent and `public/config.php` is only the loader.

Do not modify this checkout to test fixtures. Use Moodle Plugin CI to create isolated installations.

## Immediate Milestone

Implement the database-backed compatibility boundary matrix. Do this before expanding skill content or building model evaluations.

Required boundaries:

| Moodle tag | PHP | Role |
|---|---:|---|
| Latest pinned Moodle 4.5 patch | 8.1 | Oldest supported boundary |
| Latest pinned Moodle 5.2 patch | 8.4 | Newest stable boundary |

At handoff time the expected tags are `v4.5.13` and `v5.2.2`. Verify them against the official release page before pinning the workflow.

## Implementation Order

1. Inspect Moodle Plugin CI 4.5.11's current GitHub Actions example and `install --extra-plugins` behavior.
2. Add a deterministic fixture staging tool that reads `assets/fixtures/manifest.json` and never edits a source fixture or an existing Moodle checkout.
3. Add `.github/workflows/moodle-integration.yml` with the two boundary jobs and one PostgreSQL service.
4. Pin Moodle tags, Moodle Plugin CI 4.5.11, action commits, PHP versions, runner image, and database image.
5. Install all nine fixtures into one fresh Moodle site using their layout-specific destinations.
6. Add a post-install assertion script that bootstraps Moodle and verifies all nine components through `core_component` or `core_plugin_manager`.
7. Exercise each fixture's defining contract, not only plugin discovery.
8. Run Moodle Plugin CI validation, PHPDoc, Mustache, Grunt, PHPUnit, and savepoint checks where applicable.
9. Upload installation and test logs when a matrix job fails.
10. Add a scheduled non-blocking canary for moving supported branches and Moodle `main` only after the pinned boundary matrix is green.

## Contract Assertions

The first integration test should prove at least:

- `mod_momopda` installs its XMLDB table and exposes add, update, delete, and view contracts.
- `block_momopda` is discovered and its class passes block self-testing.
- `enrol_momopda` resolves both `lib.php` and `enrol_momopda_plugin`.
- `filter_momopda\text_filter` is the selected modern filter implementation.
- `local_momopda` installs as a valid no-op local plugin.
- `qbank_momopda\plugin_feature` returns its column for a real question-bank view.
- `qtype_momopda` is registered and can save/render an information item.
- `report_momopda` registers its administration page and capability.
- `tiny_momopda\plugininfo` is enabled without debugging warnings and its built AMD module passes Grunt checks.

Do not call the matrix complete if it only installs Moodle or runs PHP lint.

## Acceptance Criteria

- Both pinned boundary jobs pass from empty databases.
- Every fixture is installed at the correct pre-5.1 or 5.1+ physical path.
- Every component is discovered by Moodle after installation.
- Contract assertions run against the same fixture source under test.
- Strict coding-style and frontend warning thresholds remain zero.
- CI does not run code fixers or alter source fixtures.
- Failures retain enough logs to reproduce locally.
- `tools/validate_repo.py`, standalone Plugin CI checks, and `git diff --check` remain green.

After these criteria pass, rename `planned_integration_boundaries` in `knowledge/compatibility.json` to reflect enforced coverage and update `docs/roadmap.md`.

## Later Milestones

1. Build the public generation harness around `evals/public/tasks.json`.
2. Create the separate private holdout repository for hidden prompts, tests, and mutation cases.
3. Add source-path change tracking for selected Moodle contracts, not whole-branch churn.
4. Test a release artifact in current OpenCode and Claude Code releases.
5. Review the complete diff, commit the overhaul, merge it, and update the repository default branch only when explicitly requested.

## Invariants

- Keep one canonical skill; do not reintroduce inter-skill dependencies.
- Keep complete examples in executable fixtures rather than large unverified Markdown blocks.
- Keep CI validation non-fixing and report skipped functional checks as incomplete.
- Use target Moodle source and executable tests before local prose.
- Keep the 4.5/5.x path difference explicit: physical paths gain `public/` in Moodle 5.1+, URLs do not.
