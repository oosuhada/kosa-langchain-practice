import logging

from langgraph.graph import END, START, StateGraph

from api.sec09_multi_agent.langgraph.nodes import (
    account_node,
    analysis_node,
    gather_node,
    general_node,
    knowledge_node,
    order_node,
    refund_node,
    route_node_fun,
    tech_support_node,
    user_info_node,
)
from api.sec09_multi_agent.langgraph.state import ShareState


class CustomerSupportSupervisor:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.CustomerSupportSupervisor")
        self.build_workflow()

    ##########################################################
    # LangGraph 워크플로우 구성
    ##########################################################
    def build_workflow(self) -> None:
        graph = StateGraph(ShareState)
        # 1. 그래프에 노드 등록
        graph.add_node("analysis", analysis_node)
        graph.add_node("user_info", user_info_node)
        graph.add_node("knowledge", knowledge_node)
        graph.add_node("gather", gather_node)
        graph.add_node("tech_support", tech_support_node)
        graph.add_node("order", order_node)
        graph.add_node("refund", refund_node)
        graph.add_node("account", account_node)
        graph.add_node("general", general_node)

        # 2. 시작 노드에서 문의 분석 수행
        graph.add_edge(START, "analysis")

        # 3. 분석 후 사용자 정보와 지식 베이스를 병렬로 조회
        graph.add_edge("analysis", "user_info")
        graph.add_edge("analysis", "knowledge")

        # 4. 병렬 조회 결과를 gather 노드로 모음
        graph.add_edge("user_info", "gather")
        graph.add_edge("knowledge", "gather")

        # 5. 문의 유형에 따라 전문 Agent 노드로 조건부 라우팅
        graph.add_conditional_edges(
            "gather",
            route_node_fun,
            {
                "tech_support": "tech_support",
                "order": "order",
                "refund": "refund",
                "account": "account",
                "general": "general",
            },
        )

        # 6. 전문 Agent가 최종 답변을 만들면 워크플로우 종료
        graph.add_edge("tech_support", END)
        graph.add_edge("order", END)
        graph.add_edge("refund", END)
        graph.add_edge("account", END)
        graph.add_edge("general", END)
        self.work_flow = graph.compile()

    ##########################################################
    # 워크플로우 실행
    ##########################################################
    async def run(self, inquiry: str, user_id: str = "user1") -> str:
        initial_state: ShareState = {
            "messages": [],
            "user_inquiry": inquiry,
            "user_id": user_id,
            "inquiry_analysis": "",
            "user_info": "",
            "knowledge_base": "",
            "final_response": "",
        }
        result = await self.work_flow.ainvoke(initial_state)
        return result["final_response"]

    ##########################################################
    # 그래프 구조 이미지 생성
    ##########################################################
    def get_graph_image(self) -> bytes:
        return self.work_flow.get_graph().draw_mermaid_png()
