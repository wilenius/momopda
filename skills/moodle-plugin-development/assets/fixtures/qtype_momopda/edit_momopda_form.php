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
 * Edit form for the MoMoPDA question type contract fixture.
 *
 * @package    qtype_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

/**
 * Editing form for the information-item fixture.
 */
class qtype_momopda_edit_form extends question_edit_form {
    /**
     * Removes grading from the information item.
     *
     * @param MoodleQuickForm $mform Form being built.
     */
    protected function definition_inner($mform) {
        $mform->removeElement('defaultmark');
        $mform->addElement('hidden', 'defaultmark', 0);
        $mform->setType('defaultmark', PARAM_INT);
    }

    /**
     * Returns the question type name.
     *
     * @return string Question type name.
     */
    public function qtype() {
        return 'momopda';
    }
}
