import logging
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse, StreamingResponse

from api.sec05_create_agent.agent_chat import ChatAgentDependency
from api.sec05_create_agent.agent_chat_stream import ChatStreamAgentDependency
from api.sec05_create_agent.agent_structured_output import (
    StructuredOutputAgentDependency,
)
from api.sec05_create_agent.model import Movie

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sec05", tags=["sec05"])


# Agent를 사용하는 대화 엔드포인트 정의
@router.post("/agent-chat", response_class=PlainTextResponse)
async def agent_chat(
    question: Annotated[str, Form()], agent: ChatAgentDependency
) -> str:
    logger.info("sec5/agent-chat 엔드포인트 실행")
    # Agent 실행
    response = await agent.run(question)
    # 반환
    return response


@router.post("/agent-chat-stream", response_class=StreamingResponse)
async def agent_chat_stream(
    question: Annotated[str, Form()],
    agent: ChatStreamAgentDependency,
) -> StreamingResponse:
    async_generator = agent.run(question)
    return StreamingResponse(content=async_generator, media_type="application/x-ndjson")


@router.post("/agent-structured-output", response_model=Movie)
async def agent_structured_output(
    content: Annotated[str, Form()],
    agent: StructuredOutputAgentDependency,
) -> Movie:
    return await agent.run(content)
