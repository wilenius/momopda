# HTML Writer Best Practices for Moodle

## Problem: Error-prone html_writer usage

Many developers use html_writer with manual start_tag/end_tag pairs, leading to:
- Mismatched tags (hard to debug)
- Mixed business logic with HTML generation
- Difficult maintenance
- Poor readability

## Recommended Patterns

### 1. Use html_table for tabular data

**❌ BAD: Manual table building**
```php
echo html_writer::start_tag('div', array('class' => 'course-overrides-container'));
foreach ($items as $item) {
    echo html_writer::start_tag('div', array('class' => 'item'));
    echo html_writer::tag('h3', $item->name);
    echo html_writer::end_tag('div');
}
echo html_writer::end_tag('div');
```

**✅ GOOD: Use html_table**
```php
$table = new html_table();
$table->head = array('Name', 'Description', 'Actions');
$table->align = array('left', 'left', 'center');
$table->data = array();

foreach ($items as $item) {
    $table->data[] = array(
        format_string($item->name),
        $item->description,
        $this->build_actions($item)
    );
}

echo html_writer::table($table);
```

### 2. Use templates for complex structures

**❌ BAD: Complex HTML in PHP**
```php
echo html_writer::start_tag('div', array('class' => 'quiz-override-section card mt-3'));
echo html_writer::start_tag('div', array('class' => 'card-header'));
echo html_writer::tag('h3', format_string($quiz->name), array('class' => 'mb-0'));
echo html_writer::end_tag('div');
echo html_writer::start_tag('div', array('class' => 'card-body'));
// ... more complex structure
echo html_writer::end_tag('div');
echo html_writer::end_tag('div');
```

**✅ GOOD: Use templates**
```php
$templatecontext = array(
    'quiz' => $quiz,
    'overrides' => $this->format_overrides($overrides),
    'actions' => $this->build_actions($quiz)
);
echo $OUTPUT->render_from_template('local_myplugin/quiz_card', $templatecontext);
```

### 3. Single-call methods over start/end pairs

**❌ BAD: Start/end tag pairs**
```php
echo html_writer::start_tag('div', array('class' => 'alert alert-info'));
echo get_string('message', 'local_myplugin');
echo html_writer::end_tag('div');
```

**✅ GOOD: Single html_writer calls**
```php
echo html_writer::div(
    get_string('message', 'local_myplugin'),
    'alert alert-info'
);
```

### 4. Extract methods for reusable components

**❌ BAD: Inline HTML generation**
```php
foreach ($items as $item) {
    echo html_writer::start_tag('li', array('class' => 'list-group-item'));
    echo html_writer::tag('span', $item->displayname);
    // ... complex logic mixed with HTML
    echo html_writer::end_tag('li');
}
```

**✅ GOOD: Extract methods**
```php
foreach ($items as $item) {
    echo $this->render_item($item);
}

private function render_item($item) {
    return html_writer::tag('li',
        $this->build_item_content($item),
        array('class' => 'list-group-item')
    );
}

private function build_item_content($item) {
    // Business logic separated from HTML structure
    return html_writer::tag('span', $item->displayname);
}
```

### 5. Use $OUTPUT methods when available

**❌ BAD: Manual notification HTML**
```php
echo html_writer::div(
    html_writer::tag('i', '', array('class' => 'fa fa-warning')) . ' ' . $message,
    'alert alert-warning'
);
```

**✅ GOOD: Use $OUTPUT methods**
```php
echo $OUTPUT->notification($message, \core\output\notification::NOTIFY_WARNING);
```

## Template Structure Example

**Template file (mustache):**
```mustache
<div class="course-overrides-container">
    {{#quizzes}}
    <div class="quiz-override-section card mt-3">
        <div class="card-header">
            <h3 class="mb-0">{{name}}</h3>
        </div>
        <div class="card-body">
            {{#hasoverrides}}
            <ul class="list-group list-group-flush">
                {{#overrides}}
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <span>{{displayname}}</span>
                    <small class="text-muted">{{info}}</small>
                    {{{actions}}}
                </li>
                {{/overrides}}
            </ul>
            {{/hasoverrides}}
            {{^hasoverrides}}
            <p class="text-muted">{{#str}}nooverrides, local_myplugin{{/str}}</p>
            {{/hasoverrides}}
        </div>
    </div>
    {{/quizzes}}
</div>
```

**PHP context preparation:**
```php
$templatecontext = array(
    'quizzes' => array_map(function($quiz) {
        return $this->prepare_quiz_context($quiz);
    }, $quizzes)
);

echo $OUTPUT->render_from_template('local_myplugin/quiz_list', $templatecontext);
```

## Key Benefits

1. **Maintainability**: Templates separate structure from logic
2. **Reusability**: Components can be reused across pages
3. **Testability**: Business logic is separate from HTML generation
4. **Accessibility**: Templates can be reviewed for WCAG compliance
5. **Performance**: Templates are cached and optimized
6. **Consistency**: UI components follow the same patterns

## When to Use Each Approach

- **Templates**: Complex UI structures, reusable components, card layouts
- **html_table**: Any tabular data presentation
- **Single html_writer calls**: Simple wrappers, basic formatting
- **$OUTPUT methods**: Notifications, standard UI elements, icons