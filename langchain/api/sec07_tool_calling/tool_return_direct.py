import json
import logging
from typing import Annotated

from fastapi import Depends
from langchain.agents import create_agent
from langchain_core.tools import tool

from api.common.utils import LoggingCallbackHandler

logger = logging.getLogger(__name__)


@tool(return_direct=True)
def get_movie_recommendations(genre: str) -> str:
    """장르별 추천 영화 목록을 JSON 문자열로 직접 반환합니다."""
    logger.info(f"영화 추천 도구 호출: genre={genre}")
    movies = {
        "SF": ["엣지 오브 투모로우", "인터스텔라", "마션"],
        "코미디": ["극한직업", "세 얼간이", "행오버"],
        "드라마": ["쇼생크 탈출", "그린 북", "포레스트 검프"],
    }
    return json.dumps(
        {"genre": genre, "movies": movies.get(genre, movies["SF"])},
        ensure_ascii=False,
    )


class ReturnDirectAgent:
    # Agent 초기화
    # - return_direct=True 도구를 등록한다.
    # - 도구가 호출되면 Agent의 추가 설명 없이 도구 결과가 바로 응답으로 반환된다.
    def __init__(self) -> None:
        logger.info("ReturnDirectAgent 초기화")
        self.agent = create_agent(
            model="openai:gpt-4o-mini",
            tools=[get_movie_recommendations],
            system_prompt="사용자가 영화 추천을 요청하면 장르를 추론해서 도구를 호출하세요.",
        )

    # Agent 실행
    # - 사용자의 영화 추천 요청을 전달하고 최종 응답을 반환한다.
    async def run(self, question: str) -> str:
        logger.info(f"ReturnDirectAgent 실행 요청: {question}")
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            {"callbacks": [LoggingCallbackHandler()]},
        )
        return str(result["messages"][-1].content)


# FastAPI 의존성 주입 타입 별칭
# - controller.py에서 ReturnDirectAgent를 Depends로 주입받기 위해 사용한다.
ReturnDirectAgentDependency = Annotated[
    ReturnDirectAgent,
    Depends(ReturnDirectAgent),
]
