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
 * Public runtime assertions for the question-bank bulk-action evaluation.
 *
 * @package    qbank_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace qbank_momopda;

use core_question\local\bank\bulk_action_base;
use core_question\local\bank\question_edit_contexts;
use core_question\local\bank\question_version_status;
use core_question\local\bank\view;

/**
 * Exercises the generated action and endpoint through the pinned Moodle runtime.
 */
final class harness_contract_test extends \advanced_testcase {
    /** @var string Capability required by the task contract. */
    private const ACTION_CAPABILITY = 'qbank/momopda:use';

    /**
     * Verifies POST and sesskey enforcement at both request stages.
     */
    public function test_sesskey(): void {
        $bank = $this->create_bank('Sesskey bank');
        $question = $this->create_question($bank, 'Sesskey question');
        $actiondata = $this->discover_action($bank);
        $returnurl = $this->bank_url($bank);
        $valid = $this->selection_params($bank, $actiondata['action'], [$question->id], $returnurl);

        $getresult = $this->execute_endpoint($actiondata['endpoint'], 'GET', $valid);
        $this->assert_ready($question->id);
        $this->assertNull($this->find_confirmation_form($getresult['output'], $actiondata['urlpath']));

        $missing = $valid;
        unset($missing['sesskey']);
        $this->execute_endpoint($actiondata['endpoint'], 'POST', $missing);
        $this->assert_ready($question->id);

        $invalid = $valid;
        $invalid['sesskey'] = 'invalid-sesskey';
        $this->execute_endpoint($actiondata['endpoint'], 'POST', $invalid);
        $this->assert_ready($question->id);

        $confirmation = $this->request_confirmation($actiondata, $valid, [$question->id]);
        $this->assert_ready($question->id);

        $missingfinal = $confirmation['params'];
        unset($missingfinal['sesskey']);
        $this->execute_endpoint($actiondata['endpoint'], 'POST', $missingfinal);
        $this->assert_ready($question->id);

        $invalidfinal = $confirmation['params'];
        $invalidfinal['sesskey'] = 'invalid-sesskey';
        $this->execute_endpoint($actiondata['endpoint'], 'POST', $invalidfinal);
        $this->assert_ready($question->id);
    }

    /**
     * Verifies the advertised capability, origin context, and bank containment.
     */
    public function test_context_capability(): void {
        $bank = $this->create_bank('Origin bank');
        $otherbank = $this->create_bank('Other bank', $bank['course']);
        $question = $this->create_question($bank, 'Origin question');
        $otherquestion = $this->create_question($otherbank, 'Other-bank question');
        $actiondata = $this->discover_action($bank);

        $capability = get_capability_info(self::ACTION_CAPABILITY);
        $this->assertNotNull($capability);
        $this->assertSame(CONTEXT_MODULE, (int) $capability->contextlevel);
        $this->assertSame([self::ACTION_CAPABILITY], $actiondata['action']->get_bulk_action_capabilities());

        $user = $this->getDataGenerator()->create_user();
        $roleid = $this->create_bank_role($bank, $user);
        $this->set_role_capability($roleid, $bank['context'], 'moodle/question:editall', CAP_ALLOW);
        $this->set_role_capability($roleid, $otherbank['context'], 'moodle/question:editall', CAP_ALLOW);
        $this->assertFalse(has_capability(self::ACTION_CAPABILITY, $bank['context'], $user));

        $returnurl = $this->bank_url($bank);
        $params = $this->selection_params($bank, $actiondata['action'], [$question->id], $returnurl);
        $this->setUser($user);
        $params['sesskey'] = sesskey();
        $result = $this->execute_endpoint($actiondata['endpoint'], 'POST', $params);
        $confirmation = $this->find_confirmation_form($result['output'], $actiondata['urlpath']);
        if ($confirmation !== null) {
            $this->execute_endpoint($actiondata['endpoint'], 'POST', $confirmation['params']);
        }
        $this->assert_ready($question->id);

        $this->set_role_capability($roleid, $bank['context'], self::ACTION_CAPABILITY, CAP_ALLOW);
        $this->assertTrue(has_capability(self::ACTION_CAPABILITY, $bank['context'], $user));

        $this->setAdminUser();
        $crossbank = $this->selection_params($bank, $actiondata['action'], [$otherquestion->id], $returnurl);
        $result = $this->execute_endpoint($actiondata['endpoint'], 'POST', $crossbank);
        $crossconfirmation = $this->find_confirmation_form($result['output'], $actiondata['urlpath']);
        if ($crossconfirmation !== null) {
            $this->execute_endpoint($actiondata['endpoint'], 'POST', $crossconfirmation['params']);
        }
        $this->assert_ready($otherquestion->id);
    }

