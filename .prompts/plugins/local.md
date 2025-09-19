# Moodle Local Plugin Development Guide

You are an expert Moodle developer specializing in local plugins for Moodle 5.x. This guide covers developing custom local plugins that extend Moodle's functionality with administrative tools, course enhancements, and system integrations.

## Local Plugin Architecture

Local plugins provide custom functionality that doesn't fit into standard plugin types. They can add administrative interfaces, course-level tools, system integrations, and extend existing Moodle features without modifying core code.

### Core Components

Every local plugin consists of these essential components:

1. **Library Functions** (`lib.php`) - Hook implementations and API functions
2. **Main Pages** (`index.php`, custom pages) - User interfaces and workflows
3. **Classes** (`classes/`) - Modern PHP classes, forms, and services
4. **Database Schema** (`db/install.xml`, `db/upgrade.php`) - Data structure definitions (if needed)
5. **Language Files** (`lang/en/local_*.php`) - Internationalization strings
6. **Version File** (`version.php`) - Plugin metadata and versioning
7. **Settings** (`settings.php`) - Admin configuration options (optional)

### File Structure

```
local/yourplugin/
├── lib.php                    # Hook implementations and core functions
├── index.php                  # Main plugin page (optional)
├── settings.php               # Admin settings page (optional)
├── classes/
│   ├── form/                 # Form classes
│   ├── external/             # Web service API classes
│   ├── event/                # Event classes for logging
│   ├── privacy/              # GDPR privacy provider
│   └── task/                 # Scheduled tasks
├── db/
│   ├── install.xml           # Database schema (if needed)
│   ├── upgrade.php           # Database upgrades
│   ├── access.php            # Capability definitions
│   ├── services.php          # Web service definitions
│   └── tasks.php             # Scheduled task definitions
├── lang/en/
│   └── local_yourplugin.php  # Language strings
├── pix/                      # Icons and images
├── templates/                # Mustache templates
├── tests/                    # Unit and integration tests
├── version.php               # Plugin version and dependencies
└── README.md                # Plugin documentation
```

## Essential Files

### version.php
```php
<?php
defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_yourplugin';
$plugin->release = '1.0';
$plugin->version = 2025091700;
$plugin->requires = 2022041900;
$plugin->maturity = MATURITY_STABLE;
```

### lib.php - Navigation and Hooks
```php
<?php
defined('MOODLE_INTERNAL') || die();

/**
 * Extend navigation - add to course admin menu
 */
function local_yourplugin_extend_settings_navigation($settingsnav, $context) {
    global $PAGE;

    if ($context->contextlevel == CONTEXT_COURSE && has_capability('your/capability', $context)) {
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

            if ($PAGE->url->compare($url, URL_MATCH_BASE)) {
                $node->make_active();
            }
            $settingnode->add_node($node);
        }
    }
}

/**
 * Extend navigation - add to site admin
 */
function local_yourplugin_extend_navigation_category($navigation, $category) {
    // Add to category navigation if needed
}
```

### Main Page (index.php)
```php
<?php
require(__DIR__ . '/../../config.php');

$courseid = optional_param('courseid', 0, PARAM_INT);

if ($courseid) {
    require_login($courseid);
    $course = $DB->get_record('course', array('id' => $courseid), '*', MUST_EXIST);
    $context = context_course::instance($courseid);
} else {
    require_login();
    $context = context_system::instance();
}

require_capability('your/capability', $context);

$PAGE->set_url('/local/yourplugin/index.php', array('courseid' => $courseid));
$PAGE->set_title(get_string('pluginname', 'local_yourplugin'));
$PAGE->set_heading($courseid ? $course->fullname : get_string('pluginname', 'local_yourplugin'));
$PAGE->set_context($context);
$PAGE->set_pagelayout($courseid ? 'incourse' : 'admin');

if ($courseid) {
    $PAGE->navbar->add(get_string('pluginname', 'local_yourplugin'));
}

echo $OUTPUT->header();
echo $OUTPUT->heading(get_string('pluginname', 'local_yourplugin'));

// Your plugin content here

echo $OUTPUT->footer();
```

