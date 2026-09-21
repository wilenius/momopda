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
 * Public runtime assertions for the TinyMCE toolbar-button evaluation.
 *
 * @package    tiny_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace tiny_momopda;

use editor_tiny\manager;
use editor_tiny\plugin_with_buttons;
use editor_tiny\plugininfo\tiny;

/**
 * Exercises the submitted PHP contract and shipped AMD through pinned Moodle and Node runtimes.
 */
final class harness_contract_test extends \advanced_testcase {
    /** @var string Fully qualified button advertised to Moodle. */
    private const ADVERTISED_BUTTON = 'tiny_momopda/tiny_momopda';

    /** @var string Sentinel returned only for the required language-string request. */
    private const TRANSLATION_SENTINEL = 'MOMOPDA translated button sentinel';

    /**
     * Verifies complete, reproducible AMD build and source-map artifacts.
     */
    public function test_amd_build(): void {
        global $CFG;

        $this->resetAfterTest();
        $pluginroot = $CFG->dirroot . '/lib/editor/tiny/plugins/momopda';
        $sourcefiles = $this->tree_hashes($pluginroot . '/amd/src');
        $this->assertNotEmpty($sourcefiles, 'The plugin must contain at least one AMD source module');

        $expectedbuild = [];
        foreach (array_keys($sourcefiles) as $sourcefile) {
            if (!str_ends_with($sourcefile, '.js')) {
                continue;
            }
            $buildfile = substr($sourcefile, 0, -3) . '.min.js';
            $expectedbuild[] = $buildfile;
            $expectedbuild[] = $buildfile . '.map';
        }
        sort($expectedbuild);
        $submittedbuild = $this->tree_hashes($pluginroot . '/amd/build');
        $this->assertSame(
            $expectedbuild,
            array_keys($submittedbuild),
            'Every AMD source must have exactly one submitted build and source map',
        );

        $moodleroot = dirname($CFG->dirroot);
        $commitresult = $this->run_command(['git', '-C', $moodleroot, 'rev-parse', 'HEAD'], $moodleroot);
        $this->assert_command_passed($commitresult, 'Could not identify the disposable Moodle revision');
        $commit = trim($commitresult['stdout']);
        $this->assertSame('acfa383c13dd46c83ca82894a8e95fac273fda33', $commit);
        $this->assertDirectoryExists($moodleroot . '/node_modules');

        $temporary = make_temp_directory('tiny_momopda_amd_' . bin2hex(random_bytes(8)));
        $moodlecopy = $temporary . '/moodle';
        try {
            $cloneresult = $this->run_command(
                ['git', 'clone', '--shared', '--no-checkout', $moodleroot, $moodlecopy],
                $temporary,
            );
            $this->assert_command_passed($cloneresult, 'Could not create a clean Moodle build tree');
            $checkoutresult = $this->run_command(
                ['git', '-C', $moodlecopy, 'checkout', '--detach', $commit],
                $temporary,
            );
            $this->assert_command_passed($checkoutresult, 'Could not check out the pinned Moodle build tree');

            $copyplugin = $moodlecopy . '/public/lib/editor/tiny/plugins/momopda';
            $this->copy_tree($pluginroot, $copyplugin);
            remove_dir($copyplugin . '/amd/build');
            make_writable_directory($copyplugin . '/amd/build');
            $this->assertTrue(
                symlink($moodleroot . '/node_modules', $moodlecopy . '/node_modules'),
                'Could not attach the pinned Moodle Node dependencies',
            );

            $buildresult = $this->run_command(
                [
                    $moodlecopy . '/node_modules/.bin/grunt',
                    'amd',
                    '--root=public/lib/editor/tiny/plugins/momopda',
                    '--no-color',
                ],
                $moodlecopy,
            );
            $this->assert_command_passed($buildresult, 'The clean component-scoped Grunt AMD build failed');
            $buildoutput = $buildresult['stdout'] . $buildresult['stderr'];
            $this->assertStringContainsString('Done.', $buildoutput);
            $this->assertDoesNotMatchRegularExpression('/(?:^|\R)(?:>> )?Warning:/i', $buildoutput);
            $this->assertSame(
                $submittedbuild,
                $this->tree_hashes($copyplugin . '/amd/build'),
                'The clean Grunt build does not reproduce the submitted JavaScript and source maps',
            );
        } finally {
            if (is_link($moodlecopy . '/node_modules')) {
                unlink($moodlecopy . '/node_modules');
            }
            remove_dir($temporary);
        }
    }