    /**
     * Verifies ownership-aware final authorization and all-or-nothing updates.
     */
    public function test_per_question_capability(): void {
        $bank = $this->create_bank('Authorization bank');
        $owner = $this->getDataGenerator()->create_user();
        $otherowner = $this->getDataGenerator()->create_user();
        $owned = $this->create_question($bank, 'Owned question', $owner->id);
        $notowned = $this->create_question($bank, 'Other-owned question', $otherowner->id);
        $control = $this->create_question($bank, 'Control question', $owner->id);
        $actiondata = $this->discover_action($bank);
        $roleid = $this->create_bank_role($bank, $owner);
        $this->set_role_capability($roleid, $bank['context'], self::ACTION_CAPABILITY, CAP_ALLOW);
        $this->set_role_capability($roleid, $bank['context'], 'moodle/question:editmine', CAP_ALLOW);
        $this->setUser($owner);

        $returnurl = $this->bank_url($bank);
        $ownparams = $this->selection_params($bank, $actiondata['action'], [$owned->id], $returnurl);
        $ownconfirmation = $this->request_confirmation($actiondata, $ownparams, [$owned->id]);
        $this->execute_endpoint($actiondata['endpoint'], 'POST', $ownconfirmation['params']);
        $this->assert_draft($owned->id);
        $this->set_ready($owned->id);

        $mixedparams = $this->selection_params(
            $bank,
            $actiondata['action'],
            [$owned->id, $notowned->id],
            $returnurl,
        );
        $mixedresult = $this->execute_endpoint($actiondata['endpoint'], 'POST', $mixedparams);
        $mixedconfirmation = $this->find_confirmation_form($mixedresult['output'], $actiondata['urlpath']);
        if ($mixedconfirmation !== null) {
            $this->execute_endpoint($actiondata['endpoint'], 'POST', $mixedconfirmation['params']);
        }
        $this->assert_ready($owned->id);
        $this->assert_ready($notowned->id);

        $this->set_role_capability($roleid, $bank['context'], 'moodle/question:editall', CAP_ALLOW);
        $confirmed = $this->request_confirmation($actiondata, $mixedparams, [$owned->id, $notowned->id]);
        $this->set_role_capability($roleid, $bank['context'], 'moodle/question:editall', CAP_PROHIBIT);
        $confirmed['params']['sesskey'] = sesskey();
        $this->execute_endpoint($actiondata['endpoint'], 'POST', $confirmed['params']);
        $this->assert_ready($owned->id);
        $this->assert_ready($notowned->id);

        $this->set_role_capability($roleid, $bank['context'], 'moodle/question:editall', CAP_ALLOW);
        $confirmed = $this->request_confirmation($actiondata, $mixedparams, [$owned->id, $notowned->id]);
        $this->execute_endpoint($actiondata['endpoint'], 'POST', $confirmed['params']);
        $this->assert_draft($owned->id);
        $this->assert_draft($notowned->id);
        $this->assert_ready($control->id);
    }

