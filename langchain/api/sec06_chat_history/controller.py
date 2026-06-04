import logging
from typing import Annotated

from fastapi import APIRouter, Form, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from api.sec06_chat_history.agent_history_in_memory import (
    HistoryInMemoryAgentDependency,
)
from api.sec06_chat_history.agent_history_postgresql import (
    HistoryPostgreSQLAgentDependency,
)
from api.sec06_chat_history.history_service import (
    HistoryInMemoryServiceDependency,
    HistoryPostgreSQLServiceDependency,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sec06", tags=["sec06"])


#####################################
# Agent를 사용하는 대화 엔드포인트 정의
#####################################
@router.post("/chat-history-inmemory", response_class=PlainTextResponse)
async def chat_history_inmemory(
    message: Annotated[str, Form()],
    conversation_id: Annotated[str, Form()],
    agent: HistoryInMemoryAgentDependency,
) -> str:
    response = await agent.run(message, conversation_id)
    return response


# 대화 ID의 지난 대화 내용을 가져오는 엔드포인트
@router.get("/get-history-inmemory", response_class=JSONResponse)
async def get_history_inmemory(
    conversation_id: Annotated[str, Query()],
    service: HistoryInMemoryServiceDependency,
) -> dict:
    history = await service.get_history(conversation_id)
    return history


# 대화 ID의 지난 대화 내용을 모두 삭제하는 엔드포인트
@router.post("/clear-history-inmemory", response_class=JSONResponse)
async def clear_history_inmemory(
    conversation_id: Annotated[str, Form()],
    service: HistoryInMemoryServiceDependency,
) -> dict:
    response = await service.clear_history(conversation_id)
    return response


@router.post("/chat-history-postgresql", response_class=PlainTextResponse)
async def chat_history_postgresql(
    message: Annotated[str, Form()],
    conversation_id: Annotated[str, Form()],
    agent: HistoryPostgreSQLAgentDependency,
) -> str:
    response = await agent.run(message, conversation_id)
    return response


@router.get("/get-history-postgresql", response_class=JSONResponse)
async def get_history_postgresql(
    conversation_id: Annotated[str, Query()],
    service: HistoryPostgreSQLServiceDependency,
) -> dict:
    response = await service.get_history(conversation_id)
    return response


@router.post("/clear-history-postgresql", response_class=JSONResponse)
async def clear_history_postgresql(
    conversation_id: Annotated[str, Form()],
    service: HistoryPostgreSQLServiceDependency,
) -> dict:
    response = await service.clear_history(conversation_id)
    return response
