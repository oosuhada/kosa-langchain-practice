import logging
from api.sec09_multi_agent.langgraph.state import ShareState
from api.sec09_multi_agent.langgraph.agents.refund_agent import RefundAgent

logger = logging.getLogger(__name__)
refund_agent = RefundAgent()

async def refund_node(state: ShareState) -> dict:
    logger.info("환불/교환 노드 실행")
    response = await refund_agent.run(
        inquiry=state["user_inquiry"],
        analysis=state["inquiry_analysis"],
        user_info=state["user_info"],
        knowledge=state["knowledge_base"]
    )
    return {"final_response": response}
