import json
import logging
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse, PlainTextResponse, StreamingResponse

from api.sec03_messages.service import (
    ChainOfThoughtServiceDependency,
    FewShotServiceDependency,
    RoleServiceDependency,
    SelfConsistencyServiceDependency,
    StepBackServiceDependency,
)

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec03", tags=["sec03"])


# 엔드포인트 정의
@router.post("/chat-with-system", response_class=PlainTextResponse)
async def chat_with_system(
    question: Annotated[str, Form()], chat_service: RoleServiceDependency
):
    response = await chat_service.chat(question)
    return response


# ============================================
@router.post("/chat-with-system-stream", response_class=StreamingResponse)
async def chat_model_stream(
    question: Annotated[str, Form()], chat_service: RoleServiceDependency
):
    response = StreamingResponse(
        chat_service.chat_stream(question),  # 제너레이터 반환
        media_type="application/x-ndjson",
    )
    return response


# ============================================
@router.post("/few-shot-prompt", response_class=JSONResponse)
async def few_shot_prompt(
    order: Annotated[str, Form()], service: FewShotServiceDependency
):
    json_text = await service.chat(order)
    dict_content = json.loads(json_text)  # json -> dict로 변환
    return JSONResponse(dict_content)


# ============================================
@router.post("/step-back-prompt", response_class=PlainTextResponse)
async def step_back_prompt(
    question: Annotated[str, Form()], service: StepBackServiceDependency
):
    response = await service.chat(question)
    return response


# ============================================
@router.post("/chat-chain-of-thought-stream", response_class=StreamingResponse)
async def chat_chain_of_thought_stream(
    question: Annotated[str, Form()], service: ChainOfThoughtServiceDependency
):
    response = StreamingResponse(
        service.chat(question),  # 제너레이터 반환
        media_type="application/x-ndjson",
    )
    return response


# ============================================
@router.post("/self-consistency", response_class=PlainTextResponse)
async def self_consistency(
    content: Annotated[str, Form()], service: SelfConsistencyServiceDependency
):
    response = await service.chat(content)
    return response
