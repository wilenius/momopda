# Frontend Contracts

## Rendering

Prefer output classes and Mustache templates for non-trivial UI. Use Moodle's component library and semantic HTML. Keep user-visible strings in language packs and make controls keyboard accessible.

## JavaScript

Write AMD source modules under `amd/src` using the APIs available in the target Moodle version. Ship generated `amd/build` files in distributable plugins. Do not hand-edit generated files except in a fixture explicitly testing the loader contract.

Use Moodle modules for strings, AJAX, notifications, modals, templates, and pending-state tracking. Do not introduce jQuery into new code. Await asynchronous data before invoking APIs that require synchronous registration, including TinyMCE's `PluginManager.add()` callback.

## Styling

Use logical-direction Bootstrap utilities and the classes supported by the target Moodle branch. Avoid selectors coupled to internal DOM structure. Test both default themes and narrow viewports when layout behavior changes.

## Accessibility

- Preserve heading order and landmarks.
- Give controls accessible names and visible focus.
- Associate labels, errors, and help text with fields.
- Do not use color as the only state indicator.
- Restore focus after modal interactions.
- Test keyboard operation for custom widgets.
