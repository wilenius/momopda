# Site Report Contract

Use [`assets/fixtures/report_momopda`](../assets/fixtures/report_momopda/) as a minimal administration report. It follows the page registration shape of core `report_status` without using core check-table internals.

## Required Shape

Provide `version.php` and an English language file. A usable administration report normally adds `settings.php`, `index.php`, and a view capability in `db/access.php`.

Register an `admin_externalpage`, then call `admin_externalpage_setup()` in the page before output. Use Moodle output APIs or a template, language strings, and portable DML.

The `report_*` plugin type does not imply inheritance from Moodle Report Builder. Use Report Builder only when its datasource and report contracts match the requirement.

## Contract Pitfalls

- Do not copy MySQL-only date or aggregation expressions.
- Paginate large result sets and avoid loading all rows before table rendering.
- Enforce row-level access in addition to page-level capability checks.
- On Moodle 5.1+, the physical path is `public/report/name`.

Core references: `report/status`, `lib/classes/report_helper.php`.
