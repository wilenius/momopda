# TinyMCE Plugin Contract

Use [`assets/fixtures/tiny_momopda`](../assets/fixtures/tiny_momopda/) as the minimal loader contract. It follows core TinyMCE plugin registration without adding a toolbar control.

## Required Shape

Provide `version.php`, an English language file, and `classes/plugininfo.php`. The namespaced `plugininfo` extends `editor_tiny\plugin`, not a `plugininfo` base class. Define `tiny/name:use` in `db/access.php` for the standard enablement check used by current Moodle 5.x branches.

The AMD module `tiny_name/plugin` default-exports a promise resolving to the registered plugin name or to a plugin-name/configuration pair. Resolve asynchronous metadata and strings before calling TinyMCE's synchronous `PluginManager.add()` registration callback. Ship built AMD files in a distributable plugin.

Implement `plugin_with_buttons`, `plugin_with_menuitems`, or `plugin_with_configuration` only when supplying the corresponding contract. Methods without their interface are not discovered as configuration providers.

## Contract Pitfalls

- Do not return a `getSetup()` function as the plugin module entry contract.
- Do not use `$this` in static PHP configuration methods.
- Do not assume TinyMCE is the active editor or that uploads are enabled.
- Verify the bundled TinyMCE major version in the target Moodle branch.
- On Moodle 5.1+, the physical path is `public/lib/editor/tiny/plugins/name`.

Core references: `lib/editor/tiny/plugins/noautolink`, `lib/editor/tiny/classes/manager.php`, `lib/editor/tiny/amd/src/editor.js`.
