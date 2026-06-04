import logging
from typing import Annotated

from fastapi import Depends
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# InMemorySaver 생성, 모듈 싱글톤
in_memory_saver = InMemorySaver()


# HistoryInMemoryAgent 클래스 정의
class HistoryInMemoryAgent:
    """RAM 기반 checkpointer로 대화 기억을 유지하는 Agent"""

    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.HistoryInMemoryAgent")
        self.agent = create_agent(model=model, checkpointer=in_memory_saver)

    # 에이전트 실행 메소드
    async def run(self, message: str, conversation_id: str) -> str:
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            {"configurable": {"thread_id": conversation_id}},
        )
        return str(result["messages"][-1].content)


HistoryInMemoryAgentDependency = Annotated[
    HistoryInMemoryAgent,
    Depends(HistoryInMemoryAgent),
]
