import logging
from api.sec09_multi_agent.langgraph.state import ShareState
from api.sec09_multi_agent.langgraph.agents.general_agent import GeneralAgent

logger = logging.getLogger(__name__)
general_agent = GeneralAgent()

async def general_node(state: ShareState) -> dict:
    logger.info("일반 문의 노드 실행")
    response = await general_agent.run(
        inquiry=state["user_inquiry"],
        analysis=state["inquiry_analysis"],
        user_info=state["user_info"],
        knowledge=state["knowledge_base"]
    )
    return {"final_response": response}
