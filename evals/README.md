# Evaluations

MoMoPDA evaluates generated behavior rather than textual similarity to an exemplar.

## Public Smoke Tasks

`public/tasks.json` contains representative prompts and declares the fixture used to seed an isolated plugin workspace. `tools/eval_harness.py` prepares and runs each task with the candidate skill, an explicitly supplied released skill, or no skill. Run directories must be outside this repository so parent-directory discovery cannot contaminate the no-skill condition.

Public graders should prioritize:

1. Plugin installation on the target Moodle branch.
2. Hidden or generated PHPUnit tests for requested behavior.
3. Moodle Plugin CI with zero coding-style warnings.
4. Security invariants such as context, capability, sesskey, and output handling.
5. Task-specific forbidden patterns.

An LLM judge should be used only for qualities that deterministic checks cannot establish. Pairwise judgments should be blinded and randomized.

## Private Holdout Suite

Holdout prompts, mutation cases, hidden tests, and expected outcomes belong in a separate private repository. The generating agent must receive only the task prompt, starting workspace, released skill, and target Moodle source. It must not receive grader files or exemplar solutions.

Record the model identifier, model settings, client and harness versions, skill revision, Moodle revision, tokens, duration, and repeated-run results for every evaluation.

## Public Harness

The phases are intentionally separate. A fake run requires no network, credentials, or model spend:

```bash
run=/tmp/momopda-evals/filter-candidate-001
python3 -I -B tools/eval_harness.py prepare \
    --task filter-modern-contract \
    --condition candidate \
    --output "$run"
python3 -I -B tools/eval_harness.py run \
    --run-dir "$run" \
    --client fake
python3 -I -B tools/eval_harness.py summarize "$run"
```

A released run requires `--condition released --skill <directory>`. The harness rejects the canonical candidate path as a released input. A no-skill run uses `--condition none` and rejects `--skill`.

OpenCode is invoked only when a model is explicit. Omitting `--model` writes an `incomplete` result without starting a model request:

```bash
python3 -I -B tools/eval_harness.py run \
    --run-dir "$run" \
    --client opencode \
    --model provider/model \
    --moodle-source /path/to/moodle-4.5.13 \
    --timeout 900
```

The source checkout must be at the pinned commit declared in `knowledge/compatibility.json`. The harness creates a read-only detached clone for the agent, disables external skill discovery and plugins, isolates OpenCode configuration, and denies shell and network tools. It does not use `--auto`.

The `filter-modern-contract` grader requires PHP 8.1, Moodle Plugin CI 4.5.11, Composer 2, Node.js with `npm`/`npx`, the PostgreSQL client, and an empty reachable PostgreSQL database server. Generated plugin code is untrusted and grading must run on a disposable CI worker or container with no provider credentials and no sensitive writable mounts. The harness additionally strips the inherited environment, uses a dedicated home and temporary directory, rejects candidate-owned grader control files, and terminates timed-out process groups. It creates a unique database name and fresh Moodle, Moodledata, and plugin trees for every run:

```bash
python3 -I -B tools/eval_harness.py grade \
    --run-dir "$run" \
    --plugin-ci /tmp/opencode/moodle-plugin-ci/bin/moodle-plugin-ci \
    --db-host 127.0.0.1 \
    --db-user postgres \
    --db-pass moodle
```

The grader runs no fixers. It executes PHP lint, coding style with zero warnings, plugin validation, PHPDoc with zero warnings, savepoints, and separate Moodle PHPUnit checks for the modern class/marker contract and hostile localized replacement content. Missing prerequisites stay `incomplete`; installation failures are `error`; assertion and Plugin CI failures are `fail`.

Run records conform to `public/run-result.schema.json`. Event, stderr, grader, and tool logs remain outside the agent workspace. Summaries consume saved records only and do not rank skill conditions from a single sample.
