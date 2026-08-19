# Question Type Contract

Use [`assets/fixtures/qtype_momopda`](../assets/fixtures/qtype_momopda/) as a minimal information-item question type derived from core `qtype_description`.

## Required Shape

Question types retain global class contracts in `questiontype.php`, `question.php`, `renderer.php`, and `edit_name_form.php`. A usable plugin also needs `version.php`, language strings, and an icon.

Response question classes must implement the abstract data, completeness, validation, comparison, summary, and grading methods required by their chosen question base classes. Renderer controls must use names from the question attempt. Render question text through `format_questiontext()`.

Use `extra_question_fields()` and base save/load behavior for simple option tables. Custom persistence must cover save, update, load, initialization, deletion, and backup/restore implications.

## Contract Pitfalls

- Do not output raw `$question->questiontext`.
- Do not implement insert-only option saving.
- Do not assume every question type uses `question_answers`.
- Add backup and restore support before considering a data-owning type complete.

Core references: `question/type/description`, `question/type/truefalse`, `question/type/questiontypebase.php`.
