import logging
from api.sec09_multi_agent.langgraph.state import ShareState
from api.sec09_multi_agent.langgraph.agents.tech_support_agent import TechSupportAgent

logger = logging.getLogger(__name__)
tech_support_agent = TechSupportAgent()

async def tech_support_node(state: ShareState) -> dict:
    logger.info("기술 지원 노드 실행")
    response = await tech_support_agent.run(
        inquiry=state["user_inquiry"],
        analysis=state["inquiry_analysis"],
        user_info=state["user_info"],
        knowledge=state["knowledge_base"]
    )
    return {"final_response": response}
