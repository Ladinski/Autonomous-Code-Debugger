import pytest
from pydantic import ValidationError
from debugger_agent.agent.actions import RunTestsArgs
from debugger_agent.agent.actions import (
    AgentAction,
    ReadFileArgs,
    SearchCodeArgs,
)

def test_run_tests_action_is_valid():
    action = AgentAction(
        action="run_tests",
        reasoning_summary="Reproduce the reported failure.",
        run_tests=RunTestsArgs(
            command=["pytest"],
            timeout_seconds=30,
        ),
    )

    assert action.action == "run_tests"
    assert action.run_tests is not None
    assert action.run_tests.command == ["pytest"]


def test_run_tests_timeout_is_bounded():
    with pytest.raises(ValidationError):
        RunTestsArgs(
            command=["pytest"],
            timeout_seconds=121,
        )
        
def test_search_action_is_valid():
    action = AgentAction(
        action="search_code",
        reasoning_summary="Find token handling.",
        search_code=SearchCodeArgs(
            query="refresh_token",
            max_results=20,
        ),
    )

    assert action.action == "search_code"
    assert action.search_code is not None
    assert action.search_code.query == "refresh_token"


def test_read_file_action_is_valid():
    action = AgentAction(
        action="read_file",
        reasoning_summary="Inspect the authentication implementation.",
        read_file=ReadFileArgs(
            path="app/auth.py",
        ),
    )

    assert action.read_file is not None
    assert action.read_file.path == "app/auth.py"


def test_selected_action_requires_arguments():
    with pytest.raises(ValidationError):
        AgentAction(
            action="search_code",
            reasoning_summary="Search repository.",
        )


def test_rejects_arguments_for_different_action():
    with pytest.raises(ValidationError):
        AgentAction(
            action="read_file",
            reasoning_summary="Inspect file.",
            read_file=ReadFileArgs(
                path="app/auth.py",
            ),
            search_code=SearchCodeArgs(
                query="token",
            ),
        )


def test_search_result_limit_is_bounded():
    with pytest.raises(ValidationError):
        SearchCodeArgs(
            query="token",
            max_results=10000,
        )


def test_read_file_line_limit_is_bounded():
    with pytest.raises(ValidationError):
        ReadFileArgs(
            path="app/auth.py",
            max_lines=100000,
        )