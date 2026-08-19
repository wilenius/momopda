---
name: moodle-plugin-development
description: Develop, review, test, or upgrade Moodle plugins, including mod, block, enrol, filter, local, qbank, qtype, report, and TinyMCE plugins. Use when working with Moodle PHP, version.php, plugin callbacks, Moodle APIs, PHPUnit, Behat, Mustache, AMD modules, database upgrades, capabilities, or Moodle Plugin CI.
license: GPL-3.0-or-later
compatibility: Supports Moodle 4.5 LTS and security-supported Moodle 5.x releases. A Moodle checkout and Moodle Plugin CI are recommended for implementation validation.
metadata:
  author: momopda
  version: "0.2.0"
---

# Moodle Plugin Development

Use repository evidence and the target Moodle source before relying on remembered APIs. This skill provides routing and safety rules; detailed contracts are loaded only when relevant.

## Establish Context

Before changing code:

1. Read the plugin's `version.php` and identify `$plugin->component` and `$plugin->requires`.
2. Determine the target Moodle version from `$MOODLE_DIR/version.php` or `$MOODLE_DIR/public/version.php`.
3. Inspect existing repository instructions, CI configuration, tests, and neighboring code.
4. Locate the corresponding implementation and base classes in the target Moodle checkout.
5. Ask for the target Moodle version only when repository evidence cannot establish it.

Do not infer a version from task wording. Do not modify Moodle core unless the user explicitly asks for a core contribution.

## Route The Task

Read [compatibility](references/compatibility.md) for every task that adds files, changes APIs, or claims support for more than one Moodle branch.

Read exactly one primary plugin-type contract:

| Component | Contract |
|---|---|
| `mod_*` | [Activity modules](references/type-activity.md) |
| `block_*` | [Blocks](references/type-block.md) |
| `enrol_*` | [Enrolment methods](references/type-enrol.md) |
| `filter_*` | [Text filters](references/type-filter.md) |
| `local_*` | [Local plugins](references/type-local.md) |
| `qbank_*` | [Question bank plugins](references/type-qbank.md) |
| `qtype_*` | [Question types](references/type-qtype.md) |
| `report_*` | [Site reports](references/type-report.md) |
| `tiny_*` | [TinyMCE plugins](references/type-tiny.md) |

Add topic references based on the files and behavior involved:

| Work involves | Read |
|---|---|
| Parameters, capabilities, endpoints, output, files, or user data | [Security](references/security.md) |
| `install.xml`, DML, SQL, or `upgrade.php` | [Database](references/database.md) |
| Mustache, JavaScript, CSS, or interactive UI | [Frontend](references/frontend.md) |
| Tests, CI, review, or task completion | [Quality](references/quality.md) |

## Mandatory Engineering Rules

- Treat all request data as untrusted and use Moodle parameter APIs.
- Establish the correct context and enforce capabilities before reading or changing protected data.
- Require a sesskey for state-changing browser requests.
- Use Moodle DML with parameters; never interpolate request data into SQL.
- Escape plain output and use `format_text()` or `format_string()` for content with Moodle formatting semantics.
- Put user-visible text in language files.
- Prefer Mustache templates and renderables for non-trivial interfaces.
- Use the target Moodle checkout to verify callback names, inheritance, signatures, and deprecations.
- Add or update automated tests for behavior changes.
- Keep validation read-only. Run a fixer only as a separate, explicit action requested by the user.
- Report skipped checks as incomplete validation, not as success.

## Version-Aware Paths

- Moodle 4.5 places web-accessible code at the repository root, such as `mod/` and `filter/`.
- Moodle 5.1 and later place it below `public/`, such as `public/mod/` and `public/filter/`.
- Moodle URLs remain `/mod/...`, `/report/...`, and similar. Never add `/public` to generated URLs.
- Prefer component discovery APIs and `$CFG` paths over constructing filesystem paths.

## Implementation Workflow

1. Confirm intended behavior and compatibility range.
2. Inspect the relevant type contract and fixture.
3. Inspect the same contract in the target Moodle source.
4. Make the smallest complete change, including capabilities, language strings, privacy declarations, and upgrade steps when applicable.
5. Add focused PHPUnit tests and Behat scenarios when browser behavior is central.
6. Run repository-native checks, then Moodle Plugin CI where available.
7. Summarize checks that passed, failed, or could not run.

## Contract Fixtures

Minimal fixtures are in [`assets/fixtures`](assets/fixtures/README.md). They prove discovery and base contracts and provide complete examples. Copy concepts rather than component names. Do not treat fixture scope as production completeness.

## Source Authority

Resolve disagreements in this order:

1. Executable behavior and tests against the target Moodle version.
2. Pinned Moodle source for that version.
3. Versioned official Moodle developer documentation.
4. This skill's guidance.
5. Third-party implementations.

When this skill conflicts with the target source, follow the target source and report the stale guidance.
