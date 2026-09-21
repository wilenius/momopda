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

The three registered graders select their assertion through `public/graders.json`. `filter-modern-contract` requires PHP 8.1 and Moodle 4.5.13; `qbank-bulk-action` and `tiny-toolbar-button` require PHP 8.4 and Moodle 5.2.2. All require Moodle Plugin CI 4.5.11, Composer 2, `node` with `npm`/`npx`, the PostgreSQL client, and an empty reachable PostgreSQL database server. Generated plugin code is untrusted and grading must run on a disposable CI worker or container with no provider credentials and no sensitive writable mounts. The harness strips the inherited environment, uses a dedicated home and temporary directory, rejects candidate-owned grader control files, and terminates timed-out process groups. It creates a unique database name and fresh Moodle, Moodledata, and plugin trees for every run:

```bash
python3 -I -B tools/eval_harness.py grade \
    --run-dir "$run" \
    --plugin-ci /tmp/opencode/moodle-plugin-ci/bin/moodle-plugin-ci \
    --db-host 127.0.0.1 \
    --db-user postgres \
    --db-pass moodle
```

The grader runs no fixers. It executes PHP lint, coding style with zero warnings, plugin validation, PHPDoc with zero warnings, savepoints, and one exact PHPUnit method for every later declared check. The naming convention maps `check-id` to `harness_contract_test::test_check_id`. Every method runs even after an earlier behavioral failure. Missing prerequisites stay `incomplete`; installation failures are `error`; assertion and Plugin CI failures are `fail`.

The first-slice Docker runner provisions those tools together and starts a fresh digest-pinned PostgreSQL 17.11 server. It mounts the repository read-only, mounts only the external run directory writable, does not receive the host environment or provider credentials, and rejects `error` or `incomplete` grades:

```bash
tools/run_filter_grader.sh "$run"
python3 -I -B tools/eval_harness.py validate "$run"
```

Run generation on the host before invoking the disposable grader. The runner is intentionally limited to `filter-modern-contract`; it does not prepare or start another task grader.

The second runner is separately pinned to PHP 8.4.24, Moodle-compatible Node 22.11.0/npm 10.9.0, and PostgreSQL 17.11. It accepts only `qbank-bulk-action`, verifies the Moodle 5.2.2 revision and public plugin destination, and uses the same isolation controls:

```bash
run=/tmp/momopda-evals/qbank-fake-001
python3 -I -B tools/eval_harness.py prepare \
    --task qbank-bulk-action \
    --condition none \
    --output "$run"
python3 -I -B tools/eval_harness.py run \
    --run-dir "$run" \
    --client fake
tools/run_qbank_grader.sh "$run"
python3 -I -B tools/eval_harness.py validate "$run"
```

The third runner uses the same pinned Moodle 5.2.2/PHP 8.4/Node 22/PostgreSQL 17.11 boundary and accepts only `tiny-toolbar-button`. In addition to Plugin CI, it performs a clean component-scoped Grunt build in a disposable Moodle copy and executes the submitted AMD through a dependency-free Node shim to verify manager advertisement, synchronous registration after localization, `content` toolbar placement, command dispatch, and exact semantic insertion:

```bash
run=/tmp/momopda-evals/tiny-fake-001
python3 -I -B tools/eval_harness.py prepare \
    --task tiny-toolbar-button \
    --condition none \
    --output "$run"
python3 -I -B tools/eval_harness.py run \
    --run-dir "$run" \
    --client fake
tools/run_tiny_grader.sh "$run"
python3 -I -B tools/eval_harness.py validate "$run"
```

For deterministic grader development only, the fake client can apply an external overlay with `--fake-overlay /outside/repository/overlay`. The harness rejects repository-contained overlays and rejects this option for OpenCode, so an external known-good implementation or mutation is never exposed to a model request.

Moodle 5.2's web root is `public/`, including the plugin destinations `public/question/bank/momopda` and `public/lib/editor/tiny/plugins/momopda`. Non-web CLI scripts remain at the checkout root, so site installation uses `admin/cli/install_database.php`. Moodle URLs and AMD module names never include `/public`.

Run records conform to `public/run-result.schema.json`. Event, stderr, grader, and tool logs remain outside the agent workspace. Summaries consume saved records only and do not rank skill conditions from a single sample.
