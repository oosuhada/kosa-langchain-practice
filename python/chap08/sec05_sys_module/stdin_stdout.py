import sys

if __name__ == "__main__":
    # 입력 출력 받기 - sys 사용
    print("입력 출력 받기")
    # 표준 출력
    sys.stdout.write("콘솔에 출력\n")
    # 표준 에러 출력
    sys.stderr.write("콘솔에 에러 출력\n")
    # 표준 입력
    # line = sys.stdin.readline()
    line = input()
    print("입력 받은 내용:", line)
