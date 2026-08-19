# Modernization Roadmap

## Implemented

- One canonical progressively disclosed Agent Skill.
- Deterministic component and Moodle-version routing rules.
- Focused contracts for nine plugin types and four cross-cutting topics.
- Nine minimal contract fixtures derived from Moodle core.
- Dependency-free repository validation.
- Pinned Moodle Plugin CI lint, coding-style, and savepoint workflow.
- OpenCode and Claude Code installation adapters with discovery smoke testing for OpenCode.
- Structured compatibility and source registries.
- Weekly support, review-age, and authoritative-link freshness checks.
- Public benchmark task format and private holdout design.

## Next Integration Milestone

The implementation handoff, verified commands, and acceptance criteria are in [`next-steps.md`](next-steps.md).

Add a database-backed GitHub Actions matrix at the compatibility boundaries recorded in `knowledge/compatibility.json`:

| Moodle | PHP | Purpose |
|---|---:|---|
| 4.5 | 8.1 | Oldest supported API and runtime boundary |
| 5.2 | 8.4 | Newest stable boundary at the initial review |

The workflow must install every fixture at the layout-specific destination, complete Moodle installation, exercise plugin discovery, run applicable PHPUnit and frontend checks, and retain logs as artifacts. Moving stable branches and Moodle `main` belong in a non-blocking scheduled canary workflow.

## Evaluation Milestone

Build an isolated generation harness around `evals/public/tasks.json`. Keep smoke graders public and place holdout prompts, hidden tests, and security mutations in a private repository. Publish aggregate pass rates, regressions, token use, duration, model and client versions, and exact skill/Moodle revisions.

## Release Milestone

After the boundary matrix passes, update the reviewed Moodle revisions in `knowledge/sources.json`, tag the first modernized pre-release, test installation in released OpenCode and Claude Code versions, and make the skill branch the repository default.
