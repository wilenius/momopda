# Question Bank Plugin Contract

Use [`assets/fixtures/qbank_momopda`](../assets/fixtures/qbank_momopda/) as a minimal custom-column plugin. It follows core question-bank components and intentionally avoids adding a version-sensitive bulk action.

## Required Shape

Provide `version.php`, an English language file, and `classes/plugin_feature.php`. The namespaced entry class extends `core_question\local\bank\plugin_features_base`. A column extends `column_base`, receives the question-bank view in its constructor, and implements title, name, and content methods.

Declare required fields and joins instead of assuming arbitrary row properties.

## Moodle 5.x Bulk Actions

Verify `plugin_features_base` and `bulk_action_base` in the exact target branch before implementing registration or constructors. In Moodle 5.2, a bulk action extends `bulk_action_base`, receives the current `view` through the inherited constructor, and is returned from `plugin_feature::get_bulk_actions(view $qbank)`. It supplies a unique form key, a local endpoint URL, a title, and an array of capabilities.

The question-bank form posts a sesskey and checkboxes named `q{questionid}`. Core appends the current `cmid`, bank parameters, and `returnurl` to the action URL. Treat all of these as request input. The capabilities advertised by the action control menu visibility with any-of semantics; the endpoint must independently require the intended action capability in the activity-backed bank context.

Resolve the bank from `cmid`, require login for that course module, and use its module context. Do not derive authorization from a course ID or from an arbitrary question ID. Confirm that every selected question belongs to the originating bank and call `question_require_capability_on($question, 'edit')` for each item immediately before execution. Validate the whole selection before changing any record, and use a delegated transaction for all-or-nothing mutations.

For a confirmed question-version status change, use the status values defined by `question_version_status`. Match core's update side effects: invalidate each edited question with `question_bank::notify_question_edited()` and trigger the corresponding question-updated event in the question's context.

Use a two-stage POST flow. The initial valid submission displays a confirmation without changing state; the confirmation submission validates the request and sesskey again. Build both success and cancellation destinations from a `PARAM_LOCALURL` input only after rejecting protocol-relative values, and replace missing or invalid input with a server-built `moodle_url` for the originating bank.

## Contract Pitfalls

- Use Frankenstyle capabilities such as `qbank/name:use`.
- Do not assume question banks always use course context; newer shared banks are activity-backed.
- For Moodle's `public/` layout, install web-facing plugin files below `public/question/bank/name`, but keep URLs rooted at `/question/bank/name`; never add `/public` to a Moodle URL. Non-web CLI entry points such as `admin/cli/install_database.php` remain at the checkout root.
- Use the question type save API instead of directly inserting coordinated question-bank records.
- Normalize blank question idnumbers according to core behavior; do not invent synthetic IDs.

Core references: `question/edit.php`, `question/editlib.php`, `question/classes/local/bank`, `question/templates/bulk_actions_ui.mustache`, `question/bank/bulkmove`, `question/bank/deletequestion/delete.php`, and `question/bank/editquestion/classes/external/update_question_version_status.php`.
