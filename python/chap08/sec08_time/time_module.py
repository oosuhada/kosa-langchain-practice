import time


def sum(var1, var2):
    result = 0
    for i in range(var1, var2 + 1):
        result += i
    return result


# 시간 측정하기
start = time.time()
# time.time()은 현재 시간을 초 단위로 반환하는 함수이다.
# 1970년 1월 1일 0시 0분 0초(UTC)부터 경과한 시간을 유닉스 타임스탬프 형태의 초 단위로 나타낸다.
print(start)
sum(1, 100000000)
end = time.time()
print(end)
print(f"실행 시간: {end - start}")

# 주기적으로 실행하기
while True:
    print("2초 간격으로 출력")
    time.sleep(
        2
    )  # 2초 동안 대기하는 함수. time.sleep()은 프로그램의 실행을 일시적으로 멈추는 함수

