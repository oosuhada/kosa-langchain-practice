import math


# 원주율 이용
def circle_area(r: float) -> float:
    """원의 넓이를 계산하는 함수"""
    return math.pi * r**2


print(circle_area(5))

# 보다 큰 정수
print(math.ceil(3.2))  # 4
print(math.ceil(-3.2))  # -3
print(math.ceil(3.8))  # 4

# 보다 작은 정수
print(math.floor(3.2))  # 3
print(math.floor(-3.2))  # -4
print(math.floor(3.8))  # 3

# 반올림
print(round(3.2))  # 3
print(round(3.8))  # 4
print(round(3.5))  # 4
print(round(3.4))  # 3

# 제곱근
print(math.sqrt(9))  # 3
print(math.sqrt(16))  # 4

# 정수 부분 제곱
print(math.pow(2, 3))  # 8
print(math.pow(2, 0.5))  # 1.4142135623730951

# 절대값
print(abs(-3))  # 3
print(abs(3))  # 3