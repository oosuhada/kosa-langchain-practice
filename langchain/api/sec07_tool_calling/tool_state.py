import logging
from typing import Annotated, TypedDict

from fastapi import Depends
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolRuntime
from langgraph.types import Command

from api.common.utils import LoggingCallbackHandler

logger = logging.getLogger(__name__)


##########################################################
# CustomState: 상태(State)를 관리하는 TypedDict
##########################################################
class CustomState(TypedDict):
    # 필수 필드: 대화 내역을 도구 간 공유
    messages: Annotated[list, add_messages]
    # 사용자 정의 필드: 사용자 ID를 도구 간 공유
    user_id: str
    # 사용자 정의 필드: 사용자 역할을 도구 간 공유
    user_role: str


##########################################################
# 도구: update_state
##########################################################
@tool
def update_state(runtime: ToolRuntime) -> Command:
    """user_id를 기반으로 user_role을 결정하여 상태에 저장합니다."""

    # 상태에서 user_id 읽기
    user_id = runtime.state["user_id"]

    # 데이터베이스에서 user_id → user_role 매핑 (가정)
    role_map = {"user1": "admin", "user2": "user", "user3": "guest"}
    user_role = role_map.get(user_id, "guest")

    msg = f"[update_state] {user_id} → role: {user_role} 상태 업데이트함"
    logger.info(msg)

    return Command(
        update={
            # 상태에 user_role 업데이트
            "user_role": user_role,
            # 대화 내역에도 업데이트 메시지 추가 (도구 간 공유)
            "messages": [ToolMessage(content=msg, tool_call_id=runtime.tool_call_id)],
        }
    )


##########################################################
# 도구: check_permission
##########################################################
@tool
def check_permission(runtime: ToolRuntime) -> list[str]:
    """user_role에 따라 권한을 확인합니다."""
    user_role = runtime.state.get("user_role", "guest")

    result = {
        "admin": ["read", "write", "delete"],
        "user": ["read", "write"],
        "guest": ["read"],
    }.get(user_role, [])

    logger.info(f"[권한]: {result}")
    return result


##########################################################
# Agent: StateAgent
##########################################################
class StateAgent:
    def __init__(self, model: str = "openai:gpt-4o-mini"):
        self.logger = logging.getLogger(f"{__name__}.StateAgent")
        # 도구들이 병렬로 실행될때 문제가 될 수 있기 때문에 순차적으로 실행하도록 설정
        # parallel_tool_calls=False: 도구를 한 번에 하나씩 순차 호출(기본: True, 병렬로 실행)
        self.model = init_chat_model(model, model_kwargs={"parallel_tool_calls": False})
        self.agent = create_agent(
            model=self.model,
            tools=[update_state, check_permission],
            state_schema=CustomState,  # type: ignore
            system_prompt="""
                사용자의 요청을 처리할 때 반드시 다음 순서를 따르세요:
                1. update_state 도구로 user_role을 상태에 저장합니다.
                2. check_permission 도구로 현재 user_role의 권한 목록을 확인합니다.
                3. 권한 목록을 기준으로 요청 작업의 가능 여부를 사용자에게 안내합니다.
            """,
        )

    async def run(self, question: str, user_id: str) -> str:
        from typing import Any

        input_state: Any = {
            "messages": [{"role": "user", "content": question}],
            "user_id": user_id,
        }
        result = await self.agent.ainvoke(
            input_state, {"callbacks": [LoggingCallbackHandler()]}
        )
        return result["messages"][-1].content


# FastAPI 의존성 주입 타입 별칭
StateAgentDep = Annotated[StateAgent, Depends(StateAgent)]
