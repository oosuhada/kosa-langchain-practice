from typing import Annotated

from pydantic import BaseModel, Field


class Movie(BaseModel):
    """Agent의 구조화된 출력으로 받을 영화 정보 스키마"""

    title: Annotated[str, Field(description="영화 제목")]
    year: Annotated[int, Field(description="개봉 연도")]
    director: Annotated[str, Field(description="감독 이름")]
    plot: Annotated[str, Field(description="줄거리")]

