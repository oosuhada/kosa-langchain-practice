import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse

# 로거 생성
logger = logging.getLogger(__name__)

# 라우터 생성
router = APIRouter(prefix="/sec01", tags=["sec01"])


# 엔드포인트 정의
@router.post("/chat", response_class=PlainTextResponse)
async def chat(question: Annotated[str, Form()]):
    logger.info(f"질문을 입력하였습니다. 질문: {question}")
    await asyncio.sleep(1)
    return "LLM 문자 대화 기능은 추후 구현될 예정입니다."
