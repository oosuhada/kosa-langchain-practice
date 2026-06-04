import asyncio
import logging
import sys
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends

from langchain.embeddings import init_embeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.common.utils import LoggingCallbackHandler

logger = logging.getLogger(__name__)


# Mac 전용 실습 PDF 파일 경로
PRACTICE_PDF_FILES: dict[str, dict[str, str]] = {
    "constitution": {
        "title": "대한민국헌법",
        "author": "법제처",
        "path": "/Users/gabriel/Development/kosa-class-practice/langchain/api/sec08_rag/대한민국헌법(19880225).pdf",
    },
    "insurance": {
        "title": "삼성화재자동차보험약관",
        "author": "삼성화재",
        "path": "/Users/gabriel/Development/kosa-class-practice/langchain/api/sec08_rag/삼성화재자동차보험약관.pdf",
    },
}


##########################################################
# EmbeddingService 클래스 정의
##########################################################
class EmbeddingService:
    # 초기화 메소드
    def __init__(self) -> None:
        # 로거 생성
        self.logger = logging.getLogger(f"{__name__}.EmbeddingService")

        # 실습 PDF 파일들이 위치한 sec08_rag 디렉토리 사용
        self.pdf_dir = Path(
            "/Users/gabriel/Development/kosa-class-practice/langchain/api/sec08_rag"
        )

    # 실습 PDF 파일 경로 가져오기 메소드
    def get_practice_pdf_path(self, document_key: str) -> Path:
        # HTML에서 전달한 문서 키로 실습 PDF 파일 정보 조회
        document_info = PRACTICE_PDF_FILES.get(document_key)
        if not document_info:
            raise ValueError(f"지원하지 않는 실습 문서입니다: {document_key}")

        # Mac 전용 절대 경로를 Path 객체로 변환
        return Path(document_info["path"])

    # 실습 PDF 파일 정보 가져오기 메소드
    def get_practice_pdf_info(self, document_key: str) -> dict[str, str]:
        # 문서 제목, 작성자, 파일 경로 정보를 반환
        document_info = PRACTICE_PDF_FILES.get(document_key)
        if not document_info:
            raise ValueError(f"지원하지 않는 실습 문서입니다: {document_key}")
        return document_info

    # 파일 존재 여부 확인 메소드
    def check_file_exists(self, path: Path) -> None:
        # PDF 파일이 실제로 존재하는지 확인
        if not path.exists():
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {path}")

        # 전달된 경로가 파일인지 확인
        if not path.is_file():
            raise FileNotFoundError(f"PDF 파일 경로가 아닙니다: {path}")

    # 파일 로더 생성 메소드
    def create_pdf_loader(self, path: Path) -> PyPDFLoader:
        # LangChain에서 제공하는 PDF 문서 로더 생성
        self.logger.info(f"PDF 파일 로더 생성: {path}")
        return PyPDFLoader(str(path))

    # PDF 파일 로드 메소드
    async def load_pdf(self, file_path: str | Path) -> list[Document]:
        # PDF 파일을 로드해서 Document 목록으로 반환한다.
        path = Path(file_path)
        self.logger.info(f"PDF 파일 로드: {path}")

        # 1. 파일 존재 여부 확인
        self.check_file_exists(path)

        # 2. PDF 파일 로더 생성
        loader = self.create_pdf_loader(path)

        # 3. PDF 파일을 LangChain Document 목록으로 로드
        documents = await asyncio.to_thread(loader.load)

        # 4. 로드된 Document 목록 반환
        return documents

    # PDF Embedding 메소드
    async def pdf_embedding(
        self,
        document_key: str,
    ) -> str:
        # 실습 PDF 선택 -> 텍스트 추출 -> 청크 분할 -> 저장소 저장
        document_info = self.get_practice_pdf_info(document_key)
        pdf_path = self.get_practice_pdf_path(document_key)

        title = document_info["title"]
        author = document_info["author"]
        filename = pdf_path.name

        self.logger.info(
            f"PDF 임베딩 시작: title={title}, author={author}, file={filename}"
        )

        # 1. Mac 전용 절대 경로의 실습 PDF 파일을 Document 목록으로 로드한다.
        loaded_documents = await self.load_pdf(pdf_path)

        # 2. 로드된 Document 목록에 실습 문서 메타데이터를 추가한다.
        loaded_documents = self.add_metadata(
            loaded_documents,
            {
                "title": title,
                "author": author,
                "source": filename,
                "path": str(pdf_path),
            },
        )

        # 3. Document 목록을 청크 목록으로 분할한다.
        chunks = self.split_documents(loaded_documents)

        # 4. PGVector 벡터 저장소에 청크를 저장한다.
        result = await self.save_to_vectorstore_with_sqlalchemy(
            collection_name=title,
            chunks=chunks,
        )
        count = len(result)
        self.logger.info(f"PDF 임베딩 완료: {count}개 청크 저장")

        return f"{title} PDF 문서를 {count}개 청크로 분할하여 PGVector 벡터 저장소에 저장했습니다."

    # 메타데이터 추가 메소드
    # 청크로 쪼개기 전에 메타데이터 추가하는게 좋다
    def add_metadata(
        self,
        documents: list[Document],
        metadata: dict[str, str] | None = None,
        *,
        title: str | None = None,
        author: str | None = None,
    ) -> list[Document]:
        # 수업자료처럼 title/author를 직접 받을 수도 있고, 기존 코드처럼 dict로 받을 수도 있게 처리
        if metadata is None:
            metadata = {}
        if title is not None:
            metadata["title"] = title
        if author is not None:
            metadata["author"] = author

        # 메타데이터가 있으면 모든 Document에 동일한 메타데이터를 추가
        if metadata:
            for doc in documents:
                for key, value in metadata.items():
                    doc.metadata[key] = value
        return documents

    # --------------------------------------------------------------------------
    # Document 목록을 분할된 청크 목록으로 분할
    # --------------------------------------------------------------------------
    def split_documents(self, documents: list[Document]) -> list[Document]:
        # RecursiveCharacterTextSplitter: 텍스트를 일정한 크기로 분할하는 도구
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,  # 각 청크의 최대 토큰 수
            chunk_overlap=50,  # 청크 간 겹치는 토큰 수
            length_function=len,  # 텍스트 길이를 계산하는 함수
        )
        # Document 목록을 입력으로 받아서 청크 목록을 반환
        chunks = text_splitter.split_documents(documents)
        return chunks

    # --------------------------------------------------------------------------
    # PGVector에 임베딩 저장(커넥션 문자열 사용 버전)
    # --------------------------------------------------------------------------
    async def save_to_vectorstore(
        self,
        collection_name: str,
        chunks: list[Document],
    ) -> list[str]:
        # VectorStore 객체 생성
        vectorstore = PGVector(
            embeddings=init_embeddings(model="openai:text-embedding-3-large"),
            collection_name=collection_name,
            connection="postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
            async_mode=True,
        )

        # 청크 도큐먼트들을 각각 임베딩해서 벡터 저장소에 행으로 저장
        chunk_documents = chunks
        result = await vectorstore.aadd_documents(chunk_documents)
        return result

    # --------------------------------------------------------------------------
    # PGVector에 임베딩 저장(SQLAlchemy 비동기 엔진 사용 버전)
    # --------------------------------------------------------------------------
    async def save_to_vectorstore_with_sqlalchemy(
        self,
        collection_name: str,
        chunks: list[Document],
    ) -> list[str]:
        # VectorStore 객체 생성 (sqlalchemy_config.py의 SQLAlchemy 비동기 엔진 사용)
        from api.common.sqlalchemy_config import engine

        vectorstore = PGVector(
            embeddings=init_embeddings(model="openai:text-embedding-3-large"),
            collection_name=collection_name,
            connection=engine,  # 커넥션 문자열 대신 엔진 객체 (커넥션 풀 사용)
            async_mode=True,  # 비동기 엔진 전달 시 필수
        )

        # 청크 도큐먼트들을 각각 임베딩해서 벡터 저장소에 행으로 저장
        chunk_documents = chunks
        result = await vectorstore.aadd_documents(chunk_documents)
        return result


