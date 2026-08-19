# Question Bank Plugin Contract

Use [`assets/fixtures/qbank_momopda`](../assets/fixtures/qbank_momopda/) as a minimal custom-column plugin. It follows core `qbank_viewcreator` and avoids version-sensitive bulk-action behavior.

## Required Shape

Provide `version.php`, an English language file, and `classes/plugin_feature.php`. The namespaced entry class extends `core_question\local\bank\plugin_features_base`. A column extends `column_base`, receives the question-bank view in its constructor, and implements title, name, and content methods.

Declare required fields and joins instead of assuming arbitrary row properties.

## Version-Sensitive Bulk Actions

Moodle 4.5 allowed bulk actions without a question-bank view constructor. Later 5.x code makes the action a view component. Verify `plugin_features_base` and `bulk_action_base` in the exact target branch before implementing registration or constructors.

Bulk-action endpoints must validate sesskey, context, the advertised capability rule, and per-question capabilities. Do not rely on checkbox visibility as authorization.

## Contract Pitfalls

- Use Frankenstyle capabilities such as `qbank/name:use`.
- Do not assume question banks always use course context; newer shared banks are activity-backed.
- Use the question type save API instead of directly inserting coordinated question-bank records.
- Normalize blank question idnumbers according to core behavior; do not invent synthetic IDs.

Core references: `question/bank/viewcreator`, `question/bank/bulkmove`, `question/classes/local/bank`.
