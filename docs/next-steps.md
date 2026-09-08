# Next Implementation Steps

This document is the context-clear handoff for the modernization work started on 19 August 2026.

## Repository State

- Branch: `feature/agent-skills-conversion`.
- The commit containing this handoff completes the Immediate Milestone and the `qbank-bulk-action` second public slice.
- The expected worktree after that commit is clean. Inspect `git status` before editing, preserve any later user changes, and do not reset or overwrite them.
- The completed milestone commit has not been pushed. Do not add moving-branch or Moodle `main` canaries until the hosted pinned boundary jobs are green.
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

The harness suite has 16 passing tests. All nine canonical fixtures retain their prior Moodle Plugin CI 4.5.11 `phplint`, zero-warning `codechecker`, and `savepoints` proof. Both public grader assertions pass PHP lint and zero-warning Moodle PHPCS in their disposable boundary. Docker actionlint 1.7.12 passes all workflows.

The first-slice proof gap was closed on 30 August 2026. `tools/filter-grader.Dockerfile` and `tools/run_filter_grader.sh` provide a repeatable amd64 worker with digest-pinned PHP 8.1, Composer 2, Node.js 22.11.0 with `npm`/`npx`, Git, PostgreSQL client 15.19, Moodle Plugin CI 4.5.11, and a fresh digest-pinned PostgreSQL 17.11 server. The repository is mounted read-only, only the external run root is bind-mounted writable, Plugin CI runtime state uses container-only tmpfs, and the worker receives no provider credentials.

A deterministic fake-client run reached all five Plugin CI commands and both exact Moodle PHPUnit methods, then ended `fail` rather than `error` or `incomplete`. Both installation phases passed and the logs identified Moodle `v4.5.13` at `8cbae18a2898cfd8266ec91ac206e12004f0ff5f` and PostgreSQL 17.11.

The small non-ranked baseline cohort used explicit `openai/gpt-5.6-sol` runs with OpenCode 1.18.25 in three separate run roots. Candidate and released discovery each found one isolated MoMoPDA skill; no-skill discovery found zero. The released condition used the explicit detached `acb41db4cb49f436f56faae95eb90b659428c704` skill artifact, not the candidate path. All three records validated and ended `fail`: Plugin CI and the modern filter contract passed, while the hostile localized replacement remained unescaped. The derived summary contained one candidate failure, one released failure, one no-skill failure, and `ranking: null`.

Concise logs, generated workspaces, pinned Moodle trees, event streams, run records, and the summary remained outside the repository.

## Filter Grader Command

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

## Completed Immediate Acceptance

- A first-slice grade reached every declared check and ended `fail`, not `error` or `incomplete`.
- The Moodle checkout was exactly `v4.5.13` at `8cbae18a2898cfd8266ec91ac206e12004f0ff5f`.
- Each run used unique mutable Moodledata and database state.
- Candidate, released, and no-skill discovery remained isolated.
- Every saved record validated and the summary reported statuses without ranking.
- No credentials, reasoning text, grader implementation, or exemplar reached the generating agent or saved events.
- `tools/validate_repo.py`, the harness tests, fixture checks, actionlint, and `git diff --check` remained green.

## Completed Second Slice

`qbank-bulk-action` is now the second public vertical slice on pinned Moodle 5.2.2. No third grader, repeated comparison campaign, private holdout, moving-branch canary, or real-model sample was started.

### Contract Freeze

The contract was frozen on 6 September 2026 after inspecting Moodle `v5.2.2` at `acfa383c13dd46c83ca82894a8e95fac273fda33`.

The deterministic contract is:

> Add a `qbank/momopda:use`-gated bulk action that marks selected question versions as draft after confirmation and returns safely to the originating question bank.

The ordered public checks are:

```json
[
  "plugin-ci",
  "sesskey",
  "context-capability",
  "per-question-capability",
  "confirmation",
  "safe-return"
]
```

Pinned core confirms that bulk actions receive the 5.2 question-bank view, the form posts `sesskey` and `q{questionid}` inputs, and action capabilities are any-of menu-advertising checks rather than endpoint authorization. Question status uses the stable `draft` value in `question_versions`; core invalidates the edited question cache and emits `question_updated` after a status change. Question banks are resolved from `cmid` to module context. `PARAM_LOCALURL` rejects external and cross-host absolute URLs but accepts root-relative values, so endpoints must additionally reject protocol-relative input and use a server-built local fallback. The task prompt and ordered six-check list in `evals/public/tasks.json` now state every required behavior. The mutation is deterministic, reversible under PHPUnit reset, and directly observable through Moodle database state. Moodle 5.2.2 also confirms that `public/` is the web root while non-web CLI scripts remain below the checkout root; database installation therefore uses `moodle/admin/cli/install_database.php`, not the nonexistent `moodle/public/admin/cli/install_database.php` assumed by the earlier handoff.

