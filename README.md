# Modular Moodle Plugin Development Assistant (MoMoPDA)

This repository is a collection of prompts that can be combined in different ways in order to use agentic generative AI for software development in Moodle. Its first version is only tested with Claude Code, but with little modifications, it could be made work with other agent software and backends as well. Pull requests welcome!

## File Structure

```
├── PROMPT.md                        # Main orchestrator file
├── CLAUDE.md                        # Redirect to PROMPT.md
└── .prompts/  
    ├── core/
    │   ├── base-instructions.md     # Core Moodle development principles
    │   ├── security-checklist.md    # Security requirements
    │   └── quality-standards.md     # Code quality standards
    ├── plugins/
    │   ├── block.md                 # Block plugin development guide
    │   ├── enrol.md                 # Enrolment plugin development guide
    │   ├── enrol_patterns.md        # Enrolment plugin patterns and anti-patterns
    │   ├── filter.md                # Filter plugin development guide
    │   ├── filter_patterns.md       # Filter plugin patterns and anti-patterns
    │   ├── mod.md                   # Activity module plugin development guide
    │   ├── mod_patterns.md          # Activity module plugin patterns and anti-patterns
    │   ├── qbank.md                 # Question bank plugin development guide
    │   ├── qbank_patterns.md        # Question bank plugin patterns and anti-patterns
    │   ├── qtype.md                 # Question type plugin development guide
    │   ├── qtype_patterns.md        # Question type plugin patterns and anti-patterns
    │   ├── report.md                # Report plugin development guide
    │   ├── report_patterns.md       # Report plugin patterns and anti-patterns
    │   ├── tiny.md                  # TinyMCE editor plugin development guide
    │   └── tiny_patterns.md         # TinyMCE editor plugin patterns and anti-patterns
    ├── tasks/
    │   ├── create.md                # New plugin creation
    │   ├── bugfix.md                # Bug fixing workflow
    │   ├── test.md                  # Test creation
    │   ├── enhance.md               # Feature enhancement
    │   └── refactor.md              # Code refactoring
    └── patterns/
        ├── database.md              # Database operation patterns
        ├── forms.md                 # Moodle forms patterns
        ├── navigation.md            # Navigation integration
        └── api-usage.md             # Common API usage patterns
```
## Moodle Core Repository

The Moodle core repository should be cloned alongside this repository for reference:
```
../moodle/          # Moodle core repository
./                  # This plugin repository
```


## Usage Examples

### Example 1: New Block Plugin
**Detected**: `block_` repository name
**Loads**:
- core/base-instructions.md
- plugins/block.md  
- tasks/create.md
- core/security-checklist.md

### Example 2: Bug Fix in Question Type
**Detected**: `qtype` repository name + git branch "fix/calculation-error"
**Loads**:
- core/base-instructions.md
- plugins/qtype.md
- plugins/qtype_patterns.md
- tasks/bugfix.md
- patterns/database.md (if DB operations detected)
- core/security-checklist.md

### Example 3: New Enrolment Plugin
**Detected**: `enrol_` repository name
**Loads**:
- core/base-instructions.md
- plugins/enrol.md
- plugins/enrol_patterns.md
- tasks/create.md
- core/security-checklist.md

### Example 4: TinyMCE Editor Plugin Enhancement
**Detected**: `tiny_` repository name + request mentions "add feature"
**Loads**:
- core/base-instructions.md
- plugins/tiny.md
- plugins/tiny_patterns.md
- tasks/enhance.md
- patterns/forms.md (if form integration detected)
- core/security-checklist.md

### Example 5: Adding Tests
**Detected**: Request mentions "tests" or "phpunit"
**Loads**:
- core/base-instructions.md
- plugins/{detected_type}.md
- plugins/{detected_type}_patterns.md (if available)
- tasks/test.md
- core/security-checklist.md

## Supported Plugin Types

MoMoPDA provides comprehensive development guides and pattern documentation for the following Moodle plugin types:

### Core Plugin Types
- **Activity Modules** (`mod_*`) - Custom learning activities and assignments
- **Block Plugins** (`block_*`) - Custom dashboard and course blocks
- **Question Types** (`qtype_*`) - Custom question types for quizzes and assignments
- **Question Bank Plugins** (`qbank_*`) - Question bank management and organization tools

