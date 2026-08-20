# Modernization Roadmap

## Implemented

- One canonical progressively disclosed Agent Skill.
- Deterministic component and Moodle-version routing rules.
- Focused contracts for nine plugin types and four cross-cutting topics.
- Nine minimal contract fixtures derived from Moodle core.
- Dependency-free repository validation.
- Pinned Moodle Plugin CI lint, coding-style, and savepoint workflow.
- Database-backed integration boundaries for Moodle 4.5.13/PHP 8.1 and Moodle 5.2.2/PHP 8.4.
- Runtime discovery and defining-contract assertions for all nine fixtures.
- OpenCode and Claude Code installation adapters with discovery smoke testing for OpenCode.
- Structured compatibility and source registries.
- Weekly support, review-age, and authoritative-link freshness checks.
- Public benchmark task format and private holdout design.

## Enforced Integration Boundaries

The database-backed GitHub Actions matrix enforces the compatibility boundaries recorded in `knowledge/compatibility.json`:

| Moodle tag | PHP | Layout | Purpose |
|---|---:|---|---|
| `v4.5.13` | 8.1 | Repository root | Oldest supported API and runtime boundary |
| `v5.2.2` | 8.4 | `public/` web root | Newest stable boundary at the initial review |

Each job starts from an empty PostgreSQL database, stages hashed copies of all nine fixtures, verifies the pinned Moodle commit and physical destinations, completes Moodle installation, exercises discovery and defining contracts, runs strict Plugin CI and frontend checks, and retains failure logs. Moving stable branches and Moodle `main` remain reserved for a non-blocking scheduled canary after the pinned workflow is green.

## Evaluation Milestone

Build an isolated generation harness around `evals/public/tasks.json`. Keep smoke graders public and place holdout prompts, hidden tests, and security mutations in a private repository. Publish aggregate pass rates, regressions, token use, duration, model and client versions, and exact skill/Moodle revisions.

## Release Milestone

After the boundary matrix passes, update the reviewed Moodle revisions in `knowledge/sources.json`, tag the first modernized pre-release, test installation in released OpenCode and Claude Code versions, and make the skill branch the repository default.
