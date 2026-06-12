from sub1 import A, fun_a
from sub2 import A as B
from sub2 import fun_b

# s1.fun_a(), obj_a = s1.A()와 같이 불필요한 모듈 이름을 붙이지 않고 바로 함수와 클래스를 사용할 수 있음

if __name__ == "__main__":
    # 모듈의 함수 호출
    fun_a()
    fun_b()

    # 모듈의 클래스를 이용해서 객체 생성
    obj_a = A()
    obj_b = B()
