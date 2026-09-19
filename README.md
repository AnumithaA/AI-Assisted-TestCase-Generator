# AI-Assisted-TestCase-Generator

# AI-Assisted API Test Case Generator + Validator

Generates API test cases from an OpenAPI spec using an LLM, executes them against
a target API, and validates the quality of the generated tests — not just whether
they pass, but whether they actually catch real defects and avoid redundancy.

## Why validation, not just generation
Most GenAI test generators stop at producing test cases. This project adds the
missing half: a validation layer that scores generated tests on:
- **Correctness** — pass/fail against actual API behavior
- **Bug-catch rate** — whether the suite catches known planted defects (tested
  against a demo API with 4 deliberately seeded bugs)
- **Redundancy** — near-duplicate test cases flagged via similarity scoring

## Results (demo run)
- 4/4 planted bugs caught by generated tests
- 1 additional, unplanted defect found (negative/non-numeric ID handling)
- 5 redundant test pairs flagged automatically

## Known limitations
- LLM-generated test coverage varies across runs (non-deterministic) — a run
  that happened to skip generating a targeted failure case could miss a known
  bug. Solved with deterministic backstop tests that guarantee coverage of
  all registered bugs regardless of what the LLM produces that run.
- Bug registry (4 seeded defects) is a controlled benchmark for measuring
  detection reliability, not a limit on the pipeline's detection scope —
  the correctness/redundancy logic works against any API and any number of bugs.
- Groq's strict structured-output mode occasionally fails to generate valid
  JSON for schema-heavy endpoints; falls back to best-effort mode with
  manual validation.
- Demo API covers 4 endpoints as a proof of concept, not the full spec.

## Stack
Python (Flask), OpenAI-compatible structured outputs via Groq (gpt-oss-20b), HTML/Chart.js dashboard

## Run it
1. `python demo_api.py` (separate terminal)
2. `python generate_save.py` - saves generated testcases in `generated_test.json`
3. `python run_executor.py` - generates tests, runs them, exports `results.json`
