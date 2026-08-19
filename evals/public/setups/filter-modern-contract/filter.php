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
 * Deliberately legacy filter used as an evaluation starting state.
 *
 * @package    filter_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Legacy global filter implementation to migrate during evaluation.
 */
class filter_momopda extends moodle_text_filter {
    /**
     * Replaces the fixture marker.
     *
     * @param string $text Text to filter.
     * @param array $options Filter options.
     * @return string Filtered text.
     */
    public function filter($text, array $options = []) {
        $replacement = html_writer::span(get_string('replacement', 'filter_momopda'), 'filter-momopda');
        return str_replace('[[momopda]]', $replacement, $text);
    }
}
