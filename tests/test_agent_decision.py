from debugger_agent.agent.actions import (
    AgentAction,
    SearchCodeArgs,
)
from debugger_agent.agent.decision import AgentDecisionService


class FakeDecisionModel:
    def decide(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> AgentAction:
        return AgentAction(
            action="search_code",
            reasoning_summary="Locate refresh token handling.",
            search_code=SearchCodeArgs(
                query="refresh_token",
            ),
        )


def test_decision_service_returns_model_action():
    state = {
        "bug_report": (
            "Users sometimes receive a 401 after "
            "refreshing their access token."
        ),
        "iteration_count": 0,
        "tool_calls": [],
        "tool_observations": [],
        "files_inspected": [],
        "current_hypothesis": None,
        "final_diagnosis": None,
        "completion_status": "investigating",
    }

    service = AgentDecisionService(
        model=FakeDecisionModel()
    )

    action = service.choose_action(state)

    assert action.action == "search_code"
    assert action.search_code is not None
    assert action.search_code.query == "refresh_token"