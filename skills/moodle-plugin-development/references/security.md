# Security Contracts

## Request Boundary

Use `required_param()`, `optional_param()`, external-function parameter descriptions, or validated form data. Choose the narrowest appropriate `PARAM_*` type. Raw JSON and uploaded files require explicit structural and content validation.

## Authorization

Establish the relevant context before accessing protected records. Call `require_login()` when authentication is required and `require_capability()` before protected actions. Visibility checks in the interface do not replace endpoint authorization.

For state-changing browser requests, require POST where appropriate and call `require_sesskey()`. External functions must call `validate_context()` and enforce capabilities themselves.

For a two-stage confirmation flow, keep the first POST non-mutating and validate the sesskey again on the final POST. Re-resolve the context and re-authorize every selected object at final execution; permissions and ownership may have changed while the confirmation page was open. Validate the complete selection before opening an all-or-nothing transaction so one unauthorized object cannot leave a partial update.

Treat return targets as untrusted input. Clean them with `PARAM_LOCALURL`, explicitly reject protocol-relative values such as `//example.invalid/path`, and use a server-built `moodle_url` fallback when the result is empty or invalid. Apply the same safe destination to success and cancellation, and do not derive web URLs from physical paths such as Moodle's `public/` application directory.

## Output

- Use `s()` for plain unformatted text.
- Use `format_string()` for names and headings with Moodle string semantics.
- Use `format_text()` for stored rich text, with the correct context and format.
- Prefer Mustache templates; data remains untrusted unless deliberately formatted.
- Never concatenate untrusted values into HTML, JavaScript, CSS, URLs, or SQL.

## Data And Files

Use Moodle DML placeholders and table-name braces. Use File API areas with an explicit context, component, file area, and item ID. Verify ownership and capability before serving or modifying files.

Implement the Privacy API when personal data is stored or exported. Use a null provider only when the plugin genuinely stores no personal data.

## Review Invariants

- Every endpoint has authentication, context, and capability decisions.
- Every mutation has CSRF protection appropriate to its transport.
- Every selected object is re-authorized at execution time.
- Every multi-object mutation validates the full selection before changing state.
- Every user-controlled return target is local or replaced by a server-built local fallback.
- Every rendered value has an explicit formatting or escaping decision.
- Background tasks re-check scope and do not rely on a browser user's session.
