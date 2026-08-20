# OpenCode JSON Probe

The public harness was probed with OpenCode 1.18.18 on 20 August 2026 using a disposable workspace outside this repository.

## Observed Stream

`opencode run --format json --dir <workspace> <prompt>` writes one JSON object per stdout line. A successful one-file edit emitted:

1. `step_start` with a `step-start` part.
2. `text` with the assistant progress text.
3. `tool_use` with the tool name, input, timing, and `state.status: completed`.
4. `step_finish` with `reason: tool-calls`, token counts, cache counts, and cost.
5. A second `step_start` and final `text`.
6. A terminal `step_finish` with `reason: stop`, token counts, cache counts, and cost.

Usage is reported per `step_finish` under `part.tokens`. The observed fields were `total`, `input`, `output`, `reasoning`, `cache.read`, `cache.write`, and `part.cost`. The harness sums the non-total token fields and records missing usage explicitly rather than treating it as zero.

Session IDs, message IDs, part IDs, timestamps, provider metadata, and tool diffs may also be present. The harness removes reasoning text and credential-shaped values before saving events. It captures stderr separately.

## Permissions And Failure

Without `--auto` or an explicit policy, a non-interactive edit requested permission on stderr and auto-rejected it. OpenCode still emitted a `tool_use` event with `state.status: error` and a `step_finish` with `reason: tool-calls`; a process exit alone is therefore not sufficient evidence of success.

The successful probe used an injected policy allowing read, edit, glob, grep, and list while denying shell, task, and network tools. The public harness uses that policy with `--pure`, disables external skill discovery, and isolates `XDG_CONFIG_HOME`. It does not use `--auto`.

OpenCode 1.18.18 exposes no run-timeout option. The harness starts the client in a separate process group, captures partial stdout and stderr, sends `SIGTERM` when its configured timeout expires, escalates to `SIGKILL` after two seconds, and records `status: timeout` independently from non-zero exits and malformed streams.

Client success requires all of the following:

- Exit code zero with no signal.
- Every parsed stdout line is a JSON object.
- No tool event has `state.status: error`.
- At least one terminal `step_finish` has `reason: stop`.

Anything else remains `client_error`, `malformed`, or `timeout`; it cannot become a passing evaluation.