### Language File (lang/en/local_yourplugin.php)
```php
<?php
defined('MOODLE_INTERNAL') || die();

$string['pluginname'] = 'Your Plugin Name';
$string['privacy:metadata'] = 'The plugin does not store any personal data.';
```

### Form Classes (classes/form/example_form.php)
```php
<?php
namespace local_yourplugin\form;

use moodleform;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/formslib.php');

class example_form extends moodleform {
    protected function definition() {
        $mform = $this->_form;
        $customdata = $this->_customdata;

        $mform->addElement('text', 'name', get_string('name'));
        $mform->setType('name', PARAM_TEXT);
        $mform->addRule('name', get_string('required'), 'required', null, 'client');

        $mform->addElement('hidden', 'courseid', $customdata['courseid']);
        $mform->setType('courseid', PARAM_INT);

        $this->add_action_buttons();
    }

    public function validation($data, $files) {
        $errors = parent::validation($data, $files);
        // Add custom validation
        return $errors;
    }
}
```

## Common Local Plugin Types

### 1. Course Administration Tools
- Course management utilities
- Bulk operations on course content
- Course reporting and analytics
- Student progress tracking

### 2. System Integration Plugins
- External system synchronization
- API integrations
- Data import/export tools
- Authentication extensions

### 3. Administrative Dashboards
- Custom admin interfaces
- System monitoring tools
- Configuration management
- User management utilities

### 4. Content Management Tools
- Bulk content operations
- Content migration utilities
- Content analysis tools
- Automated content generation

## Navigation Integration

### Course-Level Integration
```php
// Add to course administration menu
function local_yourplugin_extend_settings_navigation($settingsnav, $context) {
    if ($context->contextlevel == CONTEXT_COURSE) {
        // Add to course admin
    }
}
```

### Site-Level Integration
```php
// Add to site administration
if ($hassiteconfig) {
    $ADMIN->add('localplugins', new admin_externalpage(
        'local_yourplugin',
        get_string('pluginname', 'local_yourplugin'),
        new moodle_url('/local/yourplugin/admin.php')
    ));
}
```

### Category-Level Integration
```php
function local_yourplugin_extend_navigation_category($navigation, $category) {
    // Add to category navigation
}
```

## Security and Capabilities

### Define Capabilities (db/access.php)
```php
<?php
defined('MOODLE_INTERNAL') || die();

$capabilities = array(
    'local/yourplugin:manage' => array(
        'captype' => 'write',
        'contextlevel' => CONTEXT_COURSE,
        'archetypes' => array(
            'editingteacher' => CAP_ALLOW,
            'manager' => CAP_ALLOW
        )
    ),
);
```

### Check Capabilities
```php
require_capability('local/yourplugin:manage', $context);

if (has_capability('local/yourplugin:view', $context)) {
    // User can view
}
```

## Database Integration

### Working with Existing Tables
```php
// Get course data
$course = $DB->get_record('course', array('id' => $courseid), '*', MUST_EXIST);

// Get course modules
$modules = $DB->get_records('course_modules', array('course' => $courseid));

// Use existing APIs when possible
$quizzes = $DB->get_records('quiz', array('course' => $courseid));
foreach ($quizzes as $quiz) {
    $cm = get_coursemodule_from_instance('quiz', $quiz->id, $courseid);
    $context = context_module::instance($cm->id);
    // Work with existing data
}
```