    /**
     * Verifies a distinct non-mutating confirmation and the exact final mutation.
     */
    public function test_confirmation(): void {
        $bank = $this->create_bank('Confirmation bank');
        $first = $this->create_question($bank, 'First selected question');
        $second = $this->create_question($bank, 'Second selected question');
        $control = $this->create_question($bank, 'Unselected control question');
        $actiondata = $this->discover_action($bank);
        $params = $this->selection_params(
            $bank,
            $actiondata['action'],
            [$first->id, $second->id],
            $this->bank_url($bank),
        );

        $confirmation = $this->request_confirmation($actiondata, $params, [$first->id, $second->id]);
        $this->assertStringContainsString('First selected question', $confirmation['output']);
        $this->assertStringContainsString('Second selected question', $confirmation['output']);
        $this->assert_ready($first->id);
        $this->assert_ready($second->id);
        $this->assert_ready($control->id);

        $cancel = $this->find_cancel_target($confirmation['output']);
        $this->assertSame($this->canonical_url($this->bank_url($bank)), $this->canonical_url($cancel));
        $this->assert_ready($first->id);
        $this->assert_ready($second->id);

        $malformed = $confirmation['params'];
        foreach (array_keys($malformed) as $name) {
            if (str_contains(strtolower($name), 'confirm')) {
                unset($malformed[$name]);
            }
        }
        $this->execute_endpoint($actiondata['endpoint'], 'POST', $malformed);
        $this->assert_ready($first->id);
        $this->assert_ready($second->id);

        $sink = $this->redirectEvents();
        $result = $this->execute_endpoint($actiondata['endpoint'], 'POST', $confirmation['params']);
        $events = array_filter(
            $sink->get_events(),
            static fn(\core\event\base $event): bool => $event instanceof \core\event\question_updated,
        );
        $sink->close();
        $this->assertNull($result['exception']);
        $this->assertNotNull($result['redirect']);
        $this->assertCount(2, $events);
        $this->assert_draft($first->id);
        $this->assert_draft($second->id);
        $this->assert_ready($control->id);
    }

    /**
     * Verifies preservation of local origins and safe fallback behavior.
     */
    public function test_safe_return(): void {
        global $CFG;

        $bank = $this->create_bank('Return bank');
        $question = $this->create_question($bank, 'Return question');
        $actiondata = $this->discover_action($bank);
        $validreturn = new \moodle_url('/question/edit.php', [
            'cmid' => $bank['cm']->id,
            'cat' => $bank['category']->id . ',' . $bank['context']->id,
            'qpage' => 2,
        ]);
        $validlocal = $validreturn->out_as_local_url(false);
        $params = $this->selection_params($bank, $actiondata['action'], [$question->id], $validlocal);
        $confirmation = $this->request_confirmation($actiondata, $params, [$question->id]);
        $this->assertSame($validreturn->out(false), $this->canonical_url($this->find_cancel_target($confirmation['output'])));
        $result = $this->execute_endpoint($actiondata['endpoint'], 'POST', $confirmation['params']);
        $this->assertSame($validreturn->out(false), $this->canonical_url($result['redirect']));
        $this->assertStringNotContainsString('/public/', $result['redirect']);

        $fallback = new \moodle_url('/question/edit.php', ['cmid' => $bank['cm']->id]);
        $unsafe = [
            'https://evil.example.invalid/steal',
            '//evil.example.invalid/steal',
            $CFG->wwwroot . '.evil.invalid/steal',
            'javascript:alert(1)',
            'not a valid url',
            '',
        ];
        foreach ($unsafe as $index => $returntarget) {
            $this->set_ready($question->id);
            $params = $this->selection_params($bank, $actiondata['action'], [$question->id], $returntarget);
            $confirmation = $this->request_confirmation($actiondata, $params, [$question->id]);
            $cancel = $this->find_cancel_target($confirmation['output']);
            $this->assertSame($fallback->out(false), $this->canonical_url($cancel), "Unsafe case {$index} cancellation");
            $this->assertStringNotContainsString('/public/', $cancel);
            $this->assertStringNotContainsString('<script', strtolower($confirmation['output']));

            $result = $this->execute_endpoint($actiondata['endpoint'], 'POST', $confirmation['params']);
            $this->assertSame(
                $fallback->out(false),
                $this->canonical_url($result['redirect']),
                "Unsafe case {$index} success",
            );
            $this->assertStringNotContainsString('/public/', $result['redirect']);
        }
        $this->assertStringNotContainsString('/public/', $actiondata['action']->get_bulk_action_url()->out(false));
    }

