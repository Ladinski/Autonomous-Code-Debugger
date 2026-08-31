from pathlib import Path

from pydantic import BaseModel


class EvaluationCase(BaseModel):
    name: str
    fixture_path: Path
    bug_report: str
    expected_file: str
    expected_text: str


class EvaluationResult(BaseModel):
    case_name: str
    completion_status: str
    diagnosed: bool
    expected_fix_present: bool
    tests_passed_after_patch: bool
    iterations: int
    patch_attempts: int
    tests_executed: int
    final_diagnosis: str | None