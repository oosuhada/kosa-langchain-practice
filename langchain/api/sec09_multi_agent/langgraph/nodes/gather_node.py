import logging
from api.sec09_multi_agent.langgraph.state import ShareState

logger = logging.getLogger(__name__)

def gather_node(state: ShareState) -> dict:
    logger.info("병렬 실행 완료 대기 노드 실행")
    return {}
