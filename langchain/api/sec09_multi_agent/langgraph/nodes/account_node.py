import logging
from api.sec09_multi_agent.langgraph.state import ShareState
from api.sec09_multi_agent.langgraph.agents.account_agent import AccountAgent

logger = logging.getLogger(__name__)
account_agent = AccountAgent()

async def account_node(state: ShareState) -> dict:
    logger.info("계정 관리 노드 실행")
    response = await account_agent.run(
        inquiry=state["user_inquiry"],
        analysis=state["inquiry_analysis"],
        user_info=state["user_info"],
        knowledge=state["knowledge_base"]
    )
    return {"final_response": response}
