import logging
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from langchain_community.document_loaders.parsers.pdf import PyPDFParser
from langchain_core.documents.base import Blob

from api.sec08_rag.agent_rag import RAGAgentDep
from api.sec08_rag.service import (
    EmbeddingServiceDependency,
    SimilaritySearchServiceDependency,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sec08", tags=["sec08"])

# Agent를 사용하는 대화 엔드포인트


##########################################################
# PDF Embedding: 실습 PDF 선택 -> 텍스트 추출 -> 청크 분할 -> 저장소 저장
##########################################################
@router.post("/pdf-embedding", response_class=PlainTextResponse)
async def pdf_embedding(
    title: Annotated[str, Form()],
    author: Annotated[str, Form()],
    attach: Annotated[UploadFile, File()],
    service: EmbeddingServiceDependency,
) -> str:
    logger.info(f"PDF 임베딩 엔드포인트 호출: title={title}, author={author}")

    # 1. 파일 검증
    if attach.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="PDF 파일만 업로드 가능합니다.")

    # 2. PDF 로드 및 임베딩 처리
    content = await attach.read()
    blob = Blob.from_data(content, mime_type="application/pdf")
    parser = PyPDFParser()
    documents = list(parser.lazy_parse(blob))

    # 3. 메타데이터 추가
    documents = service.add_metadata(documents, title=title, author=author)

    # 4. 청크 단위로 분할
    chunks = service.split_documents(documents)

    # 5. 벡터 저장소에 저장
    await service.save_to_vectorstore_with_sqlalchemy(
        collection_name=title,
        chunks=chunks,
    )

    # 6. 결과 반환
    result = (
        "✅ PDF 임베딩 완료!\n\n"
        f"- 컬렉션명: {title}\n"
        f"- 제목: {title}\n"
        f"- 작성자: {author}\n"
        f"- 총 페이지 수: {len(documents)}\n"
        f"- 총 청크 수: {len(chunks)}"
    )
    return result


##########################################################
# Similarity Search: 사용자 질문과 유사한 문서 청크 검색
##########################################################
@router.post("/similarity-search", response_class=PlainTextResponse)
async def similarity_search(
    query: Annotated[str, Form()],
    service: SimilaritySearchServiceDependency,
    collection_name: Annotated[str, Form()] = "대한민국헌법",
    k: Annotated[int, Form()] = 3,
) -> str:
    logger.info(
        f"유사도 검색 엔드포인트 호출: collection_name={collection_name}, query={query}, k={k}"
    )
    return await service.similarity_search(collection_name, query, k)


##########################################################
# RAGAgent: 문서 검색 도구를 사용한 답변 엔드포인트
##########################################################
@router.post("/agent-rag", response_class=PlainTextResponse)
async def agent_rag(
    question: Annotated[str, Form()],
    agent: RAGAgentDep,
    collection_name: Annotated[str, Form()] = "대한민국헌법",
) -> str:
    logger.info(f"RAG Agent 엔드포인트 호출: collection={collection_name}, question={question}")
    return await agent.run(question, collection_name)