def test_embedding() -> None:
    import selectors

    load_dotenv(".env")
    service = EmbeddingService()
    documents = asyncio.run(
        service.load_pdf(
            "/Users/gabriel/Development/kosa-class-practice/langchain/api/sec08_rag/대한민국헌법(19880225).pdf"
        )
    )

    documents = service.add_metadata(
        documents,
        title="대한민국헌법",
        author="국회",
    )

    chunks = service.split_documents(documents)

    asyncio.run(
        service.save_to_vectorstore_with_sqlalchemy(
            collection_name="대한민국헌법",
            chunks=chunks,
        ),
        # Windows는 기본적으로 ProactorEventLoop를 사용
        # - psycopg 비동기 드라이버가 이를 지원하지 않아 오류가 발생
        # - loop_factory로 SelectorEventLoop를 지정해서 호환성 문제를 해결.
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
    )

    print("[임베딩 저장 완료]")


def test_pdf_split() -> None:
    service = EmbeddingService()
    documents = asyncio.run(
        service.load_pdf(
            "/Users/gabriel/Development/kosa-class-practice/langchain/api/sec08_rag/대한민국헌법(19880225).pdf"
        )
    )

    documents = service.add_metadata(
        documents,
        title="대한민국헌법",
        author="국회",
    )

    print(f"총 도큐먼트 수: {len(documents)}", "\n")
    print(f"첫 도큐먼트 내용: {documents[0].page_content}", "\n")
    print(f"첫 도큐먼트의 메타데이터: {documents[0].metadata}")

    chunks = service.split_documents(documents)
    print(f"총 청크 수: {len(chunks)}", "\n")
    print(f"첫 청크 내용: {chunks[0].page_content}", "\n")
    print(f"첫 청크의 메타데이터: {chunks[0].metadata}")


