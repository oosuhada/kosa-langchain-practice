import logging
from pydantic import BaseModel
from langchain.agents import create_agent

class AnalysisResult(BaseModel):
    """문의 분석 결과 스키마"""
    keywords: str
    intent: str
    emotion: str
    urgency: str
    inquiry_type: str

class AnalysisAgent:
    def __init__(self, model: str = "openai:gpt-4o-mini"):
        self.logger = logging.getLogger(f"{__name__}.AnalysisAgent")
        system_prompt ="""
            당신은 고객 문의 분석 전문가입니다. 
            고객의 문의 내용을 분석하여 다음과 같은 정보를 추출해야 합니다:
            1. keywords: 문의의 핵심 키워드들을 쉼표로 구분하여 나열하세요.
            2. intent: 고객이 문의를 통해 원하는 것이 무엇인지 간단히 설명하세요.
            3. emotion: 고객의 감정 상태를 불만, 중립, 긍정 등으로 분류하세요.
            4. urgency: 문의의 긴급도를 높음, 보통, 낮음으로 평가하세요.
            5. inquiry_type: 다음 카테고리 중 하나로 문의 유형을 분류하세요.
                - 기술지원: 제품 작동 오류, 고장, 버그, 설정 문제, 기능 문의
                - 주문/배송: 주문 조회, 배송 추적, 배송 지연, 출고 문의
                - 환불/교환: 환불 요청, 교환 요청, 취소, 반품
                - 계정관리: 로그인, 비밀번호, 회원 정보 수정, 탈퇴
                - 일반문의: 위 카테고리에 해당하지 않는 모든 문의
        """
        self.agent = create_agent(
            model=model,
            system_prompt=system_prompt,
            response_format=AnalysisResult
        )        

    async def run(self, inquiry: str) -> str:
        self.logger.info("문의 분석 에이전트 실행")        
        result = await self.agent.ainvoke({"messages": [{"role": "user", "content": inquiry}]})        
        analysis: AnalysisResult = result["structured_response"]
        return analysis.model_dump_json()
