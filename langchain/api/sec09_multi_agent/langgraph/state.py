from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


##########################################################
# LangGraph 공유 상태
##########################################################
# 각 노드는 ShareState를 입력으로 받고, 처리 결과를 dict로 반환하여 상태를 갱신한다.
# messages는 add_messages를 사용해 기존 메시지 목록에 새 메시지를 누적할 수 있다.
# str 타입으로 처리했지만 사실 pydantic 모델이 되면 더 좋다
class ShareState(TypedDict):
    messages: Annotated[list[dict[str, Any]], add_messages]
    user_inquiry: str
    user_id: str
    inquiry_analysis: str
    user_info: str
    knowledge_base: str
    final_response: str
