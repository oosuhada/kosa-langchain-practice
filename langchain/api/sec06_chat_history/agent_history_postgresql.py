import logging
from typing import Annotated, Any

from fastapi import Depends
from langchain.agents import create_agent
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph.state import CompiledStateGraph

from api.common.psycopg_pool_config import psycopg_pool


class HistoryPostgreSQLAgent:
    """PostgreSQL checkpointer로 영구 대화 기억을 유지하는 Agent"""

    def __init__(self, model: str = "openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.HistoryPostgreSQLAgent")
        self.model = model
        self.agent: CompiledStateGraph[Any, Any, Any, Any] | None = None

    async def _get_agent(self) -> CompiledStateGraph[Any, Any, Any, Any]:
        if self.agent is None:
            checkpointer = AsyncPostgresSaver(psycopg_pool)
            await checkpointer.setup()
            self.agent = create_agent(model=self.model, checkpointer=checkpointer)
        return self.agent

    async def run(self, message: str, conversation_id: str) -> str:
        agent = await self._get_agent()
        result = await agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            {"configurable": {"thread_id": conversation_id}},
        )
        return str(result["messages"][-1].content)


HistoryPostgreSQLAgentDependency = Annotated[
    HistoryPostgreSQLAgent,
    Depends(HistoryPostgreSQLAgent),
]
