# 명령행으로 직접 실행했을 경우, 최상위 값으로 실행하므로
# 실행 파일이 이 모듈을 실행하는 경우
import sys

if __name__ == "__main__":
    # 실행 매개값 얻기 - sys 사용
    print(sys.argv)
    print(type(sys.argv))
    if len(sys.argv) <= 2:
        # 프로그램 종료
        sys.exit(0)

    total = 0
    for i in range(1, len(sys.argv)):
        total += int(sys.argv[i])

    print(f"합계: {total}")
    print("total:", total)
