# import sub1, sub2  - 함께 import 가능하지만 추천하지 않음

import sub1 as s1
import sub2 as s2

# as를 이용해서 모듈 이름을 별칭으로 지정할 수 있음(alias). 모듈 이름이 길거나 같은 이름의 모듈이 여러개 있을 때 유용함
# import numpy as np, pandas as pd  - numpy와 pandas는 자주 사용하는 라이브러리이므로 np와 pd로 별칭을 지정하는 경우가 많음

if __name__ == "__main__":
    # 모듈의 함수 호출
    s1.fun_a()
    s2.fun_b()
    # 이 코드만 봐서는 객체인지 모듈인지 알 수 없음
    # import를 보고 sub1과 sub2가 모듈이라는 것을 알아낸 후 .을 통해 모듈안에 정의된 함수 호출이라는 것 파악해야함

    # 모듈의 클래스를 이용해서 객체 생성
    obj_a = s1.A()
    obj_b = s2.A()

    # sub1.obj_a.method()  # 객체 안에 정의된 메소드 호출
    # sub2.obj_b.method()  # 객체 안에 정의된 메소드 호출