##########################################################
# SimilaritySearchService 클래스 정의
##########################################################
class SimilaritySearchService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(f"{__name__}.SimilaritySearchService")

    def format_search_results(
        self,
        query: str,
        results: list[tuple[Document, float]],
        content_limit: int = 1200,
        title: str = "검색어",
    ) -> str:
        """검색 결과를 화면에 출력하기 좋은 텍스트로 변환한다."""
        if not results:
            return "검색할 문서가 없습니다. 먼저 PDF Embedding을 실행하세요."

        lines = [f"{title}: {query}", "=" * 80]
        for idx, (doc, score) in enumerate(results, 1):
            lines.append(f"\n[문서 {idx}] 유사도: {score:.4f}")
            lines.append(f"제목: {doc.metadata.get('title', 'unknown')}")
            lines.append(f"작성자: {doc.metadata.get('author', 'unknown')}")
            lines.append(f"페이지: {doc.metadata.get('page', 'unknown')}")
            lines.append(f"출처: {doc.metadata.get('source', 'unknown')}")
            lines.append(str(doc.page_content)[:content_limit])
        return "\n".join(lines)

    # 유사도 검색하기
    async def similarity_search(
        self,
        collection_name: str,
        query: str,
        k: int = 3,
    ) -> str:  # 유사 거리가 가장 가까운 3개
        """사용자 질문과 유사한 문서 청크를 검색한다."""
        self.logger.info(
            f"유사도 검색 요청: collection_name={collection_name}, query={query}, k={k}"
        )

        # VectorStore 객체 생성 (sqlalchemy_config.py의 SQLAlchemy 비동기 엔진 사용)
        from api.common.sqlalchemy_config import engine

        vectorstore = PGVector(
            embeddings=init_embeddings(model="openai:text-embedding-3-large"),
            collection_name=collection_name,
            connection=engine,  # SQLAlchemy 비동기 엔진 사용
            async_mode=True,  # 비동기 엔진 전달 시 필수
        )

        # 유사도 검색
        # results: List[Tuple[도큐먼트(Document), 거리(float)]] =
        # [(Document(page_content="...", metadata={"source": "..."}, ...), 0.95), ...]
        # 거리는 0~2 사이의 거리값으로, 0에 가까울수록 유사도가 높음
        results = await vectorstore.asimilarity_search_with_score(query, k=k)
        if not results:
            return f"{collection_name}에서 '{query}'와 관련된 문서를 찾을 수 없습니다."

        return "\n".join(
            [
                f"거리: {distance}, 내용: {doc.page_content[:30]}"
                for doc, distance in results
            ]
        )
        # 방식2
        # - 검색 결과를 format_search_results() 메소드로 넘겨서 화면 출력용 문자열로 변환.
        # - 거리와 본문 일부만 보여주는 현재 방식보다 제목, 작성자, 페이지, 출처,
        #   본문 일부(content_limit)까지 자세히 확인할 수 있다.
        # - 수업자료의 간단 출력 방식과 맞추기 위해 현재는 위의 "\n".join(...) 방식을 사용한다.
        #
        # return self.format_search_results(
        #     query,
        #     results,
        #     content_limit=1200,
        #     title=f"검색 결과: {collection_name}",
        # )


def test_similarity_search() -> None:
    import selectors

    load_dotenv(".env")
    service = SimilaritySearchService()
    result = asyncio.run(
        service.similarity_search(
            collection_name="대한민국헌법",
            query="대통령의 임기는 몇 년인가요?",
            k=3,
        ),
        # Windows는 기본적으로 ProactorEventLoop를 사용
        # - psycopg 비동기 드라이버가 이를 지원하지 않아 오류가 발생
        # - loop_factory로 SelectorEventLoop를 지정해서 호환성 문제를 해결.
        loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
    )
    print(f"[유사도 검색 결과]\n{result}")


if __name__ == "__main__":
    # 벡터 저장은 이미 한 번 처리했다면 다시 실행하지 않는다.
    # 다시 실행하면 같은 문서 청크가 langchain_pg_embedding 테이블에 중복 저장될 수 있다.
    # test_embedding()
    test_similarity_search()





# 의존성 주입을 위한 타입 힌트 별칭 정의
EmbeddingServiceDependency = Annotated[EmbeddingService, Depends(EmbeddingService)]
SimilaritySearchServiceDependency = Annotated[
    SimilaritySearchService,
    Depends(SimilaritySearchService),
]
