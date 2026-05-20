# 2026-05-21 Python Review

## 1. 메모 형식 정리

### 오늘 수업 흐름

- Chap1~Chap4는 코딩테스트에 자주 나오는 기본 문법이다.
  - 변수, 자료형, 조건문, 반복문, 리스트/튜플/세트/딕셔너리 같은 기본 자료구조가 핵심이다.
- 앞으로는 함수 정의, 클래스 정의, 모듈 정의처럼 실제 애플리케이션을 만들 때 많이 쓰는 내용을 다룬다.
- 2차 프로젝트에서는 Python -> FastAPI -> LLM 연동 흐름으로 이어질 가능성이 있다.
  - LangChain 또는 LangGraph 같은 도구를 사용할 수 있다.

### Python 코드를 읽기 어렵게 만드는 이유

- Python은 처음 배울 때는 문법이 짧고 쉬워 보인다.
- 하지만 다른 사람이 짠 코드를 읽을 때는 다음 이유로 어려워질 수 있다.
  - 타입이 코드에 강제되지 않는 경우가 많다.
  - 같은 기능을 여러 방식으로 작성할 수 있다.
  - 변수명, 함수명, 클래스명이 명확하지 않으면 의도를 파악하기 힘들다.
- 그래서 수업/프로젝트 코드에서는 주석과 타입 힌트를 적극적으로 쓰는 것이 좋다.

```python
def square(x: int) -> int:
    return x**2
```

- `x: int`는 매개변수 `x`가 `int`일 것이라는 힌트다.
- `-> int`는 함수가 `int`를 반환할 것이라는 힌트다.
- 타입 힌트는 실행 자체를 강제로 막지는 않지만, VS Code/Pylance가 자동완성, 경고, 코드 이해를 도와준다.

### Lambda Expression

- 람다식은 이름 없는 짧은 함수다.
- Java의 람다식과 달리 Python 람다는 중괄호 블록을 만들 수 없다.
- Python 람다는 `lambda 매개변수: 표현식` 형태이고, 콜론 뒤에는 한 개의 표현식만 올 수 있다.

```python
add = lambda x, y: x + y
```

- 위 코드는 아래 함수와 거의 같은 역할을 한다.

```python
def add(x, y):
    return x + y
```

- 단, 복잡한 로직은 람다보다 `def`로 함수 이름을 붙이는 편이 읽기 좋다.

```python
numbers = [1, 2, 3, 4, 5]
squares = list(map(lambda x: x**2, numbers))
```

이 코드는 다음 순서로 이해하면 된다.

1. `numbers`에서 값을 하나씩 꺼낸다.
2. 꺼낸 값이 `lambda x: x**2`의 `x`로 들어간다.
3. `x**2`로 제곱값을 만든다.
4. `map()`은 그 결과들을 바로 리스트로 만들지 않고, 하나씩 꺼낼 수 있는 반복 가능한 객체로 만든다.
5. `list(...)`가 그 결과를 실제 리스트로 변환한다.

즉 아래 두 코드는 결과가 같다.

```python
squares = [x**2 for x in numbers]
squares = list(map(lambda x: x**2, numbers))
```

Python에서는 단순 변환이면 리스트 컴프리헨션이 더 읽기 쉬운 경우가 많다.
`map()`, `filter()`, `sorted(key=...)`처럼 함수 자체를 넘겨야 할 때 람다를 자주 본다.

### Generator

- 제너레이터는 값을 한 번에 전부 만들지 않고, 필요할 때 하나씩 생성하는 객체다.
- 리스트는 모든 값을 메모리에 담아둔다.
- 제너레이터는 다음 값이 필요할 때만 계산해서 내보낸다.
- 그래서 대용량 데이터 처리, 큰 파일 읽기, 무한 시퀀스, 스트리밍 응답에서 중요하다.

```python
numbers = [v for v in range(1, 1000001)]
```

- 리스트 컴프리헨션이다.
- 1부터 1,000,000까지 값을 모두 만들어 리스트에 저장한다.

```python
numbers = (v for v in range(1, 1000001))
```

- 제너레이터 표현식이다.
- 괄호로 감싸였다고 항상 튜플은 아니다.
- `(v for v in ...)`처럼 `for`가 들어간 표현식은 제너레이터다.

```python
def create_generator():
    yield 100
```

- 함수 안에 `yield`가 있으면 일반 함수가 아니라 제너레이터 함수가 된다.
- 이 함수를 호출하면 함수 본문이 바로 실행되는 것이 아니라 제너레이터 객체가 만들어진다.
- `next(generator)`가 호출될 때 `yield`까지 실행되고, 값을 밖으로 내보낸 뒤 그 자리에서 멈춘다.
- 다시 `next(generator)`가 호출되면 이전에 멈춘 `yield` 다음 줄부터 이어서 실행한다.

제너레이터를 이해할 때 핵심은 "일시정지와 재개"다.

- `yield`: 값을 밖으로 내보내고 잠깐 멈춘다.
- `next()`: 멈춘 제너레이터에게 다음 값을 요청한다.
- `send(value)`: 멈춘 제너레이터 안으로 값을 다시 보내면서 재개한다.
- `StopIteration`: 더 이상 만들 값이 없을 때 발생한다.

