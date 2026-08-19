# Evaluations

MoMoPDA evaluates generated behavior rather than textual similarity to an exemplar.

## Public Smoke Tasks

`public/tasks.json` contains representative prompts and declares the fixture used to seed an isolated plugin workspace. A future harness should run each task with the released skill, the candidate skill, and periodically without a skill.

Public graders should prioritize:

1. Plugin installation on the target Moodle branch.
2. Hidden or generated PHPUnit tests for requested behavior.
3. Moodle Plugin CI with zero coding-style warnings.
4. Security invariants such as context, capability, sesskey, and output handling.
5. Task-specific forbidden patterns.

An LLM judge should be used only for qualities that deterministic checks cannot establish. Pairwise judgments should be blinded and randomized.

## Private Holdout Suite

Holdout prompts, mutation cases, hidden tests, and expected outcomes belong in a separate private repository. The generating agent must receive only the task prompt, starting workspace, released skill, and target Moodle source. It must not receive grader files or exemplar solutions.

Record the model identifier, model settings, client and harness versions, skill revision, Moodle revision, tokens, duration, and repeated-run results for every evaluation.