    /**
     * Verifies the PHP advertisement, real manager output, built registration, and toolbar placement.
     */
    public function test_plugin_manager_registration(): void {
        $this->resetAfterTest();
        $this->setAdminUser();
        $this->assertTrue(is_a(plugininfo::class, plugin_with_buttons::class, true));
        $this->assertSame([self::ADVERTISED_BUTTON], plugininfo::get_available_buttons());

        tiny::enable_plugin('momopda', 1);
        $configuration = (new manager())->get_plugin_configuration(\context_system::instance());
        $this->assertArrayHasKey('tiny_momopda/plugin', $configuration);
        $this->assertSame(
            [self::ADVERTISED_BUTTON],
            $configuration['tiny_momopda/plugin']['buttons'] ?? null,
        );

        $result = $this->run_node_probe('plugin-manager-registration');
        $this->assertSame('tiny_momopda/plugin', $result['pluginName'] ?? null);
        $this->assertSame('tiny_momopda', $result['registeredButton'] ?? null);
        $this->assertSame(
            [
                ['name' => 'formatting', 'items' => ['bold']],
                ['name' => 'content', 'items' => ['link', 'tiny_momopda']],
            ],
            $result['toolbar'] ?? null,
        );
    }

    /**
     * Verifies the language key and asynchronous localization boundary in the submitted build.
     */
    public function test_localized_tooltip(): void {
        $this->resetAfterTest();
        $this->assertTrue(get_string_manager()->string_exists('buttontitle', 'tiny_momopda'));

        $result = $this->run_node_probe('localized-tooltip');
        $this->assertSame(self::TRANSLATION_SENTINEL, $result['tooltip'] ?? null);
        $this->assertContains(
            ['key' => 'buttontitle', 'component' => 'tiny_momopda'],
            $result['stringCalls'] ?? [],
        );
    }

    /**
     * Verifies command dispatch and exact insertion for collapsed and ranged selections.
     */
    public function test_semantic_insertion(): void {
        $result = $this->run_node_probe('semantic-insertion');
        $this->assertSame('mceMomopdaInsertMarker', $result['command'] ?? null);
        $this->assertSame('mceMomopdaInsertMarker', $result['buttonCommand'] ?? null);
        $this->assertSame(
            [
                'content' => '<mark class="tiny_momopda-marker">MoMoPDA</mark>',
                'selectionMode' => 'ranged',
            ],
            $result['insertion'] ?? null,
        );
    }

    /**
     * Runs one phase of the dependency-free AMD probe against submitted build artifacts.
     *
     * @param string $phase Public check identifier.
     * @return array<string, mixed> Probe result.
     */
    private function run_node_probe(string $phase): array {
        global $CFG;

        $temporary = make_temp_directory('tiny_momopda_probe_' . bin2hex(random_bytes(8)));
        $probefile = $temporary . '/amd-probe.js';
        try {
            $this->assertNotFalse(file_put_contents($probefile, $this->node_probe_source()));
            $result = $this->run_command(
                [
                    'node',
                    $probefile,
                    $phase,
                    $CFG->dirroot . '/lib/editor/tiny/plugins/momopda',
                ],
                $temporary,
            );
            $this->assert_command_passed($result, "The submitted AMD failed the {$phase} runtime probe");
            preg_match_all('/^MOMOPDA_PROBE:(\{.*\})$/m', $result['stdout'], $matches);
            $this->assertCount(1, $matches[1], 'The Node probe did not return one terminal result');
            $document = json_decode($matches[1][0], true, 512, JSON_THROW_ON_ERROR);
            $this->assertIsArray($document);
            $this->assertSame('pass', $document['status'] ?? null);
            $this->assertIsArray($document['result'] ?? null);
            return $document['result'];
        } finally {
            remove_dir($temporary);
        }
    }

