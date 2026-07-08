import math
import random

# random.seed(0)
# # 랜덤 파라미터 시드값 설정. 시드값이 같으면 같은 난수들이 생성된다.
# # 실행할때마다 고정된 랜덤값이 출력된다 (재연)
# # 따로 seed값 설정하지 않으면 현재 시간을 시드값으로 사용하여 실행할 때마다 다른 난수들이 생성된다 (비재연)

# 실수 난수([0.0 이상 1.0 미만)) 얻기
print(random.random())

# 정수 난수((0 이상 정수 이하)) 얻기
print(random.randint(1, 6))  # 1 이상 6 이하의 정수 난수 얻기

# 정수 난수([0 이상 정수 미만]) 얻기
print(random.randrange(10))  # 0 이상 10 미만의 정수 난수 얻기
print(random.randrange(1, 10))  # 1 이상 10 미만의 정수 난수 얻기
print(
    random.randrange(1, 10, 2)
)  # 1 이상 10 미만의 정수 난수 중에서 2씩 증가하는 정수 난수 얻기

# 시퀀스에서 무작위로 요소 선택하기
print(random.choice("Hello"))  # 문자열에서 무작위로 문자 하나 선택하기
print(random.choice([1, 2, 3, 4, 5]))  # 리스트에서 무작위로 요소 하나 선택하기

# 주사위의 눈
print(int(random.random() * 6) + 1)  # 1 이상 7 미만의 실수 난수 얻기
print(math.ceil(random.random() * 6))  # 1 이상 6 이하의 정수 난수 얻기
print(random.randint(1, 6))  # 1 이상 6 이하의 정수 난수 얻기
print(random.randrange(1, 7))  # 1 이상 7 미만의 정수 난수 얻기
