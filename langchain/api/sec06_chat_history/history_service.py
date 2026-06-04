import logging
from typing import Annotated, Any, cast

from fastapi import Depends
from langgraph.checkpoint.base import CheckpointTuple
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from api.common.psycopg_pool_config import psycopg_pool
from api.sec06_chat_history.agent_history_in_memory import in_memory_saver


def _serialize_history(
    conversation_id: str, checkpoint_tuple: CheckpointTuple | None
) -> dict:
    # checkpointer.aget_tuple()은 LangGraph의 CheckpointTuple을 반환한다.
    # 실제 대화 메시지는 checkpoint_tuple.values가 아니라
    # checkpoint_tuple.checkpoint["channel_values"]["messages"]에 저장된다.
    messages = []
    if checkpoint_tuple:
        channel_values: dict[str, Any] = checkpoint_tuple.checkpoint.get(
            "channel_values", {}
        )
        # HumanMessage, AIMessage 같은 LangChain 메시지 객체를
        # 프론트에서 사용하기 쉬운 {"role": ..., "content": ...} 딕셔너리로 변환한다.
        for msg in channel_values.get("messages", []):
            messages.append({"role": msg.type, "content": msg.content})
    return {"conversation_id": conversation_id, "messages": messages}


class HistoryInMemoryService:
    """Agent 없이 RAM 기반 checkpointer의 대화 기록을 조회/삭제한다."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.HistoryInMemoryService")
        self.checkpointer: InMemorySaver = in_memory_saver

    # 대화 히스토리 조회하기
    async def get_history(self, conversation_id: str) -> dict:
        # 현재 conversation_id(thread_id)에 해당하는 최신 checkpoint를 가져온다.
        # 여기서는 LLM을 호출하지 않고, InMemorySaver에 저장된 기록만 조회한다.
        checkpoint_tuple = await self.checkpointer.aget_tuple(
            {"configurable": {"thread_id": conversation_id}}
        )
        return _serialize_history(conversation_id, checkpoint_tuple)

    async def clear_history(self, conversation_id: str) -> dict:
        # 방법 1) 현재 방식: service가 checkpointer를 직접 사용해서 삭제한다.
        # - Agent 실행 없이 저장소의 checkpoint만 삭제한다.
        # - "대화 기록 조회/삭제는 Agent가 없어도 된다"는 역할 분리에 맞다.
        # - LangGraph 타입 힌트가 adelete_thread를 정확히 못 잡아서 cast(Any)를 사용한다.
        await cast(Any, self.checkpointer).adelete_thread(conversation_id)

        # 방법 2) 교수님 방식: agent 안의 checkpointer를 통해 삭제한다.
        # - 예: await self.agent.checkpointer.adelete_thread(conversation_id)
        # - 수업 흐름에서는 run/get_history/clear_history를 한 Agent 클래스에 모아 이해하기 쉽다.
        # - 다만 Pylance는 self.agent.checkpointer를 None 또는 bool일 수도 있다고 판단해
        #   OptionalMemberAccess / AttributeAccessIssue 경고를 표시할 수 있다.
        return {
            "conversation_id": conversation_id,
            "message": "대화 기록이 삭제되었습니다.",
        }


class HistoryPostgreSQLService:
    """Agent 없이 PostgreSQL checkpointer의 대화 기록을 조회/삭제한다."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.HistoryPostgreSQLService")
        self.checkpointer: AsyncPostgresSaver | None = None
        self._initialized = False

    async def _get_checkpointer(self) -> AsyncPostgresSaver:
        # PostgreSQL checkpointer는 최초 요청 시 한 번 생성하고 setup()까지 수행한다.
        # 이후 요청에서는 같은 서비스 인스턴스의 checkpointer를 재사용한다.
        checkpointer = self.checkpointer
        if checkpointer is None:
            checkpointer = AsyncPostgresSaver(psycopg_pool)
            self.checkpointer = checkpointer
        if not self._initialized:
            await checkpointer.setup()
            self._initialized = True
        return checkpointer

    async def get_history(self, conversation_id: str) -> dict:
        checkpointer = await self._get_checkpointer()
        # PostgreSQL에 저장된 최신 checkpoint를 조회한다.
        # InMemory와 동일하게 LLM/Agent 실행 없이 저장소만 읽는다.
        checkpoint_tuple = await checkpointer.aget_tuple(
            {"configurable": {"thread_id": conversation_id}}
        )
        return _serialize_history(conversation_id, checkpoint_tuple)

    async def clear_history(self, conversation_id: str) -> dict:
        checkpointer = await self._get_checkpointer()
        # 방법 1) 현재 방식: PostgreSQL checkpointer를 직접 사용해서 삭제한다.
        # - Agent 실행 없이 PostgreSQL에 저장된 checkpoint만 삭제한다.
        # - 조회/삭제 로직을 HistoryPostgreSQLService에 모아 Agent 역할을 줄인다.
        await cast(Any, checkpointer).adelete_thread(conversation_id)

        # 방법 2) 교수님 방식: agent 안의 checkpointer를 통해 삭제한다.
        # - 예: await self.agent.checkpointer.adelete_thread(conversation_id)
        # - 코드가 한 클래스에 모여 수업 실습에는 단순하다.
        # - 대신 agent.checkpointer 타입이 None/bool 가능성을 포함해 보이면
        #   Pylance 경고가 생길 수 있다.
        return {
            "conversation_id": conversation_id,
            "message": "대화 기록이 삭제되었습니다.",
        }


HistoryInMemoryServiceDependency = Annotated[
    HistoryInMemoryService,
    Depends(HistoryInMemoryService),
]
HistoryPostgreSQLServiceDependency = Annotated[
    HistoryPostgreSQLService,
    Depends(HistoryPostgreSQLService),
]
