import logging
from api.sec09_multi_agent.langgraph.state import ShareState
from api.sec09_multi_agent.langgraph.agents.order_agent import OrderAgent

logger = logging.getLogger(__name__)
order_agent = OrderAgent()

async def order_node(state: ShareState) -> dict:
    logger.info("주문/배송 관리 노드 실행")
    response = await order_agent.run(
        inquiry=state["user_inquiry"],
        analysis=state["inquiry_analysis"],
        user_info=state["user_info"],
        knowledge=state["knowledge_base"]
    )
    return {"final_response": response}
