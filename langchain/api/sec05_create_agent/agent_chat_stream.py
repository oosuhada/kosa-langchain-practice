import logging
from collections.abc import AsyncGenerator
from typing import Annotated, Any

from fastapi import Depends
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage


class ChatStreamAgent:
    """Agent 응답을 NDJSON 스트리밍으로 반환하는 실습 클래스"""

    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.ChatStreamAgent")
        # Agent 생성
        self.agent: Any = create_agent(
            model=model,
            system_prompt="당신은 AI 응용프로그램 개발 전문가입니다. 한국어로 쉽게 답변하세요.",
        )

    # 에이전트 실행 메소드 (제너레이터 함수)
    async def run(self, question: str) -> AsyncGenerator[str, None]:
        async_iterable = self.agent.astream(
            {"messages": [HumanMessage(question)]},
            stream_mode="messages",
        )
        # chunk: (AIMessageChunk, metadata_dict) 튜플
        async for ai_message_chunk, _metadata in async_iterable:
            if getattr(ai_message_chunk, "content", None):
                yield str(ai_message_chunk.content)

            # [참고]
            # 스트림 청크가 문자열이거나 .content 속성을 가진 객체일 수 있으므로 안전하게 처리
            # if isinstance(ai_message_chunk, str):
            #     yield ai_message_chunk
            #     continue
            # content = getattr(ai_message_chunk, "content", "")
            # if isinstance(content, str):
            #     yield content
            # else:
            #     yield str(content)


# 의존성 주입을 위한 타입 힌트 정의
ChatStreamAgentDependency = Annotated[ChatStreamAgent, Depends(ChatStreamAgent)]