    /**
     * Executes a command without invoking a shell.
     *
     * @param string[] $command Argument vector.
     * @param string $cwd Working directory.
     * @return array{exitcode: int, stdout: string, stderr: string}
     */
    private function run_command(array $command, string $cwd): array {
        $descriptors = [
            0 => ['pipe', 'r'],
            1 => ['pipe', 'w'],
            2 => ['pipe', 'w'],
        ];
        $process = proc_open($command, $descriptors, $pipes, $cwd, null, ['bypass_shell' => true]);
        $this->assertIsResource($process, 'Could not start required grader process');
        fclose($pipes[0]);
        $stdout = stream_get_contents($pipes[1]);
        fclose($pipes[1]);
        $stderr = stream_get_contents($pipes[2]);
        fclose($pipes[2]);
        $exitcode = proc_close($process);
        return [
            'exitcode' => $exitcode,
            'stdout' => $stdout,
            'stderr' => $stderr,
        ];
    }

    /**
     * Asserts successful command completion while preserving diagnostics.
     *
     * @param array $result Process result.
     * @param string $message Failure description.
     */
    private function assert_command_passed(array $result, string $message): void {
        $diagnostic = trim($result['stdout'] . "\n" . $result['stderr']);
        $this->assertSame(0, $result['exitcode'], $message . "\n" . $diagnostic);
    }

    /**
     * Returns stable SHA-256 hashes for every file in a tree.
     *
     * @param string $root Tree root.
     * @return array<string, string>
     */
    private function tree_hashes(string $root): array {
        $this->assertDirectoryExists($root);
        $hashes = [];
        $iterator = new \RecursiveIteratorIterator(
            new \RecursiveDirectoryIterator($root, \FilesystemIterator::SKIP_DOTS),
        );
        foreach ($iterator as $file) {
            $this->assertFalse($file->isLink(), 'AMD trees must not contain symbolic links');
            if (!$file->isFile()) {
                continue;
            }
            $relative = substr($file->getPathname(), strlen($root) + 1);
            $relative = str_replace(DIRECTORY_SEPARATOR, '/', $relative);
            $hash = hash_file('sha256', $file->getPathname());
            $this->assertIsString($hash);
            $hashes[$relative] = $hash;
        }
        ksort($hashes);
        return $hashes;
    }

    /**
     * Copies a plugin tree without accepting symbolic links.
     *
     * @param string $source Source directory.
     * @param string $destination New destination directory.
     */
    private function copy_tree(string $source, string $destination): void {
        $this->assertDirectoryDoesNotExist($destination);
        make_writable_directory($destination);
        $iterator = new \RecursiveIteratorIterator(
            new \RecursiveDirectoryIterator($source, \FilesystemIterator::SKIP_DOTS),
            \RecursiveIteratorIterator::SELF_FIRST,
        );
        foreach ($iterator as $item) {
            $this->assertFalse($item->isLink(), 'Plugin trees must not contain symbolic links');
            $relative = substr($item->getPathname(), strlen($source) + 1);
            $target = $destination . '/' . $relative;
            if ($item->isDir()) {
                make_writable_directory($target);
            } else {
                $this->assertTrue(copy($item->getPathname(), $target));
            }
        }
    }

