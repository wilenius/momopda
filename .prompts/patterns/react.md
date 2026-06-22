# React Integration in Moodle (5.2+)

How to add React (TypeScript/TSX) components to a Moodle plugin. Derived from the
Moodle dev docs (https://moodledev.io/docs/5.3/guides/javascript/react).

Throughout, a generic example plugin `local_example` (Frankenstyle component
`local_example`, directory `local/example/`) with a `status_panel` component is
used. Substitute your own `<plugintype>_<pluginname>` and module names.

> Availability: the Mustache `{{#react}}` helper + autoinit landed in 5.2
> (MDL-87765). Import maps, the esbuild/Grunt `react` task, and Jest unit testing
> landed in 5.3 (MDL-87781 / MDL-87922 / MDL-88812). Confirm your target Moodle
> branch supports these before scaffolding React.

## When to use React (and when NOT to)

**Use React when:** the UI is genuinely interactive/stateful (live-refreshing
panels, bulk-action toolbars, multi-step forms, dashboards that poll a web
service) — e.g. a status panel whose figures auto-refresh, or a toolbar that
applies bulk actions to selected rows.

**Do NOT reach for React when:** a Mustache template + small AMD module already
does the job. React adds a build step (esbuild), an import-map dependency, and a
larger mental model. Follow **simplicity first** — most plugin pages should stay
Mustache + AMD. Only introduce React where interactivity justifies it.

## The big picture (no runtime bundler)

Moodle serves React components as native ES modules resolved through a browser
**import map**. There is no webpack/requirejs shim at runtime:

1. You write `.ts` / `.tsx` source in `<plugin>/js/esm/src/`.
2. `grunt react` (esbuild) compiles each file to `<plugin>/js/esm/build/<name>.js`.
3. A Mustache `{{#react}}` block renders a mount `<div>` with
   `data-react-component` / `data-react-props`.
4. The core `react_autoinit` ESM module scans the DOM, dynamically `import()`s the
   component via the `@moodle/lms/<component>/<module>` specifier, and mounts it
   with `react-dom/client` `createRoot`.
5. `react`, `react-dom`, and `@moodle/lms/*` are marked **external** in the build —
   they are shared singletons served by Moodle, never duplicated into your bundle.

```
Mustache {{#react}} ──► <div data-react-component data-react-props> ──► react_autoinit
                                                                          │ import()
                          import map: @moodle/lms/<component>/<module> ◄──┘
                                       │ resolves to
                          <plugin>/js/esm/build/<module>.js  (default-exported component)
```

## Directory conventions

```
local/example/                     # your plugin root
└── js/
    └── esm/
        ├── src/          # hand-written TypeScript / TSX (commit this)
        │   ├── status_panel.tsx
        │   ├── bulk_actions.tsx
        │   └── helper.ts
        └── build/        # esbuild output (generated — commit per project policy)
            └── status_panel.js
```

The build tool auto-discovers every `js/esm/src/**/*.{ts,tsx}` across core and
plugins. No registration/config file per component is required.

## 1. The component — default-exported function component

`react_autoinit` mounts `module.default`. It MUST be a function component. Keep
the GPL file header and the `@module <component>/<name>` JSDoc tag like any other
Moodle JS module.

```tsx
// js/esm/src/status_panel.tsx
// ... GPL header ...
/**
 * React component for showing a live status panel.
 *
 * @module     local_example/status_panel
 * @copyright  2026 Your Name
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
import React, {useState, useEffect} from 'react';
import requireAmd, {loadStrings} from './helper';

const Fetch = await requireAmd('core/fetch');
const Log = await requireAmd('core/log');

export default function StatusPanel(): React.JSX.Element {
    const [stats, setStats] = useState<Stats | null>(null);
    // ... hooks, fetch, render ...
}
```

Props declared on the `{{#react}}` block arrive as the component's props object:

```tsx
type Props = {title?: string; chapter?: string};

export default function Viewer({title = 'Book', chapter = 'Chapter 1'}: Props) {
    return <div><h1>{title}</h1><p>{chapter}</p></div>;
}
```

## 2. Talking to Moodle from React — AMD bridge

**Critical gotcha:** AMD modules (`core/str`, `core/fetch`, `core/ajax`,
`core/notification`, `core/log`, …) are loaded by RequireJS and **cannot be
`import`ed** from an ES module. Bridge them with a tiny helper that wraps the
global `require`:

```ts
// js/esm/src/helper.ts
/**
 * Helper to load AMD modules from ESM/React context.
 * @module local_example/helper
 */
export default function requireAmd(mod: string) {
    /* eslint-disable @typescript-eslint/no-explicit-any */
    return new Promise<any>((resolve, reject) => {
        (require as any)([mod], resolve, reject);
    });
}

const Str = await requireAmd('core/str');

/** Batch-load language strings, keyed by string key. */
export async function loadStrings(
    defs: readonly {key: string; component: string}[]
): Promise<Record<string, string>> {
    const results: string[] = await Str.get_strings(defs);
    const strings: Record<string, string> = {};
    for (let i = 0; i < defs.length; i++) {
        strings[defs[i].key] = results[i];
    }
    return strings;
}
```

Usage inside a component:

```tsx
const Fetch = await requireAmd('core/fetch');

useEffect(() => {
    loadStrings([
        {key: 'stats:total', component: 'local_example'},
        {key: 'stats:active', component: 'local_example'},
    ]).then(setStrings).catch((e: unknown) => Log.error(e));
}, []);

const response = await Fetch.performGet('local_example', 'status');
const data = await response.json();
```

Rules:
- **Never hardcode UI text** — always go through `core/str` (`loadStrings`).
- Prefer the routed `core/fetch` / `core/ajax` web-service layer for data; do not
  build bespoke `fetch()` calls to ad-hoc endpoints.
- Use `core/log` for error reporting, not `console.*`.

## 3. The mount point — Mustache `{{#react}}` helper

The component is placed on the page from a Mustache template. The block body is a
JSON object (rendered through Mustache *first*, so `{{#str}}`, variables, and
helpers work inside it) followed by optional fallback HTML shown until React
mounts.

```mustache
{{!
    @template local_example/status_panel
}}
{{#react}}
{
    "component": "@moodle/lms/local_example/status_panel",
    "props": {}
}
<div class="d-flex justify-content-center p-5">
    <div class="spinner-border" role="status">
        <span class="sr-only">{{#str}}loading, core{{/str}}</span>
    </div>
</div>
{{/react}}
```

JSON keys:

| Key | Required | Effect |
|-----|----------|--------|
| `component` | Yes | `data-react-component` — must be `@moodle/lms/<component>/<module>` |
| `props` | No | `data-react-props` (JSON-encoded, passed to the component) |
| any other key | No | emitted as a plain HTML attribute (`id`, `class`, `aria-*`, …) |

Parsing behaviour worth knowing: Mustache is rendered before JSON parsing;
trailing commas are stripped; invalid JSON with fallback HTML degrades to that
HTML; invalid JSON without fallback yields an empty string and a
`DEBUG_DEVELOPER` `debugging()` notice. Boolean `true` emits a bare attribute,
`false` omits it.

Passing props from a template:

```mustache
{{#react}}
{
    "component": "@moodle/lms/local_example/status_panel",
    "props": {
        "title": "{{title}}",
        "confirmLabel": "{{#str}}confirm, core{{/str}}"
    },
    "id": "example-status-panel",
    "class": "status-panel-wrapper"
}
<p>{{#str}}loading, core{{/str}}</p>
{{/react}}
```

## 4. The PHP side

No `js_call_amd` is needed for the React component itself — `react_autoinit`
auto-mounts anything with `data-react-component`. You just render the template:

```php
// e.g. local/example/index.php
echo $OUTPUT->render_from_template('local_example/status_panel', []);
```

(You may still `js_call_amd` separate *AMD* helpers on the same page, e.g.
`$PAGE->requires->js_call_amd('local_example/content_modal', 'init');`.)

Dynamic content is handled automatically: `react_autoinit` installs a single
`MutationObserver`, so components inside AJAX-loaded fragments mount on insertion
and unmount on removal — no extra bootstrap call.

## 5. Import map & the `@moodle/lms/` scope

`data-react-component` must be a fully-qualified specifier:
`@moodle/lms/<component>/<module>`. The browser import map maps it to the ESM
endpoint, and the core `esm_controller` resolves it on disk to
`<component_dir>/js/esm/build/<module>.js`.

```
@moodle/lms/local_example/status_panel
        └─► local/example/js/esm/build/status_panel.js
```

Built-in import-map specifiers: `@moodle/lms/`, `@moodlehq/design-system`,
`react`, `react/` (covers `react/jsx-runtime`), `react-dom`, `react-dom/`.

Need a custom specifier (e.g. a CDN or a dev React build)? Register it from a
`pre_render` hook via the shared `import_map` singleton:

```php
$importmap = \core\di::get(\core\output\requirements\import_map::class);
$importmap->add_import('@myplugin/', path: 'local_myplugin/js/esm/build');
```

## 6. Building — esbuild via Grunt

React is part of the JS build pipeline (`.grunt/tasks/javascript.js`,
orchestrated by `.esbuild/build.mjs`). Run from the **Moodle root**, with a
Node/Grunt toolchain installed (see
https://moodledev.io/general/development/tools/nodejs):

```bash
# from the Moodle root (the directory containing the public/ tree)
grunt react                # production build (minified, no sourcemaps)
grunt react:dev            # dev build (inline sourcemaps, not minified)
grunt react:watch          # esbuild native incremental watch
grunt eslint:react         # ESLint with --fix on React sources
```

Notes:
- `cd`-ing into a `js/esm/src` dir and running bare `grunt` triggers `grunt react`.
- `grunt watch` does **not** watch React files — use `grunt react:watch`.
- A generic `grunt amd` helper only builds AMD modules; React needs the
  `grunt react*` tasks. If your environment wraps Grunt in a container or script,
  ensure it invokes `grunt react`, not just `grunt amd`.
- `tsconfig.aliases.json` is generated (by `grunt react` / `grunt jsconfig`) and
  gitignored — **never edit it by hand**.
- After building, purge Moodle caches so the new JS revision is served.

## 7. Unit testing with Jest (5.3+)

ESM/TSX is tested with **Jest** (`ts-jest`, `jsdom`). AMD modules can't run in
Jest, so you test the ESM layer and mock everything below it.

- Test location: `**/esm/tests/**/*.test.{ts,tsx}`, mirroring `src/`:
  `js/esm/src/output/Foo.tsx` → `js/esm/tests/output/Foo.test.ts`.
- Run: `npm test` (its `pretest` runs `grunt jsconfig` to regenerate aliases),
  single file `npm test -- --testPathPatterns=<path>`, coverage `--coverage`.
- Mock AMD with `mockAmdModule('core/ajax', mockObj)` — a call to an
  unregistered module throws on purpose (no silent wrong behaviour).
- Mock strings with `mockString('submit', 'core', 'Submit')`; unmocked strings
  resolve to `'[identifier, component]'`.
- Mocks/registrations reset automatically between tests.

```ts
import {getString} from '@moodle/lms/core/String';

describe('getString', () => {
    it('returns the resolved string', async () => {
        mockString('pluginname', 'mod_forum', 'Forum');
        await expect(getString('pluginname', 'mod_forum')).resolves.toBe('Forum');
    });
});
```

## Debugging checklist

Component does not render:
1. `data-react-component` uses `@moodle/lms/<component>/<module>` form.
2. The built file exists under `js/esm/build/` (did you run `grunt react`?).
3. The module has a **default-exported function component**.
4. Browser console — look for `[react_autoinit]` messages; verify the import map
   `<script type="importmap">` is present in `<head>`.
5. Caches purged / JS revision bumped after rebuild.

Component mounts twice:
1. The surrounding template isn't recreating the container on every re-render.
2. You are not calling `createRoot` manually on an autoinit-managed element.

## Quick checklist for adding a React component

- [ ] `js/esm/src/<name>.tsx` with GPL header, `@module <component>/<name>`,
      `export default function`.
- [ ] AMD/string access via a `helper.ts` `requireAmd` bridge — no hardcoded text.
- [ ] Mustache template with a `{{#react}}` block + accessible loading fallback.
- [ ] PHP renders the template via `render_from_template`.
- [ ] `grunt react` (or `:dev`) run; build output present; caches purged.
- [ ] Jest test under `js/esm/tests/` mocking AMD modules and strings.
- [ ] `grunt eslint:react` clean.

## References

- React overview: https://moodledev.io/docs/5.3/guides/javascript/react
- Build tools: https://moodledev.io/docs/5.3/guides/javascript/react/buildtools
- Mustache helper & autoinit: https://moodledev.io/docs/5.3/guides/javascript/react/reactautoinit
- Import maps: https://moodledev.io/docs/5.3/guides/javascript/react/importmap
- Unit testing: https://moodledev.io/docs/5.3/guides/javascript/react/testing
