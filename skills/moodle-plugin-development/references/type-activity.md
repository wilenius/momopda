# Activity Module Contract

Use [`assets/fixtures/mod_momopda`](../assets/fixtures/mod_momopda/) as the minimal conventional activity contract. It is derived from the structure of core `mod_page`, while omitting files, grading, completion rules, events, backup, and other optional subsystems.

## Required Shape

A conventional activity needs `version.php`, an English language file, `db/install.xml`, `db/access.php`, `lib.php`, `mod_form.php`, and normally `view.php`.

Moodle calls component-prefixed functions in `lib.php`, including add, update, delete, and feature-support callbacks. Add returns the new instance ID. Update receives the ID in `$data->instance`. Delete removes dependent data before the main row.

The form extends `moodleform_mod` and includes the standard course-module elements. A view page resolves the course module and instance, requires course login and the view capability, sets the page URL/context, and formats stored content.

## Contract Pitfalls

- Do not claim backup support without backup and restore classes.
- Do not claim custom completion rules without implementing and testing them.
- Keep the main table name equal to the activity name.
- Add gradebook, calendar, files, privacy, and events only when behavior requires them.
- On Moodle 5.1+, the physical path is `public/mod/name`; the URL remains `/mod/name`.

Core references: `mod/page`, `mod/label`, `course/moodleform_mod.php`.
