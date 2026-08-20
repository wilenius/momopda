<?php
/**
 * Verify staged fixtures after Moodle Plugin CI has installed and upgraded them.
 *
 * @copyright 2026 MoMoPDA contributors
 * @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

declare(strict_types=1);

/**
 * Stop the integration job when a contract is false.
 *
 * @param bool $condition Contract result.
 * @param string $message Failure detail.
 */
function momopda_assert(bool $condition, string $message): void {
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

try {
    $options = getopt('', ['moodle:', 'manifest:', 'layout:']);
    foreach (['moodle', 'manifest', 'layout'] as $required) {
        momopda_assert(isset($options[$required]) && is_string($options[$required]), "Missing --{$required}");
    }

    $moodleroot = realpath($options['moodle']);
    $manifestpath = realpath($options['manifest']);
    momopda_assert($moodleroot !== false && is_file($moodleroot . '/config.php'), 'Invalid Moodle application root');
    momopda_assert($manifestpath !== false && is_file($manifestpath), 'Invalid fixture manifest');
    momopda_assert(in_array($options['layout'], ['legacy', 'public'], true), 'Layout must be legacy or public');

    define('CLI_SCRIPT', true);
    require $moodleroot . '/config.php';

    global $CFG;
    require_once($CFG->libdir . '/adminlib.php');
    require_once($CFG->libdir . '/blocklib.php');
    require_once($CFG->libdir . '/enrollib.php');
    require_once($CFG->libdir . '/questionlib.php');

    $manifest = json_decode((string) file_get_contents($manifestpath), true, 512, JSON_THROW_ON_ERROR);
    momopda_assert(is_array($manifest) && $manifest['schema_version'] === 1, 'Unsupported fixture manifest');
    momopda_assert(isset($manifest['fixtures']) && is_array($manifest['fixtures']), 'Fixture list is missing');
    momopda_assert(($manifest['layout'] ?? null) === $options['layout'], 'Staged manifest layout does not match --layout');

    $detectedlayout = is_file($moodleroot . '/public/version.php') ? 'public' : 'legacy';
    momopda_assert($detectedlayout === $options['layout'], "Expected {$options['layout']} layout, found {$detectedlayout}");

    $pluginmanager = core_plugin_manager::instance();
    foreach ($manifest['fixtures'] as $fixture) {
        momopda_assert(is_array($fixture) && isset($fixture['component']), 'Invalid fixture entry');
        $component = $fixture['component'];
        $destinationkey = $detectedlayout === 'public' ? 'public_destination' : 'legacy_destination';
        momopda_assert(isset($fixture[$destinationkey]), "Missing {$destinationkey} for {$component}");
        momopda_assert(
            ($fixture['destination'] ?? null) === $fixture[$destinationkey],
            "Staged destination does not match {$destinationkey} for {$component}",
        );

        [$type, $name] = core_component::normalize_component($component);
        $actual = core_component::get_plugin_directory($type, $name);
        $expected = $moodleroot . '/' . $fixture[$destinationkey];
        momopda_assert($actual !== null, "Moodle did not discover {$component}");
        momopda_assert(realpath($actual) === realpath($expected), "Unexpected install path for {$component}: {$actual}");

        $plugininfo = $pluginmanager->get_plugin_info($component);
        momopda_assert($plugininfo !== null, "Plugin manager did not discover {$component}");
        momopda_assert(
            $plugininfo->get_status() === core_plugin_manager::PLUGIN_STATUS_UPTODATE,
            "{$component} is not upgraded: {$plugininfo->get_status()}",
        );
        momopda_assert($plugininfo->is_installed_and_upgraded(), "{$component} is not installed and upgraded");
        momopda_assert(
            (string) $plugininfo->versiondisk === (string) $plugininfo->versiondb,
            "{$component} disk and database versions differ",
        );
        $namestring = $component === 'filter_momopda' ? 'filtername' : 'pluginname';
        momopda_assert(
            get_string_manager()->string_exists($namestring, $component),
            "{$component} has no {$namestring} language string",
        );
        momopda_assert(isset($fixture['files']) && is_array($fixture['files']), "Missing file hashes for {$component}");
        foreach ($fixture['files'] as $relative => $expectedhash) {
            momopda_assert(
                is_string($relative) && is_string($expectedhash) && preg_match('/^[a-f0-9]{64}$/D', $expectedhash),
                "Invalid staged file hash for {$component}",
            );
            $parts = explode('/', $relative);
            momopda_assert(
                $relative !== '' && $relative[0] !== '/' && !in_array('..', $parts, true),
                "Unsafe staged file path for {$component}: {$relative}",
            );
            $installedfile = $actual . '/' . $relative;
            momopda_assert(is_file($installedfile), "Installed fixture file is missing: {$component}/{$relative}");
            momopda_assert(
                hash_file('sha256', $installedfile) === $expectedhash,
                "Installed fixture file differs from staged source: {$component}/{$relative}",
            );
        }
        echo "Discovered {$component} at {$fixture[$destinationkey]}" . PHP_EOL;
    }

    global $DB;
    $dbmanager = $DB->get_manager();
    momopda_assert($dbmanager->table_exists(new xmldb_table('momopda')), 'mod_momopda XMLDB table is missing');

    require_once(core_component::get_plugin_directory('mod', 'momopda') . '/lib.php');
    $record = (object) [
        'course' => SITEID,
        'name' => 'MoMoPDA integration record',
        'intro' => 'Integration contract',
        'introformat' => FORMAT_PLAIN,
    ];
    $record->id = momopda_add_instance($record);
    momopda_assert($DB->record_exists('momopda', ['id' => $record->id]), 'Activity add callback failed');
    $record->instance = $record->id;
    $record->name = 'Updated MoMoPDA integration record';
    momopda_assert(momopda_update_instance($record), 'Activity update callback failed');
    momopda_assert(momopda_delete_instance($record->id), 'Activity delete callback failed');
    momopda_assert(!momopda_delete_instance($record->id), 'Activity delete callback accepted a missing record');
    momopda_assert(
        is_file(core_component::get_plugin_directory('mod', 'momopda') . '/view.php'),
        'Activity view endpoint is missing',
    );

    $block = block_instance('momopda');
    momopda_assert($block instanceof block_momopda && $block->_self_test(), 'Block self-test failed');
    momopda_assert($block->get_content()->text !== '', 'Block content is empty');
    momopda_assert($block->get_content() === $block->get_content(), 'Block content is not cached');

    momopda_assert(array_key_exists('momopda', enrol_get_plugins(false)), 'Enrolment plugin list is missing momopda');
    $enrolplugin = enrol_get_plugin('momopda');
    momopda_assert($enrolplugin instanceof enrol_momopda_plugin, 'Enrolment class did not resolve');
    momopda_assert(is_file(core_component::get_plugin_directory('enrol', 'momopda') . '/lib.php'), 'Enrol lib.php is missing');

    $filter = new filter_momopda\text_filter(context_system::instance(), []);
    momopda_assert($filter instanceof core_filters\text_filter, 'Modern text filter class did not resolve');
    momopda_assert($filter->filter('No marker') === 'No marker', 'Text filter changed content without a marker');
    $filtered = $filter->filter('Before [[momopda]] after');
    momopda_assert(str_contains($filtered, 'filter-momopda'), 'Modern text filter was not applied');

    $qtype = question_bank::get_qtype('momopda', false);
    momopda_assert($qtype instanceof qtype_momopda, 'Question type did not register');
    momopda_assert(!$qtype->is_real_question_type(), 'Question type must remain an information item');

    $admin = get_admin();
    core\session\manager::set_user($admin);
    momopda_assert(get_capability_info('report/momopda:view') !== null, 'Report capability is missing');
    $adminroot = admin_get_root(true, true);
    $reportpage = $adminroot->locate('reportmomopda');
    momopda_assert($reportpage instanceof admin_externalpage, 'Report admin page is missing');
    momopda_assert($reportpage->url->compare(new moodle_url('/report/momopda/index.php')), 'Report admin URL is wrong');

    momopda_assert(class_exists(tiny_momopda\plugininfo::class), 'TinyMCE plugininfo class is missing');
    momopda_assert(
        is_subclass_of(tiny_momopda\plugininfo::class, editor_tiny\plugin::class),
        'TinyMCE plugininfo has the wrong base class',
    );
    momopda_assert(
        tiny_momopda\plugininfo::is_enabled(
            context_system::instance(),
            ['pluginname' => 'momopda'],
            [],
        ),
        'TinyMCE plugininfo is not enabled',
    );
    $configuration = (new editor_tiny\manager())->get_plugin_configuration(context_system::instance());
    momopda_assert(array_key_exists('tiny_momopda/plugin', $configuration), 'TinyMCE plugin is not enabled');

    echo 'All fixture installation and bootstrap contracts passed.' . PHP_EOL;
} catch (Throwable $exception) {
    fwrite(STDERR, 'ERROR: ' . $exception->getMessage() . PHP_EOL);
    exit(1);
}
