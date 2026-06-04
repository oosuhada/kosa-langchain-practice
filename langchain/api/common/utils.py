import json
import logging
from typing import Any, override
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler

###############################################################
# 커스텀 콜백 핸들러 - LLM 호출 상세 정보 출력
###############################################################


class LoggingCallbackHandler(BaseCallbackHandler):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.LoggingCallbackHandler")

    # @override
    # def on_llm_start(
    #     self,
    #     serialized: dict[str, Any],
    #     prompts: list[str],
    #     *,
    #     run_id: UUID,
    #     parent_run_id: UUID | None = None,
    #     tags: list[str] | None = None,
    #     metadata: dict[str, Any] | None = None,
    #     **kwargs: Any,
    # ) -> Any:
    #     return super().on_llm_start(
    #         serialized,
    #         prompts,
    #         run_id=run_id,
    #         parent_run_id=parent_run_id,
    #         tags=tags,
    #         metadata=metadata,
    #         **kwargs,
    #     )

    # LLM에 요청할때 바로 실행됨
    def on_llm_start(self, serialized, prompts, **kwargs):
        print("\n*******************************\n")
        print("===== 요청 프롬프트 =====")
        print(prompts)
        print("\n===== 요청 추가 파라미터 =====")
        print(json.dumps(kwargs, indent=2, ensure_ascii=False, default=str))

    # LLM에 응답을 받을때 바로 실행됨
    def on_llm_end(self, response, **kwargs):
        print("\n===== 응답 메시지 =====")
        print(response)
        print("\n===== 응답 추가 파라미터 =====")
        print(json.dumps(kwargs, indent=2, ensure_ascii=False, default=str))
        print("\n*******************************\n")
