import logging
from datetime import datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import Depends
from langchain.agents import create_agent
from langchain_core.tools import tool

from api.common.utils import LoggingCallbackHandler

logger = logging.getLogger(__name__)


@tool
def get_current_datetime() -> str:
    """현재 날짜와 시간 정보를 ISO-8601 형식의 한국 시간 문자열로 제공합니다."""
    current_datetime = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
    logger.info(f"현재 날짜와 시간: {current_datetime}")
    return current_datetime


@tool
def set_alarm(time: str) -> str:
    """지정된 시간에 알람을 설정합니다.

    Args:
        time: ISO-8601 형식의 시간 (예: 2025-07-03T14:30:00+09:00)

    Returns:
        str: 알람 설정 성공 메시지 또는 실패 시 에러 메시지
    """
    # LLM이 잘못된 시간 형식을 제공할 수 있음 (예: T24:12:29)
    # ISO-8601에서는 24시는 유효하지 않으므로 0시로 변환하고 날짜를 +1
    if "T24:" in time:
        # "T" 기준으로 날짜와 시간 분리
        t_index = time.index("T")
        date_part = time[:t_index]
        time_part = time[t_index + 1 :]

        # 날짜 +1일
        date_obj = datetime.fromisoformat(date_part)
        date_obj = date_obj + timedelta(days=1)
        date_part = date_obj.strftime("%Y-%m-%d")

        # "24:" -> "00:"으로 교체
        time_part = time_part.replace("24:", "00:", 1)

        # 재조합
        time = f"{date_part}T{time_part}"

    # ISO-8601 형식으로 파싱
    alarm_time = datetime.fromisoformat(time)
    logger.info(f"알람 설정 시간: {alarm_time}")
    return f"알람이 {alarm_time.strftime('%Y-%m-%d %H:%M:%S')}에 설정되었습니다."


class DateTimeAgent:
    # Agent 초기화
    # - create_agent()에 사용할 모델과 도구 목록을 등록한다.
    # - get_current_datetime, set_alarm 도구는 LLM이 필요하다고 판단할 때 호출된다.
    def __init__(self) -> None:
        self.agent = create_agent(
            model="openai:gpt-4o-mini",
            tools=[get_current_datetime, set_alarm],
            system_prompt="당신은 날짜와 시간 계산을 도와주는 Agent입니다.",
        )

    # Agent 실행
    # - 사용자의 질문을 LangChain 메시지 형식으로 전달한다.
    # - Agent가 필요한 도구를 호출한 뒤 최종 AI 메시지를 반환한다.
    async def run(self, question: str) -> str:
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": question}]},
            {"callbacks": [LoggingCallbackHandler()]},
        )
        return str(result["messages"][-1].content)


# FastAPI 의존성 주입 타입 별칭
# - controller.py에서 agent: DateTimeAgentDependency로 선언하면
#   Depends가 DateTimeAgent 인스턴스를 생성해 엔드포인트 함수에 주입한다.
DateTimeAgentDependency = Annotated[DateTimeAgent, Depends(DateTimeAgent)]


class DateTimeContextAgent:
    # Agent 초기화
    # - tool-context.html에서 사용하는 문맥 보강 예제용 Agent이다.
    # - 별도 도구가 있는 것은 아니고, 날짜/시간 도구를 문맥 판단에 활용한다.
    def __init__(self) -> None:
        self.agent = create_agent(
            model="openai:gpt-4o-mini",
            tools=[get_current_datetime, set_alarm],
            system_prompt=(
                "당신은 날짜와 시간 문맥을 판단하는 Agent입니다. "
                "사용자의 요청에 현재 시간이 필요하면 get_current_datetime 도구를 사용하고, "
                "알람 설정이 필요하면 set_alarm 도구를 사용하세요."
            ),
        )

    # Agent 실행
    # - controller.py의 /tool-context 엔드포인트에서 호출된다.
    # - 사용자의 질문에 현재 시간 도구 사용 지시를 덧붙여 전달한다.
    async def run(self, question: str) -> str:
        prompt = f"{question}\n필요하면 현재 시간 도구를 사용해 문맥을 보강하세요."
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]},
            {"callbacks": [LoggingCallbackHandler()]},
        )
        return str(result["messages"][-1].content)


# FastAPI 의존성 주입 타입 별칭
# - tool-context 전용 Agent를 Depends로 생성해 주입한다.
DateTimeContextAgentDependency = Annotated[
    DateTimeContextAgent,
    Depends(DateTimeContextAgent),
]
