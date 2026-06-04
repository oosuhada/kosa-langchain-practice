import logging
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse, StreamingResponse
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from api.sec02_text_chat.service import ChatServiceDependency

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec02", tags=["sec02"])

# 지금은 contorller에서 작성하지만 나중에 service 쪽으로 옮길것임


# 엔드포인트 정의
@router.post("/chat-model", response_class=PlainTextResponse)
async def chat_model(
    question: Annotated[str, Form()], chat_service: ChatServiceDependency
):
    response = await chat_service.chat(question)
    return response


@router.post("/chat-model-stream", response_class=StreamingResponse)
async def chat_model_stream(
    question: Annotated[str, Form()], chat_service: ChatServiceDependency
):
    response = StreamingResponse(
        chat_service.stream_chat(question), media_type="application/x-ndjson"
    )
    return response
