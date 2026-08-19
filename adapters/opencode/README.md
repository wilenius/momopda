# OpenCode Adapter

Run `python3 scripts/install_skill.py --client opencode --project /path/to/plugin` from the MoMoPDA repository.

The installer creates `.opencode/skills/moodle-plugin-development`. It uses a relative link for an in-project MoMoPDA submodule and a vendored copy for an external clone. OpenCode scans `SKILL.md` files in that project location. Restart OpenCode after installation or an update.

When Claude Code is also used, install with `--client all` instead. OpenCode discovers the shared `.claude/skills` location and does not receive a duplicate definition.

Use `--update` to refresh a vendored copy. The installer never replaces an unrecognized directory.
