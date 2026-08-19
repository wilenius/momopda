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
 * Moodle callbacks for the MoMoPDA activity contract fixture.
 *
 * @package    mod_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

/**
 * Reports the features supported by the fixture.
 *
 * @param string $feature Feature constant.
 * @return bool|null Whether the feature is supported.
 */
function momopda_supports(string $feature): ?bool {
    return match ($feature) {
        FEATURE_MOD_INTRO => true,
        FEATURE_SHOW_DESCRIPTION => true,
        FEATURE_BACKUP_MOODLE2 => false,
        default => null,
    };
}

/**
 * Creates an activity instance.
 *
 * @param stdClass $data Submitted activity data.
 * @param mod_momopda_mod_form|null $mform Activity form.
 * @return int New instance ID.
 */
function momopda_add_instance(stdClass $data, ?mod_momopda_mod_form $mform = null): int {
    global $DB;

    $data->timecreated = time();
    $data->timemodified = $data->timecreated;

    return $DB->insert_record('momopda', $data);
}

/**
 * Updates an activity instance.
 *
 * @param stdClass $data Submitted activity data.
 * @param mod_momopda_mod_form|null $mform Activity form.
 * @return bool Whether the instance was updated.
 */
function momopda_update_instance(stdClass $data, ?mod_momopda_mod_form $mform = null): bool {
    global $DB;

    $data->id = $data->instance;
    $data->timemodified = time();

    return $DB->update_record('momopda', $data);
}

/**
 * Deletes an activity instance.
 *
 * @param int $id Instance ID.
 * @return bool Whether the instance existed and was deleted.
 */
function momopda_delete_instance(int $id): bool {
    global $DB;

    if (!$DB->record_exists('momopda', ['id' => $id])) {
        return false;
    }

    $DB->delete_records('momopda', ['id' => $id]);
    return true;
}
