import logging
import shutil
from pathlib import Path
from typing import Annotated

from fastapi import Depends
from langchain.agents import create_agent
from langchain_core.tools import tool

from api.common.utils import LoggingCallbackHandler

logger = logging.getLogger(__name__)

##########################################################
# 파일 시스템 도구 설정
##########################################################
# 실습 중 파일 도구가 접근할 수 있는 루트 디렉토리
# 사용자가 "../" 같은 경로를 입력해도 이 디렉토리 밖으로 나가지 못하게 검증한다.
ROOT_DIR = Path("temp/tool-files").resolve()


def validate_path(path: str) -> Path:
    """실습 루트 기준으로 안전한 절대 경로를 생성하고 검증한다."""
    ROOT_DIR.mkdir(parents=True, exist_ok=True)
    target = (ROOT_DIR / path).resolve()
    logger.info(f"파일 시스템 경로 검증: {path} -> {target}")
    if target != ROOT_DIR and ROOT_DIR not in target.parents:
        raise ValueError("허용된 루트 디렉토리 밖의 경로입니다.")
    return target


##########################################################
# 디렉토리 목록 조회 도구
##########################################################
@tool
def list_directory(path: str = ".") -> str:
    """디렉토리의 파일 및 하위 디렉토리 목록을 조회합니다.

    Args:
        path: 조회할 디렉토리 경로 (기본값: 루트 디렉토리)

    Returns:
        str: 디렉토리 내용 목록 (파일과 디렉토리)
    """
    try:
        logger.info(f"디렉토리 목록 조회 요청: {path}")
        # 경로 검증 및 절대 경로 변환
        dir_path = validate_path(path)
        if not dir_path.exists():
            return f"오류: 디렉토리 '{path}'가 존재하지 않습니다."
        if not dir_path.is_dir():
            return f"오류: '{path}'는 디렉토리가 아닙니다."

        # 디렉토리 내용 목록 생성
        items = []
        for item in sorted(dir_path.iterdir()):
            item_type = "DIR" if item.is_dir() else "FILE"
            relative_path = item.relative_to(ROOT_DIR)
            items.append(f"[{item_type}] {relative_path}")

        # 목록이 비어있으면 "(빈 디렉토리)" 표시, 그렇지 않으면 항목들을 줄바꿈으로 구분하여 반환
        return "\n".join(items) if items else "(빈 디렉토리)"
    except Exception as exc:
        return f"오류: {exc}"


##########################################################
# 파일 생성 도구
##########################################################
@tool
def create_file(path: str, content: str = "") -> str:
    """안전한 실습 루트 아래에 파일을 생성합니다."""
    logger.info(f"파일 생성 요청: {path}")
    target = validate_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"파일 생성 완료: {target.relative_to(ROOT_DIR)}"


##########################################################
# 디렉토리 생성 도구
##########################################################
@tool
def create_directory(path: str) -> str:
    """안전한 실습 루트 아래에 디렉토리를 생성합니다."""
    logger.info(f"디렉토리 생성 요청: {path}")
    target = validate_path(path)
    target.mkdir(parents=True, exist_ok=True)
    return f"디렉토리 생성 완료: {target.relative_to(ROOT_DIR)}"


##########################################################
# 파일 읽기 도구
##########################################################
@tool
def read_file(path: str) -> str:
    """안전한 실습 루트 아래의 파일 내용을 읽습니다."""
    logger.info(f"파일 읽기 요청: {path}")
    target = validate_path(path)
    return target.read_text(encoding="utf-8")


##########################################################
# 파일 쓰기 도구
##########################################################
@tool
def write_file(path: str, content: str) -> str:
    """안전한 실습 루트 아래의 파일에 내용을 씁니다."""
    logger.info(f"파일 쓰기 요청: {path}")
    target = validate_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"파일 쓰기 완료: {target.relative_to(ROOT_DIR)}"


##########################################################
# 파일/디렉토리 삭제 도구
##########################################################
@tool
def delete_path(path: str) -> str:
    """안전한 실습 루트 아래의 파일 또는 디렉토리를 삭제합니다."""
    logger.info(f"파일/디렉토리 삭제 요청: {path}")
    target = validate_path(path)
    if target == ROOT_DIR:
        return "루트 디렉토리는 삭제할 수 없습니다."
    if target.is_dir():
        shutil.rmtree(target)
    elif target.exists():
        target.unlink()
    else:
        return "경로가 존재하지 않습니다."
    return f"삭제 완료: {path}"