    /**
     * Creates an activity-backed question bank.
     *
     * @param string $name Bank name.
     * @param \stdClass|null $course Existing course, if any.
     * @return array<string, mixed>
     */
    private function create_bank(string $name, ?\stdClass $course = null): array {
        $this->resetAfterTest();
        $this->setAdminUser();
        $generator = $this->getDataGenerator();
        $course = $course ?? $generator->create_course();
        $instance = $generator->create_module('qbank', ['course' => $course->id, 'name' => $name]);
        $cm = get_coursemodule_from_instance('qbank', $instance->id, $course->id, false, MUST_EXIST);
        $context = \context_module::instance($cm->id);
        $category = question_get_default_category($context->id, true);

        return compact('course', 'instance', 'cm', 'context', 'category');
    }

    /**
     * Creates a ready question in a bank.
     *
     * @param array $bank Bank data.
     * @param string $name Question name.
     * @param int|null $createdby Creator ID.
     * @return \stdClass
     */
    private function create_question(array $bank, string $name, ?int $createdby = null): \stdClass {
        $overrides = ['category' => $bank['category']->id, 'name' => $name];
        if ($createdby !== null) {
            $overrides['createdby'] = $createdby;
        }
        return $this->getDataGenerator()->get_plugin_generator('core_question')->create_question(
            'truefalse',
            null,
            $overrides,
        );
    }

    /**
     * Discovers the generated action from a real view and resolves its endpoint.
     *
     * @param array $bank Bank data.
     * @return array<string, mixed>
     */
    private function discover_action(array $bank): array {
        global $CFG;

        $pageurl = $this->bank_url($bank);
        $params = [
            'cat' => $bank['category']->id . ',' . $bank['context']->id,
            'qpage' => 0,
            'qperpage' => 20,
        ];
        $view = new view(
            new question_edit_contexts($bank['context']),
            $pageurl,
            $bank['course'],
            $bank['cm'],
            $params,
        );
        $pluginactions = (new plugin_feature())->get_bulk_actions($view);
        $this->assertCount(1, $pluginactions);
        $pluginaction = reset($pluginactions);
        $this->assertInstanceOf(bulk_action_base::class, $pluginaction);
        $this->assertArrayHasKey($pluginaction->get_key(), $view->bulkactions);
        $action = $view->bulkactions[$pluginaction->get_key()];
        $this->assertSame($pluginaction::class, $action::class);

        $actionurl = $action->get_bulk_action_url();
        $localurl = $actionurl->out_as_local_url(false);
        $this->assertStringStartsWith('/question/bank/momopda/', $localurl);
        $this->assertStringNotContainsString('/public/', $localurl);
        $url = $actionurl->out(false);
        $urlpath = parse_url($url, PHP_URL_PATH);
        $this->assertIsString($urlpath);
        $this->assertStringNotContainsString('/public/', $urlpath);
        $endpoint = $CFG->dirroot . substr($urlpath, strlen(parse_url($CFG->wwwroot, PHP_URL_PATH) ?: ''));
        $this->assertFileExists($endpoint);
        $this->assertStringStartsWith(realpath($CFG->dirroot . '/question/bank/momopda'), realpath($endpoint));

        return compact('action', 'endpoint', 'urlpath');
    }

    /**
     * Builds the normal question-bank origin URL.
     *
     * @param array $bank Bank data.
     * @return \moodle_url
     */
    private function bank_url(array $bank): \moodle_url {
        return new \moodle_url('/question/edit.php', [
            'cmid' => $bank['cm']->id,
            'cat' => $bank['category']->id . ',' . $bank['context']->id,
        ]);
    }

    /**
     * Builds the question-bank form submission.
     *
     * @param array $bank Bank data.
     * @param bulk_action_base $action Discovered action.
     * @param int[] $questionids Selected question IDs.
     * @param \moodle_url|string $returnurl Return target.
     * @return array<string, string|int>
     */
    private function selection_params(
        array $bank,
        bulk_action_base $action,
        array $questionids,
        \moodle_url|string $returnurl,
    ): array {
        $params = [
            'cmid' => $bank['cm']->id,
            'returnurl' => $returnurl instanceof \moodle_url ? $returnurl->out_as_local_url(false) : $returnurl,
            'sesskey' => sesskey(),
            $action->get_key() => $action->get_bulk_action_title(),
        ];
        foreach ($questionids as $questionid) {
            $params['q' . $questionid] = 1;
        }
        return $params;
    }

