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
 * Lists MoMoPDA contract activities in a course.
 *
 * @package    mod_momopda
 * @copyright  2026 MoMoPDA contributors
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require('../../config.php');

$id = required_param('id', PARAM_INT);
$course = $DB->get_record('course', ['id' => $id], '*', MUST_EXIST);

require_course_login($course, true);
$PAGE->set_url('/mod/momopda/index.php', ['id' => $course->id]);
$PAGE->set_pagelayout('incourse');
$PAGE->set_title($course->shortname . ': ' . get_string('modulenameplural', 'mod_momopda'));
$PAGE->set_heading($course->fullname);

echo $OUTPUT->header();
echo $OUTPUT->heading(get_string('modulenameplural', 'mod_momopda'));

$links = [];
foreach (get_all_instances_in_course('momopda', $course) as $instance) {
    $url = new moodle_url('/mod/momopda/view.php', ['id' => $instance->coursemodule]);
    $links[] = html_writer::link($url, format_string($instance->name));
}

if ($links) {
    echo html_writer::alist($links);
} else {
    echo $OUTPUT->notification(get_string('thereareno', 'moodle', get_string('modulenameplural', 'mod_momopda')));
}

echo $OUTPUT->footer();
