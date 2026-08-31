import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from debugger_agent.agent.actions import AgentAction


load_dotenv()


class OpenAIDecisionModel:
    def __init__(
        self,
        model: str | None = None,
    ):
        model_name = model or os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6-luna",
        )

        self.model_name = model_name

        self._model = ChatOpenAI(
            model=model_name,
        )

        self._structured_model = self._model.with_structured_output(
            AgentAction
        )

    def decide(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> AgentAction:
        result = self._structured_model.invoke(
            [
                ("system", system_prompt),
                ("user", user_prompt),
            ]
        )

        return result