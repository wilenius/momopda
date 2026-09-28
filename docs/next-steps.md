# Next Implementation Steps

This document is the context-clear handoff for the modernization work started on 19 August 2026. The plan is in [`roadmap.md`](roadmap.md); completed milestone detail is in [`history.md`](history.md).

## Repository State

- Branch: `feature/agent-skills-conversion`, pushed to `origin`.
- Four public graders are registered and deterministically proven: `filter-modern-contract` and `activity-schema-upgrade` (Moodle 4.5.13/PHP 8.1), `qbank-bulk-action` and `tiny-toolbar-button` (Moodle 5.2.2/PHP 8.4).
- Hosted `Validate` and `Moodle integration` workflows are green on the pinned boundaries.
- The worktree may contain user files. Inspect `git status` before editing and do not reset or overwrite them.
- Do not restore the deleted old skill files or the tracked `tags` artifact.

The canonical entry point is `skills/moodle-plugin-development/SKILL.md`. There must be exactly one `SKILL.md` under `skills/`.

## Pinned Boundaries

| Moodle tag | Moodle commit | PHP | Layout |
|---|---|---:|---|
| `v4.5.13` | `8cbae18a2898cfd8266ec91ac206e12004f0ff5f` | 8.1 | Repository root |
| `v5.2.2` | `acfa383c13dd46c83ca82894a8e95fac273fda33` | 8.4 | `public/` web root |

Grader usage, conditions, and runner commands are in [`evals/README.md`](../evals/README.md). Per-task workers are `tools/run_{filter,qbank,tiny,activity}_grader.sh`.

## Next Milestone: Measure

Roadmap Milestone 1. Build no new grader.

1. Add an under-specified prompt variant for each of the four graded tasks. State the feature as a plugin developer would request it and omit security, API, and schema instructions; keep the task's `public_checks` unchanged. Keep the current prompts as the strict control. The harness must record which variant ran.
2. Run candidate, released (`acb41db4cb49f436f56faae95eb90b659428c704`), and no-skill conditions for both variants, 5–10 samples each, with at least two explicit models. Include at least one Claude Code run to check client parity; add a Claude Code client to the harness only if needed for that.
3. Grade every sample in the existing disposable workers and summarize per-check pass rates by task, condition, variant, and model, with token use and duration.
4. Write the result to `evals/results/` as an aggregate report only; keep generated workspaces, records, logs, and Moodle trees outside the repository.

Acceptance: every run ends `pass`, `fail`, or a distinct non-success status; no single sample is ranked; the report states where the skill changes outcomes and where all conditions fail.

## Invariants

- Keep one canonical skill and do not reintroduce inter-skill dependencies.
- Keep examples executable and validation non-fixing.
- Report skipped functional checks as incomplete, never successful.
- Use pinned Moodle source and executable tests before prose or text matching.
- Keep the 4.5/5.x physical path difference explicit; URLs never gain `/public`.
- Keep generation, grading, records, and summaries separable.
- Keep private holdout material outside this repository.
- Never expose credentials, hidden reasoning, or grader material to the generating agent.
- Do not edit skill references in response to a specific evaluation failure before the holdout exists.

## Context-Reset Prompt

> Read `docs/roadmap.md` and `docs/next-steps.md`, then implement the Measure milestone only. Inspect the worktree before editing and preserve any user changes. Add under-specified prompt variants for the four graded tasks without changing their checks, then run candidate, released, and no-skill conditions with repeated samples across at least two models, grade them in the existing disposable workers, and write an aggregate report. Do not add graders, edit skill references, or keep generated artifacts in the repository.
