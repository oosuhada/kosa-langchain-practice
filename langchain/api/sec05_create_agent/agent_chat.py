import logging
from typing import Annotated, Any, cast

from fastapi import Depends
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage


class ChatAgent:
    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini") -> None:
        # 로거 생성
        self.logger = logging.getLogger(f"{__name__}.ChatAgent")
        # Agent 생성 방법1 - 모델 설정값을 줄수가 없다
        # self.agent = create_agent(model=model)

        # Agent 생성 방법2 - 모델 설정값을 주고 싶다면 이 방법을 사용한다
        chat_model = init_chat_model(model, temperature=1.0)

        self.chat_model = create_agent(model=chat_model)

    # 에이전트 실행 메소드
    async def run(self, question: str) -> str:
        # Prompt에 들어가는 메시지 목록
        messages = [HumanMessage(question)]

        # LLM으로 요청하고 응답받기
        agent_input = cast(Any, {"messages": messages})
        result = await self.chat_model.ainvoke(agent_input)

        # ai message는 result["messages"] 리스트의 마지막 요소
        ai_message = result["messages"][-1]

        # ai message에서 텍스트 얻기
        response = ai_message.content_blocks
        self.logger.info(type(response))
        return str(response)


# 의존성 주입을 위해서 타입 힌트 정의
ChatAgentDependency = Annotated[ChatAgent, Depends(ChatAgent)]
