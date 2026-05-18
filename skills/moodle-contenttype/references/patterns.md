# Content Bank Type Patterns and Anti-Patterns

## Good Patterns

### 1) Keep type and content responsibilities separated

- `contenttype` class: declares features, capabilities, rendering, and type-level behavior.
- `content` class: enforces instance-level checks and file import behavior.

### 2) Validate uploads before persisting side effects

In `import_file(...)`, validate file format and reject invalid files with Moodle exceptions.

### 3) Reuse core cleanup flow

If you override `delete_content(...)`, do plugin-specific cleanup first, then call `parent::delete_content(...)`.

### 4) Test by role and context

Always test permissions in system, category, and course contexts because Content bank visibility differs by context and role.

### 5) Use core generators in tests

Prefer `core_contentbank` test generators for fast, consistent setup and less test boilerplate.

## Anti-Patterns

### 1) Hardcoding one context scope

Do not assume all content is system-level; course and category contexts are common.

### 2) Missing capability checks in custom actions

If you add custom edit/copy/delete behavior, capability checks must happen before action execution.

### 3) Skipping language strings

Do not hardcode visible text in PHP; add plugin strings in `lang/en/contenttype_yourtype.php`.

### 4) Incomplete feature declarations

If your plugin supports download/copy/edit, return the feature in `get_implemented_features()`; otherwise the UI and APIs may behave unexpectedly.

### 5) Tests that only assert happy path

Include invalid uploads, disabled capabilities, and ownership mismatch scenarios.

## Practical Review Checklist

- Class names match plugin frankenstyle (`contenttype_yourtype`).
- `version.php` component is correct.
- `get_manageable_extensions()` aligns with actual validation logic.
- `is_view_allowed()` does not leak inaccessible content.
- Deletion removes file and content record, and any plugin-side metadata.
- PHPUnit covers both permitted and denied actions.
