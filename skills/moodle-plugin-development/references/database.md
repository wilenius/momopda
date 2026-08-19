# Database Contracts

## Schema

Create and edit `db/install.xml` with Moodle XMLDB conventions. Keep table and field names within Moodle limits, define keys and useful indexes, and avoid database-specific types or expressions.

The install schema describes a fresh installation only. Released schema changes also require an idempotent step in `db/upgrade.php` and a matching savepoint.

## DML

Use the `$DB` API for records and parameterized SQL. Use SQL helpers such as `get_in_or_equal()` and database-family abstractions instead of MySQL-specific syntax.

Request only required fields. Avoid database calls inside rendering loops, text-filter hot paths, and repeated callbacks. Use Moodle caches when data outlives one request and a local cache when it does not.

## Transactions

Use delegated transactions for multi-step writes that must succeed or fail together. Do not catch an exception merely to suppress it; roll back or allow it to propagate with useful context.

## Upgrade Rules

- Guard each change with the previous plugin version.
- Check whether fields, keys, or tables exist when reruns are possible.
- Place the savepoint after successful operations.
- Keep `$plugin->version`, upgrade thresholds, and savepoints consistent.
- Run Moodle Plugin CI `savepoints` and install/upgrade tests.