### Fixture Invariant

- The task continues to start from the complete unsolved `skills/moodle-plugin-development/assets/fixtures/qbank_momopda` fixture; it has no setup overlay.
- `classes/plugin_feature.php` registers only `question_id_column`; there is no bulk action, capability, endpoint, mutation service, confirmation flow, or qbank test.
- The fixture must remain unsolved. Generated candidates, not the canonical asset, implement the task.
- Moodle 5.2.2 uses PHP 8.4 and a `public/` application root. The plugin filesystem destination is `public/question/bank/momopda`, while Moodle URLs remain `/question/bank/momopda/...` and never include `/public`.
- The grader registry contains exactly `filter-modern-contract` and `qbank-bulk-action`.

### Pinned Source Evidence

The following contracts were inspected in the exact Moodle checkout:

- `public/question/classes/local/bank/view_component.php`
- `public/question/classes/local/bank/bulk_action_base.php`
- `public/question/classes/local/bank/plugin_features_base.php`
- `public/question/classes/local/bank/view.php`
- `public/question/templates/bulk_actions_ui.mustache`
- `public/question/bank/bulkmove/classes/plugin_feature.php`
- `public/question/bank/deletequestion/delete.php`
- `public/question/bank/editquestion/classes/external/update_question_version_status.php`
- `public/lib/questionlib.php`, especially `question_require_capability_on()`
- `public/lib/sessionlib.php`, especially sesskey validation
- Core question and `mod_qbank` generators and their PHPUnit tests

This inspection confirmed the bulk-action constructor, registration method, checkbox/form parameter names, advertised capability semantics, confirmation flow, question-version status update behavior, cache invalidation/event expectations, and local-return handling. Moodle's package metadata requires Node `>=22.11.0 <23`; the worker pins Node 22.11.0 and npm 10.9.0.

`skills/moodle-plugin-development/references/type-qbank.md`, `skills/moodle-plugin-development/references/security.md`, and `knowledge/sources.json` now contain only general, source-backed guidance. The canonical skill does not contain grader details or an exemplar solution.

### Harness Refactor

The harness was generalized only where required for the second registered grader:

1. Assertion files resolve from the selected closed, versioned `graders.json` entry, and all registered assertions contribute to the harness artifact hash.
2. The web application root derives from boundary layout, while source-verified non-web CLI scripts remain at the checkout root and Plugin CI continues to receive that root.
3. Every non-Plugin-CI check dispatches to exactly `test_<check-id-with-underscores>` and runs even after earlier behavioral failures.
4. A pass requires one executed test, at least one assertion, no duplicate success summary, and no skipped, incomplete, risky, warning, timeout, or failing result; assertion counts are not task-hard-coded.
5. Installation and toolchain failures remain `error` or `incomplete`, while Plugin CI and assertion failures remain `fail`.
6. Candidate-owned Plugin CI and PHPUnit control files are rejected recursively before installation, independent of task.

The refactor was covered offline before qbank registration. A fresh disposable filter run on Moodle 4.5.13/PHP 8.1 subsequently reached all three checks and ended `fail`, preserving the first-slice status semantics.

### Qbank Grader

`evals/public/graders/qbank-bulk-action/harness_contract_test.php` discovers the generated action through `plugin_feature` and a real Moodle 5.2 question-bank view, then resolves and executes the candidate endpoint from the action URL without assuming a candidate helper class.

The grader establishes these executable outcomes:

- `plugin-ci`: non-fixing `phplint`, zero-warning `codechecker`, `validate`, zero-warning `phpdoc`, and `savepoints` all run.
- `sesskey`: initial selection and final mutation use POST; missing or invalid sesskeys cannot mutate; final execution revalidates the sesskey.
- `context-capability`: the action declares and advertises `qbank/momopda:use` at the correct activity-backed bank context; a user with question-edit permission but without the action capability cannot mutate; IDs from another bank cannot be smuggled through the origin context.
- `per-question-capability`: every selected question is reauthorized at final execution. Test `editmine` versus `editall`, mixed ownership, permission changes between confirmation and execution, and all-or-nothing behavior with no partial update.
- `confirmation`: the first valid POST displays an explicit confirmation for the selected questions without changing state; cancel and malformed confirmation do not mutate; a distinct valid confirmation changes exactly the selected versions to draft and leaves an unselected control unchanged.
- `safe-return`: valid local origin state is preserved; external, protocol-relative, malformed, cross-host, and empty targets are rejected or replaced with a server-built local fallback; success and cancellation both use the safe target; `/public` never appears in generated URLs; hostile return input is not rendered unsafely.

