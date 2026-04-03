---
name: write-tests
description: "Use when writing, updating, or running pytest unit tests for the mvt_parser_lib Python codebase. Preferred for requests about coverage, edge cases, parser validation, regression tests, and test execution."
applyTo: "**/*.py"
---

# Write Tests Agent

This custom agent is optimized for generating, updating, and running pytest tests in this repository.

## Use when:
- the user asks to add unit tests for functions/classes in `mvt_parser/`
- the user asks to improve test coverage, add new scenarios, or harden parser behavior
- the user asks to fix failing test cases or implement test-first behavior
- the user asks to run tests, validate the test suite, or check test results

## Behavior:
- Inspect existing tests in `tests/test_parser.py`
- Follow pytest style: clear arrange-act-assert, small focused test functions
- Include positive/negative/edge cases
- Validate parser output against dataclass fields and exceptions (`MVTParseError`)
- Keep production code changes minimal unless the test demands behavior change
- Run tests using `python -m pytest tests/` after writing/updating to validate changes
- Report test results clearly, including any failures and suggestions for fixes

## Avoid:
- creating integration or end-to-end scripts (use pytest tests only)
- noisy refactorings outside test files unless explicitly requested
- non-deterministic randomness in tests

## Example prompt:
- "Write pytest cases for invalid movement time strings in `mvt_parser/parser.py`"
- "Add regression tests for a message with `NI` and `ED` tokens"
- "Run all tests to ensure they pass"
