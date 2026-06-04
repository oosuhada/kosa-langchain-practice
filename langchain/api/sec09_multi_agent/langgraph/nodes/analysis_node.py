import logging
from api.sec09_multi_agent.langgraph.state import ShareState
from api.sec09_multi_agent.langgraph.agents.analysis_agent import AnalysisAgent

logger = logging.getLogger(__name__)
analysis_agent = AnalysisAgent()

async def analysis_node(state: ShareState) -> dict:
    logger.info(f"analysis_node 호출: inquiry={state['user_inquiry']}")
    return {"inquiry_analysis": await analysis_agent.run(state["user_inquiry"])}
