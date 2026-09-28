# Modernization History

Detailed record of completed modernization milestones, moved from `docs/next-steps.md` on 28 September 2026. Proof artifacts referenced below live outside the repository.

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

## Completed Third Slice

`tiny-toolbar-button` is now the third public vertical slice on pinned Moodle 5.2.2. No fourth grader, repeated comparison campaign, private holdout, moving-branch canary, or real-model sample was started.

### Contract Freeze

The contract was frozen on 18 September 2026 after inspecting Moodle `v5.2.2` at `acfa383c13dd46c83ca82894a8e95fac273fda33` and its shipped TinyMCE 8.2.2 source:

> Add a `tiny_momopda` TinyMCE toolbar button, advertise it as `tiny_momopda/tiny_momopda`, place it in the `content` toolbar section, and localize its tooltip through `tiny_momopda/buttontitle`. Activating the button must execute the `mceMomopdaInsertMarker` command, which uses `editor.insertContent()` to insert exactly `<mark class="tiny_momopda-marker">MoMoPDA</mark>` at the current selection.

The ordered public checks are:

```json
[
  "plugin-ci",
  "amd-build",
  "plugin-manager-registration",
  "localized-tooltip",
  "semantic-insertion"
]
```

Every behavior promised by the prompt maps to an executable check. The static marker is language-neutral, does not interpolate selected content, and is tested through the submitted AMD rather than source matching.

### Pinned Source Evidence

The following exact contracts were inspected in the pinned checkout:

- `public/lib/editor/tiny/classes/plugin.php` and `plugin_with_buttons.php`
- `public/lib/editor/tiny/classes/manager.php`
- `public/lib/editor/tiny/amd/src/editor.js` and `utils.js`
- `public/lib/editor/tiny/plugins/noautolink` PHP and AMD registration files
- `public/lib/editor/tiny/plugins/accessibilitychecker/amd/src/commands.js`
- `public/lib/editor/tiny/plugins/equation/amd/src/equation.js`
- `public/lib/amd/src/str.js`
- `.grunt/tasks/javascript.js` and `.grunt/babel-plugin-add-module-to-define.js`
- `package.json`, `npm-shrinkwrap.json`, and `.nvmrc`
- Shipped TinyMCE 8.2.2 insertion code and its `selection.setContent()` deprecation warning

This confirmed manager discovery through `plugin_with_buttons`, fully qualified PHP button identifiers, the default-export promise and optional configuration tuple, synchronous `PluginManager.add()` registration after asynchronous dependencies settle, named toolbar configuration, command/button APIs, generated AMD names, source-map output, Node `>=22.11.0 <23`, and `editor.insertContent()` as the supported insertion API.

`skills/moodle-plugin-development/references/type-tiny.md`, `skills/moodle-plugin-development/references/frontend.md`, and `knowledge/sources.json` contain only general source-backed guidance. They do not contain the frozen marker, grader internals, or an exemplar.

### Fixture And Harness

- The complete canonical `tiny_momopda` fixture remains loader-only and unchanged. It has no button interface, button, toolbar configuration, localized tooltip, command, or insertion behavior.
- The task prompt now states the exact button, advertised identifier, toolbar section, language key, command, API, markup, and selection behavior.
- `semantic-insertion` is the fifth explicit check.
- `node` is now a generic grading prerequisite; result schemas, dispatch, status semantics, filter/qbank assertions, and existing runners are unchanged.
- The repository validator and offline hash test expect exactly three closed, versioned grader mappings.
- The Tiny assertion was added before registry activation, so every fresh run hashes all three assertions.

### Tiny Grader

`evals/public/graders/tiny-toolbar-button/harness_contract_test.php` implements four exact PHPUnit methods:

- `test_amd_build` requires one `.min.js` and `.min.js.map` per source, performs a clean component-scoped Grunt build in a disposable shared clone, and byte-compares the entire generated build tree without modifying the candidate workspace.
- `test_plugin_manager_registration` checks `plugin_with_buttons`, exact PHP advertisement, and a real manager configuration. It then executes the submitted built module with a dependency-free Node `vm`/AMD loader that supports single-file and modular plugin designs, verifies one `tiny_momopda/plugin` registration and one regular button, and applies returned configuration to a real-shaped `content` toolbar.
- `test_localized_tooltip` verifies the language key, delays only a mocked `tiny_momopda/buttontitle` sentinel, proves registration waits for it, and checks the submitted button tooltip.
- `test_semantic_insertion` invokes the registered command with collapsed and ranged selection states, invokes the button action, requires exact `mceMomopdaInsertMarker` dispatch, rejects `selection.setContent()`, and requires one exact `editor.insertContent()` call with the frozen marker.

The runtime tests discover behavior from `tiny_momopda/plugin` and PHP advertisement; they do not assume candidate helper filenames or inspect source strings.

### Disposable Worker

`tools/tiny-grader.Dockerfile` and `tools/run_tiny_grader.sh` provide a Tiny-only worker with digest-pinned PHP 8.4.24, Composer 2, Node 22.11.0/npm 10.9.0, PostgreSQL client 15.19, Python 3.11, Moodle Plugin CI 4.5.11, and a fresh digest-pinned PostgreSQL 17.11 server.

