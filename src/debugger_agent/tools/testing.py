import subprocess

from pydantic import BaseModel

from debugger_agent.repository.workspace import RepositoryWorkspace


class TestRunResult(BaseModel):
    command: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    timed_out: bool


class TestExecutionError(ValueError):
    """Raised when an unsafe or invalid test command is requested."""


ALLOWED_TEST_COMMANDS = {
    "pytest",
}


def run_tests(
    workspace: RepositoryWorkspace,
    command: list[str] | None = None,
    timeout_seconds: int = 30,
) -> TestRunResult:
    command = command or ["pytest"]

    if not command:
        raise TestExecutionError(
            "Test command cannot be empty."
        )

    if command[0] not in ALLOWED_TEST_COMMANDS:
        raise TestExecutionError(
            f"Command is not allowed: {command[0]}"
        )

    if timeout_seconds <= 0:
        raise ValueError(
            "timeout_seconds must be greater than 0."
        )

    try:
        completed = subprocess.run(
            command,
            cwd=workspace.root,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            shell=False,
        )

    except subprocess.TimeoutExpired as exc:
        stdout = (
            exc.stdout.decode()
            if isinstance(exc.stdout, bytes)
            else exc.stdout or ""
        )

        stderr = (
            exc.stderr.decode()
            if isinstance(exc.stderr, bytes)
            else exc.stderr or ""
        )

        return TestRunResult(
            command=command,
            exit_code=None,
            stdout=stdout,
            stderr=stderr,
            timed_out=True,
        )

    return TestRunResult(
        command=command,
        exit_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        timed_out=False,
    )