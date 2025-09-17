# Local Plugin Patterns and Antipatterns

This document outlines proven patterns and common antipatterns when developing Moodle local plugins, based on real-world implementations and best practices.

## ✅ Proven Patterns

### 1. Navigation Integration Pattern

**Pattern**: Integrate seamlessly with Moodle's existing navigation structure

```php
function local_yourplugin_extend_settings_navigation($settingsnav, $context) {
    global $PAGE;

    // ✅ Check context level and capabilities
    if ($context->contextlevel == CONTEXT_COURSE && has_capability('mod/quiz:manageoverrides', $context)) {
        if ($settingnode = $settingsnav->find('courseadmin', navigation_node::TYPE_COURSE)) {
            $str = get_string('pluginname', 'local_yourplugin');
            $url = new moodle_url('/local/yourplugin/index.php', array('courseid' => $PAGE->course->id));
            $node = navigation_node::create(
                $str,
                $url,
                navigation_node::NODETYPE_LEAF,
                'local_yourplugin',
                'local_yourplugin',
                new pix_icon('i/settings', $str)
            );

            // ✅ Highlight active page
            if ($PAGE->url->compare($url, URL_MATCH_BASE)) {
                $node->make_active();
            }
            $settingnode->add_node($node);
        }
    }
}
```

**Why this works**:
- Respects existing permissions
- Integrates naturally with Moodle UI
- Provides clear visual feedback

### 2. Form Action URL Pattern

**Pattern**: Explicitly set form action URLs to preserve parameters

```php
// ✅ Correct: Set explicit form action URL
$formurl = new moodle_url('/local/yourplugin/action.php', array('courseid' => $courseid));
$form = new \local_yourplugin\form\example_form($formurl, array(
    'courseid' => $courseid,
    'context' => $context
));

// ✅ Also include as hidden field for extra safety
class example_form extends moodleform {
    protected function definition() {
        $mform = $this->_form;
        $courseid = $this->_customdata['courseid'];

        // Form fields...

        $mform->addElement('hidden', 'courseid', $courseid);
        $mform->setType('courseid', PARAM_INT);
    }
}
```

**Why this works**:
- Prevents "missing parameter" errors
- Maintains state across form submissions
- Provides redundant parameter passing

### 3. Context Object Preparation Pattern

**Pattern**: Prepare objects with required properties for external APIs

```php
// ✅ Correct: Prepare quiz object for override_manager
foreach ($quizzes as $quiz) {
    $cm = get_coursemodule_from_instance('quiz', $quiz->id, $courseid);
    $quizcontext = context_module::instance($cm->id);

    // ✅ Add required property for API compatibility
    $quiz->cmid = $cm->id;

    $manager = new \mod_quiz\local\override_manager($quiz, $quizcontext);
    // Now the API call will work
}
```

**Why this works**:
- Satisfies API validation requirements
- Maintains object integrity
- Prevents context mismatch errors

### 4. Bulk Operation with Detailed Feedback Pattern

**Pattern**: Provide comprehensive feedback for bulk operations

```php
// ✅ Track multiple operation types
$successcount = 0;
$updatedcount = 0;
$errors = array();
$skipped = array();

foreach ($items as $item) {
    // Pre-validation checks
    if ($item->matches_default()) {
        $skipped[] = format_string($item->name) . ': Matches default value';
        continue;
    }

    if ($existing && !$update_existing) {
        $skipped[] = format_string($item->name) . ': Already exists (use update option)';
        continue;
    }

    try {
        if ($existing) {
            // Update existing
            $updatedcount++;
        } else {
            // Create new
            $successcount++;
        }
    } catch (Exception $e) {
        $errors[] = format_string($item->name) . ': ' . $e->getMessage();
    }
}

// ✅ Comprehensive feedback message
$message = '';
if ($successcount > 0) {
    $message .= get_string('created', 'local_yourplugin', $successcount);
}
if ($updatedcount > 0) {
    if ($message) $message .= ' ';
    $message .= get_string('updated', 'local_yourplugin', $updatedcount);
}
if (!empty($skipped)) {
    $message .= '<br>Skipped: ' . implode('<br>', $skipped);
}
```

**Why this works**:
- Users understand what happened to each item
- Distinguishes between different operation types
- Helps troubleshoot issues

### 5. Progressive Enhancement Pattern

**Pattern**: Start with basic functionality and add features incrementally

```php
// ✅ Start with simple checkbox
$mform->addElement('checkbox', 'updateexisting', get_string('updateexisting'));
$mform->setType('updateexisting', PARAM_BOOL);

// ✅ Add help button for clarity
$mform->addHelpButton('updateexisting', 'updateexisting', 'local_yourplugin');

// ✅ Add validation in form validation method
public function validation($data, $files) {
    $errors = parent::validation($data, $files);
    // Add specific validation rules
    return $errors;
}
```

