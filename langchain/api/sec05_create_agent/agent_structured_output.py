import logging
from typing import Annotated, Any

from fastapi import Depends
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from api.common.utils import LoggingCallbackHandler
from api.sec05_create_agent.model import Movie


class StructuredOutputAgent:
    """Agent의 response_format을 Pydantic 모델로 지정하는 실습 클래스"""

    # 초기화 메소드
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        model_provider: str = "openai",
    ) -> None:
        self.logger = logging.getLogger(f"{__name__}.StructuredOutputAgent")
        # Agent 생성
        chat_model = init_chat_model(
            model,
            model_provider=model_provider,
            temperature=0.0,
        )
        self.agent: Any = create_agent(
            model=chat_model,
            system_prompt="당신은 영화 전문가입니다. 한국어로 답변해 주세요.",
            response_format=Movie,
        )

    async def run(self, content: str) -> Movie:
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": content}]},
            config={"callbacks": [LoggingCallbackHandler()]},
        )

        # result = {
        #   "messages": [
        #       {HumanMessage(content="...")},
        #       {AIMessage(content="...")}
        #   ],
        #   "structured_response": Movie(...)
        # }
        movie = result["structured_response"]
        if isinstance(movie, Movie):
            return movie
        return Movie.model_validate(movie)


# 의존성 주입을 위한 타입 힌트 정의
StructuredOutputAgentDependency = Annotated[
    StructuredOutputAgent,
    Depends(StructuredOutputAgent),
]