    /**
     * Returns the dependency-free Node AMD runtime probe.
     *
     * @return string
     */
    private function node_probe_source(): string {
        return <<<'JS'
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const phase = process.argv[2];
const pluginRoot = path.resolve(process.argv[3]);
const component = 'tiny_momopda';
const pluginName = `${component}/plugin`;
const buttonName = 'tiny_momopda';
const commandName = 'mceMomopdaInsertMarker';
const marker = '<mark class="tiny_momopda-marker">MoMoPDA</mark>';
const sentinel = 'MOMOPDA translated button sentinel';
const definitions = new Map();
const instances = new Map();
const registrations = [];
const stringCalls = [];
const buttonRegistrations = [];
const commandRegistrations = new Map();
const execCalls = [];
const insertCalls = [];
const deprecatedInsertCalls = [];
let selectionMode = 'collapsed';
let localizedStringSettled = phase !== 'localized-tooltip';
let releaseLocalizedString = null;

const delayedLocalizedString = new Promise(resolve => {
    releaseLocalizedString = () => {
        localizedStringSettled = true;
        resolve(sentinel);
    };
});

const getString = (key, requestedComponent) => {
    stringCalls.push({key, component: requestedComponent});
    if (phase === 'localized-tooltip' && key === 'buttontitle' && requestedComponent === component) {
        return delayedLocalizedString;
    }
    return Promise.resolve(`decoy:${requestedComponent}/${key}`);
};

const addToolbarButton = (toolbar, section, button) => {
    const output = JSON.parse(JSON.stringify(toolbar || []));
    const target = output.find(group => group.name === section);
    if (target) {
        target.items.push(button);
    }
    return output;
};

const addToolbarButtons = (toolbar, section, buttons) => {
    let output = toolbar;
    for (const button of buttons) {
        output = addToolbarButton(output, section, button);
    }
    return output;
};

const tinyMCE = {
    PluginManager: {
        add(name, callback) {
            registrations.push({
                name,
                callback,
                beforeLocalizedString: !localizedStringSettled,
            });
        },
    },
};

const mocks = new Map([
    ['editor_tiny/loader', {
        getTinyMCE: () => Promise.resolve(tinyMCE),
    }],
    ['editor_tiny/utils', {
        addToolbarButton,
        addToolbarButtons,
        getButtonImage: () => Promise.resolve({html: '<svg></svg>'}),
        getPluginMetadata: async(requestedComponent, requestedPlugin) => ({
            getMetadata: () => ({name: requestedComponent, url: requestedPlugin}),
        }),
    }],
    ['core/str', {
        getString,
        get_string: getString,
    }],
]);

const define = (name, dependencies, factory) => {
    assert.equal(typeof name, 'string', 'AMD module must have a generated name');
    assert.ok(Array.isArray(dependencies), `AMD dependencies for ${name} must be an array`);
    assert.equal(typeof factory, 'function', `AMD factory for ${name} must be callable`);
    assert.ok(!definitions.has(name), `AMD module ${name} was defined more than once`);
    definitions.set(name, {dependencies, factory});
};
define.amd = {};

const sandbox = {
    clearInterval,
    clearTimeout,
    console,
    define,
    Promise,
    setInterval,
    setTimeout,
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
const context = vm.createContext(sandbox);

const normalizeDependency = (dependency, parent) => {
    if (!dependency.startsWith('.')) {
        return dependency;
    }
    return path.posix.normalize(path.posix.join(path.posix.dirname(parent), dependency));
};

const loadDefinition = moduleName => {
    if (definitions.has(moduleName)) {
        return;
    }
    assert.ok(moduleName.startsWith(`${component}/`), `Unsupported AMD dependency ${moduleName}`);
    const relativeName = moduleName.slice(component.length + 1);
    assert.match(relativeName, /^[a-zA-Z0-9_/-]+$/, `Unsafe AMD module name ${moduleName}`);
    const buildFile = path.join(pluginRoot, 'amd', 'build', `${relativeName}.min.js`);
    const isFile = fs.existsSync(buildFile) && fs.statSync(buildFile).isFile();
    assert.ok(isFile, `Missing submitted AMD build ${buildFile}`);
    vm.runInContext(fs.readFileSync(buildFile, 'utf8'), context, {
        filename: buildFile,
        timeout: 5000,
    });
    assert.ok(definitions.has(moduleName), `Built file did not define ${moduleName}`);
};

const instantiate = moduleName => {
    if (mocks.has(moduleName)) {
        return Promise.resolve(mocks.get(moduleName));
    }
    if (instances.has(moduleName)) {
        return instances.get(moduleName);
    }
    loadDefinition(moduleName);
    const definition = definitions.get(moduleName);
    const promise = Promise.all(definition.dependencies.map(dependency => {
        if (dependency === 'exports') {
            return {};
        }
        return instantiate(normalizeDependency(dependency, moduleName));
    })).then(dependencies => {
        const exportIndex = definition.dependencies.indexOf('exports');
        const exports = exportIndex === -1 ? {} : dependencies[exportIndex];
        const returned = definition.factory(...dependencies);
        return returned === undefined ? exports : returned;
    });
    instances.set(moduleName, promise);
    return promise;
};

const withTimeout = (promise, label) => new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error(`${label} timed out`)), 5000);
    promise.then(value => {
        clearTimeout(timer);
        resolve(value);
    }, error => {
        clearTimeout(timer);
        reject(error);
    });
});