The runner accepts only `tiny-toolbar-button`; verifies the exact task boundary, Moodle tag and commit, PHP, Node/npm, PostgreSQL, checkout-root CLI installer, `public/` web root, and `public/lib/editor/tiny/plugins/momopda` destination; mounts the repository read-only and only the external run root writable; uses container tmpfs; receives no provider credentials; drops all capabilities; sets `no-new-privileges`; and accepts only terminal `pass` or `fail` checks.

### Deterministic Proof

All proof artifacts are under `/tmp/opencode/momopda-tiny-milestone-20260918`, outside the repository. Disposable grading trees were removed after validation; concise logs, records, external overlays, probes, and the summary remain outside the repository.

- `tiny-fixture-verified`: the unchanged fixture passed Plugin CI and reproducible AMD build checks, reached all five checks, and ended `fail` on the three missing runtime behaviors.
- `tiny-known-good-verified`: an external known-good implementation passed Plugin CI and all four behavioral/build checks.
- `mutation-stale-source-build-verified` and `mutation-missing-map-verified` failed only `amd-build`; all submitted-AMD runtime checks still passed.
- `mutation-php-only-advertisement-verified` and `mutation-plugin-only-registration-verified` discriminated missing AMD behavior and missing PHP manager advertisement respectively.
- `mutation-missing-toolbar-placement-verified` failed only `plugin-manager-registration`.
- `mutation-hard-coded-tooltip-verified` failed only `localized-tooltip`.
- `mutation-missing-command-dispatch-verified`, `mutation-deprecated-insertion-verified`, and `mutation-wrong-markup-verified` failed only `semantic-insertion`.
- `filter-regression-verified` and `qbank-regression-verified` used fresh runs against the three-grader artifact, reached every declared check, and retained terminal `fail` semantics on Moodle 4.5.13/PHP 8.1 and Moodle 5.2.2/PHP 8.4 respectively.
- `deterministic-summary.json`: 13 records, one pass, 12 expected failures, zero errors, zero incomplete runs, zero timeouts, and `ranking: null`.
- No real-model sample was run.

### Completed Acceptance

- `graders.json` contains exactly `filter-modern-contract`, `qbank-bulk-action`, and `tiny-toolbar-button`, with ordered checks matching their tasks.
- Submitted built AMD drives registration, localization, toolbar, command, and insertion assertions.
- Grunt proves source/build/source-map freshness in a disposable copy.
- The canonical Tiny fixture is unchanged and unsolved.
- The worker uses only the pinned Moodle 5.2.2/PHP 8.4/Node 22/PostgreSQL 17.11 boundary with unique mutable Moodledata and database state.
- The fixture returns real `pass`/`fail` outcomes, the external known-good passes, and each targeted mutation is discriminated while later methods execute.
- Filter and qbank behavior remains stable after the global artifact hash changed.
- Generated workspaces, Moodle trees, records, logs, probes, exemplars, browser state, and mutations remain outside the repository.
- No credentials, hidden reasoning, assertion, probe, or exemplar reached a generating agent.
- No fourth grader or model campaign was started.

### Scope Guard

No grader was implemented, registered, tested, or containerized for `activity-schema-upgrade`, `local-external-function`, `qtype-safe-rendering`, `report-portable-query`, or `enrol-instance-ui`.

## Completed Fourth Slice

`activity-schema-upgrade` is now the fourth public vertical slice on pinned Moodle 4.5.13. No fifth grader, repeated comparison campaign, private holdout, moving-branch canary, or real-model sample was started.

### Contract Freeze

The contract was frozen on 24 September 2026 after inspecting Moodle `v4.5.13` at `8cbae18a2898cfd8266ec91ac206e12004f0ff5f`:

> Add a required per-instance `mode` setting to `mod_momopda`. Localize it through `mod_momopda/mode`, `mod_momopda/modestandard`, and `mod_momopda/modeguided`. Display it as a required select containing exactly Standard (`1`) and Guided (`2`), with no empty option and Standard selected by default. Persist submitted values when an activity is added or updated. On fresh installations, define `momopda.mode` as an integer of length 1, `NOT NULL`, with database default `1`. Upgrade from plugin version `2026081900` to exactly `2026081901` by adding the same field only when absent so every existing activity receives `1`, then call `upgrade_mod_savepoint(true, 2026081901, 'momopda')`. This setting does not require view changes.

The ordered public checks remain:

```json
[
  "plugin-ci",
  "fresh-install",
  "upgrade-install",
  "savepoint"
]
```

Every prompt promise maps to executable behavior. The unchanged fixture stays at version `2026081900`, has no `mode` field or upgrade file, and remains the unsolved generation input.

### Pinned Source Evidence

The exact 4.5.13 contracts inspected were:

- `lib/upgradelib.php`, including fresh module installation, module upgrade dispatch, and `upgrade_mod_savepoint()`
- `lib/ddl/database_manager.php` and `lib/ddl/tests/ddl_test.php` for required-field defaults and existing-row backfill
- `lib/classes/plugininfo/base.php` for disk/database version status
- `course/moodleform_mod.php` and `course/modlib.php` for form data and add/update dispatch
- `mod/page/mod_form.php` and `mod/page/lib.php` for stored activity settings
- `mod/bigbluebuttonbn/db/upgrade.php` for a guarded required integer field and module savepoint

