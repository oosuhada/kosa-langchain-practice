import json
import logging
from api.sec09_multi_agent.langgraph.state import ShareState
from api.sec09_multi_agent.langgraph.agents.knowledge_agent import KnowledgeAgent

logger = logging.getLogger(__name__)
knowledge_agent = KnowledgeAgent()

async def knowledge_node(state: ShareState) -> dict:
    logger.info("지식 베이스 검색 노드 실행")    
    inquiry = state["user_inquiry"]    
    inquiry_analysis = json.loads(state.get("inquiry_analysis", "{}"))
    inquiry_type = inquiry_analysis.get("inquiry_type", "")    
    search_keywords = f"{inquiry_type} {inquiry}" if inquiry_type else inquiry    
    knowledge = await knowledge_agent.run(search_keywords)
    return {"knowledge_base": knowledge}
