# Claude Code Adapter

Run `python3 scripts/install_skill.py --client claude-code --project /path/to/plugin` from the MoMoPDA repository.

The installer creates `.claude/skills/moodle-plugin-development`. It uses a relative link for an in-project MoMoPDA submodule and a vendored copy for an external clone. The same location is used by `--client all`. Restart Claude Code after installation or an update.

Use `--update` to refresh a vendored copy. The installer never replaces an unrecognized directory.
