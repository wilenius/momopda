# Moodle Plugin Quality Standards

## Overview

Before declaring any task complete, you MUST ensure the code meets Moodle's quality standards. This file provides a systematic approach to quality validation using automated tools.

## Moodle Plugin CI Integration

### Check for CI Tools Availability

Before running quality checks, verify that the Moodle Plugin CI tools are available:

```bash
if [ -d "../moodle-plugin-ci" ]; then
    # CI tools are available - use them for quality checks
    CI_AVAILABLE=true
else
    # CI tools not available - document limitations in response
    CI_AVAILABLE=false
fi
```

**IMPORTANT**: If `../moodle-plugin-ci/` exists, you MUST use these tools to validate code quality before declaring the task complete. In case of errors, resolve them before marking the task as done.

### Detect Moodle Installation Directory

Some CI commands require an active Moodle installation with `config.php`. Auto-detect the Moodle directory:

```bash
# Detect Moodle installation directory (check for config.php)
if [ -z "$MOODLE_DIR" ]; then
    # Try to find a configured Moodle install in common locations
    if [ -f "../moodle/config.php" ]; then
        MOODLE_DIR="../moodle"
    elif [ -f "${MOODLE_DIR}/config.php" ]; then
        MOODLE_DIR="${MOODLE_DIR}"
    elif [ -f "/var/www/moodle/config.php" ]; then
        MOODLE_DIR="/var/www/moodle"
    elif [ -f "$HOME/moodle/config.php" ]; then
        MOODLE_DIR="$HOME/moodle"
    fi
fi

# Validate that Moodle install is usable for CI tools requiring -m flag
if [ -n "$MOODLE_DIR" ] && [ -f "$MOODLE_DIR/config.php" ]; then
    MOODLE_AVAILABLE=true
else
    MOODLE_AVAILABLE=false
fi
```

**IMPORTANT**:
- Users can override auto-detection by setting `MOODLE_DIR` environment variable: `export MOODLE_DIR="/path/to/moodle"`
- Only installations with `config.php` are usable for CI commands requiring `-m` flag
- Git clones without `config.php` cannot be used for these commands

### Environment Requirements

CI tools have different requirements:

1. **Standalone Tools** (work with plugin code only):
   - `phplint` - PHP syntax validation
   - `codechecker` - Coding standards check
   - `codefixer` - Auto-fix coding standards
   - `phpmd` - Code quality analysis

2. **Require Active Moodle Install** (need config.php):
   - `validate` - Plugin validation (requires `-m ${MOODLE_DIR}`)
   - `phpdoc` - PHPDoc validation (requires local_moodlecheck plugin)
   - `phpunit` - Unit tests (requires vendor/bin/phpunit)
   - `mustache` - Template validation (requires special path setup)
   - `grunt` - JS/CSS build (requires grunt installed in Moodle)
   - `savepoints` - Database upgrade validation
   - `behat` - Acceptance tests (requires full test environment)

**Active Moodle Install Path**: Use `${MOODLE_DIR}` for commands requiring `-m` flag. Auto-detected or set via environment variable.

### Running CI Commands

CI commands are executed from the plugin root directory:

**Standalone commands:**
```bash
../moodle-plugin-ci/bin/moodle-plugin-ci <command> ./
```

**Commands requiring Moodle install:**
```bash
../moodle-plugin-ci/bin/moodle-plugin-ci <command> -m ${MOODLE_DIR} ./
```

## Quality Checks by Task Type

### MANDATORY CHECKS - Always Run These

Run these checks for ANY task involving code modifications:

1. **PHP Syntax Validation** ✅ ALWAYS RUN
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci phplint ./
   ```
   - **Purpose**: Detect PHP syntax errors
   - **Requirements**: None - standalone tool
   - **When to run**: ALWAYS, for any PHP file changes
   - **Action on failure**: Fix syntax errors immediately - BLOCKING

2. **Moodle Coding Standards** ✅ ALWAYS RUN
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci codechecker ./
   ```
   - **Purpose**: Validate adherence to Moodle coding standards
   - **Requirements**: None - standalone tool
   - **When to run**: ALWAYS, for any code changes
   - **Action on failure**: Use `codefixer` to auto-fix, then manually resolve remaining issues - BLOCKING
   - **Acceptable warnings**: Minor inline comment punctuation, line length up to 180 chars (15 warnings acceptable)

