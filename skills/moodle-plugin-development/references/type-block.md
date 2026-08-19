# Block Contract

Use [`assets/fixtures/block_momopda`](../assets/fixtures/block_momopda/) as the minimal display block. It follows the small contract demonstrated by core `block_course_summary` without depending on course summaries.

## Required Shape

Provide `version.php`, `block_name.php`, and an English language file. The global class `block_name` extends `block_base`. Its `init()` method sets a title and `get_content()` returns an object with `text` and `footer`.

Define `block/name:addinstance` when users can add it. Define `block/name:myaddinstance` only when Dashboard placement is supported. Add configuration, persistence, privacy, and backup only when needed.

## Contract Pitfalls

- Cache `$this->content` within the request.
- Format or escape dynamic content before assigning it to `text`.
- Do not copy core blocks that depend on navigation or completion internals.
- On Moodle 5.1+, the physical path is `public/blocks/name`.

Core references: `blocks/course_summary`, `blocks/moodleblock.class.php`.