    /**
     * Executes a candidate endpoint with simulated request globals.
     *
     * @param string $endpoint Endpoint path.
     * @param string $method HTTP method.
     * @param array $params Request parameters.
     * @return array{output: string, redirect: ?string, exception: ?\Throwable}
     */
    private function execute_endpoint(string $endpoint, string $method, array $params): array {
        global $OUTPUT, $PAGE;

        $oldget = $_GET;
        $oldpost = $_POST;
        $oldrequest = $_REQUEST;
        $oldserver = $_SERVER;
        $oldpage = $PAGE;
        $oldoutput = $OUTPUT;
        $_GET = $method === 'GET' ? $params : [];
        $_POST = $method === 'POST' ? $params : [];
        $_REQUEST = $params;
        $_SERVER['REQUEST_METHOD'] = $method;
        $_SERVER['SCRIPT_NAME'] = parse_url($this->canonical_url($endpoint), PHP_URL_PATH) ?: '';
        $PAGE = new \moodle_page();
        if (!empty($params['cmid'])) {
            [, $requestcm] = get_module_from_cmid((int) $params['cmid']);
            $PAGE->set_cm($requestcm, get_course($requestcm->course));
        }
        $OUTPUT = $PAGE->get_renderer('core');
        $redirect = null;
        $exception = null;
        ob_start();
        try {
            (static function (string $script): void {
                global $CFG, $COURSE, $DB, $OUTPUT, $PAGE, $SITE, $USER;
                include($script);
            })($endpoint);
        } catch (\Throwable $caught) {
            if (str_starts_with($caught->getMessage(), 'MOMOPDA_REDIRECT:')) {
                $redirect = substr($caught->getMessage(), strlen('MOMOPDA_REDIRECT:'));
            } else {
                $exception = $caught;
            }
        }
        $output = (string) ob_get_clean();
        $_GET = $oldget;
        $_POST = $oldpost;
        $_REQUEST = $oldrequest;
        $_SERVER = $oldserver;
        $PAGE = $oldpage;
        $OUTPUT = $oldoutput;

        return compact('output', 'redirect', 'exception');
    }

    /**
     * Submits an initial request and extracts its explicit confirmation form.
     *
     * @param array $actiondata Discovered action data.
     * @param array $params Initial request.
     * @param int[] $questionids Expected selected IDs.
     * @return array<string, mixed>
     */
    private function request_confirmation(array $actiondata, array $params, array $questionids): array {
        $result = $this->execute_endpoint($actiondata['endpoint'], 'POST', $params);
        $this->assertNull($result['exception']);
        $this->assertNull($result['redirect']);
        foreach ($questionids as $questionid) {
            $this->assert_ready($questionid);
        }
        $form = $this->find_confirmation_form($result['output'], $actiondata['urlpath']);
        $this->assertNotNull($form);
        $confirmkeys = array_filter(
            array_keys($form['params']),
            static fn(string $name): bool => str_contains(strtolower($name), 'confirm'),
        );
        $this->assertNotEmpty($confirmkeys);
        $form['output'] = $result['output'];
        return $form;
    }

    /**
     * Extracts forms within Moodle's explicit confirmation dialog.
     *
     * @param string $html Rendered page.
     * @return array<int, array{method: string, action: string, params: array<string, string>}>
     */
    private function confirmation_forms(string $html): array {
        if ($html === '') {
            return [];
        }
        $document = new \DOMDocument();
        $previous = libxml_use_internal_errors(true);
        $loaded = $document->loadHTML('<?xml encoding="utf-8" ?>' . $html);
        libxml_clear_errors();
        libxml_use_internal_errors($previous);
        if (!$loaded) {
            return [];
        }
        $xpath = new \DOMXPath($document);
        $forms = [];
        foreach ($xpath->query('//*[@role="alertdialog"]//form') ?: [] as $formnode) {
            if (!$formnode instanceof \DOMElement) {
                continue;
            }
            $action = html_entity_decode($formnode->getAttribute('action'), ENT_QUOTES | ENT_HTML5);
            $params = [];
            $query = parse_url($action, PHP_URL_QUERY);
            if (is_string($query)) {
                parse_str($query, $params);
            }
            foreach ($xpath->query('.//input[@name] | .//button[@name]', $formnode) ?: [] as $input) {
                if ($input instanceof \DOMElement) {
                    $params[$input->getAttribute('name')] = $input->getAttribute('value');
                }
            }
            $forms[] = [
                'method' => strtoupper($formnode->getAttribute('method') ?: 'GET'),
                'action' => $action,
                'params' => $params,
            ];
        }
        return $forms;
    }