Endpoint requests execute in-process with simulated GET/POST globals. A grading-only hook in the disposable Moodle tree converts `redirect()` termination into a captured target under PHPUnit, allowing success and cancellation destinations to be asserted. The source given to a generating agent remains pristine, and no security outcome relies on source-string matching.

### Disposable Moodle 5.2 Runner

`tools/qbank-grader.Dockerfile` and `tools/run_qbank_grader.sh` provide a qbank-only worker rather than broadening the filter runner.

The worker provides digest-pinned PHP 8.4.24, Composer 2, Node 22.11.0 with npm/npx 10.9.0, Git, PostgreSQL client 15.19, Python 3.11, Moodle Plugin CI 4.5.11, and a fresh digest-pinned PostgreSQL 17.11 server. It uses a read-only repository mount, one writable external run mount, container-only tmpfs state, no inherited provider credentials, dropped capabilities, `no-new-privileges`, cleanup traps, and terminal enforcement that every declared check ends `pass` or `fail`.

The runner must reject tasks other than `qbank-bulk-action`. It must verify Moodle `v5.2.2`, commit `acfa383c13dd46c83ca82894a8e95fac273fda33`, PHP 8.4, PostgreSQL 17.11, the source-verified checkout-root CLI installer path, the `public/` web root, and the plugin's physical destination before accepting a run as evidence.

### Deterministic Proof

All deterministic artifacts are below `/tmp/opencode/momopda-qbank-milestone-20260906`, outside this repository. Generated grading trees were removed after proof; validated records and concise logs remain.

- `qbank-fake-final`: the unchanged fixture reached all six checks and ended `fail`.
- `qbank-known-good-final`: the external known-good implementation passed Plugin CI and all five behavioral checks.
- Nine external security mutations each ended `fail` on the intended check while every later behavioral method executed: missing sesskey, menu-only capability enforcement, missing final reauthorization, mixed-owner partial update, pre-confirmation mutation, GET mutation, cross-bank IDs, unsafe return, and `/public` URL construction.
- `filter-regression-final`: the unchanged filter fake fixture reached all checks and ended `fail` on Moodle 4.5.13/PHP 8.1.
- `deterministic-summary.json`: 12 records, one pass, 11 expected failures, zero errors, zero incomplete runs, zero timeouts, and `ranking: null`.
- No real-model sample was run. Deterministic gates now permit a future explicit sampling decision, but sampling remains out of scope for this completed slice.

### Completed Acceptance

- The task has one deterministic observable mutation and every promised property has a declared executable check.
- `graders.json` has exactly two mappings, with ordered checks exactly matching their tasks.
- The filter slice remains regression-free on Moodle 4.5/PHP 8.1.
- The qbank worker uses only Moodle 5.2.2 at `acfa383c13dd46c83ca82894a8e95fac273fda33`, PHP 8.4, PostgreSQL 17.11, and unique Moodledata/database state.
- The unchanged fake fixture reaches all checks, the external known-good implementation passes all checks, and every targeted security mutation is discriminated by runtime behavior.
- Public-layout filesystem paths and URL paths are tested independently; generated URLs never include `/public`.
- Saved records validate, and errors, incomplete prerequisites, behavioral failures, generation timeouts, and test failures remain distinct.
- Generated workspaces, Moodle trees, records, logs, exemplars, and mutation candidates remain outside the repository.
- No provider credentials, hidden reasoning, grader implementation, or exemplar reached a generating agent.
- `tools/validate_repo.py`, all 16 harness tests, both grader PHP lints, both runner shell syntax checks, Docker actionlint 1.7.12, and `git diff --check` pass on the resulting tree.

### Scope Guard

No grader was implemented, registered, tested, or containerized for `tiny-toolbar-button`, `activity-schema-upgrade`, `local-external-function`, `qtype-safe-rendering`, `report-portable-query`, or `enrol-instance-ui`.

## Next Milestone

Implement `tiny-toolbar-button` as the third and only next public vertical slice on pinned Moodle 5.2.2. Do not start a fourth grader, repeated comparison campaign, private holdout, moving-branch canary, or real-model sample in this slice.

