<?php
// This file is part of Moodle - https://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <https://www.gnu.org/licenses/>.

/**
 * Resolve a source plugin through a configured Moodle's component registry.
 *
 * @package    core
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

// phpcs:disable moodle.Files.MoodleInternal.MoodleInternalGlobalState -- Standalone script loads config.php dynamically.
define('CLI_SCRIPT', true);

if ($argc !== 3) {
    fwrite(STDERR, "Usage: resolve-installed-plugin.php MOODLE_DIR PLUGIN_DIR\n");
    exit(1);
}

$moodledir = realpath($argv[1]);
$plugindir = realpath($argv[2]);
if ($moodledir === false || $plugindir === false || !is_file($moodledir . '/config.php')) {
    exit(1);
}

require($moodledir . '/config.php');
// phpcs:enable moodle.Files.MoodleInternal.MoodleInternalGlobalState

$plugin = new stdClass();
require($plugindir . '/version.php');
if (empty($plugin->component)) {
    exit(1);
}

$installed = core_component::get_component_directory($plugin->component);
if ($installed === null || realpath($installed) === false) {
    exit(2);
}

echo realpath($installed);
