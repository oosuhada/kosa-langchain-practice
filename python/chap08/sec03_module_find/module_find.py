import sys  # 운영체제와 관련된 기능을 제공하는 기본 모듈

print(sys.builtin_module_names)  # 파이썬이 기본적으로 제공하는 모듈들의 이름을 출력

print("-" * 30)

for path in sys.path:  # sys.path에 저장된 경로들을 반복하여 출력
    print(path)

print("-" * 30)

# 현재 디렉토리에 있는 my.py 모듈을 import
import my

my.fun()  # my 모듈의 fun() 함수를 호출

print("-" * 30)

# from chap08 import my2

sys.path.append("../")  # 모듈 검색 경로에 상위 디렉토리(chap08)를 추가
import my2  # 상위 디렉토리에 있는 my2.py 모듈을 import

my2.fun()  # my2 모듈의 fun() 함수를 호출
