import logging
from typing import Annotated

from fastapi import Depends
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

from api.sec04_structured_output.model import Movie, Person, PizzaOrder


#####################################
# StructuredOutputService 서비스 클래스 정의
#####################################
class StructuredOutputService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.StructuredOutputService")
        self.chat_model = init_chat_model(
            model="gpt-4o-mini",
            model_provider="openai",  # openai에서 제공하는 모델을 사용하겠다
            temperature=0.0,  # JSON 정확하게 속성:값. 질문 여러번해도 같은 답 -> 다양하게x => 0.0
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

    # 서술식 회원정보 문장 -> LLM이 서술식 문장을 JSON으로 변환하고 -> JSON을 Person형태로 반환
    async def structured_output_person(self, content: str) -> Person:
        messages = [
            HumanMessage(content),
        ]
        structured_chat_model = self.chat_model.with_structured_output(Person)
        result = await structured_chat_model.ainvoke(messages)
        if isinstance(result, Person):
            return result
        # if isinstance(result, dict):
        #     return Person.model_validate(result)
        # if isinstance(result, BaseModel):
        #     return Person.model_validate(result.model_dump())
        # -> 이렇게 할수도 있다는 점을 알려주기 위해서

        raise TypeError(f"Unexpected structured output type: {type(result)}")

    # 영화 이름 -> LLM이 영화 정보를 JSON으로 변환하고 -> JSON을 Movie형태로 반환
    async def structured_output_movie(self, content: str) -> Movie:
        messages = [
            HumanMessage(content),
        ]
        structured_chat_model = self.chat_model.with_structured_output(Movie)
        result = await structured_chat_model.ainvoke(messages)
        if isinstance(result, Movie):
            return result
        raise TypeError(f"Unexpected structured output type: {type(result)}")

    # 피자 주문(음성) -> 텍스트 변환 -> LLM이 JSON으로 변환 -> PizzaOrder 반환
    async def structured_output_pizza(self, order: str) -> PizzaOrder:
        messages = [
            HumanMessage(order),
        ]
        structured_chat_model = self.chat_model.with_structured_output(PizzaOrder)
        result = await structured_chat_model.ainvoke(messages)
        if isinstance(result, PizzaOrder):
            return result
        raise TypeError(f"Unexpected structured output type: {type(result)}")


#####################################
# 의존성 주입을 위한 타입 힌트 정의
#####################################
StructuredOutputServiceDependency = Annotated[
    StructuredOutputService, Depends(StructuredOutputService)
]
