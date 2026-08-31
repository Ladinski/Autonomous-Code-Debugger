from typing import Literal

from pydantic import BaseModel, Field, model_validator


class ListDirectoryArgs(BaseModel):
    path: str = "."


class SearchCodeArgs(BaseModel):
    query: str = Field(min_length=1)
    max_results: int = Field(default=50, ge=1, le=100)


class ReadFileArgs(BaseModel):
    path: str
    max_lines: int = Field(default=500, ge=1, le=1000)

class ApplyPatchArgs(BaseModel):
    path: str
    old_text: str = Field(min_length=1)
    new_text: str

class FinishArgs(BaseModel):
    diagnosis: str
    confidence: float = Field(ge=0.0, le=1.0)

class RunTestsArgs(BaseModel):
    command: list[str] = ["pytest"]
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    
class AgentAction(BaseModel):
    action: Literal[
        "list_directory",
        "search_code",
        "read_file",
        "run_tests",
        "apply_patch",
        "finish",
    ]

    reasoning_summary: str
    apply_patch: ApplyPatchArgs | None = None
    list_directory: ListDirectoryArgs | None = None
    search_code: SearchCodeArgs | None = None
    read_file: ReadFileArgs | None = None
    finish: FinishArgs | None = None
    run_tests: RunTestsArgs | None = None
    @model_validator(mode="after")
    def validate_selected_action(self):
        selected_args = getattr(self, self.action)

        if selected_args is None:
            raise ValueError(
                f"Arguments for action '{self.action}' are required."
            )

        action_fields = (
            "list_directory",
            "search_code",
            "read_file",
            "run_tests",
            "apply_patch",
            "finish",
        )

        for field_name in action_fields:
            if field_name == self.action:
                continue

            if getattr(self, field_name) is not None:
                raise ValueError(
                    f"Arguments supplied for unselected action '{field_name}'."
                )

        return self