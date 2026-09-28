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
 * Public runtime assertions for the activity schema-upgrade evaluation.
 *
 * @package    mod_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace mod_momopda;

/**
 * Exercises fresh installation, form persistence, upgrades, and savepoints.
 */
final class harness_contract_test extends \advanced_testcase {
    /** @var int Version of the unsolved starting fixture. */
    private const BASE_VERSION = 2026081900;

    /** @var int Required version after the schema change. */
    private const TARGET_VERSION = 2026081901;

    /**
     * Verifies the fresh schema, exact form contract, and add/update persistence.
     */
    public function test_fresh_install(): void {
        global $CFG, $DB, $PAGE;

        $this->resetAfterTest(true);
        $this->setAdminUser();
        $pluginroot = $CFG->dirroot . '/mod/momopda';

        $DB->get_manager(); // Load the XMLDB classes before parsing install.xml.
        $xmldbfile = new \xmldb_file($pluginroot . '/db/install.xml');
        $this->assertTrue($xmldbfile->loadXMLStructure(), 'The fresh-install XMLDB schema could not be loaded');
        $tabledefinition = $xmldbfile->getStructure()->getTable('momopda');
        $this->assertInstanceOf(\xmldb_table::class, $tabledefinition);
        $fielddefinition = $tabledefinition->getField('mode');
        $this->assertInstanceOf(\xmldb_field::class, $fielddefinition);
        $this->assertSame(XMLDB_TYPE_INTEGER, $fielddefinition->getType());
        $this->assertSame('1', $fielddefinition->getLength());
        $this->assertTrue($fielddefinition->getNotNull());
        $this->assertSame('1', $fielddefinition->getDefault());

        $columns = $DB->get_columns('momopda');
        $this->assertArrayHasKey('mode', $columns, 'Fresh installation did not create momopda.mode');
        $this->assertSame('I', $columns['mode']->meta_type);
        $this->assertTrue($columns['mode']->not_null);
        $this->assertTrue($columns['mode']->has_default);
        $this->assertEquals(1, $columns['mode']->default_value);

        $plugininfo = \core_plugin_manager::instance()->get_plugin_info('mod_momopda');
        $this->assertNotNull($plugininfo);
        $this->assertEquals(self::TARGET_VERSION, $plugininfo->versiondisk);
        $this->assertEquals(self::TARGET_VERSION, $plugininfo->versiondb);

        require_once($pluginroot . '/mod_form.php');
        $course = $this->getDataGenerator()->create_course();
        $PAGE->set_course($course);
        $current = (object) ['instance' => 0, 'course' => $course->id];
        $form = new \mod_momopda_mod_form($current, 0, null, $course);
        $mform = $this->get_quick_form($form);
        $this->assertTrue($mform->elementExists('mode'));
        $mode = $mform->getElement('mode');
        $this->assertInstanceOf(\MoodleQuickForm_select::class, $mode);
        $this->assertSame(get_string('mode', 'mod_momopda'), $mode->getLabel());
        $optionsproperty = new \ReflectionProperty(\HTML_QuickForm_select::class, '_options');
        $rawoptions = $optionsproperty->getValue($mode);
        $options = array_map(static function (array $option): array {
            return [
                'value' => (string) $option['attr']['value'],
                'text' => (string) $option['text'],
            ];
        }, $rawoptions);
        $this->assertSame([
            ['value' => '1', 'text' => get_string('modestandard', 'mod_momopda')],
            ['value' => '2', 'text' => get_string('modeguided', 'mod_momopda')],
        ], $options);
        $defaultvalue = array_map('strval', (array) $mform->getElementValue('mode'));
        $this->assertSame(['1'], $defaultvalue);

        $rulesproperty = new \ReflectionProperty(\HTML_QuickForm::class, '_rules');
        $rules = $rulesproperty->getValue($mform);
        $this->assertArrayHasKey('mode', $rules);
        $this->assertContains('required', array_column($rules['mode'], 'type'));
        $typesproperty = new \ReflectionProperty(\MoodleQuickForm::class, '_types');
        $types = $typesproperty->getValue($mform);
        $this->assertSame(PARAM_INT, $types['mode'] ?? null);

        $unknownvalue = ['mode' => 3];
        $this->assertNull($mode->exportValue($unknownvalue, true));
        $guidedvalue = ['mode' => 2];
        $this->assertSame(['mode' => '2'], $mode->exportValue($guidedvalue, true));

        $instanceid = momopda_add_instance((object) [
            'course' => $course->id,
            'name' => 'Guided activity',
            'intro' => '',
            'introformat' => FORMAT_HTML,
            'mode' => 2,
        ]);
        $this->assertEquals(2, $DB->get_field('momopda', 'mode', ['id' => $instanceid]));
        $this->assertTrue(momopda_update_instance((object) [
            'instance' => $instanceid,
            'course' => $course->id,
            'name' => 'Standard activity',
            'intro' => '',
            'introformat' => FORMAT_HTML,
            'mode' => 1,
        ]));
        $stored = $DB->get_record('momopda', ['id' => $instanceid], 'name, mode', MUST_EXIST);
        $this->assertSame('Standard activity', $stored->name);
        $this->assertEquals(1, $stored->mode);
    }