**Why this works**:
- Easier to debug and test
- Can iterate based on user feedback
- Reduces complexity during development

### 6. Defensive Permission Checking Pattern

**Pattern**: Check permissions at multiple levels

```php
// ✅ Check at plugin level
require_capability('mod/quiz:manageoverrides', $context);

foreach ($items as $item) {
    $itemcontext = context_module::instance($item->cmid);

    // ✅ Check at item level too
    if (!has_capability('mod/quiz:manageoverrides', $itemcontext)) {
        $skipped[] = format_string($item->name) . ': No permission';
        continue;
    }

    // Process item
}
```

**Why this works**:
- Prevents unauthorized access
- Handles complex permission scenarios
- Provides clear feedback about access issues

## ❌ Common Antipatterns

### 1. Missing Parameter Antipattern

**Antipattern**: Creating forms without proper parameter handling

```php
// ❌ Wrong: No form action URL
$form = new \local_yourplugin\form\example_form(null, $customdata);

// ❌ Wrong: Missing hidden fields
class example_form extends moodleform {
    protected function definition() {
        // Form fields but no hidden courseid
    }
}
```

**Problems**:
- Results in "missing parameter" errors
- Breaks form submission workflow
- Frustrates users

**Solution**: Use the Form Action URL Pattern above

### 2. Context Mismatch Antipattern

**Antipattern**: Using objects with external APIs without proper preparation

```php
// ❌ Wrong: Using raw database object
$quiz = $DB->get_record('quiz', array('id' => $quizid));
$cm = get_coursemodule_from_instance('quiz', $quiz->id, $courseid);
$context = context_module::instance($cm->id);

// ❌ This will fail with "context does not match quiz object"
$manager = new \mod_quiz\local\override_manager($quiz, $context);
```

**Problems**:
- API validation failures
- Cryptic error messages
- Plugin crashes

**Solution**: Use the Context Object Preparation Pattern above

### 3. Silent Failure Antipattern

**Antipattern**: Operations fail without clear feedback

```php
// ❌ Wrong: No feedback about what happened
$successcount = 0;
foreach ($items as $item) {
    try {
        process_item($item);
        $successcount++;
    } catch (Exception $e) {
        // Silent failure - user doesn't know what went wrong
    }
}

if ($successcount > 0) {
    redirect($returnurl, 'Some items processed');
} else {
    redirect($returnurl, 'Failed to process items');
}
```

**Problems**:
- Users don't know why operations failed
- Hard to troubleshoot issues
- Poor user experience

**Solution**: Use the Bulk Operation with Detailed Feedback Pattern above

### 4. Form Element Complexity Antipattern

**Antipattern**: Using complex form elements when simple ones work better

```php
// ❌ Wrong: Overcomplicating form elements
$mform->addElement('advcheckbox', 'updateexisting',
    get_string('updateexisting'),
    get_string('updateexistingdesc'),
    array('group' => 1),
    array(0, 1)
);
```

**Problems**:
- May not work consistently across browsers
- Harder to debug form submission issues
- Unnecessary complexity

**Solution**: Use simple, standard form elements

### 5. Hard-coded Navigation Antipattern

**Antipattern**: Adding navigation without checking context or permissions

```php
// ❌ Wrong: Always add navigation regardless of context
function local_yourplugin_extend_settings_navigation($settingsnav, $context) {
    // No permission check
    // No context validation
    $settingsnav->add_node($node); // Always add
}
```

**Problems**:
- Navigation appears where it shouldn't
- Security issues
- Confusing user experience

**Solution**: Use the Navigation Integration Pattern above

### 6. Database Direct Manipulation Antipattern

**Antipattern**: Bypassing Moodle APIs for database operations

```php
// ❌ Wrong: Direct database manipulation
$DB->insert_record('quiz_overrides', array(
    'quiz' => $quizid,
    'userid' => $userid,
    'timelimit' => $timelimit
));
```

**Problems**:
- Bypasses validation
- Misses event triggers
- Doesn't update caches
- Breaks integrations

**Solution**: Use existing APIs when available

### 7. Monolithic Form Processing Antipattern

**Antipattern**: Handling all logic in a single large method

```php
// ❌ Wrong: Everything in one place
if ($data = $form->get_data()) {
    // 100+ lines of processing logic
    // Multiple database operations
    // Complex validation
    // Business logic mixed with presentation
}
```

**Problems**:
- Hard to test
- Difficult to maintain
- Poor code organization