### Enrolment and User Management
- **Enrolment Plugins** (`enrol_*`) - Custom user enrolment methods and workflows

### Content and Filtering
- **Filter Plugins** (`filter_*`) - Content processing and transformation filters
- **TinyMCE Editor Plugins** (`tiny_*`) - Rich text editor extensions and tools

### Administration and Reporting
- **Report Plugins** (`report_*`) - Administrative reports and analytics dashboards

### Each Plugin Type Includes:
- **Development Guide** - Complete implementation instructions with code examples
- **Patterns & Anti-Patterns** - Best practices, common pitfalls, and security considerations
- **Testing Strategies** - Unit testing, integration testing, and quality assurance
- **Performance Guidelines** - Optimization techniques and database best practices
- **Security Checklists** - Vulnerability prevention and secure coding practices

All guides are based on analysis of Moodle 5.x core implementations and follow official Moodle development standards.

## Getting Started

### Prerequisites
- [Claude Code](https://claude.ai/code) or compatible agentic AI development environment
- Git
- Moodle development environment (optional but recommended)

### Setup Instructions

1. **Clone the MoMoPDA repository**
   ```bash
   git clone https://github.com/your-org/momopda.git
   cd momopda
   ```

2. **Create your plugin repository**

   Rename or create a new repository following Moodle plugin naming conventions:

   ```bash
   # E.g., for a new block plugin
   git clone https://github.com/your-org/momopda.git moodle-block_your_plugin_name
   cd moodle-block_your_plugin_name

   ```

   **Plugin Naming Convention Examples:**
   - Activity modules: `moodle-mod_interactive_lesson`
   - Block plugins: `moodle-block_nice_new_block`
   - Question types: `moodle-qtype_custom_quiz`
   - Enrolment plugins: `moodle-enrol_company_sso`
   - Filter plugins: `moodle-filter_content_enhancer`
   - TinyMCE plugins: `moodle-tiny_equation_editor`
   - Report plugins: `moodle-report_analytics_dashboard`
   - Question bank plugins: `moodle-qbank_question_organizer`

3. **Optional: Clone Moodle core for reference**
   ```bash
   # In parent directory
   cd ..
   git clone https://github.com/moodle/moodle.git
   ```

   Your directory structure should look like:
   ```
   .
   ├── moodle/                           # Moodle core (optional reference)
   └── moodle-block_your_plugin_name/    # Your plugin with MoMoPDA
       ├── PROMPT.md
       ├── CLAUDE.md
       └── .prompts/
   ```

4. **Start your coding agent from the root of the repository**

5. **Begin development**

   Start by describing what you want to build. MoMoPDA will automatically detect your plugin type from the repository name and load the appropriate guides:

   ```
   "I want to create a new block plugin that displays student progress charts"
   "Help me add a new question type for mathematical expressions"
   "I need to fix a bug in my enrolment plugin's user sync feature"
   ```

### How It Works

MoMoPDA automatically detects your plugin type and development context:

- **Plugin Type Detection**: Based on repository name (e.g., `block_*`, `qtype_*`, `enrol_*`)
- **Task Detection**: Based on git branch names, file changes, and user requests
- **Context Loading**: Automatically loads relevant guides, patterns, and best practices
- **Security & Quality**: Always includes security checklists and quality standards

### Tips for Best Results

1. **Use descriptive repository names** following Moodle conventions
2. **Be specific in your requests** - mention features, requirements, and constraints
3. **Reference existing Moodle plugins** if you want similar functionality
4. **Ask for tests** - MoMoPDA includes comprehensive testing guidance
5. **Request security reviews** when handling user data or permissions

### Troubleshooting

- **Plugin type not detected?** Ensure your repository name follows the `moodle-{plugintype}_{pluginname}` convention
- **Missing guidance?** Check if your plugin type is supported in the list above
- **Need custom patterns?** The guides include extension points for custom functionality
- **Your new plugin has bugs?** Fix them and ask your coding agent to improve the patterns files!
