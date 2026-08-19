# Text Filter Contract

Use [`assets/fixtures/filter_momopda`](../assets/fixtures/filter_momopda/) as the modern filter contract. It follows core `filter_emailprotect` discovery without copying its regular expressions.

## Required Shape

Provide `version.php`, `lang/en/filter_name.php` with `filtername`, and `classes/text_filter.php`. The namespaced class `filter_name\text_filter` extends `core_filters\text_filter` and implements `filter($text, array $options = [])`.

This contract is valid for Moodle 4.5 and supported 5.x branches. The old root `filter.php`, global `filter_name` class, and `moodle_text_filter` alias are deprecated compatibility paths.

## Contract Pitfalls

- Return early before expensive parsing when the marker is absent.
- Do not run uncached database queries for every text fragment.
- Preserve existing HTML structure and escape inserted user content.
- Use Moodle filtering helpers for autolinking rather than global string replacement.
- On Moodle 5.1+, the physical path is `public/filter/name`.

Core references: `filter/emailprotect`, `filter/classes/filter_manager.php`, `filter/classes/text_filter.php`.
