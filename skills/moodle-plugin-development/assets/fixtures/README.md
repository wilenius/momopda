# Contract Fixtures

These plugins are intentionally small executable contracts derived from simple Moodle-core implementations. Repository CI checks their structure, syntax, and Moodle coding style. The integration matrix installs and exercises them on the pinned Moodle 4.5 and 5.2 compatibility boundaries.

They are not production starter plugins. Production code may also require privacy declarations, backup and restore, events, tasks, accessibility work, upgrade steps, PHPUnit, Behat, and feature-specific capabilities.

| Fixture | Core reference | Contract |
|---|---|---|
| `mod_momopda` | `mod/page` | Conventional activity CRUD and view |
| `block_momopda` | `blocks/course_summary` | Block discovery and content |
| `enrol_momopda` | `enrol/fee` | Enrol plugin class discovery |
| `filter_momopda` | `filter/emailprotect` | Namespaced text filter |
| `local_momopda` | Plugin API | Minimal local plugin |
| `qbank_momopda` | `question/bank/viewcreator` | Question-bank column |
| `qtype_momopda` | `question/type/description` | Information-item question type |
| `report_momopda` | `report/status` | Administration report page |
| `tiny_momopda` | `lib/editor/tiny/plugins/noautolink` | TinyMCE loader registration |

The fixture manifest records destination paths for pre-5.1 and 5.1+ Moodle layouts. The staging tool copies every fixture, records its selected destination and file hashes, and refuses to replace an existing output directory.
