import logging
from typing import Annotated

from fastapi import APIRouter, Form
from fastapi.responses import PlainTextResponse, Response

from api.sec09_multi_agent.langgraph.supervisor import CustomerSupportSupervisor

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sec09", tags=["sec09"])
supervisor = CustomerSupportSupervisor()


##########################################################
# CustomerSupportSupervisor: 고객 문의를 분석하고 담당 Agent로 라우팅
##########################################################
@router.post("/customer-support", response_class=PlainTextResponse)
async def customer_support(inquiry: Annotated[str, Form()]) -> str:
    return await supervisor.run(inquiry, "user1")


##########################################################
# LangGraph 워크플로우 구조 이미지 조회
##########################################################
@router.get("/graph-structure", response_class=Response)
async def get_graph_structure() -> Response:
    try:
        graph_image = supervisor.get_graph_image()
        return Response(content=graph_image, media_type="image/png")
    except Exception as exc:
        svg = (
            "<svg xmlns='http://www.w3.org/2000/svg' width='900' height='220'>"
            "<rect width='100%' height='100%' fill='white'/>"
            "<text x='20' y='40' font-size='18'>LangGraph customer support workflow</text>"
            f"<text x='20' y='80' font-size='14'>Graph image fallback: {exc}</text>"
            "<text x='20' y='130' font-size='14'>START -> analysis -> user_info/knowledge -> gather -> routed expert -> END</text>"
            "</svg>"
        )
        return Response(content=svg.encode("utf-8"), media_type="image/svg+xml")