This confirms that a fresh install reads `db/install.xml` without running `db/upgrade.php`, a required field added to a populated table needs a real default, module rows feed matching edit-form controls, add/update callbacks receive submitted data, and a plugin savepoint stores the component database version. `skills/moodle-plugin-development/references/type-activity.md`, `skills/moodle-plugin-development/references/database.md`, and `knowledge/sources.json` now contain only general source-backed guidance.

### Grader And Isolation

`evals/public/graders/activity-schema-upgrade/harness_contract_test.php` implements three exact PHPUnit methods:

- `test_fresh_install` compares the submitted XMLDB definition with the installed PostgreSQL column, verifies the exact localized required select, default, option filtering and parameter type, checks disk/database version `2026081901`, and exercises add/update persistence.
- `test_upgrade_install` drops the fresh field, inserts an exact old-schema row, sets component version `2026081900`, verifies `PLUGIN_STATUS_UPGRADE`, invokes the submitted upgrade, then checks the field definition, default backfill, and preservation of existing data.
- `test_savepoint` invokes the submitted upgrade with the field already present and the database version reset to `2026081900`, proving both field-existence guarding and the plugin's own exact `mod_momopda` savepoint.

PHPUnit discovers all component tests before applying a method filter. The activity fixture's shared integration test therefore exposed a generic isolation gap: it references fixtures absent from a single-plugin grade. After all non-fixing Plugin CI commands run against the complete candidate, the harness now replaces candidate test trees in both grading copies with only the selected public assertion. An offline test proves this boundary, and all four registered graders use it.

### Disposable Worker

`tools/activity-grader.Dockerfile` and `tools/run_activity_grader.sh` provide an activity-only worker with digest-pinned PHP 8.1, Composer 2, Node 22.11.0/npm 10.9.0, PostgreSQL client 15.19, Python 3.11, Moodle Plugin CI 4.5.11, and a fresh digest-pinned PostgreSQL 17.11 server.

The runner accepts only `activity-schema-upgrade`; verifies Moodle `v4.5.13`, commit `8cbae18a2898cfd8266ec91ac206e12004f0ff5f`, PHP 8.1, Node/npm, PostgreSQL 17.11, the legacy repository-root layout, checkout-root CLI installer, and `mod/momopda` destination; mounts the repository read-only and only the external run root writable; uses container tmpfs; receives no provider credentials; drops all capabilities; sets `no-new-privileges`; and accepts only terminal `pass` or `fail` checks.

### Deterministic Proof

All proof artifacts are under `/tmp/opencode/momopda-activity-milestone-20260921`, outside the repository. Disposable grading trees and databases were removed by the runners; concise records, logs, external overlays, and the summary remain.

- `activity-fixture-final`: the unchanged fixture passed Plugin CI, reached all four checks, and ended `fail` on the three missing behaviors.
- `activity-known-good-final`: an external known-good implementation passed Plugin CI and all three runtime checks.
- `mutation-wrong-fresh-default`, `mutation-missing-required-form`, and `mutation-nonpersistent-update` failed `fresh-install` while later checks passed.
- `mutation-missing-upgrade-field` and `mutation-wrong-upgrade-default` failed only `upgrade-install`.
- `mutation-unguarded-upgrade` failed only `savepoint`.
- `mutation-missing-savepoint` passed both feature checks and failed Plugin CI plus the executable `savepoint` check.
- Fresh `filter-regression`, `qbank-regression`, and `tiny-regression` runs reached every declared check and retained terminal `fail` semantics against the four-grader artifact.
- `deterministic-summary.json`: 12 records, one pass, 11 expected failures, zero errors, zero incomplete runs, zero timeouts, and `ranking: null`.
- No real-model sample was run.

### Completed Acceptance

- `graders.json` contains exactly four closed, versioned mappings with ordered checks matching their tasks.
- Fresh-install schema, form contract, add/update persistence, old-row backfill, disk version, field guard, and exact savepoint are independently executable.
- The canonical activity fixture is unchanged and unsolved.
- The worker uses only pinned Moodle 4.5.13/PHP 8.1/Node 22/PostgreSQL 17.11 with unique mutable Moodledata and database state.
- The unchanged fixture returns real outcomes, the external known-good passes, and seven targeted mutations are discriminated while later methods continue.
- Candidate tests remain available to Plugin CI but cannot interfere with public behavioral assertions.
- Filter, qbank, and Tiny behavior remains terminal and stable after the global artifact hash changed.
- Generated workspaces, Moodle trees, records, logs, exemplars, and mutations remain outside the repository.
- No credentials, hidden reasoning, assertion, or exemplar reached a generating agent.
- No fifth grader or model campaign was started.

### Scope Guard

No grader was implemented, registered, tested, or containerized for `local-external-function`, `qtype-safe-rendering`, `report-portable-query`, or `enrol-instance-ui`.

