// This file is part of MoMoPDA - https://github.com/wilenius/momopda.
//
// MoMoPDA is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

/**
 * Minimal TinyMCE plugin loader contract.
 *
 * @module      tiny_momopda/plugin
 * @copyright   2026 MoMoPDA contributors
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

import {getTinyMCE} from 'editor_tiny/loader';
import {getPluginMetadata} from 'editor_tiny/utils';

const component = 'tiny_momopda';
const pluginName = `${component}/plugin`;

// TinyMCE registration is synchronous, so resolve dependencies first.
// eslint-disable-next-line no-async-promise-executor
export default new Promise(async(resolve) => {
    const [tinyMCE, pluginMetadata] = await Promise.all([
        getTinyMCE(),
        getPluginMetadata(component, pluginName),
    ]);

    tinyMCE.PluginManager.add(pluginName, () => pluginMetadata);
    resolve(pluginName);
});