3. **Auto-fix Coding Standards** ✅ ALWAYS RUN (if codechecker fails)
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci codefixer ./
   ```
   - **Purpose**: Automatically fix coding standard violations
   - **Requirements**: None - standalone tool
   - **When to run**: After codechecker reports violations
   - **Action**: Re-run codechecker after applying fixes to verify

4. **Plugin Validation** ✅ ALWAYS RUN
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci validate -m ${MOODLE_DIR} ./
   ```
   - **Purpose**: Check plugin integrity and configuration (version.php, etc.)
   - **Requirements**: Active Moodle installation with config.php
   - **When to run**: ALWAYS, especially after modifying plugin metadata
   - **Action on failure**: Fix plugin configuration issues - BLOCKING

### OPTIONAL CHECKS - Run When Available

5. **Code Quality Analysis** ⚠️ RUN (ignore parser errors)
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci phpmd ./
   ```
   - **Purpose**: Detect potential code quality issues
   - **Requirements**: None - standalone tool
   - **When to run**:
     - After significant code changes
     - During refactoring tasks
     - For complex new features
   - **Action on failure**: Review and address legitimate violations
   - **Known issues**: May report parser errors on valid PHP - ignore these
   - **Acceptable**: Unused parameters, long variable names (case-by-case review)

6. **PHPDoc Documentation** ⏭️ SKIP (requires local_moodlecheck)
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci phpdoc -m ${MOODLE_DIR} ./
   ```
   - **Purpose**: Verify documentation completeness
   - **Requirements**: Active Moodle install with local_moodlecheck plugin
   - **Skip if**: local_moodlecheck not installed (common in dev environments)
   - **When to run**:
     - After adding new functions/classes
     - After modifying function signatures
     - During code reviews
   - **Action on failure**: Add or update PHPDoc blocks

7. **PHPUnit Tests** ⏭️ SKIP (requires phpunit in Moodle)
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci phpunit -m ${MOODLE_DIR} ./
   ```
   - **Purpose**: Run unit tests to ensure functionality
   - **Requirements**: Active Moodle install with vendor/bin/phpunit
   - **Skip if**: PHPUnit not installed in Moodle instance
   - **When to run**:
     - After implementing new features
     - After bug fixes
     - After refactoring
     - When test files are modified
   - **Action on failure**: Fix failing tests or update tests if behavior intentionally changed

### CONDITIONAL CHECKS - Database Changes

8. **Savepoint Validation** ✅ RUN (if db/upgrade.php exists)
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci savepoints -m ${MOODLE_DIR} ./
   ```
   - **Purpose**: Verify upgrade script savepoint consistency
   - **Requirements**: Active Moodle installation
   - **When to run**:
     - After modifying `db/upgrade.php`
     - After modifying `version.php`
     - After database schema changes
   - **Skip if**: No `db/upgrade.php` file exists
   - **Action on failure**: Fix savepoint version mismatches - BLOCKING

### CONDITIONAL CHECKS - Frontend Changes

