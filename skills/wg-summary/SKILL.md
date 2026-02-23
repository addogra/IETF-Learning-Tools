Author: Aditya Dogra

# Skill: wg-summary

## Purpose
Fetch and summarize the WG charter for quick user understanding.

## Inputs
- WG acronym
- WG about page content

## Steps
1. Fetch WG about page.
2. Locate charter heading and section text.
3. Build lightweight bullet summary with key topics.
4. Do not prompt for daily update registration in this flow.

## Outputs
- Structured charter summary text

## Failure Handling
- If charter section is missing, emit clear extraction error.
- If text is empty, return "No usable charter text" summary fallback.

## Test Coverage
- `tests/test_summarizer.py`
- `tests/test_cli.py::test_cli_option_1_summary_flow`
