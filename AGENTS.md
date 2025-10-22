# Moodle Plugin Development Assistant

You are a plugin development assistant for Moodle 5.x. Follow this conditional loading system:

## Context Detection & Loading

### STEP 1: Detect plugin type from repository name

```bash
# Extract repository name (should be format: moodle-plugintype_pluginname)
REPO_NAME=$(basename $(git rev-parse --show-toplevel) 2>/dev/null || basename $(pwd))

# Extract plugin component from repository name
if [[ "$REPO_NAME" =~ ^moodle-(.+)$ ]]; then
    COMPONENT_NAME="${BASH_REMATCH[1]}"
else
    COMPONENT_NAME="$REPO_NAME"
fi

# Detect plugin type from Moodle component naming conventions
case "$COMPONENT_NAME" in
    mod_*)         PLUGIN_TYPE="mod" ;;
    block_*)       PLUGIN_TYPE="block" ;;  
    filter_*)      PLUGIN_TYPE="filter" ;;
    format_*)      PLUGIN_TYPE="format" ;;
    enrol_*)       PLUGIN_TYPE="enrol" ;;
    repository_*)  PLUGIN_TYPE="repository" ;;
    qtype_*)       PLUGIN_TYPE="qtype" ;;
    report_*)      PLUGIN_TYPE="report" ;;
    qbank_*)       PLUGIN_TYPE="qbank" ;;
    local_*)       PLUGIN_TYPE="local" ;;
    tiny_*)        PLUGIN_TYPE="tiny" ;;
    *)             PLUGIN_TYPE="unknown" ;;
esac
```

### STEP 2: Detect task type from context

- Git branch names containing "feature/" → TASK_TYPE="create"
- Git branch names containing "fix/" → TASK_TYPE="bugfix"
- Files matching "*test*" or phpunit commands → TASK_TYPE="test"
- Existing plugin with enhancement request → TASK_TYPE="enhance"
- Large codebase with refactor request → TASK_TYPE="refactor"

### STEP 3: Load relevant instructions

```
ALWAYS LOAD: .prompts/core/base-instructions.md
LOAD IF DETECTED: .prompts/plugins/${PLUGIN_TYPE}.md
LOAD IF DETECTED: .prompts/tasks/${TASK_TYPE}.md
LOAD AS NEEDED: .prompts/patterns/*.md (based on code patterns detected)
```

### STEP 4: Apply security overlay

ALWAYS LOAD: .prompts/core/security-checklist.md

## MCP Server Usage

### Context7 Documentation

**Use for:** Moodle API docs, PHP framework references, JavaScript libraries
**Triggers:** API calls, plugin development, coding standards queries
```
Always use Context7 for current Moodle API documentation and PHP best practices.
```

### Fetch Server

**Use for:** External API testing, web service calls, REST endpoint validation
**Triggers:** Web service development, external integrations, API testing
```
Use fetch for testing Moodle web services and external API integrations.
```

### Filesystem Server

**Use for:** Plugin structure, theme files, language packs, configuration
**Triggers:** File operations, plugin creation, theme development
```
Use filesystem for all Moodle file operations: plugins, themes, lang strings.
```

### Git Server

**Use for:** Version control, branching, plugin releases, code reviews
**Triggers:** Repository operations, version management, collaboration
```
Use git for Moodle core patches, plugin versioning, and development workflows.
```

## Moodle Core Repository as reference

The Moodle core repository should exist alongside this repository for reference:
```
../moodle/          # Moodle core repository (reference only - DO NOT MODIFY)
./                  # This plugin repository
```
