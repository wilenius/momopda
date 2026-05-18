# MoMoPDA - Moodle Plugin Development Assistant

MoMoPDA is a collection of Agent Skills for developing Moodle plugins. Following the [Agent Skills standard](https://agentskills.io), these skills work with Claude Code, Gemini CLI, and other compatible AI development tools.

## Available Skills

| Skill | Description |
| ----- | ----------- |
| `moodle-core` | Core Moodle 5.x development: coding standards, security, JavaScript, CI validation |
| `moodle-activity` | Activity module plugins (mod_*) |
| `moodle-block` | Block plugins (block_*) |
| `moodle-qtype` | Question type plugins (qtype_*) |
| `moodle-qbank` | Question bank plugins (qbank_*) |
| `moodle-enrol` | Enrolment plugins (enrol_*) |
| `moodle-filter` | Filter plugins (filter_*) |
| `moodle-tiny` | TinyMCE editor plugins (tiny_*) |
| `moodle-report` | Report plugins (report_*) |
| `moodle-contenttype` | Content bank type plugins (contenttype_*) |
| `moodle-local` | Local plugins (local_*) |

## Installation

### Claude Code

```bash
# Clone this repository
git clone https://github.com/wilenius/momopda.git

# Or use as a submodule in your plugin project
git submodule add https://github.com/wilenius/momopda.git .skills
```

Skills are automatically discovered from the `skills/` directory.

### Other AI Tools

Copy the desired skill folders to your tool's skill directory, or reference them directly.

## Usage

### Activate Skills

When working on a Moodle plugin, activate the relevant skills:

```text
# For a block plugin
/skill moodle-core
/skill moodle-block

# For an activity module
/skill moodle-core
/skill moodle-activity
```

### Skill Combinations

- **Always use `moodle-core`** - provides base coding standards, security practices, and CI validation
- **Add one plugin-type skill** - matches the type of plugin you're developing

### Environment Setup

Set the `MOODLE_DIR` environment variable to point to your Moodle installation:

```bash
export MOODLE_DIR=/path/to/moodle
```

Or place Moodle at `../moodle` relative to your plugin directory.

## Directory Structure

```text
skills/
├── moodle-core/
│   ├── SKILL.md                # Core development practices
│   ├── scripts/
│   │   └── run-ci.sh           # CI validation script
│   └── references/
│       ├── ci-validation.md    # Detailed CI guide
│       ├── design-principles.md # UI/UX guidelines
│       └── html-writer.md      # HTML generation patterns
│
├── moodle-activity/
│   ├── SKILL.md                # Activity module guide
│   └── references/
│       └── patterns.md         # Detailed patterns
│
├── moodle-block/
│   └── SKILL.md                # Block plugin guide
│
└── [other plugin types...]
```

## CI Validation

The `moodle-core` skill includes a CI validation script:

```bash
# From your plugin directory
./path/to/skills/moodle-core/scripts/run-ci.sh

# Or if moodle-plugin-ci is installed at ../moodle-plugin-ci/
../moodle-plugin-ci/bin/moodle-plugin-ci phplint ./
../moodle-plugin-ci/bin/moodle-plugin-ci codechecker ./
```

See [Moodle Plugin CI](https://moodlehq.github.io/moodle-plugin-ci/) for installation.

## Example Prompts

### Creating a New Plugin

> I want to create a block plugin that displays student progress charts on the course page.
> Help me create a question type plugin for mathematical expression input with LaTeX rendering.
> Help me create a content bank type plugin that lets teachers upload and preview SVG diagrams in the content bank.

### Bug Fixing

> I need to fix a bug in my enrolment plugin's user sync feature - users aren't being enrolled when their company SSO token expires.

### Complex Projects

> I want to create a question bank (qbank) plugin which adds bulk edit functionality. It should use the AI generation purpose from ../moodle-local_ai_manager and the architecture of ../moodle-qbank_questiongen to: 1) bulk select questions to modify, 2) add a modification prompt, 3) generate new versions according to the prompt, 4) add a prefix to distinguish new questions.
> This repo has a modular prompt system for developing Moodle plugins. I need to develop a local plugin that adds User overrides to all the quizzes on the course area. MVP: add custom quiz time limit for a user.

## Tips for Best Results

1. **Activate both skills** - always use `moodle-core` plus your plugin-type skill
2. **Be specific** - mention features, requirements, and constraints
3. **Reference examples** - point to existing Moodle plugins for similar functionality
4. **Ask for tests** - each skill includes testing guidance
5. **Request CI validation** - run quality checks before committing

## Contributing

Contributions welcome! Please follow the Agent Skills standard when adding new skills or improving existing ones.

## License

See [LICENSE](LICENSE) for details.

## Resources

- [Agent Skills Standard](https://agentskills.io)
- [Moodle Developer Docs](https://moodledev.io)
- [Moodle Plugin CI](https://moodlehq.github.io/moodle-plugin-ci/)
- [Component Library](https://componentlibrary.moodle.com/)
