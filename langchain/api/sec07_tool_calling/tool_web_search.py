import logging
from typing import Annotated, Any

import requests
from bs4 import BeautifulSoup
from fastapi import Depends
from langchain.agents import create_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool

from api.common.utils import LoggingCallbackHandler

logger = logging.getLogger(__name__)


@tool
def search_web(query: str, max_results: int = 5) -> list[dict[str, Any]] | str:
    """웹에서 키워드를 검색하여 관련 페이지 목록을 제공합니다.
    실시간 웹 검색을 수행합니다.
    검색 결과로 제목, URL, 요약 내용을 제공합니다.
    Args:
        query: 검색할 키워드
        max_results: 최대 결과 개수 (기본값: 5)
    Returns:
        list[dict[str, Any]]: 검색 결과 목록 (url, title, content, score)"""
    logger.info(f"웹 검색 도구 호출: query={query}, max_results={max_results}")
    try:
        tavily_search = TavilySearchResults(
            max_results=max_results,
            search_depth="basic",
        )
        return tavily_search.invoke(query)
    except Exception as exc:
        logger.exception("웹 검색 실패")
        return f"웹 검색 실패: {exc}"


@tool
def fetch_webpage(url: str) -> str:
    """특정 URL의 웹페이지 내용을 가져와 텍스트만 추출합니다."""
    logger.info(f"웹페이지 가져오기 도구 호출: url={url}")
    if not url.startswith(("http://", "https://")):
        return "오류: URL은 http:// 또는 https://로 시작해야 합니다."
    try:
        response = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=15,
        )
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)[:8000]
    except Exception as exc:
        logger.exception("웹페이지 가져오기 실패")
        return f"웹페이지 가져오기 실패: {exc}"


class WebSearchAgent:
    # Agent 초기화
    # - 웹 검색 도구와 웹페이지 본문 추출 도구를 함께 등록한다.
    # - 검색 결과만으로 부족하면 fetch_webpage 도구로 상세 내용을 가져올 수 있다.
    def __init__(self) -> None:
        logger.info("WebSearchAgent 초기화")
        self.agent = create_agent(
            model="openai:gpt-4o-mini",
            tools=[search_web, fetch_webpage],
            system_prompt="""
            당신은 인터넷 검색 및 웹페이지 분석 전문가입니다.

            [사용 가능한 도구]
            1. **search_web**: 키워드로 웹 검색
            - 웹페이지 목록을 가져옵니다
            - 각 결과에는 제목, URL, 요약 내용이 포함됩니다
            - 처음에 정보를 찾을 때 사용하세요

            2. **fetch_webpage**: 특정 URL의 내용 가져오기
            - URL을 입력받아 해당 웹페이지의 전체 내용을 가져옵니다
            - HTTP 요청 후 HTML을 파싱하여 텍스트만 추출합니다
            - 검색 결과 중 특정 페이지의 상세 내용이 필요할 때 사용하세요

            [작업 흐름]
            1. 먼저 search_web으로 관련 페이지들을 검색합니다
            2. 검색 결과의 요약만으로 답변이 가능하면 그대로 답변합니다
            3. 더 상세한 내용이 필요하면 fetch_webpage로 특정 URL의 전체 내용을 가져옵니다

            출처 URL을 명시하여 신뢰성 있는 답변을 제공하세요.
            """,
        )

    # Agent 실행
    # - 사용자의 검색 질문을 전달하고, Agent가 필요한 웹 도구를 호출한다.
    async def run(self, question: str) -> str:
        logger.info(f"WebSearchAgent 실행 요청: {question}")
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            {"callbacks": [LoggingCallbackHandler()]},
        )
        return str(result["messages"][-1].content)


# FastAPI 의존성 주입 타입 별칭
# - controller.py에서 WebSearchAgent를 Depends로 주입받기 위해 사용한다.
WebSearchAgentDependency = Annotated[WebSearchAgent, Depends(WebSearchAgent)]
