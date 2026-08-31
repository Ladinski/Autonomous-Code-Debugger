from pydantic import BaseModel
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

class FileContent(BaseModel):
    path: str
    content: str
    truncated: bool
    total_lines: int
    returned_lines: int


class DirectoryEntry(BaseModel):
    name: str
    path: str
    type: str


class DirectoryListing(BaseModel):
    path: str
    entries: list[DirectoryEntry]

class SearchMatch(BaseModel):
    path: str
    line_number: int
    line: str


class SearchResult(BaseModel):
    query: str
    matches: list[SearchMatch]
    truncated: bool