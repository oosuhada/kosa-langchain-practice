import logging
from typing import Annotated, AsyncGenerator

from fastapi import Depends
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage


#####################################
# ChatService 서비스 클래스 정의
#####################################
class ChatService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.ChatService")
        self.chat_model = init_chat_model(
            "gpt-4o-mini",
            model_provider="openai",  # openai에서 제공하는 모델을 사용하겠다
            temperature=0.7,  # **kwargs 인자로 전달.
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        self.chat_model_stream = init_chat_model(
            "gpt-4o-mini",
            model_provider="openai",  # openai에서 제공하는 모델을 사용하겠다
            streaming=True,  # 스트리밍 모드 활성화
            temperature=0.7,  # **kwargs 인자로 전달.
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

    async def chat(self, question: str) -> str:
        # 사용자 메시지 생성
        messages = [HumanMessage(question)]

        # LLM으로 메시지를(HumanMessage(question)]) 보내고(요청) 생성된 응답 메시지(ai 응답)를 가져옴
        ai_message = await self.chat_model.ainvoke(messages)  # aync-invoke를 호출
        self.logger.info(type(ai_message))
        # ai 메시지로부터 응답 텍스트를 얻어 반환
        return str(ai_message.content)

    async def stream_chat(self, question: str) -> AsyncGenerator[str, None]:
        # 사용자 메시지 생성
        messages = [HumanMessage(question)]
        # 비동기 스트리밍 응답을 위한 요청
        async for ai_message_chunk in self.chat_model.astream(messages):
            if ai_message_chunk:
                yield str(ai_message_chunk.content)


#####################################
# 의존성 타입 별칭 정의
#####################################
ChatServiceDependency = Annotated[ChatService, Depends(ChatService)]
