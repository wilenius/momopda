# Quality And Completion

## Validation Order

1. Run repository-native tests and format checks.
2. Run PHP syntax and Moodle coding-style checks.
3. Run plugin validation against the target Moodle version.
4. Run PHPUnit for changed behavior.
5. Run Mustache and Grunt checks for frontend changes.
6. Run savepoint checks and install/upgrade tests for schema changes.
7. Run focused Behat scenarios when browser workflows are central.

Use the bundled `scripts/validate-plugin.sh` only when the project does not already provide a better command. The script is read-only and returns exit code `2` when Moodle-dependent validation cannot run.

## Test Design

Test observable contracts rather than private implementation details. Include authorization failures, invalid data, empty states, and version-sensitive paths. Use Moodle generators and reset global state according to Moodle's PHPUnit conventions.

## Completion Report

State exactly which checks passed. List skipped checks and their missing prerequisites. Never describe lint-only validation as functional testing, and never report success after an automatic fixer changed unreviewed code.
