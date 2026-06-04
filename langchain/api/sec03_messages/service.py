import json
import logging
from typing import Annotated, AsyncGenerator
from venv import logger

from fastapi import Depends
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage


#####################################
# RoleService 서비스 클래스 정의
#####################################
class RoleService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.RoleService")
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
        messages = [
            SystemMessage(
                "당신은 친절하지 않은 해적의 말투로 답변하는 Python 전문가입니다. "
                "항상 코드 예제를 포함하여 설명하세요."
            ),
            HumanMessage(question),
        ]

        # LLM으로 메시지를(HumanMessage(question)]) 보내고(요청) 생성된 응답 메시지(ai 응답)를 가져옴
        ai_message = await self.chat_model.ainvoke(messages)  # aync-invoke를 호출
        self.logger.info(type(ai_message))
        # ai 메시지로부터 응답 텍스트를 얻어 반환
        return str(ai_message.content)

    async def chat_stream(self, question: str) -> AsyncGenerator[str, None]:
        # 사용자 메시지 생성
        messages = [
            SystemMessage(
                "당신은 친절하지 않은 해적의 말투로 답변하는 Python 전문가입니다. "
                "항상 코드 예제를 포함하여 설명하세요."
            ),
            HumanMessage(question),
        ]
        # 비동기 스트리밍 응답을 위한 요청
        async for ai_message_chunk in self.chat_model.astream(messages):
            if ai_message_chunk:
                yield str(ai_message_chunk.content)


####################################
# FewShotService 클래스 정의
####################################
class FewShotService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.FewShotService")

        self.chat_model = init_chat_model(  # 동기방식
            "gpt-4o-mini",
            model_provider="openai",
            temperature=0.0,  # 왜? JSON 정확하게 속성:값. 질문 여러번해도 같은 답 -> 다양하게x => 0.0
        )

    async def chat(self, order: str) -> str:
        # 주문 작성
        order_text = f"""
           고객 주문을 유효한 JSON 형식으로 바꿔주세요.
                추가 설명은 포함하지 마세요.

                예시1:
                작은 피자 하나, 치즈랑 토마토 소스, 페퍼로니 올려서 주세요.
                JSON 응답:
                {{
                "size": "small",
                "type": "normal",
                "ingredients": ["cheese", "tomato sauce", "pepperoni"]
                }}

                예시2:
                큰 피자 하나, 토마토 소스랑 바질, 모짜렐라 올려서 주세요.
                JSON 응답:
                {{
                "size": "large",
                "type": "normal",
                "ingredients": ["tomato sauce", "basil", "mozzarella"]
                }}

                고객 주문: {order}     
        """

        # 사용자 메세지 생성
        # 시스템, 휴먼 각각 지시 넣었을 때, 휴먼메세지가 지시내용 더 우선함
        # => HumanMessage에 지시 내용 적용
        messages = [HumanMessage(order_text)]
        # LLM으로 메세지를 보내고(요청) 응답 메세지(AI Message) 받기
        ai_message = await self.chat_model.ainvoke(messages)  # async invoke
        # AI Message로부터 내용(응답 텍스트)를 얻어 반환
        return str(ai_message.content)