9. **Mustache Template Validation** ⏭️ SKIP (path configuration issues)
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci mustache -m ${MOODLE_DIR} ./
   ```
   - **Purpose**: Validate Mustache template syntax
   - **Requirements**: Active Moodle install, complex path setup
   - **Skip**: Known path configuration issues in current environment
   - **Alternative**: Manually validate template syntax
   - **When to run**: After adding/modifying templates in `templates/`

10. **Grunt Build** ⏭️ SKIP (requires grunt in Moodle)
    ```bash
    ../moodle-plugin-ci/bin/moodle-plugin-ci grunt -m ${MOODLE_DIR} ./
    ```
    - **Purpose**: Process AMD modules, validate JS/CSS with eslint/stylelint
    - **Requirements**: Active Moodle install with grunt installed
    - **Skip if**: Grunt not installed in Moodle instance
    - **Alternative**: Run grunt manually in Moodle root if available
    - **When to run**:
      - After modifying JavaScript files
      - After modifying CSS/SCSS files
      - After modifying AMD modules in `amd/src/`

11. **Behat Acceptance Tests** ⏭️ SKIP (requires full test environment)
    ```bash
    ../moodle-plugin-ci/bin/moodle-plugin-ci behat -m ${MOODLE_DIR} ./
    ```
    - **Purpose**: Run acceptance tests for user workflows
    - **Requirements**: Full Moodle test environment with Behat configured
    - **Skip**: Requires extensive test environment setup
    - **When to run**:
      - After implementing new user-facing features
      - After modifying existing UI/UX
      - When Behat scenarios are added/modified

## Quality Check Workflow

### Recommended Order of Execution

Execute in this order to catch issues early and minimize re-runs:

1. **Phase 1: Basic Validation** ✅ ALWAYS RUN (fast, catches obvious issues)
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci phplint ./
   ../moodle-plugin-ci/bin/moodle-plugin-ci validate -m ${MOODLE_DIR} ./
   ```
   - Both must pass before proceeding
   - Fix any errors immediately

2. **Phase 2: Code Standards** ✅ ALWAYS RUN (auto-fixable)
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci codechecker ./
   # If violations found:
   ../moodle-plugin-ci/bin/moodle-plugin-ci codefixer ./
   # Re-run to verify:
   ../moodle-plugin-ci/bin/moodle-plugin-ci codechecker ./
   ```
   - Auto-fix most issues with codefixer
   - Manual fixes for remaining violations
   - Minor warnings (15 or fewer) are acceptable

3. **Phase 3: Quality Analysis** ⚠️ RUN (review results)
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci phpmd ./
   ```
   - Review violations, ignore parser errors
   - Fix legitimate quality issues
   - Some violations acceptable (unused params, long names)

4. **Phase 4: Conditional Tests** ⏭️ SKIP MOST (environment limitations)
   - `phpdoc` - SKIP (requires local_moodlecheck)
   - `phpunit` - SKIP (requires phpunit in Moodle)
   - `savepoints` - RUN if db/upgrade.php exists
   - `mustache` - SKIP (path issues)
   - `grunt` - SKIP (not installed)
   - `behat` - SKIP (requires test environment)

### Practical CI Test Command

For typical development work, run this sequence:

```bash
# Phase 1: Validation
../moodle-plugin-ci/bin/moodle-plugin-ci phplint ./
../moodle-plugin-ci/bin/moodle-plugin-ci validate -m ${MOODLE_DIR} ./

# Phase 2: Code Standards
../moodle-plugin-ci/bin/moodle-plugin-ci codechecker ./
# If errors, auto-fix:
../moodle-plugin-ci/bin/moodle-plugin-ci codefixer ./
# Verify:
../moodle-plugin-ci/bin/moodle-plugin-ci codechecker ./

# Phase 3: Quality
../moodle-plugin-ci/bin/moodle-plugin-ci phpmd ./
```

## Error Resolution Strategy

When CI checks fail:

1. **Read the error output carefully** - CI tools provide detailed feedback
2. **Auto-fix when possible** - Use `codefixer` for coding standards
3. **Fix issues incrementally** - Don't try to fix everything at once
4. **Re-run checks after fixes** - Verify each fix resolves the issue
5. **Document any false positives** - Some warnings may be acceptable (rare)

### Common Issues and Solutions

**Coding Standards Violations**
- ALWAYS run `codefixer` first - auto-fixes ~90% of issues
- Common auto-fixed issues:
  - Trailing whitespace at end of lines
  - Missing newline at end of file
  - Variable naming (underscores: `$bulk_ai_edit` → `$bulkaiedit`)
  - Missing trailing commas in multi-line arrays
- Manual fixes needed for:
  - Inline comments missing punctuation (add period/exclamation/question mark)
  - Lines exceeding 132 characters (refactor or split)
  - Whitespace within strings (check SQL queries)
- Check indentation (4 spaces, no tabs)
- Verify line length (<= 180 characters max, 132 preferred)

**PHPDoc Issues** (if running phpdoc)
- Add missing `@param` and `@return` tags
- Document all function parameters with types
- Include meaningful descriptions

