from pathlib import Path

from debugger_agent.observability.models import AgentTrace


def save_trace(
    trace: AgentTrace,
    output_directory: str | Path,
) -> Path:
    output_directory = Path(output_directory)

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        output_directory
        / f"{trace.trace_id}.json"
    )

    output_path.write_text(
        trace.model_dump_json(indent=2),
        encoding="utf-8",
    )

    return output_path