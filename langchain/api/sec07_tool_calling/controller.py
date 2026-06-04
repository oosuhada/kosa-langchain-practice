import json
import logging
from typing import Annotated

from fastapi import APIRouter, Form, UploadFile
from fastapi.responses import JSONResponse, PlainTextResponse

from api.sec07_tool_calling.tool_context import HeatingSystemAgentDep
from api.sec07_tool_calling.tool_datetime import DateTimeAgentDependency
from api.sec07_tool_calling.tool_file_system import FileSystemAgentDependency
from api.sec07_tool_calling.tool_hardware_control import (
    HardwareControlAgentDependency,
)
from api.sec07_tool_calling.tool_return_direct import ReturnDirectAgentDependency
from api.sec07_tool_calling.tool_state import StateAgentDep
from api.sec07_tool_calling.tool_web_search import WebSearchAgentDependency

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sec07", tags=["sec07"])

# 각 엔드포인트의 agent 파라미터는 FastAPI 의존성 주입으로 생성된다.
# 예: agent: DateTimeAgentDependency
# - DateTimeAgentDependency = Annotated[DateTimeAgent, Depends(DateTimeAgent)]
# - 요청이 들어오면 Depends가 Agent 객체를 만들고 엔드포인트 함수에 전달한다.


##########################################################
# DateTimeAgent: 현재 시간 조회 및 알람 설정
##########################################################
@router.post("/tool-datetime", response_class=PlainTextResponse)
async def tool_datetime(
    question: Annotated[str, Form()], agent: DateTimeAgentDependency
):
    return await agent.run(question)


##########################################################
# HardwareControlAgent: 차량 번호판 인식 후 차단기 제어
##########################################################
@router.post("/tool-hardware-control", response_class=PlainTextResponse)
async def tool_hardware_control(
    attach: Annotated[UploadFile, Form()],
    agent: HardwareControlAgentDependency,
):
    image_data = await attach.read()
    return await agent.run(image_data, attach.content_type or "image/jpeg")


##########################################################
# FileSystemAgent: 안전한 실습 디렉토리 안에서 파일 작업
##########################################################
@router.post("/tool-file-system", response_class=PlainTextResponse)
async def tool_file_system(
    question: Annotated[str, Form()],
    conversation_id: Annotated[str, Form()],
    agent: FileSystemAgentDependency,
):
    return await agent.run(f"대화 ID: {conversation_id}\n요청: {question}")


##########################################################
# WebSearchAgent: 웹 검색 및 웹페이지 본문 조회
##########################################################
@router.post("/tool-web-search", response_class=PlainTextResponse)
async def tool_web_search(
    question: Annotated[str, Form()], agent: WebSearchAgentDependency
):
    return await agent.run(question)


##########################################################
# ReturnDirectAgent: 도구 결과를 중간 가공 없이 바로 반환
##########################################################
@router.post("/tool-return-direct", response_class=JSONResponse)
async def tool_return_direct(
    question: Annotated[str, Form()],
    agent: ReturnDirectAgentDependency,
):
    response = await agent.run(question)
    logger.info(f"response 타입: {type(response)}, 값: {response}")

    # 방법 1) JSON 문자열을 dict로 변환해서 반환
    # - Tool이 반환한 '{"genre": "...", "movies": [...]}' 문자열을 json.loads()로 dict로 바꾼다.
    # - 브라우저에서는 아래처럼 구조화된 JSON 형태로 표시된다.
    #   {
    #     "genre": "animation",
    #     "movies": ["엣지 오브 투모로우", "인터스텔라", "마션"]
    #   }
    data = json.loads(response)
    return data

    # 방법 2) 교수님 방식: Tool/Agent 응답 문자열을 그대로 반환
    # - json.loads()를 하지 않고 아래처럼 반환한다.
    # - return response
    # - 자연스러운 텍스트 응답 흐름을 보여줄 때 사용할 수 있다.


##########################################################
# ToolContextAgent: 질문 문맥에 난방 시스템 도구 활용
##########################################################
@router.post("/tool-context", response_class=PlainTextResponse)
async def tool_context(
    question: Annotated[str, Form()], agent: HeatingSystemAgentDep
):
    return await agent.run(question)


##########################################################
# StateAgent: 사용자별 상태 저장 및 조회
##########################################################
@router.post("/tool-state", response_class=PlainTextResponse)
async def tool_state(
    question: Annotated[str, Form()],
    user_id: Annotated[str, Form()],
    agent: StateAgentDep,
):
    return await agent.run(question, user_id)