**Validation Errors**
- Check `version.php` has correct version number and requires
- Ensure `version.php` version matches upgrade savepoints
- Verify all required plugin files exist:
  - `version.php`
  - `lang/en/{pluginname}.php`
  - `db/install.xml` (if using database)

**PHPMD Violations**
- Ignore parser errors (e.g., "Unexpected token") - these are tool bugs
- Review actual violations:
  - Unused parameters: acceptable for interface implementations
  - Long variable names (>20 chars): acceptable for clarity (e.g., `$partiallycorrectfeedback`)
  - Fix genuine code smells (unused variables, excessive complexity)

**PHPUnit Failures** (if running tests)
- Check if tests need updating for intentional behavior changes
- Ensure test database is properly set up
- Verify mock data and assertions are correct

**Mustache/Grunt Errors**
- Currently skipped due to environment limitations
- Manually validate template syntax if modified
- Test templates in browser after changes

## Task Completion Checklist

Before marking any task as complete, ensure:

### MANDATORY (Must All Pass):
- [ ] `phplint` - No PHP syntax errors
- [ ] `validate` - Plugin structure and metadata valid
- [ ] `codechecker` - Moodle coding standards met (0 errors, <15 warnings acceptable)
- [ ] Code changes manually tested in Moodle

### RECOMMENDED (Run When Possible):
- [ ] `phpmd` - Quality violations reviewed and addressed
- [ ] `savepoints` - Database upgrade scripts validated (if db/upgrade.php exists)

### OPTIONAL (Skip in Current Environment):
- [ ] `phpdoc` - Documentation complete (SKIP: requires local_moodlecheck)
- [ ] `phpunit` - Unit tests pass (SKIP: requires phpunit installation)
- [ ] `mustache` - Templates validated (SKIP: path configuration issues)
- [ ] `grunt` - JS/CSS built (SKIP: requires grunt installation)
- [ ] `behat` - Acceptance tests pass (SKIP: requires test environment)

### Task Complete When:
- All MANDATORY checks pass
- RECOMMENDED checks run (if applicable files exist)
- Any code changes manually verified in Moodle
- No critical PHPMD violations

## Quick Reference

### What to Always Run
```bash
# 1. PHP Syntax
../moodle-plugin-ci/bin/moodle-plugin-ci phplint ./

# 2. Plugin Validation
../moodle-plugin-ci/bin/moodle-plugin-ci validate -m ${MOODLE_DIR} ./

# 3. Coding Standards
../moodle-plugin-ci/bin/moodle-plugin-ci codechecker ./
# If errors:
../moodle-plugin-ci/bin/moodle-plugin-ci codefixer ./
../moodle-plugin-ci/bin/moodle-plugin-ci codechecker ./

# 4. Quality Analysis
../moodle-plugin-ci/bin/moodle-plugin-ci phpmd ./
```

### What to Skip in Current Environment
- ❌ `phpdoc` - Requires local_moodlecheck plugin
- ❌ `phpunit` - Requires vendor/bin/phpunit installation
- ❌ `mustache` - Path configuration issues
- ❌ `grunt` - Not installed in Moodle
- ❌ `behat` - Requires full test environment

### What to Run Conditionally
- ✅ `savepoints -m ${MOODLE_DIR} ./` - Only if db/upgrade.php exists

## When CI Tools Are Not Available

If `../moodle-plugin-ci/` does not exist:

1. **Inform the user** that CI tools are not available
2. **Manual review checklist**:
   - Check PHP syntax manually with `php -l`
   - Review code against [Moodle Coding Standards](https://moodledev.io/general/development/policies/codingstyle)
   - Verify all files have proper PHPDoc blocks
   - Test functionality manually in Moodle
3. **Recommend installation**: Suggest installing moodle-plugin-ci for better quality assurance

## Additional Resources

- [Moodle Plugin CI Documentation](https://moodlehq.github.io/moodle-plugin-ci/)
- [Moodle Coding Style](https://moodledev.io/general/development/policies/codingstyle)
- [Moodle Plugin Validation](https://moodledev.io/general/development/policies/pluginvalidation)
