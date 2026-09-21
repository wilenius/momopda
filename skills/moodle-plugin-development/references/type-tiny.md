# TinyMCE Plugin Contract

Use [`assets/fixtures/tiny_momopda`](../assets/fixtures/tiny_momopda/) as the minimal loader contract. It follows core TinyMCE plugin registration without adding a toolbar control.

## Required Shape

Provide `version.php`, an English language file, and `classes/plugininfo.php`. The namespaced `plugininfo` extends `editor_tiny\plugin`, not a `plugininfo` base class. Define `tiny/name:use` in `db/access.php` for the standard enablement check used by current Moodle 5.x branches.

The AMD module `tiny_name/plugin` default-exports a promise resolving to the registered plugin name or to a plugin-name/configuration pair. Use the pair when the plugin must adjust editor configuration, such as adding a control to a named toolbar section. Resolve asynchronous metadata and language strings before calling TinyMCE's synchronous `PluginManager.add()` registration callback.

Implement `plugin_with_buttons`, `plugin_with_menuitems`, or `plugin_with_configuration` only when supplying the corresponding contract. Methods without their interface are not discovered as configuration providers. Button identifiers advertised by PHP use the fully qualified `tiny_name/buttonname` form; the matching TinyMCE registry name is the unqualified button name.

Use `editor_tiny/utils` configuration helpers to place controls in Moodle's named toolbar sections. Register commands and controls in the synchronous plugin callback after their localized labels have loaded. For content insertion, use `editor.insertContent()` so TinyMCE applies the operation at the current selection; TinyMCE 8 deprecates `editor.selection.setContent()`.

Ship a `.min.js` and `.min.js.map` for every AMD source module. Before release, run a clean component-scoped Grunt AMD build and verify that both generated JavaScript and source maps match the committed artifacts.

## Contract Pitfalls

- Do not return a `getSetup()` function as the plugin module entry contract.
- Do not use `$this` in static PHP configuration methods.
- Do not assume TinyMCE is the active editor or that uploads are enabled.
- Verify the bundled TinyMCE major version in the target Moodle branch.
- On Moodle 5.1+, the physical path is `public/lib/editor/tiny/plugins/name`.

Core references: `lib/editor/tiny/classes/plugin_with_buttons.php`, `lib/editor/tiny/plugins/noautolink`, `lib/editor/tiny/classes/manager.php`, `lib/editor/tiny/amd/src/editor.js`, `lib/editor/tiny/amd/src/utils.js`.
