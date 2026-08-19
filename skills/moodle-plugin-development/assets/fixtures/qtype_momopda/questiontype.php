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
 * Question type class for the MoMoPDA question type contract fixture.
 *
 * @package    qtype_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/questionlib.php');

/**
 * Minimal information-item question type.
 */
class qtype_momopda extends question_type {
    /**
     * Reports that this is not a gradable question.
     *
     * @return bool Always false.
     */
    public function is_real_question_type() {
        return false;
    }

    /**
     * Reports that random questions cannot select this type.
     *
     * @return bool Always false.
     */
    public function is_usable_by_random() {
        return false;
    }

    /**
     * Reports that this type has no responses to analyze.
     *
     * @return bool Always false.
     */
    public function can_analyse_responses() {
        return false;
    }

    /**
     * Forces the mark to zero before saving.
     *
     * @param stdClass $question Existing question data.
     * @param stdClass $form Submitted form data.
     * @return stdClass Saved question data.
     */
    public function save_question($question, $form) {
        $form->defaultmark = 0;
        return parent::save_question($question, $form);
    }

    /**
     * Returns the number of real questions represented by this item.
     *
     * @param stdClass $question Question data.
     * @return int Always zero.
     */
    public function actual_number_of_questions($question) {
        return 0;
    }

    /**
     * Returns the random-guess score.
     *
     * @param stdClass $questiondata Question data.
     * @return null This type has no score.
     */
    public function get_random_guess_score($questiondata) {
        return null;
    }
}
