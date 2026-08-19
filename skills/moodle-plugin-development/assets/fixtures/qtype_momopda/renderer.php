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
 * Renderer for the MoMoPDA question type contract fixture.
 *
 * @package    qtype_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

/**
 * Renders a formatted information item.
 */
class qtype_momopda_renderer extends qtype_renderer {
    /**
     * Renders the question text without response controls.
     *
     * @param question_attempt $qa Question attempt.
     * @param question_display_options $options Display options.
     * @return string Rendered HTML.
     */
    public function formulation_and_controls(question_attempt $qa, question_display_options $options) {
        $questiontext = $qa->get_question()->format_questiontext($qa);
        return html_writer::div($questiontext, 'qtext');
    }

    /**
     * Returns the accessible formulation heading.
     *
     * @return string Heading text.
     */
    public function formulation_heading() {
        return get_string('informationtext', 'qtype_momopda');
    }
}
