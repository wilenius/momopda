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
 * Test data for the MoMoPDA information-item question type.
 *
 * @package    qtype_momopda
 * @category   test
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
class qtype_momopda_test_helper extends question_test_helper {
    /**
     * Returns the available test question variants.
     *
     * @return string[] Variant names.
     */
    public function get_test_questions() {
        return ['info'];
    }

    /**
     * Creates an in-memory information item.
     *
     * @return qtype_momopda_question Question definition.
     */
    public static function make_momopda_question_info() {
        question_bank::load_question_definition_classes('momopda');
        $question = new qtype_momopda_question();
        test_question_maker::initialise_a_question($question);
        $question->defaultmark = 0;
        $question->penalty = 0;
        $question->length = 0;
        $question->name = 'MoMoPDA information item';
        $question->questiontext = 'MoMoPDA information item';
        $question->generalfeedback = 'MoMoPDA review information';
        $question->qtype = question_bank::get_qtype('momopda');
        return $question;
    }

    /**
     * Returns persisted question data for the save contract.
     *
     * @return stdClass Question data.
     */
    public static function get_momopda_question_data_info() {
        global $USER;

        $question = new stdClass();
        $question->id = 0;
        $question->contextid = 0;
        $question->category = 0;
        $question->parent = 0;
        $question->stamp = make_unique_id_code();
        $question->timecreated = time();
        $question->timemodified = time();
        $question->createdby = $USER->id;
        $question->modifiedby = $USER->id;
        $question->qtype = 'momopda';
        $question->name = 'MoMoPDA information item';
        $question->questiontext = 'MoMoPDA information item';
        $question->questiontextformat = FORMAT_HTML;
        $question->generalfeedback = 'MoMoPDA review information';
        $question->generalfeedbackformat = FORMAT_HTML;
        $question->defaultmark = 0;
        $question->length = 0;
        $question->penalty = 0;
        $question->status = \core_question\local\bank\question_version_status::QUESTION_STATUS_READY;
        $question->hints = [];
        $question->options = new stdClass();
        $question->options->answers = [];
        return $question;
    }

    /**
     * Returns editing form data for the save contract.
     *
     * @return stdClass Form data.
     */
    public static function get_momopda_question_form_data_info() {
        $form = new stdClass();
        $form->name = 'MoMoPDA information item';
        $form->questiontext = ['text' => 'MoMoPDA information item', 'format' => FORMAT_HTML];
        $form->generalfeedback = ['text' => 'MoMoPDA review information', 'format' => FORMAT_HTML];
        $form->status = \core_question\local\bank\question_version_status::QUESTION_STATUS_READY;
        return $form;
    }
}
