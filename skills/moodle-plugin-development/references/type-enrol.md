# Enrolment Plugin Contract

Use [`assets/fixtures/enrol_momopda`](../assets/fixtures/enrol_momopda/) as the minimal recognized enrolment method. It intentionally exposes no user interface or synchronization behavior.

## Required Shape

Provide `version.php`, an English language file, `lib.php`, and global class `enrol_name_plugin` extending `enrol_plugin`. Current Moodle can load that legacy-named class from `classes/plugin.php`, while enrolment instance discovery still requires `lib.php` to exist.

The inherited API supports instances and user enrolment, but an inert subclass does not automatically expose an add-instance interface. Add editing methods and matching capabilities only when the plugin supports management through the course UI.

## Contract Pitfalls

- Do not derive a generic plugin from core category, guest, fee, or manual behavior; each has subsystem-specific assumptions.
- Re-check status, dates, roles, and capabilities before changing enrolments.
- Return an empty validation error array when implementing the standard editing UI.
- On Moodle 5.1+, the physical path is `public/enrol/name`.

Core references: `enrol/fee/classes/plugin.php`, `lib/enrollib.php`.
