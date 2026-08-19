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
 * Question ID column for the MoMoPDA question bank contract fixture.
 *
 * @package    qbank_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace qbank_momopda;

use core_question\local\bank\column_base;

/**
 * Displays the existing question ID field.
 */
class question_id_column extends column_base {
    /**
     * Returns the internal column name.
     *
     * @return string Column name.
     */
    public function get_name(): string {
        return 'momopdaquestionid';
    }

    /**
     * Returns the visible column title.
     *
     * @return string Column title.
     */
    public function get_title(): string {
        return get_string('columnname', 'qbank_momopda');
    }

    /**
     * Displays one row's content.
     *
     * @param stdClass $question Question row.
     * @param string $rowclasses Existing row classes.
     */
    protected function display_content($question, $rowclasses): void {
        echo s((string) $question->id);
    }
}