####################################
# StepBackService 클래스 정의
####################################
class StepBackService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.StepBackService")

        self.chat_model = init_chat_model(  # 동기방식
            "gpt-4o-mini",
            model_provider="openai",
            temperature=1.0,  # 질문에 대한 다양한 답변위함
        )

    async def chat(self, question: str) -> str:
        user_text = f"""
            사용자 질문을 처리할 때 Step-Back 프롬프트 기법을 사용하려고 합니다.
            사용자 질문을 단계별 질문들로 재구성해주세요. 
            맨 마지막 질문은 사용자 질문과 일치해야 합니다.
            단계별 질문을 항목으로 하는 JSON 배열로 출력해 주세요.
            예시: ["...", "...", "...", "..."]
            사용자 질문: {question}
        """
        messages = [HumanMessage(user_text)]
        ai_message = await self.chat_model.ainvoke(messages)
        self.logger.info(f"ai_message: {ai_message.content}")

        # 텍스트 응답에서 [...]을 찾아서 list로 변환
        content = str(ai_message.content)
        start_idx = content.find("[")  # 처음에서 찾는다
        end_idx = content.rfind("]") + 1  # 마지막에서 찾는다
        json_text = content[start_idx:end_idx]
        step_questions = json.loads(json_text)

        # 단계별 질문에 대한 답변들을 저장하는 list생성
        answers = []
        # 단계별 답변들을 누적시키는 변수
        context = ""

        # 단계별로 질문하고 응답받기
        for question in step_questions:
            user_text = f"""
                {question}
                문맥: {context}
            """
            messages = [HumanMessage(user_text)]
            ai_message = await self.chat_model.ainvoke(messages)
            answer = str(ai_message.content)
            answers.append(answer)
            context += answer

        # 최종 답변
        final_answer = answers[-1]
        return final_answer


####################################
# ChainOfThoughtService 클래스 정의
####################################
class ChainOfThoughtService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.ChainOfThoughtService")

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

    async def chat(self, question: str) -> AsyncGenerator[str, None]:
        # 사용자 메시지 생성
        user_text = f"""
            {question}
                한 걸음씩 생각해 봅시다.

                [예시]
                질문: 제 동생이 2살일 때, 저는 그의 나이의 두 배였어요.
                지금 저는 40살인데, 제 동생은 몇 살일까요? 한 걸음씩 생각해 봅시다.

                답변: 제 동생이 2살일 때, 저는 2 * 2 = 4살이었어요.
                그때부터 2년 차이가 나며, 제가 더 나이가 많습니다.
                지금 저는 40살이니, 제 동생은 40 - 2 = 38살이에요. 정답은 38살입니다.
        """
        messages = [HumanMessage(user_text)]
        # 비동기 스트리밍 응답을 위한 요청
        iterator = self.chat_model_stream.astream(messages)  # async stream
        async for ai_message_chunk in iterator:  # iterator, 이터러블, 시퀀스 가능
            if ai_message_chunk:
                yield str(ai_message_chunk.content)


####################################
# SelfConsistencyService 클래스 정의
####################################
class SelfConsistencyService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.SelfConsistencyService")

        self.chat_model = init_chat_model(
            "gpt-4o-mini",
            model_provider="openai",  # openai에서 제공하는 모델을 사용하겠다
            temperature=0.0,  # 다양할 필요가 없이 정확해야 한다
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

    async def chat(self, content: str) -> str:
        # 사용자 메시지 생성
        user_text = f"""
            다음 내용을 IMPORTANT, NOT_IMPORTANT 둘 중 하나로 분류해 주세요.
            레이블만 반환하세요.

                내용: {content}
        """
        messages = [HumanMessage(user_text)]

        # 카운팅 변수
        important_count = 0
        not_important_count = 0

        # 5번 반복해서 결과 취합하기
        for i in range(5):
            response = await self.chat_model.ainvoke(messages)
            answer = str(response.content).strip().upper()
            self.logger.info(f"answer: {answer}")
            # 양쪽 공백이 있다면 제거하고, 문자는 모두 대문자로 변환
            if "NOT_IMPORTANT" in answer:
                not_important_count += 1
            else:
                important_count += 1

        # 분류 결과 출력
        result = (
            "IMPORTANT" if important_count > not_important_count else "NOT_IMPORTANT"
        )
        return result


#####################################
# 의존성 주입 위한 타입 힌트 별칭 정의
#####################################
RoleServiceDependency = Annotated[RoleService, Depends(RoleService)]
FewShotServiceDependency = Annotated[FewShotService, Depends(FewShotService)]
StepBackServiceDependency = Annotated[StepBackService, Depends(StepBackService)]
ChainOfThoughtServiceDependency = Annotated[
    ChainOfThoughtService, Depends(ChainOfThoughtService)
]
SelfConsistencyServiceDependency = Annotated[
    SelfConsistencyService, Depends(SelfConsistencyService)
]