**Solution**: Break into smaller, focused methods

## 🎯 Architecture Patterns

### 1. Layered Architecture Pattern

**Pattern**: Separate concerns into distinct layers

```php
// ✅ Presentation Layer (index.php)
$form = new \local_yourplugin\form\example_form($formurl, $customdata);
if ($data = $form->get_data()) {
    $service = new \local_yourplugin\service\example_service();
    $result = $service->process_data($data);
    redirect($returnurl, $result->get_message());
}

// ✅ Service Layer (classes/service/example_service.php)
class example_service {
    public function process_data($data) {
        $processor = new \local_yourplugin\processor\example_processor();
        return $processor->bulk_process($data);
    }
}

// ✅ Business Logic Layer (classes/processor/example_processor.php)
class example_processor {
    public function bulk_process($data) {
        // Business logic here
    }
}
```

### 2. Factory Pattern for Context-Specific Operations

**Pattern**: Create objects based on context requirements

```php
// ✅ Factory for different operation types
class operation_factory {
    public static function create_processor($type, $context) {
        switch ($type) {
            case 'course':
                return new course_processor($context);
            case 'user':
                return new user_processor($context);
            default:
                throw new \coding_exception('Unknown processor type');
        }
    }
}
```

### 3. Strategy Pattern for Different Processing Modes

**Pattern**: Encapsulate different algorithms/approaches

```php
// ✅ Different strategies for different scenarios
interface processing_strategy {
    public function process($data);
}

class create_strategy implements processing_strategy {
    public function process($data) {
        // Create new items
    }
}

class update_strategy implements processing_strategy {
    public function process($data) {
        // Update existing items
    }
}
```

## 🔧 Debugging Patterns

### 1. Progressive Debugging Pattern

**Pattern**: Add temporary debugging to understand data flow

```php
// ✅ Temporary debugging
if ($existingoverride && empty($data->updateexisting)) {
    $skipped[] = format_string($quiz->name) . ': Override already exists. ' .
                'UpdateExisting value: ' . (isset($data->updateexisting) ? $data->updateexisting : 'not set');
    continue;
}
```

### 2. Error Context Pattern

**Pattern**: Provide rich error context

```php
// ✅ Rich error context
try {
    $manager->save_override($overridedata);
} catch (Exception $e) {
    $errors[] = format_string($quiz->name) . ' (ID: ' . $quiz->id . ', User: ' . $data->userid . '): ' . $e->getMessage();
}
```

## 📋 Testing Patterns

### 1. Manual Testing Checklist Pattern

```
✅ Plugin Installation
- [ ] Plugin installs without errors
- [ ] Version information is correct
- [ ] Database tables created (if any)

✅ Navigation
- [ ] Navigation appears in correct location
- [ ] Navigation respects permissions
- [ ] Active page highlighting works

✅ Form Functionality
- [ ] Form displays correctly
- [ ] Required field validation works
- [ ] Form submission preserves parameters
- [ ] Success/error messages appear

✅ Bulk Operations
- [ ] Creates new items correctly
- [ ] Updates existing items when requested
- [ ] Skips items appropriately
- [ ] Provides detailed feedback

✅ Permissions
- [ ] Respects capability requirements
- [ ] Works across different user roles
- [ ] Handles permission edge cases

✅ Error Handling
- [ ] Graceful error handling
- [ ] Meaningful error messages
- [ ] No silent failures
```

### 2. Data Validation Testing Pattern

```php
// ✅ Test edge cases
public function test_validation_edge_cases() {
    // Empty data
    // Invalid data types
    // Boundary values
    // Special characters
    // Very long strings
}
```

## 🎨 UI/UX Patterns

### 1. Consistent Feedback Pattern

**Pattern**: Use Moodle's standard notification system

```php
// ✅ Consistent with Moodle's notification patterns
redirect($returnurl, get_string('success_message', 'local_yourplugin'), 'success');
redirect($returnurl, get_string('error_message', 'local_yourplugin'), 'error');
redirect($returnurl, get_string('info_message', 'local_yourplugin'), 'info');
```

### 2. Progressive Disclosure Pattern

**Pattern**: Show additional options only when needed

```php
// ✅ Basic form first
$mform->addElement('text', 'basic_field', get_string('basic'));

// ✅ Advanced options in collapsible section
$mform->addElement('header', 'advanced', get_string('advanced_options'));
$mform->setExpanded('advanced', false);
$mform->addElement('checkbox', 'advanced_option', get_string('advanced'));
```

Remember: These patterns evolved from real-world plugin development experience. They solve common problems that developers encounter when creating local plugins. Use them as starting points and adapt them to your specific use case.