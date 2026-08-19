# Local Plugin Contract

Use [`assets/fixtures/local_momopda`](../assets/fixtures/local_momopda/) as the smallest installable local plugin.

## Required Shape

A no-op local plugin requires only `version.php` and `lang/en/local_name.php`. There is no required base class or callback. Add settings, pages, hooks, observers, tasks, external functions, capabilities, and tables only for actual behavior.

## Contract Pitfalls

- Do not use Moodle's old `local/readme.txt` examples as authority for modern events or hooks.
- Do not confuse site-level `local/defaults.php` or `local/preupgrade.php` with files inside a normal plugin.
- Administrative pages still require authentication, context, and capability enforcement.
- On Moodle 5.1+, the physical path is `public/local/name`.

Core references: plugin API documentation and `lib/classes/plugininfo/local.php`; core intentionally ships no normal `local_*` implementation.
