from pathlib import Path

from debugger_agent.evaluation.models import EvaluationCase
from debugger_agent.evaluation.runner import run_evaluation_case


case = EvaluationCase(
    name="refresh_token_wrong_validator",
    fixture_path=Path(
        "tests/fixtures/sample_repo"
    ),
    bug_report=(
        "Users receive a 401 when attempting to refresh "
        "their access token using a valid refresh token. "
        "Find the root cause, fix it, and verify the fix."
    ),
    expected_file="app/auth.py",
    expected_text=(
        "validate_refresh_token(refresh_token)"
    ),
)

result = run_evaluation_case(
    case,
    max_iterations=15,
    max_patch_attempts=3,
)

print()
print("CASE:", result.case_name)
print("STATUS:", result.completion_status)
print("DIAGNOSED:", result.diagnosed)
print(
    "EXPECTED FIX PRESENT:",
    result.expected_fix_present,
)
print(
    "VERIFIED AFTER PATCH:",
    result.tests_passed_after_patch,
)
print("ITERATIONS:", result.iterations)
print("PATCH ATTEMPTS:", result.patch_attempts)
print("TEST RUNS:", result.tests_executed)
print("DIAGNOSIS:", result.final_diagnosis)