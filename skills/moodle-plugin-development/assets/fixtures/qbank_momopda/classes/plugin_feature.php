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
 * Feature registration for the MoMoPDA question bank contract fixture.
 *
 * @package    qbank_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace qbank_momopda;

use core_question\local\bank\plugin_features_base;

/**
 * Registers the fixture's question-bank column.
 */
class plugin_feature extends plugin_features_base {
    /**
     * Returns columns supplied by this plugin.
     *
     * @param \core_question\local\bank\view $qbank Question-bank view.
     * @return array Question-bank columns.
     */
    public function get_question_columns($qbank): array {
        return [new question_id_column($qbank)];
    }
}
