# Moodle JavaScript Standards for 5.x+

This document provides guidelines for JavaScript development in Moodle 5.x and later. Reference this when writing, refactoring, or reviewing JavaScript code.

## Quick Do's and Don'ts

**DO:**
- Use vanilla JavaScript + Moodle helper libraries
- Write ES2015+ modules transpiled to CommonJS via RequireJS
- Use native Promises with `.then()/.catch()`
- Use `document.addEventListener()` for DOM interactions
- Store CSS selectors in reusable objects
- Use `core/str`, `core/prefetch`, `core/dropzone` helpers
- Use Grunt for compilation and ESLint for code quality

**DON'T:**
- Use jQuery (deprecated since Moodle 5.x)
- Use YUI (deprecated - removed from core)
- Use heavy frameworks (React, Angular, Vue) in core code
- Use jQuery promise methods: `.done()`, `.fail()`, `.always()`
- Put complex logic in templates (use AMD modules instead)
- Use class selectors to query DOM elements

---

## Module Structure

**Format:**
```
[component_name]/[optional/sub/namespace/][modulename]
```

**Patterns:**
- Create a main entry-point module exporting an `init()` function
- Organize related functionality into sub-modules using `local/` subdirectories
- Separate concerns: selectors in dedicated modules, web service calls in repository modules

**Example:**
```
mod_forum/local/repository/posts
mod_forum/local/selectors
mod_forum/posts_handler (main module with init())
```

---

## Key Helper Libraries

| Library | Purpose | Usage |
|---------|---------|-------|
| `core/str` | Retrieve and cache language strings | `getString('key', 'component')` |
| `core/prefetch` | Optimize performance (Moodle 3.9+) | Prefetch data before needed |
| `core/dropzone` | Accessible file upload zones (Moodle 4.4+) | WCAG-compliant uploads |
| AMD modules | All browser-executed code | Use `define()` for ES2015+ modules |

---

## Promises & Async Patterns

**Use native Promises (Moodle 4.3+):**
```javascript
// ✅ CORRECT
getString('key', 'component')
  .then(str => console.log(str))
  .catch(err => console.error(err));
```

**Never use jQuery promise methods:**
```javascript
// ❌ WRONG - These don't exist in native Promises
getString('key', 'component')
  .done(str => {})    // ERROR
  .fail(err => {})    // ERROR
  .always(() => {});  // ERROR
```

**Always return promises from promise-returning functions.**

---

## Data Passing & DOM Integration

**Use data attributes for complex data:**
```html
<!-- Prefer data attributes over function parameters -->
<button data-user-id="123" data-action="delete">Delete</button>
```

**Use `{{uniqid}}` Mustache tags for unique identification:**
```
id="element-{{uniqid}}"
```

**Use web services for complex data structures** instead of inline parameters.

---

## Template & Code Inclusion

**DO:**
- Embed simple JavaScript in templates using `{{#js}}` tags (for initialization only)
- Use `$PAGE->requires->js_call_amd()` in PHP for procedurally-generated content
- Keep all complex logic in AMD modules

**DON'T:**
- Put extensive logic in templates (not transpiled or minified)
- Use inline script tags for core functionality

---

## Development Workflow

**Compilation & Watching:**
```bash
# Watch for changes and incrementally build
grunt watch
```

**Code Quality:**
- Use ESLint for JavaScript quality checks
- Moodle uses common industry tools for consistency

---

## Learning Resources

For comprehensive JavaScript guidelines, patterns, and advanced topics:
**https://moodledev.io/docs/5.0/guides/javascript**

Consult this page if you encounter:
- Complex module organization questions
- Advanced AMD pattern usage
- Web service integration details
- Performance optimization techniques
- Specific helper library documentation

---

## Migration from Deprecated Technologies

If updating legacy code:

**From jQuery → Vanilla JavaScript:**
- Replace `jQuery.ajax()` with `fetch()` or Moodle's `core/ajax`
- Replace `$(selector)` with `document.querySelector()`
- Replace jQuery events with `addEventListener()`

**From YUI → AMD Modules:**
- Migrate to ES2015+ module format
- Use RequireJS for module loading
- Leverage Moodle's core helper libraries

See https://moodledev.io/docs/5.0/guides/javascript for migration examples.

---

*This reference provides condensed JavaScript standards for Moodle 5.x development. For detailed patterns, advanced techniques, and comprehensive examples, visit the full JavaScript guidelines at the URL above.*
