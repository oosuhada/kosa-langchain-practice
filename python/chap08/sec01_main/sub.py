from enum import member

print(f"__name__ 변수값: {__name__}")


class Member:
    pass


# 모듈 싱글톤 객체 - 모듈은 하나의 객체로 만들어지기 때문에, 모듈 내에서 정의된 변수는 모듈이 import 되는 모든 곳에서 공유된다.
member = Member()

if __name__ == "__name__":
    print("python 명령어로 실행했을 경우에만 실행")