const flush = () => new Promise(resolve => setImmediate(resolve));

const editor = {
    addCommand(name, callback) {
        assert.equal(typeof callback, 'function', `Command ${name} callback must be callable`);
        assert.ok(!commandRegistrations.has(name), `Command ${name} registered more than once`);
        commandRegistrations.set(name, callback);
    },
    execCommand(name, ...args) {
        execCalls.push({name, args});
        const command = commandRegistrations.get(name);
        assert.ok(command, `Button executed unregistered command ${name}`);
        return command(...args);
    },
    insertContent(content) {
        insertCalls.push({content, selectionMode});
    },
    selection: {
        setContent(content) {
            deprecatedInsertCalls.push({content, selectionMode});
        },
    },
    ui: {
        registry: {
            addButton(name, specification) {
                buttonRegistrations.push({kind: 'button', name, specification});
            },
            addToggleButton(name, specification) {
                buttonRegistrations.push({kind: 'toggle', name, specification});
            },
            addIcon() {},
        },
    },
};

const loadPlugin = async() => {
    const pluginPromise = instantiate(pluginName);
    await flush();
    const registeredBeforeRelease = registrations.length > 0;
    if (phase === 'localized-tooltip') {
        releaseLocalizedString();
    }
    const pluginValue = await withTimeout(pluginPromise, 'plugin promise');
    assert.equal(registrations.length, 1, 'PluginManager.add must run exactly once');
    assert.equal(registrations[0].name, pluginName, 'PluginManager.add used the wrong plugin name');
    assert.equal(typeof registrations[0].callback, 'function', 'Plugin callback must be callable');
    registrations[0].callback(editor);
    assert.equal(buttonRegistrations.length, 1, 'Plugin must register exactly one toolbar button');
    assert.equal(buttonRegistrations[0].kind, 'button', 'Marker control must be a regular toolbar button');
    assert.equal(buttonRegistrations[0].name, buttonName, 'Plugin registered the wrong button name');
    return {pluginValue, registeredBeforeRelease};
};

