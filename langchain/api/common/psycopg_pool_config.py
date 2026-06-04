from psycopg import AsyncConnection
from psycopg.rows import DictRow
from psycopg_pool import AsyncConnectionPool

###############################################################
# psycopg_pool 설정: 대화 기록을 위한 연결에 사용
###############################################################
psycopg_pool: AsyncConnectionPool[AsyncConnection[DictRow]] = AsyncConnectionPool(
    "postgresql://postgres:postgres@localhost:5432/postgres",
    min_size=1,
    max_size=2,
    kwargs={
        "autocommit": True,
        "prepare_threshold": 0,
    },
    open=False,  # FastAPI lifespan에서 명시적으로 열도록 설정
)