타입 힌트는 다음처럼 읽는다.

```python
from typing import Generator

def create_generator() -> Generator[int, None, None]:
    yield 1
```

`Generator[int, None, None]`의 의미:

- 첫 번째 `int`: 제너레이터가 밖으로 내보내는 값의 타입
- 두 번째 `None`: `send()`로 안에 받을 값의 타입
- 세 번째 `None`: 제너레이터가 종료될 때 `return`으로 반환하는 값의 타입

### Class, Object, __new__, __init__

- Python도 객체 지향을 지원한다.
- Java에서 배운 클래스, 객체, 상속, 오버라이딩 개념과 큰 흐름은 비슷하다.
- 문법과 관례가 다를 뿐이다.

```python
class Car:
    pass

car1 = Car()
```

- Python에서는 Java처럼 `new Car()`라고 쓰지 않는다.
- `Car()`를 호출하면 내부적으로 객체 생성 과정이 실행된다.

객체 생성 흐름은 크게 다음 순서다.

1. `__new__(cls, ...)`가 객체를 만든다.
2. 만들어진 객체가 `__init__(self, ...)`로 전달된다.
3. `__init__`에서 인스턴스 변수를 초기화한다.

```python
class Car:
    def __init__(self, model: str, year: int) -> None:
        self.model = model
        self.year = year
```

- 일반적인 클래스는 대부분 `__init__`만 정의하면 된다.
- `__new__`는 특별한 경우가 아니면 직접 정의하지 않는다.
- `__init__`은 객체를 만드는 함수가 아니라, 이미 만들어진 객체를 초기화하는 함수다.
- `__init__`은 `self`를 반환하지 않는다. 반드시 `None`을 반환해야 한다.

`self`와 `cls`의 차이:

- `self`: 이미 만들어진 인스턴스 자기 자신
- `cls`: 클래스 자기 자신

```python
def __init__(self):
    ...
```

- 인스턴스 메서드의 첫 번째 인자는 관례적으로 `self`다.

```python
def __new__(cls):
    ...
```

- `__new__`는 객체가 아직 없을 때 호출되므로 `self`가 아니라 `cls`를 받는다.

```python
return super().__new__(cls)
```

- 부모 클래스 쪽 객체 생성 기능을 호출해서 실제 인스턴스를 만든다.
- `return cls()`를 쓰면 다시 `Car()`를 호출하는 꼴이 되어 재귀 호출 문제가 생길 수 있다.

`super()`:

- 부모 클래스의 메서드를 호출할 때 사용한다.
- 상속 구조에서 부모 쪽 초기화나 기능을 재사용할 수 있다.

`@override`:

- Java에서는 어노테이션이라고 부르지만, Python에서는 데코레이터라고 부른다.
- 부모 클래스의 메서드를 재정의한다는 의도를 표시한다.
- Python 3.12에서는 `typing.override`를 사용할 수 있다.

## 2. 실습 파일 주석 형태로 보강할 내용

### chap05/sec10_lambda_expression.ipynb

```python
# lambda는 이름 없는 짧은 함수다.
# 형식: lambda 매개변수: 반환할_표현식
# 콜론(:) 뒤에는 여러 줄 문장이나 대입문이 아니라, 하나의 표현식만 작성할 수 있다.
```

```python
# map(function, iterable)은 iterable의 각 요소를 function에 하나씩 적용한다.
# map()의 결과는 바로 리스트가 아니라 map 객체이므로, 출력/저장하려면 list()로 감싸는 경우가 많다.
squares = list(map(lambda x: x**2, numbers))
```

```python
# 위 코드는 아래 리스트 컴프리헨션과 같은 결과를 만든다.
# 단순 변환은 리스트 컴프리헨션이 더 읽기 쉬운 경우가 많다.
squares = [x**2 for x in numbers]
```

```python
# sorted(..., key=...)에서 key는 "정렬 기준을 뽑아내는 함수"다.
# student가 ("Alice", 85)라면 student[1]은 점수이므로 점수 기준 정렬이 된다.
sorted_students = sorted(students, key=lambda student: student[1])
```

```python
# filter(function, iterable)은 function의 결과가 True인 요소만 남긴다.
# lambda x: x % 2 == 0 은 x가 짝수인지 검사하는 조건 함수다.
even_numbers = list(filter(lambda x: x % 2 == 0, numbers))
```

기존 주석 중 수정 추천:

```python
# 기존: 이름을 지정하지 않으면 이름이 없어서 문자열 함수로 변환
# 수정: str(x**2)는 제곱 결과를 문자열로 변환한다. lambda와 직접 관련된 예제는 아니다.
squares = [str(x**2) for x in numbers]
```

### chap05/sec11_generator.ipynb

```python
# (v for v in range(...))는 제너레이터 표현식이다.
# 괄호를 썼다고 항상 tuple은 아니다.
# for가 들어간 generator expression은 값을 한 번에 저장하지 않고 필요할 때 하나씩 만든다.
generator = (v for v in range(1, 1000001))
```