    /**
     * Finds the distinct POST confirmation form for the candidate endpoint.
     *
     * @param string $html Rendered output.
     * @param string $endpointpath Endpoint URL path.
     * @return array<string, mixed>|null
     */
    private function find_confirmation_form(string $html, string $endpointpath): ?array {
        foreach ($this->confirmation_forms($html) as $form) {
            if ($form['method'] !== 'POST') {
                continue;
            }
            $actionpath = parse_url($form['action'], PHP_URL_PATH);
            if ($actionpath === $endpointpath) {
                return $form;
            }
        }
        return null;
    }

    /**
     * Returns the GET cancellation target from an explicit confirmation.
     *
     * @param string $html Rendered output.
     * @return string
     */
    private function find_cancel_target(string $html): string {
        foreach ($this->confirmation_forms($html) as $form) {
            if ($form['method'] === 'GET') {
                return (new \moodle_url($form['action'], $form['params']))->out(false);
            }
        }
        $this->fail('Explicit confirmation did not provide a GET cancellation target.');
    }

    /**
     * Canonicalizes a URL for comparison.
     *
     * @param string|\moodle_url|null $url URL value.
     * @return string
     */
    private function canonical_url(string|\moodle_url|null $url): string {
        $this->assertNotNull($url);
        if ($url instanceof \moodle_url) {
            return $url->out(false);
        }
        if (is_file($url)) {
            return (new \moodle_url('/' . basename($url)))->out(false);
        }
        return (new \moodle_url($url))->out(false);
    }

    /**
     * Creates a role with enough course access to exercise explicit capabilities.
     *
     * @param array $bank Bank data.
     * @param \stdClass $user User record.
     * @return int
     */
    private function create_bank_role(array $bank, \stdClass $user): int {
        $generator = $this->getDataGenerator();
        $roleid = $generator->create_role();
        $generator->enrol_user($user->id, $bank['course']->id, $roleid);
        $this->set_role_capability($roleid, $bank['context'], 'moodle/course:view', CAP_ALLOW);
        $this->set_role_capability($roleid, $bank['context'], 'mod/qbank:view', CAP_ALLOW);
        return $roleid;
    }

    /**
     * Changes a role capability and clears access caches.
     *
     * @param int $roleid Role ID.
     * @param \context $context Capability context.
     * @param string $capability Capability name.
     * @param int $permission Capability permission.
     */
    private function set_role_capability(int $roleid, \context $context, string $capability, int $permission): void {
        assign_capability($capability, $permission, $roleid, $context->id, true);
        accesslib_clear_all_caches_for_unit_testing();
    }

    /**
     * Marks one question version ready for another request.
     *
     * @param int $questionid Question ID.
     */
    private function set_ready(int $questionid): void {
        global $DB;

        $DB->set_field(
            'question_versions',
            'status',
            question_version_status::QUESTION_STATUS_READY,
            ['questionid' => $questionid],
        );
        \question_bank::notify_question_edited($questionid);
    }

    /**
     * Asserts that a question version remains ready.
     *
     * @param int $questionid Question ID.
     */
    private function assert_ready(int $questionid): void {
        global $DB;

        $this->assertSame(
            question_version_status::QUESTION_STATUS_READY,
            $DB->get_field('question_versions', 'status', ['questionid' => $questionid], MUST_EXIST),
        );
    }

    /**
     * Asserts that a question version is draft.
     *
     * @param int $questionid Question ID.
     */
    private function assert_draft(int $questionid): void {
        global $DB;

        $this->assertSame(
            question_version_status::QUESTION_STATUS_DRAFT,
            $DB->get_field('question_versions', 'status', ['questionid' => $questionid], MUST_EXIST),
        );
    }
}