### Custom Tables (if needed)
```xml
<!-- db/install.xml -->
<TABLES>
  <TABLE NAME="local_yourplugin_data" COMMENT="Plugin data table">
    <FIELDS>
      <FIELD NAME="id" TYPE="int" LENGTH="10" NOTNULL="true" SEQUENCE="true"/>
      <FIELD NAME="courseid" TYPE="int" LENGTH="10" NOTNULL="true"/>
      <FIELD NAME="userid" TYPE="int" LENGTH="10" NOTNULL="true"/>
      <FIELD NAME="data" TYPE="text" NOTNULL="false"/>
      <FIELD NAME="timecreated" TYPE="int" LENGTH="10" NOTNULL="true"/>
      <FIELD NAME="timemodified" TYPE="int" LENGTH="10" NOTNULL="true"/>
    </FIELDS>
    <KEYS>
      <KEY NAME="primary" TYPE="primary" FIELDS="id"/>
      <KEY NAME="courseid" TYPE="foreign" FIELDS="courseid" REFTABLE="course" REFFIELDS="id"/>
      <KEY NAME="userid" TYPE="foreign" FIELDS="userid" REFTABLE="user" REFFIELDS="id"/>
    </KEYS>
  </TABLE>
</TABLES>
```

## Integration with Existing Moodle Systems

### Working with Course Modules
```php
// Get course module
$cm = get_coursemodule_from_instance('quiz', $quizid, $courseid, false, MUST_EXIST);
$context = context_module::instance($cm->id);

// Check permissions
require_capability('mod/quiz:manageoverrides', $context);

// Work with module-specific APIs
$quiz->cmid = $cm->id; // Some APIs require this
$manager = new \mod_quiz\local\override_manager($quiz, $context);
```

### Using Moodle Forms
```php
// In your page
$form = new \local_yourplugin\form\example_form(null, array(
    'courseid' => $courseid,
    'context' => $context
));

if ($form->is_cancelled()) {
    redirect($returnurl);
} else if ($data = $form->get_data()) {
    // Process form data
    redirect($returnurl, get_string('success', 'local_yourplugin'));
}

$form->display();
```

## Best Practices

### 1. Use Existing APIs
- Leverage Moodle's existing functionality
- Don't reinvent existing features
- Use standard Moodle classes and methods

### 2. Follow Security Practices
- Always check capabilities
- Validate and sanitize input
- Use required_param() and optional_param()
- Implement proper context checking

### 3. Internationalization
- Externalize all strings
- Use get_string() for all user-facing text
- Support multiple languages

### 4. Error Handling
- Provide meaningful error messages
- Use Moodle's notification system
- Log errors appropriately

### 5. User Experience
- Follow Moodle's UI patterns
- Use consistent navigation
- Provide clear feedback
- Support accessibility

### 6. HTML Generation Best Practices
- **Use templates for complex structures** - Separate HTML from PHP logic
- **Use html_table for tabular data** - Don't manually build table HTML
- **Avoid start_tag/end_tag pairs** - Use single html_writer calls when possible
- **Extract methods for reusable components** - Keep HTML generation DRY
- **Use $OUTPUT methods** - Leverage Moodle's built-in UI components

See `.prompts/patterns/html_writer_best_practices.md` for detailed examples.

## Testing Local Plugins

### Unit Testing
```php
<?php
namespace local_yourplugin;

defined('MOODLE_INTERNAL') || die();

class example_test extends \advanced_testcase {
    public function test_basic_functionality() {
        $this->resetAfterTest(true);

        $course = $this->getDataGenerator()->create_course();
        $user = $this->getDataGenerator()->create_user();

        // Test your functionality
        $this->assertTrue(true);
    }
}
```

### Manual Testing Checklist
- [ ] Plugin installs correctly
- [ ] Navigation appears in correct locations
- [ ] Capabilities work as expected
- [ ] Forms validate properly
- [ ] Database operations work
- [ ] Error handling functions
- [ ] Works across different user roles
- [ ] Respects Moodle permissions

## Common Integration Points

### 1. Course Administration
- Add tools to course settings menu
- Provide course-level functionality
- Integrate with course management

### 2. User Management
- Extend user profiles
- Add user-specific tools
- Integrate with enrollment

### 3. Content Management
- Work with course content
- Provide content tools
- Integrate with activities

### 4. Reporting and Analytics
- Add custom reports
- Provide data analysis
- Export functionality

Remember: Local plugins should enhance Moodle's functionality while maintaining compatibility with core systems and following Moodle's architectural principles.