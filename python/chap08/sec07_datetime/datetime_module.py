from datetime import datetime

now = datetime.now()
# datetime은 클래스이고, now()는 datetime 클래스의 클래스 메소드다.
# 객체를 먼저 만들지 않고 datetime.now() 형태로 호출해 현재 날짜/시간을 담은 datetime 객체를 반환한다.
print(now)
print(now.year)

str_now = now.strftime("%Y-%m-%d %H:%M:%S")
str_now2 = now.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")
# strftime()는 datetime 객체를 문자열로 변환하는 메소드다. %Y, %m, %d, %H, %M, %S는 각각 연도, 월, 일, 시, 분, 초를 나타내는 포맷 코드다.

print(str_now)
print(str_now2)

print("year:", now.year)
print("month:", now.month)
print("day:", now.day)
print("hour:", now.hour)
print("minute:", now.minute)
print("second:", now.second)
