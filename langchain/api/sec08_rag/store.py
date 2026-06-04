from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RagDocument:
    """RAG 검색을 위해 메모리에 저장할 문서 청크."""

    content: str
    metadata: dict[str, str | int] = field(default_factory=dict)


# 실습용 메모리 벡터 저장소 역할을 하는 리스트
DOCUMENTS: list[RagDocument] = []


def add_documents(docs: list[RagDocument]) -> int:
    """청크 목록을 메모리 저장소에 추가하고 추가 개수를 반환한다."""
    DOCUMENTS.extend(docs)
    return len(docs)


def clear_documents() -> None:
    DOCUMENTS.clear()


def tokenize(text: str) -> set[str]:
    """간단한 유사도 계산을 위해 한글/영문/숫자 토큰만 추출한다."""
    return set(re.findall(r"[가-힣A-Za-z0-9]+", text.lower()))


def similarity(query: str, text: str) -> float:
    """질문 토큰과 문서 토큰의 겹침 정도로 간단한 유사도를 계산한다."""
    q_tokens = tokenize(query)
    t_tokens = tokenize(text)
    if not q_tokens or not t_tokens:
        return 0.0
    intersection = len(q_tokens & t_tokens)
    return intersection / math.sqrt(len(q_tokens) * len(t_tokens))


def search(query: str, k: int = 3) -> list[tuple[RagDocument, float]]:
    """저장된 문서 중 질문과 가장 유사한 상위 k개 청크를 반환한다."""
    scored = [(doc, similarity(query, doc.content)) for doc in DOCUMENTS]
    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]


def chunk_text(text: str, source: str, chunk_size: int = 800) -> list[RagDocument]:
    """긴 텍스트를 일정 크기의 문단 단위 청크로 나눈다."""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks: list[RagDocument] = []
    buffer = ""
    page = 1
    for paragraph in paragraphs or [text]:
        if len(buffer) + len(paragraph) > chunk_size and buffer:
            chunks.append(
                RagDocument(buffer, {"source": source, "page": page, "title": source})
            )
            page += 1
            buffer = ""
        buffer += ("\n\n" if buffer else "") + paragraph
    if buffer:
        chunks.append(RagDocument(buffer, {"source": source, "page": page, "title": source}))
    return chunks


def save_upload(path: Path, data: bytes) -> Path:
    """업로드된 PDF 바이트를 임시 디렉토리에 저장한다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path
