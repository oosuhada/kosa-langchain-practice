import base64
import logging
from typing import Annotated, Any

from fastapi import Depends
from langchain.agents import create_agent
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


def image_message(image_data: bytes, content_type: str) -> dict[str, Any]:
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    return {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": """다음 단계별로 처리해 주세요.
                        1단계: 이미지에서 '(숫자 2개~3개)-(한글 1자)-(숫자 4개)'로 구성된 차량 번호를 인식하세요. 예: 78라1234, 567바2558
                        2단계: 인식된 차량 번호에서 끝에서부터 5번째 문자가 한글 완성형 음절이 아닐 경우에는 다시 1단계로 돌아가세요.
                        3단계: 1단계에서 인식된 차량 번호가 등록된 차량 번호인지 도구로 확인을 하세요.
                        4단계: 3단계의 결과가 False라면 도구로 차단기를 내리고, True라면 도구로 차단기를 올리세요.
                        최종 답변은 차단기 내림 또는 차단기 올림으로 하고 추가 설명은 하지마세요.""",
            },
            {
                "type": "image",
                "base64": image_base64,
                "mime_type": content_type,
            },
        ],
    }


@tool
def check_car_number(car_number: str) -> bool:
    """인식된 차량 번호가 등록되어 있는지 확인합니다.

    Args:
        car_number: 차량 번호

    Returns:
        bool: 등록된 차량이면 True, 아니면 False
    """
    # 데이터베이스에 차량 번호가 등록되어 있다고 가정
    registered_cars: list[str] = ["23가4567", "234부8372", "345가6789"]

    # 차량 번호에 포함된 모든 공백 제거
    car_number = car_number.replace(" ", "")
    logger.info(f"LLM이 인식한 차량 번호: {car_number}")

    # 데이터베이스에 차량 번호가 등록되어 있는지 확인
    result = car_number in registered_cars
    logger.info(f"차량 번호 확인 결과: {result}")
    return result


@tool
def boom_barrier_up() -> str:
    """차단기를 올립니다.

    Returns:
        str: "차단기 올림"
    """
    logger.info("차단기를 올립니다.")
    return "차단기 올림"


@tool
def boom_barrier_down() -> str:
    """차단기를 내립니다.

    Returns:
        str: "차단기 내림"
    """
    logger.info("차단기를 내립니다.")
    return "차단기 내림"


class HardwareControlAgent:
    # Agent 초기화
    # - 이미지 인식은 gpt-4o 모델을 사용한다.
    # - 차량 번호 확인 도구와 차단기 제어 도구를 Agent에 등록한다.
    def __init__(self) -> None:
        self.agent = create_agent(
            model="openai:gpt-4o",
            tools=[check_car_number, boom_barrier_up, boom_barrier_down],
        )

    # Agent 실행
    # - 업로드된 이미지 bytes를 base64 메시지로 변환한다.
    # - Agent는 이미지에서 차량 번호를 읽고, 등록 여부 확인 후 차단기 도구를 호출한다.
    async def run(self, image_data: bytes, content_type: str) -> str:
        result = await self.agent.ainvoke(
            {"messages": [image_message(image_data, content_type)]}
        )
        return str(result["messages"][-1].content)


# FastAPI 의존성 주입 타입 별칭
# - controller.py의 tool_hardware_control 엔드포인트에서 Agent를 주입받기 위해 사용한다.
HardwareControlAgentDependency = Annotated[
    HardwareControlAgent,
    Depends(HardwareControlAgent),
]