### Contract Freeze

The current prompt says "fixed semantic element" without defining the element, markup, selection behavior, button identity, toolbar placement, or language-string key. It also promises insertion behavior while the declared checks omit it. Do not write a grader against that ambiguity.

Use this recommended deterministic contract unless exact pinned source disproves it:

> Add a `tiny_momopda` TinyMCE toolbar button, advertise it as `tiny_momopda/tiny_momopda`, place it in the `content` toolbar section, and localize its tooltip through `tiny_momopda/buttontitle`. Activating the button must execute the `mceMomopdaInsertMarker` command, which uses `editor.insertContent()` to insert exactly `<mark class="tiny_momopda-marker">MoMoPDA</mark>` at the current selection.

Change the ordered public checks to:

```json
[
  "plugin-ci",
  "amd-build",
  "plugin-manager-registration",
  "localized-tooltip",
  "semantic-insertion"
]
```

The first implementation step is to verify and record this contract against Moodle `v5.2.2` at `acfa383c13dd46c83ca82894a8e95fac273fda33`. The exact static `mark` element makes the result language-neutral, deterministic, safe from selected-content interpolation, and observable through the built AMD module and TinyMCE DOM. Every behavior promised by the frozen prompt must map to one declared check.

### Starting State

- The task starts from the complete unsolved `skills/moodle-plugin-development/assets/fixtures/tiny_momopda` fixture and has no setup overlay.
- `classes/plugininfo.php` extends `editor_tiny\plugin` but implements no feature interface. It does not advertise a button.
- `amd/src/plugin.js` registers only the plugin metadata callback. It has no button, command, toolbar configuration, localization, or insertion behavior.
- The fixture already declares `tiny/momopda:use` and ships matching loader-only `plugin.min.js` and source-map artifacts.
- The fixture must remain unsolved. Generated candidates, not the canonical asset, implement the task.
- Moodle 5.2.2 uses TinyMCE 8.2.2, Node `>=22.11.0 <23`, PHP 8.4, and the `public/` web root. The physical destination is `public/lib/editor/tiny/plugins/momopda`; Moodle module names and URLs never include `/public`.
- The final grader registry for this slice must contain exactly `filter-modern-contract`, `qbank-bulk-action`, and `tiny-toolbar-button`.

### Pinned Source Work

Inspect these exact contracts before changing task guidance or grader code:

- `public/lib/editor/tiny/classes/plugin.php`
- `public/lib/editor/tiny/classes/plugin_with_buttons.php`
- `public/lib/editor/tiny/classes/manager.php`
- `public/lib/editor/tiny/amd/src/editor.js`
- `public/lib/editor/tiny/amd/src/utils.js`
- `public/lib/editor/tiny/plugins/noautolink/classes/plugininfo.php`
- `public/lib/editor/tiny/plugins/noautolink/amd/src/common.js`
- `public/lib/editor/tiny/plugins/noautolink/amd/src/commands.js`
- `public/lib/editor/tiny/plugins/noautolink/amd/src/configuration.js`
- `public/lib/editor/tiny/plugins/noautolink/amd/src/plugin.js`
- `public/lib/editor/tiny/plugins/accessibilitychecker/amd/src/commands.js`
- `public/lib/editor/tiny/plugins/equation/amd/src/equation.js`
- `public/lib/amd/src/str.js`
- `.grunt/tasks/javascript.js`
- `.grunt/babel-plugin-add-module-to-define.js`
- `package.json`, `npm-shrinkwrap.json`, and `.nvmrc`
- The shipped TinyMCE 8.2.2 `editor.insertContent()` and deprecated `selection.setContent()` implementations

Confirm the PHP button interface, real manager configuration shape, AMD default-export promise shape, synchronous `PluginManager.add()` callback, asynchronous string loading boundary, toolbar configuration API, command/button APIs, supported insertion method, build output/module naming, source-map expectations, and exact Node/npm versions. Core `tiny_noautolink` is the closest registration model, but its use of deprecated `selection.setContent()` must not be copied; TinyMCE 8 directs new code to `editor.insertContent()`.

Update `skills/moodle-plugin-development/references/type-tiny.md`, `skills/moodle-plugin-development/references/frontend.md`, and `knowledge/sources.json` only with general source-backed guidance. Cover the PHP button interface, module promise tuple, pre-registration localization, configuration-based toolbar placement, supported insertion API, build/source-map freshness, and `public/` filesystem distinction. Do not add grader details, the frozen marker markup, or an exemplar solution to the skill.

