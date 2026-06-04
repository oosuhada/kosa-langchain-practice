import logging
from api.sec09_multi_agent.langgraph.state import ShareState
from api.sec09_multi_agent.langgraph.agents.user_info_agent import UserInfoAgent

logger = logging.getLogger(__name__)
user_info_agent = UserInfoAgent()

async def user_info_node(state: ShareState) -> dict:
    logger.info(f"user_info_node 호출: user_id={state['user_id']}")
    return {"user_info": await user_info_agent.run(state["user_id"])}
