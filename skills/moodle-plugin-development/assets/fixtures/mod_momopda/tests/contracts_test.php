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

namespace mod_momopda;

use core_question\local\bank\question_edit_contexts;
use core_question\local\bank\view;

defined('MOODLE_INTERNAL') || die();

global $CFG;
require_once($CFG->libdir . '/adminlib.php');
require_once($CFG->libdir . '/blocklib.php');
require_once($CFG->libdir . '/enrollib.php');
require_once($CFG->dirroot . '/question/editlib.php');
require_once($CFG->dirroot . '/question/engine/tests/helpers.php');
require_once($CFG->dirroot . '/question/type/edit_question_form.php');
require_once(\core_component::get_plugin_directory('qtype', 'momopda') . '/edit_momopda_form.php');

/**
 * Database-backed contracts shared by all staged fixtures.
 *
 * @package    mod_momopda
 * @category   test
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
final class contracts_test extends \advanced_testcase {
    /**
     * Exercises activity creation, update, deletion, and view routing.
     */
    public function test_activity_contract(): void {
        global $DB;

        $this->resetAfterTest(true);
        $course = $this->getDataGenerator()->create_course();
        $activity = $this->getDataGenerator()->create_module('momopda', [
            'course' => $course->id,
            'name' => 'Contract activity',
            'intro' => 'Contract intro',
            'introformat' => FORMAT_HTML,
        ]);

        $this->assertTrue(momopda_supports(FEATURE_MOD_INTRO));
        $this->assertTrue(momopda_supports(FEATURE_SHOW_DESCRIPTION));
        $this->assertFalse(momopda_supports(FEATURE_BACKUP_MOODLE2));
        $this->assertTrue($DB->record_exists('momopda', ['id' => $activity->id]));
        $cm = get_fast_modinfo($course)->get_cm($activity->cmid);
        $this->assertStringContainsString('/mod/momopda/view.php', $cm->url->out(false));

        $updated = (object) [
            'instance' => $activity->id,
            'course' => $course->id,
            'name' => 'Updated contract activity',
            'intro' => 'Updated intro',
            'introformat' => FORMAT_HTML,
        ];
        $this->assertTrue(momopda_update_instance($updated));
        $this->assertEquals('Updated contract activity', $DB->get_field('momopda', 'name', ['id' => $activity->id]));
        $this->assertTrue(momopda_delete_instance($activity->id));
        $this->assertFalse($DB->record_exists('momopda', ['id' => $activity->id]));
    }

    /**
     * Exercises block, enrolment, filter, and no-op local plugin discovery.
     */
    public function test_small_plugin_contracts(): void {
        $this->resetAfterTest();

        $block = block_instance('momopda');
        $this->assertInstanceOf(\block_momopda::class, $block);
        $this->assertTrue($block->_self_test());
        $this->assertNotEmpty($block->get_content()->text);

        $this->assertInstanceOf(\enrol_momopda_plugin::class, enrol_get_plugin('momopda'));
        $this->assertFileExists(\core_component::get_plugin_directory('enrol', 'momopda') . '/lib.php');

        $filter = new \filter_momopda\text_filter(\context_system::instance(), []);
        $this->assertStringContainsString('filter-momopda', $filter->filter('Before [[momopda]] after'));

        $local = \core_plugin_manager::instance()->get_plugin_info('local_momopda');
        $this->assertNotNull($local);
        $this->assertEquals(\core_plugin_manager::PLUGIN_STATUS_UPTODATE, $local->get_status());
    }

    /**
     * Supplies a column to an actual question-bank view.
     */
    public function test_question_bank_contract(): void {
        $this->resetAfterTest();
        $this->setAdminUser();

        $course = $this->getDataGenerator()->create_course();
        if (\core_component::get_plugin_directory('mod', 'qbank') !== null) {
            $qbank = $this->getDataGenerator()->create_module('qbank', ['course' => $course->id]);
            $cm = get_coursemodule_from_instance('qbank', $qbank->id, $course->id, false, MUST_EXIST);
            $context = \context_module::instance($cm->id);
        } else {
            $cm = null;
            $context = \context_course::instance($course->id);
        }
        $questionbank = new view(
            new question_edit_contexts($context),
            new \moodle_url('/question/edit.php'),
            $course,
            $cm,
        );

        $columns = (new \qbank_momopda\plugin_feature())->get_question_columns($questionbank);
        $this->assertCount(1, $columns);
        $this->assertInstanceOf(\qbank_momopda\question_id_column::class, $columns[0]);
        $this->assertEquals('momopdaquestionid', $columns[0]->get_name());
        $this->assertInstanceOf(
            \qbank_momopda\question_id_column::class,
            $questionbank->get_visiblecolumns()['question_id_column'],
        );
    }

    /**
     * Saves and renders the information-item question type.
     */
    public function test_question_type_contract(): void {
        global $PAGE;

        $this->resetAfterTest(true);
        $this->setAdminUser();
        $questiondata = \test_question_maker::get_question_data('momopda');
        $formdata = \test_question_maker::get_question_form_data('momopda');
        $generator = $this->getDataGenerator()->get_plugin_generator('core_question');
        $category = $generator->create_question_category();
        $formdata->category = "{$category->id},{$category->contextid}";

        \qtype_momopda_edit_form::mock_submit((array) $formdata);
        $form = \qtype_momopda_test_helper::get_question_editing_form($category, $questiondata);
        $this->assertTrue($form->is_validated());
        $saved = \question_bank::get_qtype('momopda')->save_question($questiondata, $form->get_data());
        $this->assertEquals('momopda', $saved->qtype);
        $this->assertEquals(0, $saved->defaultmark);

        $question = \question_bank::load_question($saved->id);
        $this->assertInstanceOf(\qtype_momopda_question::class, $question);
        $usage = \question_engine::make_questions_usage_by_activity(
            'mod_momopda',
            \context_system::instance(),
        );
        $usage->set_preferred_behaviour('deferredfeedback');
        $slot = $usage->add_question($question, 0);
        $usage->start_all_questions();
        $attempt = $usage->get_question_attempt($slot);
        $this->assertEquals('informationitem', $attempt->get_behaviour_name());
        $PAGE->set_context(\context_system::instance());
        $renderer = $PAGE->get_renderer('qtype_momopda');
        $html = $renderer->formulation_and_controls($attempt, new \question_display_options());
        $this->assertEquals(get_string('informationtext', 'qtype_momopda'), $renderer->formulation_heading());
        $this->assertStringContainsString('qtext', $html);
        $this->assertStringContainsString('MoMoPDA information item', $html);
    }

    /**
     * Exercises report administration and TinyMCE registration.
     */
    public function test_report_and_tiny_contracts(): void {
        $this->resetAfterTest();
        $this->setAdminUser();

        $this->assertNotNull(get_capability_info('report/momopda:view'));
        $adminroot = admin_get_root(true, true);
        $this->assertInstanceOf(\admin_externalpage::class, $adminroot->locate('reportmomopda'));

        $configuration = (new \editor_tiny\manager())->get_plugin_configuration(\context_system::instance());
        $this->assertArrayHasKey('tiny_momopda/plugin', $configuration);
        $this->assertDebuggingNotCalled();
    }
}