    /**
     * Verifies an old schema and row upgrade to the exact current contract.
     */
    public function test_upgrade_install(): void {
        global $CFG, $DB;

        $this->resetAfterTest(true);
        $this->setAdminUser();
        $dbman = $DB->get_manager();
        $table = new \xmldb_table('momopda');
        $originalversion = get_config('mod_momopda', 'version');

        try {
            if ($dbman->field_exists($table, 'mode')) {
                $dbman->drop_field($table, new \xmldb_field('mode'));
            }
            $course = $this->getDataGenerator()->create_course();
            $instanceid = $DB->insert_record('momopda', (object) [
                'course' => $course->id,
                'name' => 'Existing activity',
                'intro' => 'Preserved intro',
                'introformat' => FORMAT_HTML,
                'timecreated' => 1,
                'timemodified' => 2,
            ]);
            set_config('version', self::BASE_VERSION, 'mod_momopda');
            \core_plugin_manager::reset_caches();
            $before = \core_plugin_manager::instance()->get_plugin_info('mod_momopda');
            $this->assertNotNull($before);
            $this->assertEquals(self::BASE_VERSION, $before->versiondb);
            $this->assertEquals(self::TARGET_VERSION, $before->versiondisk);
            $this->assertSame(\core_plugin_manager::PLUGIN_STATUS_UPGRADE, $before->get_status());

            $upgradefile = $CFG->dirroot . '/mod/momopda/db/upgrade.php';
            $this->assertFileExists($upgradefile);
            require_once($CFG->libdir . '/upgradelib.php');
            require_once($upgradefile);
            $upgradefunction = 'xmldb_momopda_upgrade';
            $this->assertTrue(function_exists($upgradefunction));
            $this->assertTrue($upgradefunction(self::BASE_VERSION));

            $this->assertTrue($dbman->field_exists($table, 'mode'));
            $columns = $DB->get_columns('momopda');
            $this->assertSame('I', $columns['mode']->meta_type);
            $this->assertTrue($columns['mode']->not_null);
            $this->assertTrue($columns['mode']->has_default);
            $this->assertEquals(1, $columns['mode']->default_value);
            $upgraded = $DB->get_record('momopda', ['id' => $instanceid], 'name, intro, mode', MUST_EXIST);
            $this->assertSame('Existing activity', $upgraded->name);
            $this->assertSame('Preserved intro', $upgraded->intro);
            $this->assertEquals(1, $upgraded->mode);
        } finally {
            $this->restore_mode_field($dbman, $table);
            set_config('version', $originalversion, 'mod_momopda');
            \core_plugin_manager::reset_caches();
        }
    }

    /**
     * Verifies the guarded upgrade records its own exact module savepoint.
     */
    public function test_savepoint(): void {
        global $CFG, $DB;

        $this->resetAfterTest(true);
        $dbman = $DB->get_manager();
        $table = new \xmldb_table('momopda');
        $originalversion = get_config('mod_momopda', 'version');

        try {
            if (!$dbman->field_exists($table, 'mode')) {
                $dbman->add_field($table, self::expected_mode_field());
            }
            set_config('version', self::BASE_VERSION, 'mod_momopda');
            $upgradefile = $CFG->dirroot . '/mod/momopda/db/upgrade.php';
            $this->assertFileExists($upgradefile);
            require_once($CFG->libdir . '/upgradelib.php');
            require_once($upgradefile);
            $upgradefunction = 'xmldb_momopda_upgrade';
            $this->assertTrue(function_exists($upgradefunction));
            $this->assertTrue(
                $upgradefunction(self::BASE_VERSION),
                'The upgrade must tolerate the target field already existing',
            );
            $this->assertEquals(
                self::TARGET_VERSION,
                get_config('mod_momopda', 'version'),
                'The upgrade did not record the exact mod_momopda savepoint',
            );
        } finally {
            $this->restore_mode_field($dbman, $table);
            set_config('version', $originalversion, 'mod_momopda');
            \core_plugin_manager::reset_caches();
        }
    }

    /**
     * Returns the wrapped MoodleQuickForm for runtime form assertions.
     *
     * @param \mod_momopda_mod_form $form Activity form.
     * @return \MoodleQuickForm
     */
    private function get_quick_form(\mod_momopda_mod_form $form): \MoodleQuickForm {
        $reflection = new \ReflectionClass($form);
        $property = $reflection->getProperty('_form');
        $mform = $property->getValue($form);
        $this->assertInstanceOf(\MoodleQuickForm::class, $mform);
        return $mform;
    }

    /**
     * Returns the exact field required by both installation paths.
     *
     * @return \xmldb_field
     */
    private static function expected_mode_field(): \xmldb_field {
        return new \xmldb_field(
            'mode',
            XMLDB_TYPE_INTEGER,
            '1',
            null,
            XMLDB_NOTNULL,
            null,
            '1',
            'introformat',
        );
    }

    /**
     * Restores a stable schema for later independently executed checks.
     *
     * @param \database_manager $dbman Moodle database manager.
     * @param \xmldb_table $table Activity table.
     */
    private function restore_mode_field(\database_manager $dbman, \xmldb_table $table): void {
        if ($dbman->field_exists($table, 'mode')) {
            $dbman->drop_field($table, new \xmldb_field('mode'));
        }
        $dbman->add_field($table, self::expected_mode_field());
    }
}
