import logging
from typing import Annotated

from fastapi import Depends
from langchain.agents import create_agent
from langchain.embeddings import init_embeddings
from langchain_core.tools import tool
from langchain_postgres import PGVector

from api.common.utils import LoggingCallbackHandler

logger = logging.getLogger(__name__)


##########################################################
# RAG Agent Tool: 업로드된 문서에서 관련 조각 검색
##########################################################
def make_search_tool(collection_name: str):
    """주어진 컬렉션명을 대상으로 검색하는 tool을 생성한다."""

    @tool
    async def search_documents(query: str, k: int = 3) -> str:
        """
        문서에서 질문과 유사한 내용을 검색하는 도구입니다.

        Args:
            query: 검색할 질문이나 키워드 (예: "대통령 임기", "보험료 청구 방법")
            k: 검색할 문서 개수 (기본값: 3)

        Returns:
            str: 검색된 문서 내용과 메타데이터
        """
        # VectorStore 객체 생성 (sqlalchemy_config.py의 SQLAlchemy 비동기 엔진 사용)
        from api.common.sqlalchemy_config import engine

        vectorstore = PGVector(
            embeddings=init_embeddings(model="openai:text-embedding-3-large"),
            collection_name=collection_name,
            connection=engine,  # SQLAlchemy 비동기 엔진 사용
            async_mode=True,    # 비동기 엔진 전달 시 필수
        )

        # 유사도 검색
        # results: List[Tuple[도큐먼트(Document), 거리(float)]] =
        # [(Document(page_content="...", metadata={"source": "..."}, ...), 0.95), ...]
        # 거리는 0~2 사이의 거리값으로, 0에 가까울수록 유사도가 높음
        results = await vectorstore.asimilarity_search_with_score(query, k=k)

        if not results:
            return f"'{collection_name}'에서 '{query}'와 관련된 문서를 찾을 수 없습니다."

        # 결과를 하나의 문자열로 포맷팅하여 반환
        output_lines = [f"검색 결과: '{query}' ({collection_name})\n"]
        output_lines.append("=" * 80 + "\n")
        for idx, (doc, score) in enumerate(results, 1):
            output_lines.append(f"\n[문서 {idx}] (유사도: {score:.4f})")
            # 메타데이터 출력
            if doc.metadata:
                if "title" in doc.metadata:
                    output_lines.append(f"제목: {doc.metadata['title']}")
                if "author" in doc.metadata:
                    output_lines.append(f"작성자: {doc.metadata['author']}")
                if "page" in doc.metadata:
                    output_lines.append(f"페이지: {doc.metadata['page']}")
                if "source" in doc.metadata:
                    output_lines.append(f"출처: {doc.metadata['source']}")
            # 문서 내용
            output_lines.append(f"\n내용:\n{doc.page_content}\n")
            output_lines.append("-" * 80)
        result_text = "\n".join(output_lines)
        return result_text

    return search_documents


##########################################################
# RAGAgent 클래스 정의
##########################################################
class RAGAgent:
    # 초기화 메소드
    def __init__(self, model: str = "openai:gpt-4o-mini") -> None:
        self.logger = logging.getLogger(f"{__name__}.RAGAgent")
        self.model = model

    # 에이전트 실행 메소드
    async def run(self, question: str, collection_name: str = "대한민국헌법") -> str:
        """RAG Agent를 실행해서 문서 기반 답변을 생성한다."""
        self.logger.info(f"RAG Agent 실행 요청: collection={collection_name}, question={question}")

        # 컬렉션에 맞는 system_prompt 구성
        system_prompt = f"""
            당신은 '{collection_name}' 문서 전문가입니다.

            사용 가능한 도구:
            **search_documents**: 문서 검색

            답변 생성 지침:
            - 사용자의 질문을 받으면 search_documents 도구를 사용하여 관련 내용을 검색합니다.
            - 검색된 문서 내용을 바탕으로 정확하고 상세한 답변을 제공하세요.
            - 답변 시 조항 번호, 페이지 등 출처를 반드시 명시하여 신뢰성을 높이세요.
            - 문서에 없는 내용은 추측하지 말고 "문서에서 해당 정보를 찾을 수 없습니다"라고 답하세요.
        """

        # 컬렉션명을 캡처한 tool 생성
        search_tool = make_search_tool(collection_name)
        agent = create_agent(model=self.model, tools=[search_tool])

        result = await agent.ainvoke(
            {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                ]
            },
            {"callbacks": [LoggingCallbackHandler()]},
        )
        return result["messages"][-1].content


# 의존성 주입을 위한 타입 힌트 별칭 정의
RAGAgentDep = Annotated[RAGAgent, Depends(RAGAgent)]
