# Modernization Roadmap

## Guiding Question

Every milestone must help answer one question: **does the skill measurably change what an agent produces for Moodle plugin work?** Infrastructure is built when a measurement needs it, not ahead of evidence.

## Implemented

- One canonical progressively disclosed Agent Skill with deterministic component and Moodle-version routing.
- Focused contracts for nine plugin types and four cross-cutting topics.
- Nine minimal contract fixtures derived from Moodle core, installed and exercised on Moodle 4.5.13/PHP 8.1 and 5.2.2/PHP 8.4 in hosted CI.
- Dependency-free repository validation and pinned Moodle Plugin CI checks.
- OpenCode and Claude Code installation adapters.
- Structured compatibility and source registries with weekly freshness checks.
- A public evaluation harness with candidate, released, and no-skill conditions.
- Deterministic graders for `filter-modern-contract`, `qbank-bulk-action`, `tiny-toolbar-button`, and `activity-schema-upgrade`, each proven by an unsolved fixture, an external known-good implementation, and targeted mutations.

Milestone detail is in [`history.md`](history.md).

## Evidence So Far

One non-ranked real-model cohort (filter task, one sample per condition) produced identical failures for the candidate skill, the released skill, and no skill: all passed Plugin CI and the modern contract, and all left hostile localized content unescaped. The prompt did not mention escaping. This is the only evidence of skill effect to date, and it shows none.

## Known Weaknesses

- **Prompts disclose the answer.** The qbank, Tiny, and activity prompts spell out security, API, and schema requirements. A no-skill agent receives the same checklist, so these tasks mostly measure specification-following rather than skill knowledge.
- **The skill is tuned against its public tests.** References were updated alongside each grader. Without a holdout, public pass rates overstate generalization.
- **Coverage narrowed in the rewrite.** Forms, navigation, admin settings, events, scheduled tasks, backup/restore, web services, and bugfix/refactor/test workflows receive little or no guidance. Which omissions matter is unknown.
- **Graders are expensive.** Each slice adds a task-specific Dockerfile and runner.

## Milestone 1: Measure

Run the four existing graders with no new grader work.

- Three conditions (candidate, released `acb41db`, none), 5–10 samples each, at least two models.
- At least one Claude Code run alongside OpenCode to confirm client parity.
- Add **under-specified prompt variants** for each graded task that state the feature as a user would, while the grader keeps every security and API check. Keep the current strict prompts as a specification-following control.
- Report per-check pass rates by condition and prompt variant, with token use and duration. No ranking from single samples.

Exit: a written result stating where the skill helps, where it does not, and where every condition fails.

## Milestone 2: Private Holdout

Create the separate private repository before further skill tuning.

- Start with 3–4 hidden tasks using under-specified prompts, including at least one drawn from real plugin history (see Milestone 3).
- Freeze the skill revision used for each holdout run; never edit references in response to a specific holdout failure.

## Milestone 3: Real-Plugin Material

Use well-maintained, GPL-licensed third-party Moodle plugins as evaluation and reference material, not as skill content.

**Selection criteria:** listed in the Moodle Plugins directory, supports 4.5 LTS and a current 5.x release, active maintenance, its own PHPUnit and/or Behat tests, passing Moodle Plugin CI, and a GPL-3.0-or-later–compatible license. Record each chosen plugin with a pinned commit in `knowledge/sources.json`.

**Uses, in priority order:**

1. **Historical change replay.** Take a real fix or feature commit, reset the plugin to its parent, give the agent the issue text, and grade with the tests that the upstream commit added plus Plugin CI. This yields realistic, under-specified tasks with ready-made graders and requires no bespoke assertion code. Prefer commits made after the evaluated models' training cutoffs to limit memorization, and route such tasks to the private holdout.
2. **Known-good references for graders.** Real implementations of a contract (bulk actions, external functions, Tiny buttons) can serve as additional known-good candidates, testing that graders do not reject valid designs that differ from the in-house exemplar.
3. **Coverage audit.** Survey which APIs and files recur across selected plugins (forms, settings, events, tasks, privacy, backup) to decide which narrowed topics need references restored, guided by Milestone 1 failures.

**Constraints:** the skill must not direct agents to third-party code as authority; the source-authority order in `SKILL.md` stays unchanged. Third-party code never enters the canonical skill as copied examples. Popular plugins are likely in model training data, so they are unsuitable as public benchmarks of generalization.

## Milestone 4: Targeted Improvement

Change skill references only where Milestones 1–3 show a measurable gap, then re-run the affected public tasks and the holdout. Restore coverage topics only when evidence shows agents fail without them.

## Milestone 5: Remaining Graders

Consolidate the four task-specific worker images into one image parameterized by Moodle and PHP version. Then add graders for `local-external-function`, `qtype-safe-rendering`, `report-portable-query`, and `enrol-instance-ui` only where earlier results indicate the skill is weak in that area or replay tasks do not already cover it.

## Release

Tag the first modernized pre-release once Milestone 1 has produced a written result, test installation in current OpenCode and Claude Code releases, and make the skill branch the repository default. Do not wait for all graders; the current `main` is inferior to the modernized skill.

## Deferred

- Source-path change tracking for selected Moodle contracts.
- Non-blocking moving-branch and Moodle `main` canaries (hosted pinned jobs are green, so this is unblocked but low priority).
- Blinded LLM judgment for qualities deterministic checks cannot establish.
