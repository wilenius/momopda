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

### Running CI Commands

All CI commands are executed from the plugin root directory with this pattern:
```bash
../moodle-plugin-ci/bin/moodle-plugin-ci <command> ./
```

## Quality Checks by Task Type

### For ALL Code Changes

Run these checks for ANY task involving code modifications:

1. **PHP Syntax Validation**
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci phplint ./
   ```
   - **Purpose**: Detect PHP syntax errors
   - **When to run**: ALWAYS, for any PHP file changes
   - **Action on failure**: Fix syntax errors immediately

2. **Moodle Coding Standards**
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci codechecker ./
   ```
   - **Purpose**: Validate adherence to Moodle coding standards
   - **When to run**: ALWAYS, for any code changes
   - **Action on failure**: Use `codefixer` to auto-fix, then manually resolve remaining issues

3. **Auto-fix Coding Standards** (if codechecker fails)
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci codefixer ./
   ```
   - **Purpose**: Automatically fix coding standard violations
   - **When to run**: After codechecker reports violations
   - **Action**: Re-run codechecker after applying fixes

4. **Plugin Validation**
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci validate ./
   ```
   - **Purpose**: Check plugin integrity and configuration (version.php, etc.)
   - **When to run**: ALWAYS, especially after modifying plugin metadata
   - **Action on failure**: Fix plugin configuration issues

### For New Features or Bug Fixes

5. **PHPUnit Tests**
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci phpunit ./
   ```
   - **Purpose**: Run unit tests to ensure functionality
   - **When to run**:
     - After implementing new features
     - After bug fixes
     - After refactoring
     - When test files are modified
   - **Action on failure**: Fix failing tests or update tests if behavior intentionally changed

6. **PHPDoc Documentation**
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci phpdoc ./
   ```
   - **Purpose**: Verify documentation completeness
   - **When to run**:
     - After adding new functions/classes
     - After modifying function signatures
     - During code reviews
   - **Action on failure**: Add or update PHPDoc blocks

7. **Code Quality Analysis**
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci phpmd ./
   ```
   - **Purpose**: Detect potential code quality issues
   - **When to run**:
     - After significant code changes
     - During refactoring tasks
     - For complex new features
   - **Action on failure**: Review and address legitimate issues (some warnings may be acceptable)

### For Database/Upgrade Changes

8. **Savepoint Validation**
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci savepoints ./
   ```
   - **Purpose**: Verify upgrade script savepoint consistency
   - **When to run**:
     - After modifying `db/upgrade.php`
     - After modifying `version.php`
     - After database schema changes
   - **Action on failure**: Fix savepoint version mismatches

### For Frontend Changes

9. **Mustache Template Validation**
   ```bash
   ../moodle-plugin-ci/bin/moodle-plugin-ci mustache ./
   ```
   - **Purpose**: Validate Mustache template syntax
   - **When to run**:
     - After adding new templates
     - After modifying existing templates in `templates/`
   - **Action on failure**: Fix template syntax errors

10. **Grunt Build** (JavaScript, CSS, AMD modules)
    ```bash
    ../moodle-plugin-ci/bin/moodle-plugin-ci grunt ./
    ```
    - **Purpose**: Process AMD modules, validate JS/CSS with eslint/stylelint
    - **When to run**:
      - After modifying JavaScript files
      - After modifying CSS/SCSS files
      - After modifying AMD modules in `amd/src/`
    - **Action on failure**: Fix linting errors, rebuild assets

### For User-Facing Features

11. **Behat Acceptance Tests**
    ```bash
    ../moodle-plugin-ci/bin/moodle-plugin-ci behat ./
    ```
    - **Purpose**: Run acceptance tests for user workflows
    - **When to run**:
      - After implementing new user-facing features
      - After modifying existing UI/UX
      - When Behat scenarios are added/modified
    - **Action on failure**: Fix test failures or update scenarios

## Quality Check Workflow

### Recommended Order of Execution

1. **Phase 1: Basic Validation** (fast, catches obvious issues)
   - `phplint` - Syntax errors
   - `validate` - Plugin configuration

2. **Phase 2: Code Standards** (auto-fixable)
   - `codechecker` - Detect violations
   - `codefixer` - Auto-fix violations
   - `codechecker` - Verify fixes

3. **Phase 3: Documentation & Quality**
   - `phpdoc` - Documentation completeness
   - `phpmd` - Code quality issues (review carefully)

4. **Phase 4: Functional Testing**
   - `phpunit` - Unit tests
   - `savepoints` - If database changes exist
   - `mustache` - If templates exist
   - `grunt` - If frontend assets exist
   - `behat` - If user-facing features exist

## Error Resolution Strategy

When CI checks fail:

1. **Read the error output carefully** - CI tools provide detailed feedback
2. **Auto-fix when possible** - Use `codefixer` for coding standards
3. **Fix issues incrementally** - Don't try to fix everything at once
4. **Re-run checks after fixes** - Verify each fix resolves the issue
5. **Document any false positives** - Some warnings may be acceptable (rare)

### Common Issues and Solutions

**Coding Standards Violations**
- Run `codefixer` first
- Check indentation (4 spaces, no tabs)
- Verify line length (<= 180 characters)
- Check naming conventions (snake_case for functions/variables)

**PHPDoc Issues**
- Add missing `@param` and `@return` tags
- Document all function parameters with types
- Include meaningful descriptions

**Validation Errors**
- Check `version.php` has correct version number and requires
- Ensure `version.php` version matches upgrade savepoints
- Verify all required plugin files exist

**PHPUnit Failures**
- Check if tests need updating for intentional behavior changes
- Ensure test database is properly set up
- Verify mock data and assertions are correct

**Mustache/Grunt Errors**
- Fix syntax errors in templates
- Run `grunt ignorefiles` to update `.eslintignore` if needed
- Check for proper string escaping in JS

## Task Completion Checklist

Before marking any task as complete, ensure:

- [ ] All relevant CI commands have been run
- [ ] All CI checks pass (or failures are documented and justified)
- [ ] Code follows Moodle coding standards (codechecker passes)
- [ ] Documentation is complete (phpdoc passes)
- [ ] Tests pass (phpunit passes for code changes)
- [ ] Plugin validates successfully (validate passes)
- [ ] Frontend assets are built if modified (grunt passes if applicable)

## When CI Tools Are Not Available

If `../moodle-plugin-ci/` does not exist:

1. **Inform the user** that CI tools are not available
2. **Manual review checklist**:
   - Check PHP syntax manually
   - Review code against [Moodle Coding Standards](https://moodledev.io/general/development/policies/codingstyle)
   - Verify all files have proper PHPDoc blocks
   - Test functionality manually
3. **Recommend installation**: Suggest installing moodle-plugin-ci for better quality assurance

## Additional Resources

- [Moodle Plugin CI Documentation](https://moodlehq.github.io/moodle-plugin-ci/)
- [Moodle Coding Style](https://moodledev.io/general/development/policies/codingstyle)
- [Moodle Plugin Validation](https://moodledev.io/general/development/policies/pluginvalidation)