```python
# [v for v in range(...)]는 리스트 컴프리헨션이다.
# 모든 값을 즉시 만들어 리스트에 저장하므로 데이터가 크면 메모리를 많이 사용할 수 있다.
numbers = [v for v in range(1, 1000001)]
```

```python
# 함수 안에 yield가 있으면 이 함수는 제너레이터 함수가 된다.
# 호출 즉시 본문이 끝까지 실행되지 않고, next()가 호출될 때 yield까지 실행된다.
def create_generator():
    yield 100
```

```python
# next(generator)는 제너레이터에게 다음 값을 요청한다.
# yield를 만나면 값을 밖으로 내보내고, 제너레이터는 그 위치에서 일시정지한다.
value = next(generator)
```

```python
# next(generator, None)은 다음 값이 없을 때 StopIteration을 발생시키지 않고 None을 반환한다.
# 기본값 없이 next(generator)를 호출하면, 끝난 제너레이터에서는 StopIteration 예외가 발생한다.
value = next(generator, None)
```

```python
# Generator[YieldType, SendType, ReturnType]
# 첫 번째 타입: yield로 밖에 내보내는 값
# 두 번째 타입: send()로 안에 받을 값
# 세 번째 타입: return으로 끝낼 때 반환하는 값
def create_generator() -> Generator[int, None, None]:
    yield 1
```

기존 주석 중 수정 추천:

```python
# 기존: 타입 힌트: int값을 보내고 결과값을 받지 않는 제너레이터
# 수정: Generator[int, None, None]은 int 값을 밖으로 내보내고,
#      send()로 받는 값은 없으며, 종료 시 return 값도 없다는 의미다.
```

```python
# 무한 제너레이터는 반드시 break, 조건식, 개수 제한 같은 중단 조건과 함께 사용해야 한다.
# 그렇지 않으면 for문이 끝나지 않는다.
for value in generator:
    if value == 100:
        break
```

```python
# send(result)는 일시정지된 yield 표현식 자리에 result 값을 전달하면서 제너레이터를 재개한다.
# result = yield source 라면, 외부에서 send(result_list)를 호출했을 때 result 변수에 result_list가 들어간다.
result = yield source
```

```python
# 제너레이터가 return final_result로 종료되면 StopIteration 예외가 발생한다.
# 이때 return 값은 StopIteration 객체의 value 속성으로 꺼낼 수 있다.
except StopIteration as e:
    print(e.value)
```

### chap06/sec02_class_object.ipynb

```python
# class는 객체를 만들기 위한 설계도다.
# Car()를 호출하면 Car 클래스의 인스턴스가 생성된다.
class Car:
    pass
```

```python
# Python에서는 Java처럼 new Car()라고 쓰지 않는다.
# Car() 호출 내부에서 __new__()와 __init__()이 순서대로 호출된다.
car1 = Car()
```

```python
# car1과 car2는 같은 Car 클래스로 만든 서로 다른 인스턴스다.
# id() 값이 다르면 메모리상 서로 다른 객체라는 뜻이다.
print(id(car1))
print(id(car2))
```

### chap06/sec03_new_init.ipynb

```python
# __new__는 객체를 실제로 생성하는 메서드다.
# 객체가 아직 없으므로 첫 번째 인자로 self가 아니라 cls를 받는다.
def __new__(cls) -> Self:
    return super().__new__(cls)
```

```python
# __init__은 이미 생성된 객체를 초기화하는 메서드다.
# 여기서 self는 새로 만들어진 인스턴스 자기 자신이다.
# __init__은 self를 return하지 않고 None을 반환해야 한다.
def __init__(self) -> None:
    super().__init__()
```

```python
# return cls()를 사용하면 다시 Car()를 호출하게 되어 __new__가 반복 호출될 수 있다.
# 객체 생성은 보통 부모 클래스의 __new__를 호출하는 방식으로 처리한다.
return super().__new__(cls)
```

```python
# 일반적인 클래스에서는 __new__를 직접 정의하지 않고 __init__만 정의하는 경우가 대부분이다.
# __new__는 싱글톤, 불변 객체 커스터마이징, 객체 생성 전 제어가 필요한 경우처럼 특별할 때 사용한다.
```

```python
# 입력값 검증은 대부분 __init__에서도 충분히 처리할 수 있다.
# 단, 검증 실패 시 객체 생성 자체를 막거나 __new__ 단계에서 제어해야 하는 특별한 설계라면 __new__에서 검사할 수 있다.
```

```python
# isinstance(value, type)은 value가 해당 type의 인스턴스인지 확인한다.
# 맞으면 True, 아니면 False를 반환한다.
if not isinstance(model, str):
    raise TypeError("model은 str 타입이어야 합니다.")
```

```python
# __str__은 print(car1)처럼 객체를 문자열로 표현해야 할 때 호출된다.
def __str__(self) -> str:
    return f"{self.model} {self.year}"
```

```python
# @override는 부모 클래스의 메서드를 재정의한다는 의도를 표시하는 데코레이터다.
# Python에서는 Java의 annotation과 비슷한 위치에 쓰이지만, 이름은 decorator라고 부른다.
```

