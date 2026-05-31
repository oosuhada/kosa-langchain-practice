import sub
import sub2

# 아무리 import가 많아도 한 번만 실행됨 (sub.py가 sub2.py에도 import 되고 있지만 한 번만 실행됨)

print(f"__name__ 변수값: {__name__}")

if __name__ == "__name__":
    print("python 명령어로 실행했을 경우에만 실행")
    print(sub.member)


# print(sub.__name__)
# print(sub2.__name__)
