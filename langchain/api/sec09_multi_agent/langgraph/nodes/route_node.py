import json
import logging
from api.sec09_multi_agent.langgraph.state import ShareState

logger = logging.getLogger(__name__)

def route_node_fun(state: ShareState) -> str:
    logger.info("조건 분기 함수 실행")    
    inquiry_analysis = json.loads(state.get("inquiry_analysis", "{}"))
    inquiry_type = inquiry_analysis.get("inquiry_type", "일반문의")
    if inquiry_type == "기술지원":
        return "tech_support"
    elif inquiry_type == "주문/배송":
        return "order"
    elif inquiry_type == "환불/교환":
        return "refund"
    elif inquiry_type == "계정관리":
        return "account"
    else:
        return "general"
