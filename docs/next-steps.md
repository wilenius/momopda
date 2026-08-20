# Next Implementation Steps

This document is the context-clear handoff for the modernization work started on 19 August 2026.

## Repository State

- Branch: `feature/agent-skills-conversion`.
- The current HEAD contains the first public evaluation vertical slice after this handoff is committed.
- The branch has not been pushed. Do not add moving-branch or Moodle `main` canaries until the hosted pinned boundary jobs are green.
- The expected worktree after the handoff commit is clean.
- Do not restore the deleted old skill files or the tracked `tags` artifact.
- Do not modify or discard unrelated user changes.

The canonical entry point remains `skills/moodle-plugin-development/SKILL.md`. There must be exactly one `SKILL.md` under `skills/`.

## Completed Boundaries

Commit `acb41db` implements the database-backed compatibility matrix:

| Moodle tag | Moodle commit | PHP | Layout |
|---|---|---:|---|
| `v4.5.13` | `8cbae18a2898cfd8266ec91ac206e12004f0ff5f` | 8.1 | Repository root |
| `v5.2.2` | `acfa383c13dd46c83ca82894a8e95fac273fda33` | 8.4 | `public/` web root |

Both boundaries were recreated locally from empty PostgreSQL 17.11 databases. Each passed discovery and hash checks for all nine fixtures, five PHPUnit tests, strict Plugin CI validation, zero-warning coding style and PHPDoc, Mustache, savepoints, and TinyMCE Grunt checks.

## Completed First Slice

The public harness now implements `filter-modern-contract` end to end in separable phases:

- `tools/eval_harness.py` provides `prepare`, `run`, `grade`, `summarize`, and `validate` commands.
- All eight tasks can be prepared deterministically outside the repository.
- Setup removal and overlay paths are traversal-safe, reject symlinks, preserve source hashes, and refuse existing destinations.
- Candidate, explicit released, and no-skill conditions use isolated OpenCode configuration roots.
- OpenCode receives only the task prompt, selected skill, isolated plugin, and read-only pinned Moodle source.
- OpenCode execution uses argument arrays, no `--auto`, process-group timeouts, separate JSON/stderr capture, credential redaction, and strict terminal-event checks.
- Skips, client errors, malformed streams, timeouts, unsupported usage, grading failures, and incomplete prerequisites remain distinct.
- `evals/public/run-result.schema.json` and runtime validation enforce versioned records, exact revisions, hashes, changes, usage, artifacts, and check outcomes.
- `evals/public/graders.json` maps the implemented task to its declared checks.
- The filter grader creates fresh Moodle, Moodledata, plugin, and database state per run.
- The grader runs non-fixing lint, coding style, validation, PHPDoc, savepoints, and exact Moodle PHPUnit methods for the modern class/marker contract and hostile localized replacement content.
- Candidate-owned Plugin CI/PHPUnit controls are rejected recursively, and generated code is graded with a scrubbed environment on a disposable worker.
- `tools/fake_eval_client.py` and `tools/tests/test_eval_harness.py` cover success, non-zero exit, timeout, malformed output, destination reuse, condition isolation, actual OpenCode skill discovery, skipped real execution, control-file attacks, redaction, usage, and record mutations.
- `tools/validate_repo.py` validates task/setup safety, schemas, grader mappings, PHP syntax, and the offline harness suite.
- `evals/public/opencode-probe.md` records OpenCode 1.18.18 event, permission, usage, stderr, and timeout behavior.
- The canonical filter fixture now escapes the localized replacement string with `s()` before placing it in the span.

## Verification State

The final tree passed:

```bash
python3 -I -B tools/validate_repo.py
python3 -I -B -m unittest discover -s tools/tests -p 'test_*.py' -v
git diff --check
```

The harness suite has 11 passing tests. All nine canonical fixtures pass Moodle Plugin CI 4.5.11 `phplint`, zero-warning `codechecker`, and `savepoints`. The public filter grader passes Moodle PHPCS. Docker actionlint 1.7.12 passes all workflows.