### Harness Boundary

Keep the existing generic grader architecture. The registry already selects and hashes each assertion, layout handling already supports Moodle 5.2, and each non-Plugin-CI check already maps to one exact PHPUnit method. Make only changes concretely required by executable Tiny grading:

1. Add `node` to grading prerequisite detection because Tiny checks execute built JavaScript directly.
2. Update the repository validator and offline registry expectation from exactly two graders to exactly three only when the Tiny assertion is ready to register.
3. Keep the result schema, filter grader, qbank grader, and existing runners unchanged unless a reproduced regression requires a minimal fix.
4. Run every Tiny check after earlier failures and preserve `error`, `incomplete`, `fail`, and timeout semantics.
5. Continue rejecting candidate-owned Plugin CI/PHPUnit controls before installation and never expose the assertion or JavaScript probe to the generating agent.

Adding the third assertion changes the global harness artifact hash. Prepare fresh external proof runs after registration; do not reuse records prepared against the two-grader artifact.

### Tiny Grader

Add `evals/public/graders/tiny-toolbar-button/harness_contract_test.php`, then and only then register `tiny-toolbar-button`. Its exact methods are `test_amd_build`, `test_plugin_manager_registration`, `test_localized_tooltip`, and `test_semantic_insertion`.

The grader must establish these executable outcomes:

- `plugin-ci`: non-fixing `phplint`, zero-warning `codechecker`, `validate`, zero-warning `phpdoc`, and `savepoints` all run.
- `amd-build`: every AMD source has shipped `.min.js` and `.min.js.map` artifacts; a clean component-scoped Grunt build on a disposable copy passes with zero warnings and reproduces the submitted build and source maps without fixing the candidate workspace in place.
- `plugin-manager-registration`: `plugininfo` implements `plugin_with_buttons`, advertises exactly `tiny_momopda/tiny_momopda`, and a real Moodle manager configuration exposes it. Execute the submitted built AMD through a dependency-free Node `vm`/AMD shim; its promise must register `tiny_momopda/plugin`, register exactly one `tiny_momopda` button, and return configuration that adds it to the `content` toolbar.
- `localized-tooltip`: inject a sentinel translation through a mocked `core/str` dependency, prove string loading settles before synchronous plugin registration, and prove the button tooltip equals the sentinel rather than a hard-coded English value.
- `semantic-insertion`: execute the built module's registered command and button action against a fake editor, prove the action calls the named command, and prove the command calls `editor.insertContent()` exactly once with the frozen `mark` element. Where practical, add a credential-free local browser assertion against shipped TinyMCE 8.2.2 for collapsed and ranged selections; do not substitute source-string matching for runtime behavior.

Prototype execution of the built AMD artifacts before finalizing the assertion. The probe must support a candidate's valid single-file or modular AMD design and discover behavior through the declared PHP button and built plugin module rather than assuming candidate helper filenames. If a browser check is required, use only a local disposable page, shipped TinyMCE, and a pinned browser; no Moodle credentials or network service may be required.

### Disposable Moodle 5.2 Runner

Add a separate `tools/tiny-grader.Dockerfile` and `tools/run_tiny_grader.sh`. Do not weaken the task guards in the filter or qbank runners.

The worker must provide digest-pinned PHP 8.4, Composer 2, Node 22.11.0 with npm/npx 10.9.0, Git, PostgreSQL client 15.19, Python, Moodle Plugin CI 4.5.11, and a fresh digest-pinned PostgreSQL 17.11 server. Reuse the established isolation model: read-only repository mount, only the external run root writable, container-only tmpfs state, no provider credentials, dropped capabilities, `no-new-privileges`, cleanup traps, and terminal enforcement that every declared check ends `pass` or `fail`.

The runner must reject tasks other than `tiny-toolbar-button` and verify Moodle `v5.2.2`, commit `acfa383c13dd46c83ca82894a8e95fac273fda33`, PHP 8.4, Node/npm versions, PostgreSQL 17.11, the checkout-root CLI installer, the `public/` web root, and physical plugin destination before accepting a run as evidence.

### Ordered Delivery

