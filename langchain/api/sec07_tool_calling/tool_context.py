import logging
import random
from typing import Annotated

from fastapi import Depends
from langchain.agents import create_agent
from langchain_core.tools import tool
from langgraph.prebuilt import ToolRuntime
from pydantic import BaseModel

from api.common.utils import LoggingCallbackHandler

logger = logging.getLogger(__name__)

#==========================================================
# 문맥 (Context) 타입 정의
#==========================================================
class HeatingSystemContext(BaseModel):
    control_key: str


##########################################################
# 도구: get_temperature
# - 센서에서 현재 온도를 읽어옵니다. (가상)
##########################################################
@tool
def get_temperature() -> int:
    """현재 온도를 제공합니다.
    
    Returns:
        int: 현재 온도(18~30도 범위의 정수값)
    """
    logger.info("현재 온도 측정 도구 호출")
    temperature = random.randint(18, 30)
    logger.info(f"측정된 현재 온도: {temperature}도")
    return temperature


##########################################################
# 도구: start_heating_system
# - 타겟 온도까지 난방 시스템을 가동합니다.
##########################################################
@tool
def start_heating_system(
    target_temperature: int,
    runtime: ToolRuntime
) -> str:
    """타겟 온도까지 난방 시스템을 가동합니다.
    
    Args:
        target_temperature: 타겟 온도
        
    Returns:
        str: 난방 시스템 가동이 성공되었을 경우 "success",
             난방 시스템 가동이 실패되었을 경우 "failure"를 반환합니다.
    """
    logger.info(f"난방 시스템 가동 도구 호출: 타겟 온도 {target_temperature}도")
    
    heating_system_context = runtime.context
    
    if heating_system_context and heating_system_context.control_key == "heatingSystemKey":
        return "success"
    else:
        return "failure"


##########################################################
# 도구: stop_heating_system
# - 난방 시스템을 중지합니다.
##########################################################
@tool
def stop_heating_system(
    runtime: ToolRuntime
) -> str:
    """난방 시스템을 중지합니다.
    
    Returns:
        str: 난방 시스템 중지가 성공되었을 경우 "success",
             난방 시스템 중지가 실패되었을 경우 "failure"를 반환합니다.
    """
    logger.info("난방 시스템 중지 도구 호출")
    
    heating_system_context = runtime.context
    
    if heating_system_context and heating_system_context.control_key == "heatingSystemKey":
        return "success"
    else:
        return "failure"


##########################################################
# Agent: HeatingSystemAgent
# - 난방 시스템 제어 문맥을 처리하는 Agent
##########################################################
class HeatingSystemAgent:
    """난방 시스템을 제어하는 Agent"""
    
    def __init__(self, model: str = "openai:gpt-4o-mini"):
        self.model = model
        self.system_prompt = """
        현재 온도가 사용자가 원하는 온도 이상이라면 난방 시스템을 중지하세요.
        현재 온도가 사용자가 원하는 온도 이하라면 난방 시스템을 가동시켜주세요.
        """
        self.tools = [start_heating_system, stop_heating_system, get_temperature]
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            context_schema=HeatingSystemContext
        )

    async def run(self, question: str, control_key: str = "heatingSystemKey") -> str:
        """사용자 질문에 대한 답변을 생성합니다.
        
        Args:
            question: 사용자 질문
            control_key: 난방 시스템 제어 키
            
        Returns:
            str: Agent의 응답 메시지
        """
        result = await self.agent.ainvoke(
            {"messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question}
            ]},
            {"callbacks": [LoggingCallbackHandler()]},
            context=HeatingSystemContext(control_key=control_key)
        )
        return result["messages"][-1].content


# FastAPI 의존성 주입 타입 별칭
HeatingSystemAgentDep = Annotated[
    HeatingSystemAgent,
    Depends(HeatingSystemAgent),
]