const checkManagerRegistration = async() => {
    const {pluginValue} = await loadPlugin();
    assert.ok(Array.isArray(pluginValue), 'Plugin promise must resolve to the name/configuration tuple');
    assert.equal(pluginValue.length, 2, 'Plugin tuple must contain a name and configuration');
    assert.equal(pluginValue[0], pluginName, 'Plugin promise resolved the wrong plugin name');
    assert.equal(typeof pluginValue[1], 'object', 'Plugin configuration must be an object');
    assert.equal(typeof pluginValue[1].configure, 'function', 'Plugin configuration must provide configure()');

    const instanceConfig = {
        toolbar: [
            {name: 'formatting', items: ['bold']},
            {name: 'content', items: ['link']},
        ],
    };
    const override = pluginValue[1].configure(instanceConfig, {});
    if (override && typeof override === 'object') {
        Object.assign(instanceConfig, override);
    }
    const contentSections = instanceConfig.toolbar.filter(section => section.name === 'content');
    assert.equal(contentSections.length, 1, 'Toolbar must retain exactly one content section');
    const buttonCount = contentSections[0].items.filter(item => item === buttonName).length;
    assert.equal(buttonCount, 1, 'Configuration must add tiny_momopda once to the content toolbar');
    return {
        pluginName: pluginValue[0],
        registeredButton: buttonRegistrations[0].name,
        toolbar: instanceConfig.toolbar,
    };
};

const checkLocalizedTooltip = async() => {
    const {registeredBeforeRelease} = await loadPlugin();
    assert.equal(registeredBeforeRelease, false, 'Plugin registered before the button string settled');
    assert.equal(registrations[0].beforeLocalizedString, false, 'PluginManager.add ran before localization settled');
    const requested = stringCalls.some(call => call.key === 'buttontitle' && call.component === component);
    assert.ok(requested, 'Plugin did not request tiny_momopda/buttontitle');
    assert.equal(buttonRegistrations[0].specification.tooltip, sentinel, 'Tooltip was not localized');
    return {
        stringCalls,
        tooltip: buttonRegistrations[0].specification.tooltip,
    };
};

const assertOneInsertion = (mode, label) => {
    const expected = [{content: marker, selectionMode: mode}];
    assert.deepEqual(insertCalls, expected, `${label} inserted the wrong content`);
    assert.deepEqual(deprecatedInsertCalls, [], `${label} used deprecated selection.setContent()`);
};

const checkSemanticInsertion = async() => {
    await loadPlugin();
    assert.deepEqual([...commandRegistrations.keys()], [commandName], 'Plugin registered the wrong command');
    const action = buttonRegistrations[0].specification.onAction;
    assert.equal(typeof action, 'function', 'Button needs an onAction callback');
    assert.deepEqual(insertCalls, [], 'Plugin inserted content during registration');

    selectionMode = 'collapsed';
    await commandRegistrations.get(commandName)();
    assertOneInsertion('collapsed', 'Collapsed command');

    insertCalls.length = 0;
    deprecatedInsertCalls.length = 0;
    selectionMode = 'ranged';
    await commandRegistrations.get(commandName)();
    assertOneInsertion('ranged', 'Ranged command');

    insertCalls.length = 0;
    deprecatedInsertCalls.length = 0;
    execCalls.length = 0;
    selectionMode = 'ranged';
    await action();
    await flush();
    const executedCommands = execCalls.map(call => call.name);
    assert.deepEqual(executedCommands, [commandName], 'Button did not execute the named command exactly once');
    assertOneInsertion('ranged', 'Button action');
    return {
        command: commandName,
        buttonCommand: execCalls[0].name,
        insertion: insertCalls[0],
    };
};

const run = async() => {
    if (phase === 'plugin-manager-registration') {
        return checkManagerRegistration();
    }
    if (phase === 'localized-tooltip') {
        return checkLocalizedTooltip();
    }
    if (phase === 'semantic-insertion') {
        return checkSemanticInsertion();
    }
    throw new Error(`Unknown probe phase ${phase}`);
};

run().then(result => {
    process.stdout.write(`MOMOPDA_PROBE:${JSON.stringify({status: 'pass', result})}\n`);
}).catch(error => {
    process.stderr.write(`${error.stack || error}\n`);
    process.stdout.write(`MOMOPDA_PROBE:${JSON.stringify({status: 'fail', error: error.message})}\n`);
    process.exitCode = 1;
});
JS;
    }
}