Explicit `openai/gpt-5.6-sol` runs succeeded with OpenCode 1.18.18, emitted validated usage and change records, loaded exactly the candidate skill, and did not expose the grader. No-skill discovery found zero MoMoPDA skills.

The full Moodle grader was exercised in disposable PHP 8.1/PostgreSQL containers, but the ad hoc PHP image lacked boundary prerequisites in sequence (`psql`, Composer, then `npm`). Every attempt remained `error`; no check was converted into a pass. The disposable runs and containers were removed. The harness now preflights Composer, Git, Node `npm`/`npx`, and the PostgreSQL client before creating grading state.

No complete real-model Moodle grader record has therefore been produced yet. Close that proof gap before adding another grader.

## Immediate Milestone

Run the first slice to completion in one reproducible disposable environment, then collect a small non-ranked baseline cohort.

1. Provision PHP 8.1, Moodle Plugin CI 4.5.11, Composer 2, Node.js with `npm`/`npx`, Git, the PostgreSQL client, and isolated PostgreSQL 17.11 together.
2. Run `filter-modern-contract` through the fake client and prove the grader reaches all Plugin CI and both Moodle PHPUnit checks. A behavioral failure is acceptable; an infrastructure `error` or prerequisite `incomplete` is not.
3. Run one explicit-model candidate sample, one explicit released-skill sample, and one no-skill sample in separate run roots.
4. Use an explicit released skill path or immutable artifact. Never point the released condition at the candidate skill.
5. Validate every saved `run.json` and derive one summary from the records.
6. Preserve concise logs outside the repository, but do not commit generated workspaces, Moodle trees, model event streams, or result records.
7. Do not rank the conditions from this single non-deterministic sample.

Prefer adding a pinned, repeatable runner or workflow command over another ad hoc container. Generated plugin code is untrusted: use a disposable worker with no provider credentials or sensitive writable mounts.

## Grader Command

The grading environment must expose all prerequisites on `PATH`:

```bash
python3 -I -B tools/eval_harness.py grade \
    --run-dir /tmp/momopda-evals/<run-id> \
    --plugin-ci /tmp/opencode/moodle-plugin-ci/bin/moodle-plugin-ci \
    --db-host 127.0.0.1 \
    --db-port 5432 \
    --db-user postgres \
    --db-pass moodle
```

The complete usage and condition commands are in `evals/README.md`.

## Immediate Acceptance

- At least one first-slice grade reaches every declared check and ends as `pass` or `fail`, not `error` or `incomplete`.
- The Moodle checkout is exactly `v4.5.13` at `8cbae18a2898cfd8266ec91ac206e12004f0ff5f`.
- Each run uses unique mutable Moodledata and database state.
- Candidate, released, and no-skill discovery remains isolated.
- Saved records validate and the summary reports statuses without ranking.
- No credentials, reasoning text, grader implementation, or exemplar reaches the generating agent or saved events.
- `tools/validate_repo.py`, the 11 harness tests, fixture checks, actionlint, and `git diff --check` remain green.

## Following Milestones

1. Implement `qbank-bulk-action` as the second public vertical slice, including sesskey, context capability, and per-question capability assertions on pinned Moodle 5.2.
2. Implement deterministic graders for the remaining six public tasks.
3. Run repeated candidate/released/no-skill comparisons without ranking single samples.
4. Create the separate private holdout repository for hidden prompts, tests, expected outcomes, and mutation cases.
5. Add source-path change tracking for selected Moodle contracts.
6. Add non-blocking moving-branch and Moodle `main` canaries only after hosted pinned jobs are green.
7. Test a release artifact in current OpenCode and Claude Code releases.

## Invariants

- Keep one canonical skill and do not reintroduce inter-skill dependencies.
- Keep examples executable and validation non-fixing.
- Report skipped functional checks as incomplete, never successful.
- Use pinned Moodle source and executable tests before prose or text matching.
- Keep the 4.5/5.x physical path difference explicit; URLs never gain `/public`.
- Keep generation, grading, records, and summaries separable.
- Keep private holdout material outside this repository.
- Never expose credentials, hidden reasoning, or grader material to the generating agent.
