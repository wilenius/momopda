# Core Moodle Development Principles

## Moodle coding style

* Source for these is https://moodledev.io/general/development/policies/codingstyle.
* Moodle coding style is prioritized, then, PSR-12 or PSR-1, in that order.
* Always use "long" php tags. However, to avoid whitespace problems, DO NOT include the closing tag at the very end of the file.
* Maximum Line Length: Aim for 132 characters.
* Wrapping lines: Indent with 4 spaces by default.
* Terminate lines with LF
* Filenames are lowercase only
* Class and function names are lowercase words, separated by underscores
* In the case of legacy functions (those not placed in classes), names should start with the Frankenstyle prefix and plugin name to avoid conflicts between plugins.
* Variable names are lowercase words, no word separator.
* Constants should always be in upper case, and always start with Frankenstyle prefix and plugin name (in case of activities the module name only for legacy reasons). They should have words separated by underscores.
* Comments: All inline comments and block comments should end with proper punctuation (period, exclamation mark, or question mark). Single-line comments should be written as complete sentences. Example: `// Do this thing here.` not `// Do this thing here`
* Strings: Always use single quotes when a string is literal, or contains a lot of double quotes. Use double quotes when you need to include plain variables or a lot of single quotes.

## Other development principles

**Security**: Validate inputs, use Moodle security functions  
**I18n**: Externalize all strings
**Database**: DML API only, no raw SQL
**Capabilities**: Implement proper permission checking
**Accessibility**: WCAG 2.1 AA compliance

## Version Information

- Component naming: `{plugintype}_{pluginname}`
- Version format: YYYYMMDDRR.XX, where YYYYMMDD is the date, RR is a release increment, and XX is a micro increment. 
- Maturity levels: ALPHA, BETA, RC, STABLE