1. Freeze the exact button, command, toolbar section, language key, markup, selection behavior, and five-check task contract.
2. Reinspect pinned Moodle/TinyMCE evidence and update only general source guidance.
3. Prototype a dependency-free runtime probe against the unchanged fixture and an external implementation before coupling it to PHPUnit.
4. Add only the Node prerequisite and three-grader validation changes needed by this slice; keep filter and qbank offline behavior green.
5. Add the Tiny assertion and only then register `tiny-toolbar-button` as the third grader.
6. Add the Tiny-only disposable worker and prove the unchanged fake fixture reaches every check and ends `pass` or `fail`, never infrastructure `error` or prerequisite `incomplete`.
7. Build a known-good implementation outside the repository and prove all checks pass.
8. Run external mutations for stale or missing builds/maps, PHP-only advertisement, plugin-only registration, missing toolbar placement, hard-coded tooltip, missing/wrong command dispatch, deprecated or absent insertion, and wrong markup. Each mutation must fail its intended check while later checks still execute.
9. Re-run fresh filter and qbank disposable fake regressions after the global artifact hash changes.
10. Update offline tests, repository validation, evaluation documentation, and this handoff; run final verification from the resulting tree.

Do not run real-model candidate/released/no-skill samples until the unchanged fixture produces a real `pass`/`fail`, the known-good external implementation passes, and the mutation suite demonstrates discrimination. Model sampling remains optional and requires a separate explicit decision after deterministic proof; never rank a single sample.

### Acceptance

- The task has one exact semantic insertion and every prompt promise has a declared executable check.
- `graders.json` contains exactly three mappings with ordered checks matching their tasks.
- The canonical Tiny fixture remains unsolved and unchanged.
- The worker uses only the pinned Moodle 5.2.2/PHP 8.4/Node 22/PostgreSQL 17.11 boundary with fresh mutable state.
- The unchanged fixture reaches every check, the external known-good implementation passes, and each targeted mutation fails the intended runtime/build check.
- Submitted built AMD, not source alone, drives registration, localization, toolbar, command, and insertion assertions.
- Grunt proves distributable source/build/source-map consistency without modifying the candidate workspace.
- Filter and qbank slices remain regression-free with unchanged status semantics.
- Generated workspaces, Moodle trees, records, logs, probes, browser state, exemplars, and mutation candidates remain outside the repository.
- No credentials, hidden reasoning, grader implementation, or exemplar reaches a generating agent.
- No fourth grader or real-model campaign is started.

### Scope Guard

Do not implement, register, test, or containerize graders for `activity-schema-upgrade`, `local-external-function`, `qtype-safe-rendering`, `report-portable-query`, or `enrol-instance-ui` in this milestone.

## Later Milestones

1. Implement deterministic graders for the remaining five public tasks, one vertical slice at a time.
2. Run repeated candidate/released/no-skill comparisons without ranking single samples.
3. Create the separate private holdout repository for hidden prompts, tests, expected outcomes, and mutation cases.
4. Add source-path change tracking for selected Moodle contracts.
5. Add non-blocking moving-branch and Moodle `main` canaries only after hosted pinned jobs are green.
6. Test a release artifact in current OpenCode and Claude Code releases.

## Invariants

- Keep one canonical skill and do not reintroduce inter-skill dependencies.
- Keep examples executable and validation non-fixing.
- Report skipped functional checks as incomplete, never successful.
- Use pinned Moodle source and executable tests before prose or text matching.
- Keep the 4.5/5.x physical path difference explicit; URLs never gain `/public`.
- Keep generation, grading, records, and summaries separable.
- Keep private holdout material outside this repository.
- Never expose credentials, hidden reasoning, or grader material to the generating agent.

## Context-Reset Prompt

Use this prompt after clearing context:

> Read `docs/next-steps.md` and implement the `tiny-toolbar-button` Next Milestone only. Inspect the worktree before editing and preserve any user changes. First freeze one deterministic Moodle 5.2.2/TinyMCE 8.2.2 contract using the recommended `tiny_momopda` content-toolbar button, localized `buttontitle`, `mceMomopdaInsertMarker` command, and exact `<mark class="tiny_momopda-marker">MoMoPDA</mark>` insertion unless pinned source disproves it; add an explicit `semantic-insertion` check so every prompt promise is graded. Keep the generic filter/qbank harness behavior stable, then build executable shipped-AMD build, manager/toolbar registration, localized-tooltip, command, and insertion checks in a credential-free PHP 8.4/Node 22/PostgreSQL 17.11 disposable worker. Register no fourth grader. Do not run real-model samples until the unchanged fixture returns a real pass/fail, an external known-good implementation passes, and targeted build/runtime mutations fail as intended. Keep generated workspaces, Moodle trees, records, logs, probes, browser state, exemplars, and mutation candidates outside the repository, and carry the work through regression validation and an updated handoff.
