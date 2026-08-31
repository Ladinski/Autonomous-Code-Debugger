from pathlib import Path

from debugger_agent.evaluation.models import EvaluationCase
from debugger_agent.evaluation.runner import (
    run_evaluation_case,
    summarize_results,
)


cases = [
    EvaluationCase(
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
    ),
    EvaluationCase(
        name="email_normalization",
        fixture_path=Path(
            "tests/fixtures/transform_bug"
        ),
        bug_report=(
            "Email addresses are not being normalized "
            "consistently. Inputs with uppercase characters "
            "remain uppercase, which causes matching problems. "
            "Find the root cause, fix it, and verify the fix."
        ),
        expected_file="app/users.py",
        expected_text=(
            "return email.strip().lower()"
        ),
    ),
    EvaluationCase(
        name="quota_boundary_condition",
        fixture_path=Path(
            "tests/fixtures/boundary_bug"
        ),
        bug_report=(
            "Users are still allowed to make a request "
            "after they have already reached their request "
            "limit. Find the root cause, fix it, and verify "
            "the fix."
        ),
        expected_file="app/quota.py",
        expected_text=(
            "return used_requests < request_limit"
        ),
    ),
]


def main():
    results = []

    for case in cases:
        result = run_evaluation_case(
            case,
            max_iterations=15,
            max_patch_attempts=3,
        )

        results.append(result)

        print()
        print("=" * 60)
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
        print(
            "ITERATIONS:",
            result.iterations,
        )
        print(
            "PATCH ATTEMPTS:",
            result.patch_attempts,
        )
        print(
            "TEST RUNS:",
            result.tests_executed,
        )
        print(
            "DIAGNOSIS:",
            result.final_diagnosis,
        )

    summary = summarize_results(results)

    print()
    print("=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(
        "TOTAL CASES:",
        summary.total_cases,
    )
    print(
        "DIAGNOSED:",
        summary.diagnosed_cases,
    )
    print(
        "SUCCESSFUL FIXES:",
        summary.successful_fixes,
    )
    print(
        "VERIFIED FIXES:",
        summary.verified_fixes,
    )
    print(
        "FIX RATE:",
        f"{summary.fix_rate:.1%}",
    )
    print(
        "VERIFICATION RATE:",
        f"{summary.verification_rate:.1%}",
    )
    print(
        "AVG ITERATIONS:",
        f"{summary.average_iterations:.2f}",
    )
    print(
        "AVG PATCH ATTEMPTS:",
        f"{summary.average_patch_attempts:.2f}",
    )
    print(
        "AVG TEST RUNS:",
        f"{summary.average_test_runs:.2f}",
    )


if __name__ == "__main__":
    main()