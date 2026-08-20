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
 * Public runtime assertions for the modern filter evaluation.
 *
 * @package    filter_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace filter_momopda;

/**
 * Exercises the generated filter through the pinned Moodle runtime.
 */
final class harness_contract_test extends \advanced_testcase {
    /**
     * Verifies the modern class contract and preserved marker behavior.
     */
    public function test_modern_contract(): void {
        global $CFG;

        $this->resetAfterTest();
        $pluginroot = $CFG->dirroot . '/filter/momopda';
        $this->assertFileDoesNotExist($pluginroot . '/filter.php');
        $this->assertFileExists($pluginroot . '/classes/text_filter.php');
        $this->assertTrue(is_subclass_of(text_filter::class, \core_filters\text_filter::class));

        $filter = new text_filter(\context_system::instance(), []);
        $replacement = \html_writer::span(
            s(get_string('replacement', 'filter_momopda')),
            'filter-momopda',
        );
        $this->assertSame('No marker', $filter->filter('No marker'));
        $this->assertSame("Before {$replacement} after", $filter->filter('Before [[momopda]] after'));
        $this->assertSame("{$replacement} / {$replacement}", $filter->filter('[[momopda]] / [[momopda]]'));
    }

    /**
     * Verifies that localized replacement text cannot inject markup.
     */
    public function test_escaped_output(): void {
        $this->resetAfterTest();
        $payload = '<script>alert("momopda")</script> & text';
        $stringmanager = $this->get_mocked_string_manager();
        $stringmanager->mock_string('replacement', 'filter_momopda', $payload);

        $filter = new text_filter(\context_system::instance(), []);
        $expected = 'Before ' . \html_writer::span(s($payload), 'filter-momopda') . ' after';
        $actual = $filter->filter('Before [[momopda]] after');
        $this->assertSame($expected, $actual);
        $this->assertStringNotContainsString('<script>', $actual);
    }
}
