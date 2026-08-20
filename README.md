# MoMoPDA

MoMoPDA is one progressively disclosed Agent Skill for developing Moodle plugins. It supports Moodle 4.5 LTS and Moodle 5.x releases that still receive upstream security support.

The canonical skill is [`moodle-plugin-development`](skills/moodle-plugin-development/SKILL.md). It identifies the target Moodle version and plugin component, loads one plugin-type contract, and adds topic references only when the task needs them.

## Why One Skill?

The Agent Skills specification does not define dependencies between skills. A collection that requires users to activate both a core skill and a plugin-type skill can therefore omit security or validation guidance. MoMoPDA keeps the mandatory baseline in one entry point and uses references for progressive disclosure.

## Supported Plugin Types

| Component | Plugin type |
|---|---|
| `mod_*` | Activity modules |
| `block_*` | Blocks |
| `enrol_*` | Enrolment methods |
| `filter_*` | Text filters |
| `local_*` | Local plugins |
| `qbank_*` | Question bank plugins |
| `qtype_*` | Question types |
| `report_*` | Site reports |
| `tiny_*` | TinyMCE plugins |

## Install

Use the installer from a clone or submodule. In `auto` mode it creates a relative link when MoMoPDA is inside the plugin project and otherwise vendors a copy, so projects remain portable.

```bash
python3 scripts/install_skill.py --client opencode --project /path/to/plugin
python3 scripts/install_skill.py --client claude-code --project /path/to/plugin
```

Install once for both clients using the Claude-compatible project location that OpenCode also discovers:

```bash
python3 scripts/install_skill.py --client all --project /path/to/plugin
```

An OpenCode-only installation uses `.opencode/skills/moodle-plugin-development`. A Claude Code or shared installation uses `.claude/skills/moodle-plugin-development`. This avoids duplicate OpenCode discovery.

Restart a running client after installing or updating the skill because skill discovery occurs at startup.

Refresh a vendored installation explicitly:

```bash
python3 scripts/install_skill.py --client all --project /path/to/plugin --update
```

The installer updates only copies carrying its management marker and refuses to replace unrelated content.

## Moodle Checkout

Set `MOODLE_DIR` to a Moodle checkout or configured installation:

```bash
export MOODLE_DIR=/path/to/moodle
```

Moodle 4.5 keeps plugin directories at the repository root. Moodle 5.1 and later keep web-accessible plugin directories below `public/`; Moodle URLs still do not include `/public`.

## Contract Fixtures

Minimal plugin fixtures live in `skills/moodle-plugin-development/assets/fixtures/`. They are derived from stable contracts and simple implementations in Moodle core. CI installs all nine into fresh Moodle 4.5.13 and 5.2.2 sites, verifies layout-specific discovery, and exercises their defining contracts. They are not production starter plugins.

## Validate This Repository

Run the same dependency-free validation used in CI:

```bash
python3 -I -B tools/validate_repo.py
```

The validator checks the skill manifest, internal resources, compatibility data, installation adapters, script syntax, fixture manifests, and PHP syntax when PHP is available.

## Validate A Consumer Plugin

The skill includes a read-only Moodle Plugin CI wrapper:

```bash
skills/moodle-plugin-development/scripts/validate-plugin.sh /path/to/plugin
```

It never runs a code fixer. Missing Moodle-dependent checks produce an incomplete result rather than a false success.

## Knowledge Maintenance

[`knowledge/compatibility.json`](knowledge/compatibility.json) records the support policy. [`knowledge/sources.json`](knowledge/sources.json) maps important contracts to official documentation and Moodle-core paths. A weekly workflow checks support deadlines, review age, and authoritative links, then creates or updates one review issue. It never rewrites guidance automatically.

## Evaluations

Public smoke tasks and the holdout-suite design are documented in [`evals/`](evals/README.md). Deterministic graders should run before any blinded model judgment. The roadmap is in [`docs/roadmap.md`](docs/roadmap.md), and the context-clear implementation handoff is in [`docs/next-steps.md`](docs/next-steps.md).

## License

MoMoPDA is licensed under GPL-3.0-or-later. See [LICENSE](LICENSE).