##########################################################
# 파일/디렉토리 이동 도구
##########################################################
@tool
def move_path(source: str, destination: str) -> str:
    """안전한 실습 루트 아래의 파일 또는 디렉토리를 이동합니다."""
    logger.info(f"파일/디렉토리 이동 요청: {source} -> {destination}")
    source_path = validate_path(source)
    destination_path = validate_path(destination)
    if not source_path.exists():
        return f"오류: 원본 경로 '{source}'가 존재하지 않습니다."
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_path), str(destination_path))
    return f"이동 완료: {source} -> {destination}"


##########################################################
# 파일/디렉토리 복사 도구
##########################################################
@tool
def copy_path(source: str, destination: str) -> str:
    """안전한 실습 루트 아래의 파일 또는 디렉토리를 복사합니다."""
    logger.info(f"파일/디렉토리 복사 요청: {source} -> {destination}")
    source_path = validate_path(source)
    destination_path = validate_path(destination)
    if not source_path.exists():
        return f"오류: 원본 경로 '{source}'가 존재하지 않습니다."
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    if source_path.is_dir():
        shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
    else:
        shutil.copy2(source_path, destination_path)
    return f"복사 완료: {source} -> {destination}"


##########################################################
# 파일/디렉토리 정보 조회 도구
##########################################################
@tool
def get_file_info(path: str) -> str:
    """안전한 실습 루트 아래의 파일 또는 디렉토리 정보를 조회합니다."""
    logger.info(f"파일/디렉토리 정보 조회 요청: {path}")
    target = validate_path(path)
    if not target.exists():
        return f"오류: 경로 '{path}'가 존재하지 않습니다."
    item_type = "DIR" if target.is_dir() else "FILE"
    size = target.stat().st_size
    relative_path = target.relative_to(ROOT_DIR)
    return f"[{item_type}] {relative_path} / size={size} bytes"


##########################################################
# 파일 시스템 도구를 사용하는 Agent
##########################################################
class FileSystemAgent:
    # Agent 초기화
    # - 파일 시스템 도구들이 접근할 루트 디렉토리를 보관한다.
    # - create_agent()에 파일/디렉토리 관련 도구 목록을 등록한다.
    def __init__(self) -> None:
        logger.info("FileSystemAgent 초기화")
        self.root_dir = ROOT_DIR
        self.agent = create_agent(
            model="openai:gpt-4o-mini",
            tools=[
                list_directory,
                create_directory,
                create_file,
                read_file,
                write_file,
                delete_path,
                move_path,
                copy_path,
                get_file_info,
            ],
            system_prompt="안전한 실습 디렉토리 안에서만 파일을 관리하는 Agent입니다.",
        )

    # Agent 실행
    # - system_message로 작업 가능한 루트 디렉토리와 경로 규칙을 알려준다.
    # - user_message로 사용자의 실제 파일 작업 요청을 전달한다.
    # - Agent가 적절한 파일 도구를 선택해 호출한 뒤 최종 답변을 반환한다.
    async def run(self, question: str) -> str:
        logger.info(f"FileSystemAgent 실행 요청: {question}")
        system_message = {
            "role": "system",
            "content": f"""
                        당신은 파일 시스템 관리 도우미입니다.
                        - 작업 가능한 루트 디렉토리: {self.root_dir}
                        - 모든 경로는 이 루트 디렉토리를 기준으로 상대 경로로 지정하거나, 루트 디렉토리 내부의 절대 경로로 지정해야 합니다.
                        예: "test.txt", "folder/test.txt", "{self.root_dir}/test.txt"
                        - 사용자의 요청을 정확히 이해하고 적절한 도구를 사용하여 작업을 수행하세요.
        """,
        }
        user_message = {"role": "user", "content": question}
        result = await self.agent.ainvoke(
            {"messages": [system_message, user_message]},
            {"callbacks": [LoggingCallbackHandler()]},
        )
        return str(result["messages"][-1].content)


# FastAPI 의존성 주입 타입 별칭
# - controller.py에서 agent: FileSystemAgentDependency로 선언하면
#   Depends가 FileSystemAgent를 생성해서 엔드포인트 함수에 전달한다.
FileSystemAgentDependency = Annotated[FileSystemAgent, Depends(FileSystemAgent)]
