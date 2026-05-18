---
name: moodle-contenttype
description: Development guide for Moodle content bank type plugins (contenttype_*). Use when creating reusable content types for the content bank with upload, view, edit, download, and copy support.
compatibility: Requires Moodle 5.x development environment
metadata:
  author: sarjona
  version: "1.0.0"
---

# Moodle content bank type development

Content bank type plugins (contenttype_*) let teachers and designers upload and reuse specific content formats across Moodle contexts (system, category, and course).

## Environment Setup

This skill expects:
- Plugin code in `public/contentbank/contenttype/yourtype`
- Moodle source in the current workspace
- A Moodle test site with Content bank enabled

## Recommended Skills

For coding standards, security, and CI checks, also activate the `moodle-core` skill.

## Plugin Structure

```
contentbank/contenttype/yourtype/
|- classes/
|  |- contenttype.php          # Type behavior (features, extensions, view/edit/copy rules)
|  |- content.php              # Content instance behavior (file import, view permission)
|  |- privacy/
|  |  |- provider.php          # Usually null provider
|  |- form/                    # Optional, for custom editors
|  |  |- editor.php
|- db/
|  |- access.php               # Plugin capabilities
|- lang/en/
|  |- contenttype_yourtype.php # Plugin strings
|- tests/
|  |- *_test.php               # PHPUnit tests
|- pix/                        # Optional icons
|- version.php                 # Plugin metadata
```

## Core Implementation Flow

1. Define plugin metadata in `version.php`.
2. Implement `\\contenttype_yourtype\\contenttype` extending `\\core_contentbank\\contenttype`.
3. Implement `\\contenttype_yourtype\\content` extending `\\core_contentbank\\content`.
4. Add capabilities in `db/access.php` and strings in `lang/en/contenttype_yourtype.php`.
5. Add PHPUnit tests for create/upload/view/edit/delete/copy behavior.
6. Add Behat coverage for UI workflows in Content bank.

## Minimal `contenttype` Contract

In `classes/contenttype.php` implement at least:
- `get_implemented_features()` returning supported features.
- `get_manageable_extensions()` returning supported file extensions.

Typical supported features:
- `self::CAN_UPLOAD`
- `self::CAN_EDIT`
- `self::CAN_DOWNLOAD`
- `self::CAN_COPY`

Also commonly implemented:
- `get_contenttype_types()` for dropdown type variants.
- `get_icon()` for content-specific icon rendering.
- `get_view_content()` to render the visualizer output.
- `delete_content()` if plugin-specific cleanup is required before `parent::delete_content()`.

## Minimal `content` Contract

In `classes/content.php` you typically customize:
- `is_view_allowed()` to enforce type-specific visibility rules.
- `import_file(\\stored_file $file)` to validate and normalize uploaded files before calling parent logic.

Use file API conventions from core Content bank:
- Component: `contentbank`
- File area: `public`
- Item id: content id

## Capabilities and Access

Define plugin capabilities in `db/access.php` like:
- `contenttype/yourtype:access`
- `contenttype/yourtype:upload`
- Optional type-specific capabilities (for example, editor usage)

Use context-aware checks in type/content methods and avoid system-level assumptions when the content lives in course/category contexts.

## Editor Integration (Optional)

If your type has an authoring UI:
- Add `classes/form/editor.php` extending `\\core_contentbank\\form\\edit_content`.
- Support both create and edit flow.
- Save custom fields through `\\core_contentbank\\customfield\\content_handler` when needed.

## Testing Strategy

### PHPUnit (required)

Cover these scenarios:
- Feature availability and capability checks per role/context.
- Upload/import validation success and failure paths.
- View permission behavior (`is_view_allowed`) for different users.
- Deletion cleanup (DB records + file removal + plugin-specific side effects).
- Download/copy behavior if supported.

Use content bank generators where possible:
- `core_contentbank` generator for creating test content quickly.

### Behat (required)

Add scenarios for:
- Content creation/upload from Content bank UI.
- Access restrictions for teachers/students/admins.
- Edit/copy/download controls visibility.
- Context navigation (system/category/course).

## Quality Checklist

Before submitting:
- `phpcs --standard=moodle-extra` passes for plugin files.
- PHPUnit tests pass.
- No direct superglobal access (`$_GET`, `$_POST`) in plugin logic.
- All user-facing strings are in language files.
- Capability checks are context-specific and explicit.

## Common Pitfalls

- Declaring extensions but not enabling `CAN_UPLOAD`.
- Forgetting to clean plugin-side data in overridden `delete_content()`.
- Returning content objects without validating ownership or context permissions.
- Missing language strings for new capabilities.
- Assuming one context level only (Content bank supports multiple context scopes).

## Reference Implementations

Use these implementations as concrete guides:
- Core H5P content type: `public/contentbank/contenttype/h5p/`
- Content bank base APIs: `public/contentbank/classes/contenttype.php`, `public/contentbank/classes/content.php`

External examples:
- https://github.com/ferranrecio/moodle-contenttype_html
- https://github.com/moodle/moodle/tree/main/public/contentbank/contenttype/h5p

Official docs:
- https://docs.moodle.org/dev/Content_bank_content_types

For deeper implementation patterns and anti-patterns, see [Content Bank Type Patterns](references/patterns.md).
